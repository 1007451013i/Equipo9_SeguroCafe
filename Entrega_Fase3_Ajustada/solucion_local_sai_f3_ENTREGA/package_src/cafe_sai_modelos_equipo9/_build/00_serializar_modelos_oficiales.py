"""
SCRIPT DE SERIALIZACION DE MODELOS OFICIALES - HERRAMIENTA DE BUILD (NO RUNTIME)

REGLAS INQUEBRANTABLES ESTABLECIDAS POR EL USUARIO:
- NO modificar los modelos de Entrega_2.
- NO cambiar hiperparametros, features, datos, thresholds, seed.
- NO escribir en carpetas externas (Trabajo de Grado, Informe Mejorado) - solo lectura.

Portabilidad:
  Este script es una HERRAMIENTA DE BUILD. Busca las fuentes oficiales SOLO si
  existen en una carpeta hermana. Si las fuentes NO estan disponibles (porque la
  carpeta solucion_local_sai_f3 fue copiada aisladamente a otro PC), pero los
  CSVs de features y referencias YA EXISTEN DENTRO de models_artifacts/, el
  script puede re-entrenar y serializar los modelos sin fuentes externas.
  El RUNTIME NUNCA llama a este script.
"""

from __future__ import annotations

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
# Rutas 100% PORTABLES (sin salir de solucion_local_sai_f3 a menos que las
# fuentes originales existan como opcion adicional en una carpeta hermana).
# Este script vive en:
#   <SOLUTION_ROOT>/package_src/cafe_sai_modelos_equipo9/_build/<SCRIPT>.py
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
SOLUTION_ROOT = SCRIPT_DIR.parents[3]  # solucion_local_sai_f3 (4 niveles arriba)
MODELS_ARTIFACTS_DIR = SOLUTION_ROOT / "models_artifacts"
MODELS_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# Origen OFFICIAL es OPCIONAL. Solo se usa si existe; si no, se asume que
# los CSVs YA ESTAN copiados en models_artifacts (solucion autonoma portable).
_OPTIONAL_EXTERNAL_PROJECT_ROOT = SOLUTION_ROOT.parent
OFFICIAL_DATA_OPTIONAL = (
    _OPTIONAL_EXTERNAL_PROJECT_ROOT
    / "Trabajo de Grado"
    / "Nuestro Grupo"
    / "GitHub_Equipo9_SeguroCafe"
    / "data"
    / "processed"
    / "features_modelo_equipo9.csv"
)
OFFICIAL_OUTPUTS_OPTIONAL = (
    _OPTIONAL_EXTERNAL_PROJECT_ROOT
    / "Trabajo de Grado"
    / "Nuestro Grupo"
    / "GitHub_Equipo9_SeguroCafe"
    / "notebooks"
    / "outputs"
)
OFFICIAL_CSVS_TO_COPY_IF_EXTERNAL_EXISTS = {
    "umbrales_departamento_equipo9.csv": "umbrales_departamento.csv",
    "kpis_resumen_equipo9.csv": "kpis_resumen.csv",
    "pred_vs_real_equipo9.csv": "pred_vs_real_loyo.csv",
    "validacion_historica_n1_equipo9.csv": "validacion_historica_n1.csv",
}

# ---------------------------------------------------------------------------
# CONSTANTES OFICIALES - copiadas literales de Entrega_2.ipynb CELL 85 y 121
# ---------------------------------------------------------------------------
SEED = 42  # Entrega_2 SEED (NO es 2026; 2026 es seed de pipeline Track A)

FEATURES_FENOLOGICAS = [  # CELL 85 Entrega_2 - ORDEN FIJO
    "spi3_floracion",
    "spi3_desarrollo",
    "spi3_cosecha",
    "tmax_mean_e9",
    "oni_mean",
    "roya_dummy",
]
TARGET = "rendimiento_kg_ha"
KEY_COLS = ["departamento", "year"]

