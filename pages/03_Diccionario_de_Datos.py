"""Diccionario de Datos"""

import streamlit as st
import pandas as pd

# configuracion inicial de la pagina de el diccionario de datos
st.set_page_config(page_title="Diccionario de Datos", page_icon="🗂️", layout="wide")

# titulo
st.title("Diccionario de Datos")
st.caption("Resumen del Diccionario de Datos")
st.markdown("---")

# categoria 1: datos generales de colisiones
st.markdown("## Datos Generales de Colisiones")

st.markdown("### Tabla colision")
st.markdown(
    "Una fila por colisión que centraliza los datos generales del parte"
    " policial, condiciones ambientales y factores de impacto."
)
st.markdown("""
| Atributos Clave | Descripción general |
| :--- | :--- |
| `case_id`, `fecha`, `hora` | Identificador único y momento en que ocurrió el choque. |
| `ubicacion_id`, `jurisdiccion` | Ubicación geográfica (condado/ciudad) y agencia policial interviniente. |
| `iluminacion_id`, `superficie_id`, `dispositivo_control_id` | Condiciones de luz, estado de la calzada y señalización vial. |
| `tipo_colision_id`, `implicado_con_id`, `factor_primario_id` | Dinámica del impacto y causa principal registrada. |
""")
st.caption(
    "Nota: La presente tabla incluye más atributos relacionados con"
    " infracciones, fugas y condiciones especiales."
)

st.markdown("---")

# categoria 2: clima y condiciones del entorno
st.markdown("## Clima y Condiciones del Entorno")
st.markdown(
    "Esta categoría agrupa las tablas secundarias que especifican los factores"
    " atmosféricos, el estado de la vía, la geolocalización GPS y la"
    " infraestructura de carreteras estatales."
)

st.markdown("### Desglose de tablas del bloque")
st.markdown("""
| Tabla | Atributos Clave | Descripción general |
| :--- | :--- | :--- |
| `colision_clima` | `case_id`, `orden`, `clima_id` | Factores atmosféricos principales y secundarios. |
| `colision_condicion_via` | `case_id`, `orden`, `condicion_via_id` | Estado de la vía, baches u obras registradas. |
| `colision_geo` | `latitud`, `longitud` | Coordenadas geográficas de ubicación espacial. |
| `colision_carretera` | `ruta_estatal`, `postmile`, `distrito_caltrans` | Identificación de rutas y puntos kilométricos de Caltrans. |
""")
st.caption(
    "Nota: Se incluyen atributos adicionales de posicionamiento"
    " detallados en la documentación completa."
)

st.markdown("---")

