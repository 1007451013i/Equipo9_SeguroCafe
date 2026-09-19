# Modelos oficiales café SAI — capa de inferencia reutilizable

Paquete Python distribuible vía Wheel que expone los modelos oficiales
seleccionados en `Informe Mejorado/Entrega_2.ipynb` para Seguro Agrícola
Indexado cafetero (Quindío / Nariño).

## Regla INQUEBRANTABLE
- NO modificar hiperparámetros, features, seed (42), ni datos de entrenamiento.
- Los artefactos `.joblib` y CSVs de referencia NO vienen dentro del `.whl`;
  deben deployarse en `models_artifacts/` y localizarse vía env
  `CAFE_SAI_MODELS_DIR` o `set_models_dir()`.
