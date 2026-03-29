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

# ========================= PSANDMAN FIXED PATHS ========================= #
# Percorsi fissi richiesti (nessuna env var necessaria per input/output).
PSANDMAN_BASE_DIR      = r"PATH\TO\psandman"
PSANDMAN_SCRIPT_PATH   = os.path.join(PSANDMAN_BASE_DIR, "psandman.py")
PSANDMAN_INPUT_DIR     = os.path.join(PSANDMAN_BASE_DIR, "inputs")
PSANDMAN_OUTPUT_ROOT   = os.path.join(PSANDMAN_BASE_DIR, "output")
PSANDMAN_OUTPUT_XMLDIR = os.path.join(PSANDMAN_OUTPUT_ROOT, "xml")
PSANDMAN_XMLPWSH_DIR   = os.path.join(PSANDMAN_OUTPUT_ROOT, "xml-pwsh")

DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_API_KEY_ENV_VAR = "OPENAI_API_KEY"
LLM_DEFAULT_TEMPERATURE = 0.5
LLM_MAX_TOKENS = 4096
LLM_TIMEOUT_SEC = 1200
LLM_TEMPERATURE_CODER = 0.2
LLM_TEMPERATURE_REVIEWER = 0.1
LLM_TEMPERATURE_ALIGNER = 0.3


def _require_env(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise EnvironmentError(f"Missing env var {name}. Set it before running (e.g., OPENAI_API_KEY).")
    return v

# CrewAI/LiteLLM legge OPENAI_API_KEY dall'ambiente.
_require_env(OPENAI_API_KEY_ENV_VAR)

def make_openai_llm(
    model_name: str = DEFAULT_OPENAI_MODEL,
    temperature: float = LLM_DEFAULT_TEMPERATURE,
) -> LLM:
    return LLM(
        model=model_name,
        temperature=temperature,
        max_tokens=LLM_MAX_TOKENS,
        timeout=LLM_TIMEOUT_SEC,
    )

# Models (feel free to tweak)
OPENAI_MODEL_PLANNER = os.environ.get("OPENAI_MODEL_PLANNER", DEFAULT_OPENAI_MODEL)
OPENAI_MODEL_CODER   = os.environ.get("OPENAI_MODEL_CODER",   DEFAULT_OPENAI_MODEL)
OPENAI_MODEL_REVIEW  = os.environ.get("OPENAI_MODEL_REVIEW",  DEFAULT_OPENAI_MODEL)
OPENAI_MODEL_ALIGN   = os.environ.get("OPENAI_MODEL_ALIGN",   DEFAULT_OPENAI_MODEL)
llm_planner        = make_openai_llm(OPENAI_MODEL_PLANNER, temperature=LLM_DEFAULT_TEMPERATURE)
llm_coder          = make_openai_llm(OPENAI_MODEL_CODER,   temperature=LLM_TEMPERATURE_CODER)
llm_reviewer       = make_openai_llm(OPENAI_MODEL_REVIEW,  temperature=LLM_TEMPERATURE_REVIEWER)
llm_change_planner = make_openai_llm(OPENAI_MODEL_PLANNER, temperature=LLM_DEFAULT_TEMPERATURE)
llm_aligner        = make_openai_llm(OPENAI_MODEL_ALIGN,   temperature=LLM_TEMPERATURE_ALIGNER)

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
        "{\"status\":\"ok\",\"reason\":\"<=200 chars\"}\n"
        "Otherwise (when concrete improvements are needed):\n"
        "{\"status\":\"retry\",\"reason\":\"<=300 chars\",\"fix_notes\":\"- bullet 1\\n- bullet 2\\n- ...\"}\n\n"
        "Rules for fix_notes (when status=retry):\n"
        "- 3–9 bullets, each starting with \"- \".\n"
        "- Each bullet is a tiny, actionable delta \n"
        "- LET'S THINK STEP BY STEP; Never output lines starting with 'Thought:' or any reasoning.\n"
        "- Use inline backticks for short identifiers/tokens only;\n"
        "- Reference what/where to change by function/identifier names rather than line numbers (lines may shift).\n"
        "- Never remove or weaken the INVARIANTS; never add new dependencies; keep outputs/side-effects unchanged unless required by the invariants.\n\n"
        "Decision policy:\n"
        "- Return status=\"ok\" when differences are purely cosmetic or do not improve functional/structural equivalence.\n"
        "- Return status=\"retry\" only when small, safe deltas will materially improve equivalence or static-analysis outcomes."
    ),
    expected_output=(
        'A single JSON object with keys: '
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
        "- PASS => {\"verdict\":\"pass\",\"reason\":\"<=240 chars\"}\n"
        "- FAIL => {\"verdict\":\"fail\",\"reason\":\"<=240 chars\",\"fix_notes\":[\"<=10 items\"]}\n"
        "- fix_notes must be concrete deltas (parse errors first). Do not add dependencies.\n"
    ),
    expected_output="A single minified JSON object with verdict pass/fail.",
    agent=static_reviewer,
    markdown=False,
)

