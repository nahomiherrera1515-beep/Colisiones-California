"""
Carga el período 2010-2019 desde SWITRS a las tablas normalizadas.

Primero copiamos una sola vez las tres tablas de la fuente a tablas temporales.
La fuente no tiene índices, así que leer los 9,9 GB una vez por cada tabla
destino tardaría muchísimo más.

Después cada código se traduce a su id de catálogo (NULL o código desconocido
pasan al id 0), las fechas y horas se convierten a sus tipos, las edades y
años imposibles quedan en NULL con su bandera de cuarentena y las posiciones
1 y 2 de los grupos repetidos van a sus tablas puente.
"""

from configuracion import (ANIO_VEHICULO_MAX, ANIO_VEHICULO_MIN, DESDE,
                           EDAD_MAX, EDAD_MIN, HASTA, LAT_MAX, LAT_MIN,
                           LON_MAX, LON_MIN, NUCLEO, adjuntar_fuente, conectar)

# (columna destino, catálogo, columna de la fuente)
CODIGOS_COLISION = [
    ("iluminacion_id", "iluminacion", "lighting"),
    ("superficie_id", "superficie", "road_surface"),
    ("dispositivo_control_id", "dispositivo_control", "control_device"),
    ("tipo_colision_id", "tipo_colision", "type_of_collision"),
    ("implicado_con_id", "implicado_con", "motor_vehicle_involved_with"),
    ("factor_primario_id", "factor_primario", "primary_collision_factor"),
    ("categoria_infraccion_id", "categoria_infraccion", "pcf_violation_category"),
    ("fuga_id", "fuga", "hit_and_run"),
    ("accion_peaton_id", "accion_peaton", "pedestrian_action"),
]

CODIGOS_CARRETERA = [
    ("tipo_ubicacion_id", "tipo_ubicacion", "location_type"),
    ("sentido_id", "sentido", "side_of_highway"),
]

CODIGOS_PARTE = [
    ("tipo_parte_id", "tipo_parte", "party_type"),
    ("sexo_id", "sexo", "party_sex"),
    ("raza_id", "raza", "party_race"),
    ("sobriedad_id", "sobriedad", "party_sobriety"),
    ("droga_fisica_id", "droga_fisica", "party_drug_physical"),
    ("direccion_id", "direccion", "direction_of_travel"),
    ("movimiento_previo_id", "movimiento_previo", "movement_preceding_collision"),
    ("tipo_vehiculo_id", "tipo_vehiculo", "statewide_vehicle_type"),
    ("vehiculo_chp_id", "vehiculo_chp", "chp_vehicle_type_towing"),
    ("remolque_chp_id", "vehiculo_chp", "chp_vehicle_type_towed"),
    ("responsabilidad_financiera_id", "responsabilidad_financiera", "financial_responsibility"),
    ("uso_celular_id", "uso_celular", "cellphone_use_type"),
]

CODIGOS_VICTIMA = [
    ("rol_victima_id", "rol_victima", "victim_role"),
    ("sexo_id", "sexo", "victim_sex"),
    ("lesion_id", "lesion", "victim_degree_of_injury"),
    ("asiento_id", "asiento", "victim_seating_position"),
    ("eyeccion_id", "eyeccion", "victim_ejected"),
]

# En estos un NULL significa "no hubo", no "sin clasificar", y se conserva.
OPCIONALES_CARRETERA = [("rampa_interseccion_id", "rampa_interseccion", "ramp_intersection")]
OPCIONALES_PARTE = [("otra_infraccion_categoria_id", "otra_infraccion_categoria",
                     "oaf_violation_category")]

LLAVE_COLISION = "s.case_id"
LLAVE_PARTE = "s.case_id, s.party_number AS numero_parte"
LLAVE_VICTIMA = "s.case_id, s.party_number AS numero_parte, s.numero_victima"

# (tabla puente, llave, catálogo, tabla temporal, columnas de la fuente en orden)
PUENTES = [
    ("colision_clima", LLAVE_COLISION, "clima", "s_col", ["weather_1", "weather_2"]),
    ("colision_condicion_via", LLAVE_COLISION, "condicion_via", "s_col",
     ["road_condition_1", "road_condition_2"]),
    ("parte_equipo_seguridad", LLAVE_PARTE, "equipo_seguridad", "s_par",
     ["party_safety_equipment_1", "party_safety_equipment_2"]),
    ("parte_factor_asociado", LLAVE_PARTE, "factor_asociado", "s_par",
     ["other_associate_factor_1", "other_associate_factor_2"]),
    ("victima_equipo_seguridad", LLAVE_VICTIMA, "equipo_seguridad", "s_vic",
     ["victim_safety_equipment_1", "victim_safety_equipment_2"]),
]