MODELOS_FINALES = {  # CELL 121 Entrega_2 - Hiperparametros 100% FIJOS, no tocar
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

GOLDEN_CASES = [
    ("Narino", 2007),
    ("Narino", 2012),
    ("Quindio", 2015),
]


# ---------------------------------------------------------------------------
# Paso 1 - Copiar CSVs oficiales si el origen externo existe. Si no, se asume
# que models_artifacts/ ya los contiene (carpeta autonoma portable).
# ---------------------------------------------------------------------------
def copy_official_csvs_optional() -> None:
    dest = MODELS_ARTIFACTS_DIR / "features_panel_entrenamiento.csv"
    if (not dest.exists()) and OFFICIAL_DATA_OPTIONAL.is_file():
        shutil.copy2(OFFICIAL_DATA_OPTIONAL, dest)
        print(f"[COPY] features_modelo_equipo9.csv -> {dest.name}")
    elif dest.exists():
        print(f"[SKIP] {dest.name} ya existe en models_artifacts/ (autonomo)")
    elif not OFFICIAL_DATA_OPTIONAL.is_file():
        # Origen externo NO esta (carpeta portable). Si no hay CSV falla despues.
        print("[WARN] Fuente externa features_modelo_equipo9.csv NO encontrada.")
        print("       Se asume que models_artifacts/ es autonomo y ya contiene CSVs.")

    for src_name, dst_name in OFFICIAL_CSVS_TO_COPY_IF_EXTERNAL_EXISTS.items():
        src_path = OFFICIAL_OUTPUTS_OPTIONAL / src_name
        dst_path = MODELS_ARTIFACTS_DIR / dst_name
        if (not dst_path.exists()) and src_path.is_file():
            shutil.copy2(src_path, dst_path)
            print(f"[COPY] {src_name} -> {dst_name}")
        elif dst_path.exists():
            print(f"[SKIP] {dst_name} ya existe en models_artifacts/ (autonomo)")


# ---------------------------------------------------------------------------
# Paso 2 - Cargar panel y preparar (igual a Entrega_2 CELL 85-122)
# ---------------------------------------------------------------------------
def load_panel() -> pd.DataFrame:
    csv_path = MODELS_ARTIFACTS_DIR / "features_panel_entrenamiento.csv"
    if not csv_path.is_file():
        raise FileNotFoundError(
            "No existe features_panel_entrenamiento.csv en models_artifacts/. "
            "Ejecuta este script desde la carpeta original con las fuentes "
            "externas disponibles, o copia manualmente el CSV a models_artifacts/."
        )
    panel = pd.read_csv(csv_path)
    panel = panel.drop_duplicates(KEY_COLS).reset_index(drop=True)
    n_before = len(pd.read_csv(csv_path))
    print(
        f"[PANEL] Filas raw: {n_before}, tras drop_duplicates([depto,year]): {len(panel)}"
        f" | deptos: {sorted(panel['departamento'].unique().tolist())}"
        f" | anios min/max: {panel['year'].min()}-{panel['year'].max()}"
    )
    assert len(panel) == 24, f"Se esperaban 24 filas (12 anios * 2 deptos). Got {len(panel)}"
    return panel


# ---------------------------------------------------------------------------
# Paso 3 - Entrenar y serializar (CELL 122 Entrega_2)
# ---------------------------------------------------------------------------
def train_and_serialize(panel: pd.DataFrame) -> dict[str, object]:
    trained: dict[str, object] = {}
    for depto, model in MODELOS_FINALES.items():
        g = panel.loc[panel["departamento"] == depto].copy()
        assert len(g) == 12, f"{depto}: se esperaban 12 anios de datos, got {len(g)}"
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
# Paso 4 - Golden predictions y metadata
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

    tests_dir = SOLUTION_ROOT / "tests"
    tests_dir.mkdir(exist_ok=True)
    golden_path = tests_dir / "_golden.json"
    golden_path.write_text(
        json.dumps(golden, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[SAVE] golden -> {golden_path}")

    meta = {
        "nombre_proyecto": "SAI Cafetero Quindio-Narino - Informe Mejorado Entrega_2",
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
        "advertencia": "NO MODIFICAR ESTE ARCHIVO NI LOS .joblib - son los modelos oficiales de Entrega_2.",
    }
    meta_path = MODELS_ARTIFACTS_DIR / "metadata_entrega2.json"
    meta_path.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[SAVE] metadata -> {meta_path}")


def main() -> int:
    print("=" * 80)
    print("SERIALIZADOR MODELOS OFICIALES - HERRAMIENTA DE BUILD (NO RUNTIME)")
    print(f"Ruta raiz portable: {SOLUTION_ROOT}")
    print("=" * 80)
    copy_official_csvs_optional()
    panel = load_panel()
    trained = train_and_serialize(panel)
    compute_golden_and_metadata(panel, trained)
    print("\n[OK] Serializacion completada sin errores.")
    print("[INFO] Para correr la API NO necesitas ejecutar este script.")
    print(f"       Los .joblib estan en: {MODELS_ARTIFACTS_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
