Write-Host "=== 1: Test de carga de modelos directo (joblib) ==="
$models = "c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\models_artifacts"
$test_dir = "c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests"
$py = "C:\Users\mvale\OneDrive\Escritorio\Caso 01\Trabajo de Grado\python_portable\python.exe"

$t1 = Join-Path $test_dir "t_joblib.txt"
Remove-Item $t1 -Force -ErrorAction SilentlyContinue
$pr1 = @"
import sys, os, json, joblib, pandas as pd
ART = r"$models"
MARK = r"$t1"
def w(x):
    with open(MARK, "a", encoding="utf-8") as f: f.write(x+"\n"); f.flush()
try:
    if os.path.exists(MARK): os.remove(MARK)
    w("T1 start")
    mn = joblib.load(os.path.join(ART, "narino_extratrees_entrega2.joblib"))
    mq = joblib.load(os.path.join(ART, "quindio_randomforest_entrega2.joblib"))
    w("T1 loaded classes: Nar=" + type(mn).__name__ + " Qui=" + type(mq).__name__)
    w("T1 Nar params: md=" + str(mn.max_depth) + " ne=" + str(mn.n_estimators) + " mf=" + str(mn.max_features) + " msl=" + str(mn.min_samples_leaf) + " rs=" + str(mn.random_state))
    w("T1 Qui params: md=" + str(mq.max_depth) + " ne=" + str(mq.n_estimators) + " mf=" + str(mq.max_features) + " msl=" + str(mq.min_samples_leaf) + " rs=" + str(mq.random_state))
    gold = json.load(open(os.path.join(ART, "..", "tests", "_golden.json"), encoding="utf-8"))
    FEATS = ["spi3_floracion","spi3_desarrollo","spi3_cosecha","tmax_mean_e9","oni_mean","roya_dummy"]
    Xn = pd.DataFrame([gold["predictions"]["Narino_2007"]["features"]], columns=FEATS)
    Xq = pd.DataFrame([gold["predictions"]["Quindio_2015"]["features"]], columns=FEATS)
    pn = float(mn.predict(Xn)[0])
    pq = float(mq.predict(Xq)[0])
    w("T1 pred Nar 2007=" + str(round(pn,9)) + " expected=" + str(gold["predictions"]["Narino_2007"]["y_pred_kg_ha"]))
    w("T1 pred Qui 2015=" + str(round(pq,9)) + " expected=" + str(gold["predictions"]["Quindio_2015"]["y_pred_kg_ha"]))
    diff_n = abs(pn - gold["predictions"]["Narino_2007"]["y_pred_kg_ha"])
    diff_q = abs(pq - gold["predictions"]["Quindio_2015"]["y_pred_kg_ha"])
    w("T1 diffs Nar=" + str(diff_n) + " Qui=" + str(diff_q))
    if diff_n > 1e-6 or diff_q > 1e-6: raise AssertionError("diff fail")
    w("T1 ALL OK joblib predict match golden")
except Exception as e:
    import traceback
    w("!!! T1 ERROR " + str(e) + "\n" + traceback.format_exc())
    sys.exit(1)
