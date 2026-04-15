import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

def tabla_extremos(df, cols, head=100):
    cota_extremo = df["duracion"].quantile(.97)
    extremos = (
        df.loc[df["duracion"]>cota_extremo, cols]
        .sort_values("duracion", ascending=False)
        .head(head)
        .set_index("id")
    )

    return extremos

def format_time(segundos):
    """
    Formatea segundos a un formato dinámico: 'Xh Ymin Zseg'
    Elimina las unidades que sean cero.
    Ejemplo: 3665 -> '1h 1min 5seg'
    Ejemplo: 125  -> '2min 5seg'
    Ejemplo: 5    -> '5seg'
    """
    if segundos is None or pd.isna(segundos) or segundos == 0:
        return "0seg"
    
    # Cálculos matemáticos
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    
    # Construcción de la cadena dinámica
    partes = []
    if horas > 0:
        partes.append(f"{horas}h")
    if minutos > 0:
        partes.append(f"{minutos}min")
    if segs > 0 or not partes: # El 'not partes' asegura que si todo es 0, al menos devuelva algo
        partes.append(f"{segs}seg")
    
    return " ".join(partes)

def calcular_metricas_gestion(s: pd.Series):
    """
    Calcula métricas clave para una serie de tiempos de gestión.
    """
    # Limpieza básica
    s = s.dropna()
    
    # Cálculos estadísticos
    cantidad = len(s)
    promedio = s.mean()
    mediana = s.median()
    
    # Casos Críticos (Mayores al Percentil 97)
    p97 = s.quantile(0.97)
    casos_criticos = len(s[s > p97])

    return {
        "cantidad": f"{cantidad:,}",
        "promedio": format_time(promedio),
        "mediana": format_time(mediana),
        "criticos": f"{casos_criticos:,}"
    }