param(
    [Parameter(Mandatory=$true)]
    [string] $InputPath,
    [Parameter(Mandatory=$true)]
    [string] $OutputJsonPath
)

# Leggi il contenuto del file
$code = Get-Content -Raw -Path $InputPath -Encoding UTF8

# Tokenizza
$errors = $null
$tokens = [System.Management.Automation.PSParser]::Tokenize($code, [ref] $errors)

if ($errors.Count -gt 0) {
    Write-Host "Errore di parsing in $InputPath tokenizzazione incompleta"
}

# Prepara oggetti per JSON
$tokenObjs = $tokens | ForEach-Object {
    [PSCustomObject]@{
        Content     = $_.Content
        Type        = $_.Type.ToString()
        StartOffset = $_.Start
        Length      = $_.Length
        StartLine   = $_.StartLine
        StartColumn = $_.StartColumn
    }
}

# Esporta JSON
$tokenObjs | ConvertTo-Json -Depth 4 | Out-File -FilePath $OutputJsonPath -Encoding UTF8
