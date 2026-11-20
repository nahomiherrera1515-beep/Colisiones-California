"""Conclusiones de la investigación"""

import streamlit as st

import estilo

# titulo
estilo.encabezado("Conclusiones", antetitulo="Resultados")


tab1, tab2, tab3, tab4 = st.tabs([
    "Patrones Temporales y Geográficos",
    "Edad del Conductor y Alcohol",
    "Condiciones Ambientales",
    "Antigüedad del Vehículo y Lesiones"
])

with tab1:
    st.markdown("Patrones Temporales y Geográficos")
    st.markdown("""
El análisis evidencia que la ocurrencia de colisiones en California durante el periodo 2010–2019 no se reparte de manera uniforme: se concentra en ciertos años, meses, días, horas y condados, en coincidencia con la distribución de la población y con las rutinas diarias de desplazamiento. En la dimensión temporal, tras un mínimo cercano a las 380.000 colisiones en 2013, los registros mostraron un ascenso continuo desde 2015 hasta alcanzar su nivel más alto en 2016 y 2017 (alrededor de 490.000 incidentes por año). A lo largo del año, el volumen máximo se concentra en octubre (~400.000) y el más bajo en febrero (~340.000); mientras que por día de la semana, el viernes acumula la mayor carga (~710.000) en contraste con el domingo (~510.000). Dentro de la jornada diaria, los choques se acentúan en las franjas de entrada y salida laboral, destacando un primer pico entre las 7:30 y 8:30 y el mayor repunte entre las 15:00 y 18:00. Territorialmente, la siniestralidad se agrupa en los grandes núcleos urbanos, con Los Ángeles a la cabeza (aproximadamente 1,4 millones de colisiones), seguido por Orange, San Bernardino, San Diego y Riverside.

Frente a este escenario, los lineamientos de organismos especializados sugieren enfocar las medidas preventivas en dos frentes:

* **Control vial focalizado en franjas críticas**, reforzando la vigilancia, el control de velocidad y la gestión del flujo vehicular durante las horas pico vespertinas, los viernes y el último trimestre del año, conforme a las recomendaciones de la National Highway Traffic Safety Administration (NHTSA) y la Organización Mundial de la Salud (OMS).
* **Priorización de infraestructura en zonas metropolitanas de alta concentración**, aplicando auditorías viales, mejoras en intersecciones conflictivas y sistemas inteligentes de transporte (ITS) en condados clave como Los Ángeles, Orange y San Bernardino, en sintonía con las guías de la Federal Highway Administration (FHWA). 
    """)

with tab2:
    st.markdown("Edad del Conductor y Alcohol")
    st.markdown("""
Se analizaron las 3.926.268 colisiones del período cuyo culpable fue un conductor, tomando la edad de ese conductor. El grupo de 16 a 24 años es el que más colisiones causa (929.357), seguido por el de 25 a 34 años (804.242); entre los dos suman el 44 % del total. A partir de los 35 años el número baja en cada grupo, hasta 277.466 colisiones en los conductores de 65 años o más. La gravedad va en sentido contrario: el porcentaje de colisiones graves (K o A) sube con la edad, desde 2,94 % en el grupo de 16 a 24 años hasta 3,61 % en el de 65 o más. Es decir, los jóvenes son los culpables de más colisiones, pero aquellas en las que el culpable es mayor terminan más a menudo en muertes o heridos graves.

El alcohol aparece reportado en 412.240 colisiones (10,5 %). En ellas, el 7,13 % fue grave, frente al 2,31 % de las colisiones sin alcohol reportado: unas tres veces más. El grupo de 25 a 34 años es el que tiene más alcohol reportado (14,73 % de sus colisiones). La fuente solo marca el alcohol cuando se confirmó, así que una colisión sin alcohol reportado no significa que el conductor estuviera sobrio.

En 631.402 colisiones no se conoce la edad del culpable. El 87,6 % de ellas son colisiones con fuga, en las que no se pudo identificar al conductor, por lo que ese grupo no representa una edad en particular.

Para abordar estos hallazgos, las recomendaciones de organismos técnicos e internacionales se orientan hacia dos ejes principales:

1.    **Educación vial focalizada y esquemas de licenciamiento gradual para conductores de 16 a 34 años**, los grupos que causan más colisiones, en línea con las directrices de la National Highway Traffic Safety Administration (NHTSA) y la Organización Mundial de la Salud (OMS).
2.    **Controles de alcoholemia y campañas contra la conducción bajo los efectos del alcohol**, porque las colisiones con alcohol reportado son unas tres veces más graves que el resto, conforme a las recomendaciones de la NHTSA y la OMS.
    """)
