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

Cada objetivo trabaja con una unidad de análisis distinta, según la pregunta que responde:
"""
)

st.markdown(
    """
<style>
.contenedor-tabla {
    font-family: "Times New Roman", Times, Georgia, serif;
    margin: 20px 0;
}
.titulo-tabla {
    font-weight: bold;
    font-size: 16px;
    margin-bottom: 8px;
    text-align: left;
}
table.tabla-apa {
    width: 100%;
    border-collapse: collapse;
    border-top: 2px solid currentColor;
    border-bottom: 2px solid currentColor;
    font-size: 15px;
}
table.tabla-apa th {
    border-bottom: 1px solid currentColor;
    text-align: left;
    font-weight: bold;
    padding: 8px 10px;
    vertical-align: top;
}
table.tabla-apa td {
    border: none;
    text-align: left;
    padding: 8px 10px;
    vertical-align: top;
    line-height: 1.35;
}
.fuente-tabla {
    font-style: italic;
    font-size: 14px;
    text-align: center;
    margin-top: 8px;
}
</style>

<div class="contenedor-tabla">
    <div class="titulo-tabla">Tabla 1. Unidades de análisis por objetivo específico</div>
    <table class="tabla-apa">
        <thead>
            <tr>
                <th>Objetivo</th>
                <th>Unidad de análisis</th>
                <th>Universo</th>
                <th>Casos</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1. Patrones temporales y por condado</td>
                <td>Colisión; condado y año para las tasas</td>
                <td>Todas las colisiones del período</td>
                <td>4.368.293 colisiones; 580 condado-año</td>
            </tr>
            <tr>
                <td>2. Edad del conductor culpable y alcohol</td>
                <td>Colisión con un conductor como culpable</td>
                <td>Colisiones cuyo culpable es un conductor</td>
                <td>3.926.268</td>
            </tr>
            <tr>
                <td>3. Iluminación, clima y calzada</td>
                <td>Colisión</td>
                <td>Todas las colisiones del período</td>
                <td>4.368.293</td>
            </tr>
            <tr>
                <td>4. Antigüedad del vehículo</td>
                <td>Víctima que viajaba en un vehículo</td>
                <td>Conductores y pasajeros con año del vehículo conocido</td>
                <td>3.980.022</td>
            </tr>
        </tbody>
    </table>
</div>
""",
    unsafe_allow_html=True,
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
La Tabla 2 muestra cómo se mide cada variable a partir de los campos de SWITRS. La
gravedad se mide con la escala KABCO, el estándar en Estados Unidos para clasificar la
lesión de cada persona: K (fallecido), A (lesión grave), B (lesión visible), C (posible lesión o
dolor) y O (sin lesiones). La gravedad de una colisión es la peor lesión entre sus víctimas.
    """
)

