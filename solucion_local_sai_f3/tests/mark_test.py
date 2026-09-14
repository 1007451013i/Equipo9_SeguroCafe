# Escribo una marca a un archivo para confirmar que el script de Python se ejecuta realmente
import os, sys
MARK = r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\mark_executed.txt"
with open(MARK, "w", encoding="utf-8") as f:
    f.write("EXECUTED " + sys.version + "\n")
    f.write("CWD: " + os.getcwd() + "\n")
# importar y probar
sys.path.insert(0, r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\package_src")
try:
    import cafe_sai_modelos_equipo9 as m
    with open(MARK, "a", encoding="utf-8") as f:
        f.write("IMPORT OK version=" + str(m.__version__) + "\n")
        f.write("FEATURES=" + str(m.FEATURES_FENOLOGICAS) + "\n")
    # Predict
    import json
    gold = json.load(open(r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\_golden.json", encoding="utf-8"))
    for k, case in gold["predictions"].items():
        out = m.predict_rendimiento(case["departamento"], case["features"])
        diff = abs(out["prediccion_kg_ha"] - case["y_pred_kg_ha"])
        with open(MARK, "a", encoding="utf-8") as f:
            f.write(f"PRED {k}: pkg={out['prediccion_kg_ha']:.9f} golden={case['y_pred_kg_ha']:.9f} diff={diff:.3e} status={out['status']}\n")
        if diff > 1e-6:
            raise AssertionError(f"MISMATCH {k}")
    kp = m.get_kpis_actuariales()
    with open(MARK, "a", encoding="utf-8") as f:
        f.write(f"KPIs Narino RMSE={kp['Narino']['rmse_holdout_mejor']} HE={kp['Narino']['HE_Ederington']} Prima={kp['Narino']['prima_actuarial_pct']}\n")
        f.write(f"KPIs Quindio RMSE={kp['Quindio']['rmse_holdout_mejor']} HE={kp['Quindio']['HE_Ederington']} Prima={kp['Quindio']['prima_actuarial_pct']}\n")
    # SPI
    a1 = m.predict_activacion_spi("Narino", {"spi_min_e9": -2.0})
    a2 = m.predict_activacion_spi("Narino", {"roya_dummy": 1, "roya_shock": 1})
    a3 = m.predict_activacion_spi("Quindio", {"spi3_cosecha": -1.0})
    with open(MARK, "a", encoding="utf-8") as f:
        f.write(f"SPI Narino-2.0: activo={a1['activo']} regla={a1['regla_activada']}\n")
        f.write(f"SPI Narino ROYA: activo={a2['activo']}\n")
        f.write(f"SPI Quindio -1.0: activo={a3['activo']}\n")
    if not a1["activo"] or not a2["activo"] or a3["activo"]:
        raise AssertionError("SPI FAIL")
    # Raise tests
    try:
        m.predict_rendimiento("Bogota", {k:0.1 for k in m.FEATURES_FENOLOGICAS} | {"roya_dummy":0})
    except ValueError:
        with open(MARK, "a", encoding="utf-8") as f:
            f.write("RAISE OK depto_bad\n")
    try:
        m.predict_rendimiento("Narino", {k:0.1 for k in m.FEATURES_FENOLOGICAS if k!="spi3_floracion"} | {"roya_dummy":0})
    except ValueError:
        with open(MARK, "a", encoding="utf-8") as f:
            f.write("RAISE OK falta_spi3_floracion\n")
    try:
        bad = {k:0.1 for k in m.FEATURES_FENOLOGICAS} | {"roya_dummy": 5}
        m.predict_rendimiento("Narino", bad)
    except ValueError:
        with open(MARK, "a", encoding="utf-8") as f:
            f.write("RAISE OK roya_malo\n")
    # Panel
    with open(MARK, "a", encoding="utf-8") as f:
        f.write(f"PANEL shape={m.get_panel_entrenamiento().shape}\n")
        f.write("ALL TESTS PASSED\n")
except Exception as e:
    import traceback
    with open(MARK, "a", encoding="utf-8") as f:
        f.write("ERROR: " + str(e) + "\n" + traceback.format_exc())
    raise
