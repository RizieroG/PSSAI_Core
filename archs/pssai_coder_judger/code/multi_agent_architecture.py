import json
import os
import re
import sys
from datetime import datetime

from crewai import Agent, Crew, LLM, Task


def _require_env(name: str) -> str:
    """Verifica che una variabile d'ambiente richiesta sia presente."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise EnvironmentError(f"Missing env var {name}. Set it before running (e.g., OPENAI_API_KEY).")
    return value


# CrewAI/LiteLLM legge OPENAI_API_KEY dall'ambiente.
_require_env("OPENAI_API_KEY")


def make_openai_llm(model_name: str = "gpt-3.5-turbo", temperature: float = 0.5) -> LLM:
    """Factory unica per istanziare i modelli usati dagli agenti."""
    return LLM(
        model=model_name,
        temperature=temperature,
        max_tokens=4096,
        timeout=1200,
    )


OPENAI_MODEL_CODER = os.environ.get("OPENAI_MODEL_CODER", "gpt-3.5-turbo")
OPENAI_MODEL_ALIGN = os.environ.get("OPENAI_MODEL_ALIGN", "gpt-3.5-turbo")
llm_coder = make_openai_llm(OPENAI_MODEL_CODER, temperature=0.2)
llm_aligner = make_openai_llm(OPENAI_MODEL_ALIGN, temperature=0.3)

coder = Agent(
    role="Coder",
    goal=(
        "Deliver exactly one self-contained, directly runnable PowerShell (.ps1) script "
        "that fulfills the user request on a vanilla Windows host."
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

# ============================== TASKS ===================================== #

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
        "{\"status\":\"ok\",\"reason\":\"<=200 chars\"}\n"
        "Otherwise (when concrete improvements are needed):\n"
        "{\"status\":\"retry\",\"reason\":\"<=300 chars\",\"fix_notes\":\"- bullet 1\\n- bullet 2\\n- ...\"}\n\n"
        "Rules for fix_notes (when status=retry):\n"
        "- 3–9 bullets, each starting with \"- \".\n"
        "- Each bullet is a tiny, actionable delta\n"
        "- LET'S THINK STEP BY STEP; Never output lines starting with 'Thought:' or any reasoning.\n"
        "- Use inline backticks for short identifiers/tokens only;\n"
        "- Reference what/where to change by function/identifier names rather than line numbers (lines may shift).\n"
        "- Never remove or weaken the INVARIANTS; never add new dependencies; keep outputs/side-effects unchanged unless required by the invariants.\n\n"
        "Decision policy:\n"
        "- Return status=\"ok\" when differences are purely cosmetic or do not improve functional/structural equivalence.\n"
        "- Return status=\"retry\" only when small, safe deltas will materially improve equivalence or static-analysis outcomes."
    ),
    expected_output=(
        "A single JSON object with keys: "
        "status=(\"ok\"|\"retry\"), reason=string, and if status=\"retry\": fix_notes as a bullet list string."
    ),
    agent=aligner,
    markdown=False,
)

# ============================== UTILS ===================================== #


def _to_text(result) -> str:
    """Normalizza la risposta CrewAI in testo puro."""
    try:
        return getattr(result, "raw") if hasattr(result, "raw") else str(result)
    except Exception:
        return str(result)


def extract_powershell_code(text: str) -> str:
    """Estrae il corpo PowerShell da eventuali blocchi markdown."""
    if "```" in text:
        match = re.search(r"```(?:powershell|ps1|ps)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return re.sub(r"```", "", text, flags=re.DOTALL).strip()
    return text.strip()


def parse_jsonish(text: str) -> dict:
    """Prova a leggere un JSON anche quando il modello aggiunge testo extra."""
    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    return {}


def build_coder_input_bundle(
    request: str,
    plan_text: str,
    invariants_text: str,
    current_code: str,
    fix_notes: str,
    iter_num: int,
    user_change_request: str = "",
) -> dict:
    """Costruisce il payload passato al task di coding."""
    return {
        "request": request,
        "plan": plan_text,
        "invariants": invariants_text,
        "current_code": current_code or "<none>",
        "fix_notes": fix_notes,
        "iter_num": iter_num,
        "user_change_request": user_change_request or "<none>",
    }


def normalize_fix_notes(raw_fix_notes) -> str:
    """Normalizza FIX NOTES in una stringa multilinea."""
    if isinstance(raw_fix_notes, list):
        return "\n".join(str(item).strip() for item in raw_fix_notes if str(item).strip())
    return str(raw_fix_notes or "").strip()


# ============================== MAIN ====================================== #


def main() -> int:
    default_request = (
        "Create a PowerShell script that prints the machine’s hostname, OS version, "
        "free/used/total disk space for drive C:, and the current date/time, then exits with code 0."
    )

    # Parsing minimale CLI: --ref <path> e testo richiesta libero.
    args = sys.argv[1:]

    def pop_flag_value(flag: str) -> str | None:
        if flag in args:
            index = args.index(flag)
            if index + 1 < len(args):
                value = args[index + 1]
                del args[index:index + 2]
                return value
        return None

    ref_path = pop_flag_value("--ref")
    request = " ".join(args) if args else default_request

    ref_code = ""
    if ref_path and os.path.exists(ref_path):
        with open(ref_path, "r", encoding="utf-8-sig") as file:
            ref_code = file.read()

    # Tenuti per compatibilita con il prompt, anche se in questo script restano vuoti.
    plan_text = ""
    invariants_text = ""

    code_crew = Crew(agents=[coder], tasks=[code_task])
    align_crew = Crew(agents=[aligner], tasks=[align_task]) if ref_code.strip() else None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_code = ""
    script_path = ""
    fix_notes = "Initial implementation from the request."
    iter_num = 1

    def save_script(code: str, iteration: int) -> str:
        """Salva ogni iterazione in un file separato tracciato dal timestamp."""
        name = f"generated_{timestamp}_iter{iteration}.ps1"
        path = os.path.join(os.getcwd(), name)
        with open(path, "w", encoding="utf-8-sig") as file:
            file.write(code)
        print(f"Salvato: {path}")
        return path

    # 1) Generazione iniziale del candidato PowerShell.
    print("\n=== CODING ===")
    bundle = build_coder_input_bundle(
        request=request,
        plan_text=plan_text,
        invariants_text=invariants_text,
        current_code=script_code,
        fix_notes=fix_notes,
        iter_num=iter_num,
    )
    code_result = code_crew.kickoff(inputs=bundle)
    script_code = extract_powershell_code(_to_text(code_result))
    script_path = save_script(script_code, iter_num)

    # 2) Allineamento opzionale al reference, se fornito con --ref.
    if ref_code.strip() and align_crew is not None:
        print("\n=== ALIGNMENT ===")
        align_inputs = {
            "invariants": invariants_text,
            "original_code": ref_code,
            "candidate_code": script_code,
        }
        align_result = align_crew.kickoff(inputs=align_inputs)
        raw_align = parse_jsonish(_to_text(align_result).strip())

        # Alcune risposte arrivano come lista: prendiamo il primo elemento valido.
        if isinstance(raw_align, list):
            align_json = raw_align[0] if raw_align else {}
        else:
            align_json = raw_align or {}

        status = str(align_json.get("status") or "").lower()

        if status == "ok":
            print("Alignment: il candidato è sufficientemente simile al reference.")
        else:
            fix_notes = normalize_fix_notes(align_json.get("fix_notes"))
            if fix_notes:
                with open(f"alignnotes_{timestamp}.txt", "w", encoding="utf-8") as file:
                    file.write(fix_notes + "\n")

                print("--- ALIGNMENT FIX NOTES ---")
                print(fix_notes)
                print("\n=== APPLYING ALIGNMENT FIX NOTES ===")

                iter_num += 1
                bundle = build_coder_input_bundle(
                    request=request,
                    plan_text=plan_text,
                    invariants_text=invariants_text,
                    current_code=script_code,
                    fix_notes=fix_notes,
                    iter_num=iter_num,
                )
                code_result = code_crew.kickoff(inputs=bundle)
                script_code = extract_powershell_code(_to_text(code_result))
                script_path = save_script(script_code, iter_num)
            else:
                print("Alignment LLM: nessuna FIX NOTES fornita; nessuna azione eseguita.")

    print("Script finale:", script_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
