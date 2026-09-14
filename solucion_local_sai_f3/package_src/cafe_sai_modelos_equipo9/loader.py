"""
Loader for models_artifacts directory (RUNTIME PORTABLE).

Rule: models_artifacts NEVER ship inside .whl. All runtime paths resolve
EXCLUSIVELY within the portable root folder (solucion_local_sai_f3). No path
leaks outside this folder. No absolute paths hardcoded. No dependencies on
any external sibling folders (Trabajo de Grado, Informe Mejorado, etc.).
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


def _find_upwards_dir_with(target_name: str, start: Path, max_levels: int = 12) -> Path | None:
    """
    Portable path discovery: walk up from `start` parent by parent, until a dir
    containing a child named `target_name` is found. Works REGARDLESS of how
    many nesting levels exist above solucion_local_sai_f3 (0, 1, 3, 10 ...).
    Never leaks outside the volume's root. Stops at max_levels as safety.
    """
    current = start.resolve()
    for _ in range(max_levels):
        candidate = current / target_name
        if candidate.is_dir():
            return candidate
        if current.parent == current:  # filesystem root reached
            return None
        current = current.parent
    return None


def _infer_default_models_dir() -> Path:
    """
    3-strategy fallback (100% portable, no nesting assumptions):
      1) ENV CAFE_SAI_MODELS_DIR (highest priority, user override).
      2) Walk UPWARDS from loader.py location until we find a folder that
         CONTAINS a child named "models_artifacts". Works whether
         solucion_local_sai_f3 lives directly at the project root or nested
         1-12 levels deep (e.g. cloned repo structure).
      3) Current Working Directory / "models_artifacts".
    """
    # 1) ENV override (explicit wins)
    env = os.environ.get("CAFE_SAI_MODELS_DIR")
    if env:
        p_env = Path(env).resolve()
        if p_env.is_dir():
            return p_env

    # 2) Portable discovery relative to THIS loader file.
    #    Escenario A: <SOLUTION_ROOT>/package_src/cafe_sai_modelos_equipo9/loader.py
    #                  -> parent of package_src is SOLUTION_ROOT, contains models_artifacts
    #    Escenario B: SOLUTION_ROOT is loader.py.parents[3] if Caso_01/solucion_local/..
    #    Escenario C: SOLUTION_ROOT is parents[0] of package_src (raiz sin carpeta padre)
    #    Walk up is agnostic to all 3 (and more).
    here = Path(__file__).resolve()
    found_from_here = _find_upwards_dir_with("models_artifacts", start=here)
    if found_from_here is not None:
        return found_from_here

    # 3) CWD fallback.
    cwd_candidate = Path.cwd() / "models_artifacts"
    if cwd_candidate.is_dir():
        return cwd_candidate

    raise FileNotFoundError(
        "No se encontro models_artifacts. Define CAFE_SAI_MODELS_DIR o llama"
        " a set_models_dir(ruta). Fallbacks probados: env CAFE_SAI_MODELS_DIR,"
        " busqueda ascendente desde loader.py (max 12 niveles),"
        f" CWD/models_artifacts={cwd_candidate}. Los 2 archivos .joblib y los"
        " CSV de referencia deben estar en models_artifacts/ dentro de la"
        " carpeta solucion_local_sai_f3."
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
