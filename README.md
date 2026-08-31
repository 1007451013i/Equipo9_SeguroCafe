# Seguro Agrícola Indexado de Café — Quindío y Nariño — Equipo 9

**Universidad de los Andes · MIAD · 2026 · Proyecto Aplicado en Analítica de Datos**

---

## Contexto del Proyecto

Menos del 3% del área cafetera colombiana cuenta con seguro agrícola. Los seguros tradicionales dependen de ajustadores de campo para verificar pérdidas individuales, lo cual los hace prohibitivamente costosos para pequeños caficultores. Este proyecto diseña y valida un **seguro indexado** basado en el índice climático SPI-3 (Standardized Precipitation Index, escala 3 meses, McKee et al. 1993) que activa pagos automáticamente cuando la precipitación cruza umbrales predefinidos por departamento, eliminando costos de ajuste y Riesgo Moral.

El modelo cubre los departamentos de **Quindío y Nariño** (Colombia) con datos históricos 2000-2024 y opera en dos ejes complementarios:

| Eje | Pregunta central |
|-----|-----------------|
| **A — Índice SPI-3** | ¿Qué umbrales de precipitación activan el pago? |
| **B — Rendimiento** | ¿El índice climático predice pérdidas reales de café (kg/ha)? |

---

## Entregables Realizados

### Fase 1 (entregada semanas anteriores)
- `../Fase1/Prototipo_Fachada_Equipo9.pdf` — Prototipo de fachada con flujos de usuario y arquitectura del sistema
- `../Fase1/Tabla_de_Requerimientos_Equipo 9.pdf` — Tabla de requerimientos funcionales y no funcionales con criterios de aceptación

### Fase 2 (Entrega semana 5 — 30% del proyecto · Domingo 6 septiembre 2026)
- **Repositorio técnico (esta carpeta):** ETL, Pipeline de 4 modelos, Notebook principal, 11 CSVs de resultados, 6 PNGs de validación.
- **Reporte entregable MIAD (carpeta `../Entregables_Fase2_Equipo9/`):** 9 secciones alineadas 1:1 con la rúbrica de 6 puntos.
- **Guía para el equipo (carpeta entregables):** explicación sencilla de todo el pipeline.
- **Checklist rúbrica (carpeta entregables):** tabla detallada 6 puntos con lo que evalúa el profesor.

---

## Instalación y Reproducción

### Método 1 — One-Click (Recomendado para profesor / revisor)
> **No necesita Python instalado. No necesita permisos de administrador. No necesita Google Colab.**
>
> **Paso único:** doble clic sobre el archivo:
> ```
> ejecutar_pipeline_equipo9.cmd
> ```
>
> Automáticamente realiza en ~10 minutos:
> 1. Usa el intérprete Python 3.11.9 portable incluido en `python_portable/`
> 2. Instala las 10 dependencias con versiones exactas definidas en `requirements.txt`
> 3. Ejecuta el ETL (`etl_equipo9.py`) → 8 CSVs en `data/processed/`
> 4. Ejecuta el pipeline de modelos (`pipeline_equipo9.py`) → 11 CSVs + 6 PNGs de validación
> 5. Guarda un resumen final en el archivo `_ESTADO.txt` y logs detallados en `logs/`
>
> Sin interacción del usuario. Sin PAUSE. Sin ventanas colgadas.

### Método 2 — Desarrolladores (Python 3.11.x global o venv)
```bash
# 1. Descargar / clonar este repositorio
cd Equipo9_SeguroCafe_GitHub

# 2. Crear entorno virtual (Python 3.11.x recomendado)
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux:    source .venv/bin/activate

# 3. Instalar dependencias con versiones exactas (ABI numpy/scipy coherente)
pip install --only-binary=:all: -r requirements.txt

# 4. Ejecutar ETL + Pipeline
python etl_equipo9.py
python pipeline_equipo9.py

# 5. Opcional: explorar resultados en el notebook
jupyter notebook notebooks/seguro_cafe_pipeline_equipo9.ipynb
```

---

## Datos — Fuentes Públicas

