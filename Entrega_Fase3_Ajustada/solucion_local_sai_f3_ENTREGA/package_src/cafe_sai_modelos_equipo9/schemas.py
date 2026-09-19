"""
Constants + typed schemas for cafe_sai_modelos_equipo9 package.

These are derived directly from Informe Mejorado Entrega_2. DO NOT MODIFY.
"""

from __future__ import annotations

from typing import Literal, TypedDict

Departamento = Literal["Narino", "Quindio"]

# Exactamente Entrega_2 CELL 85 — orden fijo, NUNCA cambiar
FEATURES_FENOLOGICAS: list[str] = [
    "spi3_floracion",
    "spi3_desarrollo",
    "spi3_cosecha",
    "tmax_mean_e9",
    "oni_mean",
    "roya_dummy",
]
TARGET: str = "rendimiento_kg_ha"

# Pago por evento indemnizatorio oficial (Fase2 Externo §1.3.4 + pipeline L738)
PAGO_POR_EVENTO_COP_HA: int = 1_200_000


class RendimientoFeatures(TypedDict, total=True):
    spi3_floracion: float
    spi3_desarrollo: float
    spi3_cosecha: float
    tmax_mean_e9: float
    oni_mean: float
    roya_dummy: int  # 0 or 1


class RendimientoPredictionOutput(TypedDict):
    departamento: Departamento
    modelo: str
    prediccion_kg_ha: float
    n_features: int
    status: Literal["success", "error"]
    warnings: list[str]


class ActivacionSPIInput(TypedDict, total=False):
    spi_min_annual: float
    spi_min_e9: float
    spi3_cosecha: float
    n_sequia_e9: int
    roya_dummy: int
    roya_shock: int


class ActivacionSPIOutput(TypedDict):
    departamento: Departamento
    activo: bool
    umbral_sequia_p10: float
    umbral_exceso_p90: float
    pago_cop_ha: int
    regla_activada: str | None
    condiciones: dict[str, bool]
    status: Literal["success", "error"]
    warnings: list[str]


class KPIActuarialDepto(TypedDict):
    departamento: Departamento
    HE_Ederington: float | None
    riesgo_base_pct: float | None
    prima_actuarial_pct: float | None
    frecuencia_activacion_pct: float | None
    rmse_holdout_mejor: float | None
    pago_cop_ha: int
    pct_total_activacion: float | None
