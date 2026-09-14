#requires -Version 5.1
<#
.SYNOPSIS
  Levantar la API FastAPI en puerto 8000 (default). Usa uvicorn desde el entorno virtual.
#>

param(
    [int]$Port = 8000,
    [string]$Host = "127.0.0.1",
    [switch]$NoReload
)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot
$env:CAFE_SAI_MODELS_DIR = Join-Path $ProjectRoot "models_artifacts"

if ($env:VIRTUAL_ENV) {
    $uvicorn = Join-Path $env:VIRTUAL_ENV "Scripts\uvicorn.exe"
    if (-not (Test-Path $uvicorn)) {
        $uvicorn = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
        $argsExtra = @("-m","uvicorn")
    }
} else {
    $venvUvicorn = Join-Path (Join-Path $ProjectRoot ".venv") "Scripts\uvicorn.exe"
    $venvPy = Join-Path (Join-Path $ProjectRoot ".venv") "Scripts\python.exe"
    if (Test-Path $venvUvicorn) {
        $uvicorn = $venvUvicorn
    } elseif (Test-Path $venvPy) {
        $uvicorn = $venvPy
        $argsExtra = @("-m","uvicorn")
    } else {
        $uvicorn = (Get-Command python.exe -ErrorAction Stop).Source
        $argsExtra = @("-m","uvicorn")
    }
}

$params = @("api.main:app","--host",$Host,"--port","$Port")
if (-not $NoReload) { $params += @("--reload","--reload-dir",(Join-Path $ProjectRoot "api"),"--reload-dir",(Join-Path $ProjectRoot "package_src")) }

Write-Host "▶️  API en http://${Host}:${Port}   (docs: http://${Host}:${Port}/docs)" -ForegroundColor DarkGreen
Write-Host "   Python: $uvicorn" -ForegroundColor Gray
$cmdArgs = $argsExtra + $params
& $uvicorn @cmdArgs
