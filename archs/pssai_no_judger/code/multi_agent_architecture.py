import os
import sys
import re
import json
import subprocess
import tempfile
import shutil
import time
import atexit
from datetime import datetime, timezone
from crewai import Agent, Task, Crew, LLM

# ========================= PSANDMAN FIXED PATHS ========================= #
# Percorsi fissi richiesti (nessuna env var necessaria per input/output).
PSANDMAN_BASE_DIR      = r"I:\PATH\TO\psandman"
PSANDMAN_SCRIPT_PATH   = os.path.join(PSANDMAN_BASE_DIR, "psandman.py")
PSANDMAN_INPUT_DIR     = os.path.join(PSANDMAN_BASE_DIR, "inputs")
PSANDMAN_OUTPUT_ROOT   = os.path.join(PSANDMAN_BASE_DIR, "output")
PSANDMAN_XMLPWSH_DIR   = os.path.join(PSANDMAN_OUTPUT_ROOT, "xml-pwsh")


def _require_env(name: str) -> str:
    """Fail fast when a required environment variable is missing."""
    v = os.environ.get(name, "").strip()
    if not v:
        raise EnvironmentError(f"Missing env var {name}. Set it before running (e.g., OPENAI_API_KEY).")
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
OPENAI_MODEL_CODER   = os.environ.get("OPENAI_MODEL_CODER",   "gpt-3.5-turbo")
OPENAI_MODEL_REVIEW  = os.environ.get("OPENAI_MODEL_REVIEW",  "gpt-3.5-turbo")
llm_planner        = make_openai_llm(OPENAI_MODEL_PLANNER, temperature=0.5)
llm_coder          = make_openai_llm(OPENAI_MODEL_CODER,   temperature=0.2)
llm_reviewer       = make_openai_llm(OPENAI_MODEL_REVIEW,  temperature=0.1)
llm_change_planner = make_openai_llm(OPENAI_MODEL_PLANNER, temperature=0.5)

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

dyn_reviewer = Agent(
    role="Dynamic Execution Reviewer",
    goal=(
        "Given a PowerShell script, its CANONICAL PLAN/INVARIANTS, and the DYNAMIC EXECUTION LOGS produced by psandman, "
        "decide pass/fail. If fail, propose a minimally changed UPDATED PLAN (6–9 bullets) and optional FIX NOTES "
        "to help the Coder converge."
    ),
    backstory=(
        "Senior Windows engineer specialized in execution traces and PowerShell operational logs. "
        "You diagnose runtime errors, missing outputs, wrong sequencing, and environment/permission issues based on logs."
    ),
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
        "Never output lines starting with 'Thought:' or any reasoning."
    ),
    llm=llm_change_planner,
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

dyn_review_task = Task(
    description=(
        "You are the Dynamic Reviewer. Decide whether the *script logic* AND the *observed execution evidence* "
        "are coherent with the user_request and plan.\n\n"
        "ORIGINAL REQUEST:\n{request}\n\n"
        "CANONICAL PLAN:\n{plan}\n\n"
        "INVARIANTS (must not be removed):\n{invariants}\n\n"
        "INPUT CODE:\n<CODE>\n{code}\n</CODE>\n\n"
        "DYNAMIC EVIDENCE PACK (text timeline produced by compact_dyn_report; includes EXECUTION SUMMARY and TIMELINE):\n"
        "<EVIDENCE>\n{dyn_report}\n</EVIDENCE>\n\n"
        "How to read the evidence:\n"
        "- The pack begins with an 'EXECUTION SUMMARY' section (Exit Code, Logic Errors, Log Density).\n"
        "- Then a 'TIMELINE' section with lines formatted as: [HH:MM:SS] [TAG] Message.\n"
        "- If the evidence is JSON-escaped (e.g., contains \\n and surrounding quotes), interpret \\n as newlines and ignore the quotes.\n\n"
        "Interpretation rules:\n"
        "- Do NOT assume a step happened unless there is positive evidence in the TIMELINE (a line that clearly matches the behavior).\n"
        "- Treat Exit Code and [FAIL] lines as strong signals of execution/logic errors, but still cite the exact lines.\n"
        "- If the required logic exists in <CODE> but there is no supporting TIMELINE evidence, state 'code-path not exercised' "
        "(not 'missing logic') and FAIL with must_change describing how to make that path run by default "
        "(e.g., call the main function automatically, remove unreachable gating, ensure the script executes without requiring parameters).\n"
        "- If neither <CODE> nor the TIMELINE contains the required behavior, state 'missing logic' and FAIL with must_change describing what to implement.\n\n"
         "- If the code logic is fundamentally disconnected from the plan (e.g., creating a function definition instead of a one-liner), "
        "diagnose this as a likely generation or prompt interpretation failure. In this case, the 'must_change' field should contain "
        "specific suggestions on how to REPHRASE THE ORIGINAL REQUEST to get the desired code from the AI model, rather than suggesting code fixes.\n"
        "HARD OUTPUT RULES:\n"
        "- Output MUST be a SINGLE minified JSON object. No prose. No markdown. No code.\n"
        "- Schema:\n"
        "  PASS => {\"verdict\":\"pass\",\"reason\":\"<=240 chars\",\"evidence\":[\"<=6 items\"]}\n"
        " FAIL => {\"verdict\":\"fail\",\"reason\":\"<=240 chars\",\"evidence\":[\"<=10 items\"],\"must_change\":[\"<=10 items\"]}\n"        "- Evidence MUST cite concrete items using either:\n"
        "- The 'must_change' array can contain either code fixes OR, if a generation failure is diagnosed, specific suggestions on how to REPHRASE THE ORIGINAL REQUEST.\n"
        "- If there is no meaningful TIMELINE evidence for any required observable behavior, verdict MUST be fail and must_change MUST request "
        "either adding runtime verification (post-check) or ensuring the relevant code path executes by default.\n"
    ),
    expected_output="A single minified JSON object with verdict pass/fail.",
    agent=dyn_reviewer,
    markdown=False,
)

