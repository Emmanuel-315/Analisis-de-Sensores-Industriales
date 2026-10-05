# Informe — Aplicación al caso de Big Data

Proyecto: análisis de sensores industriales (datos simulados).
Los valores citados en este informe provienen de la ejecución de
`analisis.py` sobre `data/sensores_industriales.csv`.

---

## 5. Las 5 V aplicadas al proyecto

| V | Relación con el sistema de sensores | Ejemplo concreto | ¿Está en el CSV actual o es parte de la futura ampliación? |
|---|---|---|---|
| **Volumen** | Cantidad de datos generados por los sensores a lo largo del tiempo. | El CSV actual tiene 100,000 registros de 40 sensores en poco más de un día y medio de mediciones. | **CSV actual.** Con la ampliación a miles de sensores y lecturas por segundo, el volumen crecería en varios órdenes de magnitud. |
| **Velocidad** | Qué tan rápido se generan y necesitan procesarse los datos. | Actualmente cada sensor registra una lectura por minuto; la ampliación plantea lecturas cada segundo. | **Mixto.** El ritmo actual (una lectura/minuto) sí está en el CSV; el salto a lecturas por segundo es la **futura ampliación**. |
| **Variedad** | Diversidad de tipos y formatos de datos que el sistema maneja o manejará. | El CSV es tabular (estructurado); la ampliación añadiría JSON de sensores, fotografías y reportes de mantenimiento en texto libre. | **Futura ampliación.** El CSV actual es un único formato estructurado; no contiene imágenes ni texto libre. |
| **Veracidad** | Confiabilidad y calidad de los datos (errores de sensor, lecturas faltantes, ruido). | En el CSV actual no se encontraron valores nulos ni duplicados evidentes, pero sí lecturas extremas (hasta 104.99 °C) que podrían ser alertas reales o fallas de sensor. | **CSV actual**, aunque la pregunta de si una lectura extrema es un error de sensor o una condición real de la máquina no puede resolverse solo con este archivo. |
| **Valor** | La utilidad de negocio que se extrae de los datos. | Identificar que Planta_3 concentra el mayor número de alertas (1,777 de 6,954) permite priorizar mantenimiento preventivo en esa planta. | **CSV actual**, como primer nivel de valor descriptivo; la ampliación permitiría valor predictivo (anticipar fallas) y en tiempo real. |

---

## 6. Tipos de datos y procesamiento

| Elemento | Tipo de dato |
|---|---|
| El CSV de sensores | **Estructurado** (filas y columnas con esquema fijo y tipos definidos) |
| Un mensaje JSON enviado por un sensor | **Semiestructurado** (tiene una estructura jerárquica de clave-valor, pero no un esquema tabular rígido) |
| Una fotografía de una máquina | **No estructurado** (datos binarios sin un esquema que describa su contenido) |
| El texto libre de un reporte de mantenimiento | **No estructurado** (lenguaje natural sin una estructura predefinida) |

**¿Por qué 100,000 registros no convierten automáticamente al archivo en Big Data?**

El volumen por sí solo no define Big Data: 100,000 filas y poco más
de 4.6 MB es un tamaño que una sola computadora procesa en segundos
con herramientas convencionales como pandas, sin necesidad de
almacenamiento distribuido ni procesamiento paralelo. Big Data
describe sistemas donde el volumen, la velocidad o la variedad
superan la capacidad de las herramientas tradicionales (una sola
máquina, una hoja de cálculo, un único proceso) — no es solo
"muchos datos".

**Limitaciones que podrían aparecer al aumentar la escala:**

- Con miles de sensores y lecturas por segundo, el archivo ya no
  cabría cómodamente en memoria RAM de una sola máquina.
- Un script secuencial como `analisis.py` tardaría demasiado y
  dejaría de ser viable para generar alertas casi en tiempo real.
- Incorporar fotografías y texto libre requeriría almacenamiento y
  herramientas distintas a un CSV (bases de datos documentales,
  almacenamiento de objetos, procesamiento de imágenes/texto).
- Se necesitaría infraestructura distribuida (por ejemplo, un
  clúster de procesamiento) en lugar de un único proceso en Python.

---

## 7. Batch y Streaming

**Tipo de procesamiento utilizado en `analisis.py`:**

Es **procesamiento por lotes (batch)**: el programa lee un archivo
completo que ya fue guardado previamente (`sensores_industriales.csv`),
procesa todas las filas de una sola vez y produce un resultado al
final de la ejecución. No reacciona a datos a medida que llegan.

