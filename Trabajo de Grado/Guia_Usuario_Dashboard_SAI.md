# Guia de Usuario - Panel Ejecutivo SAI Cafetero
## Seguro Agricola Indexado Cafetero (Narino / Quindio) - Equipo 9 - 2026

---

## 1. Proposito de esta guia

Este documento explica paso a paso como usar el Panel Ejecutivo del Seguro Agricola Indexado (SAI) para Cafetero. El panel es una aplicacion web local de una sola pagina que permite interactuar con los modelos oficiales del proyecto sin necesidad de escribir codigo.

**Audiencia:** Miembros del equipo y evaluadores.
**Nivel tecnico requerido:** Basico (manejo de navegador web y formularios).

---

## 2. Pre-requisitos antes de abrir el panel

### 2.1 Verificar que la API este ejecutandose

El panel NO funciona de forma aislada. Consume todos los datos y predicciones desde una API local que DEBE estar corriendo primero.

**Comprobacion rapida:** Abre esta direccion en tu navegador web:

```
http://127.0.0.1:8000/health
```

Si todo esta bien, veras un texto similar a:
```json
{"status":"ok","package_version":"0.1.0","models_available":["Narino","Quindio"]}
```

Si aparece "No se puede acceder a este sitio" o error de conexion, debes levantar la API primero. Consulta el manual de instalacion en el archivo `Guia_Solucion_SAI_F3.md` seccion 8.

### 2.2 Levantar la API y el Dashboard (resumen rapido)

En dos terminales de PowerShell distintas, dentro de la carpeta `solucion_local_sai_f3/`:

**Terminal 1 (API):**
```
.venv\Scripts\Activate.ps1
.\run_api.ps1
```

**Terminal 2 (Dashboard):**
```
.venv\Scripts\Activate.ps1
.\run_dashboard.ps1
```

Espera el mensaje: "Levantando en http://127.0.0.1:8501".

---

## 3. Acceso al panel

Abre en tu navegador web (Chrome, Edge, Firefox recomendados):

```
http://127.0.0.1:8501
```

### 3.1 Pantalla inicial

Al entrar veras:

1. **Barra superior (cabecera):**
   - Titulo: "Seguro Agricola Indexado Cafetero - Panel Ejecutivo"
   - Subtitulo con departamentos (Narino / Quindio), rango historico (2007-2018), y pago por evento por defecto (1,200,000 COP/ha).
   - Si la API no responde, aparecera un recuadro amarillo de advertencia: "La API local no responde".

2. **Barra lateral IZQUIERDA (Filtros Panel):** Contiene todos los filtros globales que afectan los 6 modulos del cuerpo principal.

3. **Cuerpo PRINCIPAL (6 modulos verticales):** Desde KPIs en la parte superior hasta la Calculadora Actuarial en la parte inferior.

---

## 4. Barra lateral - Filtros y configuraciones globales

La barra lateral controla TODOS los modulos del cuerpo. Cambiar un filtro actualiza automaticamente las series, tablas, KPIs de detalle y calculadora.

### 4.1 Estado de la API (indicador superior)

Muestra:
- Nombre y version del paquete de inferencia.
- Estado API: "OK" (verde) o "NO DISPONIBLE" (rojo).

### 4.2 Filtro geografico (Departamento)

**Ubicacion:** Subtitulo "Filtro geografico".
**Control:** Lista desplegable.
**Opciones:**
- `Todos` (por defecto) - Muestra datos combinados de Narino y Quindio.
- `Narino` - Filtra solo datos del departamento de Narino.
- `Quindio` - Filtra solo datos del departamento del Quindio.

**Afecta a:** Modulo 2 (Serie SPI), Modulo 4 (LOYO pred vs real), Modulo 6 (Calculadora actuarial).

### 4.3 Rango de anios historicos

**Ubicacion:** Subtitulo "Rango de anios historicos".
**Control:** Slider doble (dos deslizadores).
**Rango por defecto:** 2007 a 2018 (coincide con el panel oficial de Entrega_2).
**Paso:** 1 anio.

