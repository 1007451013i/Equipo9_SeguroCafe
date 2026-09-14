import sys, os, json, time, threading, traceback
sys.path.insert(0, r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\package_src")
MARK = r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\p.txt"
stop = [False]
def heart():
    c = 0
    while not stop[0]:
        with open(MARK, "a", encoding="utf-8") as f:
            f.write("heartbeat " + str(c) + " " + time.strftime("%H:%M:%S") + "\n")
            f.flush()
        c += 1
        time.sleep(0.5)
threading.Thread(target=heart, daemon=True).start()
def w(x):
    with open(MARK, "a", encoding="utf-8") as f:
        f.write(str(x) + "\n"); f.flush()
if os.path.exists(MARK): os.remove(MARK)
w("0")
try:
    w("1: import package")
    import cafe_sai_modelos_equipo9 as m
    w("2: version=" + str(m.__version__))
    w("3: loader.get_models_dir=" + str(m.loader.get_models_dir()))
    w("4: calling load_models")
    models = m.load_models()
    w("5: models loaded keys=" + str(list(models.keys())))
    w("6: narino max_depth=" + str(models["Narino"].max_depth))
    w("7: calling predict_rendimiento nar 2007")
    gold = json.load(open(r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\_golden.json"))
    out = m.predict_rendimiento("Narino", gold["predictions"]["Narino_2007"]["features"])
    w("8: predict result status=" + out["status"] + " val=" + str(round(out["prediccion_kg_ha"], 6)))
    w("9: calling get_kpis_actuariales")
    kp = m.get_kpis_actuariales()
    w("10: KPIs Narino HE=" + str(kp["Narino"]["HE_Ederington"]))
    w("11: calling predict_activacion_spi")
    a = m.predict_activacion_spi("Narino", {"spi_min_e9":-2.0})
    w("12: SPI activo=" + str(a["activo"]))
    w("13: get_panel_entrenamiento shape=" + str(m.get_panel_entrenamiento().shape))
    w("ALL DONE OK")
    stop[0] = True
except Exception as e:
    w("!!! ERROR: " + str(e) + "\n" + traceback.format_exc())
    stop[0] = True
    sys.exit(1)
time.sleep(1)
