Write-Host "=== Inicio Smoke ==="
$py = "C:\Users\mvale\OneDrive\Escritorio\Caso 01\Trabajo de Grado\python_portable\python.exe"
$s = "c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\smoke_package.py"
$log = "c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\smoke_out.log"
$wd = Split-Path $s -Parent

$psi = [System.Diagnostics.ProcessStartInfo]::new()
$psi.FileName = $py
$psi.Arguments = "`"$s`""
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false
$psi.WorkingDirectory = $wd
$proc = [System.Diagnostics.Process]::Start($psi)
$stdout = $proc.StandardOutput.ReadToEnd()
$stderr = $proc.StandardError.ReadToEnd()
$proc.WaitForExit()

$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine("EXIT=$($proc.ExitCode)")
[void]$sb.AppendLine("=== STDOUT ===")
[void]$sb.AppendLine($stdout)
[void]$sb.AppendLine("=== STDERR ===")
[void]$sb.AppendLine($stderr)
[System.IO.File]::WriteAllText($log, $sb.ToString(), [System.Text.Encoding]::UTF8)
Write-Host "Finalizado. Log: $log"
Get-Content $log -Raw
