import sys, os, traceback
sys.path.insert(0, r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\package_src")
MARK=r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\a1.txt"
def w(x):
    with open(MARK, "a", encoding="utf-8") as f: f.write(str(x)+"\n"); f.flush()
try:
    if os.path.exists(MARK): os.remove(MARK)
    # 1. loader.py get_models_dir
    from cafe_sai_modelos_equipo9.loader import get_models_dir
    w("A1 get_models_dir = " + str(get_models_dir()))
    # 2. load_reference_csv panel_entrenamiento
    from cafe_sai_modelos_equipo9.loader import load_reference_csv
    df = load_reference_csv("panel_entrenamiento")
    w("A2 panel shape = " + str(df.shape))
    # 3. load_reference_csv umbrales
    umb = load_reference_csv("umbrales")
    w("A3 umbrales cols=" + str(list(umb.columns)) + " rows=" + str(len(umb)))
    # 4. load_reference_csv kpis
    kpis = load_reference_csv("kpis")
    w("A4 kpis head: " + kpis.to_csv(index=False).strip().split("\n")[:3] if len(kpis)>=3 else str(kpis))
    # 5. load_models
    from cafe_sai_modelos_equipo9.loader import load_models
    m = load_models()
    w("A5 models keys=" + str(sorted(m.keys())))
    w("A5 NAR class=" + type(m["Narino"]).__name__)
    w("A5 QUI class=" + type(m["Quindio"]).__name__)
    w("A5 NAR params md=" + str(m["Narino"].max_depth) + " ne=" + str(m["Narino"].n_estimators) + " mf=" + str(m["Narino"].max_features) + " msl=" + str(m["Narino"].min_samples_leaf) + " rs=" + str(m["Narino"].random_state))
    w("A5 QUI params md=" + str(m["Quindio"].max_depth) + " ne=" + str(m["Quindio"].n_estimators) + " mf=" + str(m["Quindio"].max_features) + " msl=" + str(m["Quindio"].min_samples_leaf) + " rs=" + str(m["Quindio"].random_state))
    # Verificar params exactos Entrega_2 CELL 121
    assert m["Narino"].n_estimators == 400
    assert m["Narino"].max_depth == 3
    assert abs(m["Narino"].max_features - 0.6) < 1e-9
    assert m["Narino"].min_samples_leaf == 2
    assert m["Narino"].random_state == 42
    assert m["Quindio"].n_estimators == 400
    assert m["Quindio"].max_depth == 2
    assert m["Quindio"].max_features == 1.0
    assert m["Quindio"].min_samples_leaf == 1
    assert m["Quindio"].random_state == 42
    w("A5B PARAMS MATCH EXACTOS A ENTREGA_2 CELL 121 OK")
    # 6. predict direct modelo
    from cafe_sai_modelos_equipo9.schemas import FEATURES_FENOLOGICAS
    import pandas as pd
    sample_nar = pd.DataFrame([{
        "spi3_floracion":-0.1963123140622514,
        "spi3_desarrollo":-0.3609924665595361,
        "spi3_cosecha":-0.107018845903456,
        "tmax_mean_e9":20.0,
        "oni_mean":-0.6075,
        "roya_dummy":0
    }], columns=FEATURES_FENOLOGICAS)
    p_nar = float(m["Narino"].predict(sample_nar)[0])
    w("A6 pred NAR=" + str(round(p_nar, 9)))
    sample_qui = pd.DataFrame([{
        "spi3_floracion":-0.4066499465970844,
        "spi3_desarrollo":-1.3543612672994316,
        "spi3_cosecha":-0.9206907545417508,
        "tmax_mean_e9":30.89,
        "oni_mean":1.5483333333333331,
        "roya_dummy":0
    }], columns=FEATURES_FENOLOGICAS)
    p_qui = float(m["Quindio"].predict(sample_qui)[0])
    w("A6 pred QUI=" + str(round(p_qui, 9)))
    # 7. predict via funcion predict_rendimiento (lógica inferencia única)
    from cafe_sai_modelos_equipo9 import predict_rendimiento
    out = predict_rendimiento("Narino", {
        "spi3_floracion":-0.1963123140622514,
        "spi3_desarrollo":-0.3609924665595361,
        "spi3_cosecha":-0.107018845903456,
        "tmax_mean_e9":20.0,
        "oni_mean":-0.6075,
        "roya_dummy":0
    })
    diff_nar = abs(out["prediccion_kg_ha"] - p_nar)
    w("A7 predict func NAR status=" + out["status"] + " val=" + str(round(out["prediccion_kg_ha"], 9)) + " diff_direct=" + str(diff_nar))
    assert diff_nar < 1e-9
    # 8. kpis actuariales
    from cafe_sai_modelos_equipo9 import get_kpis_actuariales
    kp = get_kpis_actuariales()
    w("A8 NAR rmse=" + str(kp['Narino']['rmse_holdout_mejor']) + " HE=" + str(kp['Narino']['HE_Ederington']) + " prima=" + str(kp['Narino']['prima_actuarial_pct']) + " pago=" + str(kp['Narino']['pago_cop_ha']))
    w("A8 QUI rmse=" + str(kp['Quindio']['rmse_holdout_mejor']) + " HE=" + str(kp['Quindio']['HE_Ederington']) + " prima=" + str(kp['Quindio']['prima_actuarial_pct']) + " pago=" + str(kp['Quindio']['pago_cop_ha']))
    assert kp["Narino"]["rmse_holdout_mejor"] == 15.1
    assert kp["Narino"]["HE_Ederington"] == 0.05
    assert abs(kp["Narino"]["prima_actuarial_pct"] - 6.36) < 1e-9
    assert kp["Narino"]["pago_cop_ha"] == 1_200_000
    assert kp["Quindio"]["rmse_holdout_mejor"] == 45.7
    assert kp["Quindio"]["HE_Ederington"] == 0.11
    assert abs(kp["Quindio"]["prima_actuarial_pct"] - 10.15) < 1e-9
    w("A8B KPIS MATCH CSV OFICIAL OK")
    # 9. SPI activacion
    from cafe_sai_modelos_equipo9 import predict_activacion_spi
    a1 = predict_activacion_spi("Narino", {"spi_min_e9": -2.0})
    w("A9 SPI NAR -2.0 activo=" + str(a1["activo"]) + " regla=" + str(a1["regla_activada"]) + " pago=" + str(a1["pago_cop_ha"]))
    assert a1["activo"] is True
    assert a1["pago_cop_ha"] == 1_200_000
    a2 = predict_activacion_spi("Narino", {"roya_dummy": 1, "roya_shock": 1})
    w("A9 SPI NAR ROYA activo=" + str(a2["activo"]))
    assert a2["activo"] is True
    a3 = predict_activacion_spi("Quindio", {"spi3_cosecha": -1.0})
    w("A9 SPI QUI -1.0 activo=" + str(a3["activo"]))
    assert a3["activo"] is False
    a4 = predict_activacion_spi("Quindio", {"spi3_cosecha": -2.3})
    w("A9 SPI QUI -2.3 activo=" + str(a4["activo"]) + " umbP10=" + str(a4["umbral_sequia_p10"]))
    assert a4["activo"] is True
    # 10. panel entrenamiento shape
    from cafe_sai_modelos_equipo9 import get_panel_entrenamiento
    p = get_panel_entrenamiento()
    w("A10 panel shape=" + str(p.shape) + " deptos=" + str(sorted(p["departamento"].unique().tolist())))
    assert p.shape == (24, 48)
    # 11. Raise tests
    try:
        predict_rendimiento("Bogota", {"spi3_floracion":0.0})
        w("A11 FAIL no raise Bogota")
        sys.exit(21)
    except ValueError as e: w("A11 OK raise Bogota: " + type(e).__name__)
    try:
        predict_rendimiento("Narino", {"spi3_desarrollo":0.0,"spi3_cosecha":0.0,"tmax_mean_e9":25.0,"oni_mean":0.0,"roya_dummy":0})
        w("A11 FAIL no raise falt spi3_floracion"); sys.exit(22)
    except ValueError as e: w("A11 OK raise falta campo: " + type(e).__name__)
    try:
        predict_rendimiento("Narino", {"spi3_floracion":0.0,"spi3_desarrollo":0.0,"spi3_cosecha":0.0,"tmax_mean_e9":25.0,"oni_mean":0.0,"roya_dummy":5})
        w("A11 FAIL no raise roya 5"); sys.exit(23)
    except ValueError as e: w("A11 OK raise roya 5: " + type(e).__name__)
    # 12. warnings de campos extra y rangos
    ok_extra = {"spi3_floracion":0.0,"spi3_desarrollo":0.0,"spi3_cosecha":0.0,"tmax_mean_e9":25.0,"oni_mean":0.0,"roya_dummy":0, "campo_extra_no_usar":1.0}
    outw = predict_rendimiento("Narino", ok_extra)
    w("A12 warnings count=" + str(len(outw["warnings"])) + " : " + str(outw["warnings"]))
    assert len(outw["warnings"]) >= 1
    w("ALL TESTS IN PACKAGE PASSED A1-A12")
except Exception as e:
    w("!!! EXCEPTION: " + str(e) + "\n" + traceback.format_exc())
    sys.exit(1)
