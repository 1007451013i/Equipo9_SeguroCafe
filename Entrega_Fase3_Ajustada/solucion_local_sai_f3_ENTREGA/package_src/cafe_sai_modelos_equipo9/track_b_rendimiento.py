"""
Track B — Predicción rendimiento kg/ha.

ÚNICA fuente de verdad para inferencia. NO duplicar esta lógica en API/Dashboard.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .loader import load_models
from .schemas import (
    FEATURES_FENOLOGICAS,
    Departamento,
    RendimientoFeatures,
    RendimientoPredictionOutput,
)

# Departamento válidos literales (por esquema TypedDict) — lista para runtime check
DEPARTAMENTOS_SET: set[str] = {"Narino", "Quindio"}


def _coerce_and_validate_features(
    features: dict[str, Any] | RendimientoFeatures,
) -> tuple[RendimientoFeatures, list[str]]:
    warnings: list[str] = []
    missing = [f for f in FEATURES_FENOLOGICAS if f not in features]
    if missing:
        raise ValueError(
            f"Faltan campos requeridos: {missing}. Requeridos: {FEATURES_FENOLOGICAS}"
        )
    extra = [k for k in features if k not in FEATURES_FENOLOGICAS]
    if extra:
        warnings.append(
            f"Se ignoran campos adicionales no usados por el modelo oficial: {extra}"
        )

    cleaned: dict[str, Any] = {}
    for f in FEATURES_FENOLOGICAS:
        v = features[f]
        try:
            if f == "roya_dummy":
                iv = int(v)
                if iv not in (0, 1):
                    raise ValueError
                cleaned[f] = iv
            else:
                cleaned[f] = float(v)
                if not np.isfinite(cleaned[f]):
                    raise ValueError
        except Exception as exc:  # noqa: BLE001
            raise ValueError(
                f"Campo {f!r} inválido {v!r}. "
                + ("roya_dummy debe ser 0 o 1" if f == "roya_dummy" else "debe ser número finito")
            ) from exc

    # Rangos razonables (warnings, no raise — modelo Entrega_2 no impone hard bounds)
    for f in ("spi3_floracion", "spi3_desarrollo", "spi3_cosecha", "oni_mean"):
        if cleaned[f] < -5 or cleaned[f] > 5:
            warnings.append(
                f"{f}={cleaned[f]:.3f} fuera de rango razonable [-5,5] SPI/ONI."
            )
    tmax = cleaned["tmax_mean_e9"]
    if tmax < 10 or tmax > 40:
        warnings.append(f"tmax_mean_e9={tmax:.2f} fuera de rango razonable [10,40] °C.")

    return cleaned, warnings  # type: ignore[return-value]


def predict_rendimiento(
    departamento: Departamento | str,
    features: dict[str, Any] | RendimientoFeatures,
) -> RendimientoPredictionOutput:
    """
    Predice rendimiento kg/ha para un departamento usando el modelo OFICIAL
    ExtraTrees (Narino) o RandomForest (Quindio) de Entrega_2.

    Regla estricta: los 6 features van en el orden FEATURES_FENOLOGICAS (igual
    que en Entrega_2 CELL 85 y CELL 122).
    """
    if departamento not in DEPARTAMENTOS_SET:
        valid = sorted(DEPARTAMENTOS_SET)
        raise ValueError(f"Departamento inválido {departamento!r}. Válidos: {valid}")

    depto: Departamento = departamento  # type: ignore[assignment]
    models = load_models()
    model = models[depto]
    cleaned_feats, warnings = _coerce_and_validate_features(features)

    X = pd.DataFrame([cleaned_feats], columns=FEATURES_FENOLOGICAS)
    raw_pred = model.predict(X)
    if raw_pred.ndim != 1 or len(raw_pred) != 1:
        raise ValueError(f"Salida de modelo inesperada shape={raw_pred.shape}")
    pred_kg_ha = float(raw_pred[0])
    if not np.isfinite(pred_kg_ha):
        return {
            "departamento": depto,
            "modelo": type(model).__name__,
            "prediccion_kg_ha": float("nan"),
            "n_features": len(FEATURES_FENOLOGICAS),
            "status": "error",
            "warnings": [*warnings, "Predicción NaN/Inf por modelo oficial."],
        }

    if pred_kg_ha < 0:
        warnings.append(
            "Predicción negativa por modelo oficial (fuera del dominio del cultivo)."
        )

    return {
        "departamento": depto,
        "modelo": type(model).__name__,
        "prediccion_kg_ha": pred_kg_ha,
        "n_features": len(FEATURES_FENOLOGICAS),
        "status": "success",
        "warnings": warnings,
    }


__all__ = ["predict_rendimiento"]
