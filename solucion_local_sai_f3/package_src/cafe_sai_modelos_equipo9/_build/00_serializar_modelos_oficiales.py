"""
SCRIPT DE SERIALIZACIÓN DE MODELOS OFICIALES — INFORME MEJORADO ENTREGA_2

REGLAS INQUEBRANTABLES ESTABLECIDAS POR EL USUARIO:
- NO modificar los modelos de Entrega_2.
- NO cambiar hiperparámetros, features, datos, thresholds, seed.
- NO escribir en ../Informe Mejorado ni ../Trabajo de Grado (solo lectura).

Este script:
1. COPIA los CSVs oficiales de Trabajo de Grado (solo lectura) hacia models_artifacts/.
2. Reproduce EXACTAMENTE Entrega_2 CELL 85 (features), CELL 121 (hiperparámetros) y CELL 122 (fit).
3. Serializa los 2 modelos oficiales + metadata + golden predictions.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor

# ---------------------------------------------------------------------------
# Rutas relativas (este script vive en: package_src/cafe_sai_modelos_equipo9/_build/)
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent.parent.parent  # solucion_local_sai_f3
MODELS_ARTIFACTS_DIR = PACKAGE_ROOT / "models_artifacts"
MODELS_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

PROJECT_ROOT = PACKAGE_ROOT.parent  # Caso 01

# Orígenes OFFICIAL — solo lectura, NUNCA se escriben
OFFICIAL_DATA = (
    PROJECT_ROOT
    / "Trabajo de Grado"
    / "Nuestro Grupo"
    / "GitHub_Equipo9_SeguroCafe"
    / "data"
    / "processed"
    / "features_modelo_equipo9.csv"
)
OFFICIAL_OUTPUTS = (
    PROJECT_ROOT
    / "Trabajo de Grado"
    / "Nuestro Grupo"
    / "GitHub_Equipo9_SeguroCafe"
    / "notebooks"
    / "outputs"
)
OFFICIAL_CSVS_TO_COPY = {
    "umbrales_departamento_equipo9.csv": "umbrales_departamento.csv",
    "kpis_resumen_equipo9.csv": "kpis_resumen.csv",
    "pred_vs_real_equipo9.csv": "pred_vs_real_loyo.csv",
    "validacion_historica_n1_equipo9.csv": "validacion_historica_n1.csv",
}

# ---------------------------------------------------------------------------
# CONSTANTES OFICIALES — copiadas literales de Entrega_2.ipynb CELL 85 y 121
# ---------------------------------------------------------------------------
SEED = 42  # Entrega_2 SEED (NO es 2026; 2026 es seed de pipeline Track A)

FEATURES_FENOLOGICAS = [  # CELL 85 Entrega_2 — ORDEN FIJO
    "spi3_floracion",
    "spi3_desarrollo",
    "spi3_cosecha",
    "tmax_mean_e9",
    "oni_mean",
    "roya_dummy",
]
TARGET = "rendimiento_kg_ha"
KEY_COLS = ["departamento", "year"]

MODELOS_FINALES = {  # CELL 121 Entrega_2 — HIperparámetros 100% FIJOS, no tocar
    "Narino": ExtraTreesRegressor(
        n_estimators=400,
        max_depth=3,
        max_features=0.6,
        min_samples_leaf=2,
        random_state=SEED,
        n_jobs=-1,
    ),
    "Quindio": RandomForestRegressor(
        n_estimators=400,
        max_depth=2,
        max_features=1.0,
        min_samples_leaf=1,
        random_state=SEED,
        n_jobs=-1,
    ),
}
MODEL_FILES = {
    "Narino": MODELS_ARTIFACTS_DIR / "narino_extratrees_entrega2.joblib",
    "Quindio": MODELS_ARTIFACTS_DIR / "quindio_randomforest_entrega2.joblib",
}

# 3 casos golden para validación reproducibilidad (depto, year indexado en panel)
GOLDEN_CASES = [
    ("Narino", 2007),
    ("Narino", 2012),
    ("Quindio", 2015),
]


# ---------------------------------------------------------------------------
# Paso 1 — Copiar CSVs oficiales a models_artifacts (SOLO lectura en origen)
# ---------------------------------------------------------------------------
def copy_official_csvs() -> None:
    dest = MODELS_ARTIFACTS_DIR / "features_panel_entrenamiento.csv"
    if not dest.exists():
        shutil.copy2(OFFICIAL_DATA, dest)
        print(f"[COPY] features_modelo_equipo9.csv -> {dest.name}")
    else:
        print(f"[SKIP] {dest.name} ya existe")

    for src_name, dst_name in OFFICIAL_CSVS_TO_COPY.items():
        src_path = OFFICIAL_OUTPUTS / src_name
        dst_path = MODELS_ARTIFACTS_DIR / dst_name
        if not dst_path.exists():
            shutil.copy2(src_path, dst_path)
            print(f"[COPY] {src_name} -> {dst_name}")
        else:
            print(f"[SKIP] {dst_name} ya existe")


# ---------------------------------------------------------------------------
# Paso 2 — Cargar panel y preparar (igual a Entrega_2 CELL 85-122)
# ---------------------------------------------------------------------------
def load_panel() -> pd.DataFrame:
    csv_path = MODELS_ARTIFACTS_DIR / "features_panel_entrenamiento.csv"
    panel = pd.read_csv(csv_path)
    # Exactamente igual que Entrega_2: panel único por departamento-año
    panel = panel.drop_duplicates(KEY_COLS).reset_index(drop=True)
    n_before = len(pd.read_csv(csv_path))
    print(
        f"[PANEL] Filas raw: {n_before}, tras drop_duplicates([depto,year]): {len(panel)}"
        f" | deptos: {sorted(panel['departamento'].unique().tolist())}"
        f" | años min/max: {panel['year'].min()}-{panel['year'].max()}"
    )
    assert len(panel) == 24, f"Se esperaban 24 filas (12 años * 2 deptos). Got {len(panel)}"
    return panel


# ---------------------------------------------------------------------------
# Paso 3 — Entrenar modelos (fit sobre TODAS obs depto — CELL 122 Entrega_2)
# ---------------------------------------------------------------------------
def train_and_serialize(panel: pd.DataFrame) -> dict[str, object]:
    trained: dict[str, object] = {}
    for depto, model in MODELOS_FINALES.items():
        g = panel.loc[panel["departamento"] == depto].copy()
        assert len(g) == 12, f"{depto}: se esperaban 12 años de datos, got {len(g)}"
        X = g[FEATURES_FENOLOGICAS]
        y = g[TARGET]
        model.fit(X, y)
        joblib.dump(model, MODEL_FILES[depto], compress=3)
        trained[depto] = model
        print(
            f"[FIT+SAVE] {depto}: {model.__class__.__name__}"
            f" n={len(g)} -> {MODEL_FILES[depto].name}"
        )
    return trained


# ---------------------------------------------------------------------------
# Paso 4 — Calcular 3 golden predictions y SHA256 de cada .joblib
# ---------------------------------------------------------------------------
def compute_golden_and_metadata(
    panel: pd.DataFrame, trained: dict[str, object]
) -> None:
    golden: dict[str, dict] = {"predictions": {}, "sha256_joblib": {}}
    for depto, year in GOLDEN_CASES:
        row = panel.loc[(panel["departamento"] == depto) & (panel["year"] == year)]
        assert len(row) == 1, f"Caso golden no encontrado: {depto}-{year}"
        X = row[FEATURES_FENOLOGICAS]
        y_true = float(row[TARGET].iloc[0])
        y_pred = float(trained[depto].predict(X)[0])
        golden["predictions"][f"{depto}_{year}"] = {
            "year": int(year),
            "departamento": depto,
            "y_real_kg_ha": round(y_true, 4),
            "y_pred_kg_ha": round(y_pred, 9),
            "features": {k: float(X[k].iloc[0]) for k in FEATURES_FENOLOGICAS},
        }
        print(
            f"[GOLDEN] {depto}-{year}: real={y_true:.2f} pred={y_pred:.6f}"
            f" | diff={abs(y_true-y_pred):.2f}"
        )

    for depto, path in MODEL_FILES.items():
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        golden["sha256_joblib"][depto] = h
        print(f"[SHA256] {depto}: {h[:12]}...")

    # Guardar golden para tests
    tests_dir = PACKAGE_ROOT / "tests"
    tests_dir.mkdir(exist_ok=True)
    golden_path = tests_dir / "_golden.json"
    golden_path.write_text(
        json.dumps(golden, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[SAVE] golden -> {golden_path}")

    # Guardar metadata_entrega2.json
    meta = {
        "nombre_proyecto": "SAI Cafetero Quindio-Narino — Informe Mejorado Entrega_2",
        "fecha_serializacion_utc": datetime.utcnow().isoformat() + "Z",
        "version_package_wheel": "0.1.0",
        "seed_oficial_entrega_2": SEED,
        "seed_track_a_pipeline_distinto": 2026,
        "features_fenologicas_orden_fijo": FEATURES_FENOLOGICAS,
        "target": TARGET,
        "panel_shape": [int(panel.shape[0]), int(panel.shape[1])],
        "n_observaciones_por_depto": {
            d: int((panel["departamento"] == d).sum())
            for d in sorted(panel["departamento"].unique())
        },
        "hiperparametros_oficiales": {
            depto: model.get_params() for depto, model in MODELOS_FINALES.items()
        },
        "modelos_artefactos": {
            depto: {"file": p.name, "sha256": golden["sha256_joblib"][depto]}
            for depto, p in MODEL_FILES.items()
        },
        "regla_track_a_pago_cop_ha": 1_200_000,
        "advertencia": "NO MODIFICAR ESTE ARCHIVO NI LOS .joblib — son los modelos oficiales de Entrega_2.",
    }
    meta_path = MODELS_ARTIFACTS_DIR / "metadata_entrega2.json"
    meta_path.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[SAVE] metadata -> {meta_path}")


def main() -> int:
    print("=" * 80)
    print("SERIALIZADOR MODELOS OFICIALES — INFORME MEJORADO ENTREGA_2")
    print("=" * 80)
    assert OFFICIAL_DATA.exists(), f"No encontrado: {OFFICIAL_DATA}"
    copy_official_csvs()
    panel = load_panel()
    trained = train_and_serialize(panel)
    compute_golden_and_metadata(panel, trained)
    print("\n[OK] Serialización completada sin errores.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