**Como usarlo:**
- Arrastra el deslizador IZQUIERDO para cambiar el anio de inicio.
- Arrastra el deslizador DERECHO para cambiar el anio de fin.
- Todo modulo que use datos historicos quedara limitado a este rango.

### 4.4 Precarga inputs Track B (Prediccion Rendimiento)

Permite cargar automaticamente los valores de variables fenologicas de un anio historico real, para no tener que digitarlos manualmente en el Modulo 3.

**Pasos:**
1. Selecciona el departamento en "Departamento para prediccion" (Narino o Quindio).
2. Selecciona el anio historico en "Anio historico (carga inputs automaticamente)".
   - Ejemplo: Narino + 2015 (carga el evento de El Nino 2015).
   - Ejemplo: Narino + 2012 (carga el evento de la Roya 2012).
3. Haz clic en el boton azul grande: "Cargar inputs historicos seleccionados".
4. Veras un mensaje verde de confirmacion. Los 6 valores del formulario del Modulo 3 se actualizaran automaticamente.

### 4.5 Parametros calculadora actuarial

Controlan el Modulo 6. Los cambios se reflejan EN VIVO (no hay boton de calcular).

**a) Hectareas aseguradas**
- Tipo: Numero decimal.
- Rango: 1.0 ha a 100,000.0 ha.
- Valor por defecto: 100.0 ha.
- Paso: +10.0 ha por clic.

**b) Pago indemnizatorio por evento (COP/ha)**
- Tipo: Numero entero.
- Rango: 0 COP a 10,000,000 COP.
- Valor por defecto: 1,200,000 COP/ha (valor oficial Entrega_2).
- Paso: +50,000 COP por clic.

**c) Sobrecarga prima adicional (%)**
- Tipo: Slider entero.
- Rango: 0 % a 50 %.
- Valor por defecto: 5 %.
- Definicion: Porcentaje extra que se suma sobre la prima actuarial oficial. Afecta directamente el balance de la Calculadora (Modulo 6).

### 4.6 Zona utilidades (inferior sidebar)

**Diagnostico API / metadata (colapsable):**
- Haz clic para expandir y ver el JSON crudo del endpoint `/health`.
- Sirve para depuracion.

**Boton "Limpiar cache y recargar":**
- Vuelve a cargar TODOS los datos desde la API y refresca el panel.
- Usalo si sospechas que los datos estan desactualizados o si aparecen valores antiguos.

---

## 5. Modulo 1 - KPIs del proyecto (6 tarjetas)

**Ubicacion:** Primer modulo del cuerpo, justo despues de la cabecera.
**Proposito:** Mostrar los indicadores clave de rendimiento de los modelos, TAL CUAL fueron calculados en Entrega_2 (NO recalculados).

### 5.1 Estructura de las 6 tarjetas (1 fila x 6 columnas)

| Columna | Nombre del KPI | Departamento | Unidad | Interpretacion |
|:--------|:---------------|:-------------|:-------|:----------------|
| 1 | RMSE Holdout | Narino | kg/ha | Error cuadratico medio. Menor = mejor modelo. Valor oficial: ~15.1 kg/ha. |
| 2 | Equidad tarificacion HE | Narino | (sin unidad) | Coeficiente HE de Ederington. Menor = mayor equidad. Valor oficial: ~0.05. |
| 3 | Prima actuarial | Narino | % | Prima por hectarea (sobre pago evento). Valor oficial: ~6.36 %. |
| 4 | RMSE Holdout | Quindio | kg/ha | Error cuadratico medio. Valor oficial: ~45.7 kg/ha. |
| 5 | Equidad tarificacion HE | Quindio | (sin unidad) | Valor oficial: ~0.11. |
| 6 | Prima actuarial | Quindio | % | Valor oficial: ~10.15 %. |

### 5.2 Detalle actuarial expandible

Debajo de las 6 tarjetas hay un boton "Detalle actuarial / frecuencia activacion". Al expandirlo muestra por cada departamento:
- Riesgo base (%).
- Frecuencia activacion historica (%).

### 5.3 Como leer correctamente los KPIs

- **Compara Narino vs Quindio:** Narino tiene menor RMSE y menor HE (mejor ajuste del modelo), por lo tanto su prima es mas baja.
- **La prima es directamente proporcional al riesgo:** Un mayor riesgo base + mayor frecuencia de activacion = prima mas alta (caso Quindio).

