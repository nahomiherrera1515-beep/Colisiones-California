# Siniestralidad vial en California, 2010-2019

Trabajo final de Computación II, Escuela de Estadística y Ciencias Actuariales de la Universidad Central de Venezuela.

Estudiamos los choques de tránsito registrados en California entre 2010 y 2019 a partir de SWITRS, el sistema en el que la California Highway Patrol reúne los partes policiales de todo el estado.

## Planteamiento del problema

Los siniestros viales son un problema de salud pública. La Organización Mundial de la Salud los señala como la principal causa de muerte entre los 5 y los 29 años en el mundo.

California registra cada choque de su territorio en un mismo sistema, lo que permite estudiar el fenómeno completo y no una muestra. Tomamos los diez años de 2010 a 2019 porque es un período continuo y anterior a los cambios de movilidad de la pandemia.

Contar choques no alcanza para entender la siniestralidad. Un mismo número puede esconder condados con tasas muy distintas, horas tranquilas y horas peligrosas, o condiciones que producen pocos choques pero de los más graves. Por eso nos interesa tanto cuántos choques ocurren como qué tan graves son.

## Pregunta de investigación

> ¿Cómo se distribuyó la siniestralidad vial en California entre 2010 y 2019 en el tiempo y entre los condados, y qué características del conductor, de las condiciones ambientales y del vehículo se asocian con la gravedad de los choques?

## Objetivos específicos

1. Describir los patrones temporales (año, mes, día y hora) y geográficos por condado, con conteos y tasas por 100.000 habitantes.
2. Comparar cómo se asocian la edad del conductor culpable y el alcohol con la gravedad del choque, y cuál de los dos pesa más.
3. Describir la distribución de choques según iluminación, clima y estado de la calzada, y la proporción de choques graves en cada condición.
4. Examinar la relación entre la antigüedad del vehículo y la gravedad de las lesiones de sus ocupantes.

## Fuente de datos

Usamos la base `switrs.sqlite` publicada en Kaggle por Alex Gude, que reúne los registros de SWITRS en tres tablas: colisiones, partes implicadas y víctimas.

https://www.kaggle.com/datasets/alexgude/california-traffic-collision-data-from-switrs

El archivo pesa cerca de 10 GB y no se sube al repositorio. Para trabajar con él hay que descargarlo y ponerlo en `data/raw/`.

## Preparar el entorno

```bash
pip install -r requirements.txt
```

## Equipo

Nahomi Herrera, Allan Arcia, Estefani Carreño, Eddie Palomino y Alejandro Huérfano.
