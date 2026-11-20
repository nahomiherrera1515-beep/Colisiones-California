"""Aplicación de la investigación sobre colisiones de tránsito en California, 2010-2019.

Este archivo solo arma la navegación; el contenido de cada página está en pages/.
"""

import streamlit as st

import estilo

st.set_page_config(
    page_title="Colisiones de tránsito en California, 2010-2019",
    page_icon=":material/traffic:",
    layout="wide",
    initial_sidebar_state="auto",
)
estilo.aplicar()

POWER_BI = ("https://app.powerbi.com/view?r=eyJrIjoiOWZkYmRhZGUtMzBhZC00YTczLWI5MzAtN2EwMDhl"
            "ZTJiNTVjIiwidCI6IjRjODE4Zjc5LWFiODQtNDU1Mi05YjdjLTJmZTcxNWIwZDBkNSIsImMiOjR9"
            "&pageName=5b65695d2ea4c36459cb")
REPOSITORIO = "https://github.com/nahomiherrera1515-beep/Colisiones-California"

paginas = {
    "": [
        st.Page("pages/00_Inicio.py", title="Inicio", url_path="inicio", default=True),
    ],
    "Investigación": [
        st.Page("pages/01_Marco_Teorico.py", title="Marco teórico", url_path="marco-teorico"),
        st.Page("pages/02_Marco_Metodologico.py", title="Marco metodológico",
                url_path="marco-metodologico"),
        st.Page("pages/03_Diccionario_de_Datos.py", title="Diccionario de datos",
                url_path="diccionario"),
    ],
    "Resultados": [
        st.Page("pages/05_Analisis_de_Resultados.py", title="Análisis de resultados",
                url_path="analisis"),
        st.Page("pages/06_Conclusiones.py", title="Conclusiones", url_path="conclusiones"),
    ],
    "Anexos": [
        st.Page("pages/04_Cuestionario_SQL.py", title="Cuestionario SQL", url_path="cuestionario"),
        st.Page("pages/07_Bibliografia.py", title="Bibliografía", url_path="bibliografia"),
    ],
}

navegacion = st.navigation(paginas)

with st.sidebar:
    st.divider()
    st.caption("Fuente: Statewide Integrated Traffic Records System (SWITRS), California "
               "Highway Patrol. Población: U.S. Census Bureau.")
    st.markdown(f"[Tablero en Power BI]({POWER_BI})  \n[Repositorio en GitHub]({REPOSITORIO})")

navegacion.run()
