"""Marco Teórico"""

import streamlit as st

# configuracion inicial de la pagina del marco teorico
st.set_page_config(page_title="Marco Teórico", page_icon="📚", layout="wide")

# marco teorico en grande para que resalte en la pagina
st.title("Marco Teórico")

# comienzo del marco teorico
st.markdown(
    """
   El marco teórico la presente investigación 
   tiene como objetivo mostrar los fundamentos teóricos del análisis 
   de colisiones en California (2010-2019). En él se incluyen aspectos 
   relacionados con la revisión de la literatura científica sobre los 
   factores de riesgo, también se hace referencia al contraste bivariado.
    """
)

st.header("1. Factores Determinantes de la Severidad en las Colisiones Viales")
st.markdown(
    """
    La severidad de una colisión vial está determinada por varios factores. 
    Algunos de ellos son:
    
    * **Factor humano (Edad del conductor):** Es un factor que mide la experiencia de los conductores y 
    su vulnerabilidad a la energía cinética. Por un lado, en los conductores jóvenes 
    la literatura científica destaca la inexperiencia al volante, 
    la propensión a la búsqueda de sensaciones y un desarrollo neurocognitivo 
    en proceso que afecta al control de impulsos (**Hanrahan et al, 2009**). Por otro lado, en los 
    conductores mayores se asocia con un declive gradual en los tiempos de 
    reacción y la agudeza visual, el cual suele ser compensado por un grado 
    mayor de experiencia y autorregulación conductual (**Lansdown et al, 2015**).

    * **Factor ambiental (Iluminación y meteorología):** Las condiciones del entorno actúan como 
    moduladores externos en la capacidad de reacción de los conductores y en el control del vehículo en 
    la via. Por un lado, la iluminación y la visibilidad (que comprenden desde la luz diurna hasta la 
    disponibilidad de alumbrado artificial en horarios nocturnos) condicionan de manera directa el tiempo 
    de reacción del conductor ante imprevistos (**Jafari Anarkooli & Hosseinlou, 2016**). Por otra parte 
    están los factores meteorológicos y la adherencia de la calzada, como la presencia de lluvia, humedad 
    o superficies resbaladizas, reducen la tracción entre el neumático y el pavimento, lo que incrementa 
    el riesgo de una colisión (**Wang & Zhang, 2017**).

    * **Factor vehicular:** El año-modelo funciona como un indicador de la antigüedad de la flota de 
    vehículos, además de indicar aspectos relacionados con las agregaciones 
    de elementos de seguridad en los vehículos (**NHTSA, 2013**). 
    Es importante diferenciar la frecuencia (número de unidades accidentadas) de la tasa de riesgo 
    (número de vehículos activos en circulación o millas recorridas)
    """
    )

st.markdown("---")

st.header("2. Definiciones Estadísticas Generales")

# definicion de tasa
st.subheader("Tasa")
st.markdown(
    """
Medida de frecuencia que expresa la relación entre el número de eventos registrados 
en una población durante un período determinado y la población total expuesta al riesgo, 
multiplicada por una constante de amplificación $k$ (por ejemplo, $10^5$) para facilitar 
su lectura y comparación (**Organización Panamericana de la Salud [OPS], 2018; Siegel & Swanson, 2004**). 
Esta medida estandariza la ocurrencia del fenómeno respecto al volumen demográfico.
"""
)

#formula
st.latex(r"T = \left(\frac{N}{P}\right) \times k")

st.markdown(
    """
**Donde:**
* **$T$**: Tasa del evento.
* **$N$**: Número total de eventos o casos registrados.
* **$P$**: Población total o población expuesta al riesgo.
* **$k$**: Constante de amplificación (ej. $10^3, 10^5$).
"""
)


# proporcion condicional
st.subheader("Proporción Condicional")
st.markdown(
    """
Medida que expresa el peso relativo o frecuencia de un desenlace específico dentro 
del total de eventos ocurridos en una categoría, estrato o subgrupo determinado 
(**Agresti & Franklin, 2013; Organización Panamericana de la Salud [OPS], 2018**). 
A diferencia de las tasas, su denominador corresponde al total de casos del subgrupo 
y no a la población total, lo que permite aislar la distribución interna del fenómeno 
(**Porta, 2014**). Para valores agregados, se calcula mediante el cociente de los 
totales acumulados del estrato, evitando promedios aritméticos simples que sesgarían 
el parámetro real (**Triola, 2018**).
"""
)

#formula
st.latex(r"p_{j|i} = \frac{n_{ij}}{n_{i\cdot}}")

st.markdown(
    """
**Donde:**
* **$p_{j|i}$**: Proporción del desenlace $j$ condicionado a la categoría o estrato $i$.
* **$n_{ij}$**: Número de casos en la categoría $i$ que presentan el desenlace $j$.
* **$n_{i\cdot}$**: Total de casos registrados en la categoría de exposición $i$ (denominador del grupo).
"""
)

# cociente de proporciones
st.subheader("Cociente de Proporciones")
st.markdown(
    """
Medida de razón relativa que cuantifica cuántas veces es más frecuente un evento 
o desenlace en un grupo, categoría o condición de interés en comparación con un 
grupo o categoría de referencia (**Agresti & Franklin, 2013; Porta, 2014**). 
Permite evaluar de forma puramente descriptiva la magnitud de las asociaciones 
relativas entre diferentes estratos.
"""
)

#formula
st.latex(r"CP = \frac{p_1}{p_2}")

st.markdown(
    """
**Donde:**
* **$CP$**: Cociente de proporciones.
* **$p_1$**: Proporción del desenlace en el grupo de interés o expuesto.
* **$p_2$**: Proporción del desenlace en el grupo de referencia.
"""
)

