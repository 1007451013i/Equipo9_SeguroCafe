#requires -Version 5.1
<#
.SYNOPSIS
  Levantar el Dashboard Streamlit en puerto 8501 (default).
#>

param(
    [int]$Port = 8501,
    [string]$DashHost = "127.0.0.1",
    [string]$ApiBase = "http://127.0.0.1:8000"
)

# Portable: resuelve la raiz del proyecto a partir de la ubicacion ESTE script.
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $ProjectRoot "dashboard")
$env:SAI_API_BASE = $ApiBase
$env:CAFE_SAI_MODELS_DIR = Join-Path $ProjectRoot "models_artifacts"

if ($env:VIRTUAL_ENV) {
    $st = Join-Path $env:VIRTUAL_ENV "Scripts\streamlit.exe"
    if (-not (Test-Path $st)) {
        $st = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
        $argsExtra = @("-m","streamlit")
    }
} else {
    $venvST = Join-Path (Join-Path $ProjectRoot ".venv") "Scripts\streamlit.exe"
    $venvPy = Join-Path (Join-Path $ProjectRoot ".venv") "Scripts\python.exe"
    if (Test-Path $venvST) {
        $st = $venvST
    } elseif (Test-Path $venvPy) {
        $st = $venvPy
        $argsExtra = @("-m","streamlit")
    } else {
        $st = (Get-Command python.exe -ErrorAction Stop).Source
        $argsExtra = @("-m","streamlit")
    }
}

$params = @(
    "run", "app.py",
    "--server.headless","true",
    "--server.port","$Port",
    "--server.address",$DashHost,
    "--server.maxUploadSize","2",
    "--browser.gatherUsageStats","false"
)

Write-Host ("Dashboard en http://" + $DashHost + ":" + $Port + "  (API: " + $ApiBase + ")") -ForegroundColor DarkGreen
Write-Host "   Antes de abrir el navegador, ejecuta .\run_api.ps1 en otra terminal." -ForegroundColor Yellow
$cmdArgs = $argsExtra + $params
& $st @cmdArgs
