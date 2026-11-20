"""Cuestionario SQL (formulario G8) sobre las colisiones de tránsito en California.

Para cada una de las preguntas 1 a 5 la app muestra el enunciado, la consulta
SQL (escrita para SQLite), la explicación, el resultado y un gráfico.

Los resultados ya vienen guardados dentro de este archivo: se obtuvieron
ejecutando estas mismas consultas sobre la fuente cruda switrs.sqlite (Kaggle,
9,9 GB). Por eso la app funciona completa sin descargar nada. Si además se
tiene switrs.sqlite, la app puede volver a ejecutar cada consulta en vivo.

Cómo usarla:
    pip install streamlit pandas altair
    streamlit run app_cuestionario.py

La ruta de switrs.sqlite (opcional) se toma de la variable SWITRS_PATH, o de un
switrs.sqlite en la misma carpeta que este archivo, y se puede cambiar desde la
barra lateral.
"""

import os
import sqlite3
import time
from pathlib import Path

import pandas as pd
import altair as alt
import streamlit as st
import plotly.express as px

# configuracion inicial de la pagina de las consultas SQL
st.set_page_config(page_title="Cuestionario de Consultas SQL", page_icon="💻", layout="wide")

# titulo
st.title("Cuestionario de Consultas SQL")


# Conexión con la fuente
# ---------------------------------------------------------------------------

RUTA_POR_DEFECTO = os.environ.get("SWITRS_PATH",
                                  str(Path(__file__).with_name("switrs.sqlite")))


def conectar(ruta):
    # mode=ro abre el archivo en solo lectura: las consultas no pueden modificarlo.
    return sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)


@st.cache_data(show_spinner=False)
def consultar(ruta, sql):
    """Ejecuta una consulta y guarda el resultado en caché para no repetirla."""
    with conectar(ruta) as con:
        return pd.read_sql_query(sql, con)


@st.cache_data(show_spinner=False)
def filas_por_tabla(ruta):
    with conectar(ruta) as con:
        return pd.DataFrame(
            [(tabla, con.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0])
             for tabla in ("collisions", "parties")],
            columns=["tabla", "filas"])



# Consultas
# ---------------------------------------------------------------------------

SQL_1 = """\
-- Pregunta 1: Perfil de la semana
-- strftime('%w') da 0 el domingo; (w + 6) % 7 + 1 lo pasa a 1 lunes ... 7 domingo.
WITH por_dia AS (
    SELECT (CAST(strftime('%w', collision_date) AS INTEGER) + 6) % 7 + 1 AS dia,
           COUNT(*)                         AS colisiones,
           COALESCE(SUM(killed_victims), 0) AS muertos
    FROM collisions
    WHERE collision_date >= '2001-01-01' AND collision_date < '2021-01-01'
    GROUP BY 1
),
nombres (dia, nombre) AS (
    VALUES (1, 'Lunes'), (2, 'Martes'), (3, 'Miércoles'), (4, 'Jueves'),
           (5, 'Viernes'), (6, 'Sábado'), (7, 'Domingo')
)
SELECT n.nombre                                                        AS dia_semana,
       d.colisiones                                                    AS colisiones,
       ROUND(100.0 * d.colisiones / SUM(d.colisiones) OVER (), 2)      AS pct_colisiones,
       ROUND(100.0 * (d.colisiones - a.colisiones) / a.colisiones, 2)  AS variacion_pct_dia_anterior,
       d.muertos                                                       AS muertos,
       ROUND(1000.0 * d.muertos / d.colisiones, 2)                     AS letalidad_por_mil,
       RANK() OVER (ORDER BY 1.0 * d.muertos / d.colisiones DESC)      AS puesto_letalidad,
       ROUND(d.colisiones / (SELECT AVG(colisiones) FROM por_dia), 3)  AS cociente_media_semanal
FROM por_dia d
JOIN por_dia a ON a.dia = CASE WHEN d.dia = 1 THEN 7 ELSE d.dia - 1 END
JOIN nombres n ON n.dia = d.dia
ORDER BY d.dia;
"""

