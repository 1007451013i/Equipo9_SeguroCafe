import sys, os, traceback, threading, time
sys.path.insert(0, r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\package_src")
MARK=r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\watch.txt"
if os.path.exists(MARK): os.remove(MARK)
def watcher():
    for i in range(60):
        if os.path.exists(MARK):
            with open(MARK, "r", encoding="utf-8") as f:
                data = f.read()
            if "DONE" in data or "ERROR" in data:
                print(data)
                os._exit(0 if "DONE" in data else 99)
        time.sleep(0.5)
    print("TIMEOUT")
    os._exit(98)
threading.Thread(target=watcher, daemon=True).start()
def w(x):
    with open(MARK, "a", encoding="utf-8") as f:
        f.write(str(x)+"\n")
try:
    w("0 start")
    import cafe_sai_modelos_equipo9.loader as loader
    w("1 import loader")
    print("models dir: ", loader.get_models_dir())
    w("2 models dir=" + str(loader.get_models_dir()))
    m = loader.load_models()
    w("3 models loaded: " + str(list(m.keys())))
    for d, model in m.items():
        import joblib, pandas as pd
        from cafe_sai_modelos_equipo9.schemas import FEATURES_FENOLOGICAS
        sample = pd.DataFrame([{f:0.1 for f in FEATURES_FENOLOGICAS}], columns=FEATURES_FENOLOGICAS)
        sample["roya_dummy"] = 0
        pred = model.predict(sample)[0]
        w(f"4 pred {d}: {pred:.4f}")
    from cafe_sai_modelos_equipo9 import predict_rendimiento
    w("5 import predict_rendimiento OK")
    sample_features = {
      "spi3_floracion": -0.1963123140622514,
      "spi3_desarrollo": -0.3609924665595361,
      "spi3_cosecha": -0.107018845903456,
      "tmax_mean_e9": 20.0,
      "oni_mean": -0.6075,
      "roya_dummy": 0
    }
    out = predict_rendimiento("Narino", sample_features)
    w("6 predict Narino status=" + out["status"] + " val=" + str(round(out["prediccion_kg_ha"], 6)))
    from cafe_sai_modelos_equipo9 import get_kpis_actuariales
    kp = get_kpis_actuariales()
    w("7 KPIs: Nar RMSE=" + str(kp['Narino']['rmse_holdout_mejor']) + " HE=" + str(kp['Narino']['HE_Ederington']))
    from cafe_sai_modelos_equipo9 import predict_activacion_spi
    a1 = predict_activacion_spi("Narino", {"spi_min_e9":-2.0})
    w("8 SPI Narino-2.0 activo=" + str(a1["activo"]) + " regla=" + str(a1["regla_activada"]))
    from cafe_sai_modelos_equipo9 import get_panel_entrenamiento
    panel = get_panel_entrenamiento()
    w("9 PANEL shape=" + str(panel.shape))
    w("DONE OK")
except Exception as e:
    w("ERROR " + str(e) + "\n" + traceback.format_exc())
    time.sleep(2)
    sys.exit(1)