st.markdown(
    """
<div class="contenedor-tabla">
    <div class="titulo-tabla">Tabla 2. Operacionalización de las variables</div>
    <table class="tabla-apa">
        <thead>
            <tr>
                <th>Variable</th>
                <th>Definición operacional</th>
                <th>Indicador</th>
                <th>Escala</th>
                <th>Campo de SWITRS</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Gravedad de la colisión</td>
                <td>Peor lesión entre las víctimas</td>
                <td>Nivel KABCO: K, A, B, C u O</td>
                <td>Ordinal</td>
                <td>victim_degree_of_injury</td>
            </tr>
            <tr>
                <td>Colisión con fallecido</td>
                <td>Al menos una víctima en K</td>
                <td>Sí / No</td>
                <td>Nominal dicotómica</td>
                <td>derivada</td>
            </tr>
            <tr>
                <td>Colisión grave</td>
                <td>Al menos una víctima en K o A</td>
                <td>Sí / No</td>
                <td>Nominal dicotómica</td>
                <td>derivada</td>
            </tr>
            <tr>
                <td>Momento de la colisión</td>
                <td>Fecha y hora del parte</td>
                <td>Año, mes, día de la semana, hora</td>
                <td>Intervalo / nominal</td>
                <td>collision_date, collision_time</td>
            </tr>
            <tr>
                <td>Condado</td>
                <td>Condado donde ocurrió</td>
                <td>58 condados</td>
                <td>Nominal</td>
                <td>county_city_location</td>
            </tr>
            <tr>
                <td>Tasa por habitante</td>
                <td>Colisiones o fallecidos por población</td>
                <td>Casos por 100.000 habitantes</td>
                <td>Razón</td>
                <td>derivada + Census</td>
            </tr>
            <tr>
                <td>Edad del conductor culpable</td>
                <td>Edad de la parte culpable cuando es conductor</td>
                <td>Años, en 9 bandas</td>
                <td>Razón (bandas: ordinal)</td>
                <td>party_age, party_type, at_fault</td>
            </tr>
            <tr>
                <td>Alcohol del conductor culpable</td>
                <td>El culpable había bebido según el parte</td>
                <td>Bebió / sin alcohol reportado</td>
                <td>Nominal dicotómica</td>
                <td>party_sobriety</td>
            </tr>
            <tr>
                <td>Iluminación</td>
                <td>Condición de luz</td>
                <td>5 categorías</td>
                <td>Nominal</td>
                <td>lighting</td>
            </tr>
            <tr>
                <td>Clima</td>
                <td>Condición atmosférica</td>
                <td>7 categorías</td>
                <td>Nominal</td>
                <td>weather_1, weather_2</td>
            </tr>
            <tr>
                <td>Estado de la calzada</td>
                <td>Superficie de la vía</td>
                <td>4 categorías</td>
                <td>Nominal</td>
                <td>road_surface</td>
            </tr>
            <tr>
                <td>Antigüedad del vehículo</td>
                <td>Año de la colisión menos año del modelo</td>
                <td>Años</td>
                <td>Razón</td>
                <td>vehicle_year, collision_date</td>
            </tr>
            <tr>
                <td>Uso del cinturón</td>
                <td>Equipo de seguridad de la víctima</td>
                <td>Con / sin cinturón</td>
                <td>Nominal</td>
                <td>victim_safety_equipment_1/2</td>
            </tr>
        </tbody>
    </table>
</div>
""",
    unsafe_allow_html=True,
)

st.subheader("7. Procedimiento")
st.markdown(
    """
El trabajo con los datos se organizó en ocho fases. Cada fase es un programa en Python que
se puede volver a ejecutar y produce siempre el mismo resultado, de modo que todo el
proceso es reproducible. La Figura 1 resume el recorrido.
    """
)

