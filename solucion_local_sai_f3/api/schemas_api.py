"""
Pydantic schemas para la API REST.

Regla: estos schemas NO implementan lógica de predicción. Solo validan entrada
y serializan salida. La lógica real está en cafe_sai_modelos_equipo9 package.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

DepartamentoLiteral = Literal["Narino", "Quindio"]


class BaseFenologicaFeatures(BaseModel):
    spi3_floracion: float = Field(
        ...,
        description="SPI-3 correspondiente a la etapa fenológica de floración (típico rango ~[-3, +3]).",
    )
    spi3_desarrollo: float = Field(
        ...,
        description="SPI-3 etapa de desarrollo del grano.",
    )
    spi3_cosecha: float = Field(
        ...,
        description="SPI-3 etapa de cosecha.",
    )
    tmax_mean_e9: float = Field(
        ...,
        description="Temperatura máxima media (°C) en el enneágono agrícola cafetera.",
    )
    oni_mean: float = Field(
        ...,
        description="Índice ONI medio anual (NOAA Oceanic Niño Index).",
    )
    roya_dummy: int = Field(
        ...,
        description="Indicador binario presencia de roya (0 = sin impacto, 1 = año con roya/epidemia).",
        ge=0,
        le=1,
    )

    @field_validator(
        "spi3_floracion",
        "spi3_desarrollo",
        "spi3_cosecha",
        "oni_mean",
        "tmax_mean_e9",
        mode="before",
    )
    @classmethod
    def _finite_numeric(cls, v: Any) -> float:
        try:
            f = float(v)
        except Exception as exc:  # noqa: BLE001
            raise ValueError("Debe ser numérico finito") from exc
        if not (-1e9 <= f <= 1e9):  # noqa: PLR2004
            raise ValueError("Valor fuera de rango numérico razonable")
        return f

    @field_validator(
        "spi3_floracion", "spi3_desarrollo", "spi3_cosecha", "oni_mean",
    )
    @classmethod
    def _spi_oni_warning(cls, v: float) -> float:
        # Hard reject solo en caso de imposibilidades; rango de warning es -5 a +5.
        if v < -10 or v > 10:  # noqa: PLR2004
            raise ValueError(
                "Índice climático (SPI/ONI) fuera de rango plausible [-10, 10]."
            )
        return v

    @field_validator("tmax_mean_e9")
    @classmethod
    def _tmax_valid(cls, v: float) -> float:
        if v < 0 or v > 50:  # noqa: PLR2004
            raise ValueError("tmax_mean_e9 fuera de rango plausible [0, 50] °C.")
        return v

    @field_validator("roya_dummy", mode="before")
    @classmethod
    def _roya_binary(cls, v: Any) -> int:
        try:
            iv = int(v)
        except Exception as exc:  # noqa: BLE001
            raise ValueError("roya_dummy debe ser entero 0 o 1.") from exc
        if iv not in (0, 1):
            raise ValueError("roya_dummy debe ser exactamente 0 o 1.")
        return iv


class PrediccionRendimientoRequest(BaseFenologicaFeatures):
    departamento: DepartamentoLiteral = Field(
        ...,
        description='Departamento de predicción: "Narino" o "Quindio".',
    )


class PrediccionRendimientoResponse(BaseModel):
    departamento: DepartamentoLiteral
    modelo: str
    prediccion_kg_ha: float
    n_features: int
    status: Literal["success", "error"]
    warnings: list[str] = Field(default_factory=list)
    request_id: str | None = None


class ActivacionSPIRequest(BaseModel):
    spi_min_annual: float | None = None
    spi_min_e9: float | None = None
    spi3_cosecha: float | None = None
    n_sequia_e9: int | None = Field(default=None, ge=0, le=12)
    roya_dummy: int | None = Field(default=None, ge=0, le=1)
    roya_shock: int | None = Field(default=None, ge=0, le=1)


class ActivacionSPIResponse(BaseModel):
    departamento: DepartamentoLiteral
    activo: bool
    umbral_sequia_p10: float
    umbral_exceso_p90: float
    pago_cop_ha: int
    regla_activada: str | None
    condiciones: dict[str, bool]
    status: Literal["success", "error"]
    warnings: list[str] = Field(default_factory=list)


class KPIActuarial(BaseModel):
    departamento: DepartamentoLiteral
    HE_Ederington: float | None
    riesgo_base_pct: float | None
    prima_actuarial_pct: float | None
    frecuencia_activacion_pct: float | None
    rmse_holdout_mejor: float | None
    pago_cop_ha: int
    pct_total_activacion: float | None


class HealthResponse(BaseModel):
    status: str = "ok"
    package_version: str
    package_name: str = "cafe-sai-modelos-equipo9"
    models_available: list[DepartamentoLiteral]
    models_dir: str
    timestamp: str


class SeriesResponse(BaseModel):
    rows: list[dict[str, Any]]
    columns: list[str]
    shape: list[int]


class KpisFullResponse(BaseModel):
    track_b_por_depto: dict[str, dict[str, Any]]
    track_a_por_depto: dict[str, dict[str, Any]]
    actuariales_por_depto: dict[DepartamentoLiteral, KPIActuarial]
    disponible_cols: dict[str, list[str]]