| Fuente | Cobertura | Propósito |
|--------|-----------|-----------|
| **ERA5 Copernicus** (Consolidado diario 0.25°) | 2000-2024 · 2 departamentos | Precipitación grilla → cálculo del SPI-3 (ventanas fenológicas floración/desarrollo/cosecha) |
| **EVA MADR** (Encuesta Nacional Cafetera datos.gov.co) | 2007-2024 · municipal → agregado departamental | Variable respuesta: **Rendimiento kg/ha**, producción t, área cosechada ha |
| **NOAA CPC** ONI ENSO | 1950-2026 · trimestral DJF/MAM/JJA/SON | Índice El Niño/La Niña rezagado 1 año → interacción clima global |
| **Federación Nacional de Cafeteros FNC** | 1944-2026 · anual | Precio COP/carga 125 kg + rezagos t−1, t−2 y ratios |
| **Avelino et al. 2015** + extensión climática | 2012-2024 anual | Dummy fitosanitario efecto roya café (epidemia 2012-2014) |
| **IDEAM** Red ECA | 2000-2024 anual · 2 departamentos | Temperatura máxima, media, mínima aire; anomalías HR; radiación solar |
| **NASA MODIS MOD13Q1** NDVI 250m 16días | 2000-2024 anual/mensual · 2 departamentos | Índice vegetación NDVI (vigencia del cultivo) |

---

## Estructura del Repositorio

```
Equipo9_SeguroCafe_GitHub/
├── python_portable/                  # Intérprete Python 3.11.9 embeddable (método 1 one-click)
│   ├── python.exe
│   └── Lib/site-packages/            # 10 dependencias PINNADAS
├── data/
│   ├── raw/                          # 16 archivos ORIGINALES (ERA5, EVA, NOAA, FNC, IDEAM, MODIS, Roya)
│   └── processed/                    # 8 CSVs generados por el ETL
│       ├── oni_anual_equipo9.csv           # ONI NOAA anual
│       ├── eva_municipal_equipo9.csv       # Rendimiento kg/ha (EVA MADR)
│       ├── precios_df_equipo9.csv          # Precio FNC COP/carga + rezagos
│       ├── roya_df_equipo9.csv             # Dummy roya 2012-14 extendida
│       ├── tmax_anual_equipo9.csv          # T máxima aire IDEAM
│       ├── tmedia_anual_equipo9.csv        # T media IDEAM
│       ├── clima_anual_spi3_equipo9.csv    # SPI-3 McKee 1993 · 3 ventanas fenológicas
│       └── features_modelo_equipo9.csv     # PANEL FINAL · 36 obs (18a × 2d) · 36 vars
├── notebooks/
│   ├── seguro_cafe_pipeline_equipo9.ipynb  # Notebook principal · 31 cells
│   └── outputs/                            # 11 CSVs de resultados del pipeline
│       ├── umbrales_departamento_equipo9.csv
│       ├── validacion_historica_spi3_equipo9.csv
│       ├── N2_ols_bivariado_equipo9.csv
│       ├── d1_holdout_metrics_equipo9.csv
│       ├── shap_importancia_permutacion_equipo9.csv
│       ├── predicciones_loyo_equipo9.csv
│       ├── supuestos_ridge_equipo9.csv
│       ├── kpis_resumen_equipo9.csv
│       ├── prima_hedging_equipo9.csv
│       ├── tabla_requerimientos_dashboard_equipo9.csv
│       └── correlaciones_top_equipo9.csv
├── outputs/                           # 6 figuras PNG de validación
│   ├── spi3_series_equipo9.png
│   ├── predicciones_vs_real_equipo9.png
│   ├── permutation_importance_top8_equipo9.png
│   ├── correlaciones_top15_equipo9.png
│   ├── spi3_vs_rendimiento_scatter_equipo9.png
│   └── kpis_resumen_barplot_equipo9.png
├── src/
│   └── utils.py                       # Módulos reutilizables (futura API P3)
├── etl_equipo9.py                     # ETL 8 pasos · Extracción/Transformación/Carga
├── pipeline_equipo9.py                # Modelado · 4 modelos · Validación · Figuras
├── ejecutar_pipeline_equipo9.cmd      # ✅ ONE-CLICK PROFESOR
├── requirements.txt                   # 10 dependencias CON versiones exactas
├── _ESTADO.txt                        # (Generado al ejecutar) Progreso 0%..100% + resumen final
├── logs/                              # (Generado al ejecutar) logs pip · etl · pipeline
├── .gitignore                         # Reglas Git (venv, __pycache__, .DS_Store)
└── README.md                          # Este archivo
```

---

## Ejecución del Pipeline

El script `pipeline_equipo9.py` procesa el panel de modelado en seis secciones secuenciales:

