import os, re, sys, json
sys.path.insert(0, r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\package_src")
log = open(r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\emoji_scan.txt","w",encoding="utf-8")
try:
    import plotly as pl
    log.write(f"plotly OK version={pl.__version__}\n")
except Exception as e:
    log.write(f"plotly FAIL {e}\n")
log.flush()
# Regex emoji amplio (rangos unicode comunes usados anteriormente en el proyecto: ️️)
EMOJI_RE = re.compile("["
    u"\U0001F300-\U0001FAFF"
    u"\u2600-\u27BF"
    u"\U0001F1E0-\U0001F1FF"
    u"\u2B00-\u2BFF"
    "]+", flags=re.UNICODE)
ROOTS = [
    r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3",
    r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\Trabajo de Grado"
]
EXCLUDE_DIRS = {".venv","__pycache__","dist",".git","python_portable"}
EXCLUDE_EXTS = {".png",".jpg",".jpeg",".gif",".joblib",".whl",".csv",".parquet",".log",".exe",".dll",".pyd",".pyc",".zip",".pdf"}
findings = []
for root in ROOTS:
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in EXCLUDE_DIRS]
        for fn in fns:
            ext = os.path.splitext(fn)[1].lower()
            if ext in EXCLUDE_EXTS: continue
            fp = os.path.join(dp, fn)
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as f:
                    txt = f.read()
            except:
                continue
            lines = txt.splitlines()
            for i, line in enumerate(lines, 1):
                if EMOJI_RE.search(line):
                    findings.append((fp, i, line))
log.write(f"TOTAL_FINDINGS={len(findings)}\n")
for fp, i, line in findings:
    log.write(f"{fp} L{i}: {line[:200]}\n")
# JSON lista para modificar programáticamente
with open(r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\emoji_findings.json","w",encoding="utf-8") as fj:
    json.dump([{"file":fp,"line":i,"text":line[:500]} for fp,i,line in findings], fj, ensure_ascii=False, indent=2)
log.write("DONE\n")
log.flush()
log.close()
