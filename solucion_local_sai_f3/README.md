# Seguro Agricola Indexado Cafetero - Solucion local v0.1.0

Carpeta 100 por ciento independiente (hermana de `Trabajo de Grado/` e `Informe Mejorado/`).
**No modifica ningun archivo** de las carpetas de referencia. La regla principal del proyecto
es estricta: **NO MODIFICAR LOS MODELOS** (no reentrenar, no cambiar hiperparametros, no cambiar features,
no recalibrar, etc.). Este proyecto unicamente:

1. Reproduce el entrenamiento oficial exacto (mismo seed=42, mismos hp, mismas features,
   mismo CSV) y **serializa** a `.joblib` (2 modelos + metadata + predicciones golden).
2. Empaqueta la logica de inferencia en un paquete Python distribuible (`.whl`).
3. Expone una API REST (FastAPI, 127.0.0.1:8000).
4. Construye un panel local de **UNA SOLA PAGINA** (Streamlit, 127.0.0.1:8501) consumiendo 100 por ciento la API.
5. Incluye tests pytest y scripts `.ps1` listos para Windows.

---

## Estructura REAL (actualizada)

```
solucion_local_sai_f3/
|-- api/
|   |-- main.py                     # FastAPI - 13 endpoints (health, models, predict, SPI, KPIs, series)
|   `-- schemas_api.py              # Pydantic v2 schemas
|
|-- dashboard/
|   `-- app.py                      # UNA SOLA PAGINA (6 modulos + sidebar filtros, NO carpeta pages/)
|
|-- models_artifacts/               # Solo lectura, NO dentro del wheel
|   |-- narino_extratrees_entrega2.joblib
|   |-- quindio_randomforest_entrega2.joblib
|   |-- metadata_entrega2.json
|   |-- features_panel_entrenamiento.csv    # shape (24, 48)
|   |-- umbrales_departamento.csv
|   |-- kpis_resumen.csv
|   |-- pred_vs_real_loyo.csv
|   `-- validacion_historica_n1.csv         # 2 eventos x 2 deptos
|
|-- package_src/
|   `-- cafe_sai_modelos_equipo9/           # UNICA fuente de logica de prediccion
|       |-- __init__.py             # exports publicos
|       |-- _version.py             # __version__ = "0.1.0"
|       |-- schemas.py              # FEATURES_FENOLOGICAS, TARGET, PAGO_EVENTO_COP_HA
|       |-- loader.py               # set_models_dir, load_models, load_reference_csv
|       |-- track_b_rendimiento.py  # predict_rendimiento()
|       |-- track_a_spi.py          # predict_activacion_spi() - 5 reglas OR
|       |-- kpis.py                 # get_kpis_actuariales / track_a / track_b
|       |-- panel.py                # panel 24x48, loyo, validacion historica
|       `-- _build/00_serializar_modelos_oficiales.py
|
|-- tests/                          # Sandbox desarrollador, no distribuir
|
|-- dist/
|   `-- cafe_sai_modelos_equipo9-0.1.0-py3-none-any.whl    # Wheel distribuible
|
|-- pyproject.toml                  # PEP 621 hatchling (excluye _build del wheel)
|-- requirements.txt                # Dependencias completas (runtime + API + dashboard + build + test)
|-- README_PACKAGE.md
|
|-- setup_dev.ps1                   # Setup ALL-IN-ONE (venv + requirements + wheel + tests)
|-- build_package.ps1               # Solo build wheel
|-- run_api.ps1                     # Levantar API FastAPI :8000
`-- run_dashboard.ps1               # Levantar Dashboard Streamlit :8501
```

---

## Modelos oficiales (NO modificados)

| Departamento | Modelo                | n_estimators | max_depth | max_features | min_samples_leaf |
|--------------|-----------------------|--------------|-----------|--------------|------------------|
| Narino       | ExtraTreesRegressor   | 400          | 3         | 0.6          | 2                |
| Quindio      | RandomForestRegressor | 400          | 2         | 1.0          | 1                |

- seed modelos (`random_state`) = **42**.
- features exactas (orden **DEBE** respetarse):
  `["spi3_floracion", "spi3_desarrollo", "spi3_cosecha", "tmax_mean_e9", "oni_mean", "roya_dummy"]`
- target: `rendimiento_kg_ha`.
- **No se usa StandardScaler.**
- Pago por evento por defecto: **1.200.000 COP/ha** (ajustable en calculadora).

### Valores golden verificados

| Caso            | Prediccion golden package  | diff vs notebook Entrega_2 |
|-----------------|----------------------------|----------------------------|
| Narino 2007     | 1150.273445185 kg/ha       | < 1e-9                     |
| Quindio 2015    | 1124.381196279 kg/ha       | < 1e-9                     |
| Narino 2012     | 974.183513203  kg/ha       | < 1e-9                     |

### KPIs y umbrales oficiales

| Depto  | P10 SPI  | P90 SPI   | Act.  | RMSE HO | HE   | Prima  | Riesgo Base |
|--------|----------|-----------|-------|---------|------|--------|-------------|
| Narino | -1.7071  | +0.1940   | 24 %  | 15.1    | 0.05 | 6.36 % | 47.36 %     |
| Quindio| -2.2143  | -0.1328   | 24 %  | 45.7    | 0.11 | 10.15% | 46.71 %     |

---

## 1. Requisitos previos

Solo necesitas **Python 3.11 estandar** (Microsoft Store o python.org). El python portable
en `../Trabajo de Grado/python_portable/` sirve para inspeccion pero **no trae `venv`** ni instala plotly correctamente.

---

## 2. Instalacion rapida

```powershell
# 1. Entra en la carpeta
cd solucion_local_sai_f3