st.markdown(
    """
<style>
.contenedor-figura {
    font-family: "Times New Roman", Times, Georgia, serif;
    margin: 25px 0;
}
.titulo-figura {
    font-weight: bold;
    font-size: 16px;
    margin-bottom: 14px;
    text-align: left;
}
.grid-diagrama {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr) auto minmax(0, 1fr);
    gap: 10px 12px;
    align-items: center;
    justify-items: center;
    max-width: 820px;
    margin: 0 auto;
}
.caja-diagrama {
    border: 1.5px solid currentColor;
    padding: 12px 10px;
    text-align: center;
    width: 100%;
    box-sizing: border-box;
    font-size: 14.5px;
    line-height: 1.35;
}
.flecha-diagrama {
    font-size: 20px;
    font-weight: bold;
    user-select: none;
}
</style>

<div class="contenedor-figura">
<div class="titulo-figura">Figura 1. Recorrido de los datos</div>
<div class="grid-diagrama">
<div class="caja-diagrama"><strong>Fuente</strong><br>SWITRS en SQLite<br>9,9 GB</div>
<div class="flecha-diagrama">&rarr;</div>
<div class="caja-diagrama"><strong>Data cruda</strong><br>Supabase Storage<br>Parquet, 506 MB</div>
<div class="flecha-diagrama">&rarr;</div>
<div class="caja-diagrama"><strong>colisiones_crudo</strong><br>MotherDuck<br>4 tablas</div>

<div></div>
<div></div>
<div></div>
<div></div>
<div class="flecha-diagrama">&darr;</div>

<div class="caja-diagrama"><strong>colisiones_analitica</strong><br>modelo en estrella<br>43 tablas</div>
<div class="flecha-diagrama">&larr;</div>
<div class="caja-diagrama"><strong>Vistas</strong><br>medidas calculadas<br>5 vistas</div>
<div class="flecha-diagrama">&larr;</div>
<div class="caja-diagrama"><strong>colisiones_normalizada</strong><br>tercera forma normal<br>52 tablas</div>
</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
***Fase 1. Obtención y revisión de la fuente***

Se descargó la base de SWITRS publicada en Kaggle y se revisaron su estructura y su
calidad: tipos de datos, valores faltantes, códigos sin documentar y coherencia entre tablas.
Esta revisión mostró los problemas que motivaron la normalización: columnas que repiten
información que se puede calcular desde otras tablas, columnas que dependen de otras y no
del caso, grupos repetidos (por ejemplo, weather_1 y weather_2) y códigos en inglés sin
catálogo.

***Fase 2. Resguardo de la data cruda en Supabase***

Para conservar la fuente intacta, las cuatro tablas originales, con todos los años de 2001 a
2021, se guardaron en Supabase Storage, un servicio de almacenamiento en la nube. Como
el plan gratuito acepta archivos de hasta 50 MB y 1 GB en total, los datos se exportaron al
formato Parquet, que es columnar y comprimido, en 167 archivos de 8 MB como máximo y
506 MB en total. El formato cambia, pero los datos no: antes de subirlos se comprobó, fila
por fila, que eran idénticos a los del archivo original.

***Fase 3. Carga de la data cruda en MotherDuck***

MotherDuck es un servicio en la nube basado en DuckDB, un motor de bases de datos
analíticas. Desde allí se leyeron los archivos de Supabase y se creó la base colisiones_crudo,
con las cuatro tablas originales como tablas SQL. Se volvió a comprobar que el contenido
fuera idéntico al de la fuente.

***Fase 4. Depuración y transformación***

Sobre la data cruda se aplicaron reglas de limpieza explícitas, sin eliminar registros:

• Se delimitó el período de estudio (2010-2019).

• Se asignó a cada campo su tipo correcto: el identificador del caso como número entero,
las fechas como fechas y las horas como horas. Una hora ilegible queda vacía y no se
reemplaza por 00:00.

• Se fijaron rangos válidos: edades entre 0 y 110 años, años de vehículo entre 1900 y
2020 y coordenadas dentro de los límites de California. Un valor fuera de rango se deja
vacío y se marca, pero la fila se conserva.

• Cada código en inglés se tradujo mediante un catálogo en español. Los valores vacíos o
desconocidos se agrupan en la categoría "Sin clasificar", de modo que ningún registro
se pierde al cruzar tablas.

• Se incorporó la población anual de cada condado desde el archivo del Census Bureau.

***Fase 5. Normalización***

En el modelo relacional propuesto por Codd (1970), la normalización organiza los datos
para que cada dato se guarde una sola vez y no pueda contradecirse con otra copia. Se
llevaron los datos hasta la tercera forma normal:

• Primera forma normal: cada celda guarda un solo valor. Los grupos repetidos de la
fuente, como las dos columnas de clima, se trasladaron a tablas puente con una fila por
valor.

• Segunda forma normal: cada dato depende de la llave completa de su tabla. Se
separaron tres tablas, una por nivel de detalle: colisión, parte y víctima.

• Tercera forma normal: ningún dato depende de otro que no sea la llave. Por ejemplo,
el condado depende del código de ubicación y no de la colisión, así que pasó a una
tabla de ubicaciones.

Además, no se guardó ninguna columna que pudiera recalcularse desde otras tablas, como el
número de fallecidos o la gravedad de la colisión. El resultado es la base
colisiones_normalizada, con 52 tablas: 10 con datos de los casos y 42 catálogos.
    """
)

