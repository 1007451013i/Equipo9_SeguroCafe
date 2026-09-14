import subprocess, sys
py = r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\Trabajo de Grado\python_portable\python.exe"
MARK = r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\pip.log"
with open(MARK, "w", encoding="utf-8") as f:
    p = subprocess.Popen(
        [py, "-m", "pip", "install", "--no-input", "build", "hatchling>=1.24", "wheel"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    for line in p.stdout:
        print(line.rstrip())
        f.write(line)
    p.wait()
    f.write("\nEXIT=" + str(p.returncode) + "\n")
print("PIP INSTALL EXIT:", p.returncode)