# 2. Crea y activa entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Actualiza pip
python -m pip install --upgrade pip

# 4. Instala todas las dependencias
pip install -r requirements.txt

# 5. Instala el package de inferencia
pip install dist\cafe_sai_modelos_equipo9-0.1.0-py3-none-any.whl
```

### Setup ALL-IN-ONE (alternativa)

Si prefieres un unico comando que haga todo (incluyendo build del wheel y tests):
```powershell
powershell -ExecutionPolicy Bypass -File .\setup_dev.ps1
```

---

## 3. Ejecutar los servicios (2 terminales)

### Terminal 1 - API FastAPI

```powershell
cd solucion_local_sai_f3
.venv\Scripts\Activate.ps1
.\run_api.ps1
```

- URL: `http://127.0.0.1:8000`
- Salud: `http://127.0.0.1:8000/health`
- Swagger UI (docs automatica): `http://127.0.0.1:8000/docs`
- Redoc: `http://127.0.0.1:8000/redoc`

### Terminal 2 - Dashboard Streamlit

```powershell
cd solucion_local_sai_f3
.venv\Scripts\Activate.ps1
.\run_dashboard.ps1
```

- URL: `http://127.0.0.1:8501`

---

## 4. Estructura del panel (UNA SOLA PAGINA)

El dashboard replica el mockup `Mockup_Panel_Fase3.pdf`:

- **Sidebar izquierdo** (filtros globales):
  - Departamento (Todos / Narino / Quindio)
  - Rango de anios (slider 2007 - 2018)
  - Precarga historica Track B (anio + departamento)
  - Parametros calculadora actuarial (ha, pago evento, sobrecarga)
- **Cuerpo principal - 6 modulos**:
  1. KPIs oficiales (6 tarjetas: RMSE, HE, Prima x 2 deptos)
  2. Track A: Serie SPI-3 fenologico + activaciones por anio
  3. Track B: Formulario prediccion rendimiento + semaforo riesgo BAJO/MEDIO/ALTO
  4. Track B: LOYO Prediccion vs Real + metricas resumen
  5. Validacion historica N=2 (2012 Roya / 2015 Nino, semaforo cumplimiento)
  6. Calculadora actuarial (prima vs indemnizaciones, 12 anios + balance)

---

## 5. Portabilidad

- **Sin rutas absolutas.** El codigo de distribucion NO contiene referencias a `C:\Users\`, `OneDrive\`, `Desktop\` ni nombres de usuario especificos.
- **Rutas dinamicas:**
  - Python: `Path(__file__).resolve().parent...`
  - PowerShell: `Split-Path -Parent $MyInvocation.MyCommand.Path`
- La carpeta `tests/` contiene archivos sandbox del desarrollador con rutas locales. **NO se distribuye ni es necesaria para usar el sistema.**

Para el manual tecnico completo, consulte:
`../Trabajo de Grado/Guia_Solucion_SAI_F3.md`
