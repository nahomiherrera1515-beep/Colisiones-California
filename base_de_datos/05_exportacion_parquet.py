"""
Exporta la base normalizada a Parquet en data/processed/.

Parquet lo leen DuckDB, pandas, R y Power BI sin depender de una versión del
motor, y comprime mucho mejor que la base. Las tablas con datos de casos van
en un archivo por año, así ninguno pasa del límite de GitHub y al filtrar por
año solo se abren los archivos necesarios. Las vistas no se exportan:
conectar_lago() las vuelve a crear encima de los archivos.
"""

import shutil

from configuracion import ANIOS, NUCLEO, PROCESADOS, conectar
from consumo import CATALOGOS

OPCIONES = "FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 9, PARQUET_VERSION V2"


def exportar_catalogos(con):
    destino = PROCESADOS / "catalogos"
    destino.mkdir(parents=True)
    for catalogo in CATALOGOS:
        con.execute(f"COPY (SELECT * FROM {catalogo} ORDER BY ALL) "
                    f"TO '{destino / catalogo}.parquet' ({OPCIONES})")


def exportar_nucleo(con):
    # Partes, víctimas, subtipos y tablas puente toman el año de su colisión.
    for tabla, llave in NUCLEO.items():
        destino = PROCESADOS / tabla
        destino.mkdir(parents=True)
        for anio in ANIOS:
            con.execute(f"""
                COPY (SELECT t.*
                      FROM {tabla} t
                      SEMI JOIN (SELECT case_id FROM colision WHERE year(fecha) = {anio}) a
                           USING (case_id)
                      ORDER BY {llave})
                TO '{destino / tabla}_{anio}.parquet' ({OPCIONES})
            """)


def main():
    shutil.rmtree(PROCESADOS, ignore_errors=True)
    with conectar(solo_lectura=True) as con:
        exportar_catalogos(con)
        exportar_nucleo(con)
    print(f"Parquet escritos en {PROCESADOS}")


if __name__ == "__main__":
    main()