---

## 6. Modulo 2 - Track A: Indice SPI y Activaciones

**Ubicacion:** Segundo modulo.
**Proposito:** Visualizar la severidad climatica (SPI-3) por etapa fenologica y ver en que anios se activo el seguro.

---

**REGLA DE ACTIVACION DEL SEGURO (5 reglas OR - cualquiera que se cumpla activa):**

| Codigo | Regla | Descripcion |
|:------:|:------|:------------|
| C1 | Sequia anual | spi3_min del anio < P10 del departamento |
| C2 | Sequia enneagro | spi3_min en periodo enneagro < P10 |
| C3 | Sequia en cosecha | spi3 en etapa cosecha < P10 |
| C4 | Acumulacion sequia | Numero de meses de sequia en enneagro >= 2 |
| C5 | Roya | roya_shock = 1 O roya_dummy = 1 |

Si AL MENOS UNA regla se cumple: **Activa = SI -> pago indemnizatorio.**

Umbrales P10 oficiales: Narino = -1.7071; Quindio = -2.2143.

---

### 6.1 Grafico SPI por etapa fenologica (izquierda)

Muestra para el rango de anios y departamento(s) filtrados:
- **Barra azul:** SPI-3 en etapa de floracion.
- **Barra amarilla:** SPI-3 en etapa de desarrollo.
- **Barra roja:** SPI-3 en etapa de cosecha.
- **Linea horizontal punteada roja:** Umbral P10 del departamento.

**Lectura del grafico:** Toda barra que CRUZA hacia ABAJO de la linea punteada roja indica sequia severa en esa etapa (potencial activacion del seguro por C1/C2/C3).

### 6.2 Tabla resumen de activaciones (derecha)

Columnas:
- **Departamento:** Narino / Quindio.
- **Anio:** Anio del evento.
- **Activa:** SI / NO.
- **Regla:** Codigo(s) de la(s) regla(s) que se activaron (ej: "C4,C5" si se cumplieron ambas).

**Casos de prueba rapidos:**
- Narino 2012: Activa SI (generalmente por C5 = Roya + C4 = >= 2 meses sequia).
- Narino 2015: Activa SI (evento El Nino, reglas sequia).
- Quindio 2012: Activa SI (Roya).
- Quindio 2015: Activa SI (El Nino).

---

## 7. Modulo 3 - Track B: Prediccion de Rendimiento (kg/ha)

**Ubicacion:** Tercer modulo.
**Proposito:** Predecir el rendimiento de cafe en kg/ha para un departamento, dadas 6 variables fenologicas y climaticas. Ademas, clasifica el resultado en un semaforo de riesgo (BAJO / MEDIO / ALTO) comparado con el historico.

### 7.1 Estructura: 2 columnas iguales (izquierda = Inputs, derecha = Resultado)

#### COLUMNA IZQUIERDA: Formulario de 6 inputs

Las 6 variables son EXACTAMENTE las features oficiales del modelo. El orden importa para la API.

| Input | Nombre | Tipo | Rango tipico | Explicacion |
|:------|:-------|:-----|:-------------|:------------|
| 1 | spi3_floracion | Decimal 4 decimales | [-5, 5] | Indice SPI-3 en etapa floracion. Negativo = sequia. Positivo = humedad. |
| 2 | spi3_desarrollo | Decimal 4 decimales | [-5, 5] | SPI-3 etapa desarrollo. |
| 3 | spi3_cosecha | Decimal 4 decimales | [-5, 5] | SPI-3 etapa cosecha. |
| 4 | tmax_mean_e9 | Decimal 2 decimales | [10, 40] grados C | Temperatura maxima media periodo enneagro. |
| 5 | oni_mean | Decimal 4 decimales | [-5, 5] | Indice ONI (Oscilacion Nino). +1.5 o mas = El Nino fuerte. -1.5 o menos = La Nina fuerte. |
| 6 | roya_dummy | Selector 0 / 1 | {0, 1} | 1 = evento de roya (shock sanitario). 0 = sin roya. |

