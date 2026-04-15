import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
#import locale
#locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')

from utils.graficos import histograma_tiempos, barras_tiempo_hora
from utils.tablas import tabla_extremos, calcular_metricas_gestion

# --- DATA LOADING ---
@st.cache_data
def load_data():
    df_act = pd.read_parquet("Data/ActivaInfo.parquet").drop(["CodigoCedente","Duplicado"], axis=1)
    for col in df_act.select_dtypes("category").columns:
        df_act[col] = df_act[col].cat.remove_unused_categories()

    df_act = df_act.drop_duplicates(subset=["id","Producto"])
    mapeo_fechas = {s: s.strftime("%B")[:3].title() + '-' + s.strftime("%Y") for s in sorted(df_act['Fecha'].unique())}
    
    df_act['Fecha'] = pd.Categorical(df_act['Fecha'].map(mapeo_fechas), categories=list(mapeo_fechas.values()), ordered=True)

    df_act["Hora"] = df_act.FechaGestion.dt.hour
    return df_act

df_act = load_data()

st.title(":material/bar_chart: Tiempos de Gestión")
st.markdown(
    # "This dashboard is a showcase of **streamlit-echarts**, demonstrating how to integrate "
    # "highly interactive ECharts visualizations into Streamlit apps using real-world enterprise data.  \n"
    f"📅 **Periodo de análisis:** {df_act['Fecha'].min()} a {df_act['Fecha'].max()}"
)

# --- SIDEBAR: Filters + Info ---
with st.sidebar:
    st.title(":material/filter_alt: Filtros")

    selected_contact_type = st.pills(
        "Tipo de Contacto", 
        options=["Directo", "Indirecto"],
        selection_mode="multi",
        key="ContactoAct",
        bind="query-params"
    )

    months = df_act["Fecha"].cat.categories

    selected_dates = st.select_slider(
        "Línea de tiempo",
        options=months,
        value=(months[0], months[-1]),
        key="FechaAct",
        bind="query-params"
    )
     
    selected_products = st.multiselect(
        "Producto",
        options=sorted(df_act.Producto.cat.categories.to_list()),
        default=[],
        key="ProductoAct",
        bind="query-params"
    )

    selected_stages = st.multiselect(
        "Etapa de Cobranza",
        options=['PRIMERA','SEGUNDA','TERCERA', 'CUARTA', 'SEXTA','SEPTIMA','OCTAVA', 'NO DEFINIDO'],
        default=[],
        key="EtapaAct",
        bind="query-params"
    )

# --- FILTER LOGIC ---
# Categorical Filtering
def apply_categorical_filters(_base_df, dates, products, stages, contact_type):
    filtered = _base_df.copy()
    
    if dates:
        filtered = filtered[filtered["Fecha"].isin(dates)]
    if products:
        filtered = filtered[filtered["Producto"].isin(products)]
    if stages:
        filtered = filtered[filtered["Etapa"].isin(stages)]
    if contact_type:
        filtered = filtered[filtered["TipoContacto"].isin(contact_type)]
        
    return filtered

current_df = apply_categorical_filters(
    df_act, 
    selected_dates, 
    selected_products, 
    selected_stages, 
    selected_contact_type
)

# Tarjetas
metricas = calcular_metricas_gestion(current_df["duracion"])

with st.container(border=True):
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    with kpi_col1:
        st.metric(
            label="Total Gestiones", 
            value=metricas["cantidad"]
        )

    with kpi_col2:
        st.metric(
            label="Tiempo Promedio", 
            value=metricas["promedio"]
        )

    with kpi_col3:
        st.metric(
            label="Mediana del tiempo", 
            value=metricas["mediana"]
        )

    with kpi_col4:
        st.metric(
            label="Casos Críticos (>P97)", 
            value=metricas["criticos"]
        )

# Histograma y extremos
col1, col2 = st.columns([1.2, .8])

with col1:
    fig_activa = histograma_tiempos(current_df["duracion"])
    st.plotly_chart(fig_activa, use_container_width=True)

with col2:
    cols = ['id', 'UserNameGestion', 'FechaGestion', 'TipoContacto', 'duracion', 'NumeroOperacion', 'Producto', 'Etapa']
    extremos = tabla_extremos(current_df, cols)
    
    st.write("### 100 Casos mas Extremos") 
    st.dataframe(
        extremos,
        use_container_width=True,
        height=350,
        hide_index=True
    )

st.divider()

# Tiempos por hora del dia
st.write("### Tiempos por horas del día") 
tipo_calculo = st.radio(
    "Selecciona la métrica a visualizar:",
    options=["Promedio", "Total"],
    horizontal=True,
    key="selector_metrica"
)

if tipo_calculo == "Promedio":
    agg_func = "mean"
elif tipo_calculo == "Total": 
    agg_func = "sum"
else:
    raise ValueError("Funcion no implementada")

fig_barras = barras_tiempo_hora(current_df, agg_func)
st.plotly_chart(fig_barras, use_container_width=True)
