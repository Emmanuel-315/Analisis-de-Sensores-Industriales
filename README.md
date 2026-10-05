# Análisis de sensores industriales

## Objetivo

Analizar las lecturas de temperatura y vibración de sensores
instalados en cuatro plantas industriales, para detectar lecturas de
temperatura en alerta (mayores a 85 °C) y resumir el comportamiento
de cada planta. El proyecto es reproducible: cualquier persona puede
clonarlo, instalar las dependencias y obtener los mismos resultados.

## Datos

- **Archivo:** `data/sensores_industriales.csv`
- **Registros:** 100,000 mediciones
- **Sensores:** 40, distribuidos en 4 plantas (`Planta_1` a `Planta_4`)
- **Columnas:** `id_registro`, `fecha_hora`, `id_sensor`, `planta`,
  `temperatura_c`, `vibracion_mm_s`
- **Los datos son simulados**, generados con fines didácticos para
  este ejercicio. No corresponden a mediciones reales de ninguna
  empresa.
- El umbral de alerta de temperatura (> 85 °C) es una regla definida
  para este ejercicio, no un estándar industrial real.

## Requisitos

- Python 3.10 o superior
- pandas (ver `requirements.txt`)

## Instalación

```bash
# 1. Clonar el repositorio
git clone URL_DEL_REPOSITORIO
cd nombre-del-repositorio

# 2. Crear el entorno virtual
python -m venv .venv

# 3. Activarlo
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt
```

## Ejecución

```bash
python analisis.py
```

El script:
- Lee `data/sensores_industriales.csv` usando una ruta relativa a su
  propia ubicación (funciona sin importar desde dónde se invoque).
- Imprime en consola: cantidad de registros y sensores, temperatura
  promedio por planta, la temperatura máxima (con el/los sensor(es) y
  fecha(s) donde ocurrió), el total de lecturas en alerta y la(s)
  planta(s) con más alertas.
- Exporta todas las lecturas en alerta a `resultados/alertas.csv`,
  conservando las columnas originales.

## Estructura del proyecto

```
.
├── data/
│   └── sensores_industriales.csv
├── resultados/
│   └── alertas.csv              # Generado al ejecutar analisis.py
├── evidencias/
│   └── reproducibilidad.png     # Captura de la ejecución en una segunda copia
├── analisis.py
├── informe.md                   # Respuestas a la Parte II (Big Data)
├── requirements.txt
├── .gitignore
└── README.md
```

## Informe

El informe con la descritcion de las 5 V, tipos de datos, batch/streaming,
arquitecturas Lambda/Kappa y analítica descriptiva/predictiva/
prescriptiva están en [`informe.md`](informe.md).
