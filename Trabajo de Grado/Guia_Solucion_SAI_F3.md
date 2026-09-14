# Implementacion Local - Modelos y Dashboard
## Seguro Agricola Indexado Cafetero (Quindio / Narino) - Equipo 9 - 2026

---

## 1. Objetivo

El objetivo de esta implementacion es proveer una solucion 100 por ciento local, portable y lista para usar, que permita a cualquier integrante del equipo ejecutar los modelos oficiales de Machine Learning definidos en Informe Mejorado/Entrega_2 sin necesidad de reentrenar ni modificar parametros. La solucion encapsula toda la logica de inferencia en un paquete Python distribuible (.whl), expone una API REST local y entrega un panel de control (dashboard) de una sola pagina listo para la toma de decisiones.

---

## 2. Alcance

La implementacion permite utilizar los modelos existentes mediante una arquitectura local compuesta por las siguientes capas, ejecutadas en el orden indicado:

```
Modelos oficiales (Entrega_2, NO modificados)
        |
        v
Capa de inferencia (package Python - logica unica)
        |
        v
Paquete distribuible .whl (cafe_sai_modelos_equipo9)
        |
        v
API REST local (FastAPI, puerto 8000)
        |
        v
Dashboard local (Streamlit de una sola pagina, puerto 8501)
```

Cada capa tiene una unica responsabilidad. La logica estadistica y los modelos NO se replican en la API ni en el dashboard: todo se consume desde el paquete.

---

## 3. Fuentes utilizadas

En esta implementacion se utilizaron las siguientes carpetas originales como **fuente de solo lectura**. Ningun archivo de estas carpetas fue modificado.

### 3.1 Trabajo de Grado

Contiene el trabajo historico relacionado con ETL, versiones anteriores de modelos y notebooks de exploracion. **Esta carpeta NO contiene los modelos finales utilizados en la implementacion.** Se usa unicamente como referencia historica y para alojar el presente documento (Guia_Solucion_SAI_F3.md), que es el unico archivo nuevo permitido dentro de esta carpeta.

### 3.2 Informe Mejorado / Entrega_2

Contiene los modelos oficiales que DEBEN utilizarse para la implementacion final, sin modificacion alguna:
- Notebook `Entrega_2.ipynb` (CELL 121: definicion de ExtraTrees para Narino y RandomForest para Quindio; CELL 122: panel de entrenamiento 24 x 48).
- CSV `features_modelo_equipo9.csv` (ubicado dentro del subarbol de Trabajo de Grado, usado como fuente de datos para reproducir el entrenamiento).
- CSV `kpis_resumen.csv`, `umbrales_departamento.csv`, `pred_vs_real_loyo.csv`, `validacion_historica_n1.csv`.

### 3.3 Informe Mejorado / Informe_Entrega_2

Contiene la documentacion, parametrizacion, resultados y hallazgos asociados a los modelos. Se consulta para validar que los KPIs reportados en el dashboard coincidan con los valores oficiales (RMSE, HE, prima, riesgo base, umbrales P10/P90).

### 3.4 Informe Mejorado / Mockup_Panel_Fase3

Contiene el diseno de referencia utilizado para construir el dashboard. El panel de Streamlit replica la estructura de una sola pagina: sidebar izquierdo con filtros, y 6 modulos en el cuerpo principal.

---

## 4. Proceso seguido

El proceso real que se siguio para llegar a la solucion actual consta de 6 pasos:

### Paso 1 - Identificacion de modelos

Se identificaron los modelos oficiales en `Informe Mejorado/Entrega_2.ipynb` (CELL 121). Se confirmaron hiperparametros, seed, features, dataset y target. NO se modifico ningun parametro.

### Paso 2 - Preparacion para inferencia

Se separo la utilizacion de los modelos de los demas componentes del proyecto. Se creo una capa unica de inferencia en `package_src/cafe_sai_modelos_equipo9/` que exporta funciones puras: `predict_rendimiento`, `predict_activacion_spi`, `get_kpis_*`, `get_panel_*`.

### Paso 3 - Empaquetamiento

Se creo el paquete Python distribuible mediante `.whl` usando PEP 621 (hatchling). El wheel se genera en `solucion_local_sai_f3/dist/cafe_sai_modelos_equipo9-0.1.0-py3-none-any.whl` y contiene unicamente codigo de inferencia. Los artefactos de modelos (`.joblib` y CSV) NO se incluyen dentro del wheel.

### Paso 4 - API

