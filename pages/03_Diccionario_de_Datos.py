"""Diccionario de Datos"""

import streamlit as st
import pandas as pd

# configuracion inicial de la pagina de el diccionario de datos
st.set_page_config(page_title="Diccionario de Datos", page_icon="🗂️", layout="wide")

# titulo
st.title("Diccionario de Datos")
st.caption("Resumen del Diccionario de Datos") 
st.markdown("---")


# esta parte de la app es un resumen del diccionario de datos, que se encuentra en el repositorio de GitHub.


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

# categoria 3: partes, victimas y seguridad
st.markdown("## Partes, Víctimas y Seguridad")
st.markdown(
    "Registra la información detallada de cada parte implicada, los factores"
    " asociados, el uso de equipos de protección y el reporte individual de"
    " víctimas afectadas."
)

st.markdown("### Desglose de tablas del bloque")
st.markdown("""
| Tabla | Atributos Clave | Descripción general |
| :--- | :--- | :--- |
| `parte` | `case_id`, `numero_parte`, `tipo_parte_id`, `culpable` | Identificación de la parte implicada, rol y responsabilidad. |
| `parte_equipo_seguridad` | `case_id`, `numero_parte`, `orden`, `equipo_seguridad_id` | Dispositivos de protección usados por las partes. |
| `parte_factor_asociado` | `case_id`, `numero_parte`, `orden`, `factor_asociado_id` | Factores adicionales asociados a la parte (distracción, visión). |
| `victima` | `case_id`, `numero_parte`, `numero_victima`, `lesion_id` | Registro individual de afectados y grado de lesión (KABCO). |
| `victima_equipo_seguridad` | `case_id`, `numero_parte`, `numero_victima`, `equipo_seguridad_id` | Equipos de protección específicos utilizados por las víctimas. |
""")
st.caption(
    "Nota: Este bloque comprende múltiples tablas puente y de relación que"
    " detallan equipos y factores específicos; consulte el boton inferior para ver"
    " el desglose completo."
)

st.markdown("---")

# categoria 4: catalogos y vistas de consumo
st.markdown("## Catálogos y Vistas de Consumo")
st.markdown(
    "Conjunto de tablas auxiliares para la traducción de códigos a texto,"
    " gestión demográfica y vistas precalculadas en MotherDuck."
)

st.markdown("### Desglose de estructuras y vistas")
st.markdown("""
| Tipo / Recurso | Atributos Clave | Descripción general |
| :--- | :--- | :--- |
| **Catálogos** | `catalogo_id`, `codigo`, `etiqueta`, `kabco` | Estructura base para traducción de códigos y niveles de severidad. |
| **Geografía / Población** | `condado_id`, `habitantes` | Gestión de condados y datos poblacionales del Census Bureau. |
| **Vistas (`vw_colision`, etc.)** | `anio`, `mes`, `severidad`, `alcohol_implicado` | Dimensiones temporales e indicadores clave precalculados. |
| **Tasas analíticas** | `colisiones_por_100k`, `fallecidos_por_100k` | Tasas normalizadas por habitante a nivel de condado y año. |
""")
st.caption(
    "Nota: El proyecto contempla decenas de catálogos y vistas especializadas;"
    " puede revisar todas sus columnas y definiciones haciendo clic en el botón"
    " superior."
)

st.markdown("---")

# boton de enlace al diccionario completo en GitHub
st.link_button(
    label="Para consultar el diccionario completo haga clic aquí",
    url=(
        "https://github.com/nahomiherrera1515-beep/Colisiones-California/blob/main/base_de_datos/DICCIONARIO_DE_DATOS.md"
    ),
    icon="🔗",
)