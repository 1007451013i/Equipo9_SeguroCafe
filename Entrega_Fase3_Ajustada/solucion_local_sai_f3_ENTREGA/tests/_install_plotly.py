import sys, os, site
log_path = r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\plotly_install.log"
with open(log_path, "w", encoding="utf-8") as log:
    log.write(f"PYTHON EXE = {sys.executable}\n")
    log.write(f"VERSION = {sys.version}\n")
    log.write(f"PATH = {os.pathsep.join(sys.path)}\n")
    log.write(f"SITE PACKAGES (getsitepackages) = {site.getsitepackages()}\n")
    try:
        import plotly
        log.write(f"plotly OK: {plotly.__file__} version={plotly.__version__}\n")
    except Exception as e:
        log.write(f"plotly FAIL IMPORT: {type(e).__name__}: {e}\n")
    # Intentar importar pip dentro y reinstalar con --target = site package del portable
    try:
        sp_dirs = site.getsitepackages()
        if sp_dirs:
            log.write(f"INSTALAR con --target={sp_dirs[0]}\n")
            import subprocess
            cmd = [sys.executable, "-m", "pip", "install", "--quiet", "--no-warn-script-location",
                   "--target", sp_dirs[0], "plotly==5.22.0", "tenacity>=8.0", "packaging"]
            log.write(f"CMD: {' '.join(cmd)}\n")
            r = subprocess.run(cmd, capture_output=True, text=True)
            log.write(f"rc={r.returncode}\nSTDOUT:\n{r.stdout[-800:]}\nSTDERR:\n{r.stderr[-800:]}\n")
    except Exception as e2:
        log.write(f"INSTALL FAIL SUBPROCESS: {type(e2).__name__}: {e2}\n")
    # Volver a importar
    try:
        import plotly as pl2
        log.write(f"DESPUES plotly OK: {pl2.__file__} v={pl2.__version__}\n")
        import plotly.express as px
        log.write(f"plotly.express OK {px.__name__}\n")
        import plotly.graph_objects as go
        log.write(f"plotly.graph_objects OK {go.__name__}\n")
    except Exception as e3:
        log.write(f"AFTER FAIL: {type(e3).__name__}: {e3}\n")
        import traceback
        log.write(traceback.format_exc())
log.close()