# ============================== UTILS ===================================== #

def compact_dyn_report(report: dict, request_text: str = "", plan_text: str = "", code_text: str = "") -> str:
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

def parse_verdict_from_json(s: str) -> tuple[str, dict, str]:
    raw = (s or "").strip()
    obj = parse_jsonish(raw)

    verdict = (obj.get("verdict") or obj.get("decision") or obj.get("status") or "").strip().lower()
    if verdict in ("pass", "ok"):
        return "pass", obj, raw
    if verdict in ("fail", "retry"):
        return "fail", obj, raw

    # formato non rispettato
    return "invalid", obj, raw

def plan_to_invariants(plan_text: str) -> str:
    lines = []
    for ln in plan_text.splitlines():
        ln = ln.strip()
        if ln.startswith("- "):
            lines.append(f"- {ln[2:]}")
    return "\n".join(lines) if lines else f"- {plan_text.strip()}"


def build_coder_input_bundle(request: str, plan_text: str, invariants_text: str,
                             current_code: str, fix_notes: str, iter_num: int,
                             user_change_request: str = "") -> dict:
    return {
        "request": request,
        "plan": plan_text,
        "invariants": invariants_text,
        "current_code": current_code if current_code else "<none>",
        "fix_notes": fix_notes,
        "iter_num": iter_num,
        "user_change_request": user_change_request or "<none>",
    }



