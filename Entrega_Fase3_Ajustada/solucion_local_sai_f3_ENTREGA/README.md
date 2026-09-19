# Solucion Local Autonoma SAI Cafetero - v0.1.0

**Carpeta 100 por ciento AUTONOMA y PORTABLE.**

Esta carpeta contiene TODO lo necesario para ejecutar la API local de modelos.
**No requiere** ninguna otra carpeta del proyecto (Trabajo de Grado, Informe Mejorado, notebooks, datos externos, etc.).
Los modelos oficiales ya estan serializados en `models_artifacts/`. No es necesario ejecutar ningun script de entrenamiento, serializacion, ETL ni reconstruccion.

**Regla inquebrantable del proyecto:** NO MODIFICAR LOS MODELOS (no reentrenar, no cambiar hiperparametros, no cambiar features, no cambiar semilla, no cambiar datasets).

Contenido:
1. Paquete de inferencia en `package_src/` y `.whl` distribuible en `dist/`.
2. API REST local (FastAPI, puerto 8000).
3. Panel ejecutivo de UNA SOLA PAGINA (Streamlit, puerto 8501).
4. Scripts `.ps1` para Windows 10/11.
5. 2 modelos oficiales serializados + 6 artefactos CSV/JSON de referencia dentro de `models_artifacts/`.

---

## 1. Requisito previo

Unicamente necesitas **Python 3.11 estandar** (instalado desde Microsoft Store o python.org), con el launcher `py.exe` en el PATH. No requiere acceso a internet una vez que las dependencias esten instaladas.

Sistema operativo probado: Windows 10 / Windows 11 (PowerShell 5.1 o superior).

---

## 2. Instalacion (5 pasos MINIMOS)

```powershell
# Paso 1. Copia/clona esta carpeta EN CUALQUIER UBICACION. Entra dentro:
cd solucion_local_sai_f3

# Paso 2. Crea entorno virtual dentro de la carpeta:
py.exe -3.11 -m venv .venv

# Paso 3. Activa el entorno virtual (Windows):
.venv\Scripts\Activate.ps1

# Si PowerShell bloquea scripts:
# powershell -ExecutionPolicy Bypass -Command ".venv\Scripts\Activate.ps1"

# Paso 4. Actualiza pip e instala dependencias:
python -m pip install --upgrade pip
pip install -r requirements.txt

# Paso 5. Instala el paquete distribuible .whl (opcional pero recomendado):
pip install dist\cafe_sai_modelos_equipo9-0.1.0-py3-none-any.whl
```

Listo. No necesitas hacer nada mas.

---

## 3. Ejecutar la API

Abre 1 terminal de PowerShell dentro de `solucion_local_sai_f3\` y escribe:

```powershell
# Asegura activar .venv si no lo hiciste antes:
.venv\Scripts\Activate.ps1

# Levanta la API:
.\run_api.ps1
```

Espera el mensaje de OK. Abre en tu navegador:

- **Swagger UI (documentacion automatica de endpoints):** `http://127.0.0.1:8000/docs`
- **Salud (comprueba que los 2 modelos se cargaron correctamente):** `http://127.0.0.1:8000/health`
- **Modelos disponibles:** `http://127.0.0.1:8000/api/v1/models`
- **Endpoint raiz:** `http://127.0.0.1:8000/`

Parametros opcionales de `run_api.ps1`:
```
-Port <int>         Puerto (por defecto 8000)
-ApiHost <string>   Host (por defecto 127.0.0.1)
-NoReload           Desactiva auto-reload de uvicorn
```

---

## 4. Ejecutar el panel ejecutivo (dashboard)

Abre OTRA terminal de PowerShell (debes dejar la API corriendo).

```powershell
cd solucion_local_sai_f3
.venv\Scripts\Activate.ps1
.\run_dashboard.ps1
```

Abre en el navegador: `http://127.0.0.1:8501`

