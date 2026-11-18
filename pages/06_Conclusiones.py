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
    st.markdown("""
El análisis evidencia que la ocurrencia de colisiones en California durante el periodo 2010–2019 no es aleatoria, sino que responde directamente a la dinámica poblacional y a las rutinas diarias de desplazamiento. En la dimensión temporal, tras un mínimo cercano a las 380.000 colisiones en 2013, los registros mostraron un ascenso continuo desde 2015 hasta alcanzar su nivel más alto en 2016 y 2017 (alrededor de 490.000 incidentes por año). A lo largo del año, el volumen máximo se concentra en octubre (~400.000) y el más bajo en febrero (~340.000); mientras que por día de la semana, el viernes acumula la mayor carga (~710.000) en contraste con el domingo (~510.000). Dentro de la jornada diaria, los choques se acentúan en las franjas de entrada y salida laboral, destacando un primer pico entre las 7:30 y 8:30 y el mayor repunte entre las 15:00 y 18:00. Territorialmente, la siniestralidad se agrupa en los grandes núcleos urbanos, con Los Ángeles a la cabeza (aproximadamente 1,4 millones de colisiones), seguido por Orange, San Bernardino, San Diego y Riverside.

Frente a este escenario, los lineamientos de organismos especializados sugieren enfocar las medidas preventivas en dos frentes:

* **Control vial focalizado en franjas críticas***, reforzando la vigilancia, el control de velocidad y la gestión del flujo vehicular durante las horas pico vespertinas, los viernes y el último trimestre del año, conforme a las recomendaciones de la National Highway Traffic Safety Administration (NHTSA) y la Organización Mundial de la Salud (OMS).
* **Priorización de infraestructura en zonas metropolitanas de alta concentración***, aplicando auditorías viales, mejoras en intersecciones conflictivas y sistemas inteligentes de transporte (ITS) en condados clave como Los Ángeles, Orange y San Bernardino, en sintonía con las guías de la Federal Highway Administration (FHWA). 
    """)

with tab2:
    st.markdown("Edad del Conductor y Alcohol")
    st.markdown("""
Los resultados muestran que la siniestralidad vial se concentra de manera marcada en los conductores jóvenes y adultos jóvenes. El grupo de 25 a 34 años registra el mayor volumen absoluto (superando los 1,6 millones de colisiones), seguido muy de cerca por el segmento de 16 a 24 años (alrededor de 1,55 millones). A partir de los 35 años, el número total de incidentes desciende de forma progresiva en cada tramo etario hasta alcanzar su punto más bajo en los conductores de 65 años o más (cerca de 600.000 colisiones). En todos los rangos de edad, las colisiones no graves dominan ampliamente el volumen total (superando los 8 millones de registros en conjunto) frente a una proporción menor de siniestros graves (K o A). Asimismo, destacan dos hallazgos clave en la calidad del registro: un volumen elevado en la categoría Desconocido / Menor de 16 (superior a 1,3 millones) y la presencia exclusiva de registros clasificados bajo Alcohol Involucrado = No en el subconjunto visualizado, lo que evidencia brechas en la captura o codificación de estas variables en la fuente analizada.

Para abordar estos hallazgos, las recomendaciones de organismos técnicos e internacionales se orientan hacia dos ejes principales:

1.    **Educación vial focalizada y esquemas de licenciamiento gradual para conductores de 16 a 34 años**, reforzando la prevención de conductas de riesgo en los grupos etarios con mayor concentración de colisiones, en línea con las directrices de la National Highway Traffic Safety Administration (NHTSA) y la Organización Mundial de la Salud (OMS).
2.    **Estandarización y auditoría de los reportes policiales en escena**, mejorando la captura de variables críticas como la edad del conductor y los indicadores de consumo de alcohol —conforme a los estándares de calidad de datos promovidos por la NHTSA y el Safe Transportation Research and Education Center (SafeTREC, UC Berkeley)— para reducir el peso de los registros desconocidos y evaluar con precisión el impacto real del alcohol.
    """)
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
    st.markdown("""
Los resultados demuestran que la mayor frecuencia absoluta de víctimas involucradas en colisiones se concentra en los vehículos de menor antigüedad (especialmente entre 0 y 5 años, con un máximo en aquellos de 1 año). Posteriormente, aunque se registra un leve repunte en el volumen de afectados alrededor de los 9 y 10 años de antigüedad, el total de víctimas desciende de manera progresiva a medida que la edad del automóvil continúa aumentando. Sin embargo, al examinar la distribución interna de las lesiones según la escala KABCO (nivel de severidad), se observa que ni el pico inicial ni el repunte intermedio producen un aumento lineal en el volumen de desenlaces graves (K o A), predominando de forma constante las lesiones leves (C) y los ocupantes sin lesiones aparentes (O) en todos los tramos de antigüedad analizados. Para mitigar esto se hace recomendaciones claves:

1.    **Uso obligatorio y fiscalización de sistemas de retención**: Dado que el mayor volumen absoluto de víctimas ocurre en los vehículos más recientes (0 a 5 años) y que predominan las lesiones leves o sin daños aparentes, organismos como la Organización Mundial de la Salud (OMS) y los Centros para el Control y la Prevención de Enfermedades (CDC) destacan que el uso correcto del cinturón de seguridad y de los sistemas de retención infantil constituye el factor principal que contiene la escalada hacia lesiones graves (A) o fatales (K) durante una colisión.
2.    **Inspecciones técnicas periódicas (Mantenimiento del vehículo)**: Dado que los vehículos siguen registrando un volumen significativo de ocupantes incluso alrededor de los 9 a 12 años de antigüedad, organizaciones como la Administración Nacional de Seguridad del Tráfico en las Carreteras (NHTSA) y el Insurance Institute for Highway Safety (IIHS) enfatizan el control riguroso de los sistemas de seguridad activa y pasiva (frenos, neumáticos, suspensión y bolsas de aire) a lo largo de todo el ciclo de vida útil del automóvil, independientemente de su año de fabricación.

""")