SQL_2 = """\
-- Pregunta 2: Culpabilidad por edad y sexo
WITH por_grupo_sexo AS (
    SELECT CASE WHEN party_age <= 24 THEN 1
                WHEN party_age <= 44 THEN 2
                WHEN party_age <= 64 THEN 3
                ELSE 4 END AS grupo,
           party_sex       AS sexo,
           COUNT(*)        AS conductores,
           SUM(at_fault)   AS culpables
    FROM parties
    WHERE party_type = 'driver'
      AND party_sex IN ('male', 'female')
      AND party_age BETWEEN 16 AND 100
    GROUP BY 1, 2
)
SELECT CASE h.grupo WHEN 1 THEN '16 a 24' WHEN 2 THEN '25 a 44'
                    WHEN 3 THEN '45 a 64' ELSE '65 o más' END              AS grupo_edad,
       h.conductores                                                       AS hombres,
       m.conductores                                                       AS mujeres,
       ROUND(100.0 * h.culpables / h.conductores, 2)                       AS pct_culpables_hombres,
       ROUND(100.0 * m.culpables / m.conductores, 2)                       AS pct_culpables_mujeres,
       ROUND(100.0 * h.culpables / h.conductores
             - 100.0 * m.culpables / m.conductores, 2)                     AS diferencia_puntos,
       ROUND(100.0 * (h.culpables + m.culpables) / (h.conductores + m.conductores)
             - (SELECT 100.0 * SUM(culpables) / SUM(conductores) FROM por_grupo_sexo), 2)
                                                                           AS diferencia_con_total_puntos,
       RANK() OVER (ORDER BY 1.0 * (h.culpables + m.culpables)
                             / (h.conductores + m.conductores) DESC)      AS puesto_culpabilidad
FROM por_grupo_sexo h
JOIN por_grupo_sexo m ON m.grupo = h.grupo AND m.sexo = 'female'
WHERE h.sexo = 'male'
ORDER BY h.grupo;
"""

SQL_3 = """\
-- Pregunta 3: Peso de las motocicletas en la mortalidad
WITH por_anio AS (
    SELECT CAST(substr(collision_date, 1, 4) AS INTEGER) AS anio,
           motorcycle_collision                          AS moto,
           COUNT(*)                                      AS colisiones,
           COALESCE(SUM(killed_victims), 0)              AS muertos
    FROM collisions
    WHERE collision_date >= '2001-01-01' AND collision_date < '2021-01-01'
    GROUP BY 1, 2
)
SELECT m.anio                                                              AS anio,
       m.colisiones                                                        AS colisiones_con_moto,
       ROUND(100.0 * m.colisiones / (m.colisiones + r.colisiones), 2)      AS pct_colisiones_con_moto,
       ROUND(100.0 * m.muertos / (m.muertos + r.muertos), 2)               AS pct_muertos_con_moto,
       ROUND(1000.0 * m.muertos / m.colisiones, 2)                         AS letalidad_con_moto,
       ROUND(1000.0 * r.muertos / r.colisiones, 2)                         AS letalidad_resto,
       ROUND((1.0 * m.muertos / m.colisiones) / (1.0 * r.muertos / r.colisiones), 2)
                                                                           AS cociente_letalidades,
       RANK() OVER (ORDER BY 1.0 * m.muertos / (m.muertos + r.muertos) DESC)
                                                                           AS puesto_pct_muertos,
       ROUND(100.0 * m.muertos / (m.muertos + r.muertos)
             - (SELECT 100.0 * SUM(CASE WHEN moto = 1 THEN muertos ELSE 0 END) / SUM(muertos)
                FROM por_anio), 2)                                         AS diferencia_con_periodo_puntos
FROM por_anio m
JOIN por_anio r ON r.anio = m.anio AND r.moto = 0
WHERE m.moto = 1
ORDER BY m.anio;
"""

SQL_4 = """\
-- Pregunta 4: Mayores caídas interanuales por mes
WITH serie AS (
    SELECT CAST(substr(collision_date, 1, 4) AS INTEGER) AS anio,
           CAST(substr(collision_date, 6, 2) AS INTEGER) AS mes,
           COUNT(*)                                      AS colisiones,
           COALESCE(SUM(killed_victims), 0)              AS muertos
    FROM collisions
    WHERE collision_date >= '2001-01-01' AND collision_date < '2021-01-01'
    GROUP BY 1, 2
),
comparacion AS (
    SELECT s.anio, s.mes,
           s.colisiones, s.muertos,
           p.colisiones AS colisiones_previas,
           p.muertos    AS muertos_previos,
           100.0 * (s.colisiones - p.colisiones) / p.colisiones          AS var_colisiones,
           100.0 * (s.muertos - p.muertos) / NULLIF(p.muertos, 0)        AS var_muertos
    FROM serie s
    JOIN serie p ON p.mes = s.mes AND p.anio = s.anio - 1
)
SELECT puesto                                                  AS puesto,
       anio                                                    AS anio,
       mes                                                     AS mes,
       colisiones                                              AS colisiones,
       muertos                                                 AS muertos,
       colisiones_previas                                      AS colisiones_anio_anterior,
       muertos_previos                                         AS muertos_anio_anterior,
       ROUND(var_colisiones, 2)                                AS variacion_pct_colisiones,
       ROUND(var_muertos, 2)                                   AS variacion_pct_muertos,
       ROUND(1000.0 * muertos / colisiones, 2)                 AS letalidad_por_mil,
       ROUND(1000.0 * muertos_previos / colisiones_previas, 2) AS letalidad_anio_anterior,
       meses_con_caida                                         AS meses_con_caida,
       meses_comparados                                        AS meses_comparados
FROM (
    SELECT c.*,
           RANK() OVER (ORDER BY var_colisiones)                                  AS puesto,
           SUM(CASE WHEN colisiones < colisiones_previas THEN 1 ELSE 0 END) OVER () AS meses_con_caida,
           COUNT(*) OVER ()                                                       AS meses_comparados
    FROM comparacion c
) ranking
WHERE puesto <= 10
ORDER BY puesto;
"""

