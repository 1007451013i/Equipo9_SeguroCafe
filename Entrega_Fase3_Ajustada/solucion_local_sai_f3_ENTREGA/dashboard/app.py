"""
Dashboard local Streamlit — Seguro Agricola Indexado Cafetero (SAI)
Informe Mejorado Entrega_2 Fase 3 — Equipo 9 2026.

ESTRUCTURA (1 SOLA PAGINA, basada en Mockup_Panel_Fase3.pdf):
  SIDEBAR IZQUIERDO:
    - Filtro departamento (Todos, Narino, Quindio)
    - Rango de anios (slider 2007..2018)
    - Precarga historica Track B (anio/departamento)
    - Parametros calculadora actuarial (ha aseguradas, pago evento, sobrecarga prima)
  CUERPO PRINCIPAL 6 MODULOS:
    1. KPIs de negocio de la Entrega 2 (6 tarjetas actual vs deseado)
    2. Track A: Serie SPI-3 fenologico + activaciones por anio
    3. Track B: Formulario prediccion rendimiento + resultado
    4. Track B: LOYO Prediccion vs Real + metricas resumen
    5. Validacion historica N=2 (2012 Roya / 2015 Nino, semaforo cumplimiento)
    6. Calculadora actuarial (prima vs indemnizaciones, 12 anios + balance)

REGLA DURA: ESTE DASHBOARD NO CARGA MODELOS DIRECTAMENTE.
Todo se consume via HTTP a la API local FastAPI (:8000).
"""

from __future__ import annotations

import json
import os
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Graficacion: plotly (preferido) si esta disponible, si no matplotlib (fallback)
# El portable de Trabajo de Grado no trae plotly por defecto; en requirements.txt
# del proyecto si se incluye plotly>=5.18 para cuando el usuario use Python normal.
# ---------------------------------------------------------------------------
try:
    import plotly.express as px  # noqa: F401
    import plotly.graph_objects as go  # noqa: F401
    _HAS_PLOTLY = True
except Exception:  # noqa: BLE001
    _HAS_PLOTLY = False
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt  # noqa: F401
    except Exception:  # noqa: BLE001
        pass

# ---------------------------------------------------------------------------
# Configuracion de la pagina (sin emojis, sin iconos personalizados)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SAI Cafetero — Panel Ejecutivo",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = os.environ.get("SAI_API_BASE", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT = int(os.environ.get("SAI_API_TIMEOUT", "10"))


# ---------------------------------------------------------------------------
# Helpers API
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False, ttl=600)
def _api_get(path: str) -> dict | list:
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=TIMEOUT)
    except Exception as exc:  # noqa: BLE001
        st.error(
            "(!) API no disponible en "
            f"{API_BASE}. Verifica que run_api.ps1 se este ejecutando. Detalle: {exc}"
        )
        return {}
    if r.status_code >= 400:
        try:
            detail = r.json()
        except Exception:  # noqa: BLE001
            detail = r.text
        st.error(f"HTTP {r.status_code} en GET {path}: {detail}")
        return {}
    try:
        return r.json()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Respuesta no JSON en GET {path}: {exc}")
        return {}


@st.cache_data(show_spinner=False, ttl=60)
def _api_post(path: str, payload: dict, _silent: bool = False) -> dict | list:
    try:
        r = requests.post(f"{API_BASE}{path}", json=payload, timeout=TIMEOUT)
    except Exception as exc:  # noqa: BLE001
        if not _silent:
            st.error(f"(!) API sin conexion POST {path}: {exc}")
        return {}
    if r.status_code >= 400:
        try:
            detail = r.json()
        except Exception:  # noqa: BLE001
            detail = r.text
        if not _silent:
            st.error(f"HTTP {r.status_code} en POST {path}: {detail}")
        return {}
    try:
        return r.json()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Respuesta no JSON en POST {path}: {exc}")
        return {}


