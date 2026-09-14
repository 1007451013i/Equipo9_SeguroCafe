import sys, os, time, threading, traceback
sys.path.insert(0, r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\package_src")
MARK = r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\pp.txt"
stop = [False]
def heart():
    c = 0
    while not stop[0]:
        with open(MARK, "a", encoding="utf-8") as f:
            f.write(f"hb{c}\n")
            f.flush()
        c += 1
        time.sleep(0.25)
threading.Thread(target=heart, daemon=True).start()
def w(x):
    with open(MARK, "a", encoding="utf-8") as f:
        f.write(str(x) + "\n"); f.flush()
if os.path.exists(MARK): os.remove(MARK)
try:
    # 3: get_models_dir
    w("S3:start")
    from cafe_sai_modelos_equipo9.loader import get_models_dir, set_models_dir
    t0 = time.time()
    d = get_models_dir()
    w(f"S3:end elapsed={time.time()-t0:.3f} dir={d}")
    # 4: load_models
    w("S4:start")
    t0 = time.time()
    from cafe_sai_modelos_equipo9.loader import load_models
    m = load_models()
    w(f"S4:end elapsed={time.time()-t0:.3f} keys={list(m.keys())} NAR_md={m['Narino'].max_depth}")
    # 5: predict rendimiento (NAR 2007)
    import json
    gold = json.load(open(r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\_golden.json"))
    w("S5:start")
    t0 = time.time()
    from cafe_sai_modelos_equipo9.track_b_rendimiento import predict_rendimiento
    out = predict_rendimiento("Narino", gold["predictions"]["Narino_2007"]["features"])
    w(f"S5:end elapsed={time.time()-t0:.3f} status={out['status']} val={out['prediccion_kg_ha']:.6f}")
    # 6: get_kpis_actuariales
    w("S6:start")
    t0 = time.time()
    from cafe_sai_modelos_equipo9.kpis import get_kpis_actuariales
    kp = get_kpis_actuariales()
    w(f"S6:end elapsed={time.time()-t0:.3f} NarHE={kp['Narino']['HE_Ederington']} QuiHE={kp['Quindio']['HE_Ederington']}")
    # 7: SPI
    w("S7:start")
    t0 = time.time()
    from cafe_sai_modelos_equipo9.track_a_spi import predict_activacion_spi
    a = predict_activacion_spi("Narino", {"spi_min_e9": -2.0})
    w(f"S7:end elapsed={time.time()-t0:.3f} activo={a['activo']} pago={a['pago_cop_ha']}")
    # 8: Panel
    w("S8:start")
    t0 = time.time()
    from cafe_sai_modelos_equipo9.panel import get_panel_entrenamiento
    panel = get_panel_entrenamiento()
    w(f"S8:end elapsed={time.time()-t0:.3f} shape={panel.shape}")
    w("ALL SECTION S3-S8 OK")
    stop[0] = True
except Exception as e:
    w("!!! EXC: " + str(e) + "\n" + traceback.format_exc())
    stop[0] = True
    sys.exit(1)
time.sleep(0.5)
