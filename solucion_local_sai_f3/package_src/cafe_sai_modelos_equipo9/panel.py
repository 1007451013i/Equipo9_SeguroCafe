"""
Series históricas (panel de entrenamiento 24 obs + LOYO pred vs real + validación histórica N1).

CSVs oficiales pre-calculados. No recalculamos nada (rule #1).
"""

from __future__ import annotations

import pandas as pd

from .loader import load_reference_csv


def get_panel_entrenamiento() -> pd.DataFrame:
    """24 filas = 12 años × 2 departamentos (drop dup depto+year). Features originales."""
    df = load_reference_csv("panel_entrenamiento")
    return df.drop_duplicates(["departamento", "year"]).reset_index(drop=True)


def get_pred_vs_real_loyo() -> pd.DataFrame:
    """LOYO pred vs real ya calculado en pipeline Fase2."""
    return load_reference_csv("pred_vs_real")


def get_validacion_historica_n1() -> pd.DataFrame:
    """Eventos históricos: 2012 Roya, 2015 Niño. SI/SI por depto."""
    return load_reference_csv("validacion_historica")


__all__ = [
    "get_panel_entrenamiento",
    "get_pred_vs_real_loyo",
    "get_validacion_historica_n1",
]