**Metodos para llenar el formulario:**
- **METODO 1 (RECOMENDADO):** Usa la precarga del sidebar (seccion 4.4). Selecciona departamento + anio historico -> boton "Cargar inputs historicos". Los valores se llenan automaticamente.
- **METODO 2 (MANUAL):** Digita cada valor uno por uno. Util cuando quieres probar escenarios hipoteticos (ej: "que pasaria si la ONI fuera +3.0?").

**Boton "Calcular prediccion":**
- Color azul.
- Se desactiva automaticamente si la API no esta disponible (gris).
- Al hacer clic, se envia una solicitud a la API y aparece un spinner mientras se calcula.

#### COLUMNA DERECHA: Resultado + Semaforo de riesgo

Aparece despues de pulsar "Calcular prediccion":

**1) Tarjeta de Rendimiento estimado (izq):**
- Valor numerico principal en kg/ha (formato: 1,085.4 kg/ha).
- Departamento asociado.

**2) Tarjeta SEMAFORO DE RIESGO (der):**
- **Titulo:** NIVEL DE RIESGO (vs historico depto).
- **Valor grande en color:** BAJO, MEDIO o ALTO.
- **Leyenda inferior:** Q1 hist. = X kg/ha y Q3 hist. = Y kg/ha.

**Logica del semaforo (percentiles historicos del departamento filtrado):**
| Color | Nivel | Condicion |
|:-----:|:-----:|:----------|
| Azul  | BAJO  | prediccion < Percentil 25 (Q1) del historico |
| Naranja | MEDIO | Q1 <= prediccion <= Q3 (Percentil 75) |
| Verde | ALTO  | prediccion > Q3 del historico |

Nota: El color "verde = ALTO" es bueno para el caficultor (alto rendimiento = mayor ingreso). "Azul = BAJO" es el riesgo real (bajo rendimiento).

**3) Detalle tecnico expandible:**
Muestra el JSON crudo de la respuesta: departamento, validaciones, warnings (rangos fuera de [-5,5] para SPI/ONI), timestamp, y los valores de Q1/Q3 usados para el semaforo.

---

## 8. Modulo 4 - Track B: Validacion Leave-One-Year-Out (prediccion vs real)

**Ubicacion:** Cuarto modulo.
**Proposito:** Comparar graficamente el rendimiento REAL historico contra el rendimiento PREDICHO por la tecnica Leave-One-Year-Out (LOYO). Sirve para validar visualmente que tan bien funciona el modelo retrospectivamente.

### 8.1 Grafico (3/4 ancho)

**Leyenda de lineas:**
- **Linea continua gruesa:** Rendimiento REAL oficial.
- **Linea punteada delgada:** Rendimiento PREDICHO LOYO.
- **Color AZUL:** Narino.
- **Color NARANJA:** Quindio.

**Que buscar en el grafico:**
- Las lineas punteadas (predicho) deben seguir DE CERCA las lineas solidas (real), especialmente en los picos y valles.
- Prueba rapida: Selecciona en el sidebar "Narino" y rango 2012-2015. Verifica que la prediccion del 2015 casi toca el valor real.

### 8.2 Tabla metricas resumen (1/4 ancho)

Por cada departamento en el filtro:
- **RMSE LOYO:** Root Mean Squared Error en modo Leave-One-Year-Out. Coincide con el RMSE Holdout del Modulo 1 (Narino ~15.1, Quindio ~45.7).
- **MAE LOYO:** Mean Absolute Error (menor sensible a outliers que RMSE).
- **Sesgo medio:** Promedio (Predicho - Real). Positivo = sobreprediccion sistematica. Negativo = subprediccion.

---

## 9. Modulo 5 - Validacion Historica N=2 (Eventos 2012 y 2015)

**Ubicacion:** Quinto modulo.
**Proposito:** Es el CONTROL DE CALIDAD MAS IMPORTANTE del panel. Reproduce EN VIVO las predicciones para 4 eventos conocidos (2 departamentos x 2 eventos historicos) y compara contra el resultado esperado (debe activar el seguro en los 4).

### 9.1 Eventos evaluados