dyn_fix_notes_task = Task(
    description=(
        "Convert review_json into actionable fix notes mapped to plan bullets.\n\n"
        "INPUTS:\n"
        "• ORIGINAL REQUEST:\n{request}\n\n"
        "• CANONICAL PLAN (read-only):\n{plan}\n\n"
        "• INVARIANTS (must keep):\n{invariants}\n\n"
        "• CURRENT SCRIPT (read-only):\n<CODE>\n{current_code}\n</CODE>\n\n"
        "• DYNAMIC REPORT (compact JSON):\n{dyn_report}\n\n"
        "• DIAGNOSIS (text):\n{diagnosis}\n\n"
        "TASK:\n"
        "Translate the DIAGNOSIS into FIX NOTES as precise deltas to the CANONICAL PLAN.\n\n"
        "OUTPUT RULES (STRICT):\n"
        "- Return 3–9 lines.\n"
        "- Each line MUST start with '- '.\n"
        "- Use imperative edits (replace/insert/remove/move/rename) naming exact objects/methods/lines/identifiers when possible.\n"
        "- Do NOT add new concerns beyond fixing what DIAGNOSIS indicates.\n"
        "- Do NOT introduce new outputs/logs/params unless required by the request.\n"
        "- Preserve semantics as much as possible while fixing the observed failure.\n"
        "- No code.\n"
    ),
    expected_output="3–9 lines starting with '- Bullet <n>:' describing deltas to the plan. No code.",
    agent=change_planner,
    markdown=False,
)

dyn_fix_crew = Crew(agents=[change_planner], tasks=[dyn_fix_notes_task])


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
        "- PASS => {\"verdict\":\"pass\",\"reason\":\"<=240 chars\"}\n"
        "- FAIL => {\"verdict\":\"fail\",\"reason\":\"<=240 chars\",\"fix_notes\":[\"<=10 items\"]}\n"
        "- fix_notes must be concrete deltas (parse errors first). Do not add dependencies.\n"
    ),
    expected_output="A single minified JSON object with verdict pass/fail.",
    agent=static_reviewer,
    markdown=False,
)

# ============================== UTILS ===================================== #

