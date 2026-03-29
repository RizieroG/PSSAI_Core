import os
import sys
import re
import json
import subprocess
import tempfile
import shutil
from datetime import datetime
from crewai import Agent, Task, Crew, LLM


def _require_env(name: str) -> str:
    """Fail fast when a required environment variable is missing."""
    v = os.environ.get(name, "").strip()
    if not v:
        raise EnvironmentError(
            f"Missing env var {name}. Set it before running (e.g., OPENAI_API_KEY)."
        )
    return v


# CrewAI/LiteLLM legge OPENAI_API_KEY dall'ambiente.
_require_env("OPENAI_API_KEY")


def make_openai_llm(model_name: str = "gpt-3.5-turbo", temperature: float = 0.5) -> LLM:
    """Centralized LLM factory used by all agents."""
    return LLM(
        model=model_name,
        temperature=temperature,
        max_tokens=4096,
        timeout=1200,
    )


# Models (feel free to tweak)
OPENAI_MODEL_PLANNER = os.environ.get("OPENAI_MODEL_PLANNER", "gpt-3.5-turbo")
OPENAI_MODEL_CODER = os.environ.get("OPENAI_MODEL_CODER", "gpt-3.5-turbo")
OPENAI_MODEL_REVIEW = os.environ.get("OPENAI_MODEL_REVIEW", "gpt-3.5-turbo")
OPENAI_MODEL_ALIGN = os.environ.get("OPENAI_MODEL_ALIGN", "gpt-3.5-turbo")
llm_planner = make_openai_llm(OPENAI_MODEL_PLANNER, temperature=0.5)
llm_coder = make_openai_llm(OPENAI_MODEL_CODER, temperature=0.2)
llm_reviewer = make_openai_llm(OPENAI_MODEL_REVIEW, temperature=0.1)
llm_aligner = make_openai_llm(OPENAI_MODEL_ALIGN, temperature=0.3)

# ============================== AGENTS ==================================== #

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
        • Never output lines starting with 'Thought:' or any reasoning.

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
    verbose=False,
)

coder = Agent(
    role="Coder",
    goal=(
        "Deliver exactly one self-contained, directly runnable PowerShell (.ps1) script "
        "that fulfills the Planner’s steps on a vanilla Windows host."
    ),
    backstory=(
        """
        You are a Senior Software Engineer specialized in PowerShell scripting.
        Your output MUST be only the final .ps1 file contents — no markdown, no prose, no fences, no placeholders, no TODOs.
        LET'S THINK STEP BY STEP (INTERNAL ONLY — do not output your thoughts).

        Hard requirements:
        • Use only built-in Microsoft.PowerShell.* modules.
        • No external dependencies, no installs, no external parameters. Define default values if needed.
        • Structure the script for reliability: optional Param() (only if inputs are explicitly required), helper functions, main execution block,
        and a single well-defined exit point.
        • No explanations, comments about decisions, or extra lines before/after the code.
        • The script must be directly runnable as-is without modifications or external params.
        • LET'S THINK STEP BY STEP. Never output lines starting with 'Thought:' or any reasoning. Output ONLY PowerShell code.
        """
    ),
    llm=llm_coder,
    verbose=False,
)

aligner = Agent(
    role="Code Similarity Aligner",
    goal=(
        "Compare the ORIGINAL (reference) code with the CANDIDATE produced by the Coder and, "
        "only when warranted, generate minimal, precise FIX NOTES that move the candidate closer "
        "to the reference without violating INVARIANTS, altering required behavior, or introducing "
        "new dependencies."
    ),
    backstory=(
        "You are a senior refactoring engineer focused on conservative, semantics-preserving changes. "
        "You prefer small deltas over rewrites, keep public contracts stable, and you are familiar with "
        "PowerShell idioms and code. Your north star is functional parity "
        "with the reference and adherence to the stated invariants, not superficial stylistic matching."
        "• Never output lines starting with 'Thought:' or any reasoning."
    ),
    llm=llm_aligner,
    verbose=False,
)

static_reviewer = Agent(
    role="Static Analysis Reviewer (PSScriptAnalyzer)",
    goal="Given a PowerShell script and a PSScriptAnalyzer report, decide pass/fail. If fail, output minimal fix_notes to make it pass without violating invariants.",
    backstory="Senior Windows PowerShell reviewer specialized in PSScriptAnalyzer diagnostics and surgical fixes.",
    llm=llm_reviewer,
    verbose=False,
)

# ============================== TASKS ===================================== #

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
    markdown=False,
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
        "- THE CODE MUST BE DIRECTLY RUNNABLE AS-IS, WITHOUT THE NEED FOR PARAMETERS TO DEFINE OR BE PASSED.\n"
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

