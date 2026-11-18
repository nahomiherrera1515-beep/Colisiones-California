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