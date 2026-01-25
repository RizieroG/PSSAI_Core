import os
import sys
import re
import json
import subprocess
import tempfile
import shutil
import time
from datetime import datetime
from crewai import Agent, Task, Crew, LLM

# ========================= OLLAMA / LiteLLM SETUP ========================= #

def detect_base_url() -> str:
    env = os.environ.get("OLLAMA_BASE_URL") or os.environ.get("OLLAMA_API_BASE")
    if env:
        return env.rstrip("/")
    return "http://localhost:11434"

BASE_URL = detect_base_url()

# Models
llm_planner = LLM(
    model=f"ollama/dolphin3:8b",
    base_url=BASE_URL,
    temperature=0.5,
    max_tokens=8192,
    timeout=1200,
)

llm_coder = LLM(
    model=f"ollama/gavineke/powershell-codex:latest",
    base_url=BASE_URL,
    temperature=0.2,
    max_tokens=8192,
    timeout=1200,
)

llm_reviewer = LLM(
    model=f"ollama/llama3.1:8b",
    base_url=BASE_URL,
    temperature=0.2,
    max_tokens=8192,
    timeout=1200,
)

llm_change_planner = LLM(
    model=f"ollama/dolphin3:8b",
    base_url=BASE_URL,
    temperature=0.5,
    max_tokens=8192,
    timeout=1200,
)

# ============================== AGENTS ==================================== #
# Agents info and prompts -> https://docs.crewai.com/en/concepts/agents
planner = Agent(
    role="Planner",
    goal=(
        "Produce a minimal, unambiguous execution plan for the Coder to implement as a single, "
        "runnable PowerShell script on vanilla Windows. No code, no acceptance tests, no placeholders."
    ),
    backstory=(
        """
        You are the Planner in a Planner→Coder pipeline. Transform the user request 
        into the smallest set of sequential, atomic, and testable instructions.

        Global ethos:
        • Prefer zero interactivity.
        • Keep scope tight; no installs; no environment changes.
        • Be deterministic; no branches unless strictly needed.

        Output format:
        • Obey the task spec exactly: return only 6–9 bullet lines starting with '- ' (no code, no JSON, no headings).
        
        EXAMPLE 1:
        USER REQUEST: "Write a PowerShell script that open multiple popups using Windows Forms. It generates a random number of popups and displays a message in each popup."
        THOUGHT:
        1.  The user wants to display multiple GUI popups. This is an interactive task by nature.
        2.  The technology is specified: Windows Forms. This requires loading the `System.Windows.Forms` assembly as the very first step.
        3.  The number of popups must be random, specifically between 5 and 10 as detailed in the final plan. This requires using the `Get-Random` cmdlet.
        4.  Since the action of creating and showing a popup is repetitive, a reusable function (`Show-Popup`) is the cleanest and most robust approach. This avoids duplicating code in the main loop.
        5.  Popups steal focus and require user interaction to close. To adhere to the "zero interactivity" ethos, they must close automatically. A self-closing timer is the best non-interactive mechanism for this.
        6.  The user request does not mention saving, exporting, or writing to files. The output is purely visual (the popups themselves), not text to the console. Therefore, the plan must explicitly state that no files are created.
        7.  The final plan will be structured logically: first the setup (assembly loading), then the tool definition (the function), and finally the main execution logic (generating the random number and looping). This decomposition leads to the 8 atomic steps.
        FINAL PLAN:
        - Load the Windows Forms assembly to enable GUI creation.
        - Define a function called Show-Popup that accepts a message and a popup number as parameters.
        - Inside the function, create a new Windows Form object with a specific size and title.
        - Add a Label control to the form to display the incoming message text.
        - Configure a Timer object to automatically close the form after a 5-second interval.
        - Show the form as a dialog window, which waits until it's closed.
        - Generate a random integer between 5 and 10 to determine how many popups to show.
        - Loop from 1 to the random number, calling the Show-Popup function in each iteration with a unique message.


        EXAMPLE 2:
        USER REQUEST: "Write a PowerShell script that create a proof of concept backdoor that reads instructions or scripts from a specific registry key, executes those instructions, and then stores the output back to another registry key. The script includes functionality to start the backdoor immediately upon activation, and also includes a cleanup script to remove the created registry keys."
        THOUGHT:
        1. The user's core goal is to create a PowerShell script that acts as a backdoor, reading instructions from a specific registry key, executing them, and storing the output in another registry key. This involves several key components: registry manipulation, command execution, and a continuous loop for monitoring and executing commands.
        2. The script needs to handle the creation and deletion of registry keys, which are used to store instructions and results. This requires using PowerShell's New-Item, Set-ItemProperty, and Remove-Item cmdlets to interact with the Windows Registry.
        3. The backdoor should be capable of starting immediately upon activation, which means the script must include a mechanism to check for an activation key and begin execution if it is present.
        4. The Invoke-Expression cmdlet will be used to execute the commands read from the registry. This cmdlet runs a specified string as a command, which is essential for executing dynamic content read from the registry.
        5. A cleanup script is required to remove the registry keys created by the backdoor. This ensures that no traces of the backdoor remain in the registry after it has been used.
        6. An infinite loop is necessary to continually check for new commands in the input registry key. This loop will read the command, execute it, and then store the output in the specified output registry key.
        7. To avoid excessive CPU usage, the script should include a sleep interval within the loop, allowing the script to periodically check for new commands without constantly running.
        8. The script must handle potential errors, such as missing registry keys or invalid commands, to ensure robustness and prevent unexpected behavior.
        9. The design should encapsulate the main functionality in a reusable function, such as Start-Backdoor, to promote code organization and reusability.
        FINAL PLAN:
        - Define the Start-Backdoor function with parameters for input and output registry paths, and an optional activation key path.
        - Create the input and output registry keys at the specified paths using New-Item and Set-ItemProperty.
        - Optionally create an activation registry key to start the backdoor immediately.
        - Set the initial command in the input registry key.
        - Optionally create a cleanup script that deletes the input, output, and activation registry keys.
        - Start an infinite loop that checks for the activation registry key.
        - Inside the loop, read the command from the input registry key, execute it using Invoke-Expression, and store the output in the output registry key.
        - Include a sleep interval within the loop to prevent continuous checking.
        - Handle potential errors, such as missing registry keys or invalid commands, to ensure the script runs smoothly.
        """
    ),
    llm=llm_planner,
    verbose=False
)

