#requires -Version 5.1
<#
.SYNOPSIS
  Build wheel package manual (si ya tienes entorno .venv activo / requisitos instalados).
#>

param(
    [switch]$Force
)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot
$ErrorActionPreference = "Stop"

$PyAuto = $env:VIRTUAL_ENV
if ($PyAuto) {
    $PyExe = Join-Path $PyAuto "Scripts\python.exe"
} else {
    if (Test-Path ".venv\Scripts\python.exe") {
        $PyExe = (Resolve-Path ".venv\Scripts\python.exe").Path
    } else {
        $PyExe = (Get-Command python.exe -ErrorAction Stop).Source
    }
}

Write-Host "Usando Python: $PyExe" -ForegroundColor DarkCyan
$dist = Join-Path $ProjectRoot "dist"
if ((Get-ChildItem (Join-Path $dist "cafe_sai_modelos_equipo9-*.whl") -ErrorAction SilentlyContinue | Measure-Object).Count -and -not $Force) {
    Write-Host "Ya existen wheels en dist/; usa -Force para re-build."
    exit 0
}
& $PyExe -m build --outdir $dist --wheel --no-isolation
if ($LASTEXITCODE -ne 0) { Write-Error "fallo build." }
Write-Host "Build OK:" -ForegroundColor Green
Get-ChildItem (Join-Path $dist "cafe_sai_modelos_equipo9-*.whl") | Select-Object Name, Length
