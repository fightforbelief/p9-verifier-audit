param([Parameter(Mandatory=$true)][ValidateSet("ace","lightman","test")][string]$Study)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { throw "Create the project .venv with py -3.12 -m venv .venv" }
$env:PYTHONUTF8 = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
New-Item -ItemType Directory -Force reports | Out-Null
Start-Transcript -Path "reports/run-${Study}-$stamp.log"
try {
    Write-Output "Study $Study, PID $PID, UTC $stamp"
    & $py --version
    if ($LASTEXITCODE -ne 0) { throw "Environment audit failed" }
    & $py -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw "Exhaustive checks failed" }
    if ($Study -eq "ace") {
        & $py run.py gsm8k math500 minerva_math gaokao2023en olympiadbench college_math mmlu_stem
    } elseif ($Study -eq "lightman") {
        & $py run.py lightman
    }
    if ($LASTEXITCODE -ne 0) { throw "Study failed" }
    Write-Output "Completed $Study"
} finally {
    Stop-Transcript
}