coder = Agent(
    role="Coder",
    goal=(
        "Deliver exactly one self-contained, directly runnable PowerShell (.ps1) script "
        "that fulfills the Planner’s steps on a vanilla Windows host."
    ),
    backstory=("""
        You are a Senior Software Engineer specialized in PowerShell scripting.
        Your output MUST be only the final .ps1 file contents — no markdown, no prose, no fences, no placeholders, no TODOs. 
        LET'S THINK STEP BY STEP

        Hard requirements:
        • Use only built-in Microsoft.PowerShell.* modules. 
        • Structure the script for reliability: optional Param() (only if inputs are explicitly required), helper functions, main execution block, 
        and a single well-defined exit point.
        • No explanations, comments about decisions, or extra lines before/after the code.
        • LET'S THINK STEP BY STEP
        """
    ),
    llm=llm_coder,
    verbose=False,
)

reviewer = Agent(
    role="Evaluator/Reviewer",
    goal=(
        "Given a PowerShell script and the PSScriptAnalyzer report, decide pass/fail. "
        "If fail, craft a minimal, precise FIX PROMPT for the Coder based strictly on parsing/syntax/rule errors."
    ),
    backstory=("Senior Windows engineer & code reviewer. Diagnose parsing issues and propose surgical fixes."),
    llm=llm_reviewer,
    verbose=False,
)

change_planner = Agent(
    role="Change Planner",
    goal=(
        "Produce FIX NOTES as precise deltas to the CANONICAL PLAN. "
        "Mirror its bullets and reference them by ordinal (e.g., 'Bullet 3'). "
        "Address ONLY what the USER CHANGE REQUEST asks. No code."
    ),
    backstory=(
        "You come after a working script. Users request adjustments. "
        "Your job is to convert their wishes into minimal, testable DELTAS, "
        "not a new plan. Preserve the original objective, invariants, and "
        "stdout/file policies unless the user explicitly changes them. "
        "If the request names identifiers (functions/vars), target them by exact name. "
        "If something is ambiguous, choose the narrowest local change that satisfies the user's words; "
        "do NOT introduce new platforms, params, outputs, logs, or messaging."
    ),
    llm=llm_change_planner,
    verbose=False,
)

