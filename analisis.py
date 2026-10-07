"""
Análisis de lecturas de sensores industriales.

Lee data/sensores_industriales.csv, calcula estadísticas sobre
temperatura por planta y sensor, identifica alertas (temperatura
> 85 °C) y exporta las lecturas en alerta a resultados/alertas.csv.

"""

import os
import pandas as pd

# Rutas relativas, calculadas a partir de la ubicación de este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CSV = os.path.join(BASE_DIR, "data", "sensores_industriales.csv")
RUTA_SALIDA = os.path.join(BASE_DIR, "resultados", "alertas.csv")
UMBRAL_ALERTA = 85.0  # °C — regla didáctica de este ejercicio


def cargar_datos(ruta: str) -> pd.DataFrame:
    df = pd.read_csv(ruta)
    df["fecha_hora"] = pd.to_datetime(df["fecha_hora"], format="%d/%m/%y %H:%M")
    return df


def main():
    df = cargar_datos(RUTA_CSV)

    print("=" * 60)
    print("ANÁLISIS DE SENSORES INDUSTRIALES (datos simulados)")
    print("=" * 60)

    # 1) Cantidad de registros y de sensores distintos
    n_registros = len(df)
    n_sensores = df["id_sensor"].nunique()
    print(f"\n1) Registros totales: {n_registros}")
    print(f"   Sensores distintos: {n_sensores}")

    # 2) Temperatura promedio por planta
    temp_promedio_planta = (
        df.groupby("planta")["temperatura_c"].mean().round(2).sort_values(ascending=False)
    )
    print("\n2) Temperatura promedio por planta (°C):")
    for planta, promedio in temp_promedio_planta.items():
        print(f"   {planta}: {promedio}")

    # 3) Temperatura máxima, con sensor(es) y fecha(s) (maneja empates)
    temp_maxima = df["temperatura_c"].max()
    registros_max = df[df["temperatura_c"] == temp_maxima]
    print(f"\n3) Temperatura máxima registrada: {temp_maxima} °C")
    print("   Sensor(es) y fecha(s) donde ocurrió:")
    for _, fila in registros_max.iterrows():
        print(f"   - Sensor {fila['id_sensor']} ({fila['planta']}) el {fila['fecha_hora']}")

    # 4) Conteo de lecturas con temperatura > 85 °C
    alertas = df[df["temperatura_c"] > UMBRAL_ALERTA]
    n_alertas = len(alertas)
    print(f"\n4) Lecturas con temperatura > {UMBRAL_ALERTA} °C: {n_alertas}")

    # 5) Planta con más alertas (maneja empates)
    alertas_por_planta = alertas.groupby("planta").size().sort_values(ascending=False)
    max_alertas = alertas_por_planta.max()
    plantas_top = alertas_por_planta[alertas_por_planta == max_alertas]
    print(f"\n5) Planta(s) con más alertas de temperatura ({max_alertas} alertas):")
    for planta, cantidad in plantas_top.items():
        print(f"   - {planta}: {cantidad} alertas")

    # 6) Exportar todas las lecturas en alerta, con columnas originales
    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)
    alertas_exportar = alertas.copy()
    alertas_exportar["fecha_hora"] = alertas_exportar["fecha_hora"].dt.strftime("%d/%m/%y %H:%M")
    alertas_exportar.to_csv(RUTA_SALIDA, index=False)
    print(f"\n6) Se exportaron {len(alertas_exportar)} lecturas en alerta a: {RUTA_SALIDA}")

    print("\n" + "=" * 60)
    print("Análisis completado.")
    print("=" * 60)


if __name__ == "__main__":
    main()