Parametros opcionales de `run_dashboard.ps1`:
```
-Port <int>        Puerto (por defecto 8501)
-DashHost <string> Host (por defecto 127.0.0.1)
-ApiBase <string>  URL base de la API (por defecto http://127.0.0.1:8000)
```

---

## 5. Estructura (SOLO para referencia)

No es necesario entender esto para usar la solucion. Se incluye para auditoria:

```
solucion_local_sai_f3/
|-- api/                                (FastAPI - 13 endpoints)
|   |-- main.py
|   `-- schemas_api.py
|
|-- dashboard/                          (Streamlit - UNA SOLA PAGINA, NO pages/)
|   `-- app.py                          (6 modulos + sidebar filtros)
|
|-- models_artifacts/                   (ARTEFACTOS DE RUNTIME, no tocar)
|   |-- narino_extratrees_entrega2.joblib    (modelo oficial Narino, seed 42)
|   |-- quindio_randomforest_entrega2.joblib (modelo oficial Quindio, seed 42)
|   |-- metadata_entrega2.json
|   |-- features_panel_entrenamiento.csv     (24 filas x 48 cols)
|   |-- umbrales_departamento.csv            (P10/P90 SPI3 por depto)
|   |-- kpis_resumen.csv                     (RMSE, HE, Prima, RiesgoBase...)
|   |-- pred_vs_real_loyo.csv                (Leave-One-Year-Out)
|   `-- validacion_historica_n1.csv          (4 eventos 2012/2015)
|
|-- package_src/
|   `-- cafe_sai_modelos_equipo9/      (LOGICA UNICA DE INFERENCIA)
|       |-- __init__.py
|       |-- schemas.py / loader.py
|       |-- track_b_rendimiento.py / track_a_spi.py
|       |-- kpis.py / panel.py
|       `-- _build/00_serializar_modelos_oficiales.py (herramienta BUILD, NO runtime)
|
|-- dist/
|   `-- cafe_sai_modelos_equipo9-0.1.0-py3-none-any.whl
|
|-- requirements.txt
|-- pyproject.toml
|-- run_api.ps1 / run_dashboard.ps1
|-- setup_dev.ps1 / build_package.ps1
`-- README.md (ESTE ARCHIVO)
```

---

## 6. Modelos oficiales (NO MODIFICAR)

| Departamento | Modelo                | n_est | max_d | max_f | msl  | seed |
|:------------:|:---------------------:|:-----:|:-----:|:-----:|:----:|:----:|
| Narino       | ExtraTreesRegressor   | 400   | 3     | 0.6   | 2    | 42   |
| Quindio      | RandomForestRegressor | 400   | 2     | 1.0   | 1    | 42   |

- Features fijas (orden fijo): `["spi3_floracion","spi3_desarrollo","spi3_cosecha","tmax_mean_e9","oni_mean","roya_dummy"]`
- Target: `rendimiento_kg_ha`
- Pago por evento Track A: 1,200,000 COP/ha (ajustable en calculadora).

---

## 7. Resumen rapido - checklist de 1 minuto

| Verificar | Comando / URL |
|:----------|:--------------|
| (1) En mi carpeta? | `pwd` muestra la ruta de solucion_local_sai_f3 |
| (2) .venv existe?  | `Test-Path .venv\Scripts\python.exe` debe ser True |
| (3) .venv activo?  | `Get-Command python | Select-Object Source` debe apuntar a `...\.venv\Scripts\python.exe` |
| (4) Dependencias?  | `pip list \| findstr fastapi` y `...scikit-learn` deben mostrar versiones |
| (5) Models ok?     | `Test-Path models_artifacts\narino_extratrees_entrega2.joblib` True + Quindio True |
| (6) API ok?        | `http://127.0.0.1:8000/health` muestra "status":"ok" |
| (7) Docs API?      | `http://127.0.0.1:8000/docs` abre Swagger UI |
| (8) Dashboard?     | `http://127.0.0.1:8501` panel en navegador |
