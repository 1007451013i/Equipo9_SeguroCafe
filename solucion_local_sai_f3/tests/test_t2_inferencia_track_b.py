"""
T2. Tests de inferencia Track B + validaciones.
Coincidencia con golden predictions (3 casos), warnings rangos, validaciones de esquema.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import cafe_sai_modelos_equipo9 as pkg
from cafe_sai_modelos_equipo9 import FEATURES_FENOLOGICAS


GOLDEN = json.loads(
    (Path(__file__).resolve().parent / "_golden.json").read_text(encoding="utf-8")
)


def _mk_feats_from_golden(depto_row: dict) -> dict:
    return {k: depto_row["features"][k] for k in FEATURES_FENOLOGICAS}


def _golden_pred(depto_row: dict) -> float:
    return float(depto_row.get("prediccion_kg_ha") or depto_row["y_pred_kg_ha"])


def test_predict_narino_2007_golden():
    key = "Narino_2007"
    row = GOLDEN.get("predicciones_rendimiento", GOLDEN["predictions"])[key]
    out = pkg.predict_rendimiento("Narino", _mk_feats_from_golden(row))
    assert out["status"] == "success"
    assert out["departamento"] == "Narino"
    assert abs(out["prediccion_kg_ha"] - _golden_pred(row)) < 1e-6
    assert out["modelo"] == "ExtraTreesRegressor"
    assert out["n_features"] == 6


def test_predict_quindio_2015_golden():
    key = "Quindio_2015"
    row = GOLDEN.get("predicciones_rendimiento", GOLDEN["predictions"])[key]
    out = pkg.predict_rendimiento("Quindio", _mk_feats_from_golden(row))
    assert out["status"] == "success"
    assert out["departamento"] == "Quindio"
    assert abs(out["prediccion_kg_ha"] - _golden_pred(row)) < 1e-6
    assert out["modelo"] == "RandomForestRegressor"


def test_predict_narino_2012_golden():
    key = "Narino_2012"
    row = GOLDEN.get("predicciones_rendimiento", GOLDEN["predictions"])[key]
    out = pkg.predict_rendimiento("Narino", _mk_feats_from_golden(row))
    assert abs(out["prediccion_kg_ha"] - _golden_pred(row)) < 1e-6


def test_predict_rendimiento_raises_departamento_desconocido():
    with pytest.raises(ValueError):
        pkg.predict_rendimiento("Bogota", {k: 0.0 for k in FEATURES_FENOLOGICAS})


def test_predict_rendimiento_raises_falta_campo():
    f = {k: 0.0 for k in FEATURES_FENOLOGICAS}
    del f["spi3_floracion"]
    with pytest.raises(ValueError):
        pkg.predict_rendimiento("Narino", f)


def test_predict_rendimiento_raises_roya_fuera_rango():
    f = {k: 0.0 for k in FEATURES_FENOLOGICAS}
    f["roya_dummy"] = 5
    with pytest.raises(ValueError):
        pkg.predict_rendimiento("Narino", f)


def test_predict_rendimiento_warnings_rangos_fuera_soft():
    f = {k: 0.0 for k in FEATURES_FENOLOGICAS}
    f["spi3_floracion"] = -7.0  # warning level: por fuera rango [-5, 5]
    f["tmax_mean_e9"] = 45.0   # por fuera [10, 40]
    out = pkg.predict_rendimiento("Narino", f)
    warnings_text = " | ".join(out["warnings"]).lower()
    assert out["status"] == "success"
    # Al menos 2 warnings de rango.
    count_range = 0
    for w in out["warnings"]:
        if ("spi" in w.lower() or "tmax" in w.lower()) and ("rango" in w.lower() or "fuera" in w.lower()):
            count_range += 1
    assert count_range >= 2, f"No detectó 2+ warnings de rango soft: {out['warnings']}"


def test_predict_rendimiento_warning_campos_extra():
    f = {k: 0.0 for k in FEATURES_FENOLOGICAS}
    f["campo_inventado_xyz"] = 12345
    out = pkg.predict_rendimiento("Narino", f)
    assert out["status"] == "success"
    hay_extra = any("extra" in w.lower() or "adicional" in w.lower() or "ignor" in w.lower() for w in out["warnings"])
    assert hay_extra, f"Debe advertir campos extra: {out['warnings']}"