SQL_5 = """\
-- Pregunta 5: Rachas de años con más muertos
WITH serie AS (
    SELECT county_location                               AS condado,
           CAST(substr(collision_date, 1, 4) AS INTEGER) AS anio,
           COALESCE(SUM(killed_victims), 0)              AS muertos
    FROM collisions
    WHERE collision_date >= '2001-01-01' AND collision_date < '2021-01-01'
    GROUP BY 1, 2
),
condados_validos AS (
    SELECT condado
    FROM serie
    GROUP BY condado
    HAVING COUNT(*) = 20
       AND SUM(muertos) >= (SELECT AVG(total)
                            FROM (SELECT SUM(muertos) AS total FROM serie GROUP BY condado) t)
),
aumentos AS (
    -- Años cuyo total supera al del año anterior en el mismo condado.
    SELECT s.condado, s.anio, s.muertos, p.muertos AS muertos_previos
    FROM serie s
    JOIN serie p ON p.condado = s.condado AND p.anio = s.anio - 1
    WHERE s.muertos > p.muertos
      AND s.condado IN (SELECT condado FROM condados_validos)
),
islas AS (
    -- En años consecutivos, anio menos su número de fila es constante.
    SELECT a.*, anio - ROW_NUMBER() OVER (PARTITION BY condado ORDER BY anio) AS isla
    FROM aumentos a
),
rachas AS (
    SELECT condado, MIN(anio) AS inicio, MAX(anio) AS fin, COUNT(*) AS anios
    FROM islas
    GROUP BY condado, isla
),
mejor_racha AS (
    SELECT r.*,
           ROW_NUMBER() OVER (PARTITION BY condado ORDER BY anios DESC, inicio) AS orden
    FROM rachas r
)
SELECT RANK() OVER (ORDER BY r.anios DESC)                           AS puesto,
       r.condado                                                     AS condado,
       r.inicio                                                      AS primer_anio_aumento,
       r.fin                                                         AS ultimo_anio_aumento,
       r.anios                                                       AS anios_de_racha,
       i.muertos_previos                                             AS muertos_anio_previo,
       f.muertos                                                     AS muertos_ultimo_anio,
       ROUND(100.0 * (f.muertos - i.muertos_previos)
             / NULLIF(i.muertos_previos, 0), 2)                      AS aumento_pct
FROM mejor_racha r
JOIN aumentos i ON i.condado = r.condado AND i.anio = r.inicio
JOIN aumentos f ON f.condado = r.condado AND f.anio = r.fin
WHERE r.orden = 1
ORDER BY puesto, condado;
"""

# ---------------------------------------------------------------------------
# Resultados guardados
# ---------------------------------------------------------------------------
# Se obtuvieron ejecutando SQL_1 a SQL_5 sobre el switrs.sqlite completo de Kaggle
# (9,9 GB) con SQLite. Así la app muestra todo sin necesidad del archivo.