1. **Configuración** · imports · rutas · semilla `SEED = 2026` (reproducibilidad)
2. **Partición anti-leakage** · Train = 2007-2018 · **Hold-out = 2019-2020** (2 años temporales, nunca visto en selección) · **LOYO CV 18-folds** (Leave-One-Year-Out)
3. **Track A** · cálculo umbrales P10/P90 SPI-3 por departamento · validación histórica eventos extremos · OLS bivariado Rend ~ SPI-3
4. **Track B** · 4 modelos predictivos (RidgeCV, LassoCV, RandomForest, ExtraTrees) · LOYO selección · Hold-out evaluación final · Permutation Importance (B=6 reps, Top-8 variables)
5. **Supuestos Regresión Lineal Ridge LOYO (S1-S5)** · Linealidad · Multicolinealidad VIF · Normalidad Shapiro+JB · Autocorrelación Durbin-Watson · Homocedasticidad Spearman
6. **Cálculo Actuarial Financiero** · Hedging Effectiveness (HE) · Prima actuarial justa · Riesgo Base CV · Pago indemnización por hectárea · guardado CSV/PNG

---

## Resumen de Resultados Clave

### Track A — Umbrales del Índice
| Departamento | Umbral sequía P10 (activa pago) | Umbral exceso lluvia P90 (activa pago) | Eventos extremos 2000-2024 |
|---|---|---|---|
| Nariño | **[[TOFILL_UMBRAL_N_P10]]** | **[[TOFILL_UMBRAL_N_P90]]** | **[[TOFILL_N1_N_TOT]]** |
| Quindío | **[[TOFILL_UMBRAL_Q_P10]]** | **[[TOFILL_UMBRAL_Q_P90]]** | **[[TOFILL_N1_Q_TOT]]** |
| **Total** | | | **[[TOFILL_N1_GLOBAL]]** |

### Track B — Modelos predictivos de Rendimiento (Hold-out = 2019-2020)
| Modelo | RMSE [kg/ha] | R² | MAPE [%] | ΔR² LOYO vs HO |
|--------|--------------|----|----------|----------------|
| RidgeCV | [[TOFILL_D1_RMSE_RIDGE]] | [[TOFILL_D1_R2_RIDGE]] | [[TOFILL_D1_MAPE_RIDGE]] | [[TOFILL_D3_DR2_RIDGE]] |
| LassoCV | [[TOFILL_D1_RMSE_LASSO]] | [[TOFILL_D1_R2_LASSO]] | [[TOFILL_D1_MAPE_LASSO]] | [[TOFILL_D3_DR2_LASSO]] |
| Random Forest | [[TOFILL_D1_RMSE_RF]] | [[TOFILL_D1_R2_RF]] | [[TOFILL_D1_MAPE_RF]] | [[TOFILL_D3_DR2_RF]] |
| **ExtraTrees (seleccionado)** | **[[TOFILL_D1_RMSE_ET]]** | **[[TOFILL_D1_R2_ET]]** | **[[TOFILL_D1_MAPE_ET]]** | **[[TOFILL_D3_DR2_ET]]** |

### Supuestos Regresión Lineal Ridge LOYO (S1-S5)
| ID · Supuesto | Prueba | Estadístico | p-valor | Cumple |
|----------|------|--------|---------|--------|
| S1 Linealidad | corr(ŷ, y) | r = **[[TOFILL_S1_R]]** | **[[TOFILL_S1_P]]** | **[[TOFILL_S1_PASS]]** |
| S2 No Multicolinealidad | VIF máx top-8 | VIF = **[[TOFILL_S2_VIFMAX]]** | — | **[[TOFILL_S2_PASS]]** |
| S3 Normalidad ε | Shapiro-Wilk | W = **[[TOFILL_S3_SW]]** | **[[TOFILL_S3_PSW]]** | **[[TOFILL_S3_PASS]]** |
| S4 No Autocorrelación | Durbin-Watson | DW = **[[TOFILL_S4_DW]]** | aprox tabla | **[[TOFILL_S4_PASS]]** |
| S5 Homocedasticidad | Spearman \|ε\| vs ŷ | ρ = **[[TOFILL_S5_RHO]]** | **[[TOFILL_S5_P]]** | **[[TOFILL_S5_PASS]]** |

