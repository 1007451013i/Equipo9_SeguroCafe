$py = "C:\Users\mvale\OneDrive\Escritorio\Caso 01\Trabajo de Grado\python_portable\python.exe"
$root = "c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3"

$env:CAFE_SAI_MODELS_DIR = "$root\models_artifacts"
$env:SAI_API_BASE        = "http://127.0.0.1:8000"

Get-Process -Name python -ErrorAction SilentlyContinue | ForEach-Object {
  try   { $mins = ((Get-Date) - $_.StartTime).TotalMinutes }
  catch { $mins = 9999 }
  # NO matar el que lleva menos de 1m que es probablemente otro script en sandbox; la API lleva >20m ya
  # Solo matar DASH (puerto 8501): buscamos python con port 8501 via netstat luego
}
# Kill via puerto 8501 (Streamlit viejo)
try {
  $conns = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue
  foreach ($c in $conns) {
    $p = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue
    if ($p -and $p.ProcessName -eq "python") {
      Write-Host ("Kill viejo Streamlit PID=" + $p.Id)
      Stop-Process -Id $p.Id -Force
      Start-Sleep -Seconds 2
    }
  }
} catch {}

$dashSo = "$root\tests\streamlit_stdout.log"
$dashSe = "$root\tests\streamlit_stderr.log"
foreach ($f in @($dashSo,$dashSe)) {
  if (Test-Path $f) { Remove-Item $f -Force -ErrorAction SilentlyContinue }
  "" | Set-Content $f
}

$dashArgs = '-m streamlit run app.py --server.headless true --server.port 8501 --server.address 127.0.0.1 --server.maxUploadSize 2 --browser.gatherUsageStats false'
$pDash = Start-Process -FilePath $py -ArgumentList $dashArgs -WorkingDirectory "$root\dashboard" -RedirectStandardOutput $dashSo -RedirectStandardError $dashSe -WindowStyle Hidden -PassThru
("DASH=" + $pDash.Id) | Add-Content "$root\tests\running_pids.txt"
Write-Host ("Nuevo Streamlit PID=" + $pDash.Id + " Esperando 50s para arranque...")
Start-Sleep -Seconds 55

$alive = (Get-Process -Id $pDash.Id -ErrorAction SilentlyContinue) -ne $null
Write-Host ("Streamlit alive: " + $alive)

# HTTP check reintentos
for ($i=1; $i -le 4; $i++) {
  try {
    $resp = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8501/" -TimeoutSec 15
    Write-Host ("DASH / intento " + $i + " HTTP=" + $resp.StatusCode + " bytes=" + $resp.RawContentLength)
    break
  } catch {
    Write-Host ("DASH / intento " + $i + " FAIL: " + $_.Exception.Message)
    Start-Sleep -Seconds 5
  }
}
