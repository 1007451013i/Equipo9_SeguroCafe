import sys, os, json, time, traceback
sys.path.insert(0, r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\package_src")
MARK = r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\mark2.txt"
def w(x):
    with open(MARK, "a", encoding="utf-8") as f:
        f.write(str(x) + "\n")
        f.flush()
try:
    if os.path.exists(MARK): os.remove(MARK)
    w("1 START")
    import cafe_sai_modelos_equipo9 as m
    w("2 IMPORTED version=" + str(m.__version__))
    gold = json.load(open(r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\_golden.json", encoding="utf-8"))
    w("3 GOLDEN LOADED keys=" + str(list(gold["predictions"].keys())))
    case = gold["predictions"]["Narino_2007"]
    w("4 CASE LOADED depto=" + str(case['departamento']) + " year=" + str(case['year']))
    out = m.predict_rendimiento(case["departamento"], case["features"])
    w("5 PREDICT DONE status=" + out["status"] + " val=" + str(round(out["prediccion_kg_ha"], 6)))
    w("6 GOLDEN val=" + str(case["y_pred_kg_ha"]))
    diff = abs(out["prediccion_kg_ha"] - case["y_pred_kg_ha"])
    w("7 DIFF=" + str(diff))
    if diff > 1e-6: raise Exception(f"MISMATCH diff={diff}")
    kp = m.get_kpis_actuariales()
    w("8 KPIS NAR rmse=" + str(kp['Narino']['rmse_holdout_mejor']) + " he=" + str(kp['Narino']['HE_Ederington']))
    if kp['Narino']['rmse_holdout_mejor'] != 15.1: raise Exception("KPIS NAR RMSE FAIL")
    a1 = m.predict_activacion_spi("Narino", {"spi_min_e9": -2.0})
    w("9 SPI a1 activo=" + str(a1["activo"]) + " regla=" + str(a1["regla_activada"]))
    if not a1["activo"]: raise Exception("SPI FAIL a1")
    panel = m.get_panel_entrenamiento()
    w("10 PANEL shape=" + str(panel.shape))
    if panel.shape != (24, 48): raise Exception("PANEL SHAPE FAIL")
    w("11 END ALL TESTS PASSED")
except Exception as e:
    w("!!! ERROR: " + str(e) + "\n" + traceback.format_exc())
    sys.exit(1)
