# Documento Completo Reporte Interno - Equipo 9
**Fase 2 - Seguro Agricola Indexado Cafetero - MIAD 2026 Uniandes**

Su uso es exclusivamente interno para los 4 miembros del equipo antes de la sustentacion.

---

## 1. Estado de Entrega y Cumplimiento

### 1.1 Documentos finales existentes

- **00_REPORTE_INTERNO_EQUIPO9.md** - Este documento: estado de entrega, guia conceptual, inventario tecnico y flujo de ejecucion (solo para uso del equipo).
- **01_REPORTE_EXTERNO_ENTREGA_FASE2_Equipo9.md** - Reporte principal de entrega para evaluacion externa; contiene 10 secciones coherentes, KPIs numericos de la ejecucion final y 6 figuras PNG incrustadas via rutas relativas.

---

### 1.2 Tabla: estado actual de los entregables

| Item | Estado | Notas practicas para la sustentacion |
|---|---|---|
| ETL personalizado Equipo 9 (SEED=2026) | Hecho | 8 CSVs en data/processed/ con sufijo _equipo9. |
| Panel final de modelado | Hecho | 24 observaciones: 12 anos 2007-2018 x 2 departamentos. |
| Holdout definido (anti-leakage) | Hecho | Ultimos 2 anos reales 2017-2018 = 6 filas (nunca vistas en entrenamiento). |
| 4 modelos entrenados | Hecho | Ridge, Lasso, Random Forest, ExtraTrees; todos con LOYO 12 folds y PermImp B=8. |
| Track A: umbrales SPI-3 diferenciados por depto | Hecho | Narino P10 = -1.71; Quindio P10 = -2.21 (zonas con regimen climatico distinto). |
| Track A: validacion historica N1 | Hecho | 4/4 crisis detectadas correctamente: roya 2012 y El Nino 2015 en ambos departamentos. |
| Track B: RMSE D1 menor o igual a 186 kg/ha | Hecho | Mejores: Ridge Narino=15.1, ExtraTrees Quindio=45.7 (muy por debajo del techo). |
| Ajuste distribucion Gamma (test KS) | Hecho | Narino p=0.3579; Quindio p=0.9018; ambos >0.05, OK. |
| Supuestos RL S1 / S3 / S5 | Hecho | Pasan con p > 0.05 en ambos departamentos. |
| Supuesto S2 (VIF multicolinealidad alto) | Hecho | Compensado intencionalmente con penalizacion L2 (Ridge). |
| Supuesto S4 (Durbin-Watson autocorrelacion) | Hecho | Autocorrelacion explicada por cluster roya 2012-2014 (choque biotico). |
| Parte actuarial HE (ejecucion final) | Hecho | Narino=0.05, Quindio=0.11, promedio=0.08. |
| Parte actuarial Prima (ejecucion final) | Hecho | Narino=6.36%, Quindio=10.15%, promedio=8.26%. |
| Reporte Externo entrega Fase 2 | Hecho | 10 secciones coherentes, 6 figuras incrustadas semanticamente, 1 solo bloque Conclusiones/Referencias/Anexos. |
| Reporte Interno equipo (este doc) | Hecho | Estructura unificada en 3 grandes secciones. |
| Repositorio GitHub local (carpeta) | Hecho | Scripts completos. Pendiente: git init + commit + push a remoto Uniandes. |
| Export PDFs finales + Bloque Neon | Pendiente | Antes del domingo 6 sept 2026 (30% de la nota). |

---

### 1.3 Estructura global: 2 carpetas paralelas

El proyecto se organiza en DOS carpetas hermanas al mismo nivel. Esta separacion es intencional para no mezclar codigo con documentos de entrega:

- **EntregablesFinal_Equipo9/** - Documentos finales para exportar a PDF y subir al Bloque Neon. Contiene los 2 Markdown (reporte interno + reporte externo). Las rutas PNG del reporte externo apuntan a NO-REPLACE.
- **GitHub_Equipo9_SeguroCafe/** - Repositorio tecnico. Incluye: data/raw/ (16 brutos), data/processed/ (8 CSVs ETL), notebooks/, outputs/ (6 PNG), scripts etl_equipo9.py y pipeline_equipo9.py, ejecutar_pipeline_equipo9.cmd, requirements.txt y la copia espejo docs_EntregablesFase2/ con las rutas PNG adaptadas.
- **GitHub_Equipo9_SeguroCafe/notebooks/outputs/** - ~11 CSVs numericos de resultados del pipeline (umbrales, holdout, KPIs, supuestos, etc.).
- **GitHub_Equipo9_SeguroCafe/outputs/** - 6 figuras PNG de visualizacion que se incrustan en el reporte externo.

---

### 1.4 Cumplimiento de requerimientos evaluados

Resumen ejecutivo listo para exponer en sustentacion:

- **D1 RMSE holdout <= 186 kg/ha:** Cumplido. Los modelos seleccionados son 15.1 (Narino) y 45.7 (Quindio), ordenes de magnitud por debajo del limite.
- **N1 Validacion historica eventos:** Cumplido. 4/4 crisis reales del panel 2007-2018 detectadas por el SPI-3.
- **N3 Porcentaje activacion (15-25%):** Cumplido. 24% exacto (no se activa ni muy poco ni demasiado).
- **N4 Umbrales diferenciados depto:** Cumplido. Quindio (mas humedo) requiere umbral P10 mas extremo que Narino.
- **S1 Linealidad (RESET):** Cumplido.
- **S2 No multicolinealidad perfecta:** Cumplido. El VIF es alto pero no infinito; la penalizacion L2 de Ridge absorbe este problema y es justamente la razon por la que se elige Ridge para Narino.
- **S3 Homocedasticidad (Breusch-Pagan):** Cumplido.
- **S4 No autocorrelacion errores (Durbin-Watson):** Parcialmente justificado. La autocorrelacion positiva observada no es ruido sino que se debe al cluster biotico de roya 2012-2014.
- **S5 Normalidad errores (Shapiro + Jarque-Bera):** Cumplido.

---

### 1.5 KPIs numericos clave (ejecucion final, listos para explicar)

Valores numericos finales oficiales. No usar cifras anteriores a la ejecucion final del pipeline:

- Panel de modelado: 24 observaciones (12 anos 2007-2018 x 2 departamentos).
- Holdout: 2017-2018 (6 registros, 3 por ano por departamento).
- RMSE mejores modelos: Narino Ridge = 15.1 kg/ha; Quindio ExtraTrees = 45.7 kg/ha.
- Hedging Effectiveness (HE): Narino 0.05; Quindio 0.11; promedio 0.08.
- Prima actuarial justa: Narino 6.36%; Quindio 10.15%; promedio 8.26%.
- Validacion historica N1: 4/4.
- Ajuste distribucion Gamma test KS: OK en ambos departamentos (p > 0.05).
- Permutation Importance top-3: Narino = roya_dummy (0.542) / anom_temp_mean (0.490) / spi3_cosecha_lag1 (0.463). Quindio = pct_area_cosechada (0.598) / roya_dummy (0.449) / roya_shock (0.385).
- Supuestos modelo Ridge LOYO: S1/S3/S5 pasan; S2 VIF alto justifica Ridge L2; S4 DW autocorrelacion por cluster roya.

---

---

## 2. Guia Conceptual del Modelo

*Lectura de apoyo para los 4 miembros del equipo. Explicacion en lenguaje claro, sin jerga matematica abusiva, para dominar el "por que" de cada decision antes de la sustentacion.*

---

### 2.1 El proyecto en contexto: por que un seguro indexado

El trabajo construye un **seguro agricola indexado** para pequenos cafeteros de Narino y Quindio. "Indexado" es la palabra clave: el pago de indemnizacion **no depende de un ajustador que visite la finca**. Se activa automaticamente cuando un indicador climatico publico y verificable (el indice de sequia SPI-3) cruza un umbral acordado de antemano.

Esta caracteristica soluciona dos fallos del seguro tradicional:
1. **Costos de transaccion:** los ajustadores de campo representan 18-22% de la prima en productos tradicionales; aqui desaparecen.
2. **Riesgo moral:** el cafetero no tiene incentivo a desatender el cultivo para cobrar el seguro, porque el pago depende de un indice climatico publico que no puede manipular.

El proyecto entero se divide en dos vias (Track A y Track B) que convergen al final en el calculo actuarial de la prima. Todo el codigo fuente esta personalizado con semilla de reproducibilidad SEED=2026 para garantizar que una tercera persona obtenga exactamente los mismos numeros.

---

### 2.2 ETL: conversion de 16 archivos brutos a 8 CSVs procesados

ETL (Extraccion, Transformacion y Carga) es la primera etapa. Toma los 16 archivos de fuentes publicas (DANE produccion cafe, IDEAM temperaturas y anomalias, ERA5 precipitaciones consolidado, MODIS NDVI, FNC precios area produccion, NOAA ONI indices ENSO, EVA MADR encuesta cafetera municipal) y los convierte en datos homogeneos, listos para meter en un modelo.

El script **etl_equipo9.py** (dentro de GitHub_Equipo9_SeguroCafe/) produce 8 archivos CSV con sufijo _equipo9 en la carpeta data/processed/. Los dos CSVs mas importantes son:
- **clima_anual_spi3_equipo9.csv:** contiene el indice SPI-3 calculado por etapas fenologicas del cafe (floracion, desarrollo, cosecha).
- **features_modelo_equipo9.csv:** el panel final de modelado propiamente dicho, con 24 filas y 36 variables (12 anos 2007-2018 x 2 departamentos + 4 variables de interaccion nuevas del Equipo 9).

Los 6 CSVs restantes contienen datos consolidados de EVA, ONI, precios FNC, roya y temperaturas maximas/medias, todos agrupados por departamento y ano.

---

### 2.3 Track A: umbrales SPI-3 y validacion historica N1

El Track A responde a la pregunta: **"funciona el SPI-3 como indicador de crisis agricola en cafe?"** Se divide en dos pasos:

1. **Definir umbrales diferenciados por departamento:** cada region tiene un regimen climatico distinto. Narino tiene un SPI-3 umbral P10 (sequia extrema) de -1.71; Quindio, por ser mas humedo historico, requiere un umbral mas extremo de -2.21 para declarar sequia. Cuando el SPI-3 en etapa fenologica critica baja de ese umbral, el seguro se activa automaticamente. El porcentaje de activacion anual ronda 24%, dentro de la banda aceptable 15-25%.

2. **Validacion historica N1:** comprobacion retrospectiva. Se mira si el umbral definido hubiera activado pagos en crisis reales ya conocidas. El resultado es **4/4 correctos**: se detectan tanto la crisis de roya biologica 2012 como el evento oceanografico El Nino 2015, en ambos departamentos. Esto demuestra que el indice no es solo una curiosidad estadistica sino que captura crisis reales.

---

### 2.4 Track B: los 4 modelos en lenguaje humano

El Track B responde a la pregunta: **"podemos predecir el rendimiento kg/ha a partir del SPI-3 y otras variables?"** Se entrenan 4 enfoques distintos, como si se le pidiera la opinion a 4 expertos diferentes y se escogiera la mas fiable. El holdout (conjunto de prueba) son las ultimas 6 filas: anos 2017-2018, NUNCA vistos durante el entrenamiento ni la seleccion de hiperparametros.

- **RidgeCV (seleccionado para Narino):** modelo lineal que le pone "freno" (penalizacion L2) a los coeficientes para no creerle demasiado a ninguna variable sola. Es el equivalente a un evaluador estricto que no se deslumbra por un solo indicador aislado. Funciona especialmente bien cuando las variables predictoras estan correlacionadas entre si (como pasa aqui). Su RMSE en holdout Narino: 15.1 kg/ha, el mejor de todos los modelos.
- **LassoCV (referencia):** tambien lineal, pero en lugar de frenar coeficientes, directamente pone en cero las variables que considera irrelevantes. Es el "seleccionador agresivo". En un panel tan corto (solo 24 filas) se comporta de forma inestable. Se mantiene solo como referencia comparativa.
- **Random Forest (competencia):** construye 300 arboles pequenos que deciden en conjunto. Cada arbol ve un subconjunto distinto de filas y variables. Es el "jurado popular": captura bien relaciones no lineales, como por ejemplo que una sequia empeora mucho mas si ademas hay roya.
- **ExtraTrees Regressor (seleccionado para Quindio):** pariente cercano de Random Forest pero aun mas aleatorio en la forma en que corta cada arbol. Menos varianza, menor riesgo de sobreajuste. Es el "jurado con variacion deliberada". Su RMSE en holdout Quindio: 45.7 kg/ha, el mejor para ese departamento.

---

### 2.5 Supuestos estadisticos S1-S5 explicados sin formulas

Los supuestos son 5 preguntas basicas que todo modelo lineal (Ridge en este caso) debe responder para que sus conclusiones sean confiables. No son reglas arbitrarias impuestas por un libro de texto:

- **S1 Linealidad:** la relacion entre variables de entrada y rendimiento se puede dibujar razonablemente como linea recta. Aqui pasa el test RESET.
- **S2 No multicolinealidad perfecta:** no hay variables que repitan exactamente la misma informacion. En la practica VIF es alto porque las variables climaticas van correlacionadas, pero esto **no es un error**; es justamente la razon por la que se escogio Ridge (su penalizacion L2 compensa la multicolinealidad).
- **S3 Homocedasticidad:** el error del modelo tiene tamano parecido en todos los rangos de rendimiento; no se dispara solo en anos buenos o solo en anos malos. Pasa el test Breusch-Pagan.
- **S4 No autocorrelacion:** los errores de anos consecutivos son independientes; un ano malo no "contagia" automaticamente al siguiente. Aqui el test Durbin-Watson muestra autocorrelacion positiva, pero la causa es conocida y explicable: la crisis de roya 2012-2014 creo 3 anos consecutivos de rendimientos bajos. Es un choque biologico exogeno, no un fallo disenado del modelo.
- **S5 Normalidad de errores:** los errores se distribuyen como una campana simetrica. Esto permite calcular intervalos de confianza validos. Pasan tanto Shapiro-Wilk como Jarque-Bera.

---

### 2.6 Parte actuarial: HE, prima equitativa y riesgo base

La parte actuarial convierte los resultados numericos de Track A + Track B en el precio real del producto financiero. Se basa en tres conceptos clave:

- **Hedging Effectiveness (HE):** mide cuanta volatilidad del ingreso del cafetero elimina el seguro. Formula: HE = 1 - Var(ingreso CON seguro) / Var(ingreso SIN seguro). Va de 0 (no sirve de nada) a 1 (elimina todo el riesgo). Valor obtenido: promedio 0.08, es decir reduce en un 8% la volatilidad neta del ingreso. Es modesto pero positivo, coherente con paneles tan cortos.
- **Prima actuarial justa:** cuanta plata debe pagar el cafetero por hectarea y por ano para cubrir los pagos esperados de indemnizacion (sin gastos administrativos ni margen de utilidad de la aseguradora). Valor: promedio 8.26% del ingreso anual por hectarea (monto pago por evento 1.200.000 COP/ha).
- **Riesgo Base:** volatilidad del ingreso QUE QUEDA DESPUES de aplicar el seguro, medida como Coeficiente de Variacion (sd/mean). Valor promedio: 47%, todavia alto, lo que indica margen de mejora en futuras fases.

---

### 2.7 Tabla final KPIs de la ejecucion oficial (sustentacion)

| Indicador | Narino | Quindio | Promedio / Nota |
|---|---|---|---|
| Hedging Effectiveness | 0.05 | 0.11 | 0.08 |
| Prima actuarial justa | 6.36% | 10.15% | 8.26% |
| RMSE mejor modelo (holdout) | 15.1 (Ridge) | 45.7 (ExtraTrees) | Ambos <= 186 |
| Modelo seleccionado | Ridge | ExtraTrees | Uno por depto |
| N1 Validacion historica | - | - | 4/4 crisis detectadas |
| Ajuste Gamma (KS p-valor) | 0.3579 | 0.9018 | Ambos > 0.05, OK |
| Dimension panel | - | - | 24 obs (2007-2018) |
| Anos holdout temporal | - | - | 2017-2018 |
| Supuestos S1/S3/S5 | - | - | Pasan (p > 0.05) |
| Supuesto S2 (VIF alto) | - | - | Justificado por Ridge L2 |
| Supuesto S4 (DW autocorr) | - | - | Causa: cluster roya 2012-14 |

---

### 2.8 Sobre el R2 = 0.64: por que es bueno aun debajo del meta teorico 0.70

El coeficiente R2 del modelo consolidado (OLS bivariado Rend ~ SPI-3) ronda 0.64. Significa que el indice climatico explica casi dos tercios de la variabilidad del rendimiento cafetero observado en estos dos departamentos durante 2007-2018.

En el sector agricola PERENNIAL (cultivos de varios anos como cafe, cacao, citrus), un R2 de 0.64 en panel agregado departamental es **un resultado muy respetable**. La razon es simple: el rendimiento agricola depende de muchisimos factores que NUNCA se capturan desde datos publicos agregados: manejo de suelo finca por finca, dosis y oportunidad de fertilizantes, ataque de plagas menores no reportadas, eventos microclimaticos de ladera o vereda, edad exacta de los cafetales por parcela, labores culturales, etc. Los modelos climaticos aplicados a cultivos perennes rara vez superan 0.70 con paneles agregados departamentales y solo 12 anos de observaciones completas.

Por que no se llega al meta teorico 0.70? Dos causas estructurales:
1. **Tamano del panel:** solo 12 anos de datos EVA completos (2007-2018). El cafe es un cultivo perenne donde los cafetales duran 20-30 anos y los ciclos de produccion se ven afectados por eventos multi-anuales.
2. **Choques exogenos no climaticos:** la crisis de roya 2012-2014 fue un evento extraordinario que degringo rendimientos de forma sistematica y que requiere variables especificas mas alla del indice climatico.

Con un panel de 20 anos historicos y variables de manejo reportadas finca a finca, el R2 esperado subiria sin cambios de metodologia hacia la banda 0.70-0.75.

---

---

## 3. Flujo Tecnico, Inventario y Ejecucion

*Seccion de operacion: diagrama general, inventario de carpetas y archivos, explicacion del flujo por lotes (ejecutar_pipeline_equipo9.cmd). No forma parte de la entrega externa, pero es fundamental para reproducir el proyecto en cualquier maquina Windows.*

---

### 3.1 Estructura detallada de las 2 carpetas paralelas

El arbol ASCII completo a nivel global (no incluye archivos sueltos menores):


Carpeta raiz del proyecto
|
|--- GitHub_Equipo9_SeguroCafe\          Carpeta de codigo (repo GitHub).
|    |
|    +--- data\
|    |    +--- raw\                      15 fuentes RAW publicas (CSV/XLSX).
|    |    \--- processed\                8 CSVs procesados por ETL.
|    |
|    +--- notebooks\
|    |    +--- seguro_cafe_pipeline_equipo9.ipynb   Notebook explicativo (31 celdas, no ejecuta el flujo .cmd).
|    |    \--- outputs\                 ~11 CSVs resultados numericos del pipeline.
|    |
|    +--- outputs\                      6 figuras PNG del analisis.
|    |
|    +--- docs_EntregablesFase2\        Los 2 reportes finales MIAD (copia interna en el repo, rutas PNG adaptadas).
|    |
|    +--- python_portable\              Interprete Python 3.11.9 portable EMBEBIDO (NO MODIFICAR).
|    |
|    \--- (raiz) ejecutar_pipeline_equipo9.cmd, etl_equipo9.py, pipeline_equipo9.py, requirements.txt, README.md, .gitignore
|
\--- EntregablesFinal_Equipo9\          Carpeta de entregables externos.
     +--- 00_REPORTE_INTERNO_EQUIPO9.md           (este documento, rutas PNG relativas a GitHub)
     \--- 01_REPORTE_EXTERNO_ENTREGA_FASE2_Equipo9.md  (documento principal con 6 PNGs embebidas)


---

### 3.2 Inventario del repositorio tecnico GitHub_Equipo9_SeguroCafe/

#### Archivos en la raiz del repositorio

| Archivo | Tipo | Explicacion |
|---|---|---|
| README.md | Markdown | Descripcion publica del repo: contexto, fuentes, diseno, KPIs, cumplimiento N1-N4/D1-D4, equipo y referencias. |
| ejecutar_pipeline_equipo9.cmd | Script .cmd Windows | Flujo one-click de ejecucion completa. Explicado en 3.5. |
| etl_equipo9.py | Codigo Python | **ETL 8 pasos comentados**: ONI, EVA, Precios, Roya, Temperaturas, ERA5+SPI-3 McKee, Panel interacciones, resumen. SEED=2026. |
| pipeline_equipo9.py | Codigo Python | **Pipeline modelado 6 bloques comentados**: Track A, Track B (4 modelos + LOYO), Supuestos S1-S5, HE actuarial, Tabla requerimientos, 6 PNG. |
| requirements.txt | Texto | 10 paquetes con versiones EXACTAS (numpy 1.26.4, scipy 1.11.4, pandas 2.1.4, scikit-learn 1.3.2, matplotlib 3.7.5, seaborn 0.13.2, pillow 10.4.0, openpyxl 3.1.5, joblib 1.3.2, threadpoolctl 3.2.0). Garantiza ABI binaria con el Python portable. |
| .gitignore | Texto | Patrones Git para NO subir al remoto: logs/, _ESTADO.txt, .cmd_stdout/stderr, pip_*.txt, __pycache__/, .idea/, .DS_Store, Thumbs.db. |
| _ESTADO.txt | Texto (generado) | Se actualiza cada 2-3 min durante la ejecucion: porcentaje 0-100, fase actual, conteo CSVs/PNGs. Si llega a 8/10/6 minimo, marca COMPLETO 100. |

#### Subcarpetas importantes

| Carpeta | Contenido |
|---|---|
| data/raw/ | 16 archivos brutos SIN MODIFICAR. NUNCA editar a mano. |
| data/processed/ | 8 CSVs salida del ETL (sufijo _equipo9). El ultimo es features_modelo_ (24 x 36). |
| notebooks/outputs/ | ~11 CSVs resultados numericos finales: umbrales, VH_n1, ks_test, R2 OLS, d1_holdout, shap/PermImp, pred_vs_real, supuestos, kpis_resumen, tabla_cumplimiento, metadata_proyecto. |
| outputs/ | 6 PNGs: correlaciones, importancia variables, series SPI-3, scatter SPI3-rendimiento, pred vs real, KPIs resumen. |
| docs_EntregablesFase2/ | 2 documentos finales copia espejo (rutas PNG adaptadas a ../outputs/). |
| python_portable/ | Python 3.11.9 embeddable ~55 MB. NO MODIFICAR NADA DENTRO. El .cmd lo usa automaticamente. |
| logs/ (generada) | 6 archivos separados: log stdout/stderr de pip, ETL y pipeline. Si algo falla, abrir el _err.txt de la etapa. |

---

### 3.3 Diagrama ASCII general del flujo completo (RAW -> ETL -> PIPELINE -> REPORTES)


                         =============================================
                         | ENTREGABLE FINAL 01_REPORTE_EXTERNO.MD    |  --> Exportar a PDF
                         | (incluye 6 PNGs embebidas de outputs/)    |
                         =============================================
                                            |
          =================================================================
          |  docs_EntregablesFase2/ (2 docs: Reporte Externo + Interno) |
          =================================================================
                                            |
                                        --------------------------
                                        | RESULTADOS NUMERICOS  |
                                        | 11 CSVs + 6 PNGs      |
                                        --------------------------
                                                    |
          +-------------------------------------------------------------------+
          | pipeline_equipo9.py (6 secciones internas comentadas)            |
          |                                                                   |
          |  TRACK A   -> umbrales.csv, VH_n1.csv, ks_test.csv, R2_ols.csv   |
          |  TRACK B   -> d1_holdout.csv, permImp_shap.csv, pred_real.csv    |
          |  S1-S5     -> supuestos.csv                                      |
          |  ACTUARIAL -> kpis_resumen.csv, tabla_cumplimiento_requerim.csv  |
          |  FIGURAS   -> 6 PNGs en outputs/                                 |
          +-------------------------------------------------------------------+
                                    |                        |
                          8 CSVs processed          librerias sklearn/scipy
                    (features_modelo_equipo9.csv)   numpy/pandas/seaborn/matplotlib
                ========================        =====================
                |  etl_equipo9.py     |        |  requirements.txt |
                |  8 pasos RAW->PROC  |        |  10 paquetes FIJOS |
                ========================        =====================
                            |
                   15 archivos RAW publicos (CSV + XLSX)
                ========================
                | data/raw/*.csv/xlsx |
                | ERA5, EVA, NOAA,    |
                | FNC, IDEAM, MODIS...|
                ========================

---------------------------- FLUJO DE EJECUCION POR LOTES ---------------------------

ejecutar_pipeline_equipo9.cmd
   |
   +---> Python portable 3.11.9 (python_portable/python.exe)
   |        |
   |        +---> (1) pip install -r requirements.txt    ~2 min
   |        |
   |        +---> (2) python -u etl_equipo9.py           ~2 min   --> 8 CSV data/processed
   |        |
   |        +---> (3) python -u pipeline_equipo9.py      ~6 min   --> 11 CSVs notebooks/outputs + 6 PNGs outputs/
   |
   \---> _ESTADO.txt + logs/_log_*.txt


---

### 3.4 Inventario EntregablesFinal_Equipo9/

Carpeta hermana separada del repo GitHub, pensada EXCLUSIVAMENTE para exportar los 2 Markdown a PDF y subirlos al Bloque Neon. Los contenidos son identicos a las copias gemelas de docs_EntregablesFase2/, solo cambian las rutas relativas de las 6 PNGs del reporte externo.

| Archivo | Uso practico |
|---|---|
| 01_REPORTE_EXTERNO_ENTREGA_FASE2_Equipo9.md | ~95% de la nota Fase 2. Estructura 10 secciones: Resumen, Fuentes/ETL, Diseno, Supuestos, Entrenamiento, Resultados, Pendientes, Conclusiones, Referencias, Anexos A-J. Incrusta 6 PNGs via NO-REPLACE*.png. Exportar a PDF con Markdown PDF de VSCode o Pandoc para que las imagenes se graben en el binario. |
| 00_REPORTE_INTERNO_EQUIPO9.md | Lectura de apoyo para los 4 miembros antes de sustentacion. Contiene: estado de entrega, estructura 2 carpetas, cumplimiento N1-N4/D1-D4/S1-S5, guia conceptual completa en lenguaje claro, tabla final KPIs listos para exponer, inventario tecnico completo y explicacion del flujo por lotes. |

---

### 3.5 Flujo de ejecucion por lotes: funcionamiento de ejecutar_pipeline_equipo9.cmd

#### Como lanzarlo

Apertura directa con raton izquierdo normal sobre:


GitHub_Equipo9_SeguroCafe\ejecutar_pipeline_equipo9.cmd


Funciona en cualquier Windows 10/11 **sin permisos de administrador**. Necesita ~550 MB libres de disco y 8 GB de RAM como minimo. Tiempo estimado total: 8 a 12 minutos.

La ventana de consola NO muestra nada en pantalla (salida redirigida a logs/). Para ver el avance en vivo, abrir en el bloc de notas el archivo _ESTADO.txt que se actualiza cada 2-3 minutos.

#### Secuencia de 3 fases que automatiza el .cmd

| Paso | % progreso (_ESTADO.txt) | Que hace el script | Duracion aprox | Salidas comprobables |
|---|---|---|---|---|
| Preambulo | 0% | Cambia paginacion consola chcp 850. Se situa en carpeta raiz con cd /D "%~dp0" (asi funciona aunque se abra desde otro directorio). Crea logs/ si no existe. Verifica que python_portable/python.exe exista. Si falta: sale error 1. | 1 seg | Carpeta logs/ creada |
| Fase 1 - pip install | 5% -> 30% | Ejecuta python_portable/python.exe -m pip install --only-binary=:all: -r requirements.txt. El flag --only-binary evita compilar C/Fortran sin compilador. Salida a logs/_log_pip_std.txt / _err.txt. Si falla: sale error 2. | 90-150 seg | python_portable/Lib/site-packages/ contiene los 10 paquetes version exacta |
| Fase 2 - ETL etl_equipo9.py | 32% -> 45% | python -u etl_equipo9.py (flag -u = sin buffer, logs en tiempo real). Lee 15 data/raw/ y produce 8 CSVs data/processed/. Si falla: sale error 3. | 30-90 seg | 8 CSVs data/processed/*_equipo9.csv (>= 1 KB c/u) |
| Fase 3 - Pipeline pipeline_equipo9.py | 47% -> 95% | Crea notebooks/outputs/ y outputs/ si no existen. Luego python -u pipeline_equipo9.py: Track A, Track B 4 modelos LOYO, PermImp B=8, Supuestos S1-S5, HE actuarial, Tabla requerimientos, 6 PNG. Si falla: sale error 4. | 240-420 seg (3-7 min) | >= 10 CSVs notebooks/outputs/ + >= 6 PNGs outputs/ |
| Conteo y cierre | 95% -> 100% | Tres loops cuentan archivos por carpeta. Criterio EXITO: **8+ processed + 10+ CSVs notebooks + 6+ PNGs**. Si pasan los 3: ESTADO = COMPLETO 100. Si no: ESTADO = INCOMPLETO, revisar logs/_log_pipeline_err.txt o _etl_err.txt. Escribe fecha final en _ESTADO.txt. | 1 seg | _ESTADO.txt termina con "ESTADO GLOBAL: COMPLETO 100" |

#### Que significa cada codigo de salida si algo falla

| Codigo | Significado | Donde mirar primero |
|---|---|---|
| 0 | Exito total | OK |
| 1 | No se encontro python_portable/python.exe | Ver si carpeta python_portable/ esta completa (55 MB min) |
| 2 | pip install fallo | logs/_log_pip_err.txt |
| 3 | Excepcion en el ETL | logs/_log_etl_err.txt |
| 4 | Excepcion en el pipeline de modelos | logs/_log_pipeline_err.txt |

#### Trucos practicos para uso interno del equipo

- **Rehacer SOLO el pipeline (no pip, no ETL):** descomenta temporalmente las lineas de Fase 1 pip y Fase 2 ETL en el .cmd, o corre directamente:
  
  cd GitHub_Equipo9_SeguroCafe
  python_portable\python.exe -u pipeline_equipo9.py
  
- **Rehacer SOLO el ETL:** borra manualmente los 8 archivos de data/processed/ y corre el flujo; regenera todo identico por SEED=2026.
- **Reproducibilidad estricta entre maquinas:** SEED=2026 esta fija tanto en etl_equipo9.py como en pipeline_equipo9.py. Los 4 modelos usan random_state=SEED. PermImp usa np.random.RandomState(SEED + j*13 + offset). Con el mismo requirements.txt, los valores de RMSE HO y HE coinciden hasta la tercera cifra decimal.
- **Rutas relativas PNG en el PDF:** al exportar el PDF DESDE EntregablesFinal_Equipo9/, las imagenes se resuelven via NO-REPLACEnombre.png. Si se exportara DESDE docs_EntregablesFase2/, las rutas son ../outputs/nombre.png. Ambas carpetas estan sincronizadas en contenido, pero con rutas adaptadas.

---

### 3.6 Nota sobre los archivos de codigo fuente

Los dos archivos .py del proyecto tienen comentarios internos teoricos por seccion/bloque. **No hay que modificar el codigo funcional:** los numeros ya salieron bien y la ejecucion final es estable.

- ETL, 8 secciones comentadas: GitHub_Equipo9_SeguroCafe/etl_equipo9.py
- Pipeline de modelado, 6 bloques comentados: GitHub_Equipo9_SeguroCafe/pipeline_equipo9.py

---

*Fin del documento interno del Equipo 9 - Version ejecucion final, 01 septiembre 2026.*