RESULTADOS_GUARDADOS = {
    1: {
        "columnas": ["dia_semana", "colisiones", "pct_colisiones", "variacion_pct_dia_anterior", "muertos", "letalidad_por_mil", "puesto_letalidad", "cociente_media_semanal"],
        "filas": [
            ('Lunes', 1301907, 14.01, 19.94, 9049, 6.95, 4, 0.981),
            ('Martes', 1357711, 14.61, 4.29, 8785, 6.47, 6, 1.023),
            ('Miércoles', 1363393, 14.67, 0.42, 8578, 6.29, 7, 1.027),
            ('Jueves', 1373527, 14.78, 0.74, 9158, 6.67, 5, 1.035),
            ('Viernes', 1533604, 16.51, 11.65, 11153, 7.27, 3, 1.155),
            ('Sábado', 1275999, 13.73, -16.8, 13070, 10.24, 2, 0.961),
            ('Domingo', 1085423, 11.68, -14.94, 12535, 11.55, 1, 0.818),
        ],
    },
    2: {
        "columnas": ["grupo_edad", "hombres", "mujeres", "pct_culpables_hombres", "pct_culpables_mujeres", "diferencia_puntos", "diferencia_con_total_puntos", "puesto_culpabilidad"],
        "filas": [
            ('16 a 24', 2101883, 1453111, 62.77, 53.82, 8.94, 12.62, 1),
            ('25 a 44', 3883074, 2557802, 46.51, 39.5, 7.01, -2.76, 3),
            ('45 a 64', 2491615, 1519660, 40.35, 36.53, 3.82, -7.58, 4),
            ('65 o más', 681061, 432126, 48.75, 50.58, -1.83, 2.98, 2),
        ],
    },
    3: {
        "columnas": ["anio", "colisiones_con_moto", "pct_colisiones_con_moto", "pct_muertos_con_moto", "letalidad_con_moto", "letalidad_resto", "cociente_letalidades", "puesto_pct_muertos", "diferencia_con_periodo_puntos"],
        "filas": [
            (2001, 9875, 1.89, 7.67, 30.48, 7.07, 4.31, 20, -4.97),
            (2002, 10783, 1.98, 7.97, 30.23, 7.05, 4.29, 19, -4.66),
            (2003, 11749, 2.18, 8.97, 32.26, 7.3, 4.42, 17, -3.67),
            (2004, 11370, 2.11, 8.87, 31.93, 7.08, 4.51, 18, -3.77),
            (2005, 11495, 2.16, 9.74, 36.45, 7.45, 4.89, 16, -2.9),
            (2006, 11707, 2.35, 10.29, 35.19, 7.37, 4.78, 15, -2.34),
            (2007, 13656, 2.72, 11.95, 34.71, 7.15, 4.85, 14, -0.69),
            (2008, 14503, 3.2, 16.26, 38.13, 6.5, 5.87, 2, 3.62),
            (2009, 12749, 2.99, 12.87, 31.06, 6.48, 4.79, 13, 0.24),
            (2010, 12085, 2.9, 13.18, 29.87, 5.88, 5.08, 12, 0.54),
            (2011, 13263, 3.29, 15.27, 32.65, 6.15, 5.31, 5, 2.64),
            (2012, 13848, 3.5, 15.59, 33.72, 6.62, 5.1, 3, 2.96),
            (2013, 14431, 3.76, 15.3, 32.92, 7.12, 4.63, 4, 2.67),
            (2014, 15061, 3.77, 16.95, 35.19, 6.75, 5.21, 1, 4.32),
            (2015, 16711, 3.81, 15.01, 30.88, 6.93, 4.46, 7, 2.38),
            (2016, 17711, 3.6, 15.26, 33.26, 6.9, 4.82, 6, 2.62),
            (2017, 17422, 3.58, 14.81, 33.18, 7.09, 4.68, 8, 2.17),
            (2018, 17316, 3.59, 13.98, 30.72, 7.04, 4.36, 10, 1.34),
            (2019, 15870, 3.37, 13.38, 31.51, 7.12, 4.42, 11, 0.75),
            (2020, 12956, 3.54, 14.47, 41.37, 8.96, 4.62, 9, 1.84),
        ],
    },
    4: {
        "columnas": ["puesto", "anio", "mes", "colisiones", "muertos", "colisiones_anio_anterior", "muertos_anio_anterior", "variacion_pct_colisiones", "variacion_pct_muertos", "letalidad_por_mil", "letalidad_anio_anterior", "meses_con_caida", "meses_comparados"],
        "filas": [
            (1, 2020, 4, 19985, 224, 37045, 265, -46.05, -15.47, 11.21, 7.15, 149, 228),
            (2, 2006, 8, 28346, 296, 45321, 426, -37.46, -30.52, 10.44, 9.4, 149, 228),
            (3, 2020, 5, 25098, 306, 39047, 307, -35.72, -0.33, 12.19, 7.86, 149, 228),
            (4, 2020, 6, 27456, 288, 37364, 331, -26.52, -12.99, 10.49, 8.86, 149, 228),
            (5, 2020, 3, 29478, 248, 39971, 270, -26.25, -8.15, 8.41, 6.75, 149, 228),
            (6, 2020, 8, 32164, 343, 41142, 338, -21.82, 1.48, 10.66, 8.22, 149, 228),
            (7, 2020, 12, 31205, 309, 39519, 318, -21.04, -2.83, 9.9, 8.05, 149, 228),
            (8, 2020, 7, 30200, 334, 37953, 311, -20.43, 7.4, 11.06, 8.19, 149, 228),
            (9, 2020, 11, 32455, 355, 40550, 362, -19.96, -1.93, 10.94, 8.93, 149, 228),
            (10, 2020, 9, 32124, 347, 40004, 331, -19.7, 4.83, 10.8, 8.27, 149, 228),
        ],
    },
    5: {
        "columnas": ["puesto", "condado", "primer_anio_aumento", "ultimo_anio_aumento", "anios_de_racha", "muertos_anio_previo", "muertos_ultimo_anio", "aumento_pct"],
        "filas": [
            (1, 'riverside', 2012, 2018, 7, 203, 318, 56.65),
            (2, 'los angeles', 2012, 2016, 5, 542, 847, 56.27),
            (3, 'san bernardino', 2011, 2014, 4, 221, 281, 27.15),
            (3, 'tulare', 2014, 2017, 4, 54, 86, 59.26),
            (5, 'kern', 2015, 2017, 3, 111, 187, 68.47),
            (5, 'orange', 2011, 2013, 3, 106, 185, 74.53),
            (5, 'sacramento', 2015, 2017, 3, 112, 171, 52.68),
            (5, 'santa clara', 2013, 2015, 3, 87, 135, 55.17),
            (9, 'alameda', 2002, 2003, 2, 111, 113, 1.8),
            (9, 'contra costa', 2002, 2003, 2, 57, 71, 24.56),
            (9, 'fresno', 2002, 2003, 2, 149, 209, 40.27),
            (9, 'san diego', 2004, 2005, 2, 290, 308, 6.21),
            (9, 'san joaquin', 2010, 2011, 2, 64, 83, 29.69),
            (9, 'stanislaus', 2002, 2003, 2, 85, 90, 5.88),
            (9, 'ventura', 2005, 2006, 2, 70, 82, 17.14),
        ],
    },
}