def resolver(codigos, opcionales=()):
    """Devuelve las columnas y los LEFT JOIN que traducen cada código a su id."""
    columnas, uniones = [], []
    for i, (destino, catalogo, origen) in enumerate([*codigos, *opcionales]):
        alias = f"k{i}"
        uniones.append(f"LEFT JOIN {catalogo} {alias} ON {alias}.codigo = s.{origen}")
        id_o_cero = f"COALESCE({alias}.{catalogo}_id, 0)"
        if i >= len(codigos):
            id_o_cero = f"CASE WHEN s.{origen} IS NOT NULL THEN {id_o_cero} END"
        columnas.append(f"{id_o_cero} AS {destino}")
    return ",\n               ".join(columnas), "\n        ".join(uniones)


def en_rango(columna, minimo, maximo):
    return f"CASE WHEN {columna} BETWEEN {minimo} AND {maximo} THEN {columna} END"


def en_cuarentena(columna, minimo, maximo):
    return f"COALESCE({columna} NOT BETWEEN {minimo} AND {maximo}, FALSE)"


def extraer(con):
    adjuntar_fuente(con)
    # Fuera del período hay case_id con letras, por eso filtramos con el texto
    # original y convertimos a número después.
    con.execute(f"""
        CREATE TEMP TABLE casos AS
        SELECT case_id FROM src.collisions
        WHERE collision_date >= '{DESDE}' AND collision_date < '{HASTA}'
    """)
    con.execute("""
        CREATE TEMP TABLE s_col AS
        SELECT * REPLACE (CAST(case_id AS INTEGER) AS case_id)
        FROM src.collisions
        WHERE case_id IN (SELECT case_id FROM casos)
    """)
    con.execute("""
        CREATE TEMP TABLE s_par AS
        SELECT * REPLACE (CAST(case_id AS INTEGER) AS case_id,
                          CAST(party_number AS UTINYINT) AS party_number)
        FROM src.parties
        WHERE case_id IN (SELECT case_id FROM casos)
    """)
    # El id de la víctima no se repite dentro de su parte, así que ordenar por
    # él numera siempre igual.
    con.execute("""
        CREATE TEMP TABLE s_vic AS
        SELECT * REPLACE (CAST(case_id AS INTEGER) AS case_id,
                          CAST(party_number AS UTINYINT) AS party_number),
               CAST(ROW_NUMBER() OVER (PARTITION BY case_id, party_number ORDER BY id)
                    AS UTINYINT) AS numero_victima
        FROM src.victims
        WHERE case_id IN (SELECT case_id FROM casos)
    """)
    con.execute("DETACH src")


def cargar_colision(con):
    columnas, uniones = resolver(CODIGOS_COLISION)
    con.execute(f"""
        INSERT INTO colision BY NAME
        SELECT s.case_id,
               CAST(s.collision_date AS DATE)                AS fecha,
               CAST(s.collision_time AS TIME)                AS hora,
               CAST(s.county_city_location AS USMALLINT)     AS ubicacion_id,
               CAST(s.jurisdiction AS USMALLINT)             AS jurisdiccion,
               {columnas},
               iv.infraccion_vehicular_id,
               CAST(s.intersection AS BOOLEAN)               AS en_interseccion,
               CAST(s.tow_away AS BOOLEAN)                   AS vehiculo_remolcado,
               CAST(s.state_highway_indicator AS BOOLEAN)    AS carretera_estatal,
               s.special_condition = '1'                     AS condicion_especial
        FROM s_col s
        {uniones}
        LEFT JOIN infraccion_vehicular iv
               ON iv.seccion = s.pcf_violation
              AND iv.inciso IS NOT DISTINCT FROM s.pcf_violation_subsection
    """)


