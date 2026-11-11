""" Marco Metodológico """

import streamlit as st

# configuracion inicial de la pagina del marco metodologico
st.set_page_config(page_title="Marco Metodológico", page_icon="🔬", layout="wide")

# marco metodologico en grande para que resalte en la pagina
st.title("Marco Metodológico")

# comienzo del marco teorico
st.markdown(
    """
En este capítulo se describe cómo se llevó a cabo la investigación: el tipo y el diseño del
estudio, la población analizada, las fuentes y técnicas de recolección de los datos, la
operacionalización de las variables, el procedimiento seguido para procesar la información y
las técnicas de análisis. Se detalla en especial el tratamiento de los datos, porque la fuente
original pesa cerca de 10 GB y debió ordenarse en una base de datos normalizada antes de
poder analizarse.
    """
)

st.subheader("1. Tipo de investigación")
st.markdown(
    """
La investigación es de tipo descriptivo. Según Hernández Sampieri, Fernández Collado y
Baptista Lucio (2014), los estudios descriptivos buscan especificar las propiedades y
características de un fenómeno, y medir o recoger información sobre las variables que lo
componen, sin pretender explicar sus causas. En este trabajo se describe cómo se
distribuyeron las colisiones de tránsito en California entre 2010 y 2019 en el tiempo y entre
los condados, y cómo varía la gravedad de los choques según características del conductor,
del entorno y del vehículo.
Por la fuente de los datos, es además una investigación documental. Arias (2012) la define
como aquella que se basa en la búsqueda, recuperación, análisis e interpretación de datos
secundarios, es decir, registrados previamente por otros. Aquí los datos provienen de los
partes policiales que la California Highway Patrol reúne en el sistema SWITRS, y de las
estimaciones de población del U.S. Census Bureau. El equipo no levantó datos propios.
El análisis se limita a la estadística descriptiva. No se plantean hipótesis causales ni se hacen
inferencias, porque se trabaja con todas las colisiones registradas y no con una muestra: las
proporciones y tasas que se presentan son valores de la población completa.
    """
)

st.subheader("2. Diseño de investigación")
st.markdown(
    """
El diseño es no experimental, porque no se manipula ninguna variable: se observan los
hechos tal como ocurrieron y quedaron registrados (Hernández Sampieri et al., 2014). Es
retrospectivo, porque estudia colisiones ya ocurridas, y longitudinal de tendencia, porque
sigue la evolución de la misma población, las colisiones de California, a lo largo de diez
años consecutivos.
    """
)

st.subheader("3. Población y muestra")
st.markdown(
    """
La población está formada por todas las colisiones de tránsito registradas en SWITRS dentro
de los 58 condados de California entre el 1 de enero de 2010 y el 31 de diciembre de 2019:
4.368.293 colisiones, en las que participaron 8.688.142 partes (conductores, peatones,
ciclistas y otros) y se registraron 4.280.801 víctimas, de las cuales 33.541 fallecieron.
No se extrajo una muestra. Como la población es finita y está completa y disponible en
formato digital, se trabajó con todos sus elementos, lo que corresponde a un estudio de tipo
censal. Así se evita el error de muestreo y los resultados describen el universo completo.
El período 2010-2019 se eligió por ser una década completa, anterior a los cambios de
movilidad producidos por la pandemia, y porque para esos mismos años existen
estimaciones oficiales de población por condado, necesarias para calcular tasas por
habitante.
    """
)

st.subheader("4. Fuentes de información")
st.markdown(
    """
Se usaron dos fuentes secundarias:
• Statewide Integrated Traffic Records System (SWITRS). Es el sistema en el que la
California Highway Patrol reúne los partes policiales de las colisiones de todo el
estado. Se usó la versión publicada por Gude (2021) en Kaggle: un archivo SQLite de
9,9 GB con las colisiones de 2001 a 2021, organizado en tres tablas principales:
collisions (9.424.334 filas y 75 columnas), parties (18.669.166 filas y 32 columnas) y
victims (9.639.334 filas y 11 columnas), más una tabla auxiliar, case_ids.

• Estimaciones de población del U.S. Census Bureau (County population totals:
2010-2019, edición 2019). El archivo original tiene 3.193 filas y 164 columnas con
todos los condados de Estados Unidos. Se conservaron los 58 condados de California y
la población estimada al 1 de julio de cada año entre 2010 y 2019, que se usa para
calcular tasas por 100.000 habitantes.
    """
)