# ---------------------------------------------------------------------------
# Gráficos (uno por pregunta)
# ---------------------------------------------------------------------------

def grafico_1(df):
    return alt.Chart(df).mark_bar().encode(
        x=alt.X("dia_semana:N", sort=list(df.dia_semana), title=None),
        y=alt.Y("letalidad_por_mil:Q", title="Muertos por cada 1.000 colisiones"),
        tooltip=["dia_semana", "colisiones", "muertos", "letalidad_por_mil"])


def grafico_2(df):
    largo = df.melt(id_vars="grupo_edad",
                    value_vars=["pct_culpables_hombres", "pct_culpables_mujeres"],
                    var_name="sexo", value_name="pct_culpables")
    largo["sexo"] = largo.sexo.map({"pct_culpables_hombres": "Hombres",
                                    "pct_culpables_mujeres": "Mujeres"})
    return alt.Chart(largo).mark_bar().encode(
        x=alt.X("grupo_edad:N", title="Grupo de edad"),
        xOffset="sexo:N",
        y=alt.Y("pct_culpables:Q", title="% declarado culpable"),
        color=alt.Color("sexo:N", title=None),
        tooltip=["grupo_edad", "sexo", "pct_culpables"])


def grafico_3(df):
    largo = df.melt(id_vars="anio",
                    value_vars=["pct_colisiones_con_moto", "pct_muertos_con_moto"],
                    var_name="medida", value_name="porcentaje")
    largo["medida"] = largo.medida.map({"pct_colisiones_con_moto": "% de las colisiones",
                                        "pct_muertos_con_moto": "% de los muertos"})
    return alt.Chart(largo).mark_line(point=True).encode(
        x=alt.X("anio:O", title="Año"),
        y=alt.Y("porcentaje:Q", title="Porcentaje con motocicleta"),
        color=alt.Color("medida:N", title=None),
        tooltip=["anio", "medida", "porcentaje"])


def grafico_4(df):
    df = df.assign(periodo=df.anio.astype(str) + "-" + df.mes.astype(str).str.zfill(2))
    return alt.Chart(df).mark_bar().encode(
        x=alt.X("variacion_pct_colisiones:Q", title="Variación % de colisiones frente al año anterior"),
        y=alt.Y("periodo:N", sort=list(df.periodo), title=None),
        tooltip=["periodo", "colisiones", "colisiones_anio_anterior", "variacion_pct_colisiones"])


def grafico_5(df):
    return alt.Chart(df).mark_bar().encode(
        x=alt.X("anios_de_racha:Q", title="Años seguidos con más muertos que el anterior"),
        y=alt.Y("condado:N", sort=list(df.condado), title=None),
        tooltip=["condado", "primer_anio_aumento", "ultimo_anio_aumento", "anios_de_racha",
                 "aumento_pct"])

