"""
KPIs oficiales desde los CSVs de referencia ya calculados en Fase 2/Entrega_2.

NO recalculamos nada: solo exponemos el output oficial del pipeline para el
dashboard. Esto cumple regla #1 (no modificar lógica estadística).
"""

from __future__ import annotations

import pandas as pd

from .loader import load_reference_csv
from .schemas import Departamento, KPIActuarialDepto, PAGO_POR_EVENTO_COP_HA

DEPARTAMENTOS_SET: set[str] = {"Narino", "Quindio"}


def _normalizar_col(col: str) -> str:
    return (
        col.strip().lower().replace(" ", "_").replace("%", "pct").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    )


def _kpis_df() -> pd.DataFrame:
    df = load_reference_csv("kpis")
    df.columns = [_normalizar_col(c) for c in df.columns]
    return df


def _umbrales_df() -> pd.DataFrame:
    df = load_reference_csv("umbrales")
    df.columns = [_normalizar_col(c) for c in df.columns]
    return df


def _df_to_rows(df: pd.DataFrame) -> list[dict]:
    cols = df.columns.tolist()
    return [dict(zip(cols, r)) for r in df.to_dict(orient="split")["data"]]


def get_kpis_track_b() -> dict[Departamento, dict]:
    """
    KPIs de rendimiento predicho (Track B): RMSE holdout, etc.
    Fuente: kpis_resumen.csv oficial. Formato LONG, con columna kpi.
    Devuelve tanto rows por departamento como un dict kpi->valor.
    """
    df = _kpis_df()
    rows_all = _df_to_rows(df)
    out: dict[Departamento, dict] = {}
    depto_col = next(c for c in df.columns if c.startswith("departamento"))
    for d in ("Narino", "Quindio"):
        rows = [r for r in rows_all if r.get(depto_col) == d]
        out[d] = {
            "_rows": rows,
            **{
                _normalizar_col(str(r["kpi"])): r["valor"]
                for r in rows
                if "kpi" in r and "valor" in r and r["kpi"] is not None
            },
        }
    # Cachear rows para actuariales
    global _KB_ROWS_CACHE  # noqa: PLW0603
    _KB_ROWS_CACHE = rows_all
    return out


_KB_ROWS_CACHE: list[dict] | None = None
_KA_ROWS_CACHE: list[dict] | None = None


def get_kpis_track_a() -> dict[Departamento, dict]:
    """
    Umbrales P10/P90 y pct_total_activacion por departamento.
    Fuente: umbrales_departamento.csv oficial. Formato WIDE (1 fila depto).
    """
    df = _umbrales_df()
    rows_all = _df_to_rows(df)
    out: dict[Departamento, dict] = {}
    depto_col = next(c for c in df.columns if c.startswith("departamento"))
    for r in rows_all:
        d = r.get(depto_col)
        if d not in DEPARTAMENTOS_SET:
            continue
        base = {
            k: (None if (isinstance(v, float) and pd.isna(v)) else v)
            for k, v in r.items()
            if k != depto_col
        }
        # Aliases (backwards compat + nombres semánticos)
        p10 = base.get("umbral_sequia_p10")
        p90 = base.get("umbral_exceso_p90")
        if p10 is not None:
            base.setdefault("sequia_p10", p10)
            base.setdefault("p10", p10)
        if p90 is not None:
            base.setdefault("exceso_p90", p90)
            base.setdefault("p90", p90)
        pct = base.get("pct_total_activacion")
        if pct is not None:
            base.setdefault("pct_activacion_ann", pct)
            base.setdefault("frecuencia_pct", pct)
        out[d] = base
    global _KA_ROWS_CACHE  # noqa: PLW0603
    _KA_ROWS_CACHE = rows_all
    return out


def get_kpis_actuariales() -> dict[Departamento, KPIActuarialDepto]:
    """
    KPIs actuariales consolidados por departamento: HE, riesgo_base, prima,
    frecuencia, rmse, pago evento, pct activación.

    Fuentes únicas: kpis_resumen.csv (LONG) + umbrales_departamento.csv (WIDE).
    """
    kb = get_kpis_track_b()
    ka = get_kpis_track_a()
    kb_rows = list(_KB_ROWS_CACHE or [])
    ka_rows = list(_KA_ROWS_CACHE or [])
    out: dict[Departamento, KPIActuarialDepto] = {}
    for depto in ("Narino", "Quindio"):
        d: Departamento = depto  # type: ignore[assignment]
        # KPIs están en formato LONG: (departamento, track, kpi, valor, modelo)
        kpi_rows_b = [
            r for r in kb_rows if r.get("departamento") == d
        ]
        kpi_rows_a = [
            r for r in ka_rows if r.get("departamento") == d
        ]
        kpi_by_name: dict[str, float] = {}
        for r in kpi_rows_b + kpi_rows_a:
            k_raw = r.get("kpi")
            v = r.get("valor")
            if (
                k_raw is None
                or v is None
                or (isinstance(v, float) and pd.isna(v))
            ):
                continue
            k_norm = _normalizar_col(str(k_raw))
            try:
                kpi_by_name[k_norm] = float(v)
            except Exception:  # noqa: BLE001
                continue
        rmse = kpi_by_name.get("rmse_holdout_best")
        he = kpi_by_name.get("he_varianza")
        rb = kpi_by_name.get("riesgo_base")
        prima = kpi_by_name.get("prima_act")
        pct_act = kpi_by_name.get("pct_activacion_total", ka.get(d, {}).get("pct_total_activacion"))
        frec = kpi_by_name.get("frec_act_pct", pct_act)  # fallback a % total activación

        # Valores oficiales del CSV están en PORCENTAJE (ej. 6.36% → 6.36). Convertimos
        # a fracción (0.0636) para consistencia con la API actuarial (0-1).
        def _as_fraction(x: float | None) -> float | None:
            if x is None:
                return None
            try:
                fx = float(x)
            except Exception:  # noqa: BLE001
                return None
            return None if pd.isna(fx) else (fx / 100.0 if abs(fx) > 1.0 else fx)

        out[d] = {
            "departamento": d,
            "HE_Ederington": _as_fraction(he) if he is not None else None,
            "riesgo_base_pct": _as_fraction(rb),
            "prima_actuarial_pct": _as_fraction(prima),
            "frecuencia_activacion_pct": _as_fraction(frec),
            "rmse_holdout_mejor": rmse,
            "pago_cop_ha": PAGO_POR_EVENTO_COP_HA,
            "pct_total_activacion": _as_fraction(pct_act),
        }
    return out


def list_kpis_available() -> dict[str, list[str]]:
    return {
        "kpis_cols": sorted(_kpis_df().columns.tolist()),
        "umbrales_cols": sorted(_umbrales_df().columns.tolist()),
    }


__all__ = [
    "get_kpis_track_b",
    "get_kpis_track_a",
    "get_kpis_actuariales",
    "list_kpis_available",
]
