import sys, os
sys.path.insert(0, r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\package_src")
MARK=r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\debug3.txt"
def w(x):
    with open(MARK, "a", encoding="utf-8") as f:
        f.write(x+"\n"); f.flush()
try:
    if os.path.exists(MARK): os.remove(MARK)
    w("1")
    import cafe_sai_modelos_equipo9.track_b_rendimiento as t
    w("2 imported track_b")
    m = t.predict_rendimiento
    w("3 got func")
    sample_features = {
      "spi3_floracion": -0.1963123140622514,
      "spi3_desarrollo": -0.3609924665595361,
      "spi3_cosecha": -0.107018845903456,
      "tmax_mean_e9": 20.0,
      "oni_mean": -0.6075,
      "roya_dummy": 0
    }
    w("4 feats built")
    cleaned, warns = t._coerce_and_validate_features(sample_features)
    w("5 coerced: " + str(cleaned))
    from cafe_sai_modelos_equipo9.loader import load_models
    w("6 loader imported")
    models = load_models()
    w("7 models loaded: " + str(sorted(models.keys())))
    model = models["Narino"]
    import pandas as pd
    from cafe_sai_modelos_equipo9.schemas import FEATURES_FENOLOGICAS
    X = pd.DataFrame([sample_features], columns=FEATURES_FENOLOGICAS)
    w("8 X built shape=" + str(X.shape))
    pred = model.predict(X)
    w("9 predict direct=" + str(round(float(pred[0]), 6)))
    out = m("Narino", sample_features)
    w("10 predict via func status=" + out["status"] + " val=" + str(round(out["prediccion_kg_ha"], 6)))
    w("ALL DONE")
except Exception as e:
    import traceback
    w("ERROR " + str(e) + "\n" + traceback.format_exc())
    sys.exit(1)
