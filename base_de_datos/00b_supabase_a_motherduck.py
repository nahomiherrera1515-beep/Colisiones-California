"""
Crea en MotherDuck la base colisiones_crudo a partir de los Parquet de Supabase.

MotherDuck lee los archivos directamente desde el bucket de Supabase, dentro de
la nube, así que no pasan de nuevo por la conexión de la Mac. El resultado son
las cuatro tablas crudas como tablas SQL normales, con los mismos nombres y
columnas del archivo de Kaggle. Desde ahí trabajan los scripts 01 a 04 con
DESTINO=motherduck.

Necesita motherduck_token y las mismas variables de Supabase que 00a.
"""

import os

import duckdb

from configuracion import CRUDO_MD

TABLAS = ["collisions", "parties", "victims", "case_ids"]


def main():
    bucket = os.environ["SUPABASE_BUCKET"]
    endpoint = os.environ["SUPABASE_S3_ENDPOINT"].removeprefix("https://")
    with duckdb.connect("md:") as con:
        # El secreto queda guardado en la cuenta de MotherDuck, no en el código.
        con.execute(f"""
            CREATE OR REPLACE SECRET supabase_crudo IN MOTHERDUCK (
                TYPE S3,
                KEY_ID '{os.environ["SUPABASE_S3_KEY_ID"]}',
                SECRET '{os.environ["SUPABASE_S3_SECRET"]}',
                REGION '{os.environ["SUPABASE_S3_REGION"]}',
                ENDPOINT '{endpoint}',
                URL_STYLE 'path',
                SCOPE 's3://{bucket}'
            )
        """)
        con.execute(f"CREATE DATABASE IF NOT EXISTS {CRUDO_MD}")
        for tabla in TABLAS:
            con.execute(f"""
                CREATE OR REPLACE TABLE {CRUDO_MD}.{tabla} AS
                SELECT * FROM read_parquet('s3://{bucket}/{tabla}/*.parquet')
            """)
            filas = con.execute(f"SELECT COUNT(*) FROM {CRUDO_MD}.{tabla}").fetchone()[0]
            print(f"{tabla:<12}{filas:>12,} filas")
    print(f"Fuente cruda en MotherDuck: {CRUDO_MD}")


if __name__ == "__main__":
    main()