Se creo la API local con FastAPI para recibir solicitudes HTTP y ejecutar las predicciones a traves del paquete. La API NO carga sklearn directamente.

### Paso 5 - Dashboard

Se conecto el dashboard Streamlit de una sola pagina con la API local. El dashboard NO carga modelos directamente: todo dato se obtiene via requests HTTP a `http://127.0.0.1:8000`.

### Paso 6 - Integracion

El flujo final quedo:

```
Usuario (navegador web)
        |
        v
Dashboard (Streamlit :8501)
        |  (HTTP GET / POST JSON)
        v
API local (FastAPI :8000)
        |  (llamado al paquete Python)
        v
Modelo oficial (ExtraTrees / RandomForest .joblib)
        |
        v
Prediccion (kg/ha / activacion SPI / KPIs)
        |
        v
API local (respuesta JSON)
        |
        v
Dashboard (renderizado de tarjetas, graficos y semaforos)
        |
        v
Usuario (visualizacion del resultado)
```

---

## 5. Estructura actual del proyecto

La estructura real de carpetas y archivos relevantes es la siguiente:

```
Caso 01/
|
|-- Trabajo de Grado/                         (solo lectura + este archivo)
|   |-- Nuestro Grupo/
|   |   `-- GitHub_Equipo9_SeguroCafe/
|   |       `-- data/processed/features_modelo_equipo9.csv
|   `-- Guia_Solucion_SAI_F3.md               (ESTE DOCUMENTO)
|
|-- Informe Mejorado/                         (solo lectura)
|   |-- Entrega_2.ipynb                       (modelos oficiales CELL 121/122)
|   |-- Informe_Entrega_2/                    (documentacion y resultados oficiales)
|   `-- Mockup_Panel_Fase3.pdf                (diseno referencia dashboard)
|
`-- solucion_local_sai_f3/                    (TODO LO NUEVO - carpeta hermana)
    |
    |-- api/                                  (FastAPI local)
    |   |-- main.py                           (entrypoint 13 endpoints)
    |   `-- schemas_api.py                    (Pydantic v2 schemas)
    |
    |-- dashboard/                            (Streamlit - UNA SOLA PAGINA)
    |   `-- app.py                            (modulos KPI/SPI/TrackB/LOYO/Validacion/Calculadora)
    |
    |-- dist/
    |   `-- cafe_sai_modelos_equipo9-0.1.0-py3-none-any.whl    (Wheel distribuible)
    |
    |-- models_artifacts/                     (artefactos, NO en wheel)
    |   |-- narino_extratrees_entrega2.joblib
    |   |-- quindio_randomforest_entrega2.joblib
    |   |-- metadata_entrega2.json
    |   |-- features_panel_entrenamiento.csv
    |   |-- umbrales_departamento.csv
    |   |-- kpis_resumen.csv
    |   |-- pred_vs_real_loyo.csv
    |   `-- validacion_historica_n1.csv
    |
    |-- package_src/
    |   `-- cafe_sai_modelos_equipo9/         (LOGICA UNICA DE INFERENCIA)
    |       |-- __init__.py
    |       |-- _version.py
    |       |-- schemas.py                    (FEATURES_FENOLOGICAS, TARGET, PAGO_EVENTO)
    |       |-- loader.py                     (set_models_dir / load_models / cache)
    |       |-- track_b_rendimiento.py        (predict_rendimiento)
    |       |-- track_a_spi.py                (predict_activacion_spi 5 reglas OR)
    |       |-- kpis.py                       (get_kpis_track_a / track_b / actuariales)
    |       |-- panel.py                      (series historicas / loyo / validacion)
    |       `-- _build/
    |           `-- 00_serializar_modelos_oficiales.py
    |
    |-- tests/                                (sandbox desarrollador, ignorar para uso)
    |
    |-- build_package.ps1                     (Re-construir el wheel manualmente)
    |-- setup_dev.ps1                         (ALL-IN-ONE: venv + deps + wheel + tests)
    |-- run_api.ps1                           (Levantar API en :8000)
    |-- run_dashboard.ps1                     (Levantar Dashboard en :8501)
    |
    |-- pyproject.toml                        (PEP 621 hatchling build config)
    |-- requirements.txt                      (dependencias completas)
    |-- README_PACKAGE.md
    `-- README.md                             (resumen para la carpeta solucion_local_sai_f3)