align_task = Task(
    description=(
        "Act as an alignment reviewer.\n\n"
        "INVARIANTS (must NEVER be violated):\n{invariants}\n\n"
        "ORIGINAL CODE (reference / gold):\n<ORIG>\n{original_code}\n</ORIG>\n\n"
        "CANDIDATE CODE (produced by the Coder):\n<CAND>\n{candidate_code}\n</CAND>\n\n"
        "Goals:\n"
        "- Bring the CANDIDATE closer to the ORIGINAL as much as possible.\n"
        "- Preserve behavior required by the plan and respect all INVARIANTS.\n\n"
        "STRICT OUTPUT FORMAT — reply with MINIFIED JSON ONLY (no prose, no code blocks):\n"
        "If already sufficiently aligned:\n"
        '{"status":"ok","reason":"<=200 chars"}\n'
        "Otherwise (when concrete improvements are needed):\n"
        '{"status":"retry","reason":"<=300 chars","fix_notes":"- bullet 1\\n- bullet 2\\n- ..."}\n\n'
        "Rules for fix_notes (when status=retry):\n"
        '- 3–9 bullets, each starting with "- ".\n'
        "- Each bullet is a tiny, actionable delta \n"
        "- LET'S THINK STEP BY STEP; Never output lines starting with 'Thought:' or any reasoning.\n"
        "- Use inline backticks for short identifiers/tokens only;\n"
        "- Reference what/where to change by function/identifier names rather than line numbers (lines may shift).\n"
        "- Never remove or weaken the INVARIANTS; never add new dependencies; keep outputs/side-effects unchanged unless required by the invariants.\n\n"
        "Decision policy:\n"
        '- Return status="ok" when differences are purely cosmetic or do not improve functional/structural equivalence.\n'
        '- Return status="retry" only when small, safe deltas will materially improve equivalence or static-analysis outcomes.'
    ),
    expected_output=(
        "A single JSON object with keys: "
        'status=("ok"|"retry"), reason=string, and if status="retry": fix_notes as a bullet list string.'
    ),
    agent=aligner,
    markdown=False,
)

static_review_task = Task(
    description=(
        "You are the Static Reviewer. Use ONLY the PSScriptAnalyzer report to decide pass/fail.\n\n"
        "ORIGINAL REQUEST:\n{request}\n\n"
        "CANONICAL PLAN:\n{plan}\n\n"
        "INVARIANTS (must not be removed):\n{invariants}\n\n"
        "INPUT CODE:\n<CODE>\n{code}\n</CODE>\n\n"
        "PSScriptAnalyzer REPORT (JSON):\n<REPORT>\n{report}\n</REPORT>\n\n"
        "HARD OUTPUT RULES:\n"
        "- Output MUST be a SINGLE minified JSON object. No prose. No markdown.\n"
        '- PASS => {"verdict":"pass","reason":"<=240 chars"}\n'
        '- FAIL => {"verdict":"fail","reason":"<=240 chars","fix_notes":["<=10 items"]}\n'
        "- fix_notes must be concrete deltas (parse errors first). Do not add dependencies.\n"
    ),
    expected_output="A single minified JSON object with verdict pass/fail.",
    agent=static_reviewer,
    markdown=False,
)

# ============================== UTILS ===================================== #


def _to_text(result) -> str:
    """Normalizes CrewAI results into plain text."""
    try:
        return getattr(result, "raw") if hasattr(result, "raw") else str(result)
    except Exception:
        return str(result)


