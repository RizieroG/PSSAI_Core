@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ======================== USO =========================
REM pssa_compare.cmd -dir "<cartella_con_ps1>" [-limit N] [-csv "<out.csv>"] [-settings "<PSScriptAnalyzerSettings.psd1>"] [-artifacts json]
REM Esempi:
REM   pssa_compare.cmd -dir "." -csv ".\pssa_results.csv"
REM   pssa_compare.cmd -dir "I:\...\all_scripts" -limit 50 -settings ".\PSScriptAnalyzerSettings.psd1" -artifacts json

REM ======================= DEFAULT ======================
set "SCRIPT_DIR=%~dp0"
set "DIR=%SCRIPT_DIR%"
set "CSV=%DIR%\pssa_results.csv"
set "LIMIT="
set "SETTINGS="
set "ARTIFACTS=none"
set "ART_DIR=%DIR%\pssa_artifacts"

REM ===================== PARSING ARGS ===================
:parse
if "%~1"=="" goto after_parse
if /I "%~1"=="-dir"       set "DIR=%~2"       & shift & shift & goto parse
if /I "%~1"=="-csv"       set "CSV=%~2"       & shift & shift & goto parse
if /I "%~1"=="-limit"     set "LIMIT=%~2"     & shift & shift & goto parse
if /I "%~1"=="-settings"  set "SETTINGS=%~2"  & shift & shift & goto parse
if /I "%~1"=="-artifacts" set "ARTIFACTS=%~2" & shift & shift & goto parse
shift
goto parse

:after_parse
if not exist "%DIR%" (
  echo [ERR] Cartella non trovata: "%DIR%"
  exit /b 1
)

REM =================== HEADER CSV ======================
if not exist "%CSV%" (
  echo number,ref_ps1,cand_ps1,ref_errors,ref_warnings,ref_infos,cand_errors,cand_warnings,cand_infos,diff_errors,diff_warnings,diff_infos,ref_rules,cand_rules,common_rules,unique_ref_rules,unique_cand_rules> "%CSV%"
)

if /I "%ARTIFACTS%"=="json" (
  if not exist "%ART_DIR%" mkdir "%ART_DIR%" >nul 2>&1
)

REM ========== Verifica script helper PowerShell =========
set "HELPER=%SCRIPT_DIR%pssa_pair_compare.ps1"
if not exist "%HELPER%" (
  echo [ERR] Manca "%HELPER%". Copia il file pssa_pair_compare.ps1 accanto a questo .cmd
  exit /b 1
)

echo [SCAN] Cartella: "%DIR%"
set /a COUNT=0

for %%F in ("%DIR%\example_*.ps1") do (
  set "BASENAME=%%~nF"
  rem Se il nome contiene "_generated", è uno script candidato e NON va processato qui
  echo !BASENAME! | find /i "_generated" >nul
  if not errorlevel 1 (
    REM skip
  ) else (
    for /f "tokens=2 delims=_" %%N in ("!BASENAME!") do set "N=%%N"

    rem Costruisce i percorsi della coppia: reference e candidate
    set "REF=%DIR%\example_!N!.ps1"
    set "CAND=%DIR%\example_!N!_generated.ps1"

    rem Procede solo se entrambi i file esistono
    if exist "!REF!" if exist "!CAND!" (
      set /a COUNT+=1
      echo [RUN] N=!N!  "%%~fnF"  vs  "!CAND!"

      rem Opzione settings (se -settings è stato passato)
      set "OPT_SETTINGS="
      if defined SETTINGS set "OPT_SETTINGS=-Settings ""%SETTINGS%"""

      rem Opzioni artifacts JSON (se richiesto con -artifacts json)
      set "OPT_ART="
      if /I "%ARTIFACTS%"=="json" set "OPT_ART=-Artifacts Json -ArtifactsDir ""%ART_DIR%"""

      rem Invoca lo script PowerShell che fa il confronto e appende al CSV
      powershell -NoProfile -ExecutionPolicy Bypass -File "%HELPER%" ^
        -Ref "!REF!" -Cand "!CAND!" -Number !N! -CsvPath "%CSV%" %OPT_SETTINGS% %OPT_ART%

      rem Controlla l’esito della chiamata PowerShell
      if errorlevel 1 (
        echo [WARN] N=!N!: confronto fallito
      ) else (
        echo [OK  ] N=!N! completato
      )

      rem Se c’è un limite di coppie da processare, interrompe al raggiungimento
      if defined LIMIT (
        for /f "delims=" %%L in ("%LIMIT%") do if !COUNT! GEQ %%L goto done
      )
    ) else (
      rem Segnala file mancanti nella coppia
      if not exist "!REF!"  echo [WARN] N=!N!: reference mancante
      if not exist "!CAND!" echo [WARN] N=!N!: candidate mancante
    )
  )
)

:done
echo [DONE] Confronti eseguiti: %COUNT%
echo [CSV ] "%CSV%"
exit /b 0
