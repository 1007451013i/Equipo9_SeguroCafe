import sys, os, json, traceback
sys.path.insert(0, r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\package_src")
MARK = r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\pkg_ok.txt"
def w(x):
    with open(MARK, "a", encoding="utf-8") as f: f.write(x + "\n"); f.flush()
try:
    if os.path.exists(MARK): os.remove(MARK)
    w("PKG START")
    import cafe_sai_modelos_equipo9 as m
    w("PKG imported version=" + str(m.__version__))
    from cafe_sai_modelos_equipo9 import (
        predict_rendimiento, get_kpis_actuariales,
        predict_activacion_spi, get_panel_entrenamiento,
        FEATURES_FENOLOGICAS,
    )
    w("PKG FEATURES=" + str(FEATURES_FENOLOGICAS))
    gold_path = r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\_golden.json"
    gold = json.load(open(gold_path, encoding="utf-8"))
    for key, case in gold["predictions"].items():
        out = predict_rendimiento(case["departamento"], case["features"])
        diff = abs(out["prediccion_kg_ha"] - case["y_pred_kg_ha"])
        w("PRED " + key + ": pkg=" + str(round(out["prediccion_kg_ha"], 9))
          + " expected=" + str(case["y_pred_kg_ha"]) + " diff=" + str(diff)
          + " status=" + out["status"])
        if diff > 1e-6: raise AssertionError("MISMATCH " + key)
    kp = get_kpis_actuariales()
    for d in ("Narino", "Quindio"):
        k = kp[d]
        w("KPI " + d + ": rmse=" + str(k["rmse_holdout_mejor"])
          + " HE=" + str(k["HE_Ederington"])
          + " prima=" + str(k["prima_actuarial_pct"])
          + " rb=" + str(k["riesgo_base_pct"])
          + " pago=" + str(k["pago_cop_ha"])
          + " act=" + str(k["pct_total_activacion"]))
    assert kp["Narino"]["rmse_holdout_mejor"] == 15.1, "RMSE NAR"
    assert kp["Narino"]["HE_Ederington"] == 0.05, "HE NAR"
    assert abs(kp["Narino"]["prima_actuarial_pct"] - 6.36) < 1e-9, "PRIMA NAR"
    assert kp["Quindio"]["rmse_holdout_mejor"] == 45.7, "RMSE QUI"
    assert kp["Quindio"]["HE_Ederington"] == 0.11, "HE QUI"
    assert abs(kp["Quindio"]["prima_actuarial_pct"] - 10.15) < 1e-9, "PRIMA QUI"
    assert kp["Narino"]["pago_cop_ha"] == 1200000
    a1 = predict_activacion_spi("Narino", {"spi_min_e9": -2.0})
    a2 = predict_activacion_spi("Narino", {"roya_dummy": 1, "roya_shock": 1})
    a3 = predict_activacion_spi("Quindio", {"spi3_cosecha": -1.0})
    a4 = predict_activacion_spi("Quindio", {"spi3_cosecha": -2.3})
    w("SPI NAR -2.0: activo=" + str(a1["activo"]) + " regla=" + str(a1["regla_activada"]) + " pago=" + str(a1["pago_cop_ha"]))
    w("SPI NAR ROYA: activo=" + str(a2["activo"]))
    w("SPI QUI -1.0: activo=" + str(a3["activo"]) + " umbP10=" + str(a3["umbral_sequia_p10"]))
    w("SPI QUI -2.3: activo=" + str(a4["activo"]))
    assert a1["activo"] and a2["activo"] and not a3["activo"] and a4["activo"]
    panel = get_panel_entrenamiento()
    w("PANEL shape=" + str(panel.shape) + " deptos=" + str(sorted(panel["departamento"].unique().tolist())))
    assert panel.shape == (24, 48), "PANEL SHAPE"
    try:
        predict_rendimiento("Bogota", {f: 0.1 for f in FEATURES_FENOLOGICAS} | {"roya_dummy": 0})
        w("FAIL raise Bogota"); sys.exit(31)
    except ValueError as e:
        w("OK raise Bogota: " + type(e).__name__)
    try:
        predict_rendimiento("Narino", {f: 0.1 for f in FEATURES_FENOLOGICAS if f != "spi3_floracion"} | {"roya_dummy": 0})
        w("FAIL raise falta campo"); sys.exit(32)
    except ValueError as e:
        w("OK raise falta campo: " + type(e).__name__)
    try:
        bad = {f: 0.1 for f in FEATURES_FENOLOGICAS} | {"roya_dummy": 5}
        predict_rendimiento("Narino", bad)
        w("FAIL raise roya 5"); sys.exit(33)
    except ValueError as e:
        w("OK raise roya 5: " + type(e).__name__)
    bad_extra = {f: 0.1 for f in FEATURES_FENOLOGICAS} | {"roya_dummy": 0, "campo_extra": 1.23}
    outw = predict_rendimiento("Narino", bad_extra)
    w("WARNINGS count=" + str(len(outw["warnings"])) + " w=" + str(outw["warnings"]))
    assert len(outw["warnings"]) >= 1
    w("ALL PACKAGE TESTS PASSED OK")
except Exception as e:
    w("!!! EXCEPTION: " + str(e) + "\n" + traceback.format_exc())
    sys.exit(1)
