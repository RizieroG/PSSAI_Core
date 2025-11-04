param(
    # Path allo script "reference"
    [Parameter(Mandatory)][string]$Ref,
    # Path allo script "candidate"
    [Parameter(Mandatory)][string]$Cand,
    # Numero identificativo della coppia (es. N dell'example_N)
    [Parameter(Mandatory)][int]$Number,
     # CSV di output (append di una riga per coppia)
    [string]$CsvPath = ".\pssa_results.csv",
    [string]$Settings = $null,
    [ValidateSet('None','Json')][string]$Artifacts = 'None',
    # Cartella dove scrivere gli artifacts JSON
    [string]$ArtifactsDir = ".\pssa_artifacts"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-PSSA-One {
    param([string]$Path, [string]$Settings)
    if ($Settings) {
        return Invoke-ScriptAnalyzer -Path $Path -Settings $Settings
    } else {
        return Invoke-ScriptAnalyzer -Path $Path
    }
}

# Riassume i findings: conta severità e raccoglie i RuleName unici
function Summarize {
    param([object[]]$Findings)

    # normalizza: $Findings = @() se null
    if ($null -eq $Findings) { $Findings = @() }

    # Conteggi per severità
    $errors   = @($Findings | Where-Object { $_.Severity -eq 'Error' }).Count
    $warnings = @($Findings | Where-Object { $_.Severity -eq 'Warning' }).Count
    $infos    = @($Findings | Where-Object { $_.Severity -eq 'Information' }).Count

    # Estrae i RuleName solo se c'è almeno un finding
    $ruleNames = @()
    if ($Findings.Count -gt 0) {
        $ruleNames = $Findings | ForEach-Object { $_.RuleName } | Sort-Object -Unique
    }

    [pscustomobject]@{
        errors   = $errors
        warnings = $warnings
        infos    = $infos
        rules    = $ruleNames
    }
}

# Unisce una lista di stringhe con ';' per una singola cella CSV
function JoinList {
    param([string[]]$Items)
    if (-not $Items) { return "" }
    return ($Items -join ';')
}

try {
    # 1) Esecuzione PSScriptAnalyzer su Ref e Cand
    $refRes  = Invoke-PSSA-One -Path $Ref  -Settings $Settings
    $candRes = Invoke-PSSA-One -Path $Cand -Settings $Settings

    # 2) Riassunti (contatori + lista regole)
    $sR = Summarize $refRes
    $sC = Summarize $candRes

    $refRules  = @($sR.rules)
    $candRules = @($sC.rules)

    # 3) Confronto regole: comuni e uniche
    $common     = @()
    $uniqueRef  = @()
    $uniqueCand = @()

    # Usa Compare-Object per derivare comuni e unici
    $cmp = Compare-Object -ReferenceObject $refRules -DifferenceObject $candRules -IncludeEqual

    if ($cmp) {
        $common     = @($cmp | Where-Object SideIndicator -eq '==' | Select-Object -ExpandProperty InputObject | Sort-Object -Unique)
        $uniqueRef  = @($cmp | Where-Object SideIndicator -eq '<=' | Select-Object -ExpandProperty InputObject | Sort-Object -Unique)
        $uniqueCand = @($cmp | Where-Object SideIndicator -eq '=>' | Select-Object -ExpandProperty InputObject | Sort-Object -Unique)
    }

    # 4) Differenze nei contatori (Cand - Ref)
    $diffE = ($sC.errors   - $sR.errors)
    $diffW = ($sC.warnings - $sR.warnings)
    $diffI = ($sC.infos    - $sR.infos)

    # 5) Artifacts opzionali: salvataggio dei findings grezzi in JSON (debug/analisi post)
    if ($Artifacts -eq 'Json') {
        if (-not (Test-Path -LiteralPath $ArtifactsDir)) {
            New-Item -ItemType Directory -Path $ArtifactsDir | Out-Null
        }
        $base = (Split-Path -Leaf $Ref) -replace '\.ps1$',''
        $refJson  = Join-Path $ArtifactsDir "$base.ref.pssa.json"
        $candJson = Join-Path $ArtifactsDir "$base.cand.pssa.json"
        $refRes  | ConvertTo-Json -Depth 6 | Out-File -Encoding UTF8 -FilePath $refJson
        $candRes | ConvertTo-Json -Depth 6 | Out-File -Encoding UTF8 -FilePath $candJson
    }

    # 6) Composizione della riga CSV (campi separati da virgola; liste joinate con ';')
    $line = @(
        $Number
        ('"{0}"' -f $Ref)
        ('"{0}"' -f $Cand)
        $sR.errors
        $sR.warnings
        $sR.infos
        $sC.errors
        $sC.warnings
        $sC.infos
        $diffE
        $diffW
        $diffI
        ('"{0}"' -f (JoinList $sR.rules))
        ('"{0}"' -f (JoinList $sC.rules))
        ('"{0}"' -f (JoinList $common))
        ('"{0}"' -f (JoinList $uniqueRef))
        ('"{0}"' -f (JoinList $uniqueCand))
    ) -join ','

    # Appende la riga al CSV (UTF-8)
    Add-Content -Path $CsvPath -Value $line -Encoding UTF8
    exit 0
}
catch {
    Write-Host "[ERR] $($_.Exception.Message)"
    exit 1
}
