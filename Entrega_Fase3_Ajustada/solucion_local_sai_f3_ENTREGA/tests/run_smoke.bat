@echo off
setlocal
set PY="C:\Users\mvale\OneDrive\Escritorio\Caso 01\Trabajo de Grado\python_portable\python.exe"
set SCRIPT=c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\smoke_package.py
set LOG=c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\smoke_out.log
del /F /Q "%LOG%" 2>NUL
%PY% "%SCRIPT%" >> "%LOG%" 2>&1
echo EXIT=%ERRORLEVEL% >> "%LOG%"
type "%LOG%"
endlocal