| Departamento | Anio | Evento climatico / sanitario | Esperado |
|:------------:|:----:|:-----------------------------|:--------:|
| Narino       | 2012 | Crisis de la Roya (roya_shock=1) + sequia | Activo = SI |
| Narino       | 2015 | El Nino fuerte (ONI alta + sequia extrema) | Activo = SI |
| Quindio      | 2012 | Crisis de la Roya | Activo = SI |
| Quindio      | 2015 | El Nino fuerte | Activo = SI |

### 9.2 Panel de cumplimiento (tabla con colores)

Columnas:
- **Departamento / Anio / Evento:** Identificador unico de la fila.
- **Track B (kg/ha):** Prediccion de rendimiento del modelo (ExtraTrees Narino / RandomForest Quindio). Valores de referencia: Narino 2012 ~974 kg/ha, Narino 2015 ~1085 kg/ha, Quindio 2015 ~1124 kg/ha.
- **Track A activo?:** SI / NO.
- **Regla Track A:** Codigo de regla que activo (C1-C5).
- **Cumplimiento esperado?:** CUMPLE (verde) o NO CUMPLE (rojo).

### 9.3 Como interpretar los colores

- **Fondo VERDE en "Cumplimiento":** Correcto. El sistema detecto el evento como debia.
- **Fondo ROJO en "Cumplimiento":** Error. El sistema fallo en detectar el evento.
- **Letra marron oscuro en "Track A activo? = SI":** Resalta que el seguro se pago ese ano.

**Lectura esperada (sistema funcionando bien):**
- 4/4 CUMPLE (100 %).
- Cumplimiento global: "4/4 (100.0 %)".

Si aparece un NO CUMPLE, revisa que la API este OK y que tengas los modelos correctos en `models_artifacts/`.

---

## 10. Modulo 6 - Calculadora Actuarial (Flujo prima vs indemnizaciones)

**Ubicacion:** Sexto y ultimo modulo.
**Proposito:** Simular el balance financiero del seguro en el periodo historico filtrado. Sirve para analizar sostenibilidad del producto.

### 10.1 Parametros en vivo (leyenda superior)

Muestra los valores actuales tomados del sidebar (no se editan aqui, se editan en el sidebar):
- Hectareas aseguradas.
- Pago por evento (COP/ha).
- Sobrecarga prima adicional (%).

### 10.2 Cinco tarjetas KPI de la calculadora

En una fila de 5 columnas:

| Columna | KPI | Formula / Definicion |
|:-------:|:----|:---------------------|
| 1 | Prima / ha / anio | Promedio anual de prima cobrada por hectarea (COP). |
| 2 | Total prima (periodo) | Suma de prima cobrada en todos los anios del rango filtrado. |
| 3 | Total indemnizacion (periodo) | Suma de pagos por eventos activos en el periodo. |
| 4 | Balance periodo | Total prima - Total indemnizacion. POSITIVO = superavit (bueno para asegurador). NEGATIVO = deficit (insostenible). |
| 5 | Eventos activados | Conteo total de (depto, anio) donde se activo el seguro en el filtro actual. |

### 10.3 Grafico de barras agrupadas (Prima vs Indemnizacion por anio)

- **Barras AZULES:** Prima cobrada en el anio.
- **Barras ROJAS:** Indemnizacion pagada en el anio.

**Patrones tipicos (Narino+Quindio, rango 2007-2018):**
- Anios normales (sin eventos): Prima alta, indemnizacion cero o baja -> superavit.
- Anios de eventos (2012 y 2015): Barra roja (indemnizacion) SUPERA ampliamente la barra azul -> deficit anual.
- El balance global depende de cuantos anios "buenos" compensan los anos "malos".

### 10.4 Tabla detalle anual (expandible inferiormente)

Por cada anio en el rango:
- Prima cobrada (COP).
- Indemnizacion pagada (COP).
- N eventos (conteo de deptos que activaron).
- Balance anual (COP) = Prima - Indemnizacion.

---

## 11. Flujos de uso practico (ejemplos paso a paso)

### Ejemplo 1: Verificar el caso control Narino - El Nino 2015

**Objetivo:** Confirmar que la prediccion Track B + la activacion Track A coinciden con el golden.

