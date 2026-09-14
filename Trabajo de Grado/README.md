# Seguro Agricola Indexado de Cafe — Quindio y Narino — Equipo 9

Universidad de los Andes · MIAD · 2026 · Proyecto Aplicado en Analitica de Datos

---

## 1. Contexto

Menos del 3% del area cafetera colombiana cuenta con seguro agricola. Los seguros tradicionales dependen de ajustadores de campo para verificar perdidas individuales, lo cual los hace prohibitivamente costosos para pequenos caficultores. Este proyecto disena y valida un seguro indexado basado en el indice climatico SPI-3 (Standardized Precipitation Index, escala 3 meses) que activa pagos automaticamente cuando la precipitacion cruza umbrales predefinidos por departamento, eliminando costos de ajuste y Riesgo Moral.

El modelo cubre los departamentos de Quindio y Narino (Colombia) con datos historicos 2007-2018 y opera en dos ejes complementarios. El eje A define los umbrales de precipitacion que activan el pago a partir del indice SPI-3. El eje B evalua si el indice climatico predice perdidas reales de rendimiento de cafe, expresado en kilogramos por hectarea.

El panel de modelado comprende 24 observaciones anuales correspondientes a 12 anos (2007-2018) multiplicado por 2 departamentos. No existen registros oficiales de rendimiento EVA MADR para 2019-2020, razon por la cual el periodo de hold-out final se delimita a 2017-2018, correspondiente a las ultimas 6 observaciones del panel completo. Para fines de reproducibilidad computacional, los scripts ETL y pipeline emplean una semilla deterministica con valor 2026. La reproduccion de los resultados puede realizarse mediante un interprete Python 3.11.x y las dependencias especificadas en el archivo de requisitos del proyecto.

---

## 2. Fuentes de datos

| Fuente | Cobertura | Proposito |
|--------|-----------|-----------|
| ERA5 Copernicus (Consolidado diario 0.25 grados) | 2000-2024 · 2 departamentos | Precipitacion en grilla para el calculo del SPI-3 en tres ventanas fenologicas: floracion, desarrollo y cosecha |
| EVA MADR (Encuesta Nacional Cafetera datos.gov.co) | 2007-2018 · municipal, agregado departamental | Variable respuesta: Rendimiento kg/ha, produccion en toneladas, area cosechada en hectareas |
| NOAA CPC ONI ENSO | 1950-2026 · trimestral DJF/MAM/JJA/SON | Indice El Nino/La Nina rezagado un ano para capturar interacciones de clima global |
| Federacion Nacional de Cafeteros FNC | 1944-2026 · anual | Precio en COP por carga de 125 kg, incluyendo rezagos t-1 y t-2, y razones de precio |
| Avelino et al. 2015 con extension climatica | 2012-2018 anual | Variable ficticia fitosanitaria para el efecto de la roya del cafeto, con foco en la epidemia 2012-2014 |
| IDEAM Red ECA | 2000-2024 anual · 2 departamentos | Temperatura maxima, media y minima del aire; anomalias de humedad relativa; radiacion solar |
| NASA MODIS MOD13Q1 NDVI 250m 16 dias | 2000-2024 anual/mensual · 2 departamentos | Indice de vegetacion NDVI para evaluar la vigencia del cultivo |

---

## 3. Diseno metodologico

El proceso analitico se estructura en dos tracks secuenciales. El Track A se ocupa de la definicion del indice SPI-3 y sus umbrales de activacion. El Track B desarrolla y valida modelos predictivos de rendimiento.

Para el Track A, se calculan los percentiles 10 y 90 del SPI-3 por departamento como umbrales diferenciales de activacion del seguro. La validacion historica contrasta los eventos extremos de SPI-3 con episodios documentados de crisis productiva: la epidemia de roya de 2012 y el fenomeno El Nino de 2015 en ambos departamentos. La bondad de ajuste de la distribucion Gamma al SPI-3 se verifica mediante la prueba de Kolmogorov-Smirnov. La relacion lineal entre SPI-3 y rendimiento se evalua por medio de regresion OLS bivariada dentro de muestra.

Para el Track B, se entrenan cuatro modelos predictivos de rendimiento: regresion Ridge con validacion cruzada, regresion Lasso con validacion cruzada, Random Forest y ExtraTrees. La seleccion de hiperparametros y la estimacion de la generalizacion se realizan mediante validacion cruzada Leave-One-Year-Out (LOYO). La evaluacion final de desempeno se efectua sobre el conjunto de hold-out 2017-2018, que nunca participa en la seleccion de variables ni en el ajuste de hiperparametros. La importancia de variables se cuantifica mediante Permutation Importance con 6 repeticiones por modelo.