def compact_dyn_report(report: dict) -> str:
    """Compresses psandman events into a bounded-size timeline for the reviewer."""
    raw_events = report.get("events", [])
    
    ignore_cmds = {
        "Set-StrictMode", "Out-Default", "Get-Command", "Get-FormatData", 
        "Out-String", "Format-Default", "Check-In", "Measure-Object", 
        "Select-Object", "Get-Help"
    }

    # BUDGETING: Lasciamo spazio per prompt e codice.
    # 12000 chars sono circa 3000-4000 token.
    MAX_OUTPUT_CHARS = 12000 
    
    timeline = []
    error_count = 0
    current_chars = 0
    
    # Variabili per deduplicazione (folding)
    last_msg = None
    last_tag = None
    repeat_count = 0

    def flush_repeat():
        nonlocal repeat_count, current_chars
        if repeat_count > 0:
            line = f"   ... (Previous event repeated {repeat_count} times) ..."
            timeline.append(line)
            current_chars += len(line)
            repeat_count = 0

    for e in raw_events:
        # Check budget preventivo
        if current_chars >= MAX_OUTPUT_CHARS:
            flush_repeat()
            timeline.append("\n[!!!] LOG TRUNCATED: Token budget exceeded. Check full logs manually if needed.")
            break

        msg = e.get("Msg", "")
        tag = e.get("Tag", "INFO")
        
        # Filtro comandi inutili
        if any(ign in msg for ign in ignore_cmds):
            continue
            
        # Conteggio errori
        if tag == "FAIL" or "Error" in msg:
            error_count += 1
            tag = "FAIL"

        # Logica di DEDUPLICAZIONE
        # Se il messaggio e il tag sono IDENTICI al precedente, incrementa contatore
        if msg == last_msg and tag == last_tag:
            repeat_count += 1
            continue
        
        # Se siamo qui, l'evento è nuovo: flushiamo i precedenti se necessario
        flush_repeat()
        
        ts = e.get("Time", "").split("T")[-1][:8]
        line = f"[{ts}] [{tag}] {msg}"
        
        timeline.append(line)
        current_chars += len(line)
        
        # Aggiorna memoria per il prossimo giro
        last_msg = msg
        last_tag = tag

    # Flush finale (se il log finisce con ripetizioni)
    flush_repeat()

    header = f"""
EXECUTION SUMMARY:
- Exit Code: {report.get('exit_code')}
- Logic Errors: {error_count}
- Log Density: {len(timeline)} unique lines (deduplicated).

TIMELINE:
"""
    return header + "\n".join(timeline)

def _to_text(result) -> str:
    """Normalizes CrewAI results into plain text."""
    try:
        return getattr(result, "raw") if hasattr(result, "raw") else str(result)
    except Exception:
        return str(result)


