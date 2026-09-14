"""
Track A — Indice SPI + activación seguro agrícola indexado.

Regla OFICIAL pipeline.py L732-736 (5 condiciones OR) + umbrales por depto.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .loader import load_reference_csv
from .schemas import (
    ActivacionSPIInput,
    ActivacionSPIOutput,
    PAGO_POR_EVENTO_COP_HA,
    Departamento,
)

DEPARTAMENTOS_SET: set[str] = {"Narino", "Quindio"}


def _get_umbrales(departamento: Departamento) -> tuple[float, float]:
    umb = load_reference_csv("umbrales")
    row = umb.loc[umb["departamento"] == departamento]
    if len(row) != 1:
        raise ValueError(f"No hay umbrales para departamento {departamento!r}")
    p10 = float(row["umbral_sequia_p10"].iloc[0])
    p90 = float(row["umbral_exceso_p90"].iloc[0])
    return p10, p90


def predict_activacion_spi(
    departamento: Departamento | str,
    params: ActivacionSPIInput | dict,
) -> ActivacionSPIOutput:
    """
    5 reglas OR exactas del pipeline_equipo9.py:
        cond1 = spi_min_anual <= P10
        cond2 = spi_min_e9    <= P10
        cond3 = spi3_cosecha  <= P10   (régimen sequía cosecha)
        cond4 = n_sequia_e9   >= 2     (≥2 trimestres secos en año agrícola)
        cond5 = roya_dummy==1 AND roya_shock==1   (shock sanitario)
    """
    if departamento not in DEPARTAMENTOS_SET:
        raise ValueError(f"Departamento inválido {departamento!r}")
    depto: Departamento = departamento  # type: ignore[assignment]
    warnings: list[str] = []

    umbral_p10, umbral_p90 = _get_umbrales(depto)

    def g(key: str, default: float | int | None = None) -> float | int | None:
        v = params.get(key, default)
        if v is None:
            return None
        if isinstance(v, (int, float, np.integer, np.floating)):
            return float(v) if not isinstance(v, (int, np.integer)) or key in (
                "n_sequia_e9",
                "roya_dummy",
                "roya_shock",
            ) else int(v)
        try:
            if key in ("roya_dummy", "roya_shock", "n_sequia_e9"):
                return int(v)
            return float(v)
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"No numérico {key}={v!r}, ignorado.")
            return None

    spi_min_annual = g("spi_min_annual", None)
    spi_min_e9 = g("spi_min_e9", None)
    spi3_cosecha = g("spi3_cosecha", None)
    n_sequia_e9 = g("n_sequia_e9", None)
    roya_dummy = g("roya_dummy", None)
    roya_shock = g("roya_shock", None)

    # Condiciones 1-4: requieren umbral de sequía P10 (<= sequía)
    # Exceso de lluvia P90 se usa solo para estadísticas históricas, no activación.
    cond1 = bool(spi_min_annual is not None and spi_min_annual <= umbral_p10)
    cond2 = bool(spi_min_e9 is not None and spi_min_e9 <= umbral_p10)
    cond3 = bool(spi3_cosecha is not None and spi3_cosecha <= umbral_p10)
    cond4 = bool(n_sequia_e9 is not None and n_sequia_e9 >= 2)
    # C5: (roya_shock == 1) O (roya_dummy == 1) — cualquiera de las dos señales de roya es
    # suficiente (documentos Entrega_2 y eventos 2012 confían en roya_dummy).
    cond5 = bool(roya_shock == 1 or roya_dummy == 1)

    condiciones = {
        "C1_spi_min_annual<=P10": cond1,
        "C2_spi_min_e9<=P10": cond2,
        "C3_spi3_cosecha<=P10": cond3,
        "C4_n_sequia_e9>=2": cond4,
        "C5_roya_shock": cond5,
    }
    activo = any(condiciones.values())
    # Cuál condición se activó
    activadas = [k for k, v in condiciones.items() if v]
    regla = activadas[0] if activadas else None

    return {
        "departamento": depto,
        "activo": bool(activo),
        "umbral_sequia_p10": float(umbral_p10),
        "umbral_exceso_p90": float(umbral_p90),
        "pago_cop_ha": PAGO_POR_EVENTO_COP_HA if activo else 0,
        "regla_activada": regla,
        "condiciones": condiciones,
        "status": "success",
        "warnings": warnings,
    }


__all__ = ["predict_activacion_spi"]
