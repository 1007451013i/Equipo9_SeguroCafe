import os, re, sys
EMOJI_RE = re.compile("["
    u"\U0001F300-\U0001FAFF"
    u"\u2600-\u27BF"
    u"\U0001F1E0-\U0001F1FF"
    u"\u2B00-\u2BFF"
    u"\u2300-\u23FF"
    "]+", flags=re.UNICODE)
# SOLO archivos de texto creados por nosotros
CANDIDATES = [
    r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\README.md",
    r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\run_dashboard.ps1",
    r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\run_api.ps1",
    r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\setup_dev.ps1",
    r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\build_package.ps1",
    r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\README_PACKAGE.md",
    r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\dashboard\app.py",
    r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\Trabajo de Grado\Guia_Solucion_SAI_F3.md",
]
# Recursivamente agregar pages/*.py, api/*.py, tests/*.py, package_src/**/*.py
for extra_root in [
    r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\dashboard",
    r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\api",
    r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests",
    r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\package_src"
]:
    for dp, dns, fns in os.walk(extra_root):
        for fn in fns:
            ext = os.path.splitext(fn)[1].lower()
            if ext in {".py",".md",".ps1",".txt",".json",".toml",".yaml",".yml"}:
                fp = os.path.join(dp, fn)
                if fp not in CANDIDATES:
                    CANDIDATES.append(fp)
log = open(r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\emoji_fix.log","w",encoding="utf-8")
total_changes = 0
files_changed = 0
for fp in CANDIDATES:
    if not os.path.exists(fp):
        continue
    try:
        with open(fp, "r", encoding="utf-8", errors="replace") as f:
            txt = f.read()
    except Exception as e:
        log.write(f"SKIP READ {fp}: {e}\n"); continue
    new_txt = EMOJI_RE.sub("", txt)
    # Tambien reemplazar los checkmarks tipicos a texto plano: ->(!), ->(bal.), etc.
    if new_txt != txt:
        with open(fp, "w", encoding="utf-8", newline="") as f:
            f.write(new_txt)
        diff_count = sum(1 for a,b in zip(txt.splitlines(), new_txt.splitlines()) if a != b)
        files_changed += 1
        total_changes += diff_count
        log.write(f"FIXED {diff_count} lines -> {fp}\n")
log.write(f"\nDONE files_changed={files_changed} total_line_changes={total_changes}\n")
log.close()