PREGUNTAS = {
    1: {
        "titulo": "Perfil de la semana",
        "sql": SQL_1,
        "grafico": grafico_1,
        "enunciado": "¿Cuántas colisiones y cuántos muertos hubo cada día de la semana entre "
                     "2001 y 2020, cómo cambia cada día frente al anterior y qué día es el más "
                     "letal? La letalidad se mide como muertos por cada 1.000 colisiones.",
        "tecnicas": "CTE `por_dia` y `nombres`; self join de `por_dia` con el día anterior; "
                    "ventanas `SUM() OVER ()` y `RANK()`; subconsulta con la media de los "
                    "siete días.",
        "explicacion": """
1. El CTE `por_dia` recorre la tabla `collisions` una sola vez y agrupa por día de la
   semana. En SQLite, `strftime('%w', fecha)` devuelve 0 para el domingo y 6 para el
   sábado; la fórmula `(w + 6) % 7 + 1` lo pasa a 1 = lunes, ..., 7 = domingo.
2. Por cada día cuenta las colisiones con `COUNT(*)` y suma los muertos con
   `SUM(killed_victims)`. `SUM` ignora los nulos y `COALESCE` deja un 0 si un grupo no
   tuviera ningún dato.
3. El CTE `nombres` es una pequeña tabla escrita con `VALUES` que traduce el número del
   día a su nombre.
4. El self join une `por_dia d` con `por_dia a`, donde `a` es el día anterior. El lunes
   (1) se compara con el domingo (7) gracias al `CASE`. Así sale la variación porcentual
   frente al día previo.
5. `SUM(d.colisiones) OVER ()` pone el total de la semana en cada fila sin perder el
   detalle, y con eso se calcula el porcentaje de cada día. `RANK()` ordena los días de
   mayor a menor letalidad.
6. La subconsulta `(SELECT AVG(colisiones) FROM por_dia)` da la media diaria; el
   cociente indica si un día está por encima (más de 1) o por debajo (menos de 1).
7. Se multiplica por `100.0` o `1000.0` para que SQLite haga una división decimal; entre
   dos enteros, SQLite trunca el resultado.
""",
        "lectura": "El viernes concentra más colisiones (16,51 %) y el domingo menos "
                   "(11,68 %). Sin embargo, el domingo es el día más letal, con 11,55 muertos "
                   "por cada 1.000 colisiones, seguido del sábado con 10,24. De lunes a jueves "
                   "la letalidad se mantiene entre 6,29 y 6,95. El fin de semana tiene menos "
                   "colisiones, pero son más graves.",
    },
    2: {
        "titulo": "Culpabilidad por edad y sexo",
        "sql": SQL_2,
        "grafico": grafico_2,
        "enunciado": "Entre los conductores de 16 a 100 años, agrupados en cuatro grupos de "
                     "edad, ¿qué porcentaje de hombres y de mujeres fue declarado culpable de la "
                     "colisión? Ambos sexos deben quedar en la misma fila.",
        "tecnicas": "CTE `por_grupo_sexo`; self join hombres contra mujeres del mismo grupo; "
                    "ventana `RANK()`; subconsulta con el porcentaje de todos los conductores.",
        "explicacion": """
1. El CTE `por_grupo_sexo` lee la tabla `parties` (una fila por cada parte de la
   colisión) y se queda solo con conductores (`party_type = 'driver'`), con sexo
   informado y con edad entre 16 y 100 años, para descartar edades imposibles.
2. Un `CASE` asigna cada edad a su grupo: 16 a 24, 25 a 44, 45 a 64 y 65 o más. Se agrupa
   por grupo y sexo.
3. `at_fault` vale 1 si el conductor fue declarado culpable y 0 si no, así que
   `SUM(at_fault)` cuenta directamente a los culpables.
4. El self join toma el CTE dos veces: `h` con los hombres y `m` con las mujeres, unidos
   por el mismo grupo de edad. Así cada fila muestra los dos sexos lado a lado y se puede
   restar un porcentaje del otro.
5. La subconsulta escalar calcula el porcentaje de culpables de todos los conductores.
   `diferencia_con_total_puntos` dice cuántos puntos está cada grupo por encima o por
   debajo de ese total.
6. `RANK()` ordena los grupos de edad del más culpable al menos culpable, tomando a
   hombres y mujeres juntos.
""",
        "lectura": "Los jóvenes de 16 a 24 años son el grupo con mayor culpabilidad: 62,77 % "
                   "en hombres y 53,82 % en mujeres. El porcentaje baja hasta el grupo de 45 a "
                   "64 años y vuelve a subir a partir de los 65. Los hombres son declarados "
                   "culpables más a menudo en todos los grupos menos en el de 65 o más, donde "
                   "las mujeres los superan por 1,83 puntos.",
    },
    3: {
        "titulo": "Peso de las motocicletas en la mortalidad",
        "sql": SQL_3,
        "grafico": grafico_3,
        "enunciado": "Para cada año entre 2001 y 2020, ¿qué parte de las colisiones y de los "
                     "muertos corresponde a colisiones con motocicleta, y cuánto más letales son "
                     "que el resto?",
        "tecnicas": "CTE `por_anio`; self join del grupo con moto contra el resto del mismo "
                    "año; ventana `RANK()`; subconsulta con el porcentaje de todo el periodo.",
        "explicacion": """
1. El CTE `por_anio` saca el año de la fecha con `substr(collision_date, 1, 4)` y agrupa
   por año y por `motorcycle_collision`, que vale 1 si hubo una moto involucrada y 0 si
   no. Para cada combinación cuenta colisiones y suma muertos.
2. El self join pone en la misma fila el grupo con moto (`m`, moto = 1) y el resto (`r`,
   moto = 0) del mismo año. Sumando los dos se obtiene el total del año, y con él los
   porcentajes.
3. Se calcula la letalidad de cada grupo (muertos por cada 1.000 colisiones) y el
   cociente entre ambas: cuántas veces más letal es una colisión con moto.
4. `RANK()` ordena los años según el porcentaje de muertos que corresponde a motos.
5. La subconsulta suma con `CASE` los muertos con moto de los veinte años y los divide
   entre todos los muertos. La última columna dice cuántos puntos se aleja cada año de
   ese porcentaje del periodo.
""",
        "lectura": "Las colisiones con moto son apenas entre el 1,9 % y el 3,8 % del total, "
                   "pero representan entre el 7,7 % y el 17 % de los muertos. Una colisión con moto "
                   "es entre 4,3 y 5,9 veces más letal que una sin moto. El año con mayor peso "
                   "de las motos en la mortalidad fue 2014 (16,95 %) y el de mayor cociente fue "
                   "2008 (5,87). Desde 2008, todos los años quedan por encima del porcentaje "
                   "del periodo.",
    },
    4: {
        "titulo": "Mayores caídas interanuales por mes",
        "sql": SQL_4,
        "grafico": grafico_4,
        "enunciado": "Comparando cada mes de 2002 a 2020 con el mismo mes del año anterior, "
                     "¿cuáles son los diez meses con mayor caída porcentual de colisiones?",
        "tecnicas": "CTE `serie` y `comparacion`; self join de la serie con el año anterior; "
                    "ventanas `RANK()`, `SUM() OVER ()` y `COUNT() OVER ()`; subconsulta en el "
                    "`FROM` para quedarse con los diez primeros.",
        "explicacion": """
1. El CTE `serie` agrupa las colisiones por año y mes, sacados de la fecha con `substr`,
   y cuenta colisiones y muertos de cada mes.
2. El CTE `comparacion` hace el self join: cada mes `s` se une con `p`, el mismo mes del
   año anterior (`p.anio = s.anio - 1`). Los meses de 2001 no tienen con quién
   compararse, por eso quedan 19 x 12 = 228 meses. `NULLIF` evita dividir entre cero si
   un mes previo no tuviera muertos.
3. En la subconsulta del `FROM`, `RANK() OVER (ORDER BY var_colisiones)` ordena de la
   caída más fuerte a la menor. En la misma pasada, `SUM(CASE ...) OVER ()` cuenta
   cuántos meses bajaron y `COUNT(*) OVER ()` cuántos se compararon.
4. El filtro `WHERE puesto <= 10` va en la consulta exterior porque SQL no permite
   filtrar por una función de ventana en el mismo nivel donde se calcula.
""",
        "lectura": "Nueve de los diez meses son de 2020, el año de la pandemia. La mayor caída "
                   "fue abril de 2020, con 46,05 % menos colisiones que en abril de 2019. En "
                   "esos meses los muertos bajaron mucho menos que las colisiones, así que la "
                   "letalidad subió (11,21 en abril de 2020 frente a 7,15 un año antes). Agosto "
                   "de 2006 aparece en segundo lugar, pero parece un problema de registro de la "
                   "fuente más que una caída real. En total, 149 de los 228 meses tuvieron menos "
                   "colisiones que el mismo mes del año anterior.",
    },
    5: {
        "titulo": "Rachas de años con más muertos",
        "sql": SQL_5,
        "grafico": grafico_5,
        "enunciado": "Entre los condados con datos en los veinte años y con un total de muertos "
                     "igual o mayor que la media por condado, ¿cuál es la racha más larga de años "
                     "seguidos en que los muertos superaron al año anterior?",
        "tecnicas": "CTE `serie`, `condados_validos`, `aumentos`, `islas`, `rachas` y "
                    "`mejor_racha`; self join de la serie con el año anterior; ventanas "
                    "`ROW_NUMBER()` y `RANK()`; subconsulta con la media por condado.",
        "explicacion": """
1. El CTE `serie` suma los muertos de cada condado en cada año.
2. `condados_validos` se queda con los condados que tienen los 20 años
   (`COUNT(*) = 20`) y cuyo total de muertos es igual o mayor que la media. Esa media sale
   de una subconsulta anidada: primero suma los muertos por condado y luego promedia esos
   totales.
3. `aumentos` es el self join: une cada año con el anterior del mismo condado y guarda
   solo los años en que los muertos subieron.
4. `islas` agrupa los años de aumento que son seguidos. Si a cada año se le resta su
   número de fila (`ROW_NUMBER()`), los años consecutivos dan el mismo valor. Por
   ejemplo, 2012, 2013 y 2014 con filas 1, 2 y 3 dan 2011 las tres veces. Cuando hay un
   hueco, el valor cambia.
5. `rachas` agrupa por ese valor para obtener el año de inicio, el de fin y la duración
   de cada racha. `mejor_racha` numera las rachas de cada condado de la más larga a la
   más corta y se queda con la primera; si hay empate, gana la más antigua.
6. La consulta final ordena los condados con `RANK()` según la duración de su racha; por
   eso hay empates (dos terceros puestos y luego el quinto). Vuelve a unir con
   `aumentos` para mostrar los muertos del año previo a la racha y los del último año, y
   calcula el aumento porcentual.
""",
        "lectura": "Quince condados cumplen las condiciones. Riverside tiene la racha más "
                   "larga: siete años seguidos de aumento, de 2012 a 2018, en los que pasó de "
                   "203 a 318 muertos (56,65 % más). Le sigue Los Ángeles, con cinco años (2012 "
                   "a 2016) y un salto de 542 a 847 muertos. Las rachas más largas se concentran "
                   "entre 2011 y 2018, mientras que las de dos años se dieron sobre todo a "
                   "comienzos de la década de 2000.",
    },
}

# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------

if "en_vivo" not in st.session_state:
    st.session_state.en_vivo = {}


def ejecutar(numero, ruta):
    inicio = time.time()
    df = consultar(ruta, PREGUNTAS[numero]["sql"])
    st.session_state.en_vivo[numero] = (df, time.time() - inicio)


def resultado_guardado(numero):
    guardado = RESULTADOS_GUARDADOS[numero]
    return pd.DataFrame(guardado["filas"], columns=guardado["columnas"])


with st.sidebar:
    st.header("Fuente de datos")
    st.markdown("Los resultados ya están guardados en la app. El archivo `switrs.sqlite` "
                "solo hace falta para volver a ejecutar las consultas en vivo.")
    ruta = st.text_input("Ruta de switrs.sqlite (opcional)", RUTA_POR_DEFECTO)
    hay_fuente = Path(ruta).is_file()
    if hay_fuente:
        st.success(f"Archivo encontrado ({Path(ruta).stat().st_size / 1e9:.1f} GB).")
        if st.button("Ejecutar todas en vivo", type="primary"):
            with st.spinner("Ejecutando las cinco consultas (unos dos o tres minutos)..."):
                for n in PREGUNTAS:
                    ejecutar(n, ruta)
        st.caption("El archivo se abre en modo solo lectura. Cada resultado queda en caché, "
                   "así que volver a ejecutar una consulta es inmediato.")
    else:
        st.info("No se encontró el archivo: se muestran los resultados guardados.")

