"""Rutas, período de estudio y rangos válidos que comparten todos los scripts."""

import os
from pathlib import Path

import duckdb

DIRECTORIO = Path(__file__).resolve().parent
RAIZ = DIRECTORIO.parent

BASE = DIRECTORIO / "siniestralidad_california.duckdb"
FUENTE = Path(
    os.environ.get("SWITRS_PATH", RAIZ / "data" / "raw" / "switrs.sqlite")
).expanduser()
CENSO = RAIZ / "data" / "externa" / "census_co-est2019_california.csv"
PROCESADOS = RAIZ / "data" / "processed"
CIFRAS = RAIZ / "resultados" / "cifras.json"

# La fuente guarda la fecha como texto ISO, así que comparar cadenas basta.
DESDE, HASTA = "2010-01-01", "2020-01-01"
ANIOS = range(2010, 2020)

# Fuera de estos rangos el valor queda en NULL, pero la fila se conserva.
EDAD_MIN, EDAD_MAX = 0, 110
ANIO_VEHICULO_MIN, ANIO_VEHICULO_MAX = 1900, 2020
LAT_MIN, LAT_MAX = 32, 43
LON_MIN, LON_MAX = -125, -114

# Tablas con datos de casos y su llave, en orden de carga.
NUCLEO = {
    "colision": "case_id",
    "colision_clima": "case_id, orden",
    "colision_condicion_via": "case_id, orden",
    "colision_geo": "case_id",
    "colision_carretera": "case_id",
    "parte": "case_id, numero_parte",
    "parte_equipo_seguridad": "case_id, numero_parte, orden",
    "parte_factor_asociado": "case_id, numero_parte, orden",
    "victima": "case_id, numero_parte, numero_victima",
    "victima_equipo_seguridad": "case_id, numero_parte, numero_victima, orden",
}


def conectar(solo_lectura=False):
    return duckdb.connect(str(BASE), read_only=solo_lectura)


def adjuntar_fuente(con):
    if not FUENTE.exists():
        raise SystemExit(f"No está {FUENTE}. Descárguelo de Kaggle o indique SWITRS_PATH.")
    con.execute("INSTALL sqlite; LOAD sqlite;")
    con.execute(f"ATTACH '{FUENTE}' AS src (TYPE sqlite, READ_ONLY)")