with tab3:
    st.markdown("Condiciones Ambientales")
    st.markdown("""
Los resultados demuestran que las condiciones con mayor volumen absoluto de 
colisiones graves (como la luz diurna, el clima despejado y el pavimento seco) responden a la alta 
exposición cotidiana del parque vehicular. En el caso de la gravedad los que mayor destacan son:
Luz diurna con 71.524 colisiones graves, Despejado con 118.040 y Seca con 128.015.
En proporción, en cambio, la condición más peligrosa es la oscuridad sin alumbrado: el 6,28 % de sus
colisiones fueron graves, frente al 2,48 % con luz diurna. Eso no quiere decir que ahí ocurran la mayoría
de las colisiones graves, ya que es una proporción condicional: indica qué tan grave suele ser una
colisión en esa condición.

Para mitigar esta problemática, las recomendaciones de organismos 
internacionales y técnicos convergen en dos líneas de acción:

* **Gestión general del tránsito y velocidades en contextos de alta circulación**, alineada con las 
directrices de la Organización Mundial de la Salud (OMS) en su *Plan Mundial para el Decenio de Acción 
para la Seguridad Vial*.
* **Intervenciones focalizadas de infraestructura** (como el mantenimiento preventivo del alumbrado público 
respaldado por la Federal Highway Administration [FHWA] y los tratamientos de alta fricción en la vía 
recomendados por el Safe Transportation Research and Education Center [SafeTREC, UC Berkeley]) para reducir 
los picos de severidad en los entornos con mayor proporción de colisiones graves.
""")

with tab4:
    st.markdown("""Antigüedad del Vehículo y Lesiones""")
    st.markdown("""
Los resultados demuestran que la mayor frecuencia absoluta de víctimas involucradas en colisiones se concentra en los vehículos de menor antigüedad (especialmente entre 0 y 5 años, con un máximo en aquellos de 1 año). Posteriormente, aunque se registra un leve repunte en el volumen de afectados alrededor de los 9 y 10 años de antigüedad, el total de víctimas desciende de manera progresiva a medida que la edad del automóvil continúa aumentando. Sin embargo, al examinar la distribución interna de las lesiones según la escala KABCO (nivel de severidad), se observa que ni el pico inicial ni el repunte intermedio producen un aumento lineal en el volumen de desenlaces graves (K o A), predominando de forma constante las lesiones leves (C) y los ocupantes sin lesiones aparentes (O) en todos los tramos de antigüedad analizados. Para mitigar esto se hace recomendaciones claves:

1.    **Uso obligatorio y fiscalización de sistemas de retención**: Dado que el mayor volumen absoluto de víctimas ocurre en los vehículos más recientes (0 a 5 años) y que predominan las lesiones leves o sin daños aparentes, organismos como la Organización Mundial de la Salud (OMS) y los Centros para el Control y la Prevención de Enfermedades (CDC) destacan que el uso correcto del cinturón de seguridad y de los sistemas de retención infantil constituye el factor principal que contiene la escalada hacia lesiones graves (A) o fatales (K) durante una colisión.
2.    **Inspecciones técnicas periódicas (Mantenimiento del vehículo)**: Dado que los vehículos siguen registrando un volumen considerable de ocupantes incluso alrededor de los 9 a 12 años de antigüedad, organizaciones como la Administración Nacional de Seguridad del Tráfico en las Carreteras (NHTSA) y el Insurance Institute for Highway Safety (IIHS) enfatizan el control riguroso de los sistemas de seguridad activa y pasiva (frenos, neumáticos, suspensión y bolsas de aire) a lo largo de todo el ciclo de vida útil del automóvil, independientemente de su año de fabricación.

""")