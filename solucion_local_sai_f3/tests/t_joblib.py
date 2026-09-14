import sys, os, json, joblib, pandas as pd
ART = r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\models_artifacts"
MARK = r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\t_joblib.txt"
def w(x):
    with open(MARK, "a", encoding="utf-8") as f: f.write(x+"\n"); f.flush()
try:
    if os.path.exists(MARK): os.remove(MARK)
    w("T1 start")
    mn = joblib.load(os.path.join(ART, "narino_extratrees_entrega2.joblib"))
    mq = joblib.load(os.path.join(ART, "quindio_randomforest_entrega2.joblib"))
    w("T1 loaded classes: Nar=" + type(mn).__name__ + " Qui=" + type(mq).__name__)
    w("T1 Nar params: md=" + str(mn.max_depth) + " ne=" + str(mn.n_estimators) + " mf=" + str(mn.max_features) + " msl=" + str(mn.min_samples_leaf) + " rs=" + str(mn.random_state))
    w("T1 Qui params: md=" + str(mq.max_depth) + " ne=" + str(mq.n_estimators) + " mf=" + str(mq.max_features) + " msl=" + str(mq.min_samples_leaf) + " rs=" + str(mq.random_state))
    gold = json.load(open(os.path.join(ART, "..", "tests", "_golden.json"), encoding="utf-8"))
    FEATS = ["spi3_floracion","spi3_desarrollo","spi3_cosecha","tmax_mean_e9","oni_mean","roya_dummy"]
    Xn = pd.DataFrame([gold["predictions"]["Narino_2007"]["features"]], columns=FEATS)
    Xq = pd.DataFrame([gold["predictions"]["Quindio_2015"]["features"]], columns=FEATS)
    pn = float(mn.predict(Xn)[0])
    pq = float(mq.predict(Xq)[0])
    w("T1 pred Nar 2007=" + str(round(pn,9)) + " expected=" + str(gold["predictions"]["Narino_2007"]["y_pred_kg_ha"]))
    w("T1 pred Qui 2015=" + str(round(pq,9)) + " expected=" + str(gold["predictions"]["Quindio_2015"]["y_pred_kg_ha"]))
    diff_n = abs(pn - gold["predictions"]["Narino_2007"]["y_pred_kg_ha"])
    diff_q = abs(pq - gold["predictions"]["Quindio_2015"]["y_pred_kg_ha"])
    w("T1 diffs Nar=" + str(diff_n) + " Qui=" + str(diff_q))
    if diff_n > 1e-6 or diff_q > 1e-6: raise AssertionError("diff fail")
    w("T1 ALL OK joblib predict match golden")
except Exception as e:
    import traceback
    w("!!! T1 ERROR " + str(e) + "\n" + traceback.format_exc())
    sys.exit(1)
