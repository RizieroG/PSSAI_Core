import os
import sys
from datetime import datetime
from crewai import Agent, Task, Crew, LLM


def _require_env(name: str) -> str:
    """Ensure required env var is set (used by CrewAI/OpenAI)."""
    v = os.environ.get(name, "").strip()
    if not v:
        raise EnvironmentError(
            f"Missing env var {name}. Set it before running (e.g., OPENAI_API_KEY)."
        )
    return v


_require_env("OPENAI_API_KEY")


def make_openai_llm(model_name: str = "gpt-3.5-turbo", temperature: float = 0.2) -> LLM:
    """Centralized LLM factory used by the Coder agent."""
    return LLM(model=model_name, temperature=temperature, max_tokens=4096, timeout=1200)


OPENAI_MODEL_CODER = os.environ.get("OPENAI_MODEL_CODER", "gpt-3.5-turbo")
llm_coder = make_openai_llm(OPENAI_MODEL_CODER, temperature=0.2)

# ============================== AGENT ===================================== #

coder = Agent(
    role="Coder",
    goal=(
        "Deliver exactly one self-contained, directly runnable PowerShell (.ps1) script "
        "that fulfills the USER REQUEST on a vanilla Windows host."
    ),
    backstory=(
        """
        You are a Senior Software Engineer specialized in PowerShell scripting.
        Your output MUST be only the final .ps1 file contents — no markdown, no prose, no fences, no placeholders, no TODOs.
        LET'S THINK STEP BY STEP (INTERNAL ONLY — do not output your thoughts).

        Hard requirements:
        • Use only built-in Microsoft.PowerShell.* modules.
        • No external dependencies, no installs, no external parameters. Define default values if needed.
        • Structure the script for reliability: optional Param() (only if inputs are explicitly required), helper functions,
          main execution block, and a single well-defined exit point.
        • No explanations, comments about decisions, or extra lines before/after the code.
        • The script must be directly runnable as-is without modifications or external params.
        • LET'S THINK STEP BY STEP. Never output lines starting with 'Thought:' or any reasoning. Output ONLY PowerShell code.
        """
    ),
    llm=llm_coder,
    verbose=False,
)

# =============================== TASK ===================================== #

code_task = Task(
    description=(
        "Return only a single runnable PowerShell (.ps1) script that satisfies the USER REQUEST.\n\n"
        "USER REQUEST:\n{request}\n\n"
        "Rules:\n"
        "- Output only the script body (no markdown/prose/fences).\n"
        "- Use only built-in Microsoft.PowerShell.* modules; no external dependencies.\n"
        "- Script must run without needing extra parameters unless the request explicitly asks for them."
    ),
    expected_output="Only executable PowerShell code (.ps1), no fences or extra text.",
    agent=coder,
    markdown=False,
)

# =============================== UTILS ==================================== #


def _to_text(result) -> str:
    """Extract raw text from CrewAI result as robustly as possible."""
    # common attrs in CrewAI results
    for attr in ("raw", "output", "result", "outputs"):
        if hasattr(result, attr):
            try:
                val = getattr(result, attr)
                if val is None:
                    continue
                if isinstance(val, list) and val:
                    return str(val[-1])
                return str(val)
            except Exception:
                pass
    # try to_dict fallback
    try:
        if hasattr(result, "to_dict"):
            d = result.to_dict()
            if isinstance(d, dict) and d.get("raw"):
                return str(d.get("raw"))
    except Exception:
        pass
    # last resort
    try:
        return str(result)
    except Exception:
        return ""


def extract_powershell_code(text: str) -> str:
    """Unwrap fenced output if present and return plain PowerShell code."""
    if "```" not in text:
        return text.strip()
    parts = text.split("```")
    for i in range(1, len(parts), 2):
        block = parts[i]
        if block.strip().startswith("powershell"):
            return block.split("\n", 1)[1].strip() if "\n" in block else ""
        return block.strip()
    return text.strip()


def build_coder_input_bundle(request: str) -> dict:
    """Builds the minimal input payload for the single-pass Coder flow."""
    return {
        "request": request,
    }


# =============================== MAIN ===================================== #


def main():
    """Single-pass pipeline: request -> coder -> sanitize output -> save script."""
    default_request = (
        "Create a PowerShell script that prints the machine's hostname, OS version, "
        "free/used/total disk space for drive C:, and the current date/time, then exits with code 0."
    )

    # If no CLI request is provided, fall back to a safe demo request.
    args = sys.argv[1:]
    request = " ".join(args) if args else default_request

    # Single-pass architecture: one coder call, then save the resulting script.
    code_crew = Crew(agents=[coder], tasks=[code_task])

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle = build_coder_input_bundle(request=request)

    # Ask the Coder to generate the full .ps1 content in one shot.
    code_res = code_crew.kickoff(inputs=bundle)
    raw_text = _to_text(code_res)

    # Debug/guard rails: surface empty generations explicitly
    print(f"--- RAW LLM OUTPUT (len={len(raw_text)}) ---")
    if raw_text:
        preview = raw_text[:400]
        print(preview + ("..." if len(raw_text) > 400 else ""))
    else:
        print("[LLM returned empty output]")

    # Strip possible markdown fences to keep only executable PowerShell.
    script_code = extract_powershell_code(raw_text)

    if not script_code.strip():
        raise RuntimeError(
            "LLM returned empty PowerShell code (probabile blocco policy o errore nel prompt)."
        )

    # Persist with UTF-8 BOM for Windows PowerShell compatibility.
    script_path = os.path.join(os.getcwd(), f"generated_{timestamp}.ps1")
    with open(script_path, "w", encoding="utf-8-sig") as f:
        f.write(script_code)

    print(f"Salvato: {script_path}")
    print("Script finale:", script_path)
    return 0


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