### Cálculo Actuarial Financiero
| Indicador | Valor | Objetivo |
|---|---|---|
| **Hedging Effectiveness HE** | **[[TOFILL_HE]]** | ≥ 0.20 (reduce volatilidad ingreso cafetero) |
| **Reducción Volatilidad** | **[[TOFILL_HE_PCT]]** % | ≥ 20% |
| **Prima actuarial justa** | **[[TOFILL_PRIMA]]** % del ingreso anual / ha | ≤ 5% (viable mercado) |
| **Prima final (gastos 15%)** | **[[TOFILL_PRIMA_FINAL]]** % | ≤ 6% |
| **Riesgo Base CV** | **[[TOFILL_RB_CV]]** | < 0.20 (ingreso estable post-cobertura) |

> Los valores se rellenan automáticamente al ejecutar el pipeline.

---

## Cumplimiento Requerimientos Fase 1

| ID | Requerimiento | Cumple | Evidencia CSV |
|----|---------------|--------|---------------|
| N1 | Validación histórica ≥ 8 eventos SPI-3 extremos | **[[TOFILL_N1_PASS]]** | tabla_requerimientos_dashboard_equipo9.csv |
| N2 | Poder predictivo R²-ajust OLS ≥ 0.25 | **[[TOFILL_N2_PASS]]** | N2_ols_bivariado_equipo9.csv |
| N3 | Frecuencia activación 1-3 eventos/década | **[[TOFILL_N3_PASS]]** | umbrales_departamento_equipo9.csv |
| N4 | Umbrales P10/P90 DIFERENCIALES por depto | **[[TOFILL_N4_PASS]]** | umbrales_departamento_equipo9.csv |
| D1 | RMSE Hold-out ≤ 186 kg/ha | **[[TOFILL_D1_PASS]]** | d1_holdout_metrics_equipo9.csv |
| D2 | Coherencia Top-3 PermImp ≥ 60% LOYO/HO | **[[TOFILL_D2_PASS]]** | shap_importancia_permutacion_equipo9.csv |
| D3 | ΔR² LOYO vs HO < 0.15 (estabilidad temporal) | **[[TOFILL_D3_PASS]]** | kpis_resumen_equipo9.csv |
| D4 | ΔR² vs RBIM ≤ 0.10 (valor agregado ML) | **[[TOFILL_D4_PASS]]** | kpis_resumen_equipo9.csv |

---

## Equipo 9 — MIAD 2026 · Universidad de los Andes

| Integrante | Rol Fase 2 |
|-----------|-------------------|
| Miembro 1 | Datos + ETL + Integraciones · `etl_equipo9.py` · 8 CSVs processed · unificación departamentos · runtime python_portable one-click |
| Miembro 2 | Modelado predictivo + Documentación · `pipeline_equipo9.py` · LOYO CV · Hold-out 2019-2020 · 4 modelos comparación · KPIs reales en docs |
| Miembro 3 | Estadística + Visualizaciones + UX · Pruebas S1-S5 · KS Gamma · VIF · HE y cálculo prima actuarial · Notebook 31 celdas · 6 PNGs |
| Miembro 4 | Líder + Entregables + GitHub · CMD one-click `ejecutar_pipeline_equipo9.cmd` · inventario archivos · reportes · PDFs finales · `git init`/commit/push · entrega Bloque Neón |

---

## Referencias
1. McKee TB, Doesken NJ, Kleist J. *The relationship of drought frequency and duration to time scales*. 8th Conf. Appl. Climatol., 1993.
2. Copernicus Climate Change Service C3S. ERA5-Land hourly data 1950-present. ECMWF, 2024. DOI 10.24381/cds.e2161bac.
3. MADR / Datos Abiertos Colombia. Encuesta Nacional Cafetera EVA 2007-2024.
4. NOAA Climate Prediction Center. Oceanic Niño Index ONI. 1950-2026.
5. Federación Nacional de Cafeteros de Colombia (Oficina Económica). Precios Internos y Externos 1944-2026.
6. Avelino J et al. *The coffee rust crises in Colombia and Central America (2008–2013)*. Food Security 7(2): 303–321, 2015.
7. IDEAM. Red ECA Nacional — Anomalías T, HR, Radiación. 2000-2024.
8. NASA LP DAAC. MOD13Q1 MODIS Vegetation Indices 250m. 2024. DOI 10.5067/MODIS/MOD13Q1.061.
9. Geurts P, Ernst D, Wehenkel L. *Extremely Randomized Trees*. Machine Learning 63(1): 3–42, 2006.
10. Breiman L. *Random Forests*. Machine Learning 45(1): 5–32, 2001.