st.subheader("5. Técnicas e instrumentos de recolección de datos")
st.markdown(
    """
La técnica empleada fue el análisis documental de registros administrativos: en lugar de
aplicar encuestas o entrevistas, se recuperaron y organizaron los datos que ya existían en las
fuentes descritas. Como instrumento se diseñó una base de datos relacional, que cumple la
función de una matriz de registro: define qué datos se toman de cada parte policial, con qué
tipo y con qué categorías. Su estructura completa, campo por campo, está documentada en el
diccionario de datos del repositorio del proyecto.
    """
)

st.subheader("6. Operacionalización de las variables")
st.markdown(
    """
    """
)

st.subheader("7. Procedimiento")
st.markdown(
    """
    """
)

st.subheader("8. Técnicas de análisis de datos")
st.markdown(
    """
Se aplicaron únicamente técnicas de estadística descriptiva:
• Distribuciones de frecuencias absolutas y relativas de las colisiones por año, mes,
día de la semana, hora, condado y condición del entorno.
• Proporción de colisiones graves y con fallecido en cada grupo, para separar la
frecuencia de la gravedad: un grupo puede tener pocas colisiones pero muy graves.
• Tasas por 100.000 habitantes, para comparar condados con poblaciones muy
distintas.
• Cocientes y diferencias de proporciones, para expresar cuántas veces más frecuente
es un desenlace en un grupo que en otro, y a cuántos puntos porcentuales de distancia.
• Tablas cruzadas, para observar dos variables a la vez; por ejemplo, la proporción de
colisiones mortales con y sin alcohol dentro de cada banda de edad del conductor
culpable.
• Medidas de tendencia central, como la antigüedad media de los vehículos.
    """
)

st.subheader("9. Validez y confiabilidad de los datos")
st.markdown(
    """
La validez de los datos descansa en su origen oficial: son los partes que levantan los agentes
de tránsito y que la California Highway Patrol consolida para todo el estado. La
confiabilidad del tratamiento se garantiza por tres vías: el proceso es automático y
reproducible, de modo que al repetirlo se obtienen los mismos resultados; cada etapa se
validó contra la anterior, como se describe en la fase 7; y todas las decisiones de limpieza y
de modelado quedaron documentadas en el diccionario y en el documento de modelado de
datos del repositorio.
    """
)

st.subheader("10. Consideraciones éticas")
st.markdown(
    """
Los datos son públicos y anónimos: los partes no incluyen nombres, direcciones ni otros
datos que permitan identificar a las personas. Se usaron solo con fines académicos y se citan
sus fuentes.
    """
)

st.subheader("11. Limitaciones metodológicas")
st.markdown(
    """
• En 2017 SWITRS cambió los códigos de lesión, y entre 2016 y 2019 las víctimas con
lesión grave aumentan un 23,9 % sin que los choques sean más graves. Por eso, para
comparar años se usan solo los fallecidos.
• El alcohol solo se registra cuando estuvo presente. Que no aparezca significa que no se
reportó, no que el conductor estuviera sobrio.
• La edad del conductor culpable falta en el 71,2 % de las colisiones con fuga y en el 2,2
% de las demás, así que el objetivo 2 se analiza también sin las fugas.
• Solo el 49,4 % de las colisiones tiene coordenadas, y la cobertura pasa del 34,3 % en
2010 al 64,1 % en 2019. Por eso el análisis territorial se hace por condado.
• No hay datos de exposición, como kilómetros recorridos o parque vehicular. Se
describe cómo se reparten las colisiones y su gravedad, no el riesgo de chocar.
• La población del Census cuenta a quienes viven en el condado, no a quienes lo
atraviesan; los condados pequeños con carreteras de paso muestran tasas muy altas.
    """
)

st.subheader("12. Herramientas tecnológicas")
st.markdown(
    """
    """
)