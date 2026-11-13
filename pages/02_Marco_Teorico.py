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

