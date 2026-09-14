$py = "C:\Users\mvale\OneDrive\Escritorio\Caso 01\Trabajo de Grado\python_portable\python.exe"
$script = "c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\a1_complete.py"
$log = "c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\a1_py_out.log"
Remove-Item $log -Force -ErrorAction SilentlyContinue
$psi = [System.Diagnostics.ProcessStartInfo]::new()
$psi.FileName = $py
$psi.Arguments = "`"$script`""
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false
$psi.WorkingDirectory = Split-Path $script -Parent
$p = [System.Diagnostics.Process]::Start($psi)
$so = $p.StandardOutput.ReadToEnd()
$se = $p.StandardError.ReadToEnd()
$p.WaitForExit()
$out = "EXIT=$($p.ExitCode)`r`nSTDOUT:`r`n$so`r`nSTDERR:`r`n$se"
Set-Content $log $out -Encoding UTF8
Write-Host "Process Exit: $($p.ExitCode)  Log: $log"
Get-Content $log -Raw
