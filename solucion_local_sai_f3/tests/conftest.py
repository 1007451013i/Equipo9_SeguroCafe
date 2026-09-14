"""
Conftest pytest.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE_SRC = ROOT / "package_src"
if PACKAGE_SRC.is_dir() and str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))
# Limitar threading/forking en workers para evitar hangs.
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

MODELS_DIR = ROOT / "models_artifacts"
if MODELS_DIR.is_dir():
    os.environ["CAFE_SAI_MODELS_DIR"] = str(MODELS_DIR)


def pytest_configure(config):  # noqa: D401, ARG001
    import cafe_sai_modelos_equipo9 as pkg  # type: ignore[import-not-found]
    # Warm-up carga de modelos y CSVs para que tests sean rápidos.
    if MODELS_DIR.is_dir():
        pkg.set_models_dir(str(MODELS_DIR))
    pkg.load_models()
    pkg.get_panel_entrenamiento()
    pkg.get_kpis_actuariales()
