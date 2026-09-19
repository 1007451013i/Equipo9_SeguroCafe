"""
T4. Tests FastAPI + httpx ASGI TestClient (IN-PROCESS, no levanta servidor).
- health, models, kpis, umbrales, predict POST, activacion POST, series.
- 422 en inputs inválidos.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
# Importamos con sys.path el módulo `api`
sys.path.insert(0, str(ROOT))

from api.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "endpoints" in data
    assert "version_api" in data


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "ok"
    assert set(d["models_available"]) == {"Narino", "Quindio"}
    assert "package_version" in d


def test_models_meta():
    r = client.get("/api/v1/models")
    assert r.status_code == 200
    d = r.json()
    assert d["features_fenologicas_orden"] == [
        "spi3_floracion",
        "spi3_desarrollo",
        "spi3_cosecha",
        "tmax_mean_e9",
        "oni_mean",
        "roya_dummy",
    ]
    assert d["pago_evento_cop_ha"] >= 1_000_000


def test_post_predict_rendimiento_narino_ok():
    body = {
        "departamento": "Narino",
        "spi3_floracion": -0.3,
        "spi3_desarrollo": -0.4,
        "spi3_cosecha": -0.2,
        "tmax_mean_e9": 22.0,
        "oni_mean": 0.0,
        "roya_dummy": 0,
    }
    r = client.post("/api/v1/predict/rendimiento", json=body)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["status"] == "success"
    assert 800 <= float(d["prediccion_kg_ha"]) <= 1400
    assert d["n_features"] == 6
    assert d["departamento"] == "Narino"


def test_post_predict_rendimiento_422_roya_invalido():
    body = {
        "departamento": "Narino",
        "spi3_floracion": 0.0,
        "spi3_desarrollo": 0.0,
        "spi3_cosecha": 0.0,
        "tmax_mean_e9": 22.0,
        "oni_mean": 0.0,
        "roya_dummy": 9,
    }
    r = client.post("/api/v1/predict/rendimiento", json=body)
    # Pydantic retornará 422
    assert r.status_code == 422, r.text


def test_post_predict_rendimiento_path_400_depto_malo():
    r = client.post("/api/v1/predict/rendimiento/Bogota", params={
        "spi3_floracion": 0.0,
        "spi3_desarrollo": 0.0,
        "spi3_cosecha": 0.0,
        "tmax_mean_e9": 22.0,
        "oni_mean": 0.0,
        "roya_dummy": 0,
    })
    assert r.status_code == 400


def test_get_kpis_endpoint():
    r = client.get("/api/v1/kpis")
    assert r.status_code == 200
    d = r.json()
    assert "actuariales_por_depto" in d
    assert "Narino" in d["actuariales_por_depto"]
    assert d["actuariales_por_depto"]["Narino"]["pago_cop_ha"] == 1_200_000


def test_get_umbrales_track_a():
    r = client.get("/api/v1/track-a/umbrales")
    assert r.status_code == 200
    d = r.json()
    assert "umbrales_por_departamento" in d
    nar = d["umbrales_por_departamento"].get("Narino", {})
    assert "sequia_p10" in nar


def test_post_activacion_narino_activa():
    r = client.post(
        "/api/v1/track-a/activacion/Narino",
        json={"spi_min_e9": -2.5, "roya_shock": 1},
    )
    assert r.status_code == 200
    d = r.json()
    assert d["activo"] is True
    assert d["pago_cop_ha"] == 1_200_000


def test_series_panel_historico():
    r = client.get("/api/v1/series/historico")
    assert r.status_code == 200
    d = r.json()
    assert d["shape"] == [24, 48]


def test_series_validacion_historica():
    r = client.get("/api/v1/validacion-historica")
    assert r.status_code == 200
    d = r.json()
    assert d["shape"][0] == 4


def test_cors_preflight_localhost_8501():
    r = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:8501",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.status_code == 200
    assert "8501" in r.headers.get("access-control-allow-origin", "")
