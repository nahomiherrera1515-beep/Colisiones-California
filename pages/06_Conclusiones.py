"""Conclusiones de la investigación"""

import streamlit as st

# configuracion inicial de la pagina de las conclusiones
st.set_page_config(page_title="Conclusiones", page_icon="📌", layout="wide")

# titulo
st.title("Conclusiones")


tab1, tab2, tab3, tab4 = st.tabs([
    "Patrones Temporales y Geográficos",
    "Edad del Conductor y Alcohol",
    "Condiciones Ambientales",
    "Antigüedad del Vehículo y Lesiones"
])

with tab1:
    st.markdown("Patrones Temporales y Geográficos")

with tab2:
    st.markdown("Edad del Conductor y Alcohol")

with tab3:
    st.markdown("Condiciones Ambientales")
    st.markdown("""
Los resultados demuestran que las condiciones con mayor volumen absoluto de 
colisiones graves (como la luz diurna, el clima despejado y el pavimento seco) responden a la alta 
exposición cotidiana del parque vehicular. En el caso de la gravedad los que mayor destacan son: 
Luz diurna con 71.524 colisiones, Despejado con 118.040 colisiones y Seca con 128.015 colisiones. 
Que la proporción interna de gravedad perteneciente a cada categoría sea de 6,28%, por ejemplo, no quiere 
decir que ahí ocurran la mayoría de las colisiones graves, ya que es una proporción condicional.

Para mitigar esta problemática, las recomendaciones de organismos 
internacionales y técnicos convergen en dos líneas de acción:

* **Gestión general del tránsito y velocidades en contextos de alta circulación**, alineada con las 
directrices de la Organización Mundial de la Salud (OMS) en su *Plan Mundial para el Decenio de Acción 
para la Seguridad Vial*.
* **Intervenciones focalizadas de infraestructura** (como el mantenimiento preventivo del alumbrado público 
respaldado por la Federal Highway Administration [FHWA] y los tratamientos de alta fricción en la vía 
recomendados por el Safe Transportation Research and Education Center [SafeTREC, UC Berkeley]) para reducir 
los picos de severidad en los entornos de mayor riesgo relativo.
""")


with tab4:
    st.markdown("""Antigüedad del Vehículo y Lesiones""")