def cargar_subtipos(con):
    con.execute(f"""
        INSERT INTO colision_geo
        SELECT case_id,
               CAST(latitude AS DECIMAL(8, 5)),
               CAST(longitude AS DECIMAL(8, 5))
        FROM s_col
        WHERE latitude BETWEEN {LAT_MIN} AND {LAT_MAX}
          AND longitude BETWEEN {LON_MIN} AND {LON_MAX}
    """)
    columnas, uniones = resolver(CODIGOS_CARRETERA, OPCIONALES_CARRETERA)
    con.execute(f"""
        INSERT INTO colision_carretera BY NAME
        SELECT s.case_id,
               COALESCE(cc.condado_id, 0)                AS condado_caltrans_id,
               CAST(s.caltrans_district AS UTINYINT)     AS distrito_caltrans,
               CAST(s.state_route AS USMALLINT)          AS ruta_estatal,
               s.postmile_prefix                         AS prefijo_postmile,
               CAST(s.postmile AS DECIMAL(6, 3))         AS postmile,
               {columnas}
        FROM s_col s
        {uniones}
        LEFT JOIN condado cc ON cc.codigo = s.caltrans_county
        WHERE s.caltrans_county IS NOT NULL
    """)


def cargar_parte(con):
    columnas, uniones = resolver(CODIGOS_PARTE, OPCIONALES_PARTE)
    edad = ("s.party_age", EDAD_MIN, EDAD_MAX)
    anio = ("s.vehicle_year", ANIO_VEHICULO_MIN, ANIO_VEHICULO_MAX)
    con.execute(f"""
        INSERT INTO parte BY NAME
        SELECT s.case_id,
               s.party_number                                    AS numero_parte,
               {columnas},
               s.at_fault = 1                                    AS culpable,
               {en_rango(*edad)}                                 AS edad,
               {en_cuarentena(*edad)}                            AS edad_en_cuarentena,
               {en_rango(*anio)}                                 AS anio_vehiculo,
               {en_cuarentena(*anio)}                            AS anio_vehiculo_en_cuarentena,
               COALESCE(mv.marca_vehiculo_id, 0)                 AS marca_vehiculo_id,
               CASE WHEN s.hazardous_materials = 1 THEN TRUE END AS materiales_peligrosos,
               CASE WHEN s.school_bus_related = 1 THEN TRUE END  AS relacion_bus_escolar,
               iv.infraccion_vehicular_id                        AS otra_infraccion_vehicular_id
        FROM s_par s
        {uniones}
        LEFT JOIN marca_vehiculo mv ON mv.codigo = s.vehicle_make
        LEFT JOIN infraccion_vehicular iv
               ON iv.seccion = CAST(s.oaf_violation_section AS INTEGER)
              AND iv.inciso IS NOT DISTINCT FROM s.oaf_violation_suffix
    """)


def cargar_victima(con):
    columnas, uniones = resolver(CODIGOS_VICTIMA)
    edad = ("s.victim_age", EDAD_MIN, EDAD_MAX)
    con.execute(f"""
        INSERT INTO victima BY NAME
        SELECT s.case_id,
               s.party_number             AS numero_parte,
               s.numero_victima,
               {columnas},
               {en_rango(*edad)}          AS edad,
               {en_cuarentena(*edad)}     AS edad_en_cuarentena
        FROM s_vic s
        {uniones}
    """)


def cargar_puentes(con):
    # Una fila por posición llena; un código desconocido apunta al id 0.
    for tabla, llave, catalogo, temporal, origenes in PUENTES:
        bloques = [f"""
            SELECT {llave}, {orden} AS orden, COALESCE(k.{catalogo}_id, 0) AS {catalogo}_id
            FROM {temporal} s
            LEFT JOIN {catalogo} k ON k.codigo = s.{origen}
            WHERE s.{origen} IS NOT NULL"""
                   for orden, origen in enumerate(origenes, start=1)]
        con.execute(f"INSERT INTO {tabla} BY NAME {' UNION ALL '.join(bloques)}")


def main():
    with conectar() as con:
        for tabla in reversed(NUCLEO):
            con.execute(f"DELETE FROM {tabla}")
        extraer(con)
        cargar_colision(con)
        cargar_subtipos(con)
        cargar_parte(con)
        cargar_victima(con)
        cargar_puentes(con)
        con.execute("CHECKPOINT")
    print("Carga terminada")


if __name__ == "__main__":
    main()