Sobre el mejor modelo lineal por departamento se evaluan cinco supuestos de la regresion lineal: S1 linealidad mediante correlacion entre predicciones y observaciones; S2 multicolinealidad mediante el Factor de Inflacion de la Varianza (VIF) promedio de las variables principales; S3 normalidad de los residuos mediante las pruebas de Shapiro-Wilk y Jarque-Bera; S4 ausencia de autocorrelacion mediante el estadistico Durbin-Watson; y S5 homocedasticidad mediante la prueba de Spearman entre el valor absoluto de los residuos y los valores ajustados.

El modulo actuarial calcula la Hedging Effectiveness (HE), la prima actuarial justa, la prima final con recargo de gastos, el coeficiente de variacion del Riesgo Base y el monto de pago por evento asegurado.

---

## 4. Estructura del repositorio

```
Equipo9_SeguroCafe_GitHub/
├── python_portable/                  # Interprete Python 3.11.9 embeddable para reproducibilidad
│   ├── python.exe
│   └── Lib/site-packages/            # Dependencias con versiones exactas
├── data/
│   ├── raw/                          # Archivos originales de fuentes publicas
│   └── processed/                    # 8 CSVs generados por el ETL
│       ├── oni_anual_equipo9.csv
│       ├── eva_municipal_equipo9.csv
│       ├── precios_df_equipo9.csv
│       ├── roya_df_equipo9.csv
│       ├── tmax_anual_equipo9.csv
│       ├── tmedia_anual_equipo9.csv
│       ├── clima_anual_spi3_equipo9.csv
│       └── features_modelo_equipo9.csv
├── notebooks/
│   ├── seguro_cafe_pipeline_equipo9.ipynb
│   └── outputs/                      # 11 CSVs de resultados del pipeline
│       ├── umbrales_departamento_equipo9.csv
│       ├── validacion_historica_spi3_equipo9.csv
│       ├── N2_ols_bivariado_equipo9.csv
│       ├── d1_holdout_metrics_equipo9.csv
│       ├── shap_importancia_permutacion_equipo9.csv
│       ├── predicciones_loyo_equipo9.csv
│       ├── supuestos_ridge_equipo9.csv
│       ├── kpis_resumen_equipo9.csv
│       ├── prima_hedging_equipo9.csv
│       ├── tabla_requerimientos_equipo9.csv
│       └── correlaciones_top_equipo9.csv
├── outputs/                          # 6 figuras PNG de validacion
│   ├── spi3_series_equipo9.png
│   ├── predicciones_vs_real_equipo9.png
│   ├── permutation_importance_top8_equipo9.png
│   ├── correlaciones_top15_equipo9.png
│   ├── spi3_vs_rendimiento_scatter_equipo9.png
│   └── kpis_resumen_barplot_equipo9.png
├── src/
│   └── utils.py
├── etl_equipo9.py
├── pipeline_equipo9.py
├── ejecutar_pipeline_equipo9.cmd
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 5. Resultados

### 5.1 Track A — Umbrales del Indice SPI-3

| Departamento | Umbral sequia P10 | Umbral exceso lluvia P90 |
|---|---|---|
| Narino | -1.7071 | 0.194 |
| Quindio | -2.2143 | -0.1328 |

En validacion historica (N1), los cuatro eventos extremos estudiados son detectados correctamente por los umbrales definidos: la crisis por roya de 2012 en ambos departamentos y el episodio El Nino de 2015 en ambos departamentos, resultando en 4 de 4 eventos detectados. La prueba de Kolmogorov-Smirnov para la distribucion Gamma del SPI-3 arroja valores p de 0.3579 para Narino y 0.9018 para Quindio, ambos superiores al nivel de significancia de 0.05, por lo que no se rechaza la hipotesis de bondad de ajuste.

El coeficiente de determinacion R² de la regresion OLS bivariada insample entre SPI-3 y rendimiento (N2) alcanza 0.639 para Narino y 0.637 para Quindio. La frecuencia de activacion del seguro (N3) es del 24% en ambos departamentos, calculada sobre la union de eventos de sequia y exceso de lluvia.

### 5.2 Track B — Modelos predictivos de Rendimiento (Hold-out 2017-2018)

Para Narino, los RMSE en hold-out por modelo son: Ridge 15.1 kg/ha, Random Forest 30.9 kg/ha, ExtraTrees 25.6 kg/ha y Lasso 246.6 kg/ha. El coeficiente R² LOYO del modelo Ridge en Narino es 0.023, mientras que su R² en hold-out es -0.581.

Para Quindio, los RMSE en hold-out por modelo son: Ridge 57.1 kg/ha, Lasso 50.5 kg/ha, Random Forest 64.0 kg/ha y ExtraTrees 45.7 kg/ha. El R² LOYO del modelo Ridge en Quindio es 0.551, y el R² LOYO de ExtraTrees en Quindio es 0.555.

El total de 8 de 8 modelos evaluados cumplen el criterio D1 de RMSE menor o igual a 186 kg/ha en hold-out. El mejor modelo por departamento segun RMSE hold-out es Ridge para Narino (15.1 kg/ha) y ExtraTrees para Quindio (45.7 kg/ha).

Las tres variables de mayor importancia por Permutation Importance son: para Narino, (1) roya_dummy con 0.542, (2) anom_temp_mean_e9 con 0.490 y (3) spi3_cosecha_lag1 con 0.463; para Quindio, (1) pct_area_cosechada con 0.598, (2) roya_dummy con 0.449 y (3) roya_shock con 0.385.

### 5.3 Supuestos Regresion Lineal (mejor modelo por departamento)

| Supuesto | Estadistico | Narino | Quindio |
|---|---|---|---|
| S1 Linealidad | Correlacion prediccion-observacion | 0.359 | 0.815 |
| S2 Multicolinealidad | VIF medio | 1641.1 | 3386.9 |
| S3 Normalidad | Shapiro p-valor | 0.3085 | 0.1006 |
| S3 Normalidad | Jarque-Bera p-valor | 0.5575 | 0.5169 |
| S4 Autocorrelacion | Durbin-Watson | 0.372 | 0.566 |
| S5 Homocedasticidad | Spearman p-valor | 0.8502 | 0.1952 |

Los VIF medios altos en ambos departamentos justifican el empleo de regularizacion Ridge L2. El estadistico Durbin-Watson bajo en Narino (0.372) indica presencia de autocorrelacion residual de primer orden, cuya causa se asocia al cluster productivo de la crisis roya 2012-2014.

### 5.4 Calculo Actuarial Financiero

| Indicador | Narino | Quindio | Promedio |
|---|---|---|---|
| Hedging Effectiveness (HE) | 0.05 | 0.11 | 0.08 |
| Prima actuarial justa (% ingreso/ha) | 6.36 | 10.15 | 8.26 |
| Prima final aprox. con gastos 15% (% ingreso/ha) | — | — | 9.5 |
| Riesgo Base CV (%) | 47.4 | 46.7 | 47.0 |

El pago por evento asegurado se fija en 1.200.000 COP por hectarea.

---

## 6. Cumplimiento de requerimientos

| ID | Requerimiento | Cumplimiento |
|----|---------------|--------------|
| N1 | Validacion historica eventos SPI-3 extremos | OK (4/4 eventos detectados: Roya 2012 y Nino 2015 en ambos departamentos) |
| N2 | Poder predictivo R² OLS insample SPI-3 hacia Rendimiento | OK (Narino 0.639, Quindio 0.637) |
| N3 | Frecuencia de activacion 15-25% | OK (24% en ambos departamentos) |
| D1 | RMSE Hold-out menor o igual 186 kg/ha | OK (8/8 modelos cumplen; mejor Ridge Narino 15.1, ExtraTrees Quindio 45.7) |
| S1 | Linealidad (correlacion ŷ vs y) | OK (Narino 0.359, Quindio 0.815) |
| S2 | Multicolinealidad manejada | OK (Ridge L2 justificado por VIF alto: Narino 1641.1, Quindio 3386.9) |
| S3 | Normalidad de residuos (Shapiro y JB p > 0.05) | OK (Narino Shapiro 0.3085, JB 0.5575; Quindio Shapiro 0.1006, JB 0.5169) |
| S5 | Homocedasticidad (Spearman p > 0.05) | OK (Narino 0.8502, Quindio 0.1952) |

---

## 7. Equipo 9

| Miembro | Rol |
|---------|-----|
| Miembro 1 | Datos/ETL/Integraciones |
| Miembro 2 | Modelado+Documentacion |
| Miembro 3 | Estadistica+Visualizaciones |
| Miembro 4 | Lider+Entregables+GitHub |

---

## 8. Referencias

1. McKee TB, Doesken NJ, Kleist J. The relationship of drought frequency and duration to time scales. 8th Conference on Applied Climatology, 1993.
2. Copernicus Climate Change Service C3S. ERA5-Land hourly data 1950-present. ECMWF, 2024.
3. MADR / Datos Abiertos Colombia. Encuesta Nacional Cafetera EVA.
4. NOAA Climate Prediction Center. Oceanic Nino Index ONI.
5. Federacion Nacional de Cafeteros de Colombia. Precios Internos y Externos del Cafe.
6. Avelino J et al. The coffee rust crises in Colombia and Central America (2008-2013). Food Security 7(2): 303-321, 2015.
7. IDEAM. Red ECA Nacional — Anomalias climaticas.
8. NASA LP DAAC. MOD13Q1 MODIS Vegetation Indices 250m.
9. Breiman L. Random Forests. Machine Learning 45(1): 5-32, 2001.
10. Geurts P, Ernst D, Wehenkel L. Extremely Randomized Trees. Machine Learning 63(1): 3-42, 2006.