st.markdown("Perfiles de riesgo en colisiones de tránsito en California · Computación II · "
            "UCV EECA · Formulario G8")
st.markdown(
    "Cada pregunta se responde con una sola consulta SQL escrita para SQLite, que se ejecuta "
    "directamente sobre la fuente cruda `switrs.sqlite`, sin crear tablas, vistas ni "
    "índices. Todas usan al menos un CTE (`WITH`), una función de ventana (`OVER`), una "
    "subconsulta y un self join (una tabla unida consigo misma).")

st.info(
    "Los resultados que se muestran se obtuvieron ejecutando cada consulta sobre el archivo "
    "completo `switrs.sqlite` (9,9 GB) del conjunto *California Traffic Collision Data from "
    "SWITRS* de Kaggle, y quedaron guardados en la app. Quien tenga ese archivo puede "
    "indicar su ruta en la barra lateral y volver a ejecutarlas en vivo.")

pestanas = st.tabs(["Los datos"] + [f"Pregunta {n}" for n in PREGUNTAS])

with pestanas[0]:
    st.subheader("Los datos")
    st.markdown(
        "La fuente es la base SWITRS (Statewide Integrated Traffic Records System) de la "
        "Patrulla de Carreteras de California, publicada en Kaggle como un archivo SQLite. "
        "Las consultas usan dos de sus tablas:\n\n"
        "- `collisions`: una fila por colisión, con la fecha, el condado, la gravedad, los "
        "muertos (`killed_victims`) y si hubo una moto (`motorcycle_collision`).\n"
        "- `parties`: una fila por cada parte involucrada (conductor, peatón, ciclista, etc.), "
        "con su tipo, sexo, edad y si fue declarada culpable (`at_fault`).\n\n"
        "Las consultas sobre colisiones toman los veinte años de 2001 a 2020.")
    if hay_fuente:
        if st.button("Contar filas y ver una muestra", key="muestra"):
            with st.spinner("Contando filas..."):
                st.dataframe(filas_por_tabla(ruta), hide_index=True)
            st.markdown("Primeras filas de `collisions` (columnas que usan las consultas):")
            st.dataframe(consultar(ruta, """
                SELECT case_id, collision_date, county_location, collision_severity,
                       killed_victims, motorcycle_collision
                FROM collisions LIMIT 5"""), hide_index=True)
            st.markdown("Primeras filas de `parties`:")
            st.dataframe(consultar(ruta, """
                SELECT case_id, party_number, party_type, party_sex, party_age, at_fault,
                       vehicle_make
                FROM parties LIMIT 5"""), hide_index=True)

for pestana, (numero, p) in zip(pestanas[1:], PREGUNTAS.items()):
    with pestana:
        st.subheader(f"Pregunta {numero}. {p['titulo']}")
        st.markdown(f"**Enunciado.** {p['enunciado']}")
        st.markdown(f"**Técnicas.** {p['tecnicas']}")

        st.markdown("#### Consulta")
        st.code(p["sql"], language="sql")

        st.markdown("#### Explicación")
        st.markdown(p["explicacion"])

        st.markdown("#### Resultado")
        if hay_fuente and st.button("Ejecutar en vivo", key=f"ejecutar_{numero}"):
            with st.spinner("Recorriendo switrs.sqlite..."):
                ejecutar(numero, ruta)

        if numero in st.session_state.en_vivo:
            df, segundos = st.session_state.en_vivo[numero]
            st.caption(f"Ejecutada en vivo sobre switrs.sqlite: {len(df)} filas en "
                       f"{segundos:.1f} s.")
        else:
            df = resultado_guardado(numero)
            st.caption(f"Resultado guardado ({len(df)} filas), obtenido sobre el "
                       f"switrs.sqlite completo.")
        st.dataframe(df, hide_index=True)
        st.altair_chart(p["grafico"](df))
        st.markdown("#### Qué muestra")
        st.markdown(p["lectura"])