```

---

## 6. Requisitos

### 6.1 Version de Python

- **Python 3.11** (versión oficialmente utilizada y probada). Compatible tambien con 3.10 y 3.12.
- El python portable ubicado en `Trabajo de Grado/python_portable/` puede usarse para inspeccion, pero NO incluye el modulo `venv` ni permite instalar plotly correctamente. Para la instalacion oficial se requiere Python estandar de Microsoft Store o python.org.

### 6.2 Sistema operativo

- Windows 10 / Windows 11 (PowerShell 5.1 o superior). Los comandos de este documento son para Windows.

### 6.3 Dependencias

Todas las dependencias estan documentadas en `solucion_local_sai_f3/requirements.txt` y en `solucion_local_sai_f3/pyproject.toml`. La lista minima es:

- Runtime base: `numpy==1.26.4`, `scipy==1.11.4`, `pandas==2.1.4`, `scikit-learn==1.3.2`, `joblib==1.3.2`, `matplotlib==3.7.5`, `seaborn==0.13.2`, `pillow==10.4.0`, `openpyxl==3.1.5`, `threadpoolctl==3.2.0`
- API: `fastapi>=0.110`, `uvicorn[standard]>=0.27`, `pydantic>=2.5`, `httpx>=0.27`
- Dashboard: `streamlit>=1.32`, `plotly>=5.18`
- Build / dev: `hatchling>=1.24`, `build>=1.1`, `wheel>=0.43`, `pytest>=8.0`

---

## 7. Instalacion desde cero

Sigue estos pasos en orden. NO es necesario modificar ninguna ruta en el codigo.

### Paso 1: Copiar el proyecto

Copia o clona toda la carpeta `Caso 01/` en cualquier ubicacion del nuevo computador, por ejemplo:
- `C:\Users\Miembro1\Desktop\Proyecto\`
- `D:\Universidad\Caso01\`

### Paso 2: Abrir una terminal en la carpeta de la solucion

```powershell
cd "ruta\donde\este\el\proyecto\Caso 01\solucion_local_sai_f3"
```

### Paso 3: Crear entorno virtual

```powershell
python -m venv .venv
```

### Paso 4: Activar el entorno virtual (Windows)

```powershell
.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la ejecucion de scripts, usa:
```powershell
powershell -ExecutionPolicy Bypass -Command ".venv\Scripts\Activate.ps1"
```

### Paso 5: Actualizar pip

```powershell
python -m pip install --upgrade pip
```

### Paso 6: Instalar dependencias

```powershell
pip install -r requirements.txt
```

### Paso 7: Instalar el paquete .whl

El nombre REAL del wheel es `cafe_sai_modelos_equipo9-0.1.0-py3-none-any.whl`.

```powershell
pip install dist\cafe_sai_modelos_equipo9-0.1.0-py3-none-any.whl
```

Si el wheel no existe (por ejemplo en un equipo nuevo donde no se corrio setup_dev.ps1), reconstruyelo primero:
```powershell
python -m build --outdir dist --wheel --no-isolation
pip install dist\cafe_sai_modelos_equipo9-0.1.0-py3-none-any.whl
```

---

## 8. Ejecutar el sistema

Se requieren DOS terminales separadas (o ejecutar los scripts .ps1 en paralelo). La API DEBE levantarse primero, luego el dashboard.

### 8.1 Terminal 1 - Ejecutar la API

**Carpeta desde donde ejecutar:** `solucion_local_sai_f3\`

**Comando real:**
```powershell
.venv\Scripts\Activate.ps1
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir api --reload-dir package_src
```

O de forma mas sencilla usando el script incluido:
```powershell
.\run_api.ps1
```

**Datos importantes de la API:**
- Puerto: `8000`
- Direccion local: `http://127.0.0.1:8000`
- Endpoint principal (root): `http://127.0.0.1:8000/`
- Endpoint de salud: `http://127.0.0.1:8000/health`
- Documentacion automatica FastAPI (Swagger UI): `http://127.0.0.1:8000/docs`
- Documentacion alternativa Redoc: `http://127.0.0.1:8000/redoc`

**Como comprobar que la API esta funcionando:**
Abre en el navegador `http://127.0.0.1:8000/health`. Debe retornar un JSON con `status: "ok"`, `package_version: "0.1.0"` y los modelos disponibles (`Narino`, `Quindio`).

### 8.2 Terminal 2 - Ejecutar el dashboard

