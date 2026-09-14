"""
Loader for models_artifacts directory.

Rule: models_artifacts NEVER ship inside .whl (they are deployed alongside via
MODELS_DIR env var or explicit set_models_dir() call).
"""

from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from .schemas import Departamento

_MODELS_DIR_LOCK = threading.Lock()
_MODELS_DIR: Path | None = None

_MODEL_FILES: dict[Departamento, str] = {
    "Narino": "narino_extratrees_entrega2.joblib",
    "Quindio": "quindio_randomforest_entrega2.joblib",
}

_REF_CSVS: dict[str, str] = {
    "umbrales": "umbrales_departamento.csv",
    "kpis": "kpis_resumen.csv",
    "pred_vs_real": "pred_vs_real_loyo.csv",
    "validacion_historica": "validacion_historica_n1.csv",
    "panel_entrenamiento": "features_panel_entrenamiento.csv",
    "metadata": "metadata_entrega2.json",
}


def set_models_dir(path: str | os.PathLike[str]) -> None:
    global _MODELS_DIR
    p = Path(path).resolve()
    if not p.is_dir():
        raise FileNotFoundError(f"MODELS_DIR no existe o no es carpeta: {p}")
    with _MODELS_DIR_LOCK:
        _MODELS_DIR = p


def _infer_default_models_dir() -> Path:
    package_root = Path(__file__).resolve().parent.parent.parent
    candidate = package_root / "models_artifacts"
    if candidate.is_dir():
        return candidate
    env = os.environ.get("CAFE_SAI_MODELS_DIR")
    if env:
        p = Path(env).resolve()
        if p.is_dir():
            return p
    cwd_candidate = Path.cwd() / "models_artifacts"
    if cwd_candidate.is_dir():
        return cwd_candidate
    raise FileNotFoundError(
        "No se encontró models_artifacts. Setea CAFE_SAI_MODELS_DIR o llama"
        f" a set_models_dir(ruta). Buscados: {candidate}, CWD/models_artifacts,"
        " env CAFE_SAI_MODELS_DIR."
    )


def get_models_dir() -> Path:
    with _MODELS_DIR_LOCK:
        if _MODELS_DIR is None:
            set_models_dir(_infer_default_models_dir())
        assert _MODELS_DIR is not None
        return _MODELS_DIR


_CACHED: dict[str, Any] = {}
_CACHE_LOCK = threading.Lock()


def load_models() -> dict[Departamento, Any]:
    key = "__models__"
    with _CACHE_LOCK:
        if key in _CACHED:
            return _CACHED[key]
        models_dir = get_models_dir()
        loaded: dict[Departamento, Any] = {}
        for depto, fname in _MODEL_FILES.items():
            fpath = models_dir / fname
            if not fpath.exists():
                raise FileNotFoundError(
                    f"No existe artefacto modelo para {depto}: {fpath}."
                    " Ejecuta primero package_src/.../_build/00_serializar_modelos_oficiales.py"
                )
            model = joblib.load(fpath)
            # Runtime-only override: disable parallelism. El .joblib original se
            # preserva con n_jobs=-1 (valor oficial); esto evita cuelgues en
            # sandbox entornos. NO modifica entrenamiento, sólo los workers de predict.
            try:
                if hasattr(model, "n_jobs"):
                    object.__setattr__(model, "n_jobs", 1)
            except Exception:  # noqa: BLE001
                pass
            loaded[depto] = model
        _CACHED[key] = loaded
        return loaded


def load_reference_csv(ref_name: str) -> pd.DataFrame:
    if ref_name not in _REF_CSVS:
        valid = ", ".join(sorted(_REF_CSVS))
        raise KeyError(f"ref_name inválido: {ref_name}. Válidos: {valid}")
    key = f"csv_{ref_name}"
    with _CACHE_LOCK:
        if key in _CACHED:
            return _CACHED[key]
        fname = _REF_CSVS[ref_name]
        fpath = get_models_dir() / fname
        if not fpath.exists():
            raise FileNotFoundError(f"No existe CSV referencia: {fpath}")
        df = pd.read_csv(fpath)
        _CACHED[key] = df
        return df