# ============================== TASKS ===================================== #
# Tasks info and prompts -> https://docs.crewai.com/en/concepts/tasks
plan_task = Task(
    description=(
        "First, silently brainstorm 2–3 alternative step sequences in a private scratchpad and choose the best "
        "using these criteria: determinism, zero interactivity. "
        "Do NOT reveal or reference the scratchpad.\n\n"
        "Now produce the final plan.\n\n"
        "Turn the following USER REQUEST into a minimal, executable plan for the Coder.\n\n"
        "USER REQUEST:\n{request}\n\n"
        "Output exactly 6–9 lines, each starting with '- '. No code, no JSON, no headings, "
        "no numbering, no placeholders. One atomic, imperative action per line.\n\n"
    ),
    expected_output=(
        "Exactly 6–9 bullet lines, each starting with '- ', ordered per the spec and grounded in the USER REQUEST."
    ),
    agent=planner,
    markdown=False
)

code_task = Task(
    description=(
        "You are an EDITOR, not a re-writer.\n"
        "CONTEXT BUNDLE:\n"
        "ORIGINAL REQUEST:\n{request}\n\n"
        "CANONICAL PLAN:\n{plan}\n\n"
        "INVARIANTS (MUST KEEP ALWAYS):\n{invariants}\n\n"
        "CURRENT SCRIPT (read-only context; update MINIMALLY):\n<CODE>\n{current_code}\n</CODE>\n\n"
        "FIX NOTES (apply as deltas; DO NOT remove any invariant):\n{fix_notes}\n\n"
        "TASK: Return ONLY a complete PowerShell (.ps1) implementing the plan and invariants, with the FIX NOTES applied as the SMALLEST possible change set.\n"
        "Rules:\n"
        "- FIX NOTES are authoritative. If they require structural changes (e.g., refactor/rename/reorder), implement them even if not minimal.\n"
        "- DO NOT discard features from the plan\n"
        "- FIX NOTES are authoritative over 'minimal changes'. If FIX NOTES require an algorithmic refactor (e.g., recursion vs loop), implement it even if it is non-trivial.\n"
        "- Do NOT add comments except the single '## PATCH NOTES: iter {iter_num}' header.\n"
        "- No prose before/after; emit only runnable .ps1.\n"
        "- Target Windows PowerShell\n"
        "USER CHANGE REQUEST (original words from human):\n{user_change_request}\n\n"
        "DECISION POLICY:\n"
        "- First, apply FIX NOTES exactly.\n"
        "- If FIX NOTES are inapplicable (e.g., they mention non-existent parameters/identifiers or impossible API usage), implement the USER CHANGE REQUEST directly in the smallest concrete way, using the platform idioms already present in CURRENT SCRIPT (e.g., event handlers, timers) while preserving INVARIANTS.\n"
        "- You MUST produce an executable behavior change: if the resulting script is identical to CURRENT SCRIPT aside from whitespace/comments, treat it as a failure and implement the change.\n"
        "OUTPUT: ONLY the .ps1 body (no markdown/backticks/prose/comments).\n"
    ),
    expected_output="Only executable PowerShell code (.ps1), no fences or extra text.",
    agent=coder,
    markdown=False,
)

review_task = Task(
    description=(
        "Strict evaluator.\n"
        "ORIGINAL REQUEST:\n{request}\n\n"
        "CANONICAL PLAN:\n{plan}\n\n"
        "INVARIANTS (must not be removed):\n{invariants}\n\n"
        "INPUT CODE:\n<CODE>\n{code}\n</CODE>\n\n"
        "STATIC ANALYSIS REPORT (PSScriptAnalyzer JSON):\n<REPORT>\n{report}\n</REPORT>\n\n"
        "Decide and reply with STRICT JSON ONLY (no prose):\n"
        "If pass (exit_code==0 and no diagnostics with RuleName ParseError/TokenizeError):\n"
        '{"status":"ok","reason":"short confirmation"}\n'
        "Else produce MINIMAL PATCH-STYLE FIXES that change executable behavior:\n"
        '{'
        '"status":"retry",'
        '"reason":"<=400 chars explaining concrete failure (quote offending lines if useful)",'
        '"edits":[\n'
        '  {"op":"replace","find":"<exact snippet>","replace":"<new snippet>"},\n'
        '  {"op":"insert_after","anchor":"<unique line fragment>","code":"<code to insert>"},\n'
        '  {"op":"remove","find":"<exact snippet>"}\n'
        '],'
        '"notes":"Do NOT remove invariants; fix parse/syntax errors first; keep minimal changes"\n'
        '}\n'
        "Rules:\n"
        "- Edits MUST reference real code from <CODE>.\n"
        "- Prefer concrete PowerShell statements that address the specific diagnostics.\n"
        "- Avoid generic advice; provide at least 1 edit that modifies an executable statement.\n"
    ),
    expected_output=(
        'JSON with keys: status=("ok"|"retry"), reason, and when retry: edits=[...], notes.'
    ),
    agent=reviewer,
    markdown=False,
)