**Carpeta desde donde ejecutar:** `solucion_local_sai_f3\`

**Comando real:**
```powershell
.venv\Scripts\Activate.ps1
streamlit run dashboard\app.py --server.headless true --server.port 8501 --server.address 127.0.0.1 --server.maxUploadSize 2 --browser.gatherUsageStats false
```

O de forma mas sencilla usando el script incluido:
```powershell
.\run_dashboard.ps1
```

**Datos importantes del dashboard:**
- Puerto: `8501`
- Direccion para abrir en el navegador: `http://127.0.0.1:8501`

---

## 9. Ejemplo de uso

En este ejemplo se realiza una prediccion de rendimiento para Narino, a o 2015 (punto de control golden).

### Flujo completo

```
Entrada (usuario en el dashboard)
        |
        v  (usuario selecciona Narino y precarga 2015 en sidebar)
Dashboard Streamlit (:8501)
        |  (HTTP POST a /api/v1/predict/rendimiento)
        |  Body JSON FLAT:
        |     {"departamento": "Narino",
        |      "spi3_floracion": -0.0262,
        |      "spi3_desarrollo": -0.8443,
        |      "spi3_cosecha": -0.9861,
        |      "tmax_mean_e9": 20.21,
        |      "oni_mean": 1.5483,
        |      "roya_dummy": 0}
        v
API FastAPI (:8000)
        |  (pkg.predict_rendimiento)
        v
Modelo ExtraTreesRegressor .joblib (Narino)
        |
        v
Resultado: prediccion_kg_ha = 1085.3514506746224
        |
        v
API FastAPI (responde JSON 200 OK)
        |
        v
Dashboard (modulo 3 Track B):
  - Muestra valor numerico 1,085.35 kg/ha
  - Consulta Q1/Q3 historico Narino (Q1=992.2, Q3=1093.2)
  - 1085.35 esta entre Q1 y Q3 -> Semaforo MEDIO (naranja)
  - Muestra delta vs media historica y variables fenologicas
```

### Otros tipos de prediccion disponibles

- **Track A SPI**: Determina si para un ano/departamento dado se activa el seguro (5 reglas OR: sequia anual, sequia enneagro, sequia en cosecha, mas de 2 meses de sequia en enneagro, o roya shock).
- **Validacion historica**: Verifica que 2 eventos conocidos (Roya 2012 y Nino 2015) activan el seguro correctamente en ambos departamentos.
- **Calculadora actuarial**: Calcula prima, indemnizaciones y balance para N anos a partir de hectareas aseguradas y pago por evento.

---

## 10. Solucion de problemas

### 10.1 Error de dependencia: ModuleNotFound

**Sintoma:** Al ejecutar API o dashboard aparece `ModuleNotFoundError: No module named 'fastapi'` (o cualquier otra libreria).

**Solucion:**
```powershell
cd solucion_local_sai_f3
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 10.2 Error de entorno virtual: no existe .venv

**Sintoma:** `El sistema no puede encontrar la ruta especificada .venv\Scripts\...`

**Solucion:** Vuelve a crear el entorno virtual desde cero:
```powershell
cd solucion_local_sai_f3
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install dist\cafe_sai_modelos_equipo9-0.1.0-py3-none-any.whl
```

### 10.3 La API no responde desde el dashboard

**Sintoma:** El dashboard muestra "La API local no responde" en color amarillo.

**Solucion:** Primero debes ejecutar la API. Abre otra terminal y corre:
```powershell
cd solucion_local_sai_f3
.venv\Scripts\Activate.ps1
.\run_api.ps1
```
Espera 10-15 segundos a que los modelos se carguen y luego refresca el dashboard (F5).

**Comprobacion:** Abre `http://127.0.0.1:8000/health` en el navegador. Si muestra JSON con `"status":"ok"`, la API esta bien. Si no, revisa que el puerto 8000 no este ocupado por otra aplicacion.

### 10.4 El dashboard no obtiene predicciones (HTTP 422 Unprocessable Entity)

**Solucion:** Verifica que la URL base de la API sea la correcta. Por defecto es `http://127.0.0.1:8000`. Si cambiaste el puerto en run_api.ps1, definelo antes de ejecutar el dashboard:
```powershell
$env:SAI_API_BASE = "http://127.0.0.1:PUERTO_NUEVO"
.\run_dashboard.ps1
```

### 10.5 Error "No se encontro models_artifacts"

**Sintoma:** `FileNotFoundError: No se encontro models_artifacts. Setea CAFE_SAI_MODELS_DIR...`

