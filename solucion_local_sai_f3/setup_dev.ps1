#requires -Version 5.1
<#
.SYNOPSIS
  (1a) Crea un entorno virtual en .venv, (1b) instala requirements.txt,
  (1c) ejecuta el serializador de modelos (si los .joblib no existen),
  (1d) build del wheel package.

.DESCRIPTION
  Solo funciona con Python 3.11+ estandar (Microsoft Store o python.org).
  Requisitos: los modelos .joblib oficiales ya deben existir en models_artifacts/.
  Si no existen y las fuentes originales de build estan disponibles en una
  carpeta hermana, el serializador intentara regenerarlos. Esta carpeta es
  100% portable y no requiere fuentes externas para RUNTIME (solo para build).
#>

param(
    [ValidateSet("3.11", "3.12")]
    [string]$PyVersion = "3.11",
    [switch]$ForceRebuildWheel,
    [switch]$SkipModelsBuild
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "== [1/6] Localizando py launcher y Python $PyVersion ==" -ForegroundColor DarkCyan
$PyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
if (-not $PyLauncher) {
    Write-Error "No se encontró py.exe en PATH. Instala Python 3.11 estándar (python.org o Microsoft Store)."
}
try {
    & py.exe -$PyVersion -c "import sys; print(sys.version)"
} catch {
    Write-Error "No existe Python $PyVersion instalado. Instálalo desde Microsoft Store / python.org."
}

Write-Host "== [2/6] Creando entorno virtual .venv ==" -ForegroundColor DarkCyan
if (-not (Test-Path (Join-Path $ProjectRoot ".venv\Scripts\python.exe"))) {
    & py.exe -$PyVersion -m venv (Join-Path $ProjectRoot ".venv")
    if ($LASTEXITCODE -ne 0) { Write-Error "venv create falló." }
}

$venvPy = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$venvPip = Join-Path $ProjectRoot ".venv\Scripts\pip.exe"
$venvActivate = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"
Write-Host "    Python venv: $venvPy" -ForegroundColor Green

Write-Host "== [3/6] Actualizando pip + instalando requirements.txt ==" -ForegroundColor DarkCyan
& $venvPy -m pip install --upgrade pip wheel build hatchling --no-input --quiet 2>$null
& $venvPip install -r (Join-Path $ProjectRoot "requirements.txt") --no-input --disable-pip-version-check
if ($LASTEXITCODE -ne 0) { Write-Error "pip install -r requirements.txt falló." }

Write-Host "== [4/6] Serializar modelos (si no existen los .joblib) ==" -ForegroundColor DarkCyan
$artifactDir = Join-Path $ProjectRoot "models_artifacts"
$narJob = Join-Path $artifactDir "narino_extratrees_entrega2.joblib"
$quiJob = Join-Path $artifactDir "quindio_randomforest_entrega2.joblib"
if ((-not $SkipModelsBuild) -and (-not (Test-Path $narJob) -or -not (Test-Path $quiJob))) {
    Write-Host "   Modelos faltantes. Ejecutando serializador ..."
    $env:CAFE_SAI_MODELS_DIR = $artifactDir
    $serializador = Join-Path $ProjectRoot "package_src\cafe_sai_modelos_equipo9\_build\00_serializar_modelos_oficiales.py"
    & $venvPy $serializador
    if ($LASTEXITCODE -ne 0) { Write-Error "Serializador de modelos falló." }
}

Write-Host "== [5/6] Build wheel del package ==" -ForegroundColor DarkCyan
$distDir = Join-Path $ProjectRoot "dist"
$wheelExistente = Get-ChildItem (Join-Path $distDir "cafe_sai_modelos_equipo9-*.whl") -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (($ForceRebuildWheel) -or (-not $wheelExistente)) {
    & $venvPy -m build --outdir $distDir --wheel --no-isolation
    if ($LASTEXITCODE -ne 0) { Write-Error "fallo `python -m build`." }
    $wheelExistente = Get-ChildItem (Join-Path $distDir "cafe_sai_modelos_equipo9-*.whl") -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
}
if ($wheelExistente) {
    Write-Host "    Wheel: $($wheelExistente.Name)" -ForegroundColor Green
    Write-Host "   → Instalando wheel en .venv..."
    & $venvPip install --force-reinstall --no-deps $wheelExistente.FullName | Out-Null
    Write-Host "    Instalado." -ForegroundColor Green
}

Write-Host "== [6/6] pytest T1-T5 ==" -ForegroundColor DarkCyan
& $venvPy -m pytest (Join-Path $ProjectRoot "tests") -q
if ($LASTEXITCODE -ne 0) { Write-Error "Tests fallaron." }

Write-Host "`n️  Setup dev completado." -ForegroundColor Green
Write-Host "   Activar manual: . `"$venvActivate`""
Write-Host "   Levantar API  : .\run_api.ps1"
Write-Host "   Levantar Dash : .\run_dashboard.ps1"
