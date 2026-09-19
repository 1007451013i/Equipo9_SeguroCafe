import sys, os, json, traceback
MARK = r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\t_pkg.log"
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
        w("T2 pred  pkg=" + str(round(out["prediccion_kg_ha"],9)) + " expected=" + str(case["y_pred_kg_ha"]) + " diff=" + str(diff) + " status=" + out["status"])
        if diff > 1e-6: raise AssertionError("MISMATCH  diff=")
    kp = get_kpis_actuariales()
    for d in ("Narino","Quindio"):
        k = kp[]
        w("T2 KPI  rmse=" + str(k["rmse_holdout_mejor"]) + " HE=" + str(k["HE_Ederington"]) + " prima=" + str(k["prima_actuarial_pct"]) + " pago=" + str(k["pago_cop_ha"]) + " act=" + str(k["pct_total_activacion"]))
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