change_plan_task = Task(
    description=(
        "Translate the USER CHANGE REQUEST into FIX NOTES for the Coder (no code).\n\n"
        "USER CHANGE REQUEST (free text from human):\n{change_request}\n\n"
        "CONTEXT:\n"
        "• ORIGINAL REQUEST:\n{request}\n"
        "• CANONICAL PLAN (read-only):\n{plan}\n"
        "• INVARIANTS (must keep):\n{invariants}\n"
        "• CURRENT SCRIPT (read-only):\n<CODE>\n{current_code}\n</CODE>\n\n"
        "SCOPE CONTRACT (hard):\n"
        "- Only address what the USER CHANGE REQUEST explicitly asks. Do NOT introduce new concerns, platforms, params, outputs, logs, or messages unless the user requests them.\n"
        "- Mirror the CANONICAL PLAN: express each delta as a modification to a specific plan item by ordinal.\n"
        "- Feasibility: do NOT invent non-existent method parameters/overloads or platform features. If the target API cannot accept a parameter to achieve the change, propose concrete insert/replace steps using idiomatic constructs already available in the CURRENT SCRIPT (e.g., event handlers, timers) to achieve the behavior.\n"
        "- Concreteness: each delta MUST name the exact object/method/event you intend to change or insert.\n"
        "- If the user names identifiers (functions/vars), at least one delta MUST target them by exact name.\n\n"
        "OUTPUT (STRICT):\n"
        "Return 3–9 lines; each line MUST start with '- ' and reference 'Bullet <n>' (the ordinal in the CANONICAL PLAN), e.g. '- Bullet 3: replace ...'.\n"
        "Use imperative, testable edits (replace/insert/remove/move/rename) with concrete targets and behaviors. No prose before/after. No code.\n"
    ),
    expected_output="3–9 delta lines starting with '- ', each referencing 'Bullet <n>'.",
    agent=change_planner,
    markdown=False,
)


# ============================== UTILS ===================================== #

def _to_text(result) -> str:
    """
    Normalize any Crew/LLM result to a plain string, safely.

    Why this exists:
    - Different SDKs/agents may return wrapper objects where the actual text
      is under `result.raw` (e.g., CrewAI Result), not directly the object itself.
    - Some result types implement a brittle __str__ that can raise or produce
      non-useful representations.
    - Callers (planning/coding/review) expect a robust string for downstream
      regex/JSON parsing and file writes.
    """
    try:
        return getattr(result, "raw") if hasattr(result, "raw") else str(result)
    except Exception:
        return str(result)