**Pasos:**
1. Asegurate de ver "API OK" en el indicador superior del sidebar.
2. En sidebar Precarga inputs Track B: selecciona Departamento = Narino, Anio = 2015.
3. Haz clic en "Cargar inputs historicos seleccionados". Espera el verde OK.
4. Baja al Modulo 3 y haz clic en "Calcular prediccion".
5. Verifica el resultado:
   - Rendimiento esperado: 1,085.4 kg/ha (aprox.).
   - Semaforo: MEDIO (naranja).
   - Q1 ~992 kg/ha, Q3 ~1093 kg/ha (Narino historico).
6. Baja al Modulo 5. En la fila Narino 2015 El Nino 2015:
   - Track B debe coincidir con el valor del paso 5.
   - Track A activo? = SI.
   - Cumplimiento = CUMPLE (verde).
7. Confirmacion final: Modulo 5 footer dice "Cumplimiento global: 4/4 (100.0 %)".

### Ejemplo 2: Escenario hipotetico sequia extrema en Quindio

**Objetivo:** Probar que pasa con un anio de sequia extrema en Quindio (sin ser historico).

**Pasos:**
1. En sidebar: Filtro geografico = Quindio.
2. En sidebar Precarga: Departamento para prediccion = Quindio.
3. Baja al Modulo 3. En el formulario digita MANUALMENTE:
   - spi3_floracion: -2.5
   - spi3_desarrollo: -3.0
   - spi3_cosecha: -2.8
   - tmax_mean_e9: 23.5
   - oni_mean: 2.5 (El Nino muy fuerte)
   - roya_dummy: 1
4. Pulsa "Calcular prediccion".
5. Observa el semaforo: probablemente BAJO (azul) o MEDIO, porque los SPI extremos bajan el rendimiento.
6. Baja a Modulo 6 Calculadora. Observa:
   - Como el filtro geografico es Quindio solo, la prima es ~10.15% + sobrecarga.
   - Total indemnizaciones refleja los eventos solo de Quindio.

### Ejemplo 3: Sensibilidad prima en la Calculadora

**Objetivo:** Ver como cambia el balance cuando aumentas o disminuyes la sobrecarga de prima.

**Pasos:**
1. Filtro sidebar = Todos, rango = 2007-2018 (maximo).
2. Baja al Modulo 6. Anota el valor "Balance periodo" (actual).
3. En el sidebar, arrastra el slider "Sobrecarga prima adicional (%)" hasta 20 %.
4. Espera 2-3 segundos a que se recalculen KPIs y grafico.
5. Anota el nuevo "Balance periodo". Subio considerablemente (aumento superavit).
6. Ahora baja el slider a 0 %. El balance baja o se vuelve negativo.
7. Encuentra el punto de equilibrio: mueve la sobrecarga hasta que Balance periodo se acerque a cero (break-even).

---

## 12. Preguntas frecuentes (FAQ)

### P1. El panel abre pero ve todo vacio o con mensajes "La API local no responde".

**R:** La API no esta corriendo. Ejecuta `.\run_api.ps1` en otra terminal dentro de `solucion_local_sai_f3/`. Luego pulsa F5 en el navegador o clic en "Limpiar cache y recargar" al final del sidebar.

### P2. Cambio el filtro de Departamento pero el grafico LOYO no cambia.

**R:** El filtro "Departamento" afecta las series historicas PERO el boton "Limpiar cache y recargar" fuerza una recarga inmediata. Haz clic en el boton del sidebar. Alternativamente, espera el TTL de cache (60 segundos para predicciones, 600 segundos para KPIs fijos).

### P3. Cliqueo "Cargar inputs historicos" pero los inputs del Modulo 3 no cambian.

**R:** Este comportamiento es conocido en Streamlit. El formulario no se actualiza visualmente hasta que cambias de anio en el selector O recargas la pagina. Solucion: Despues de hacer clic, selecciona otro anio y luego vuelve al original. O usa F5.

### P4. El semaforo de riesgo muestra INDETERMINADO.

**R:** El panel historico del departamento filtrado tiene MENOS de 3 valores validos. Vuelve a poner el filtro geografico en "Todos" y vuelve a calcular.

