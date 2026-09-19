"""
FastAPI entry point for SAI Cafetero Quindío/Nariño local API.

Toda la lógica de inferencia está en cafe_sai_modelos_equipo9 (package único).
ESTA API NO CARGA sklearn/joblib/pandas DIRECTAMENTE: usa el package.
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Path as _Fastapi_Path, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Permitir ejecutar la API tanto con "uvicorn api.main:app" (desde solucion_local_sai_f3)
# como directamente importada. Aseguramos que package_src esté en sys.path solo si
# aún no está instalado el wheel (entorno dev).
# ---------------------------------------------------------------------------
_ROOT_DIR = Path(__file__).resolve().parent.parent
_PACKAGE_SRC = _ROOT_DIR / "package_src"
if _PACKAGE_SRC.is_dir() and str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

try:
    import cafe_sai_modelos_equipo9 as pkg  # type: ignore[import-not-found]
except Exception as exc:  # noqa: BLE001
    raise RuntimeError(
        "Package cafe_sai_modelos_equipo9 no disponible. Instala el wheel o agrega"
        " package_src al PYTHONPATH."
    ) from exc

from api.schemas_api import (  # noqa: E402
    ActivacionSPIRequest,
    ActivacionSPIResponse,
    DepartamentoLiteral,
    HealthResponse,
    KPIActuarial,
    KpisFullResponse,
    PrediccionRendimientoRequest,
    PrediccionRendimientoResponse,
    SeriesResponse,
)

API_VERSION = "0.1.0"
PACKAGE_FULL_VERSION = pkg.__version__
DEPARTAMENTOS_VALIDOS: tuple[DepartamentoLiteral, ...] = ("Narino", "Quindio")


# ---------------------------------------------------------------------------
# Lifespan (precarga de modelos a startup)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: D401
    # Startup
    models_dir_env = os.environ.get("CAFE_SAI_MODELS_DIR")
    if models_dir_env:
        try:
            pkg.set_models_dir(models_dir_env)
        except Exception as exc:  # noqa: BLE001
            print(f"[API-STARTUP] Warning CAFE_SAI_MODELS_DIR inválido: {exc}")
    try:
        pkg.load_models()
        print(f"[API-STARTUP] Modelos cargados OK desde: {pkg.get_models_dir()}")
    except Exception as exc:  # noqa: BLE001
        print(f"[API-STARTUP] ERROR cargando modelos: {exc}")
    yield
    # Shutdown: no hay recursos que liberar


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="API Seguro Agrícola Indexado Cafetero",
    description=(
        "Expone los modelos oficiales Informe Mejorado Entrega_2 "
        "(ExtraTrees Nariño + RandomForest Quindío) + Track A SPI + KPIs."
    ),
    version=API_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _uuid() -> str:
    return uuid.uuid4().hex[:12]


def _check_depto(depto: str) -> DepartamentoLiteral:
    if depto not in DEPARTAMENTOS_VALIDOS:
        valid = sorted(DEPARTAMENTOS_VALIDOS)
        raise HTTPException(
            status_code=400,
            detail=f"Departamento inválido {depto!r}. Válidos: {valid}",
        )
    return depto  # type: ignore[return-value]


def _series_to_response(df: Any) -> SeriesResponse:
    cols = [str(c) for c in df.columns.tolist()]
    # Convert NaN/NaT a None (JSON safe)
    import math

    def _to_json_safe(v: Any) -> Any:
        if isinstance(v, float) and math.isnan(v):
            return None
        if hasattr(v, "item"):
            try:
                return v.item()
            except Exception:  # noqa: BLE001
                pass
        return v

    rows = [
        {c: _to_json_safe(v) for c, v in zip(cols, r)}
        for r in df.itertuples(index=False, name=None)
    ]
    return SeriesResponse(rows=rows, columns=cols, shape=[len(rows), len(cols)])


# ---------------------------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------------------------
@app.get("/health", tags=["meta"], response_model=HealthResponse)
def health() -> HealthResponse:
    """Estado de salud de la API y versiones."""
    models = pkg.load_models()
    return HealthResponse(
        status="ok",
        package_version=PACKAGE_FULL_VERSION,
        models_available=sorted(models.keys()),  # type: ignore[arg-type]
        models_dir=str(pkg.get_models_dir()),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/api/v1/models", tags=["meta"])
def list_models() -> dict[str, Any]:
    """Lista de modelos disponibles + features oficiales y metadata."""
    models = pkg.load_models()
    md_path = pkg.get_models_dir() / "metadata_entrega2.json"
    meta: dict[str, Any] | None = None
    if md_path.exists():
        try:
            import json

            meta = json.loads(md_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            meta = None
    return {
        "package_version": PACKAGE_FULL_VERSION,
        "api_version": API_VERSION,
        "departamentos": sorted(models.keys()),
        "features_fenologicas_orden": pkg.FEATURES_FENOLOGICAS,
        "target": pkg.TARGET,
        "pago_evento_cop_ha": pkg.schemas.PAGO_POR_EVENTO_COP_HA,
        "metadata_entrega2": meta,
    }


# -------- Track B: predicción rendimiento --------
@app.post(
    "/api/v1/predict/rendimiento",
    tags=["Track B — Rendimiento"],
    response_model=PrediccionRendimientoResponse,
)
def predict_rendimiento(
    body: PrediccionRendimientoRequest,
) -> PrediccionRendimientoResponse:
    """
    Predice rendimiento kg/ha con el modelo oficial del departamento.

    Recibe departamento + 6 variables fenológicas en el body.
    Valida con Pydantic y retorna 422 si hay errores de esquema.
    """
    depto = _check_depto(body.departamento)
    req_id = _uuid()
    t0 = time.perf_counter()
    try:
        out = pkg.predict_rendimiento(depto, body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en predict_rendimiento: {exc}",
        ) from exc
    if out["status"] != "success":
        # Solo status success en este endpoint dado que package no produce "error"
        # con inputs que pasan Pydantic. Por si acaso:
        raise HTTPException(status_code=500, detail=out["warnings"])
    out["warnings"].append(
        f"server_ms={round((time.perf_counter()-t0)*1000, 2)}"
    )
    return PrediccionRendimientoResponse(
        departamento=out["departamento"],
        modelo=out["modelo"],
        prediccion_kg_ha=out["prediccion_kg_ha"],
        n_features=out["n_features"],
        status=out["status"],
        warnings=out["warnings"],
        request_id=req_id,
    )


@app.post(
    "/api/v1/predict/rendimiento/{departamento}",
    tags=["Track B — Rendimiento"],
    response_model=PrediccionRendimientoResponse,
)
def predict_rendimiento_path(
    departamento: str = _Fastapi_Path(
        ..., description='Departamento: "Narino" o "Quindio".'
    ),
    body: PrediccionRendimientoRequest | None = None,
    spi3_floracion: float | None = Query(default=None),
    spi3_desarrollo: float | None = Query(default=None),
    spi3_cosecha: float | None = Query(default=None),
    tmax_mean_e9: float | None = Query(default=None),
    oni_mean: float | None = Query(default=None),
    roya_dummy: int | None = Query(default=None, ge=0, le=1),
) -> PrediccionRendimientoResponse:
    """
    Endpoint alternativo: departamento en URL + features por query params o body.
    """
    depto = _check_depto(departamento)
    # Preferencia: body > query params
    features: dict[str, Any] = {}
    if body is not None:
        features = body.model_dump(exclude={"departamento"}, exclude_none=False)
    # Si vienen query params, prevalecen sobre el body
    for name, val in {
        "spi3_floracion": spi3_floracion,
        "spi3_desarrollo": spi3_desarrollo,
        "spi3_cosecha": spi3_cosecha,
        "tmax_mean_e9": tmax_mean_e9,
        "oni_mean": oni_mean,
        "roya_dummy": roya_dummy,
    }.items():
        if val is not None:
            features[name] = val
    if set(features.keys()) < set(pkg.FEATURES_FENOLOGICAS):
        missing = [f for f in pkg.FEATURES_FENOLOGICAS if f not in features]
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Campos fenológicos incompletos",
                "faltantes": missing,
                "requeridos": pkg.FEATURES_FENOLOGICAS,
            },
        )
    try:
        out = pkg.predict_rendimiento(depto, features)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return PrediccionRendimientoResponse(
        departamento=out["departamento"],
        modelo=out["modelo"],
        prediccion_kg_ha=out["prediccion_kg_ha"],
        n_features=out["n_features"],
        status=out["status"],
        warnings=out["warnings"],
        request_id=_uuid(),
    )


# -------- Track A: SPI / activación seguro --------
@app.get("/api/v1/track-a/umbrales", tags=["Track A — SPI"])
def get_umbrales_track_a() -> dict[str, Any]:
    """Umbrales P10/P90 oficiales por departamento."""
    kb = pkg.get_kpis_track_a()
    return {
        "package_version": PACKAGE_FULL_VERSION,
        "umbrales_por_departamento": kb,
    }


@app.post(
    "/api/v1/track-a/activacion/{departamento}",
    tags=["Track A — SPI"],
    response_model=ActivacionSPIResponse,
)
def predict_activacion_spi(
    departamento: str,
    body: ActivacionSPIRequest,
) -> ActivacionSPIResponse:
    """
    5 reglas OR para activación del seguro (exactamente pipeline_equipo9.py).
    """
    depto = _check_depto(departamento)
    try:
        out = pkg.predict_activacion_spi(depto, body.model_dump(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ActivacionSPIResponse(**out)


# -------- KPIs --------
@app.get("/api/v1/kpis", tags=["KPIs"])
def get_kpis() -> KpisFullResponse:
    """KPIs completos: Track B (rendimiento), Track A (SPI) y actuariales (HE, prima)."""
    kb = pkg.get_kpis_track_b()
    ka = pkg.get_kpis_track_a()
    act = pkg.get_kpis_actuariales()
    cols = pkg.list_kpis_available()
    actuariales_out = {
        k: KPIActuarial(**v) for k, v in act.items()
    }
    return KpisFullResponse(
        track_b_por_depto=kb,
        track_a_por_depto=ka,
        actuariales_por_depto=actuariales_out,
        disponible_cols=cols,
    )


# -------- Series / Historical --------
@app.get("/api/v1/series/historico", tags=["Series históricas"])
def get_series_panel_entrenamiento() -> SeriesResponse:
    """Panel único 24 filas (12 años × 2 deptos) usado en Entrega_2 CELL 122."""
    df = pkg.get_panel_entrenamiento()
    return _series_to_response(df)


@app.get("/api/v1/series/pred-vs-real", tags=["Series históricas"])
def get_series_pred_vs_real() -> SeriesResponse:
    """LOYO pred-vs-real pre-calculado en Fase 2."""
    df = pkg.get_pred_vs_real_loyo()
    return _series_to_response(df)


@app.get("/api/v1/validacion-historica", tags=["Series históricas"])
def get_validacion_historica_n1() -> SeriesResponse:
    """Eventos 2012 Roya / 2015 Niño y activación esperada."""
    df = pkg.get_validacion_historica_n1()
    return _series_to_response(df)


# -------- Root --------
@app.get("/", tags=["meta"])
def root() -> dict[str, Any]:
    return {
        "nombre": "API SAI Cafetero (Entrega_2)",
        "version_api": API_VERSION,
        "package": f"cafe-sai-modelos-equipo9=={PACKAGE_FULL_VERSION}",
        "docs": "/docs",
        "endpoints": [
            "GET /health",
            "GET /api/v1/models",
            "POST /api/v1/predict/rendimiento",
            "POST /api/v1/predict/rendimiento/{departamento}",
            "GET /api/v1/track-a/umbrales",
            "POST /api/v1/track-a/activacion/{departamento}",
            "GET /api/v1/kpis",
            "GET /api/v1/series/historico",
            "GET /api/v1/series/pred-vs-real",
            "GET /api/v1/validacion-historica",
        ],
    }
