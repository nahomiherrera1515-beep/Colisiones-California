"""
Crea en MotherDuck la capa desnormalizada, en la base colisiones_analitica.

Las vistas de la base normalizada ya arman una estrella por grano. Aquí se
guardan como tablas: tres tablas de hechos (colisión, parte y víctima), el
resumen por condado y año, y las dimensiones. Es la capa que consultan el
tablero y Power BI, y deja a la vista el paso de la 3FN al modelo en estrella.

Requiere haber corrido 01 a 04 con DESTINO=motherduck.
"""

import duckdb

from configuracion import ANALITICA_MD, EN_LA_NUBE, NORMALIZADA_MD
from consumo import CATALOGOS

HECHOS = {
    "hechos_colision": "vw_colision",
    "hechos_parte": "vw_parte",
    "hechos_victima": "vw_victima",
    "resumen_condado_anio": "vw_condado_anio",
    "dim_fecha": "vw_calendario",
}

# Las tablas de apoyo de la normalización no son dimensiones de la estrella.
NO_DIMENSIONES = {"mes", "dia_semana", "ubicacion", "poblacion_condado"}


def main():
    if not EN_LA_NUBE:
        raise SystemExit("La capa analítica se arma en MotherDuck: corra con DESTINO=motherduck.")
    with duckdb.connect("md:") as con:
        con.execute(f"DROP DATABASE IF EXISTS {ANALITICA_MD} CASCADE")
        con.execute(f"CREATE DATABASE {ANALITICA_MD}")
        # Las vistas se resuelven dentro de su propia base.
        con.execute(f"USE {NORMALIZADA_MD}")
        for tabla, vista in HECHOS.items():
            con.execute(f"CREATE TABLE {ANALITICA_MD}.{tabla} AS SELECT * FROM {vista}")
        for catalogo in CATALOGOS:
            if catalogo not in NO_DIMENSIONES:
                con.execute(f"CREATE TABLE {ANALITICA_MD}.dim_{catalogo} AS SELECT * FROM {catalogo}")
        tablas = con.execute(f"""
            SELECT table_name, estimated_size FROM duckdb_tables()
            WHERE database_name = '{ANALITICA_MD}' AND table_name NOT LIKE 'dim_%'
            ORDER BY 1
        """).fetchall()
    for tabla, filas in tablas:
        print(f"{tabla:<24}{filas:>12,} filas")
    print(f"Capa analítica en MotherDuck: {ANALITICA_MD}")


if __name__ == "__main__":
    main()