def extract_powershell_code(text: str) -> str:
    """Extracts script code from a fenced markdown response, if present."""
    if "```" in text:
        m = re.search(
            r"```(?:powershell|ps1|ps)?\s*(.*?)```",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if m:
            return m.group(1).strip()
        return re.sub(r"```", "", text, flags=re.DOTALL).strip()
    return text.strip()


def parse_jsonish(s: str) -> dict | list:
    """Parses strict JSON first, then falls back to the first JSON object in the text."""
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


def parse_verdict_from_json(s: str) -> tuple[str, dict, str]:
    """Returns normalized verdict ('pass'|'fail'|'invalid'), parsed object, and raw text."""
    raw = (s or "").strip()
    parsed = parse_jsonish(raw)
    if isinstance(parsed, list):
        obj = parsed[0] if parsed and isinstance(parsed[0], dict) else {}
    elif isinstance(parsed, dict):
        obj = parsed
    else:
        obj = {}

    verdict = (
        (obj.get("verdict") or obj.get("decision") or obj.get("status") or "")
        .strip()
        .lower()
    )
    if verdict in ("pass", "ok"):
        return "pass", obj, raw
    if verdict in ("fail", "retry"):
        return "fail", obj, raw

    # formato non rispettato
    return "invalid", obj, raw


def plan_to_invariants(plan_text: str) -> str:
    """Converts plan bullets into invariant bullets consumed downstream."""
    lines = []
    for ln in plan_text.splitlines():
        ln = ln.strip()
        if ln.startswith("- "):
            lines.append(f"- {ln[2:]}")
    return "\n".join(lines) if lines else f"- {plan_text.strip()}"


def build_coder_input_bundle(
    request: str,
    plan_text: str,
    invariants_text: str,
    current_code: str,
    fix_notes: str,
    iter_num: int,
    user_change_request: str = "",
) -> dict:
    """Builds the payload expected by the coder task."""
    return {
        "request": request,
        "plan": plan_text,
        "invariants": invariants_text,
        "current_code": current_code or "<none>",
        "fix_notes": fix_notes,
        "iter_num": iter_num,
        "user_change_request": user_change_request or "<none>",
    }


def normalize_fix_notes(raw_fix_notes, enforce_bullets: bool = False) -> str:
    """Normalizes fix notes from either list or string format."""
    if isinstance(raw_fix_notes, list):
        cleaned = [
            str(item).strip().lstrip("- ").strip()
            for item in raw_fix_notes
            if str(item).strip()
        ]
        if enforce_bullets:
            return "\n".join(f"- {item}" for item in cleaned)
        return "\n".join(cleaned)

    text = str(raw_fix_notes or "").strip()
    if enforce_bullets and text:
        return f"- {text.lstrip('- ').strip()}" if not text.startswith("- ") else text
    return text


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
        with tempfile.NamedTemporaryFile(
            "w", suffix=".ps1", delete=False, encoding="utf-8"
        ) as tf:
            tf.write(ps_code)
            temp_ps1 = tf.name

        try:
            proc = subprocess.run(
                [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", temp_ps1],
                capture_output=True,
                timeout=self.timeout,
                text=True,
            )
            out = (proc.stdout or "").strip()
            try:
                return (
                    json.loads(out)
                    if out
                    else {
                        "success": False,
                        "exit_code": -3,
                        "stdout": out,
                        "stderr": "Empty output from analyzer",
                        "runner": "PSScriptAnalyzer",
                        "diagnostics": [],
                    }
                )
            except Exception:
                return {
                    "success": False,
                    "exit_code": -4,
                    "stdout": out,
                    "stderr": (proc.stderr or "").strip()
                    or "Invalid JSON from analyzer",
                    "runner": "PSScriptAnalyzer",
                    "diagnostics": [],
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": "TimeoutExpired",
                "runner": "PSScriptAnalyzer",
                "diagnostics": [],
            }
        finally:
            try:
                os.remove(temp_ps1)
            except Exception:
                pass


# ============================== MAIN ====================================== #


def main():
    default_request = (
        "Create a PowerShell script that prints the machine’s hostname, OS version, "
        "free/used/total disk space for drive C:, and the current date/time, then exits with code 0."
    )
    # --- parse args: --ref <path> + request libero ---
    args = sys.argv[1:]

    def _pop(flag: str) -> str | None:
        if flag in args:
            i = args.index(flag)
            if i + 1 < len(args):
                v = args[i + 1]
                del args[i : i + 2]
                return v
        return None

    ref_path = _pop("--ref")

    request = " ".join(args) if args else default_request
    ref_code = ""
    if ref_path and os.path.exists(ref_path):
        with open(ref_path, "r", encoding="utf-8-sig") as f:
            ref_code = f.read()
    # 1) PLANNING
    print("--- 1) PLANNING ---")
    plan_crew = Crew(agents=[planner], tasks=[plan_task])
    plan_res = plan_crew.kickoff(inputs={"request": request})
    plan_text = _to_text(plan_res).strip()
    print(plan_text)
    invariants_text = plan_to_invariants(plan_text)

    code_crew = Crew(agents=[coder], tasks=[code_task])
    static_review_crew = Crew(agents=[static_reviewer], tasks=[static_review_task])

    max_static_iters = 3
    max_align_rounds = 3
    max_global_iters = 3

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_code = ""
    script_path = ""
    fix_notes = "Initial implementation from the plan."
    iter_num = 0

    def _save_script(code: str, it: int) -> str:
        name = f"generated_{timestamp}_iter{it}.ps1"
        path = os.path.join(os.getcwd(), name)
        with open(path, "w", encoding="utf-8-sig") as f:
            f.write(code)
        print(f"Salvato: {path}")
        return path

    align_crew = (
        Crew(agents=[aligner], tasks=[align_task]) if ref_code.strip() else None
    )

    global_completed = False
    for g in range(1, max_global_iters + 1):
        print(f"\n=== GLOBAL ITERATION {g} / {max_global_iters} ===")

        # === STATIC LOOP: coder → PSSA → static reviewer (max 3) ===
        for s in range(1, max_static_iters + 1):
            iter_num += 1
            print(f"\n=== STATIC ITERATION {s} / {max_static_iters} ===")
            print("--- CODING ---")
            bundle = build_coder_input_bundle(
                request=request,
                plan_text=plan_text,
                invariants_text=invariants_text,
                current_code=script_code if script_code else "",
                fix_notes=fix_notes,
                iter_num=iter_num,
            )
            code_res = code_crew.kickoff(inputs=bundle)
            script_code = extract_powershell_code(_to_text(code_res))
            script_path = _save_script(script_code, iter_num)

            print("--- STATIC ANALYSIS (PSScriptAnalyzer) ---")
            runner = PSScriptAnalyzerRunner(script_path, timeout_sec=180)
            report = runner.run()
            print(json.dumps(report, indent=2, ensure_ascii=False))

            if report.get("success"):
                print("Static gate: PASS (PSScriptAnalyzer).")
                break

            if report.get("exit_code") == -2:
                raise RuntimeError(
                    report.get("stderr") or "PSScriptAnalyzer non disponibile."
                )

            review_inputs = {
                "request": request,
                "plan": plan_text,
                "invariants": invariants_text,
                "code": script_code,
                "report": json.dumps(report, ensure_ascii=False),
            }

            review_res = static_review_crew.kickoff(inputs=review_inputs)
            _verdict, obj, _raw = parse_verdict_from_json(_to_text(review_res).strip())

            fix_list = obj.get("fix_notes") if isinstance(obj, dict) else None
            if fix_list:
                fix_notes = normalize_fix_notes(fix_list, enforce_bullets=True)
            else:
                fix_notes = (
                    "Fix the previous script to pass PSScriptAnalyzer while preserving the plan and invariants. "
                    f"Errors:\n{report.get('stderr','')}\n"
                    "Do NOT remove any invariant. Apply minimal changes."
                )

            print("--- STATIC FIX NOTES ---")
            print(fix_notes)
        else:
            print(
                "Static analysis did not pass within max iterations; continuing anyway."
            )

        # === ALIGNMENT STAGE (global restart if fixes are needed) ===
        if ref_code.strip():
            alignment_ok = False
            alignment_restart = False
            for a in range(1, max_align_rounds + 1):
                print(f"--- ALIGNMENT ROUND {a}/{max_align_rounds} ---")
                align_inputs = {
                    "invariants": invariants_text,
                    "original_code": ref_code,
                    "candidate_code": script_code,
                }
                align_res = align_crew.kickoff(inputs=align_inputs)
                align_raw = parse_jsonish(_to_text(align_res).strip())
                if isinstance(align_raw, list):
                    align_json = (
                        align_raw[0]
                        if align_raw and isinstance(align_raw[0], dict)
                        else {}
                    )
                elif isinstance(align_raw, dict):
                    align_json = align_raw
                else:
                    align_json = {}
                status = (align_json.get("status") or "").lower()

                if status == "ok":
                    print(
                        "Alignment: il candidato è sufficientemente simile al reference."
                    )
                    alignment_ok = True
                    break

                fix_notes = normalize_fix_notes(
                    align_json.get("fix_notes"), enforce_bullets=True
                )

                if not fix_notes:
                    print(
                        "Alignment LLM: nessuna FIX NOTES fornita; interrompo l'allineamento."
                    )
                    break

                with open(
                    f"alignnotes_{timestamp}_round{a}.txt", "w", encoding="utf-8"
                ) as f:
                    f.write(fix_notes + "\n")

                print("--- ALIGNMENT FIX NOTES ---")
                print(fix_notes)
                alignment_restart = True
                break

            if alignment_ok:
                global_completed = True
                break

            if alignment_restart:
                if g == max_global_iters:
                    print(
                        "Alignment retries exhausted; continuing with latest candidate."
                    )
                    global_completed = True
                    break
                continue

            raise RuntimeError(
                "Alignment stage could not complete due to missing fix notes."
            )
        else:
            global_completed = True
            break

        if global_completed:
            break
    else:
        print("Global iteration budget exhausted; continuing with latest candidate.")

    print("Script finale:", script_path)

    return 0


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
