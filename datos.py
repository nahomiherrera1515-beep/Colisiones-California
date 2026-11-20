"""Conexión compartida con MotherDuck.

Una sola conexión para toda la app (st.cache_resource) y resultados guardados en
caché por consulta, para que cada gráfico no vuelva a consultar la nube en cada
interacción. El cuestionario SQL no usa esta caché: sus consultas corren en vivo.
"""

import duckdb
import pandas as pd
import streamlit as st


@st.cache_resource(show_spinner=False)
def conexion():
    token = st.secrets["motherduck_token"]
    return duckdb.connect(f"md:?motherduck_token={token}")


@st.cache_data(show_spinner=False, ttl="12h")
def consulta(sql: str) -> pd.DataFrame:
    # un cursor por consulta: varias personas pueden usar la app al mismo tiempo
    return conexion().cursor().execute(sql).df()