**Para emitir una alerta pocos segundos después de una lectura > 85 °C:**

Se usaría **procesamiento por streaming**. Cada lectura del sensor se
evaluaría en el momento en que llega (por ejemplo, con una
herramienta de procesamiento de flujos de eventos), comparando su
temperatura contra el umbral y generando la alerta de inmediato, sin
esperar a que se acumule un archivo completo.

**Para generar un resumen al terminar el día:**

Se usaría **procesamiento por lotes**, igual que el de este
proyecto: al final del día se toman todas las lecturas acumuladas y
se calculan los agregados (promedios, máximos, conteos de alertas)
en una sola ejecución.

**Relación con el tiempo en que se necesita cada resultado:**

La elección depende de la urgencia del resultado: una alerta de
seguridad necesita una respuesta en segundos, lo que exige streaming;
un resumen diario tolera procesarse horas después de generado el
dato, lo que hace que el batch sea más simple y suficiente —y más
barato de operar— para ese caso.

---

## 8. Lambda y Kappa

**Escenario A — combinar una ruta por lotes (historial) con otra rápida (mediciones recientes): arquitectura Lambda**

La arquitectura Lambda está diseñada exactamente para esto: mantiene
dos rutas en paralelo, una de **batch** que recalcula el historial
completo con precisión, y otra de **velocidad (speed layer)** que
procesa las mediciones recientes con baja latencia. Una capa de
servicio combina ambos resultados para responder consultas.

```
                 ┌─────────────────┐
 Sensores ──────▶│  Batch Layer     │──▶ Vista histórica
      │          │  (recalcula todo)│         │
      │          └─────────────────┘         ▼
      │                                ┌─────────────┐
      └───────▶┌─────────────────┐    │ Serving Layer│──▶ Consultas
               │  Speed Layer     │───▶│ (combina)   │
               │  (tiempo real)   │    └─────────────┘
               └─────────────────┘
```

**Escenario B — una sola lógica de procesamiento de eventos, conservando las mediciones para reprocesar: arquitectura Kappa**

La arquitectura Kappa usa **una sola ruta de procesamiento de
streaming** para todo (tanto tiempo real como recálculos), y conserva
los eventos en un log duradero. Si se necesita reprocesar, se vuelve
a reproducir el log completo a través de la misma lógica, en lugar de
mantener un sistema batch separado.

```
                ┌───────────────────────┐
 Sensores ─────▶│   Log de eventos       │
                │ (mediciones guardadas) │
                └───────────┬───────────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │  Procesamiento de     │──▶ Resultados /
                 │  streaming (única     │    Alertas
                 │  lógica)               │
                 └──────────────────────┘
                             ▲
                             │
              (reprocesa leyendo el log de nuevo)
```

---

## 9. Analítica descriptiva, predictiva y prescriptiva

**Descriptiva** (dos hallazgos reales de este análisis):

1. La temperatura promedio es muy similar entre las cuatro plantas
   (entre 66.53 °C y 66.77 °C), por lo que no hay una planta que
   opere sistemáticamente "más caliente" que las demás en promedio.
2. De 100,000 lecturas, 6,954 (≈ 6.95%) superaron el umbral de alerta
   de 85 °C, y Planta_3 concentra la mayor cantidad de estas alertas
   (1,777), seguida de cerca por Planta_1 (1,737) y Planta_4 (1,732).

**Predictiva:**

Pregunta: ¿qué sensores tienen mayor probabilidad de generar una
alerta de temperatura en las próximas horas, a partir de su historial
reciente de temperatura y vibración? Para investigarla se necesitarían
datos adicionales como: el historial de mantenimiento de cada sensor
o máquina, la carga de trabajo o nivel de uso de cada equipo, la
temperatura ambiente de cada planta, y, idealmente, un registro de
fallas pasadas (fecha y causa) para poder entrenar un modelo que
relacione patrones de sensor con fallas reales.

**Prescriptiva:**

Acción propuesta: dado que Planta_3 concentra el mayor número de
alertas, la empresa podría programar una inspección de mantenimiento
preventivo prioritaria en los sensores/máquinas de esa planta antes
de que ocurra una falla. Antes de decidir, convendría revisar si esas
alertas se concentran en pocos sensores específicos de Planta_3 (lo
que apuntaría a un equipo puntual con problema) o están distribuidas
entre muchos sensores de la planta (lo que apuntaría a un factor
ambiental, como ventilación o temperatura ambiente de esa planta).