def extract_powershell_code(text: str) -> str:
    """Extracts script code from a fenced markdown response, if present."""
    if "```" in text:
        m = re.search(r"```(?:powershell|ps1|ps)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
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

    verdict = (obj.get("verdict") or obj.get("decision") or obj.get("status") or "").strip().lower()
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


def build_coder_input_bundle(request: str, plan_text: str, invariants_text: str,
                             current_code: str, fix_notes: str, iter_num: int,
                             user_change_request: str = "") -> dict:
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
        cleaned = [str(item).strip().lstrip("- ").strip() for item in raw_fix_notes if str(item).strip()]
        if enforce_bullets:
            return "\n".join(f"- {item}" for item in cleaned)
        return "\n".join(cleaned)

    text = str(raw_fix_notes or "").strip()
    if enforce_bullets and text:
        return f"- {text.lstrip('- ').strip()}" if not text.startswith("- ") else text
    return text


class PsandmanRunner:
    """
    Runs psandman by copying the candidate script into the fixed inputs folder and
    collecting XML output logs from PSANDMAN_XMLPWSH_DIR (e.g., ...\\output\\xml-pwsh).

    After collecting and extracting a compact event summary, it:
      - removes the tested script from inputs
      - cleans ALL subfolders/files under PSANDMAN_OUTPUT_ROOT
      - cleans ALL subfolders/files under PSANDMAN_XMLPWSH_DIR
    """
    def __init__(self, guest_user: str, guest_pass: str, timeout_sec: int = 1800):
        self.psandman_path = os.path.abspath(PSANDMAN_SCRIPT_PATH)
        self.workdir = os.path.abspath(PSANDMAN_BASE_DIR)
        self.input_dir = os.path.abspath(PSANDMAN_INPUT_DIR)
        self.output_root = os.path.abspath(PSANDMAN_OUTPUT_ROOT)
        self.output_sources = [os.path.abspath(PSANDMAN_XMLPWSH_DIR)]
        self.guest_user = guest_user
        self.guest_pass = guest_pass
        self.timeout = timeout_sec

    def _clean_dir(self, path: str):
        os.makedirs(path, exist_ok=True)
        for name in os.listdir(path):
            p = os.path.join(path, name)
            try:
                if os.path.isdir(p):
                    shutil.rmtree(p)
                else:
                    os.remove(p)
            except Exception:
                pass

    def _collect_xml_files(self) -> list[str]:
        xmls = []
        for src in self.output_sources:
            if os.path.isdir(src):
                for root, _dirs, files in os.walk(src):
                    for fn in files:
                        if fn.lower().endswith(".xml"):
                            xmls.append(os.path.join(root, fn))
        return sorted(set(xmls))

    def _extract_events_from_xml(self, xml_path: str, max_events: int = 1000) -> list[dict]:
        import xml.etree.ElementTree as ET
        import re

        def _strip_ns(tag: str) -> str:
            return tag.split("}", 1)[-1] if "}" in tag else tag

        # REGEX OTTIMIZZATA: Cattura solo i primi 150 caratteri del valore di un parametro
        # Questo previene l'esplosione dei token su payload base64 o contenuti file lunghi
        re_binding = re.compile(r'ParameterBinding\(([^)]+)\):\s*name="([^"]+)";\s*value="([^"]{0,150})') 
        re_cmd = re.compile(r'CommandInvocation\(([^)]+)\)')
        re_error = re.compile(r'(TerminatingError|NonTerminatingError)\(([^)]+)\):\s*"(.*)"')

        events = []
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except Exception:
            return events

        for ev in root.iter():
            if _strip_ns(ev.tag) != "Event":
                continue

            # --- 1. Header ---
            eid, time_created, level = None, None, None
            sys_node = next((ch for ch in list(ev) if _strip_ns(ch.tag) == "System"), None)
            if sys_node:
                for ch in list(sys_node):
                    tag = _strip_ns(ch.tag)
                    if tag == "EventID": eid = ch.text.strip()
                    elif tag == "TimeCreated": time_created = ch.attrib.get("SystemTime")
                    elif tag == "Level": level = ch.text.strip()

            # --- 2. Data ---
            data_map = {}
            edata_node = next((ch for ch in list(ev) if _strip_ns(ch.tag) == "EventData"), None)
            if edata_node:
                for d in list(edata_node):
                    if _strip_ns(d.tag) == "Data":
                        name = d.attrib.get("Name")
                        if name and d.text:
                            data_map[name] = d.text.strip()

            # --- 3. Parsing e Troncamento ---
            semantic_msg = ""
            tag_type = "INFO"

            if eid == "4104": # ScriptBlock
                tag_type = "CODE"
                script_text = data_map.get("ScriptBlockText", "")
                if "SIG # Begin signature block" in script_text:
                    semantic_msg = "<Signature Block Skipped>"
                else:
                    # Prendi solo la prima riga significativa, max 200 chars
                    lines = [l.strip() for l in script_text.splitlines() if l.strip()]
                    if lines:
                        first_line = lines[0][:200]
                        semantic_msg = f"Exec ScriptBlock: {first_line}..." if len(lines) > 1 else first_line

            elif eid == "4103": # Pipeline
                tag_type = "EXEC"
                payload = data_map.get("Payload", "")
                
                cmd_match = re_cmd.search(payload)
                err_match = re_error.search(payload)
                
                if cmd_match:
                    cmd_name = cmd_match.group(1)
                    # Estrai parametri troncati
                    params = []
                    for m in re_binding.findall(payload):
                        # m[1] = param name, m[2] = truncated value
                        val = m[2] + ("..." if len(m[2]) == 150 else "")
                        params.append(f'-{m[1]} "{val}"')
                    
                    semantic_msg = f"CMD: {cmd_name} {' '.join(params)}"
                
                if err_match:
                    tag_type = "FAIL"
                    err_text = err_match.group(3)[:300] # Max 300 chars per errore
                    sep = " | " if semantic_msg else ""
                    semantic_msg = f"{semantic_msg}{sep}ERROR: {err_text}"
                
                if not semantic_msg and payload:
                    semantic_msg = payload[:200].replace("\n", " | ")

            elif eid == "4100": # Error
                tag_type = "FAIL"
                msg = data_map.get('Message') or data_map.get('Payload') or ""
                semantic_msg = f"ERROR: {msg[:300]}"

            # Scarta eventi vuoti o inutili
            if not semantic_msg or "Host Name =" in semantic_msg:
                continue

            events.append({
                "EventID": eid,
                "Time": time_created,
                "Tag": tag_type,
                "Msg": semantic_msg
            })
            
            if len(events) >= max_events:
                break
                
        return events

    def run(self, host_script_path: str) -> dict:
        start = time.time()

        # Pre-clean to avoid mixing logs across runs
        self._clean_dir(self.input_dir)
        self._clean_dir(self.output_root)

        # NON creare xml-pwsh: deve crearla psandman. Se esiste da run precedente, eliminala completamente.
        try:
            if os.path.isdir(PSANDMAN_XMLPWSH_DIR):
                shutil.rmtree(PSANDMAN_XMLPWSH_DIR)
        except Exception:
            pass

        src = os.path.abspath(host_script_path)
        dst = os.path.join(self.input_dir, os.path.basename(src))

        try:
            try:
                shutil.copy2(src, dst)
            except Exception:
                with open(src, "r", encoding="utf-8-sig", errors="replace") as fsrc:
                    data = fsrc.read()
                with open(dst, "w", encoding="utf-8-sig") as fdst:
                    fdst.write(data)

            # --- force UTF-8 for psandman output (avoids UnicodeEncodeError on Windows pipes) ---
            env = os.environ.copy()
            env["PYTHONUTF8"] = "1"
            env["PYTHONIOENCODING"] = "utf-8"

            cmd = [
                sys.executable, "-X", "utf8",
                self.psandman_path,
                "--snapshot", "post-setup-20260126",
                "--debug",
                "--guest-user", self.guest_user,
                "--guest-pass", self.guest_pass,
            ]

            try:
                proc = subprocess.run(
                    cmd,
                    cwd=self.workdir,
                    env=env,
                    capture_output=True,
                    timeout=self.timeout
                )
            except subprocess.TimeoutExpired as e:
                dur_ms = int((time.time() - start) * 1000)
                return {
                    "success": False,
                    "runner": "psandman",
                    "exit_code": -1,
                    "stdout": (e.stdout.decode("utf-8", errors="replace") if e.stdout else ""),
                    "stderr": "TimeoutExpired",
                    "duration_ms": dur_ms,
                    "input_dir": self.input_dir,
                    "output_sources": self.output_sources,
                    "xml_files": [],
                    "events": [],
                }

            def _dec(b: bytes) -> str:
                for enc in ("utf-8", "cp1252", "latin-1"):
                    try:
                        return b.decode(enc)
                    except UnicodeDecodeError:
                        pass
                return b.decode("utf-8", errors="replace")

            xmls = self._collect_xml_files()
            all_events = []
            for xp in xmls:
                all_events.extend(self._extract_events_from_xml(xp, max_events=200))

            dur_ms = int((time.time() - start) * 1000)
            payload = {
                "success": (proc.returncode == 0 and len(xmls) > 0),
                "runner": "psandman",
                "exit_code": proc.returncode,
                "stdout": _dec(proc.stdout).strip(),
                "stderr": _dec(proc.stderr).strip(),
                "duration_ms": dur_ms,
                "input_dir": self.input_dir,
                "output_sources": self.output_sources,
                "xml_files": [
                    {
                        "path": os.path.relpath(p, PSANDMAN_BASE_DIR),
                        "size": (os.path.getsize(p) if os.path.exists(p) else None),
                    }
                    for p in xmls
                ],
                "events": all_events[:600],
            }
            return payload
        finally:
            # Post-clean as requested: remove tested script from inputs and wipe output folders
            try:
                if os.path.exists(dst):
                    os.remove(dst)
            except Exception:
                pass
            try:
                self._clean_dir(self.output_root)
            except Exception:
                pass
            try:
                if os.path.isdir(PSANDMAN_XMLPWSH_DIR):
                    shutil.rmtree(PSANDMAN_XMLPWSH_DIR)
            except Exception:
                pass

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
        with tempfile.NamedTemporaryFile('w', suffix='.ps1', delete=False, encoding='utf-8') as tf:
            tf.write(ps_code)
            temp_ps1 = tf.name

        try:
            proc = subprocess.run(
                [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", temp_ps1],
                capture_output=True,
                timeout=self.timeout,
                text=True
            )
            out = (proc.stdout or "").strip()
            try:
                return json.loads(out) if out else {
                    "success": False, "exit_code": -3, "stdout": out, "stderr": "Empty output from analyzer", "runner": "PSScriptAnalyzer", "diagnostics": []
                }
            except Exception:
                return {
                    "success": False,
                    "exit_code": -4,
                    "stdout": out,
                    "stderr": (proc.stderr or "").strip() or "Invalid JSON from analyzer",
                    "runner": "PSScriptAnalyzer",
                    "diagnostics": []
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False, "exit_code": -1, "stdout": "", "stderr": "TimeoutExpired", "runner": "PSScriptAnalyzer", "diagnostics": []
            }
        finally:
            try: os.remove(temp_ps1)
            except Exception: pass

# ============================== MAIN ====================================== #

def _utc_now_iso() -> str:
    """Returns current UTC timestamp in ISO-8601 with millisecond precision."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class ExecutionObserver:
    """
    Captures per-run observability:
    - UTC timestamps for every agent transition
    - start/end + duration for agent and stage executions
    - total run duration
    """
    def __init__(self, run_id: str, output_dir: str):
        self.run_id = run_id
        self.output_path = os.path.join(output_dir, f"observability_{run_id}.json")
        self.events = []
        self.last_agent = None
        self._closed = False
        self._seq = 0
        self._start_perf = time.perf_counter()
        self._started_at = _utc_now_iso()
        self._record("run_start", detail="Execution started")
        atexit.register(self._flush_on_exit)

    def _record(self, event: str, **fields):
        self._seq += 1
        entry = {
            "seq": self._seq,
            "event": event,
            "timestamp_utc": _utc_now_iso(),
            "offset_ms": int((time.perf_counter() - self._start_perf) * 1000),
        }
        entry.update(fields)
        self.events.append(entry)
        return entry

    def note(self, event: str, **fields):
        self._record(event, **fields)

    def _flush_on_exit(self):
        if self._closed:
            return
        try:
            self.finish(status="aborted", exit_code=1, final_script_path="")
        except Exception:
            pass

    def run_agent(self, agent_name: str, step: str, call):
        from_agent = self.last_agent or "START"
        self._record(
            "agent_transition",
            from_agent=from_agent,
            to_agent=agent_name,
            step=step,
        )
        print(f"[OBS] {from_agent} -> {agent_name} | step={step}")

        self._record("agent_start", agent=agent_name, step=step)
        start = time.perf_counter()
        try:
            result = call()
        except Exception as exc:
            dur_ms = int((time.perf_counter() - start) * 1000)
            self._record(
                "agent_end",
                agent=agent_name,
                step=step,
                status="error",
                duration_ms=dur_ms,
                error=str(exc),
            )
            raise

        dur_ms = int((time.perf_counter() - start) * 1000)
        self._record(
            "agent_end",
            agent=agent_name,
            step=step,
            status="ok",
            duration_ms=dur_ms,
        )
        print(f"[OBS] {agent_name} completed in {dur_ms} ms | step={step}")
        self.last_agent = agent_name
        return result

    def run_stage(self, stage: str, call):
        self._record("stage_start", stage=stage)
        start = time.perf_counter()
        try:
            result = call()
        except Exception as exc:
            dur_ms = int((time.perf_counter() - start) * 1000)
            self._record(
                "stage_end",
                stage=stage,
                status="error",
                duration_ms=dur_ms,
                error=str(exc),
            )
            raise

        dur_ms = int((time.perf_counter() - start) * 1000)
        self._record(
            "stage_end",
            stage=stage,
            status="ok",
            duration_ms=dur_ms,
        )
        print(f"[OBS] {stage} completed in {dur_ms} ms")
        return result

    def finish(self, status: str, exit_code: int, final_script_path: str = ""):
        if self._closed:
            return
        self._closed = True
        total_ms = int((time.perf_counter() - self._start_perf) * 1000)
        finished_at = _utc_now_iso()
        self._record(
            "run_end",
            status=status,
            exit_code=exit_code,
            total_duration_ms=total_ms,
            final_script_path=final_script_path,
        )
        payload = {
            "run_id": self.run_id,
            "started_at_utc": self._started_at,
            "finished_at_utc": finished_at,
            "status": status,
            "exit_code": exit_code,
            "total_duration_ms": total_ms,
            "final_script_path": final_script_path,
            "events": self.events,
        }
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"[OBS] Total execution duration: {total_ms} ms")
        print(f"[OBS] Observability report: {self.output_path}")

def main():
    run_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    observer = ExecutionObserver(run_id=run_id, output_dir=os.getcwd())
    script_path = ""

    try:
        default_request = (
            "Create a PowerShell script that prints the machine’s hostname, OS version, "
            "free/used/total disk space for drive C:, and the current date/time, then exits with code 0."
        )
        # --- parse args: --ref <path> (optional: --guest-user/--guest-pass) + request libero ---
        args = sys.argv[1:]

        def _pop(flag: str) -> str | None:
            if flag in args:
                i = args.index(flag)
                if i + 1 < len(args):
                    v = args[i + 1]
                    del args[i:i+2]
                    return v
            return None

        ref_path = _pop("--ref")
        guest_user = _pop("--guest-user") or "rizz"
        guest_pass = _pop("--guest-pass") or "rizz"

        request = " ".join(args) if args else default_request
        observer.note(
            "inputs_parsed",
            has_ref=bool(ref_path),
            guest_user=guest_user,
            request_chars=len(request),
        )

        # Validate fixed psandman paths
        if not os.path.isdir(PSANDMAN_BASE_DIR):
            raise FileNotFoundError(f"PSANDMAN_BASE_DIR not found: {PSANDMAN_BASE_DIR}")
        if not os.path.isfile(PSANDMAN_SCRIPT_PATH):
            raise FileNotFoundError(f"psandman.py not found at: {PSANDMAN_SCRIPT_PATH}")
        if not os.path.isdir(PSANDMAN_INPUT_DIR):
            os.makedirs(PSANDMAN_INPUT_DIR, exist_ok=True)

        ref_code = ""
        if ref_path and os.path.exists(ref_path):
            with open(ref_path, "r", encoding="utf-8-sig") as f:
                ref_code = f.read()
        observer.note(
            "reference_loaded",
            has_reference=bool(ref_code.strip()),
            ref_path=ref_path or "",
        )

        # 1) PLANNING
        print("--- 1) PLANNING ---")
        plan_crew = Crew(agents=[planner], tasks=[plan_task])
        plan_res = observer.run_agent(
            "planner",
            "planning",
            lambda: plan_crew.kickoff(inputs={"request": request}),
        )
        plan_text = _to_text(plan_res).strip()
        print(plan_text)
        invariants_text = plan_to_invariants(plan_text)

        code_crew = Crew(agents=[coder], tasks=[code_task])
        dyn_review_crew = Crew(agents=[dyn_reviewer], tasks=[dyn_review_task])
        static_review_crew = Crew(agents=[static_reviewer], tasks=[static_review_task])

        max_static_iters = 3
        max_dynamic_iters = 1
        max_global_iters = 3
        observer.note(
            "execution_config",
            max_static_iters=max_static_iters,
            max_dynamic_iters=max_dynamic_iters,
            max_global_iters=max_global_iters,
        )

        timestamp = run_id
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

        # Global cycle: static hardening first, then dynamic execution evidence.
        for g in range(1, max_global_iters + 1):
            observer.note("global_iteration_start", global_iteration=g)
            print(f"\n=== GLOBAL ITERATION {g} / {max_global_iters} ===")

            # === STATIC LOOP: coder -> PSSA -> static reviewer (max 3) ===
            for s in range(1, max_static_iters + 1):
                observer.note("static_iteration_start", global_iteration=g, static_iteration=s)
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
                code_res = observer.run_agent(
                    "coder",
                    f"static_coding_g{g}_s{s}_iter{iter_num}",
                    lambda: code_crew.kickoff(inputs=bundle),
                )
                script_code = extract_powershell_code(_to_text(code_res))
                script_path = observer.run_stage(
                    f"save_script_iter{iter_num}",
                    lambda: _save_script(script_code, iter_num),
                )

                print("--- STATIC ANALYSIS (PSScriptAnalyzer) ---")
                runner = PSScriptAnalyzerRunner(script_path, timeout_sec=180)
                report = observer.run_stage(
                    f"psscriptanalyzer_g{g}_s{s}",
                    lambda: runner.run(),
                )
                print(json.dumps(report, indent=2, ensure_ascii=False))
                observer.note(
                    "static_gate_result",
                    global_iteration=g,
                    static_iteration=s,
                    success=bool(report.get("success")),
                    exit_code=report.get("exit_code"),
                )

                if report.get("success"):
                    print("Static gate: PASS (PSScriptAnalyzer).")
                    observer.note("static_iteration_end", global_iteration=g, static_iteration=s, verdict="pass")
                    break

                if report.get("exit_code") == -2:
                    raise RuntimeError(report.get("stderr") or "PSScriptAnalyzer non disponibile.")

                review_inputs = {
                    "request": request,
                    "plan": plan_text,
                    "invariants": invariants_text,
                    "code": script_code,
                    "report": json.dumps(report, ensure_ascii=False),
                }

                review_res = observer.run_agent(
                    "static_reviewer",
                    f"static_review_g{g}_s{s}_iter{iter_num}",
                    lambda: static_review_crew.kickoff(inputs=review_inputs),
                )
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
                observer.note("static_iteration_end", global_iteration=g, static_iteration=s, verdict="fail")
            else:
                print("Static analysis did not pass within max iterations; continuing anyway.")
                observer.note("static_loop_exhausted", global_iteration=g, max_static_iters=max_static_iters)

            # === DYNAMIC LOOP: psandman -> dynamic reviewer (max 3) ===
            fix_notes = "Proceed to dynamic validation based on runtime evidence."
            for d in range(1, max_dynamic_iters + 1):
                observer.note("dynamic_iteration_start", global_iteration=g, dynamic_iteration=d)
                print(f"\n=== DYNAMIC ITERATION {d} / {max_dynamic_iters} ===")

                print("--- DYNAMIC ANALYSIS (psandman) ---")
                runner = PsandmanRunner(
                    guest_user=guest_user,
                    guest_pass=guest_pass,
                    timeout_sec=1800,
                )
                report = observer.run_stage(
                    f"psandman_g{g}_d{d}",
                    lambda: runner.run(script_path),
                )
                print(json.dumps(report, indent=2, ensure_ascii=False))
                observer.note(
                    "dynamic_gate_result",
                    global_iteration=g,
                    dynamic_iteration=d,
                    success=bool(report.get("success")),
                    exit_code=report.get("exit_code"),
                    duration_ms=report.get("duration_ms"),
                )

                print("--- DYNAMIC REVIEW ---")
                compact = compact_dyn_report(report)
                review_inputs = {
                    "request": request,
                    "plan": plan_text,
                    "invariants": invariants_text,
                    "code": script_code,
                    "dyn_report": json.dumps(compact, ensure_ascii=False),
                }

                review_res = observer.run_agent(
                    "dynamic_reviewer",
                    f"dynamic_review_g{g}_d{d}_iter{iter_num}",
                    lambda: dyn_review_crew.kickoff(inputs=review_inputs),
                )
                review_text = _to_text(review_res).strip()

                verdict, _review_obj, raw = parse_verdict_from_json(review_text)

                if verdict == "invalid":
                    repair_inputs = dict(review_inputs)
                    repair_inputs["dyn_report"] = (
                        "FORMAT REPAIR: Your previous output was invalid. "
                        "Return ONLY ONE minified JSON object with verdict pass/fail.\n\n"
                        + repair_inputs["dyn_report"]
                    )
                    review_res2 = observer.run_agent(
                        "dynamic_reviewer",
                        f"dynamic_review_repair_g{g}_d{d}_iter{iter_num}",
                        lambda: dyn_review_crew.kickoff(inputs=repair_inputs),
                    )
                    review_text2 = _to_text(review_res2).strip()
                    verdict, _review_obj, raw = parse_verdict_from_json(review_text2)

                if verdict == "pass":
                    print("Dynamic Reviewer: PASS")
                    print(raw)
                    observer.note("dynamic_iteration_end", global_iteration=g, dynamic_iteration=d, verdict="pass")
                    break

                print("Dynamic Reviewer: FAIL")
                print("--- DYNAMIC REVIEW JSON ---")
                print(raw)

                diagnosis = raw

                xml_files = report.get("xml_files") or []
                has_xml_pwsh = any(
                    "xml-pwsh" in (f.get("path", "").replace("/", "\\").lower())
                    for f in xml_files
                )
                if not has_xml_pwsh:
                    raise RuntimeError("psandman did not produce xml-pwsh output. Aborting the flow.")

                fix_inputs = {
                    "request": request,
                    "plan": plan_text,
                    "invariants": invariants_text,
                    "current_code": script_code,
                    "dyn_report": json.dumps(compact, ensure_ascii=False),
                    "diagnosis": diagnosis,
                }

                fix_res = observer.run_agent(
                    "change_planner",
                    f"dynamic_fix_notes_g{g}_d{d}_iter{iter_num}",
                    lambda: dyn_fix_crew.kickoff(inputs=fix_inputs),
                )
                fix_notes = _to_text(fix_res).strip()

                if not fix_notes.startswith("- "):
                    fix_notes = (
                        "Fix the previous script to satisfy the plan and invariants based on the dynamic diagnosis and report. "
                        "Do NOT remove any invariant. Apply minimal changes."
                    )

                print("--- DYNAMIC FIX NOTES ---")
                print(fix_notes)

                iter_num += 1
                print("--- CODING (apply dynamic fixes) ---")
                bundle = build_coder_input_bundle(
                    request=request,
                    plan_text=plan_text,
                    invariants_text=invariants_text,
                    current_code=script_code,
                    fix_notes=fix_notes,
                    iter_num=iter_num,
                )
                code_res = observer.run_agent(
                    "coder",
                    f"dynamic_coding_g{g}_d{d}_iter{iter_num}",
                    lambda: code_crew.kickoff(inputs=bundle),
                )
                script_code = extract_powershell_code(_to_text(code_res))
                script_path = observer.run_stage(
                    f"save_script_iter{iter_num}",
                    lambda: _save_script(script_code, iter_num),
                )
                observer.note("dynamic_iteration_end", global_iteration=g, dynamic_iteration=d, verdict="fail")
            else:
                print("Dynamic analysis did not pass within max iterations; continuing anyway.")
                observer.note("dynamic_loop_exhausted", global_iteration=g, max_dynamic_iters=max_dynamic_iters)
        else:
            print("Global iteration budget exhausted; continuing with latest candidate.")
            observer.note("global_loop_exhausted", max_global_iters=max_global_iters)

        print("Script finale:", script_path)
        observer.finish(status="success", exit_code=0, final_script_path=script_path)
        return 0
    except Exception:
        observer.finish(status="error", exit_code=1, final_script_path=script_path)
        raise


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
