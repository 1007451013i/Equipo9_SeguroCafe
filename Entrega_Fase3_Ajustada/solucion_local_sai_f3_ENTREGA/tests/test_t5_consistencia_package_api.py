"""
T5. Prueba de consistencia 3-vías: PACKAGE ≡ API ≡ (GOLDEN).
- Misma entrada.
- Comparar predicciones numéricas estrictamente 1e-6.
- Comparar activación Track A estrictamente booleana y regla.
- Comparar KPIs.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import json  # noqa: E402

from api.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import cafe_sai_modelos_equipo9 as pkg  # noqa: E402


client = TestClient(app)

GOLDEN = json.loads(
    (Path(__file__).resolve().parent / "_golden.json").read_text(encoding="utf-8")
)
FEATS = pkg.FEATURES_FENOLOGICAS


def _golden_depto(key: str) -> dict:
    return GOLDEN.get("predicciones_rendimiento", GOLDEN["predictions"])[key]


def _golden_pred_val(row: dict) -> float:
    return float(row.get("prediccion_kg_ha") or row["y_pred_kg_ha"])


@pytest.mark.parametrize(
    "depto,key",
    [
        ("Narino", "Narino_2007"),
        ("Quindio", "Quindio_2015"),
        ("Narino", "Narino_2012"),
    ],
)
def test_consistencia_package_api_golden_rendimiento(depto, key):
    row = _golden_depto(key)
    feats = {k: row["features"][k] for k in FEATS}
    golden = _golden_pred_val(row)

    # PACKAGE
    out_pkg = pkg.predict_rendimiento(depto, feats)
    assert out_pkg["status"] == "success"

    # API
    r = client.post("/api/v1/predict/rendimiento", json={"departamento": depto, **feats})
    assert r.status_code == 200
    out_api = r.json()
    assert out_api["status"] == "success"

    pred_pkg = float(out_pkg["prediccion_kg_ha"])
    pred_api = float(out_api["prediccion_kg_ha"])

    assert abs(pred_pkg - golden) < 1e-6, f"pkg != golden: {pred_pkg:.10f} vs {golden:.10f}"
    assert abs(pred_api - golden) < 1e-6, f"api != golden: {pred_api:.10f} vs {golden:.10f}"
    assert abs(pred_api - pred_pkg) < 1e-9, f"pkg != api: {pred_pkg:.12f} vs {pred_api:.12f}"


def test_consistencia_activacion_spi_package_api():
    body = {
        "spi_min_e9": -2.0,
        "spi_min_annual": -1.5,
        "spi3_cosecha": -0.5,
        "n_sequia_e9": 0,
        "roya_shock": 1,
    }
    for depto in ["Narino", "Quindio"]:
        out_pkg = pkg.predict_activacion_spi(depto, body)
        r = client.post(f"/api/v1/track-a/activacion/{depto}", json=body)
        assert r.status_code == 200
        out_api = r.json()
        assert out_pkg["activo"] == out_api["activo"], (depto, out_pkg, out_api)
        assert out_pkg["pago_cop_ha"] == out_api["pago_cop_ha"]
        assert out_pkg["departamento"] == out_api["departamento"]


def test_consistencia_kpis_package_api():
    pkg_k = pkg.get_kpis_actuariales()
    r = client.get("/api/v1/kpis")
    assert r.status_code == 200
    api_k = r.json()["actuariales_por_depto"]
    for depto in ["Narino", "Quindio"]:
        for key in ["rmse_holdout_mejor", "HE_Ederington", "prima_actuarial_pct", "riesgo_base_pct", "pago_cop_ha"]:
            pv = pkg_k[depto].get(key)
            av = api_k[depto].get(key)
            if isinstance(pv, (int, float)) and isinstance(av, (int, float)):
                assert abs(pv - av) < 1e-6, (depto, key, pv, av)
            else:
                assert pv == av, (depto, key, pv, av)