### P5. En la validacion historica veo 3/4 CUMPLE (1 NO CUMPLE).

**R:** Los modelos serializados no coinciden con los oficiales. Posibles causas:
- Borraste la carpeta `models_artifacts/` y el serializador no corrio con la seed correcta.
- Instalaste una version incorrecta del paquete.
Solucion: Reconstruye los artefactos ejecutando `setup_dev.ps1` (que incluye el serializador).

### P6. Los graficos aparecen borrosos o son imagenes estaticas sin zoom.

**R:** No se encontro la libreria `plotly`. El dashboard tiene un fallback automatico a `matplotlib` (imagen PNG). Si deseas graficos interactivos (zoom, hover, exportar PNG), asegura que plotly este instalado:
```
pip install plotly>=5.18
```
Y reinicia el dashboard con `.\run_dashboard.ps1`.

### P7. Cambio el numero de hectareas pero el balance no se actualiza.

**R:** El calculo es instantaneo. Si no lo hace, haz clic en "Limpiar cache y recargar".

### P8. Que significan los colores en el Modulo 5 Validacion?

| Color | Ubicacion | Significado |
|:-----:|:----------|:------------|
| Verde | Celda Cumplimiento | CUMPLE (sistema detecto evento correctamente) |
| Rojo | Celda Cumplimiento | NO CUMPLE (fallo de deteccion) |
| Marron oscuro | Track A activo = SI | Resalta visualmente pago indemnizatorio |

### P9. Puedo exportar las tablas a Excel o CSV?

**R:** Actualmente el panel no tiene boton de exportacion. Pero puedes:
- Modulo 4, 5 y 6: Pasar el cursor por encima de cualquier tabla y apareceran los iconos nativos de Streamlit (descarga CSV, maximizar, buscar).

### P10. El panel tarda mucho en cargar la primera vez.

**R:** Es normal. La primera carga debe: (a) consultar 6 endpoints de la API, (b) la API carga en memoria los 2 modelos .joblib (tarda ~5-10 segundos), (c) renderizar 6 modulos. Las siguientes cargas son rapidas (<2 segundos) por el cache.

---

## 13. Atajos y buenas practicas

1. **Primero API, luego dashboard:** Siempre ejecuta la API primero. Espera el mensaje "Modelos cargados OK" en la consola de la API antes de abrir el navegador.
2. **Usa la precarga historica:** Evita errores de digitacion.
3. **Modulo 5 es tu testigo:** Si Modulo 5 marca 4/4 CUMPLE, puedes confiar en todas las demas predicciones.
4. **Limpia cache despues de cambios en la API:** Si reinicias la API o cambias modelos, pulsa "Limpiar cache y recargar".
5. **Comparte el enlace del manual:** Si otro miembro tiene dudas, envia el archivo `Guia_Usuario_Dashboard_SAI.md` junto con `Guia_Solucion_SAI_F3.md`.

---

## 14. Resumen rapido (hoja de referencia 1 pagina)

| Que quiero hacer? | Donde voy | Que hago |
|:-----------------|:---------|:---------|
| Ver RMSE y prima oficiales | Modulo 1 KPIs | Lee las 6 tarjetas. |
| Saber si 2015 activo seguro | Modulo 5 Validacion | Ve fila Narino 2015 / Quindio 2015 |
| Predecir rendimiento con datos de 2012 | Sidebar Precarga -> Modulo 3 | Dep=Narino, Anio=2012 -> Cargar -> Calcular |
| Ver grafico SPI por etapa | Modulo 2 Track A | Columna izquierda. |
| Comparar predicho vs real historico | Modulo 4 LOYO | Grafico lineas. |
| Calcular prima total 12 anios, 1000 ha | Sidebar Calculadora + Modulo 6 | Cambia ha a 1000 -> lee KPIs Modulo 6 |
| Aumentar prima para ver superavit | Sidebar slider Sobrecarga % | Arrastra a 20% -> ve Balance. |
| Resetear todo | Sidebar final | Boton "Limpiar cache y recargar" |

---

*Fin de la Guia de Usuario. Para problemas de instalacion o ejecucion, consulta Guia_Solucion_SAI_F3.md en la misma carpeta.*
