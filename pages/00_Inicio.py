"""Portada de la aplicación."""

import streamlit as st

import estilo
from datos import consulta

estilo.encabezado(
    "Colisiones de tránsito en California, 2010–2019",
    bajada="Esta plataforma interactiva recopila la investigación descriptiva sobre colisiones "
           "de tránsito en California durante el período decenal 2010–2019, a partir del "
           "registro oficial SWITRS (<i>Statewide Integrated Traffic Records System</i>), "
           "administrado por la California Highway Patrol (CHP).",
    antetitulo="Computación II · Escuela de Estadística y Ciencias Actuariales · UCV",
)

cifras = consulta("""
    SELECT COUNT(*)        AS colisiones,
           SUM(partes)     AS partes,
           SUM(victimas)   AS victimas,
           SUM(fallecidos) AS fallecidos
    FROM colisiones_normalizada.vw_colision
    WHERE anio BETWEEN 2010 AND 2019
""").iloc[0]

st.write("")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Colisiones registradas", estilo.entero(cifras.colisiones), border=True)
c2.metric("Partes involucradas", estilo.entero(cifras.partes), border=True)
c3.metric("Víctimas", estilo.entero(cifras.victimas), border=True)
c4.metric("Fallecidos", estilo.entero(cifras.fallecidos), border=True)
estilo.nota("Todas las colisiones registradas en los 58 condados del estado entre el 1 de enero "
            "de 2010 y el 31 de diciembre de 2019. Se trabaja con el universo completo, no con "
            "una muestra.")

st.write("")
st.subheader("Pregunta de investigación")
estilo.pregunta(
    "¿Cómo se distribuyeron las colisiones de tránsito en California entre 2010 y 2019 en el "
    "tiempo y entre los condados, y qué características del conductor, de las condiciones "
    "ambientales y del vehículo se asocian con la gravedad de los choques?"
)

st.subheader("Objetivos de la investigación")
estilo.conclusion(
    "Analizar la distribución temporal y territorial de las colisiones de tránsito en "
    "California entre 2010 y 2019 y su asociación con características del conductor, del "
    "entorno y del vehículo.",
    titulo="Objetivo general",
)

OBJETIVOS = [
    ("Tiempo y territorio",
     "Describir los patrones temporales (año, mes, día y hora) y geográficos por condado, "
     "con conteos y tasas por 100.000 habitantes.",
     "Colisión; condado y año"),
    ("Conductor culpable",
     "Comparar cómo se asocian la edad del conductor culpable y el alcohol con la gravedad "
     "del choque, comparando la proporción de colisiones graves en cada grupo.",
     "Colisión con un conductor como culpable"),
    ("Condiciones del entorno",
     "Describir la distribución de choques según iluminación, clima y estado de la calzada, "
     "y la proporción de choques graves en cada condición.",
     "Colisión"),
    ("Vehículo y ocupantes",
     "Examinar la relación entre la antigüedad del vehículo y la gravedad de las lesiones "
     "de sus ocupantes.",
     "Víctima que viajaba en un vehículo"),
]
columnas = st.columns(4)
for i, (columna, (titulo, texto, unidad)) in enumerate(zip(columnas, OBJETIVOS), start=1):
    with columna.container(border=True, height="stretch"):
        st.markdown(f'<div class="antetitulo">Objetivo específico {i}</div>',
                    unsafe_allow_html=True)
        st.markdown(f"**{titulo}**")
        st.markdown(texto)
        st.markdown(f'<p class="nota">Unidad de análisis: {unidad}</p>',
                    unsafe_allow_html=True)

st.write("")
st.subheader("Recorrido")
RECORRIDO = [
    ("pages/05_Analisis_de_Resultados.py", "Análisis de resultados", ":material/monitoring:",
     "Mapa interactivo de los condados, patrones en el tiempo y los cuatro objetivos."),
    ("pages/06_Conclusiones.py", "Conclusiones", ":material/task_alt:",
     "Hallazgos de cada objetivo y recomendaciones."),
    ("pages/04_Cuestionario_SQL.py", "Cuestionario SQL", ":material/database:",
     "Cinco consultas que se ejecutan en vivo sobre la fuente cruda en MotherDuck."),
    ("pages/02_Marco_Metodologico.py", "Marco metodológico", ":material/schema:",
     "Tipo y diseño de la investigación, población, variables y tratamiento de los datos."),
    ("pages/01_Marco_Teorico.py", "Marco teórico", ":material/menu_book:",
     "Factores de la severidad de las colisiones y medidas descriptivas usadas."),
    ("pages/03_Diccionario_de_Datos.py", "Diccionario de datos", ":material/table_view:",
     "Tablas, campos y catálogos de la base normalizada."),
]
for fila in (RECORRIDO[:3], RECORRIDO[3:]):
    for columna, (pagina, titulo, icono, texto) in zip(st.columns(3), fila):
        with columna.container(border=True, height="stretch"):
            st.page_link(pagina, label=titulo, icon=icono)
            st.markdown(f'<p class="nota">{texto}</p>', unsafe_allow_html=True)
