import sys, os, time, traceback
sys.path.insert(0, r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\package_src")
MARK = r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\m.txt"
def w(x):
    with open(MARK, "a", encoding="utf-8") as f:
        f.write(str(x)+"\n"); f.flush()
if os.path.exists(MARK): os.remove(MARK)
try:
    w("M0 start")
    from pathlib import Path as P
    package_root = P(r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3")
    models_dir = package_root / "models_artifacts"
    w("M1 models_dir exists=" + str(models_dir.is_dir()) + " path=" + str(models_dir))
    # Simular get_models_dir
    w("M2 now import loader")
    t0 = time.time()
    from cafe_sai_modelos_equipo9 import loader
    w("M3 loader imported, elapsed=" + str(round(time.time()-t0, 3)))
    w("M3B loader attrs: " + str([x for x in dir(loader) if not x.startswith("_")]))
    w("M4 call set_models_dir")
    loader.set_models_dir(str(models_dir))
    w("M5 get_models_dir=" + str(loader.get_models_dir()))
    t0 = time.time()
    w("M6 call load_reference_csv umbrales")
    u = loader.load_reference_csv("umbrales")
    w("M7 umbrales shape=" + str(u.shape) + " elapsed=" + str(round(time.time()-t0,3)))
    t0 = time.time()
    w("M8 call load_reference_csv kpis")
    k = loader.load_reference_csv("kpis")
    w("M9 kpis shape=" + str(k.shape) + " elapsed=" + str(round(time.time()-t0,3)))
    t0 = time.time()
    w("M10 call load_reference_csv panel")
    p = loader.load_reference_csv("panel_entrenamiento")
    w("M11 panel shape=" + str(p.shape) + " elapsed=" + str(round(time.time()-t0,3)))
    t0 = time.time()
    w("M12 call load_models")
    m = loader.load_models()
    w("M13 load_models done keys=" + str(list(m.keys())) + " elapsed=" + str(round(time.time()-t0,3)))
    t0 = time.time()
    w("M14 now predict direct Narino 2007")
    import json, pandas as pd
    gold = json.load(open(r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\_golden.json", encoding="utf-8"))
    FEATS = ["spi3_floracion","spi3_desarrollo","spi3_cosecha","tmax_mean_e9","oni_mean","roya_dummy"]
    Xn = pd.DataFrame([gold["predictions"]["Narino_2007"]["features"]], columns=FEATS)
    pn = float(m["Narino"].predict(Xn)[0])
    w("M15 direct pred Narino 2007=" + str(round(pn,9)) + " elapsed=" + str(round(time.time()-t0,3)))
    t0 = time.time()
    w("M16 now predict via track_b_rendimiento.predict_rendimiento (la inferencia UNICA)")
    from cafe_sai_modelos_equipo9.track_b_rendimiento import predict_rendimiento
    out = predict_rendimiento("Narino", gold["predictions"]["Narino_2007"]["features"])
    w("M17 func pred status=" + str(out["status"]) + " val=" + str(round(out["prediccion_kg_ha"], 9)) + " elapsed=" + str(round(time.time()-t0,3)))
    diff = abs(out["prediccion_kg_ha"] - gold["predictions"]["Narino_2007"]["y_pred_kg_ha"])
    w("M18 diff vs golden=" + str(diff))
    if diff > 1e-6: raise AssertionError("NAR MISMATCH diff=" + str(diff))
    t0 = time.time()
    w("M19 Quindio 2015")
    out2 = predict_rendimiento("Quindio", gold["predictions"]["Quindio_2015"]["features"])
    diff2 = abs(out2["prediccion_kg_ha"] - gold["predictions"]["Quindio_2015"]["y_pred_kg_ha"])
    w("M20 Qui status=" + str(out2["status"]) + " val=" + str(round(out2["prediccion_kg_ha"], 9)) + " diff=" + str(diff2) + " elapsed=" + str(round(time.time()-t0, 3)))
    if diff2 > 1e-6: raise AssertionError("QUI MISMATCH diff2=" + str(diff2))
    t0 = time.time()
    w("M21 call kpis.get_kpis_actuariales")
    from cafe_sai_modelos_equipo9.kpis import get_kpis_actuariales
    kp = get_kpis_actuariales()
    w("M22 KPI Nar RMSE=" + str(kp["Narino"]["rmse_holdout_mejor"]) + " HE=" + str(kp["Narino"]["HE_Ederington"]) + " Prima=" + str(kp["Narino"]["prima_actuarial_pct"]) + " elapsed=" + str(round(time.time()-t0, 3)))
    assert kp["Narino"]["rmse_holdout_mejor"] == 15.1
    assert kp["Narino"]["HE_Ederington"] == 0.05
    assert abs(kp["Narino"]["prima_actuarial_pct"] - 6.36) < 1e-9
    assert kp["Narino"]["pago_cop_ha"] == 1200000
    assert kp["Quindio"]["rmse_holdout_mejor"] == 45.7
    assert kp["Quindio"]["HE_Ederington"] == 0.11
    assert abs(kp["Quindio"]["prima_actuarial_pct"] - 10.15) < 1e-9
    t0 = time.time()
    w("M23 SPI tests")
    from cafe_sai_modelos_equipo9.track_a_spi import predict_activacion_spi
    a1 = predict_activacion_spi("Narino", {"spi_min_e9": -2.0})
    a2 = predict_activacion_spi("Narino", {"roya_dummy":1,"roya_shock":1})
    a3 = predict_activacion_spi("Quindio", {"spi3_cosecha": -1.0})
    a4 = predict_activacion_spi("Quindio", {"spi3_cosecha": -2.3})
    w("M24 SPI NAR-2.0=" + str(a1["activo"]) + " NRoya=" + str(a2["activo"]) + " Q-1.0=" + str(a3["activo"]) + " Q-2.3=" + str(a4["activo"]) + " regla_a1=" + str(a1["regla_activada"]) + " elapsed=" + str(round(time.time()-t0,3)))
    assert a1["activo"] and a2["activo"] and not a3["activo"] and a4["activo"]
    t0 = time.time()
    w("M25 Panel tests")
    from cafe_sai_modelos_equipo9.panel import get_panel_entrenamiento, get_pred_vs_real_loyo, get_validacion_historica_n1
    pe = get_panel_entrenamiento()
    pr = get_pred_vs_real_loyo()
    vh = get_validacion_historica_n1()
    w("M26 shapes panel=" + str(pe.shape) + " loyo=" + str(pr.shape) + " valhist=" + str(vh.shape) + " elapsed=" + str(round(time.time()-t0,3)))
    assert pe.shape == (24, 48)
    t0 = time.time()
    w("M27 Raise validation tests")
    try:
        predict_rendimiento("Bogota", {f:0.1 for f in FEATS} | {"roya_dummy": 0})
        raise AssertionError("No raise Bogota")
    except ValueError as e:
        w("M27A OK Bogota raise: " + type(e).__name__)
    try:
        predict_rendimiento("Narino", {f:0.1 for f in FEATS if f != "spi3_floracion"} | {"roya_dummy": 0})
        raise AssertionError("No raise falta campo")
    except ValueError as e:
        w("M27B OK falta campo raise: " + type(e).__name__)
    try:
        bad = {f:0.1 for f in FEATS} | {"roya_dummy": 5}
        predict_rendimiento("Narino", bad)
        raise AssertionError("No raise roya 5")
    except ValueError as e:
        w("M27C OK roya_malo raise: " + type(e).__name__)
    bad_extra = {f:0.1 for f in FEATS} | {"roya_dummy": 0, "campo_extra": 1.23}
    outw = predict_rendimiento("Narino", bad_extra)
    w("M27D warnings count=" + str(len(outw["warnings"])) + " first_w=" + (str(outw["warnings"][0])[:60] if outw["warnings"] else "none"))
    assert len(outw["warnings"]) >= 1
    w("ALL M TESTS PASSED SECTION M0-M27D ELAPSED_TOTAL=" + str(round(time.time()-float(w is not None), 3)))
    w("ALL_PACKAGE_OK")
except Exception as e:
    w("!!! EXCEPTION: " + str(e) + "\n" + traceback.format_exc())
    sys.exit(1)
