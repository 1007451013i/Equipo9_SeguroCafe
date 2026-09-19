$py = "C:\Users\mvale\OneDrive\Escritorio\Caso 01\Trabajo de Grado\python_portable\python.exe"
$root = "c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3"

$env:CAFE_SAI_MODELS_DIR = "$root\models_artifacts"
$env:SAI_API_BASE        = "http://127.0.0.1:8000"

Get-Process -Name python -ErrorAction SilentlyContinue | ForEach-Object {
  try   { $mins = ((Get-Date) - $_.StartTime).TotalMinutes }
  catch { $mins = 9999 }
  if ($mins -gt 3) {
    Write-Host ("Kill old python PID=" + $_.Id + " mins=" + [math]::Round($mins,1))
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
  }
}
Start-Sleep -Seconds 2

$apiSo = "$root\tests\uvicorn_api_stdout.log"
$apiSe = "$root\tests\uvicorn_api_stderr.log"
$dashSo = "$root\tests\streamlit_stdout.log"
$dashSe = "$root\tests\streamlit_stderr.log"
foreach ($f in @($apiSo,$apiSe,$dashSo,$dashSe)) {
  if (Test-Path $f) { Remove-Item $f -Force -ErrorAction SilentlyContinue }
  "" | Set-Content $f
}

# IMPORTANTE: NO usar -NoNewWindow. Los procesos independientes sobreviven al proceso padre.
# -WindowStyle Hidden esconde la consola. -RedirectStandardOutput/Error sigue funcionando.
$pAPI  = Start-Process -FilePath $py `
  -ArgumentList ("-m uvicorn api.main:app --host 127.0.0.1 --port 8000 --no-access-log") `
  -WorkingDirectory $root `
  -RedirectStandardOutput $apiSo -RedirectStandardError $apiSe `
  -WindowStyle Hidden -PassThru

$pDash = Start-Process -FilePath $py `
  -ArgumentList ('-m streamlit run app.py --server.headless true --server.port 8501 --server.address 127.0.0.1 --server.maxUploadSize 2 --browser.gatherUsageStats false') `
  -WorkingDirectory "$root\dashboard" `
  -RedirectStandardOutput $dashSo -RedirectStandardError $dashSe `
  -WindowStyle Hidden -PassThru

("API=" + $pAPI.Id)  | Set-Content "$root\tests\running_pids.txt"
("DASH=" + $pDash.Id) | Add-Content "$root\tests\running_pids.txt"

Write-Host ("PIDs: API=" + $pAPI.Id + " DASH=" + $pDash.Id + "  Esperando 70s...")
Start-Sleep -Seconds 70

$aliveAPI  = (Get-Process -Id $pAPI.Id  -ErrorAction SilentlyContinue) -ne $null
$aliveDASH = (Get-Process -Id $pDash.Id -ErrorAction SilentlyContinue) -ne $null
Write-Host ("Alive API=$aliveAPI DASH=$aliveDASH")

# Intentos HTTP con reintentos (por si Streamlit aún no cargó bundle)
for ($i=1; $i -le 3; $i++) {
  try {
    $h = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 10
    Write-Host ("API /health -> status=" + $h.status + " pkg=" + $h.package_version)
    break
  } catch {
    Write-Host ("API /health intento $i FAIL: " + $_.Exception.Message)
    Start-Sleep -Seconds 4
  }
}

for ($i=1; $i -le 3; $i++) {
  try {
    $resp = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8501/" -TimeoutSec 15
    Write-Host ("DASH / -> HTTP=" + $resp.StatusCode + " bytes=" + $resp.RawContentLength)
    break
  } catch {
    Write-Host ("DASH / intento $i FAIL: " + $_.Exception.Message)
    Start-Sleep -Seconds 5
  }
}
