import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy.stats import gaussian_kde

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

def histograma_tiempos(s: pd.Series):
    s = s.dropna()
    max_val = s.quantile(.97)
    n_sample = min(len(s), 10_000)
    sample = s.sample(n_sample, random_state=42)

    kde = gaussian_kde(sample)
    x_range = np.concatenate([
        np.linspace(0, max_val, 500), 
        np.linspace(max_val, sample.max(), 11)[1:]
    ])

    tiempo_formateado = [format_time(seg) for seg in x_range]

    y_density = kde(x_range)
    y_cumulative = np.cumsum(y_density) * (x_range[1] - x_range[0]) * 100
    datos_hover = np.stack((y_cumulative, tiempo_formateado), axis=-1)

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=sample,
        name="Histograma",
        histnorm='probability density',
        xbins=dict(
            start=0,
            end=1.5*max_val,
            size=int(max_val/60)
        ),
        marker_color='#2E86C1',
        marker_line=dict(color='#D6EAF8', width=.6),
        opacity=0.4,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=x_range,
        y=y_density,
        mode='lines',
        line=dict(color='#2E86C1', width=2.5),
        name="Curva de Densidad",
        customdata=datos_hover, 
        hovertemplate=(
            "<b>Tiempo de Gestión:</b> %{customdata[1]}<br>" + # <--- MM:SS
            "<b>Población Acumulada:</b> %{customdata[0]:.1f}%" +
            "<extra></extra>"
        )
    ))

    fig.update_layout(
        title={
            'text': "Densidad de Tiempos de Gestión",
            'y': 0.95,
            'x': 0.05,
            'xanchor': 'left',
            'yanchor': 'top',
            'font': dict(size=25, color='#1B4F72')
        },
        
        template="plotly_white",
        bargap=0.05,
        showlegend=True,
        legend=dict(
            yanchor="top", 
            y=0.98,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255, 255, 255, 0.5)",
            bordercolor="#566573",
            borderwidth=.5,
            font = dict(size=15)
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        
        xaxis=dict(
            title=dict(text="Tiempo de Gestión (segundos)", font=dict(color='#566573', size=18)),
            tickfont=dict(color='#566573', size=15),
            showgrid=True,
            zeroline=True,
            range=[0, max_val],
        ),

        yaxis=dict(
            title=dict(text="Densidad", font=dict(color='#566573', size=18)),
            tickfont=dict(color='#566573', size=15),
            showgrid=True,
            gridcolor='#EBEDEF',
            zeroline=True
        ),

        hoverlabel=dict(
            bgcolor="white",
            font_size=14, 
            font_family="Arial",
            font_color="#1B4F72",
            bordercolor="#2E86C1", 
            namelength=0
        ),
    )

    return fig

def barras_tiempo_hora(df, agg_func="mean"):
    df_filtrado = df[df.Hora.between(7, 20) & ~df.FechaGestion.dt.weekday.isin([5,6])].copy()
    n_sample = min(len(df_filtrado), 10_000)
    df_filtrado = df_filtrado.sample(n_sample, random_state=42)
    
    if agg_func == "mean":
        param_func = {
            "func":"mean", 
            "title":"⌚ Promedio del Tiempo de Gestión por Hora del día y Tipo de Contacto",
            "ylabel": "Tiempo Promedio (seg)"
            }
    elif agg_func == "sum": 
        param_func = {
            "func":"sum", 
            "title":"⌚ Total del Tiempo de Gestión por Hora del día y Tipo de Contacto",
            "ylabel": "Total Tiempo (seg)"
            }
    else:
        raise ValueError("Funcion de agregacion no implementada")
    df_grouped = df_filtrado.groupby(['Hora', 'TipoContacto'])['duracion'].agg(param_func["func"]).reset_index()

    df_grouped['duracion_txt'] = df_grouped['duracion'].apply(format_time)

    horas_unicas = sorted(df_grouped["Hora"].unique())
    fig_barras = px.bar(
        df_grouped, 
        x="Hora", 
        y="duracion", 
        color="TipoContacto",
        barmode="group",
        color_discrete_sequence=["#2E86C1", "#E67E22"], 
        category_orders={"Hora": horas_unicas},
        title=param_func["title"],
        labels={"duracion": param_func["ylabel"], "Hora": "Hora del Día"},
        custom_data=["duracion_txt"]
    )
    fig_barras.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=450,
        template="plotly_white",
  
        title=dict(
            font=dict(size=20, color='#1B4F72'),
            x=0.02,
            y=0.95
        ),
        
        legend=dict(
            title="",
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color='#566573')
        ),
        
        hovermode="x unified",
        
        xaxis=dict(
            title=dict(standoff=10),
            showgrid=False,
            tickmode='array',
            tickvals=list(range(7, 21)),
            ticktext=[f"{h if h <= 12 else h - 12}{'AM' if h < 12 else 'PM'}" for h in horas_unicas],
            tickfont=dict(color='#566573')
        ),
        
        yaxis=dict(
            showgrid=True,
            gridcolor='#EAECEE',
            tickfont=dict(color='#566573'),
            zeroline=False
        )
    )

    fig_barras.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{data.name}</b>: %{customdata[0]}<extra></extra>"
    )

    return fig_barras