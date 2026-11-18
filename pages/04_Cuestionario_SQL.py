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