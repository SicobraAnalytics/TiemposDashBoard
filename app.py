import streamlit as st

st.set_page_config(
    page_title="Tiempos de Gestion",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

pg = st.navigation(
    [
        st.Page(
            "pages/activa.py",
            title="Cartera Activa",
            icon=":material/dashboard:",
            default=True,
        ),
        st.Page(
            "pages/pasiva.py", 
            title="Cartera Pasiva", 
            icon=":material/menu_book:"
        )
    ]
)
pg.run()