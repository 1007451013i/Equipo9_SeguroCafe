@ECHO OFF
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION
chcp 850 >nul 2>&1

cd /D "%~dp0"
IF NOT EXIST logs MKDIR logs
SET "ROOT=%~dp0"

(ECHO [%%] 0/100 - INICIO - !DATE! !TIME!) > _ESTADO.txt
(ECHO PROYECTO: Seguro Agricola Indexado - Quindio y Narino - Equipo 9) >> _ESTADO.txt
(ECHO FASE 2 Entrega Semana 5 - MIAD Uniandes 2026) >> _ESTADO.txt
(ECHO Directorio: !ROOT!) >> _ESTADO.txt

SET "PYEXE="
IF EXIST "!ROOT!python_portable\python.exe" SET "PYEXE=!ROOT!python_portable\python.exe"

IF DEFINED PYEXE (
    ECHO [OK] Python portable: !PYEXE! >> _ESTADO.txt
) ELSE (
    ECHO [ERROR %% 1] No existe python_portable\python.exe en !ROOT! >> _ESTADO.txt
    EXIT /B 1
)

ECHO [%%] 5/100 - FASE 1/3 pip install paquetes... >> _ESTADO.txt

"!PYEXE!" -m pip install --only-binary=:all: --no-warn-script-location --no-color --progress-bar off -r "!ROOT!requirements.txt" >> logs\_log_pip_std.txt 2>> logs\_log_pip_err.txt

IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR %% 5] pip install FAIL codigo %ERRORLEVEL% - ver logs\_log_pip_err.txt >> _ESTADO.txt
    EXIT /B 2
)

ECHO [%%] 30/100 - FASE 1/3 pip install OK >> _ESTADO.txt

ECHO [%%] 32/100 - FASE 2/3 ETL etl_equipo9.py... >> _ESTADO.txt

"!PYEXE!" -u etl_equipo9.py >> logs\_log_etl_std.txt 2>> logs\_log_etl_err.txt

IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR %% 32] ETL FAIL codigo %ERRORLEVEL% - ver logs\_log_etl_err.txt >> _ESTADO.txt
    EXIT /B 3
)

ECHO [%%] 45/100 - FASE 2/3 ETL OK - 8 CSVs data/processed >> _ESTADO.txt

IF NOT EXIST notebooks\outputs MKDIR notebooks\outputs
IF NOT EXIST outputs MKDIR outputs

ECHO [%%] 47/100 - FASE 3/3 pipeline_equipo9.py - 4 modelos + HE + PermImp + 6 PNGs... >> _ESTADO.txt

"!PYEXE!" -u pipeline_equipo9.py >> logs\_log_pipeline_std.txt 2>> logs\_log_pipeline_err.txt

IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR %% 47] PIPELINE FAIL codigo %ERRORLEVEL% - ver logs\_log_pipeline_err.txt >> _ESTADO.txt
    EXIT /B 4
)

ECHO [%%] 95/100 - FASE 3/3 pipeline OK - 10 CSVs notebooks/outputs + 6 PNGs outputs >> _ESTADO.txt

SET cntCSVproc=0
SET cntCSVout=0
SET cntPNG=0

FOR %%A IN ("data\processed\*_equipo9.csv") DO SET /A cntCSVproc+=1
FOR %%A IN ("notebooks\outputs\*_equipo9.csv") DO SET /A cntCSVout+=1
FOR %%A IN ("outputs\*equipo9.png") DO SET /A cntPNG+=1

ECHO. >> _ESTADO.txt
ECHO ======================================================================== >> _ESTADO.txt
ECHO RESUMEN FINAL ARCHIVOS GENERADOS Equipo 9 _equipo9 >> _ESTADO.txt
ECHO CSVs data/processed:       !cntCSVproc!  / 8  minimo >> _ESTADO.txt
ECHO CSVs notebooks/outputs:    !cntCSVout!  / 10 minimo >> _ESTADO.txt
ECHO PNGs outputs:              !cntPNG!      / 6  minimo >> _ESTADO.txt

SET "STATUS=INCOMPLETO"

IF !cntCSVproc! GEQ 8 IF !cntCSVout! GEQ 10 IF !cntPNG! GEQ 6 SET "STATUS=COMPLETO 100"

ECHO ESTADO GLOBAL: !STATUS! >> _ESTADO.txt
ECHO ======================================================================== >> _ESTADO.txt
ECHO [%%] 100/100 - FIN - !DATE! !TIME! >> _ESTADO.txt

ENDLOCAL
EXIT /B 0
