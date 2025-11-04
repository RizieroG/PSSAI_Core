@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM === USO ===
REM automation_batch.cmd [-py "python"] [-eval ".\test_evaluation_json_token.py"] [-dir "."]
REM automation_batch.cmd -py "py" -eval ".\test_evaluation_json_token.py" -dir "."

set "SCRIPT_DIR=%~dp0"
set "DIR=%SCRIPT_DIR%"
REM Interprete Python
set "PY=py"
REM Script Python di valutazione (default completo)
set "EVAL=%SCRIPT_DIR%test_evaluation_json_token_complete.py"
REM CSV di output con i risultati aggregati
set "CSV=%DIR%\results_eval_complete.csv"

:parse
if "%~1"=="" goto after_parse
if /I "%~1"=="-py"   set "PY=%~2"    & shift & shift & goto parse
if /I "%~1"=="-eval" set "EVAL=%~2"  & shift & shift & goto parse
if /I "%~1"=="-dir"  set "DIR=%~2"   & shift & shift & goto parse
shift
goto parse

:after_parse
REM Se il CSV non esiste, scrivi l'header
if not exist "%CSV%" (
  echo number,ref_ps1,cand_ps1,BLEU1,BLEU2,BLEU4,ROUGE_L_F,METEOR,EditDistance,EditNorm,chrF> "%CSV%"
)

echo [BATCH] Scansione in "%DIR%"
for %%F in ("%DIR%\example_*.ps1") do (
  REM Nome base (senza estensione), es: example_12 o example_12_generated
  set "BASENAME=%%~nF"

  REM Salta i file *_generated.ps1: qui vogliamo partire dai reference "example_N.ps1"
  echo !BASENAME! | find /i "_generated" >nul
  if not errorlevel 1 (
    REM file *_generated.ps1 -> skip
  ) else (
    REM estrai N da example_N
    for /f "tokens=2 delims=_" %%N in ("!BASENAME!") do set "N=%%N"

    set "REF=%DIR%\example_!N!.ps1"
    set "CAND=%DIR%\example_!N!_generated.ps1"

    REM (opzionale) fallback "esample_*" se ti serve davvero
    if not exist "!REF!"  set "REF=%DIR%\esample_!N!.ps1"
    if not exist "!CAND!" set "CAND=%DIR%\esample_!N!_generated.ps1"

    REM esegui il lavoro solo se entrambi i file esistono
    if exist "!REF!" if exist "!CAND!" (
      set "REFJSON=!REF:.ps1=.json!"
      set "CANDJSON=!CAND:.ps1=.json!"

      REM Tokenizza REF -> REFJSON
      echo [TOK] "!REF!"  ^>  "!REFJSON!"
      powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%tokenization.ps1" -InputPath "!REF!" -OutputJsonPath "!REFJSON!"
      if errorlevel 1 (
        REM Se fallisce la tokenizzazione del reference, logga e passa al prossimo N
        echo [WARN] N=!N!: tokenizzazione ref fallita
      ) else (
        REM Tokenizza CAND -> CANDJSON
        echo [TOK] "!CAND!" ^>  "!CANDJSON!"
        powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%tokenization.ps1" -InputPath "!CAND!" -OutputJsonPath "!CANDJSON!"
        if errorlevel 1 (
          echo [WARN] N=!N!: tokenizzazione cand fallita
        ) else (
          REM Esegui lo script Python di valutazione, appendendo una riga al CSV
          echo [PY ] "%PY%" "%EVAL%" --ref-ps1 "!REF!" --cand-ps1 "!CAND!" --ref-json "!REFJSON!" --cand-json "!CANDJSON!" --csv-append "%CSV%" --number !N!
          "%PY%" "%EVAL%" --ref-ps1 "!REF!" --cand-ps1 "!CAND!" --ref-json "!REFJSON!" --cand-json "!CANDJSON!" --csv-append "%CSV%" --number !N!
          if errorlevel 1 (
            echo [WARN] N=!N!: valutazione fallita
          ) else (
            echo [OK  ] N=!N! completato
          )
        )
      )
    ) else (
      REM Avvisi se manca uno dei due file della coppia
      if not exist "!REF!"  echo [WARN] N=!N!: reference mancante
      if not exist "!CAND!" echo [WARN] N=!N!: candidate mancante
    )
  )
)

echo [DONE] Batch completato. CSV: "%CSV%"
exit /b 0