st.markdown(
    """
<div class="contenedor-tabla">
<div class="titulo-tabla">Tabla 3. Tablas principales de la base normalizada</div>
<table class="tabla-apa">
<thead>
<tr>
<th style="width: 28%;">Tabla</th>
<th>Qué representa cada fila</th>
<th style="width: 24%;">Filas</th>
</tr>
</thead>
<tbody>
<tr>
<td>colision</td>
<td>Una colisión</td>
<td>4.368.293</td>
</tr>
<tr>
<td>parte</td>
<td>Una parte implicada (conductor, peatón, ciclista u otro)</td>
<td>8.688.142</td>
</tr>
<tr>
<td>victima</td>
<td>Una víctima</td>
<td>4.280.801</td>
</tr>
<tr>
<td>colision_geo · colision_carretera</td>
<td>Coordenadas y datos de carretera estatal, cuando existen</td>
<td>2.159.739 · 904.581</td>
</tr>
<tr>
<td>5 tablas puente</td>
<td>Clima, condición de la vía, equipo de seguridad y factores, una fila por valor</td>
<td>entre 4,4 y 14,2 millones</td>
</tr>
<tr>
<td>42 catálogos</td>
<td>Las categorías de cada variable, en español</td>
<td>de 4 a 5.194</td>
</tr>
</tbody>
</table>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
***Fase 6. Desnormalización***

Una base normalizada evita la redundancia, pero para analizar exige unir muchas tablas en
cada consulta. Por eso se construyó una segunda capa pensada para el análisis. Primero,
cinco vistas que calculan las medidas a partir de las tablas: fallecidos y heridos por colisión,
gravedad, presencia de alcohol, edad del conductor culpable, antigüedad del vehículo y tasas
por condado y año. Luego, esas vistas se guardaron en la base colisiones_analitica como un
modelo en estrella: tablas de hechos con las medidas y tablas de dimensiones con las
categorías (Kimball y Ross, 2013). Este enfoque, en el que los datos se guardan
normalizados y se sirven en estrella para el análisis, sigue la propuesta de Inmon (2005).

***Fase 7. Validación***

Se verificó que ningún paso alterara o perdiera datos:

• Se comparó cada etapa con la anterior mediante una huella digital: un código calculado
a partir de cada fila completa. Si un solo valor cambiara, la huella sería distinta. El
archivo original, los Parquet, la base cruda en MotherDuck y la base normalizada en la
nube y en el equipo local resultaron idénticos.

• Cada medida recalculada en las vistas se comparó con la columna original de la fuente.
Coinciden en las 4.368.293 colisiones salvo una, que se documentó como error de
captura.

• Se comprobó que ningún identificador se repite y que toda parte y víctima corresponde
a una colisión existente.

***Fase 8. Análisis y presentación de resultados***
Las cifras del informe se calculan con un programa que lee la base y las guarda en un
archivo, de modo que ningún número se escribe a mano...
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

***Las fórmulas principales son:***

*Proporción de colisiones con fallecido = colisiones del grupo con al menos una víctima K /
colisiones del grupo*

*Tasa = fallecidos del condado en el año / habitantes del condado en ese año × 100.000
Cociente de proporciones = proporción en el grupo / proporción en el grupo de referencia*
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
<div class="contenedor-tabla">
<div class="titulo-figura">Tabla 4. Herramientas utilizadas</div>
<table class="tabla-apa">
<thead>
<tr>
<th style="width: 28%;">Herramienta</th>
<th>Uso en el trabajo</th>
</tr>
</thead>
<tbody>
<tr>
<td>Python</td>
<td>Programas de cada fase del procesamiento y cálculo de las cifras.</td>
</tr>
<tr>
<td>SQL y DuckDB</td>
<td>Lenguaje y motor de base de datos para la limpieza, la normalización y las consultas.</td>
</tr>
<tr>
<td>Parquet</td>
<td>Formato de archivo columnar y comprimido para la data cruda y la base exportada.</td>
</tr>
<tr>
<td>Supabase Storage</td>
<td>Almacenamiento en la nube de la data cruda.</td>
</tr>
<tr>
<td>MotherDuck</td>
<td>Base de datos en la nube donde se ejecutan la normalización y la desnormalización.</td>
</tr>
<tr>
<td>Streamlit y Plotly</td>
<td>Aplicación web y gráficos interactivos para la presentación de los resultados.</td>
</tr>
<tr>
<td>Power BI</td>
<td>Tablero ejecutivo para la visualización de indicadores clave.</td>
</tr>
<tr>
<td>GitHub</td>
<td>Control de versiones y repositorio del proyecto.</td>
</tr>
</tbody>
</table>
</div>
""",
    unsafe_allow_html=True,
)
