$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$python = "..\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

& $python -m pip install pyinstaller
& $python -m PyInstaller --onefile --windowed --name JsonConverter .\json_converter.py

Write-Host "Built: .\dist\JsonConverter.exe"
