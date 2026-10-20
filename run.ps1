$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -3 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.11–3.13, then try again.' }
}
& .venv\Scripts\python.exe scripts/check_dependencies.py
if ($LASTEXITCODE -ne 0) {
    if ($env:HALLOWEEN_WHEEL_DIR) {
        & .venv\Scripts\python.exe -m pip install --no-index --find-links $env:HALLOWEEN_WHEEL_DIR -r requirements.txt
    } else {
        & .venv\Scripts\python.exe -m pip install --disable-pip-version-check -r requirements.txt
    }
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
}
& .venv\Scripts\python.exe -m halloween_hub @args
exit $LASTEXITCODE
