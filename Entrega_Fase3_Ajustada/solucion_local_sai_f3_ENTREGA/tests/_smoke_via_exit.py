# Bypass el sandbox: escribo salida directamente y hago assertions con exit code.
# El script de serializacion ya corrio exit 0 y dio archivos correctos (por ls).
# Ahora voy a escribir un test de prediccion con joblib directamente (no usa el package)
# para validar que los .joblib funcionan, luego uso ese mismo resultado para seguir.
import sys, json, hashlib, os
sys.path.insert(0, r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\package_src")
ART = r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\models_artifacts"

import joblib, pandas as pd
from cafe_sai_modelos_equipo9.loader import load_models, load_reference_csv, get_models_dir
from cafe_sai_modelos_equipo9 import predict_rendimiento, FEATURES_FENOLOGICAS, predict_activacion_spi, get_kpis_actuariales, get_panel_entrenamiento

print("models_dir:", get_models_dir())
print("FEATURES:", FEATURES_FENOLOGICAS)
# Cargar modelos
m = load_models()
print("Loaded deptos:", sorted(m.keys()))

# Golden
gold = json.load(open(r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\_golden.json", encoding="utf-8"))
for key, case in gold["predictions"].items():
    out = predict_rendimiento(case["departamento"], case["features"])
    diff = abs(out["prediccion_kg_ha"] - case["y_pred_kg_ha"])
    print(f"[PREDICT] {key}: pkg={out['prediccion_kg_ha']:.9f} golden={case['y_pred_kg_ha']:.9f} diff={diff:.3e} status={out['status']}")
    if diff > 1e-6:
        print(f"[FATAL] MISMATCH {key}")
        sys.exit(11)

# Activacion SPI
a1 = predict_activacion_spi("Narino", {"spi_min_e9": -2.0})
print("[SPI] Narino SPI-2.0:", a1["activo"], a1["regla_activada"])
assert a1["activo"] is True
a2 = predict_activacion_spi("Narino", {"roya_dummy": 1, "roya_shock": 1})
print("[SPI] Narino ROYA:", a2["activo"], a2["regla_activada"])
assert a2["activo"] is True
a3 = predict_activacion_spi("Quindio", {"spi3_cosecha": -1.0})  # No supera P10=-2.2143
print("[SPI] Quindio cosecha=-1.0:", a3["activo"], a3["regla_activada"])
assert a3["activo"] is False

# KPIs
kp = get_kpis_actuariales()
for d in ("Narino", "Quindio"):
    k = kp[d]
    print(f"[KPIS] {d}: RMSE={k['rmse_holdout_mejor']} HE={k['HE_Ederington']} Prima={k['prima_actuarial_pct']}% RB={k['riesgo_base_pct']}% Act={k['pct_total_activacion']}% Pago={k['pago_cop_ha']}")
assert kp["Narino"]["rmse_holdout_mejor"] == 15.1
assert kp["Quindio"]["rmse_holdout_mejor"] == 45.7
assert kp["Narino"]["HE_Ederington"] == 0.05
assert kp["Quindio"]["prima_actuarial_pct"] == 10.15
assert kp["Narino"]["pago_cop_ha"] == 1_200_000

# Panel
panel = get_panel_entrenamiento()
print("[PANEL] shape:", panel.shape, "deptos:", sorted(panel["departamento"].unique()))
assert panel.shape == (24, 48)

# Excepciones
try:
    predict_rendimiento("Bogota", {k:0.0 for k in FEATURES_FENOLOGICAS} | {"roya_dummy":0})
except ValueError as e:
    print("[RAISE] OK depto_bad:", type(e).__name__, str(e)[:60])
else:
    print("[RAISE] FAIL no raise depto_bad"); sys.exit(12)

try:
    bad = {k:0.1 for k in FEATURES_FENOLOGICAS if k!="spi3_floracion"} | {"roya_dummy":0}
    predict_rendimiento("Narino", bad)
except ValueError as e:
    print("[RAISE] OK falta_campo:", type(e).__name__, str(e)[:60])
else:
    print("[RAISE] FAIL no raise falta"); sys.exit(13)

try:
    bad = {k:0.1 for k in FEATURES_FENOLOGICAS} | {"roya_dummy":5}
    predict_rendimiento("Narino", bad)
except ValueError as e:
    print("[RAISE] OK roya_malo:", type(e).__name__, str(e)[:60])
else:
    print("[RAISE] FAIL no raise roya"); sys.exit(14)

# Extras (campo no usado debe warning, no error)
ok_extra = {k:0.1 for k in FEATURES_FENOLOGICAS} | {"roya_dummy":0, "campo_que_no_va":"ignorado"}
out_e = predict_rendimiento("Narino", ok_extra)
print("[EXTRA] warnings:", out_e["warnings"])
assert len(out_e["warnings"]) >= 1

# Rangos extremos warnings
bad_range = {k:100.0 for k in FEATURES_FENOLOGICAS} | {"roya_dummy":0}
bad_range["tmax_mean_e9"] = 5.0
out_w = predict_rendimiento("Quindio", bad_range)
print("[RANGOS] warnings count:", len(out_w["warnings"]))
assert len(out_w["warnings"]) >= 4

print("\n[ALL OK] ===================================================")
print("All package smoke tests PASS")
sys.exit(0)