def _safe(d: dict, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def _fmt_num(v: float | int | None, dec: int = 1, suf: str = "") -> str:
    if v is None:
        return "—"
    try:
        return f"{float(v):,.{dec}f}{suf}"
    except Exception:  # noqa: BLE001
        return str(v)


def _fmt_pct(v: float | None) -> str:
    if v is None:
        return "—"
    f = float(v)
    if abs(f) <= 1.5:
        f = f * 100.0
    return f"{f:.2f} %"


@st.cache_data(show_spinner=False, ttl=30)
def _health_status() -> dict:
    h = _api_get("/health") or {}
    return {
        "ok": _safe(h, "status") == "ok",
        "pkg_version": _safe(h, "package_version", default="?"),
        "pkg_name": _safe(h, "package_name", default="?"),
        "models": _safe(h, "models_available", default=[]),
        "raw": h,
    }


# ---------------------------------------------------------------------------
# Helpers para extraer datos correctamente desde la API (formato TabularResponse)
# ---------------------------------------------------------------------------
def _rows_of(payload) -> list[dict]:
    if isinstance(payload, list):
        return list(payload)
    if isinstance(payload, dict):
        if isinstance(payload.get("rows"), list):
            return list(payload["rows"])
        return [dict(payload)]
    return []


def _kpis_to_list(payload) -> list[dict]:
    if not isinstance(payload, dict):
        return []
    flat: list[dict] = []
    for section_key, section in payload.items():
        if section_key == "disponible_cols":
            continue
        if isinstance(section, dict):
            for depto, inner in section.items():
                if isinstance(inner, dict):
                    if isinstance(inner.get("_rows"), list):
                        for row in inner["_rows"]:
                            d = dict(row)
                            d.setdefault("departamento", depto)
                            d.setdefault("seccion", section_key)
                            flat.append(d)
                    else:
                        d = {"departamento": depto, "seccion": section_key}
                        d.update({str(k): v for k, v in inner.items() if not str(k).startswith("_")})
                        flat.append(d)
    return flat


def _umbrales_to_list(payload) -> list[dict]:
    if not isinstance(payload, dict):
        return []
    by = payload.get("umbrales_por_departamento")
    if not isinstance(by, dict):
        return []
    flat: list[dict] = []
    for depto, v in by.items():
        if isinstance(v, dict):
            d = {"departamento": depto}
            d.update(v)
            flat.append(d)
    return flat


# ---------------------------------------------------------------------------
# Carga inicial de datos (una sola vez, cacheados)
# ---------------------------------------------------------------------------
with st.spinner("Cargando datos desde API local..."):
    HEALTH = _health_status()
    KPIS_ALL: dict = _api_get("/api/v1/kpis") or {}
    KPIS_FLAT: list[dict] = _kpis_to_list(KPIS_ALL)
    if isinstance(KPIS_ALL, dict):
        KPIS_ALL.setdefault("track_b", KPIS_ALL.get("track_b_por_depto") or {})
        KPIS_ALL.setdefault("actuariales", KPIS_ALL.get("actuariales_por_depto") or {})
        KPIS_ALL.setdefault("track_a", KPIS_ALL.get("track_a_por_depto") or {})
    UMBRALES_RAW = _api_get("/api/v1/track-a/umbrales") or {}

def _prima_of(depto: str):
    actuariales = KPIS_ALL.get("actuariales", {})
    if not isinstance(actuariales, dict):
        return None
    datos = actuariales.get(depto, {})
    if not isinstance(datos, dict):
        return None
    return datos.get("prima_actuarial_pct")

UMBRALES: list[dict] = _umbrales_to_list(UMBRALES_RAW)
PANEL_FULL: list[dict] = _rows_of(_api_get("/api/v1/series/historico") or [])
LOYO_FULL: list[dict] = _rows_of(_api_get("/api/v1/series/pred-vs-real") or [])
VALHIST_FULL: list[dict] = _rows_of(_api_get("/api/v1/validacion-historica") or [])

def _list_to_df(data: list[dict] | list | None) -> pd.DataFrame:
    if not data:
        return pd.DataFrame()
    try:
        return pd.json_normalize(data, sep="_")
    except Exception:  # noqa: BLE001
        try:
            return pd.DataFrame(data)
        except Exception:  # noqa: BLE001
            return pd.DataFrame()


PANEL_DF = _list_to_df(PANEL_FULL)
LOYO_DF = _list_to_df(LOYO_FULL)
if not LOYO_DF.empty:
    rename_map = {}
    for c in LOYO_DF.columns:
        if c == "y_real_kg_ha":
            rename_map[c] = "rendimiento_real_kg_ha"
        elif c == "y_pred_loyo_kg_ha":
            rename_map[c] = "rendimiento_predicho_kg_ha"
        elif "y_pred" in c and "predicho" not in c:
            rename_map[c] = "rendimiento_predicho_kg_ha"
    if rename_map:
        LOYO_DF = LOYO_DF.rename(columns=rename_map)
UMBRALES_DF = _list_to_df(UMBRALES)
VALHIST_DF = _list_to_df(VALHIST_FULL)

DEPTOS_DISPONIBLES = sorted(HEALTH["models"]) if HEALTH["models"] else ["Narino", "Quindio"]
ANIOS_DISPONIBLES = sorted(PANEL_DF["year"].unique().tolist()) if not PANEL_DF.empty else list(range(2007, 2019))

# ---------------------------------------------------------------------------
# SIDEBAR: Filtros interactivos globales
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("Filtros Panel")
    st.caption(
        f"Package: {HEALTH['pkg_name']} v{HEALTH['pkg_version']}  |  "
        f"API: {'OK' if HEALTH['ok'] else 'NO DISPONIBLE'}"
    )

    st.subheader("Filtro geografico")
    filtro_depto = st.selectbox(
        "Departamento",
        options=["Todos"] + DEPTOS_DISPONIBLES,
        index=0,
        help="Aplica a series SPI, LOYO y KPIs de detalle.",
    )

    st.subheader("Rango de anios historicos")
    if len(ANIOS_DISPONIBLES) >= 2:
        anio_ini, anio_fin = st.slider(
            "Anio inicio / Anio fin",
            min_value=int(min(ANIOS_DISPONIBLES)),
            max_value=int(max(ANIOS_DISPONIBLES)),
            value=(int(min(ANIOS_DISPONIBLES)), int(max(ANIOS_DISPONIBLES))),
            step=1,
        )
    else:
        anio_ini = anio_fin = 2007

    st.markdown("---")
    st.subheader("Precarga inputs Track B")
    prec_depto = st.selectbox(
        "Departamento para prediccion",
        options=DEPTOS_DISPONIBLES,
        index=0,
    )
    anios_depto = (
        sorted(PANEL_DF.loc[PANEL_DF["departamento"] == prec_depto, "year"].dropna().astype(int).tolist())
        if not PANEL_DF.empty
        else ANIOS_DISPONIBLES
    )
    prec_anio_default = 2015 if 2015 in anios_depto else (anios_depto[0] if anios_depto else 2015)
    prec_anio = st.selectbox(
        "Anio historico (carga inputs automaticamente)",
        options=anios_depto,
        index=anios_depto.index(prec_anio_default) if anios_depto else 0,
    )
    if st.button("Cargar inputs historicos seleccionados", use_container_width=True):
        if not PANEL_DF.empty:
            mask = (PANEL_DF["departamento"] == prec_depto) & (PANEL_DF["year"].astype(int) == int(prec_anio))
            if mask.any():
                row = PANEL_DF.loc[mask].iloc[0].to_dict()
                for k in [
                    "spi3_floracion", "spi3_desarrollo", "spi3_cosecha",
                    "tmax_mean_e9", "oni_mean", "roya_dummy",
                ]:
                    st.session_state.setdefault("trackb_inputs", {})[k] = row.get(k)
                st.success(f"Cargados inputs de {prec_depto} {prec_anio}.")

    st.markdown("---")
    st.subheader("Parametros calculadora actuarial")
    calc_ha = st.number_input(
        "Hectareas aseguradas", min_value=1.0, max_value=100000.0, value=100.0, step=10.0, format="%.1f"
    )
    calc_pago_ha = st.number_input(
        "Pago indemnizatorio por evento (COP/ha)",
        min_value=0, max_value=10_000_000, value=1_200_000, step=50_000,
    )
    calc_prima_extra = st.slider(
        "Sobrecarga prima adicional (%)", min_value=0, max_value=50, value=5, step=1
    )
    st.caption("Se suma este porcentaje sobre la prima actuarial oficial.")

    st.markdown("---")
    with st.expander("Diagnostico API / metadata"):
        st.write(HEALTH["raw"])
    if st.button("Limpiar cache y recargar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ---------------------------------------------------------------------------
# Filtro de datos (Departamento / anios)
# ---------------------------------------------------------------------------
def _filtrar(df: pd.DataFrame, depto_col: str = "departamento", anio_col: str = "year") -> pd.DataFrame:
    if df.empty:
        return df
    x = df.copy()
    if filtro_depto != "Todos":
        x = x[x[depto_col].astype(str) == str(filtro_depto)]
    if anio_col in x.columns:
        x = x[(x[anio_col].astype(int) >= int(anio_ini)) & (x[anio_col].astype(int) <= int(anio_fin))]
    return x


PANEL_FILT = _filtrar(PANEL_DF)
LOYO_FILT = _filtrar(LOYO_DF)


# ---------------------------------------------------------------------------
# CABECERA PRINCIPAL
# ---------------------------------------------------------------------------
st.title("Seguro Agricola Indexado Cafetero — Panel Ejecutivo")
st.caption(
    "Departamentos: Narino / Quindio    |    Panel historico: "
    f"{anio_ini}-{anio_fin}    |    Pago evento por defecto: 1,200,000 COP/ha "
    "(ajustable en la calculadora de la barra lateral)."
)
st.markdown(
    "Esta herramienta encapsula los modelos oficiales del proyecto Entrega_2 CELL 121 sin modificarlos y los expone para la toma de decisiones. "
    "Los filtros de la izquierda controlan la vista de los modulos siguientes."
)

if not HEALTH["ok"]:
    st.warning(
        "La API local no responde. Modulos de Track B, Validacion y Calculadora actuarial quedan deshabilitados. "
        "Ejecuta run_api.ps1 antes de usar el panel."
    )

# ---------------------------------------------------------------------------
# MODULO 1. KPIs de negocio — Entrega 2, seccion 5.6
# ---------------------------------------------------------------------------
st.markdown("---")
st.header("KPIs de negocio — impacto esperado")
st.caption(
    "Indicadores operativos definidos en la Entrega 2 (seccion 5.6). "
    "Los valores actuales son supuestos/estimaciones declaradas del proyecto y deben validarse con una aseguradora en Fase 3."
)

def _business_kpi_card(col, titulo: str, actual: str, deseado: str, nota: str):
    with col:
        st.metric(titulo, actual)
        st.caption(f"Objetivo: {deseado}")
        st.caption(nota)

def _kpi_card(col, titulo: str, valor: str, nota: str):
    with col:
        st.metric(titulo, valor)
        st.caption(nota)

# Los seis KPI corresponden literalmente al caso de negocio documentado en la Entrega 2.
row1 = st.columns(3, gap="medium")
_business_kpi_card(
    row1[0], "Costo evaluacion tecnica / poliza",
    "$511 mil Q. · $586 mil N.", "$34.100",
    "Construccion por componentes; reduccion esperada del orden de 93-94 %."
)
_business_kpi_card(
    row1[1], "Tiempo de evaluacion tecnica",
    "1 dia de campo / predio", "1 hora de analista",
    "Estimacion profesional del equipo."
)
_business_kpi_card(
    row1[2], "Respuesta de cotizacion",
    "3-4 dias habiles", "4 horas",
    "Estimacion profesional del equipo."
)

row2 = st.columns(3, gap="medium")
_business_kpi_card(
    row2[0], "Prima minima viable",
    "Piso por costo fijo", "Piso ~90 % menor",
    "El artefacto reduce gastos de evaluacion; no modifica la prima de riesgo."
)
_business_kpi_card(
    row2[1], "Fuentes manuales / evaluacion",
    "4", "0",
    "Conteo directo de las fuentes declaradas en el prototipo."
)
_business_kpi_card(
    row2[2], "Consistencia entre analistas",
    "No medida", "Concordancia verificable",
    "La Fase 3 debe definir y aplicar el instrumento de medicion."
)

# Metricas tecnicas canonicas del scoring final de la Entrega 2.
# Se muestran como informacion secundaria, no como KPI de negocio.
with st.expander("Metricas tecnicas del scoring — referencia Entrega 2"):
    tech = pd.DataFrame([
        {"Departamento": "Narino", "Modelo final": "ExtraTrees parametrizado", "RMSE LOYO (kg/ha)": 100.1, "MAE LOYO (kg/ha)": 86.1, "R2 LOYO": 0.114, "Mejora vs baseline": "13.7 %"},
        {"Departamento": "Quindio", "Modelo final": "Random Forest parametrizado", "RMSE LOYO (kg/ha)": 90.5, "MAE LOYO (kg/ha)": 70.4, "R2 LOYO": 0.326, "Mejora vs baseline": "24.7 %"},
    ])
    st.dataframe(tech, use_container_width=True, hide_index=True)
    st.caption(
        "Cifras canonicas del Informe de Implementacion y Experimentos (Entrega 2), obtenidas con validacion LOYO. "
        "No se usan aqui los RMSE holdout 15.1/45.7 del artefacto kpis_resumen.csv porque corresponden a modelos/esquemas distintos."
    )

# ---------------------------------------------------------------------------
# MODULO 2. Track A — Serie SPI-3 fenologica + activaciones por anio
# ---------------------------------------------------------------------------
st.markdown("---")
st.header("Track A — Indice SPI-3 y activaciones por anio")
col_spi, col_act = st.columns([3, 2], gap="large")

with col_spi:
    if not PANEL_FILT.empty:
        plot_df = PANEL_FILT[["departamento", "year",
                              "spi3_floracion", "spi3_desarrollo", "spi3_cosecha"]].copy()
        plot_df["year"] = plot_df["year"].astype(int)
        long_df = plot_df.melt(
            id_vars=["departamento", "year"],
            value_vars=["spi3_floracion", "spi3_desarrollo", "spi3_cosecha"],
            var_name="Fase fenologica",
            value_name="SPI-3",
        )
        if _HAS_PLOTLY:
            fig = px.line(
                long_df, x="year", y="SPI-3", color="Fase fenologica",
                facet_col="departamento" if filtro_depto == "Todos" else None,
                markers=True,
                title=f"Serie SPI-3 fenologico (filtro: {filtro_depto}, anios {anio_ini}-{anio_fin})",
            )
            fig.update_xaxes(dtick=1, title="Anio")
            fig.update_yaxes(title="SPI-3 (desviaciones estandar)")
            if filtro_depto != "Todos" and not UMBRALES_DF.empty:
                row_u = UMBRALES_DF[UMBRALES_DF["departamento"].astype(str) == filtro_depto]
                if not row_u.empty:
                    r0 = row_u.iloc[0]
                    p10 = None
                    for k_p in ("umbral_sequia_p10", "sequia_p10", "p10", "spi3_p10"):
                        try:
                            p10 = float(r0[k_p])
                            break
                        except Exception:  # noqa: BLE001
                            continue
                    p90 = None
                    for k_p in ("umbral_exceso_p90", "exceso_p90", "p90", "spi3_p90"):
                        try:
                            p90 = float(r0[k_p])
                            break
                        except Exception:  # noqa: BLE001
                            continue
                    if p10 is not None:
                        fig.add_hline(y=p10, line_dash="dash", line_color="red",
                                      annotation_text=f"P10 = {p10:.3f}", annotation_position="bottom left")
                    if p90 is not None:
                        fig.add_hline(y=p90, line_dash="dash", line_color="green",
                                      annotation_text=f"P90 = {p90:.3f}", annotation_position="top left")
            fig.update_layout(height=420, legend_orientation="h", legend_y=-0.25)
            st.plotly_chart(fig, use_container_width=True)
        else:
            n_dep = len(sorted(long_df["departamento"].unique()))
            ncols = 2 if (filtro_depto == "Todos" and n_dep >= 2) else 1
            deptos = sorted(long_df["departamento"].unique()) if filtro_depto == "Todos" else [filtro_depto]
            fig_m, axes = plt.subplots(1, ncols, figsize=(6 * ncols, 4), squeeze=False, sharey=True)
            pal = {"spi3_floracion": "#1f77b4", "spi3_desarrollo": "#ff7f0e", "spi3_cosecha": "#2ca02c"}
            for axi, d in enumerate(deptos):
                ax = axes[0][axi]
                sub = long_df[long_df["departamento"] == d].sort_values(["Fase fenologica", "year"])
                for fase, color in pal.items():
                    s2 = sub[sub["Fase fenologica"] == fase]
                    ax.plot(s2["year"], s2["SPI-3"], marker="o", label=fase, color=color, linewidth=2)
                if filtro_depto != "Todos" and not UMBRALES_DF.empty:
                    row_u = UMBRALES_DF[UMBRALES_DF["departamento"].astype(str) == filtro_depto]
                    if not row_u.empty:
                        r0 = row_u.iloc[0]
                        p10 = None
                        for k_p in ("umbral_sequia_p10", "sequia_p10", "p10", "spi3_p10"):
                            try:
                                p10 = float(r0[k_p])
                                break
                            except Exception:  # noqa: BLE001
                                continue
                        p90 = None
                        for k_p in ("umbral_exceso_p90", "exceso_p90", "p90", "spi3_p90"):
                            try:
                                p90 = float(r0[k_p])
                                break
                            except Exception:  # noqa: BLE001
                                continue
                        if p10 is not None:
                            ax.axhline(p10, color="red", linestyle="--", label=f"P10={p10:.2f}")
                        if p90 is not None:
                            ax.axhline(p90, color="green", linestyle="--", label=f"P90={p90:.2f}")
                ax.set_title(f"SPI-3 - {d}")
                ax.set_xlabel("Anio")
                ax.grid(True, alpha=0.3)
                ax.legend(fontsize=7, loc="lower left")
                ax.set_xticks(sorted(long_df["year"].astype(int).unique()))
            axes[0][0].set_ylabel("SPI-3 (desv. estandar)")
            fig_m.suptitle(f"Serie SPI-3 fenologico | {filtro_depto} {anio_ini}-{anio_fin}")
            fig_m.tight_layout()
            st.pyplot(fig_m, clear_figure=True, use_container_width=True)
    else:
        st.info("No hay datos historicos para mostrar en SPI-3.")

with col_act:
    st.subheader("Activaciones Track A por anio (regla 5-OR)")
    if not PANEL_FILT.empty and UMBRALES:
        UMB_D = {u["departamento"]: u for u in UMBRALES}
        rows = []
        for _, r in PANEL_FILT.iterrows():
            d = str(r.get("departamento"))
            if d not in UMB_D:
                continue
            r_dict = r.to_dict()
            spi3_min_val = r_dict.get("spi3_min")
            payload = {
                "spi_min_annual": spi3_min_val,
                "spi_min_e9": spi3_min_val,
                "spi3_cosecha": r_dict.get("spi3_cosecha"),
                "n_sequia_e9": r_dict.get("n_sequia_e9"),
                "roya_shock": r_dict.get("roya_shock"),
                "roya_dummy": r_dict.get("roya_dummy"),
                "departamento": d,
            }
            umb_d = UMB_D[d]
            p10d = float(
                umb_d.get("umbral_sequia_p10")
                or umb_d.get("sequia_p10")
                or umb_d.get("p10")
                or -999
            )
            def seq(v):
                return (v is not None) and (float(v) <= p10d)
            c1 = seq(payload.get("spi_min_annual"))
            c2 = seq(payload.get("spi_min_e9"))
            c3 = seq(payload.get("spi3_cosecha"))
            try: c4 = int(payload.get("n_sequia_e9") or 0) >= 2
            except Exception: c4 = False
            try: c5 = (int(payload.get("roya_shock") or 0) == 1) or (int(payload.get("roya_dummy") or 0) == 1)
            except Exception: c5 = False
            reglas = []
            if c1: reglas.append("C1")
            if c2: reglas.append("C2")
            if c3: reglas.append("C3")
            if c4: reglas.append("C4")
            if c5: reglas.append("C5")
            activo = any([c1, c2, c3, c4, c5])
            rows.append({
                "Departamento": d,
                "Anio": int(r.get("year")),
                "Activa": "SI" if activo else "NO",
                "Regla": ",".join(reglas) if reglas else "—",
            })
        tbl = pd.DataFrame(rows).sort_values(["Departamento", "Anio"])
        st.dataframe(tbl, use_container_width=True, hide_index=True, height=420)
        st.caption(
            "Reglas: C1=min_anual<P10, C2=min_e9<P10, C3=cosecha<P10, "
            "C4=n_sequia_e9>=2, C5=roya_shock=1 OR roya_dummy=1. "
            "Activa SI indica un anio climaticamente exigente; no constituye disparo de pago. "
            "La regla activa en la mayoria de los anios del panel (6 de 12 en Narino, 9 de 12 en Quindio), "
            "por lo que tiene alta tasa de falsas alarmas. Ver manual de usuario, advertencia 8."
        )
    else:
        st.info("Sin datos suficientes para generar tabla de activaciones.")


# ---------------------------------------------------------------------------
# MODULO 3. Track B — Formulario prediccion rendimiento
# ---------------------------------------------------------------------------
st.markdown("---")
st.header("Track B — Prediccion rendimiento (kg/ha)")
st.info(
    "Alcance de la senal: mide exposicion climatica. No cubre choques "
    "fitosanitarios como la roya, ni calcula prima o trigger de pago. "
    "La decision de suscripcion es del analista."
)
col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.subheader("Inputs fenologicos")
    st.caption(
        "Valores: SPI/ONI en rango [-5,5] tipico; tmax_mean_e9 en Celsius (10-40); "
        "roya_dummy en {0,1}. Usa el boton 'Cargar inputs historicos' en la barra lateral."
    )
    default_inputs = st.session_state.get("trackb_inputs", {}) or {}
    with st.form("trackb_form", clear_on_submit=False):
        f_flor = st.number_input("spi3_floracion", value=float(default_inputs.get("spi3_floracion") or 0.0), step=0.01, format="%.4f")
        f_des =  st.number_input("spi3_desarrollo", value=float(default_inputs.get("spi3_desarrollo") or 0.0), step=0.01, format="%.4f")
        f_cos =  st.number_input("spi3_cosecha",    value=float(default_inputs.get("spi3_cosecha") or 0.0), step=0.01, format="%.4f")
        f_tmax = st.number_input("tmax_mean_e9 (C)",   value=float(default_inputs.get("tmax_mean_e9") or 21.0), step=0.1,  format="%.2f")
        f_oni =  st.number_input("oni_mean",           value=float(default_inputs.get("oni_mean") or 0.0), step=0.01, format="%.4f")
        f_roya = st.selectbox("roya_dummy", options=[0, 1], index=int(default_inputs.get("roya_dummy") or 0))
        submitted = st.form_submit_button("Calcular prediccion", use_container_width=True, disabled=(not HEALTH["ok"]))

    features_payload = {
        "spi3_floracion": f_flor,
        "spi3_desarrollo": f_des,
        "spi3_cosecha": f_cos,
        "tmax_mean_e9": f_tmax,
        "oni_mean": f_oni,
        "roya_dummy": int(f_roya),
    }

with col_out:
    st.subheader("Resultado")
    if not HEALTH["ok"]:
        st.warning("API no disponible.")
    elif submitted:
        with st.spinner("Calculando prediccion de rendimiento ..."):
            body_rend = {"departamento": prec_depto}
            for k, v in features_payload.items():
                body_rend[k] = v
            resp = _api_post("/api/v1/predict/rendimiento", body_rend)
        if resp:
            valor = _safe(resp, "prediccion_kg_ha")
            rango_baixo, rango_altoo = 900, 1200
            # Benchmarks propios por departamento (mediana historica PANEL_FILT)
            bm_panel = PANEL_FILT.copy()
            if "rendimiento_kg_ha" in bm_panel.columns:
                bm_d = bm_panel[bm_panel["departamento"].astype(str) == str(prec_depto)]
                if not bm_d.empty:
                    series_r = pd.to_numeric(bm_d["rendimiento_kg_ha"], errors="coerce").dropna()
                    if len(series_r) >= 3:
                        q1 = float(series_r.quantile(0.25))
                        q2 = float(series_r.quantile(0.50))
                        q3 = float(series_r.quantile(0.75))
                        rango_baixo = q1
                        rango_altoo = q3
            try:
                v_num = float(valor)
                if v_num < rango_baixo:
                    nivel, color = "RENDIMIENTO BAJO", "#d62728"
                elif v_num <= rango_altoo:
                    nivel, color = "RENDIMIENTO MEDIO", "#ff7f0e"
                else:
                    nivel, color = "RENDIMIENTO ALTO", "#2ca02c"
            except Exception:  # noqa: BLE001
                nivel, color = "INDETERMINADO", "#7f7f7f"
            col_p, col_s = st.columns([3, 2])
            with col_p:
                st.metric(
                    f"Rendimiento estimado - {prec_depto}",
                    _fmt_num(valor, 1, " kg/ha"),
                )
            with col_s:
                _html_semaforo = f"""
                <div style="border:2px solid {color};border-radius:14px;padding:14px 16px;background-color:rgba(255,255,255,0.02);">
                  <div style="font-size:11px;color:#555555;letter-spacing:0.5px;">RENDIMIENTO ESPERADO (vs historico depto)</div>
                  <div style="font-size:30px;font-weight:800;color:{color};margin-top:4px;letter-spacing:1px;">{nivel}</div>
                  <div style="font-size:11px;color:#666666;margin-top:8px;">
                    Q1 hist. = {rango_baixo:.0f} kg/ha · Q3 hist. = {rango_altoo:.0f} kg/ha
                  </div>
                </div>
                """
                st.markdown(_html_semaforo, unsafe_allow_html=True)
            with st.expander("Detalle tecnico de la prediccion"):
                st.write({
                    "departamento": _safe(resp, "departamento"),
                    "validaciones": _safe(resp, "validaciones"),
                    "warnings": _safe(resp, "warnings"),
                    "timestamp": _safe(resp, "timestamp"),
                    "benchmark_hist": {
                        "departamento": prec_depto,
                        "Q1_kg_ha": round(rango_baixo, 1),
                        "Q3_kg_ha": round(rango_altoo, 1),
                    }
                })
    else:
        st.info("Carga inputs historicos en el sidebar o digita manualmente y pulsa Calcular prediccion.")


# ---------------------------------------------------------------------------
# MODULO 4. Track B — LOYO Pred vs Real
# ---------------------------------------------------------------------------
st.markdown("---")
st.header("Track B — Validacion Leave-One-Year-Out (prediccion vs real)")
col_loyo_fig, col_loyo_met = st.columns([3, 1], gap="large")

with col_loyo_fig:
    if not LOYO_FILT.empty:
        loyo_plot = LOYO_FILT.copy()
        loyo_plot["year"] = loyo_plot["year"].astype(int)
        deptos_loyo = sorted(loyo_plot["departamento"].unique())
        pal = {"Narino": "#1f77b4", "Quindio": "#ff7f0e"}
        if _HAS_PLOTLY:
            fig = go.Figure()
            for d in deptos_loyo:
                sub = loyo_plot[loyo_plot["departamento"] == d].sort_values("year")
                fig.add_trace(go.Scatter(
                    x=sub["year"], y=sub["rendimiento_real_kg_ha"], mode="lines+markers",
                    name=f"Real {d}", line=dict(color=pal.get(d, None), width=3),
                ))
                fig.add_trace(go.Scatter(
                    x=sub["year"], y=sub["rendimiento_predicho_kg_ha"], mode="lines+markers",
                    name=f"Predicho LOYO {d}", line=dict(dash="dot", color=pal.get(d, None), width=2),
                ))
            fig.update_layout(
                title=f"Rendimiento real vs predicho LOYO ({filtro_depto}, {anio_ini}-{anio_fin})",
                xaxis_title="Anio", yaxis_title="kg/ha",
                height=420, legend_orientation="h", legend_y=-0.3,
            )
            fig.update_xaxes(dtick=1)
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig_m, ax = plt.subplots(figsize=(9, 4.5))
            for d in deptos_loyo:
                sub = loyo_plot[loyo_plot["departamento"] == d].sort_values("year")
                color = pal.get(d, None)
                ax.plot(sub["year"], sub["rendimiento_real_kg_ha"],
                        marker="o", label=f"Real {d}", color=color, linewidth=3)
                ax.plot(sub["year"], sub["rendimiento_predicho_kg_ha"],
                        marker="s", label=f"Predicho LOYO {d}", linestyle=":",
                        color=color, linewidth=2)
            ax.set_title(f"Rendimiento real vs predicho LOYO ({filtro_depto}, {anio_ini}-{anio_fin})")
            ax.set_xlabel("Anio")
            ax.set_ylabel("kg/ha")
            ax.set_xticks(sorted(loyo_plot["year"].unique().astype(int).tolist()))
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=8, loc="lower left")
            fig_m.tight_layout()
            st.pyplot(fig_m, clear_figure=True, use_container_width=True)
    else:
        st.info("Sin datos LOYO para mostrar.")

with col_loyo_met:
    st.subheader("Metricas resumen LOYO")
    if not LOYO_FILT.empty:
        rows_m = []
        for d in (sorted(LOYO_FILT["departamento"].unique())
                  if filtro_depto == "Todos" else [filtro_depto]):
            sub = LOYO_FILT[LOYO_FILT["departamento"] == d]
            if sub.empty: continue
            err = sub["rendimiento_predicho_kg_ha"] - sub["rendimiento_real_kg_ha"]
            rmse = float((err ** 2).mean() ** 0.5)
            mae = float(err.abs().mean())
            sesgo = float(err.mean())
            rows_m.append({
                "Departamento": d,
                "RMSE LOYO": _fmt_num(rmse, 1),
                "MAE LOYO": _fmt_num(mae, 1),
                "Sesgo medio": _fmt_num(sesgo, 2),
            })
        st.dataframe(pd.DataFrame(rows_m), use_container_width=True, hide_index=True)
        st.caption(
            "Calculado sobre el archivo de validacion del artefacto, que contiene varias corridas por anio. "
            "Las metricas oficiales del modelo (RMSE 100.1 kg/ha en Narino y 90.5 kg/ha en Quindio) "
            "son las del bloque Metricas tecnicas del scoring y las del reporte tecnico de experimentos."
        )
    else:
        st.info("Sin metricas.")


# ---------------------------------------------------------------------------
# MODULO 5. Validacion historica N=2
# ---------------------------------------------------------------------------
st.markdown("---")
st.header("Validacion historica — Eventos 2012 (Roya) y 2015 (El Nino)")

if not VALHIST_DF.empty:
    with st.expander("Fuente primaria de eventos"):
        st.dataframe(VALHIST_DF, use_container_width=True, hide_index=True, height=170)

st.subheader("Panel de cumplimiento")

def _reproduccion_en_vivo() -> pd.DataFrame:
    if PANEL_DF.empty or not HEALTH["ok"]:
        return pd.DataFrame()
    eventos = [
        ("Narino", 2012, "Roya 2012"),
        ("Narino", 2015, "El Nino 2015"),
        ("Quindio", 2012, "Roya 2012"),
        ("Quindio", 2015, "El Nino 2015"),
    ]
    rows = []
    panel_cols = set(PANEL_DF.columns.tolist())
    for d, anio, evento in eventos:
        mask = (PANEL_DF["departamento"] == d) & (PANEL_DF["year"].astype(int) == int(anio))
        if not mask.any():
            continue
        row = PANEL_DF.loc[mask].iloc[0].to_dict()
        feats_keys = [
            "spi3_floracion", "spi3_desarrollo", "spi3_cosecha",
            "tmax_mean_e9", "oni_mean", "roya_dummy",
        ]
        body_rend = {"departamento": d}
        for k in feats_keys:
            v = row.get(k)
            if v is None:
                continue
            if k == "roya_dummy":
                try:
                    body_rend[k] = int(v)
                except Exception:  # noqa: BLE001
                    body_rend[k] = 0
            else:
                try:
                    body_rend[k] = float(v)
                except Exception:  # noqa: BLE001
                    pass
        r_b = _api_post("/api/v1/predict/rendimiento", body_rend, _silent=True)
        t_a_payload = {
            "spi_min_annual": row.get("spi3_min"),
            "spi_min_e9": row.get("spi3_min"),
            "spi3_cosecha": row.get("spi3_cosecha"),
            "n_sequia_e9": int(row.get("n_sequia_e9") or 0),
            "roya_shock": int(row.get("roya_shock") or 0),
            "roya_dummy": int(row.get("roya_dummy") or 0),
        }
        # Si alguna key es None y la API no lo permite, omitirla (TypedDict total=False)
        t_a_clean = {k: v for k, v in t_a_payload.items() if v is not None}
        r_a = _api_post(f"/api/v1/track-a/activacion/{d}", t_a_clean, _silent=True)
        if "activo" in (r_a or {}):
            # API oficial: key "activo" (schema ActivacionSPIOutput)
            act_bool = bool(_safe(r_a, "activo"))
            regla = _safe(r_a, "regla_activada") or _safe(r_a, "regla_activacion") or "—"
        else:
            # fallback: compatibilidad antigua
            act_bool = True if _safe(r_a, "seguro_activo") in (True, "SI", 1) else False
            regla = _safe(r_a, "regla_activacion", default="—")
        # Esperado: para los 4 eventos historicos 2012/2015 en Narino/Quindio: activo=True (SI)
        esperado = True  # segun VALHIST_DF: seguro_activo="SI"
        cumple = (
            "CUMPLE" if (act_bool == esperado)
            else ("NO CUMPLE" if act_bool != esperado else "INDETERMINADO")
        )
        rows.append({
            "Departamento": d,
            "Anio": anio,
            "Evento": evento,
            "Track B (kg/ha)": _fmt_num(_safe(r_b, "prediccion_kg_ha"), 1, ""),
            "Track A activo?": "SI" if act_bool else "NO",
            "Regla Track A": regla,
            "Cumplimiento esperado?": cumple,
        })
    return pd.DataFrame(rows)

vh_df = _reproduccion_en_vivo()
if not vh_df.empty:
    # Semaforo de colores
    def _colorear(v):
        cls = ""
        if isinstance(v, str):
            if "CUMPLE" in v and "NO" not in v:
                cls = 'style="background-color:#d4edda;color:#0f5132;font-weight:700;"'
            elif "NO CUMPLE" in v:
                cls = 'style="background-color:#f8d7da;color:#842029;font-weight:700;"'
            elif v == "SI":
                cls = 'style="color:#b45f06;font-weight:700;"'
        return cls

    headers = list(vh_df.columns)
    thead = "".join(f"<th>{c}</th>" for c in headers)
    rows_html = ""
    for _, r in vh_df.iterrows():
        cells = ""
        for c in headers:
            cls_attr = _colorear(r[c])
            cells += f"<td {cls_attr}>{r[c]}</td>"
        rows_html += f"<tr>{cells}</tr>"
    style = """<style>
    table.valhist {border-collapse:collapse;width:100%;font-family:system-ui;font-size:14px;}
    table.valhist th {background:#f1f3f5;padding:10px;border:1px solid #dee2e6;text-align:left;}
    table.valhist td {padding:8px 10px;border:1px solid #dee2e6;}
    table.valhist tr:nth-child(even) td {background:#fafbfc;}
    </style>"""
    tabla_html = f"""{style}<table class=\"valhist\"><thead><tr>{thead}</tr></thead><tbody>{rows_html}</tbody></table>"""
    st.markdown(tabla_html, unsafe_allow_html=True)
    total = len(vh_df)
    ok = sum(1 for x in vh_df["Cumplimiento esperado?"].astype(str) if "CUMPLE" in x and "NO" not in x)
    pct = (ok / total * 100.0) if total else 0.0
    st.write(f"Cumplimiento global: {ok}/{total} ({pct:.1f} %).")
else:
    st.info("Sin API o sin panel historico no se puede reproducir validacion N=2.")


# ---------------------------------------------------------------------------
# MODULO 6. Calculadora actuarial (12 anios, prima vs indemnizacion)
# ---------------------------------------------------------------------------
st.markdown("---")
st.header("Calculadora actuarial — ejercicio exploratorio")
st.caption(
    "Modulo exploratorio, fuera del alcance comprometido en la tabla de "
    "requerimientos de la Fase 1. El artefacto no calcula prima ni define "
    "trigger de pago: las cifras de este modulo son ilustrativas y no "
    "constituyen una tarifa actuarial validada."
)

st.caption(
    f"Parametros actuales: {_fmt_num(calc_ha, 1, ' ha')}  |  "
    f"pago/evento = $ {_fmt_num(calc_pago_ha, 0, ' COP/ha')}  |  "
    f"sobrecarga prima adicional = {calc_prima_extra:.0f} %. "
    "Cambia estos valores en la barra lateral."
)

TABLA_ACT_CALC = None
FIG_CALC = None
RESUMEN_CALC = None

if not PANEL_DF.empty and not UMBRALES_DF.empty and HEALTH["ok"]:
    UMB_D = {u["departamento"]: u for u in UMBRALES}
    # Tabla anual global (Todos) o por depto: 12 anios x 2 deptos o 12 x 1
    anios_rango_full = list(range(int(min(ANIOS_DISPONIBLES)), int(max(ANIOS_DISPONIBLES)) + 1))
    rows_calc = []
    deptos_loop = DEPTOS_DISPONIBLES if filtro_depto == "Todos" else [filtro_depto]
    # Sumas por anio (agrupa deptos)
    for y in anios_rango_full:
        if not (anio_ini <= y <= anio_fin):
            continue
        eventos_anio = 0
        prima_anio = 0.0
        for d in deptos_loop:
            # Frecuencia oficial del depto -> prima por ha
            frac_prima = _prima_of(d)
            if frac_prima is None:
                frac_prima = 0.0
            # El valor _prima_of puede ser pct (6.36) o fraccion (0.0636)
            if isinstance(frac_prima, (int, float)) and abs(float(frac_prima)) > 1.5:
                frac_prima = float(frac_prima) / 100.0
            frac_prima_total = float(frac_prima) * (1 + float(calc_prima_extra) / 100.0)
            # Pero: cada depto agrega su prima y sus eventos independientes (suma total)
            prima_anio += (frac_prima_total * float(calc_pago_ha) * float(calc_ha)) / len(deptos_loop)
            # Contamos evento (activo?) para el depto/anio
            mask = (PANEL_DF["departamento"] == d) & (PANEL_DF["year"].astype(int) == y)
            if not mask.any():
                continue
            row = PANEL_DF.loc[mask].iloc[0].to_dict()
            if d in UMB_D:
                u = UMB_D[d]
                p10d = float(
                    u.get("umbral_sequia_p10")
                    or u.get("sequia_p10")
                    or u.get("p10")
                    or -999
                )
                def _s(v):
                    try: return (v is not None) and (float(v) <= p10d)
                    except Exception: return False
                spi3_min_val = row.get("spi3_min")
                c1 = _s(spi3_min_val)
                c2 = _s(spi3_min_val)
                c3 = _s(row.get("spi3_cosecha"))
                try: c4 = int(row.get("n_sequia_e9") or 0) >= 2
                except Exception: c4 = False
                try: c5 = (int(row.get("roya_shock") or 0) == 1) or (int(row.get("roya_dummy") or 0) == 1)
                except Exception: c5 = False
                if any([c1, c2, c3, c4, c5]):
                    eventos_anio += 1
        indemnizacion = eventos_anio * (float(calc_pago_ha) * float(calc_ha)) / len(deptos_loop)
        rows_calc.append({
            "Anio": y,
            "Prima cobrada (COP)": round(prima_anio, 0),
            "Indemnizacion pagada (COP)": round(indemnizacion, 0),
            "N eventos": eventos_anio,
        })
    TABLA_ACT_CALC = pd.DataFrame(rows_calc)
    if not TABLA_ACT_CALC.empty:
        TABLA_ACT_CALC["Balance anual (COP)"] = (
            TABLA_ACT_CALC["Prima cobrada (COP)"] - TABLA_ACT_CALC["Indemnizacion pagada (COP)"]
        )
        total_prima = float(TABLA_ACT_CALC["Prima cobrada (COP)"].sum())
        total_indem = float(TABLA_ACT_CALC["Indemnizacion pagada (COP)"].sum())
        balance = total_prima - total_indem
        total_eventos = int(TABLA_ACT_CALC["N eventos"].sum())
        RESUMEN_CALC = {
            "prima_ha_anual_prom_COP": (total_prima / (len(anios_rango_full) * calc_ha)) if calc_ha else 0.0,
            "total_prima_12anios_COP": total_prima,
            "total_indem_12anios_COP": total_indem,
            "balance_12anios_COP": balance,
            "eventos_totales_periodo": total_eventos,
        }
        # Figura barras agrupadas
        if _HAS_PLOTLY:
            long_calc = TABLA_ACT_CALC[["Anio", "Prima cobrada (COP)", "Indemnizacion pagada (COP)"]].melt(
                id_vars=["Anio"], var_name="Concepto", value_name="COP"
            )
            FIG_CALC = px.bar(
                long_calc, x="Anio", y="COP", color="Concepto", barmode="group",
                title=f"Prima vs Indemnizacion por anio ({filtro_depto}, {anio_ini}-{anio_fin})",
            )
            FIG_CALC.update_layout(height=460, legend_orientation="h", legend_y=-0.25)
            FIG_CALC.update_xaxes(dtick=1)
        else:
            anios_list = TABLA_ACT_CALC["Anio"].astype(int).tolist()
            x = list(range(len(anios_list)))
            width = 0.38
            fig_m, ax = plt.subplots(figsize=(10, 4.8))
            bars_prima = [float(v) for v in TABLA_ACT_CALC["Prima cobrada (COP)"].tolist()]
            bars_indem = [float(v) for v in TABLA_ACT_CALC["Indemnizacion pagada (COP)"].tolist()]
            ax.bar([i - width/2 for i in x], bars_prima, width=width, label="Prima cobrada (COP)", color="#1f77b4")
            ax.bar([i + width/2 for i in x], bars_indem, width=width, label="Indemnizacion pagada (COP)", color="#d62728")
            ax.set_xticks(x, labels=[str(a) for a in anios_list], rotation=45, ha="right")
            ax.set_title(f"Prima vs Indemnizacion por anio ({filtro_depto}, {anio_ini}-{anio_fin})")
            ax.set_xlabel("Anio")
            ax.set_ylabel("COP")
            try:
                from matplotlib.ticker import FuncFormatter
                ax.yaxis.set_major_formatter(FuncFormatter(lambda z, _pos: f"${z/1_000_000:.1f}M"))
            except Exception:  # noqa: BLE001
                pass
            ax.grid(True, axis="y", alpha=0.3)
            ax.legend(fontsize=8, loc="upper right")
            fig_m.tight_layout()
            FIG_CALC = fig_m

if RESUMEN_CALC:
    rc1, rc2, rc3, rc4, rc5 = st.columns(5, gap="medium")
    _kpi_card(rc1, "Prima / ha / anio",
              f"$ {_fmt_num(RESUMEN_CALC['prima_ha_anual_prom_COP'], 0, ' COP')}",
              "Promedio periodo prima cobrada por hectarea anual.")
    _kpi_card(rc2, f"Total prima {anio_ini}-{anio_fin}",
              f"$ {_fmt_num(RESUMEN_CALC['total_prima_12anios_COP'], 0)}",
              "Suma del periodo (prima cobrada).")
    _kpi_card(rc3, f"Total indemnizacion {anio_ini}-{anio_fin}",
              f"$ {_fmt_num(RESUMEN_CALC['total_indem_12anios_COP'], 0)}",
              "Pagos por eventos activos en el periodo.")
    _kpi_card(rc4, "Balance periodo",
              f"$ {_fmt_num(RESUMEN_CALC['balance_12anios_COP'], 0)}",
              "Positivo = superavit prima; negativo = deficit.")
    _kpi_card(rc5, "Eventos activados (periodo)",
              f"{int(RESUMEN_CALC['eventos_totales_periodo'])} eventos",
              "Numero de anios/deptos que activaron el seguro en el filtro actual.")

if FIG_CALC is not None:
    if _HAS_PLOTLY:
        st.plotly_chart(FIG_CALC, use_container_width=True)
    else:
        st.pyplot(FIG_CALC, clear_figure=True, use_container_width=True)

if TABLA_ACT_CALC is not None and not TABLA_ACT_CALC.empty:
    st.subheader("Detalle anual")
    st.dataframe(TABLA_ACT_CALC, use_container_width=True, hide_index=True, height=320)
    st.caption(
        "La prima por anio se calcula como Prima Actuarial oficial (depto) + sobrecarga parametrizada, "
        "multiplicada por pago evento y hectareas. Indemnizacion = eventos * pago/ha * ha."
    )
else:
    st.info("No hay datos suficientes para la calculadora actuarial (requiere panel, umbrales y API activa).")

# ---------------------------------------------------------------------------
# Pie de pagina
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  "
    f"Package: {HEALTH['pkg_name']} v{HEALTH['pkg_version']}  |  "
    f"API local: {API_BASE}  |  Modelos: {', '.join(HEALTH['models']) or '—'}."
)