class PsandmanRunner:
    """
    Runs psandman by copying the candidate script into the fixed inputs folder and
    collecting XML output logs from the configured output sources (xml-pwsh by default).

    After collecting and extracting a compact event summary, it:
    - removes the tested script from inputs
    - cleans all subfolders/files under PSANDMAN_OUTPUT_ROOT
    - cleans all subfolders/files under PSANDMAN_XMLPWSH_DIR
    """
    def __init__(self, guest_user: str, guest_pass: str, timeout_sec: int = 1800):
        # Fixed paths for the psandman harness and its input/output areas.
        self.psandman_path = os.path.abspath(PSANDMAN_SCRIPT_PATH)
        self.workdir = os.path.abspath(PSANDMAN_BASE_DIR)
        self.input_dir = os.path.abspath(PSANDMAN_INPUT_DIR)
        self.output_root = os.path.abspath(PSANDMAN_OUTPUT_ROOT)
        # Only xml-pwsh is used to avoid mixing with other log types.
        self.output_sources = [os.path.abspath(PSANDMAN_XMLPWSH_DIR)]
        # Guest VM credentials used by psandman.
        self.guest_user = guest_user
        self.guest_pass = guest_pass
        # Upper bound for the full psandman run.
        self.timeout = timeout_sec

    def _clean_dir(self, path: str):
        # Best-effort cleanup to keep runs isolated.
        os.makedirs(path, exist_ok=True)
        for name in os.listdir(path):
            p = os.path.join(path, name)
            try:
                # Remove both files and subdirectories.
                if os.path.isdir(p):
                    shutil.rmtree(p)
                else:
                    os.remove(p)
            except Exception:
                # Ignore cleanup failures to avoid blocking the run.
                pass

    def _collect_xml_files(self) -> list[str]:
        # Walk configured output sources and collect .xml files.
        xmls = []
        for src in self.output_sources:
            if os.path.isdir(src):
                for root, _dirs, files in os.walk(src):
                    for fn in files:
                        if fn.lower().endswith(".xml"):
                            xmls.append(os.path.join(root, fn))
            # Missing folders are ignored to keep the run resilient.
        return sorted(set(xmls))

    def _extract_events_from_xml(self, xml_path: str, max_events: int = 1000) -> list[dict]:
        """
        Extract a compact list of semantic events from a PowerShell ETW XML log.

        Strategy:
        - Parse XML and iterate <Event> nodes.
        - Read header fields (EventID/TimeCreated/Level) and EventData payload.
        - Normalize into a small {EventID, Time, Tag, Msg} dict per event.
        - Truncate long payloads and stop after max_events to keep memory/time bounded.
        """
        # Parse Windows PowerShell event XML and keep a compact, bounded summary.
        import xml.etree.ElementTree as ET
        import re

        # Remove XML namespaces so tags can be compared with plain names.
        def _strip_ns(tag: str) -> str:
            return tag.split("}", 1)[-1] if "}" in tag else tag

        # Regex helpers:
        # - ParameterBinding: grab param name/value (value capped to 150 chars).
        # - CommandInvocation: grab invoked command name.
        # - Error: capture error text (later truncated).
        re_binding = re.compile(r'ParameterBinding\(([^)]+)\):\s*name="([^"]+)";\s*value="([^"]{0,150})')
        re_cmd = re.compile(r'CommandInvocation\(([^)]+)\)')
        re_error = re.compile(r'(TerminatingError|NonTerminatingError)\(([^)]+)\):\s*"(.*)"')

        # Output container for normalized events.
        events = []
        try:
            # Parse the XML file; any parse failure yields no events.
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except Exception:
            # Malformed or unreadable XML yields no events.
            return events

        # Walk all nodes and keep only <Event> records.
        for ev in root.iter():
            if _strip_ns(ev.tag) != "Event":
                continue

            # --- 1. Header ---
            # Pull minimal header fields used for summary and ordering.
            eid, time_created, level = None, None, None
            sys_node = next((ch for ch in list(ev) if _strip_ns(ch.tag) == "System"), None)
            if sys_node:
                for ch in list(sys_node):
                    tag = _strip_ns(ch.tag)
                    if tag == "EventID": eid = ch.text.strip()
                    elif tag == "TimeCreated": time_created = ch.attrib.get("SystemTime")
                    elif tag == "Level": level = ch.text.strip()
            # NOTE: 'level' is currently unused but kept for possible future filtering.

            # --- 2. Data ---
            # Extract EventData <Data Name="...">...</Data> entries into a dict.
            data_map = {}
            edata_node = next((ch for ch in list(ev) if _strip_ns(ch.tag) == "EventData"), None)
            if edata_node:
                for d in list(edata_node):
                    if _strip_ns(d.tag) == "Data":
                        name = d.attrib.get("Name")
                        if name and d.text:
                            data_map[name] = d.text.strip()
            # data_map now holds the key event fields we care about.

            # --- 3. Parsing e Troncamento ---
            # Build a short, human-readable message + a coarse tag.
            semantic_msg = ""
            tag_type = "INFO"

            # Kept events:
            # - 4104: ScriptBlock logging (testo degli script/powerShell blocchi eseguiti).
            # - 4103: Pipeline execution (invocazione comandi + parametri).
            # - 4100: Error event (errori generici di PowerShell).
            # - Any other EventID will keep semantic_msg empty and be dropped.
            # EventID 4104: ScriptBlock logging (script text).
            if eid == "4104": # ScriptBlock
                # ScriptBlockText contains executed script content.
                tag_type = "CODE"
                script_text = data_map.get("ScriptBlockText", "")
                if "SIG # Begin signature block" in script_text:
                    semantic_msg = "<Signature Block Skipped>"
                else:
                    # Use only the first non-empty line to keep the log concise.
                    lines = [l.strip() for l in script_text.splitlines() if l.strip()]
                    if lines:
                        first_line = lines[0][:200]
                        semantic_msg = f"Exec ScriptBlock: {first_line}..." if len(lines) > 1 else first_line

            # EventID 4103: Pipeline execution (command + parameters).
            elif eid == "4103": # Pipeline
                # Pipeline events contain command invocation + parameter bindings.
                tag_type = "EXEC"
                payload = data_map.get("Payload", "")

                # Try to detect command name and parameter bindings from payload.
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
                    # Promote to FAIL when errors are present in the payload.
                    tag_type = "FAIL"
                    err_text = err_match.group(3)[:300] # Max 300 chars per errore
                    sep = " | " if semantic_msg else ""
                    semantic_msg = f"{semantic_msg}{sep}ERROR: {err_text}"

                if not semantic_msg and payload:
                    # Fallback: keep a trimmed payload line for visibility.
                    semantic_msg = payload[:200].replace("\n", " | ")

            # EventID 4100: generic PowerShell error.
            elif eid == "4100": # Error
                # Generic PowerShell error event.
                tag_type = "FAIL"
                msg = data_map.get('Message') or data_map.get('Payload') or ""
                semantic_msg = f"ERROR: {msg[:300]}"

            # Scarta eventi vuoti o inutili
            if not semantic_msg or "Host Name =" in semantic_msg:
                # Drop empty/noisy events to keep the timeline compact.
                continue

            # Normalize event shape for downstream consumers.
            events.append({
                "EventID": eid,
                "Time": time_created,
                "Tag": tag_type,
                "Msg": semantic_msg
            })

            if len(events) >= max_events:
                # Stop early to bound memory/time per XML file.
                break

        return events

    def run(self, host_script_path: str) -> dict:
        start = time.time()

        # Pre-clean to avoid mixing logs across runs.
        self._clean_dir(self.input_dir)
        self._clean_dir(self.output_root)

        # NON creare xml-pwsh: deve crearla psandman. Se esiste da run precedente, eliminala completamente.
        try:
            if os.path.isdir(PSANDMAN_XMLPWSH_DIR):
                shutil.rmtree(PSANDMAN_XMLPWSH_DIR)
        except Exception:
            # Cleanup failures are non-fatal.
            pass

        src = os.path.abspath(host_script_path)
        dst = os.path.join(self.input_dir, os.path.basename(src))

        try:
            # Place the script into psandman inputs.
            try:
                shutil.copy2(src, dst)
            except Exception:
                # Fallback copy to preserve encoding and avoid copy errors on locked files.
                with open(src, "r", encoding="utf-8-sig", errors="replace") as fsrc:
                    data = fsrc.read()
                with open(dst, "w", encoding="utf-8-sig") as fdst:
                    fdst.write(data)

            # Force UTF-8 for psandman output (avoids UnicodeEncodeError on Windows pipes).
            env = os.environ.copy()
            env["PYTHONUTF8"] = "1"
            env["PYTHONIOENCODING"] = "utf-8"

            # Run psandman in setup+debug mode with guest credentials.
            cmd = [
                sys.executable, "-X", "utf8",
                self.psandman_path,
                "--setup",
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
                # Hard timeout: return a structured failure payload.
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
                # Decode stdout/stderr defensively across common encodings.
                for enc in ("utf-8", "cp1252", "latin-1"):
                    try:
                        return b.decode(enc)
                    except UnicodeDecodeError:
                        pass
                return b.decode("utf-8", errors="replace")

            xmls = self._collect_xml_files()
            # Collect a bounded number of events across all XMLs.
            all_events = []
            for xp in xmls:
                all_events.extend(self._extract_events_from_xml(xp, max_events=200))

            dur_ms = int((time.time() - start) * 1000)
            payload = {
                # Success requires both zero exit code and at least one XML produced.
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
                # Ignore cleanup failures to keep the pipeline running.
                pass
            try:
                self._clean_dir(self.output_root)
            except Exception:
                # Output cleanup is best-effort.
                pass
            try:
                if os.path.isdir(PSANDMAN_XMLPWSH_DIR):
                    shutil.rmtree(PSANDMAN_XMLPWSH_DIR)
            except Exception:
                # xml-pwsh cleanup is best-effort.
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

def main() -> int:
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
    # 1) PLANNING
    print("--- 1) PLANNING ---")
    plan_crew = Crew(agents=[planner], tasks=[plan_task])
    plan_res = plan_crew.kickoff(inputs={"request": request})
    plan_text = _to_text(plan_res).strip()
    print(plan_text)
    invariants_text = plan_to_invariants(plan_text)

    code_crew = Crew(agents=[coder], tasks=[code_task])
    dyn_review_crew = Crew(agents=[dyn_reviewer], tasks=[dyn_review_task])
    static_review_crew = Crew(agents=[static_reviewer], tasks=[static_review_task])

    max_auto_fix_iters = 3    # dynamic-analysis iterations

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

    # === Auto loop: code -> analyze -> (review fix) until pass ===
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
        code_text = _to_text(code_res)
        script_code = extract_powershell_code(code_text)
        script_path = _save_script(script_code, it)


        print("--- DYNAMIC ANALYSIS (psandman) ---")
        runner = PsandmanRunner(
            guest_user=guest_user,
            guest_pass=guest_pass,
            timeout_sec=1800,
        )
        report = runner.run(script_path)
        print(json.dumps(report, indent=2, ensure_ascii=False))

        print("--- DYNAMIC REVIEW ---")
        compact = compact_dyn_report(
            report,
            request_text=request,
            plan_text=plan_text,
            code_text=script_code,
        )
        review_inputs = {
            "request": request,
            "plan": plan_text,
            "invariants": invariants_text,
            "code": script_code,
            "dyn_report": json.dumps(compact, ensure_ascii=False),
        }

        review_res = dyn_review_crew.kickoff(inputs=review_inputs)
        review_text = _to_text(review_res).strip()

        verdict, review_obj, raw = parse_verdict_from_json(review_text)

        if verdict == "invalid":
            repair_inputs = dict(review_inputs)
            repair_inputs["dyn_report"] = (
                "FORMAT REPAIR: Your previous output was invalid. "
                "Return ONLY ONE minified JSON object with verdict pass/fail.\n\n"
                + repair_inputs["dyn_report"]
            )
            review_res2 = dyn_review_crew.kickoff(inputs=repair_inputs)
            review_text2 = _to_text(review_res2).strip()
            verdict, review_obj, raw = parse_verdict_from_json(review_text2)

        if verdict == "pass":
            print("Dynamic Reviewer: PASS")
            print(raw)  # JSON
            break

        # qui siamo in fail (o ancora invalid)
        print("Dynamic Reviewer: FAIL")
        print("--- DYNAMIC REVIEW JSON ---")
        print(raw)

        diagnosis = raw

        # vogliamo xml-pwsh. Se manca, abort del flusso.
        xml_files = report.get("xml_files") or []
        has_xml_pwsh = any(
            "xml-pwsh" in (f.get("path", "").replace("/", "\\").lower())
            for f in xml_files
        )
        if not has_xml_pwsh:
            raise RuntimeError("psandman did not produce xml-pwsh output. Aborting the flow.")

        # Genera FIX NOTES (deltas sul piano) dal Change Planner
        fix_inputs = {
            "request": request,
            "plan": plan_text,
            "invariants": invariants_text,
            "current_code": script_code,
            "dyn_report": json.dumps(compact, ensure_ascii=False),
            "diagnosis": diagnosis,
        }

        fix_res = dyn_fix_crew.kickoff(inputs=fix_inputs)
        fix_notes = _to_text(fix_res).strip()

        # Fallback robusto se il formato non è rispettato
        if not fix_notes.startswith("- "):
            fix_notes = (
                "Fix the previous script to satisfy the plan and invariants based on the dynamic diagnosis and report. "
                "Do NOT remove any invariant. Apply minimal changes."
            )

        print("--- FIX NOTES (from change planner) ---")
        print(fix_notes)



    # === Se ho un reference, avvio l'allineamento automatico LLM → FIX NOTES ===
    if ref_code.strip():
        align_crew = Crew(agents=[aligner], tasks=[align_task])
        max_align_rounds = 3
        for a in range(1, max_align_rounds + 1):
            print(f"--- ALIGNMENT ROUND {a}/{max_align_rounds} ---")
            align_inputs = {
                "invariants": invariants_text,
                "original_code": ref_code,
                "candidate_code": script_code,
            }
            align_res = align_crew.kickoff(inputs=align_inputs)
            align_json = parse_jsonish(_to_text(align_res).strip())
            status = (align_json.get("status") or "").lower()

            if status == "ok":
                print("Alignment: il candidato è sufficientemente simile al reference.")
                break

            fix_notes = (align_json.get("fix_notes") or "").strip()
            if not fix_notes:
                print("Alignment LLM: nessuna FIX NOTES fornita; interrompo l'allineamento.")
                break

            with open(f"alignnotes_{timestamp}_round{a}.txt", "w", encoding="utf-8") as f:
                f.write(fix_notes + "\n")

            iter_num += 1
            print("--- CODING (apply alignment deltas) ---")
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

        # === POST-ALIGNMENT: static gate con PSScriptAnalyzer (come richiesto) ===
        print("--- POST-ALIGNMENT STATIC ANALYSIS (PSScriptAnalyzer) ---")
        max_post_align_static_iters = 3
        for s in range(1, max_post_align_static_iters + 1):
            print(f"--- PSScriptAnalyzer CHECK {s}/{max_post_align_static_iters} ---")
            runner = PSScriptAnalyzerRunner(script_path, timeout_sec=180)
            report = runner.run()
            print(json.dumps(report, indent=2, ensure_ascii=False))

            if report.get("success"):
                print("Static gate: PASS (PSScriptAnalyzer). Script finale accettato.")
                break

            if report.get("exit_code") == -2:
                # modulo mancante: non è qualcosa che il coder può fixare nel .ps1
                raise RuntimeError(report.get("stderr") or "PSScriptAnalyzer non disponibile.")

            review_inputs = {
                "request": request,
                "plan": plan_text,
                "invariants": invariants_text,
                "code": script_code,
                "report": json.dumps(report, ensure_ascii=False),
            }

            review_res = static_review_crew.kickoff(inputs=review_inputs)
            verdict, obj, raw = parse_verdict_from_json(_to_text(review_res).strip())

            fix_list = obj.get("fix_notes") if isinstance(obj, dict) else None
            if isinstance(fix_list, list) and fix_list:
                fix_notes = "\n".join([("- " + x.strip().lstrip("- ").strip()) for x in fix_list if x and x.strip()])
            else:
                fix_notes = (
                    "Fix the previous script to pass PSScriptAnalyzer while preserving the plan and invariants. "
                    f"Errors:\n{report.get('stderr','')}\n"
                    "Do NOT remove any invariant. Apply minimal changes."
                )

            iter_num += 1
            print("--- CODING (apply static-analysis fixes) ---")
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
    else:
        print("Nessun --ref fornito: salto l'allineamento automatico.")

    print("Script finale:", script_path)

    return 0


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
