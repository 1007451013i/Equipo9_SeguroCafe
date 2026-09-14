"""
T1. Tests de carga de artefactos oficiales.
- 2 modelos joblib existen.
- metadata json tiene hiperparámetros oficiales.
- 5 CSVs referencia existen.
- Loader retorna 2 modelos.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest  # noqa: F401  (available in env)

import cafe_sai_modelos_equipo9 as pkg


MODELS_DIR = pkg.get_models_dir()


def _sha256(path: Path, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def test_artefactos_modelos_existen():
    assert (MODELS_DIR / "narino_extratrees_entrega2.joblib").is_file(), "Nariño .joblib missing"
    assert (MODELS_DIR / "quindio_randomforest_entrega2.joblib").is_file(), "Quindío .joblib missing"
    assert (MODELS_DIR / "metadata_entrega2.json").is_file()


def test_csvs_referencia_existen():
    for name in [
        "features_panel_entrenamiento.csv",
        "umbrales_departamento.csv",
        "kpis_resumen.csv",
        "pred_vs_real_loyo.csv",
        "validacion_historica_n1.csv",
    ]:
        assert (MODELS_DIR / name).is_file(), f"Falta CSV {name}"


def test_modelos_sha256_no_vacios():
    for name in ["narino_extratrees_entrega2.joblib", "quindio_randomforest_entrega2.joblib"]:
        size = (MODELS_DIR / name).stat().st_size
        assert size > 20_000, f"{name} demasiado pequeño ({size}b)"
        sha = _sha256(MODELS_DIR / name)
        assert len(sha) == 64


def test_metadata_oficial_hiperparametros():
    md = json.loads((MODELS_DIR / "metadata_entrega2.json").read_text(encoding="utf-8"))
    nar = md["hiperparametros_oficiales"]["Narino"]
    qui = md["hiperparametros_oficiales"]["Quindio"]
    assert nar["n_estimators"] == 400
    assert nar["max_depth"] == 3
    # Clase se infiere del nombre de archivo / modelo en artifacts.
    # Validamos los campos que sí existen en metadata (bootstrap false = ExtraTrees, true = RF).
    assert nar.get("bootstrap") is False or nar.get("bootstrap") in (False, 0)
    assert qui["n_estimators"] == 400
    assert qui["max_depth"] == 2
    assert qui.get("bootstrap") is True or qui.get("bootstrap") in (True, 1)
    assert md.get("seed_oficial_entrega_2") == 42
    feats = (
        md.get("features_fenologicas_orden_fijo")
        or md.get("features_fenologicas")
        or md.get("features")
    )
    assert feats == pkg.FEATURES_FENOLOGICAS


def test_loader_load_models_retorna_2_modelos():
    models = pkg.load_models()
    assert set(models.keys()) == {"Narino", "Quindio"}
    for v in models.values():
        assert hasattr(v, "predict")
        assert hasattr(v, "fit")
        # Loader debe haber forzado runtime n_jobs=1.
        assert getattr(v, "n_jobs", 1) == 1, "loader debe sobreescribir runtime n_jobs a 1"


def test_loader_panel_shape():
    p = pkg.get_panel_entrenamiento()
    assert p.shape == (24, 48), f"Panel shape esperado (24,48) obtuvo {p.shape}"
    # Sin duplicados (depto, year)
    dup = p.duplicated(subset=["departamento", "year"]).sum()
    assert int(dup) == 0, f"Duplicados (depto,year): {int(dup)}"
