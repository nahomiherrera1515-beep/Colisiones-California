"""
Sube la fuente cruda de SWITRS a Supabase Storage.

Van las cuatro tablas originales del archivo de Kaggle (collisions, parties,
victims y case_ids), con todos los años y sin cambiar ningún dato. El .sqlite
pesa 9,9 GB y Supabase gratuito no acepta archivos de más de 50 MB, así que
cada tabla se guarda en Parquet partida en archivos de menos de 40 MB. Antes de
subir se comprueba que los Parquet sean idénticos al .sqlite fila por fila.

Necesita las variables SUPABASE_S3_ENDPOINT, SUPABASE_S3_REGION,
SUPABASE_S3_KEY_ID, SUPABASE_S3_SECRET y SUPABASE_BUCKET (las claves de
Storage → Settings → S3 Connection). Nunca se escriben en el código.
"""

import os
import shutil
from concurrent.futures import ThreadPoolExecutor

import boto3
import duckdb

from configuracion import FUENTE, RAIZ

TABLAS = ["collisions", "parties", "victims", "case_ids"]
PARQUET = RAIZ / "data" / "raw" / "parquet"


def exportar(con):
    shutil.rmtree(PARQUET, ignore_errors=True)
    PARQUET.mkdir(parents=True)
    for tabla in TABLAS:
        con.execute(f"""
            COPY (SELECT * FROM src.{tabla}) TO '{PARQUET / tabla}'
            (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 9, FILE_SIZE_BYTES '40MB')
        """)


def verificar(con):
    # Una huella por fila que cubre todas las columnas: si cambiara un solo
    # valor, la suma de huellas no coincidiría.
    for tabla in TABLAS:
        huella = "SELECT COUNT(*), SUM(hash(x)::HUGEINT) FROM {} x"
        sqlite = con.execute(huella.format(f"src.{tabla}")).fetchone()
        parquet = con.execute(huella.format(f"read_parquet('{PARQUET / tabla}/*.parquet')")).fetchone()
        if sqlite != parquet:
            raise SystemExit(f"{tabla}: los Parquet no coinciden con el .sqlite")
        print(f"{tabla:<12}{sqlite[0]:>12,} filas idénticas")


def subir():
    s3 = boto3.client("s3", endpoint_url=os.environ["SUPABASE_S3_ENDPOINT"],
                      region_name=os.environ["SUPABASE_S3_REGION"],
                      aws_access_key_id=os.environ["SUPABASE_S3_KEY_ID"],
                      aws_secret_access_key=os.environ["SUPABASE_S3_SECRET"])
    bucket = os.environ["SUPABASE_BUCKET"]
    archivos = sorted(PARQUET.rglob("*.parquet"))
    with ThreadPoolExecutor(4) as hilos:
        list(hilos.map(lambda a: s3.upload_file(str(a), bucket, f"{a.parent.name}/{a.name}"),
                       archivos))
    print(f"{len(archivos)} archivos subidos al bucket {bucket}")


def main():
    if not FUENTE.exists():
        raise SystemExit(f"No está {FUENTE}. Descárguelo de Kaggle o indique SWITRS_PATH.")
    with duckdb.connect() as con:
        con.execute("INSTALL sqlite; LOAD sqlite;")
        con.execute(f"ATTACH '{FUENTE}' AS src (TYPE sqlite, READ_ONLY)")
        exportar(con)
        verificar(con)
    subir()


if __name__ == "__main__":
    main()