**Solucion:** Define la variable de entorno apuntando a la carpeta correcta (el script `run_api.ps1` ya lo hace automaticamente):
```powershell
$env:CAFE_SAI_MODELS_DIR = "ruta\completa\solucion_local_sai_f3\models_artifacts"
```

---

## 11. Portabilidad y ejecucion en otros computadores

Esta implementacion fue disenada especificamente para ser portable entre distintos computadores del equipo. Se garantiza lo siguiente:

1. **No se utilizan rutas absolutas hardcodeadas.** Ningun archivo distribuible (package, API, dashboard, scripts .ps1, pyproject.toml, requirements.txt, documentacion) contiene referencias a `C:\Users\...`, `OneDrive\...`, `Desktop\...` o `Documents\...`.
2. **No depende del usuario que desarrollo el proyecto.** No existen referencias a nombres de usuario especificos en el codigo de distribucion.
3. **Los archivos se resuelven mediante rutas relativas / dinamicas.**
   - El cargador de modelos (`loader.py`) usa `Path(__file__).resolve().parent.parent.parent / "models_artifacts"` para inferir automaticamente la ubicacion.
   - La API (`api/main.py`) usa `Path(__file__).resolve().parent.parent` como raiz.
   - Los scripts `.ps1` usan `Split-Path -Parent $MyInvocation.MyCommand.Path` para determinar la carpeta del proyecto independientemente de donde este ubicado.
4. **Las dependencias estan completamente documentadas** en `requirements.txt` (lista completa con versiones) y en `pyproject.toml` (PEP 621 con extras opcionales api, dashboard, dev, all).
5. **El proyecto puede ubicarse en cualquier carpeta** de cualquier unidad (`C:`, `D:`, unidad de red, etc.). El comportamiento es identico.
6. **Otro integrante puede crear su propio entorno virtual** siguiendo la seccion 7 de este documento, sin necesidad de editar ninguna linea de codigo.

---

## 12. Checklist final

### 12.1 Dashboard

[x] Los numeros de los KPI tienen un tamano mas pequeno (ajuste CSS 1.45rem valor numerico, 0.9rem etiqueta).
[x] Los valores de los KPI no fueron modificados (solo presentacion).
[x] Los calculos no fueron modificados.
[x] El diseno general permanece consistente con el mockup Mockup_Panel_Fase3.pdf.

### 12.2 Modelos

[x] No se modificaron.
[x] No se modificaron parametros.
[x] No se modificaron variables.
[x] No se modificaron resultados.

### 12.3 Portabilidad

[x] No existen rutas absolutas en archivos distribuidos.
[x] No existe ninguna referencia a mi usuario de Windows en archivos distribuidos.
[x] No existe ninguna referencia a mi Desktop.
[x] No existe ninguna referencia a mis Documents.
[x] No existe ninguna referencia a OneDrive personal en el codigo.
[x] No existen rutas `C:\Users\...` hardcodeadas fuera de la carpeta tests/.
[x] Las rutas son relativas / dinamicas (Path(__file__) en Python, $MyInvocation en PowerShell).
[x] Las dependencias estan documentadas en requirements.txt y pyproject.toml.

### 12.4 Ejecucion

[x] Se puede crear un entorno virtual con `python -m venv .venv`.
[x] Se pueden instalar las dependencias con `pip install -r requirements.txt`.
[x] Se puede instalar el .whl: `pip install dist\cafe_sai_modelos_equipo9-0.1.0-py3-none-any.whl`.
[x] Se puede iniciar la API: `uvicorn api.main:app --host 127.0.0.1 --port 8000`.
[x] Se puede iniciar el dashboard: `streamlit run dashboard\app.py --server.port 8501`.
[x] Se puede realizar una prediccion de rendimiento y una activacion SPI.

### 12.5 Documentacion

[x] Explica que se hizo (objetivo + proceso 6 pasos).
[x] Explica como funciona la arquitectura de 5 capas (Modelos -> Package -> API -> Dashboard -> Usuario).
[x] Explica como instalarlo (7 pasos desde cero: copy -> cd -> venv -> activate -> pip upgrade -> requirements -> wheel).
[x] Explica como ejecutar la API (comando real, puerto 8000, /health, /docs).
[x] Explica como ejecutar el dashboard (comando real, puerto 8501).
[x] Explica como utilizarlo (ejemplo prediccion Narino 2015).
[x] Explica como ejecutarlo en otro computador (seccion portabilidad + pasos 7 + 8).
