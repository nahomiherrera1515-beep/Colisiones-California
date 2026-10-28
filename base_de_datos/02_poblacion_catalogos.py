"""
Llena los catálogos: los escritos a mano en catalogos.py y los tres que salen
de la propia fuente (ubicacion, marca_vehiculo e infraccion_vehicular).
"""

from catalogos import (BANDAS_EDAD, CONDADOS, DIAS, EXTRAS, KABCO, MESES,
                       RANGO_POBLACION, VALORES)
from configuracion import DESDE, HASTA, adjuntar_fuente, conectar

PERIODO = f"collision_date >= '{DESDE}' AND collision_date < '{HASTA}'"
CASOS_DEL_PERIODO = f"case_id IN (SELECT case_id FROM src.collisions WHERE {PERIODO})"


def poblar_catalogos_base(con):
    con.executemany("INSERT INTO kabco VALUES (?, ?, ?, ?)", KABCO)
    con.executemany("INSERT INTO mes VALUES (?, ?, ?)",
                    [(i, nombre, (i - 1) // 3 + 1) for i, nombre in enumerate(MESES, start=1)])
    con.executemany("INSERT INTO dia_semana VALUES (?, ?, ?)",
                    [(i, nombre, i >= 6) for i, nombre in enumerate(DIAS, start=1)])


def poblar_catalogos_de_codigos(con):
    # El id 0 "Sin clasificar" recibe los NULL y los códigos que no están en la lista.
    for nombre, filas in VALORES.items():
        n_extras = len(EXTRAS[nombre])
        marcadores = ", ".join(["?"] * (4 + n_extras))
        con.execute(f"INSERT INTO {nombre} VALUES ({marcadores})",
                    [0, None, "Sin clasificar", 0] + [None] * n_extras)
        con.executemany(f"INSERT INTO {nombre} VALUES ({marcadores})",
                        [[i, codigo, etiqueta, i, *extras]
                         for i, (codigo, etiqueta, *extras) in enumerate(filas, start=1)])


def poblar_geografia(con):
    con.execute("INSERT INTO condado VALUES (0, NULL, 'Sin clasificar')")
    con.executemany("INSERT INTO condado VALUES (?, ?, ?)",
                    [(i, nombre.lower(), nombre) for i, nombre in enumerate(CONDADOS, start=1)])
    con.execute("INSERT INTO rango_poblacion VALUES (0, NULL, 'Sin clasificar', 0)")
    con.executemany("INSERT INTO rango_poblacion VALUES (?, ?, ?, ?)",
                    [(i, codigo, etiqueta, i)
                     for i, (codigo, etiqueta) in enumerate(RANGO_POBLACION, start=1)])
    con.executemany("INSERT INTO banda_edad VALUES (?, ?, ?, ?)", BANDAS_EDAD)


def poblar_desde_fuente(con):
    adjuntar_fuente(con)

    # Los dos primeros dígitos de county_city_location son el código del condado.
    con.execute(f"""
        INSERT INTO ubicacion
        SELECT DISTINCT CAST(s.county_city_location AS USMALLINT),
               CAST(substr(s.county_city_location, 1, 2) AS UTINYINT),
               COALESCE(r.rango_poblacion_id, 0)
        FROM src.collisions s
        LEFT JOIN rango_poblacion r ON r.codigo = s.population
        WHERE {PERIODO}
    """)

    # Numeradas de la más a la menos frecuente.
    con.execute(f"""
        INSERT INTO marca_vehiculo
        SELECT 0, NULL
        UNION ALL
        SELECT ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC, vehicle_make), vehicle_make
        FROM src.parties
        WHERE vehicle_make IS NOT NULL AND {CASOS_DEL_PERIODO}
        GROUP BY vehicle_make
    """)

    # La infracción principal de la colisión y la otra infracción de cada
    # parte son citas del mismo código vehicular, así que comparten catálogo.
    con.execute(f"""
        INSERT INTO infraccion_vehicular
        WITH citas AS (
            SELECT CAST(pcf_violation AS INTEGER) AS seccion,
                   pcf_violation_subsection        AS inciso
            FROM src.collisions
            WHERE {PERIODO} AND pcf_violation IS NOT NULL
            UNION
            SELECT CAST(oaf_violation_section AS INTEGER), oaf_violation_suffix
            FROM src.parties
            WHERE oaf_violation_section IS NOT NULL AND {CASOS_DEL_PERIODO}
        )
        SELECT ROW_NUMBER() OVER (ORDER BY seccion, inciso NULLS FIRST), seccion, inciso
        FROM citas
    """)
    con.execute("DETACH src")


def main():
    with conectar() as con:
        poblar_catalogos_base(con)
        poblar_catalogos_de_codigos(con)
        poblar_geografia(con)
        poblar_desde_fuente(con)
    print("Catálogos poblados")


if __name__ == "__main__":
    main()