"@
$s1 = Join-Path $test_dir "t_joblib.py"
Set-Content $s1 $pr1 -Encoding UTF8
$psi1 = [System.Diagnostics.ProcessStartInfo]::new()
$psi1.FileName = $py
$psi1.Arguments = "`"$s1`""
$psi1.UseShellExecute = $false
$psi1.RedirectStandardOutput = $true
$psi1.RedirectStandardError = $true
$p1 = [System.Diagnostics.Process]::Start($psi1)
$null = $p1.StandardOutput.ReadToEnd()
$null = $p1.StandardError.ReadToEnd()
$p1.WaitForExit()
Write-Host "T1 Exit=$($p1.ExitCode)"
Start-Sleep 1
if (Test-Path $t1) { Get-Content $t1 } else { Write-Host "T1 LOG MISSING" }

Write-Host ""
Write-Host "=== 2: Test package via PYTHONPATH env ==="
$t2 = Join-Path $test_dir "t_pkg.log"
Remove-Item $t2 -Force -ErrorAction SilentlyContinue
$pr2 = @"
import sys, os, json, traceback
MARK = r"$t2"
def w(x):
    with open(MARK, "a", encoding="utf-8") as f: f.write(x+"\n"); f.flush()
try:
    if os.path.exists(MARK): os.remove(MARK)
    w("T2 start path0=" + sys.path[0])
    import cafe_sai_modelos_equipo9 as m
    w("T2 imported m ver=" + str(m.__version__))
    from cafe_sai_modelos_equipo9 import predict_rendimiento, get_kpis_actuariales, predict_activacion_spi, get_panel_entrenamiento, FEATURES_FENOLOGICAS
    w("T2 FEATURES=" + str(FEATURES_FENOLOGICAS))
    gold = json.load(open(r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\_golden.json", encoding="utf-8"))
    for key, case in gold["predictions"].items():
        out = predict_rendimiento(case["departamento"], case["features"])
        diff = abs(out["prediccion_kg_ha"] - case["y_pred_kg_ha"])
        w("T2 pred $key pkg=" + str(round(out["prediccion_kg_ha"],9)) + " expected=" + str(case["y_pred_kg_ha"]) + " diff=" + str(diff) + " status=" + out["status"])
        if diff > 1e-6: raise AssertionError("MISMATCH $key diff=$diff")
    kp = get_kpis_actuariales()
    for d in ("Narino","Quindio"):
        k = kp[$d]
        w("T2 KPI $d rmse=" + str(k["rmse_holdout_mejor"]) + " HE=" + str(k["HE_Ederington"]) + " prima=" + str(k["prima_actuarial_pct"]) + " pago=" + str(k["pago_cop_ha"]) + " act=" + str(k["pct_total_activacion"]))
    assert kp["Narino"]["rmse_holdout_mejor"] == 15.1
    assert kp["Narino"]["HE_Ederington"] == 0.05
    assert abs(kp["Narino"]["prima_actuarial_pct"] - 6.36) < 1e-9
    assert kp["Quindio"]["rmse_holdout_mejor"] == 45.7
    assert kp["Quindio"]["HE_Ederington"] == 0.11
    assert abs(kp["Quindio"]["prima_actuarial_pct"] - 10.15) < 1e-9
    assert kp["Narino"]["pago_cop_ha"] == 1200000
    a1 = predict_activacion_spi("Narino", {"spi_min_e9":-2.0})
    a2 = predict_activacion_spi("Narino", {"roya_dummy":1,"roya_shock":1})
    a3 = predict_activacion_spi("Quindio", {"spi3_cosecha":-1.0})
    a4 = predict_activacion_spi("Quindio", {"spi3_cosecha":-2.3})
    w("T2 SPI N-2.0=" + str(a1["activo"]) + " regla=" + str(a1["regla_activada"]) + " pago=" + str(a1["pago_cop_ha"]))
    w("T2 SPI NRoya=" + str(a2["activo"]))
    w("T2 SPI Q-1.0=" + str(a3["activo"]) + " umbP10=" + str(a3["umbral_sequia_p10"]))
    w("T2 SPI Q-2.3=" + str(a4["activo"]))
    assert a1["activo"] is True and a2["activo"] is True and a3["activo"] is False and a4["activo"] is True
    panel = get_panel_entrenamiento()
    w("T2 PANEL shape=" + str(panel.shape) + " deptos=" + str(sorted(panel["departamento"].unique().tolist())))
    assert panel.shape == (24, 48)
    try:
        predict_rendimiento("Bogota", {f:0.1 for f in FEATURES_FENOLOGICAS} + {"roya_dummy":0})
        w("T2 FAIL: Bogota sin raise"); sys.exit(31)
    except ValueError as e: w("T2 OK raise Bogota: " + type(e).__name__)
    try:
        predict_rendimiento("Narino", {f:0.1 for f in FEATURES_FENOLOGICAS if f!="spi3_floracion"} + {"roya_dummy":0})
        w("T2 FAIL sin raise campo"); sys.exit(32)
    except ValueError as e: w("T2 OK raise falta campo: " + type(e).__name__)
    try:
        bad = {f:0.1 for f in FEATURES_FENOLOGICAS}
        bad["roya_dummy"] = 5
        predict_rendimiento("Narino", bad)
        w("T2 FAIL roya 5 raise"); sys.exit(33)
    except ValueError as e: w("T2 OK raise roya 5: " + type(e).__name__)
    bad_extra = {f:0.1 for f in FEATURES_FENOLOGICAS} + {"roya_dummy":0, "campo_xx":1.23}
    outw = predict_rendimiento("Narino", bad_extra)
    w("T2 warnings count=" + str(len(outw["warnings"])) + " w=" + str(outw["warnings"]))
    assert len(outw["warnings"]) >= 1
    w("T2 ALL TESTS IN PACKAGE OK")
except Exception as e:
    import traceback as tb2
    w("!!! T2 EXCEPTION: " + str(e) + "\n" + tb2.format_exc())
    sys.exit(2)
"@
$s2 = Join-Path $test_dir "t_pkg.py"
Set-Content $s2 $pr2 -Encoding UTF8
$psi2 = [System.Diagnostics.ProcessStartInfo]::new()
$psi2.FileName = $py
$psi2.Arguments = "`"$s2`""
$psi2.UseShellExecute = $false
$psi2.RedirectStandardOutput = $true
$psi2.RedirectStandardError = $true
$env:PYTHONPATH = "c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\package_src"
$psi2.EnvironmentVariables["PYTHONPATH"] = $env:PYTHONPATH
$p2 = [System.Diagnostics.Process]::Start($psi2)
$so2 = $p2.StandardOutput.ReadToEnd()
$se2 = $p2.StandardError.ReadToEnd()
$p2.WaitForExit()
"EXIT=$($p2.ExitCode)" | Out-File -FilePath $t2 -Append -Encoding UTF8
"STDOUT:$so2" | Out-File -FilePath $t2 -Append -Encoding UTF8
"STDERR:$se2" | Out-File -FilePath $t2 -Append -Encoding UTF8
Write-Host "T2 Exit=$($p2.ExitCode)"
Start-Sleep 1
Get-Content $t2