def extract_powershell_code(text: str) -> str:
    if "```" in text:
        m = re.search(r"```(?:powershell|ps1|ps)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip()
        return re.sub(r"```", "", text, flags=re.DOTALL).strip()
    return text.strip()


def parse_jsonish(s: str) -> dict:
    try:
        return json.loads(s)
    except Exception:
        pass
    m = re.search(r"\{.*\}", s, flags=re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return {}

# clean up plan to only invariants
def plan_to_invariants(plan_text: str) -> str:
    """
    Normalize a free-form plan into a canonical bullet list of "invariants".

    The Coder prompt works best with a clean, bullet-point checklist of
    must-have items. This function extracts only lines that already start with
    "- " and rewrites them into a consistent bullet format. If none are found,
    it falls back to a single bullet containing the whole plan.
    """
    lines = []
    for ln in plan_text.splitlines():
        ln = ln.strip()
        if ln.startswith("- "):
            lines.append(f"- {ln[2:]}")
    return "\n".join(lines) if lines else f"- {plan_text.strip()}"

# Pack all context needed by the Coder task into a single dict.
def build_coder_input_bundle(request: str, plan_text: str, invariants_text: str,
                             current_code: str, fix_notes: str, iter_num: int,
                             user_change_request: str = "") -> dict:
    return {
        "request": request, # What to build
        "plan": plan_text,  # Natural-language plan
        "invariants": invariants_text, # Must-have constraints/checklist
        "current_code": current_code if current_code else "<none>",
        "fix_notes": fix_notes, # Findings from static analysis/review
        "iter_num": iter_num, # Iteration index for the Coder
        "user_change_request": user_change_request or "<none>", # User free-text change request
    }


class PSScriptAnalyzerRunner:
    """
    Runs PSScriptAnalyzer on the saved script and returns a JSON-ish dict with diagnostics.
    """
    def __init__(self, host_script_path: str, timeout_sec: int = 120):
        self.host_script_path = os.path.abspath(host_script_path)
        self.timeout = timeout_sec

    def _detect_shell(self) -> str:
        for exe in ("pwsh", "powershell"):
            if shutil.which(exe):
                return exe
        return "powershell"


    # --- How PSScriptAnalyzer is used here ---------------------------------------
    # Execute a PowerShell snippet that:
    # 1) Ensures PSScriptAnalyzer is available (Import-Module); if missing, it
    #    returns a JSON payload with success=false, exit_code=-2 and an install hint.
    # 2) Runs Invoke-ScriptAnalyzer over self.host_script_path with default rules,
    #    limited to severities Error and Warning.
    # 3) Separately collects parsing/tokenization issues (ParseError, TokenizeError)
    #    and all other Errors.
    # 4) Builds a diagnostics array (RuleName, Severity, Message, file/extent info,
    #    and offending Text) for every result (all severities).
    # 5) Computes exit_code = (#Parse/Tokenize errors) + (#Errors). Warnings do NOT
    #    increase exit_code.
    # 6) Returns a single JSON object
    #    -> This lets the caller gate the pipeline: exit_code>0 = failing static checks,
    #       while still showing full diagnostics (including warnings) to the user.
    def run(self) -> dict:
        shell = self._detect_shell()
        ps_code = f"""
        $ErrorActionPreference = 'Stop'
        try {{
        Import-Module PSScriptAnalyzer -ErrorAction Stop
        }} catch {{
        $payload = [pscustomobject]@{{
            success     = $false
            exit_code   = -2
            stdout      = ''
            stderr      = 'PSScriptAnalyzer non è installato. Esegui: Install-Module PSScriptAnalyzer -Scope CurrentUser'
            runner      = 'PSScriptAnalyzer'
            diagnostics = @()
        }}
        $payload | ConvertTo-Json -Depth 6
        exit 1
        }}

        $results = Invoke-ScriptAnalyzer -Path '{self.host_script_path}' -IncludeDefaultRules -Severity Error,Warning
        $parse = $results | Where-Object {{ $_.RuleName -in @('ParseError','TokenizeError') }}
        $errors = $results | Where-Object {{ $_.Severity -eq 'Error' }}

        $diag = $results | ForEach-Object {{
        [pscustomobject]@{{
            RuleName   = $_.RuleName
            Severity   = $_.Severity
            Message    = $_.Message
            ScriptName = $_.ScriptName
            StartLine  = $_.Extent.StartLineNumber
            StartCol   = $_.Extent.StartColumnNumber
            EndLine    = $_.Extent.EndLineNumber
            EndCol     = $_.Extent.EndColumnNumber
            Text       = $_.Extent.Text
        }}
        }}

        $exit = ($parse.Count + $errors.Count)
        $payload = [pscustomobject]@{{
        success     = ($exit -eq 0)
        exit_code   = $exit
        stdout      = ''
        stderr      = ($parse + $errors | Select-Object RuleName,Message,ScriptName | ForEach-Object {{ "$( $_.RuleName): $( $_.Message)" }}) -join "`n"
        runner      = 'PSScriptAnalyzer'
        diagnostics = $diag
        }}

        $payload | ConvertTo-Json -Depth 6
        """
        with tempfile.NamedTemporaryFile('w', suffix='.ps1', delete=False, encoding='utf-8') as tf:
            tf.write(ps_code)
            temp_ps1 = tf.name
        try:
            start = time.time()
            proc = subprocess.run([shell, "-NoProfile", "-File", temp_ps1], capture_output=True, timeout=self.timeout)
            dur_ms = int((time.time() - start) * 1000)

            def _dec(b: bytes) -> str:
                for enc in ("utf-8", "cp1252", "latin-1"):
                    try:
                        return b.decode(enc)
                    except UnicodeDecodeError:
                        pass
                return b.decode("utf-8", errors="replace")

            out = _dec(proc.stdout).strip()
            try:
                payload = json.loads(out) if out else {}
            except Exception:
                payload = {}
            if not payload:
                payload = {
                    "success": proc.returncode == 0,
                    "exit_code": proc.returncode,
                    "stdout": out,
                    "stderr": _dec(proc.stderr).strip(),
                    "runner": "PSScriptAnalyzer(raw)",
                }
            payload["duration_ms"] = dur_ms
            return payload
        finally:
            try:
                os.remove(temp_ps1)
            except Exception:
                pass

# ============================== USER GATE ================================= #

# get multi-line input from user until a line with only "END"
def _prompt_multiline(prompt: str) -> str:
    print(prompt)
    print("(Terminate with a single line containing END)")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def user_review_gate(request: str, plan_text: str, script_path: str, script_code: str) -> tuple[str, str]:
    """
    Interactive human-in-the-loop gate for final approval or change requests.

    Behavior:
      - Prints the high-level request, the bullet-point plan, and where the script has been saved on disk.
      - Prompts the user to: Accept, View code here, Edit (opens a multiline prompt to collect change notes, then returns ("change", <notes>))
      - Keeps prompting until a valid choice is entered.

    Returns:
        tuple[str, str]: (decision, notes)
            decision ∈ {"accept", "change"}
            notes    = "" when decision == "accept"; otherwise the user's change request.
    """
    print("\n===== USER REVIEW GATE =====")
    print(f"Request: {request}")
    print("Plan (bullets):")
    for ln in plan_text.splitlines():
        print(f"  {ln}")
    print(f"\nScript saved at: {script_path}")
    while True:
        choice = input("[A]ccept / [V]iew code here / [E]dit (request changes)? ").strip().lower()
        if choice in ("a", "accept"):
            return "accept", ""
        if choice in ("v", "view"):
            print("\n----- SCRIPT BEGIN -----")
            print(script_code)
            print("----- SCRIPT END -----\n")
            continue
        if choice in ("e", "edit", "change"):
            notes = _prompt_multiline("Describe the changes you want. Be specific (constants, order, outputs).")
            if not notes:
                print("No changes provided. Returning to menu.")
                continue
            return "change", notes
        print("Please answer A / V / E.")


# ============================== MAIN ====================================== #

def main():
    request = (
        "Default request text."
    )
    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])

    # 1) PLANNING
    print("--- 1) PLANNING ---")
    # https://docs.crewai.com/en/concepts/crews
    plan_crew = Crew(agents=[planner], tasks=[plan_task])
    plan_res = plan_crew.kickoff(inputs={"request": request})
    plan_text = _to_text(plan_res).strip()
    print(plan_text)
    invariants_text = plan_to_invariants(plan_text)

    code_crew = Crew(agents=[coder], tasks=[code_task])
    review_crew = Crew(agents=[reviewer], tasks=[review_task])
    change_crew = Crew(agents=[change_planner], tasks=[change_plan_task])

    max_auto_fix_iters = 3    # static-analysis iterations
    max_user_rounds    = 5    # user change rounds

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    script_code = ""
    fix_notes = "Initial implementation from the plan."
    iter_num = 0

    def _save_script(code: str, it: int) -> str:
        name = f"generated_{timestamp}_iter{it}.ps1"
        path = os.path.join(os.getcwd(), name)
        with open(path, "w", encoding="utf-8-sig") as f:
            f.write(code)
        print(f"Salvato: {path}")
        return path

    # === Auto loop: code -> analyze -> review -> human gate until pass ===
    for it in range(1, max_auto_fix_iters + 1):
        iter_num = it
        print(f"\n=== ITERATION {it} / {max_auto_fix_iters} ===")
        print("--- CODING ---")
        bundle = build_coder_input_bundle(
            request=request,
            plan_text=plan_text,
            invariants_text=invariants_text,
            current_code=script_code if it > 1 else "",
            fix_notes=fix_notes,
            iter_num=it,
        )
        code_res = code_crew.kickoff(inputs=bundle)
        # normalize the text to extract only the code
        code_text = _to_text(code_res)
        script_code = extract_powershell_code(code_text)
        script_path = _save_script(script_code, it)

        print("--- ANALYSIS (PSScriptAnalyzer) ---")
        runner = PSScriptAnalyzerRunner(script_path, timeout_sec=180)
        report = runner.run()
        print(json.dumps(report, indent=2, ensure_ascii=False))

        print("--- REVIEW ---")
        review_inputs = {
            "request": request,
            "plan": plan_text,
            "invariants": invariants_text,
            "code": script_code,
            "report": json.dumps(report, ensure_ascii=False),
        }
        review_res = review_crew.kickoff(inputs=review_inputs)
        decision = parse_jsonish(_to_text(review_res).strip())
        status = (decision.get("status") or "").lower()

        if status == "ok" or report.get("success"):
            print("Reviewer: OK (script accepted).")
            break
        else:
            reason = decision.get("reason", "")
            print(f"Reviewer: RETRY — {reason or 'reason not specified'}")
            fix_notes = (
                decision.get("coder_prompt", "").strip()
                or f"Fix the previous script to satisfy the plan. Errors:\n{report.get('stderr','')}\nDo NOT remove any invariant. Apply minimal changes."
            )
            if it == max_auto_fix_iters:
                print("Auto-fix limit reached — switching to user gate with latest version.")

    # ================= USER REVIEW GATE ================= #
    user_round = 0
    while True:
        user_round += 1
        decision, notes = user_review_gate(request, plan_text, script_path, script_code)
        if decision == "accept":
            print("Script approved by user. End.")
            print(f"Final script: {script_path}")
            return 0
        # decision == "change"
        if user_round > max_user_rounds:
            print("Maximum number of user requests reached. Logging out.")
            return 1

        print("--- CHANGE PLANNING (user deltas → FIX NOTES) ---")
        change_inputs = {
            "change_request": notes,
            "request": request,
            "plan": plan_text,
            "invariants": invariants_text,
            "current_code": script_code,
        }
        change_res = change_crew.kickoff(inputs=change_inputs)
        fix_notes = _to_text(change_res).strip()
        print("--- FIX NOTES (from change_planner) ---")
        print(fix_notes)
        with open(f"fixnotes_{timestamp}_round{user_round}.txt", "w", encoding="utf-8") as f:
            f.write(fix_notes + "\n")

        if not fix_notes:
            print("Error: no FIX NOTES generated by the change planner. Quit.")
            return 2

        # New coding round using current_code + fix_notes
        iter_num += 1
        print("--- CODING (apply user deltas) ---")
        bundle = build_coder_input_bundle(
            request=request,
            plan_text=plan_text,
            invariants_text=invariants_text,
            current_code=script_code,
            fix_notes=fix_notes,
            iter_num=iter_num,
        )
        code_res = code_crew.kickoff(inputs=bundle)
        script_code = extract_powershell_code(_to_text(code_res))
        script_path = _save_script(script_code, iter_num)

        print("--- ANALYSIS (PSScriptAnalyzer) ---")
        runner = PSScriptAnalyzerRunner(script_path, timeout_sec=180)
        report = runner.run()
        print(json.dumps(report, indent=2, ensure_ascii=False))

        print("--- REVIEW ---")
        review_inputs = {
            "request": request,
            "plan": plan_text,
            "invariants": invariants_text,
            "code": script_code,
            "report": json.dumps(report, ensure_ascii=False),
        }
        review_res = review_crew.kickoff(inputs=review_inputs)
        decision_ai = parse_jsonish(_to_text(review_res).strip())
        status_ai = (decision_ai.get("status") or "").lower()
        if status_ai == "ok" or report.get("success"):
            print("Reviewer: OK. Script passes static analysis.")
            # loop back to user gate for acceptance or further changes
            continue
        else:
            print("Reviewer: static analysis failed after applying user changes.")
            tech_notes = (
                decision_ai.get("reason", "").strip()
                or report.get("stderr", "")
            )
            fix_notes = (
                f"Apply minimal fixes to pass static analysis and keep invariants. Technical notes: {tech_notes}"
            )
            # Keep loop; next iteration will use these fix notes on top of user deltas


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
