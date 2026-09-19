"""
T3. Tests Track A SPI activación + KPIs actuariales.
"""

from __future__ import annotations

import pytest

import cafe_sai_modelos_equipo9 as pkg


def test_predict_activacion_spi_regla_sequia_p10_narino():
    # Nariño P10 ~ -1.7071. Mandar spi_min_e9 < P10, debería activar.
    out = pkg.predict_activacion_spi(
        "Narino",
        {"spi_min_e9": -2.0, "roya_dummy": 1},
    )
    assert out["departamento"] == "Narino"
    assert out["status"] == "success"
    assert out["activo"] is True
    assert out["pago_cop_ha"] == pkg.schemas.PAGO_POR_EVENTO_COP_HA
    assert out["umbral_sequia_p10"] == pytest.approx(-1.7071, abs=0.05)


def test_predict_activacion_spi_regla_roya_shock():
    # Roya shock activa (C5). No hay sequías fuertes.
    out = pkg.predict_activacion_spi(
        "Quindio",
        {"spi3_cosecha": -0.2, "roya_shock": 1},
    )
    assert out["activo"] is True
    assert out["regla_activada"] is not None


def test_predict_activacion_spi_no_activa():
    out = pkg.predict_activacion_spi(
        "Narino",
        {"spi3_cosecha": 0.5, "roya_shock": 0, "spi_min_annual": -0.5, "spi_min_e9": -0.5},
    )
    assert out["status"] == "success"
    assert out["activo"] is False
    assert out["regla_activada"] is None


def test_kpis_actuariales_valores_oficiales():
    """Valores exactos según kpis_resumen.csv/Entrega_2."""
    k = pkg.get_kpis_actuariales()
    assert set(k.keys()) == {"Narino", "Quindio"}
    assert float(k["Narino"]["rmse_holdout_mejor"]) == pytest.approx(15.1, abs=0.05)
    assert float(k["Narino"]["HE_Ederington"]) == pytest.approx(0.05, abs=0.005)
    assert float(k["Narino"]["prima_actuarial_pct"]) == pytest.approx(0.0636, abs=0.001)
    assert float(k["Narino"]["riesgo_base_pct"]) == pytest.approx(0.4736, abs=0.002)
    assert float(k["Quindio"]["rmse_holdout_mejor"]) == pytest.approx(45.7, abs=0.1)
    assert float(k["Quindio"]["HE_Ederington"]) == pytest.approx(0.11, abs=0.005)
    assert float(k["Quindio"]["prima_actuarial_pct"]) == pytest.approx(0.1015, abs=0.002)
    assert float(k["Quindio"]["riesgo_base_pct"]) == pytest.approx(0.4671, abs=0.002)


def test_validacion_historica_n1_cumple_todos():
    v = pkg.get_validacion_historica_n1()
    # Al menos 4 filas: 2 años × 2 deptos
    assert len(v) == 4
    col_cumple = [c for c in v.columns if c.lower().startswith("cumpl") or "cumple" in c.lower()]
    if col_cumple:
        todos_ok = v[col_cumple[0]].astype(str).str.lower().isin(["si", "true", "1", "ok", "cumple", "yes"])
        assert todos_ok.all(), f"Validación histórica no cumple en: {v[~todos_ok].to_dict('records')}"
    else:
        # Fallback: columnas "activa_esperado" vs "activa_obtenido"
        cols = list(v.columns)
        esp = [c for c in cols if "esperad" in c.lower()]
        obt = [c for c in cols if "obtenid" in c.lower()]
        if esp and obt:
            match = v[esp[0]].astype(str).str.lower() == v[obt[0]].astype(str).str.lower()
            assert match.all(), f"Mismatch validación: {(~match).sum()} filas"


def test_pred_vs_real_loyo_shapes():
    l = pkg.get_pred_vs_real_loyo()
    # 12 años × 2 deptos = 24 pero el CSV oficial en Entrega_2 es (160, 5) por loyo 12 fold × cols.
    assert l.shape[0] >= 24
    assert l.shape[1] >= 2
