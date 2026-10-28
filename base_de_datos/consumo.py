"""
Vistas de consumo: aquí se calculan los fallecidos, heridos, severidad,
número de partes y demás medidas que las tablas no guardan.

Cada medida se cuenta en su propio grano (víctimas en victima, partes en
parte) para que los totales no se inflen al unir tablas. conectar_lago() monta
los Parquet como tablas y crea estas mismas vistas encima, así que todo se
puede consultar sin la fuente.
"""

import duckdb

from catalogos import EXTRAS
from configuracion import DESDE, HASTA, NUCLEO, PROCESADOS


def antiguedad(anio_modelo):
    # Un modelo del año siguiente daría -1 y lo llevamos a 0. El CASE hace
    # falta porque GREATEST ignora los NULL y devolvería 0.
    return (f"CASE WHEN {anio_modelo} IS NOT NULL "
            f"THEN GREATEST(year(c.fecha) - {anio_modelo}, 0) END")


CATALOGOS = ["kabco", "mes", "dia_semana", *EXTRAS, "condado", "rango_poblacion",
             "ubicacion", "poblacion_condado", "banda_edad", "marca_vehiculo",
             "infraccion_vehicular"]

VISTAS = {
    "vw_calendario": f"""
        SELECT f.fecha,
               year(f.fecha)      AS anio,
               m.mes,
               m.nombre           AS nombre_mes,
               m.trimestre,
               d.dia_semana,
               d.nombre           AS nombre_dia,
               d.es_fin_semana
        FROM (SELECT CAST(unnest(generate_series(DATE '{DESDE}', DATE '{HASTA}' - 1,
                                                 INTERVAL 1 DAY)) AS DATE) AS fecha) f
        JOIN mes m        ON m.mes = month(f.fecha)
        JOIN dia_semana d ON d.dia_semana = isodow(f.fecha)
    """,

    # La severidad es el peor nivel KABCO entre sus víctimas; sin víctimas, O.
    "vw_colision": f"""
        WITH victimas AS (
            SELECT v.case_id,
                   MAX(k.nivel)                          AS nivel_max,
                   COUNT(*)                              AS victimas,
                   COUNT(*) FILTER (WHERE k.kabco = 'K') AS fallecidos,
                   COUNT(*) FILTER (WHERE k.kabco = 'A') AS heridos_graves,
                   COUNT(*) FILTER (WHERE k.kabco = 'B') AS heridos_visibles,
                   COUNT(*) FILTER (WHERE k.kabco = 'C') AS posibles_lesionados
            FROM victima v
            JOIN lesion l USING (lesion_id)
            LEFT JOIN kabco k USING (kabco)
            GROUP BY v.case_id
        ),
        partes AS (
            SELECT p.case_id,
                   COUNT(*)                                AS partes,
                   BOOL_OR(tp.codigo = 'pedestrian')       AS peaton_implicado,
                   BOOL_OR(tp.codigo = 'bicyclist')        AS ciclista_implicado,
                   BOOL_OR(tv.grupo = 'Motocicleta')       AS motociclista_implicado,
                   BOOL_OR(tv.grupo = 'Camión')            AS camion_implicado,
                   ANY_VALUE(p.tipo_parte_id) FILTER (WHERE p.culpable)
                                                           AS tipo_parte_culpable_id,
                   ANY_VALUE(p.tipo_vehiculo_id) FILTER (WHERE p.culpable)
                                                           AS tipo_vehiculo_culpable_id,
                   ANY_VALUE(p.edad) FILTER (WHERE p.culpable AND tp.codigo = 'driver')
                                                           AS edad_conductor_culpable,
                   ANY_VALUE(p.anio_vehiculo) FILTER (WHERE p.culpable)
                                                           AS anio_vehiculo_culpable
            FROM parte p
            JOIN tipo_parte tp    USING (tipo_parte_id)
            JOIN tipo_vehiculo tv USING (tipo_vehiculo_id)
            GROUP BY p.case_id
        )
        SELECT c.*,
               year(c.fecha)                                   AS anio,
               hour(c.hora)                                    AS hora_del_dia,
               u.condado_id,
               u.rango_poblacion_id,
               COALESCE(cl1.clima_id, 0)                       AS clima_id,
               cl2.clima_id                                    AS clima_2_id,
               COALESCE(cv1.condicion_via_id, 0)               AS condicion_via_id,
               cv2.condicion_via_id                            AS condicion_via_2_id,
               sev.kabco                                       AS severidad,
               sev.nivel                                       AS nivel_severidad,
               sev.kabco = 'K'                                 AS con_fallecido,
               sev.kabco IN ('K', 'A')                         AS es_grave,
               COALESCE(v.victimas, 0)                         AS victimas,
               COALESCE(v.fallecidos, 0)                       AS fallecidos,
               COALESCE(v.heridos_graves, 0)                   AS heridos_graves,
               COALESCE(v.heridos_visibles, 0)                 AS heridos_visibles,
               COALESCE(v.posibles_lesionados, 0)              AS posibles_lesionados,
               COALESCE(p.partes, 0)                           AS partes,
               COALESCE(p.peaton_implicado, FALSE)             AS peaton_implicado,
               COALESCE(p.ciclista_implicado, FALSE)           AS ciclista_implicado,
               COALESCE(p.motociclista_implicado, FALSE)       AS motociclista_implicado,
               COALESCE(p.camion_implicado, FALSE)             AS camion_implicado,
               f.codigo <> 'not hit and run'                   AS hubo_fuga,
               p.tipo_parte_culpable_id,
               p.tipo_vehiculo_culpable_id,
               p.edad_conductor_culpable,
               COALESCE(b.banda_edad_id, 0)                    AS banda_edad_conductor_culpable_id,
               p.anio_vehiculo_culpable,
               {antiguedad('p.anio_vehiculo_culpable')}        AS edad_vehiculo_culpable,
               g.case_id IS NOT NULL                           AS tiene_coordenadas,
               k.case_id IS NOT NULL                           AS tiene_datos_caltrans
        FROM colision c
        JOIN ubicacion u            USING (ubicacion_id)
        JOIN fuga f                 USING (fuga_id)
        LEFT JOIN victimas v        USING (case_id)
        LEFT JOIN partes p          USING (case_id)
        JOIN kabco sev              ON sev.nivel = COALESCE(v.nivel_max, 0)
        LEFT JOIN colision_clima cl1         ON cl1.case_id = c.case_id AND cl1.orden = 1
        LEFT JOIN colision_clima cl2         ON cl2.case_id = c.case_id AND cl2.orden = 2
        LEFT JOIN colision_condicion_via cv1 ON cv1.case_id = c.case_id AND cv1.orden = 1
        LEFT JOIN colision_condicion_via cv2 ON cv2.case_id = c.case_id AND cv2.orden = 2
        LEFT JOIN banda_edad b
               ON b.banda_edad_id > 0
              AND p.edad_conductor_culpable BETWEEN b.edad_min AND b.edad_max
        LEFT JOIN colision_geo g       ON g.case_id = c.case_id
        LEFT JOIN colision_carretera k ON k.case_id = c.case_id
    """,

    "vw_parte": f"""
        WITH victimas AS (
            SELECT v.case_id, v.numero_parte,
                   MAX(k.nivel)                          AS nivel_max_victimas,
                   COUNT(*)                              AS victimas,
                   COUNT(*) FILTER (WHERE k.kabco = 'K') AS fallecidos
            FROM victima v
            JOIN lesion l USING (lesion_id)
            LEFT JOIN kabco k USING (kabco)
            GROUP BY v.case_id, v.numero_parte
        )
        SELECT p.*,
               c.fecha,
               year(c.fecha)                                   AS anio,
               u.condado_id,
               COALESCE(b.banda_edad_id, 0)                    AS banda_edad_id,
               {antiguedad('p.anio_vehiculo')}                 AS edad_vehiculo,
               COALESCE(e1.equipo_seguridad_id, 0)             AS equipo_seguridad_id,
               e2.equipo_seguridad_id                          AS equipo_seguridad_2_id,
               COALESCE(f1.factor_asociado_id, 0)              AS factor_asociado_id,
               f2.factor_asociado_id                           AS factor_asociado_2_id,
               uc.en_uso                                       AS usaba_celular,
               v.nivel_max_victimas,
               COALESCE(v.victimas, 0)                         AS victimas,
               COALESCE(v.fallecidos, 0)                       AS fallecidos
        FROM parte p
        JOIN colision c    USING (case_id)
        JOIN ubicacion u   USING (ubicacion_id)
        JOIN uso_celular uc USING (uso_celular_id)
        LEFT JOIN banda_edad b
               ON b.banda_edad_id > 0 AND p.edad BETWEEN b.edad_min AND b.edad_max
        LEFT JOIN parte_equipo_seguridad e1
               ON e1.case_id = p.case_id AND e1.numero_parte = p.numero_parte AND e1.orden = 1
        LEFT JOIN parte_equipo_seguridad e2
               ON e2.case_id = p.case_id AND e2.numero_parte = p.numero_parte AND e2.orden = 2
        LEFT JOIN parte_factor_asociado f1
               ON f1.case_id = p.case_id AND f1.numero_parte = p.numero_parte AND f1.orden = 1
        LEFT JOIN parte_factor_asociado f2
               ON f2.case_id = p.case_id AND f2.numero_parte = p.numero_parte AND f2.orden = 2
        LEFT JOIN victimas v
               ON v.case_id = p.case_id AND v.numero_parte = p.numero_parte
    """,

    "vw_victima": f"""
        SELECT v.*,
               l.kabco,
               k.nivel                                         AS nivel_lesion,
               COALESCE(b.banda_edad_id, 0)                    AS banda_edad_id,
               COALESCE(e1.equipo_seguridad_id, 0)             AS equipo_seguridad_id,
               e2.equipo_seguridad_id                          AS equipo_seguridad_2_id,
               p.tipo_parte_id,
               p.tipo_vehiculo_id,
               p.anio_vehiculo,
               {antiguedad('p.anio_vehiculo')}                 AS edad_vehiculo,
               p.culpable                                      AS parte_culpable,
               c.fecha,
               year(c.fecha)                                   AS anio,
               u.condado_id
        FROM victima v
        JOIN lesion l       USING (lesion_id)
        LEFT JOIN kabco k   USING (kabco)
        JOIN parte p        USING (case_id, numero_parte)
        JOIN colision c   USING (case_id)
        JOIN ubicacion u  USING (ubicacion_id)
        LEFT JOIN banda_edad b
               ON b.banda_edad_id > 0 AND v.edad BETWEEN b.edad_min AND b.edad_max
        LEFT JOIN victima_equipo_seguridad e1
               ON e1.case_id = v.case_id AND e1.numero_parte = v.numero_parte
              AND e1.numero_victima = v.numero_victima AND e1.orden = 1
        LEFT JOIN victima_equipo_seguridad e2
               ON e2.case_id = v.case_id AND e2.numero_parte = v.numero_parte
              AND e2.numero_victima = v.numero_victima AND e2.orden = 2
    """,

    "vw_condado_anio": """
        WITH colisiones AS (
            SELECT u.condado_id, year(c.fecha) AS anio, COUNT(*) AS colisiones
            FROM colision c
            JOIN ubicacion u USING (ubicacion_id)
            GROUP BY ALL
        ),
        fallecidos AS (
            SELECT u.condado_id, year(c.fecha) AS anio, COUNT(*) AS fallecidos
            FROM victima v
            JOIN lesion l    USING (lesion_id)
            JOIN colision c  USING (case_id)
            JOIN ubicacion u USING (ubicacion_id)
            WHERE l.kabco = 'K'
            GROUP BY ALL
        )
        SELECT pc.condado_id,
               co.nombre                                         AS condado,
               pc.anio,
               pc.habitantes,
               COALESCE(c.colisiones, 0)                         AS colisiones,
               COALESCE(f.fallecidos, 0)                         AS fallecidos,
               100000 * COALESCE(c.colisiones, 0) / pc.habitantes AS colisiones_por_100k,
               100000 * COALESCE(f.fallecidos, 0) / pc.habitantes AS fallecidos_por_100k
        FROM poblacion_condado pc
        JOIN condado co        USING (condado_id)
        LEFT JOIN colisiones c USING (condado_id, anio)
        LEFT JOIN fallecidos f USING (condado_id, anio)
    """,
}


def crear_vistas(con):
    for nombre, consulta in VISTAS.items():
        con.execute(f"CREATE OR REPLACE VIEW {nombre} AS {consulta}")


def conectar_lago(directorio=PROCESADOS):
    """Conexión en memoria sobre los Parquet con las mismas tablas y vistas."""
    con = duckdb.connect()
    con.execute("SET enable_progress_bar = false")
    for catalogo in CATALOGOS:
        ruta = directorio / "catalogos" / f"{catalogo}.parquet"
        con.execute(f"CREATE VIEW {catalogo} AS SELECT * FROM read_parquet('{ruta}')")
    for tabla in NUCLEO:
        patron = directorio / tabla / "*.parquet"
        con.execute(f"CREATE VIEW {tabla} AS SELECT * FROM read_parquet('{patron}')")
    crear_vistas(con)
    return con
