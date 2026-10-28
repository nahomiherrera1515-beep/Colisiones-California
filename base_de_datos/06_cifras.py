"""
Calcula sobre los Parquet las cifras que vamos a citar en el README y en el
informe, y las guarda en resultados/cifras.json. Así ningún número se escribe
a mano.
"""

import json

from configuracion import CIFRAS
from consumo import conectar_lago

# Porcentaje de colisiones con al menos un fallecido dentro de cada grupo.
PCT_FALLECIDO = "ROUND(100 * AVG(CAST(con_fallecido AS DOUBLE)), 2)"

# Para el objetivo 2 solo cuentan las colisiones cuyo culpable es un conductor;
# así un atropello en que el peatón tuvo la culpa no se mezcla con el resto.
CULPABLE_CONDUCTOR = """tipo_parte_culpable_id = (SELECT tipo_parte_id FROM tipo_parte
                                                     WHERE codigo = 'driver')"""


def uno(con, sql):
    return con.execute(sql).fetchone()[0]


def pares(con, sql):
    return {str(clave): valor for clave, valor in con.execute(sql).fetchall()}


def variacion(antes, despues):
    return round(100 * (despues - antes) / antes, 1)


def calcular(con):
    c = {}
    c["colisiones"] = uno(con, "SELECT COUNT(*) FROM colision")
    c["partes"] = uno(con, "SELECT COUNT(*) FROM parte")
    c["victimas"] = uno(con, "SELECT COUNT(*) FROM victima")
    c["fallecidos"] = uno(con, "SELECT SUM(fallecidos) FROM vw_colision")
    c["condados"] = uno(con, "SELECT COUNT(DISTINCT condado_id) FROM vw_colision")

    # Entre años solo comparamos fallecidos: en 2017 cambiaron los códigos de lesión.
    c["colisiones_por_anio"] = pares(con, """
        SELECT anio, COUNT(*) FROM vw_colision GROUP BY 1 ORDER BY 1""")
    c["fallecidos_por_anio"] = pares(con, """
        SELECT anio, SUM(fallecidos) FROM vw_colision GROUP BY 1 ORDER BY 1""")
    c["variacion_colisiones_2010_2017"] = variacion(c["colisiones_por_anio"]["2010"],
                                                    c["colisiones_por_anio"]["2017"])
    c["variacion_fallecidos_2010_2017"] = variacion(c["fallecidos_por_anio"]["2010"],
                                                    c["fallecidos_por_anio"]["2017"])

    graves = pares(con, """
        SELECT anio, COUNT(*) FROM vw_victima WHERE kabco = 'A' GROUP BY 1 ORDER BY 1""")
    ilesos = pares(con, """
        SELECT anio, COUNT(*) FROM vw_victima WHERE kabco = 'O' GROUP BY 1 ORDER BY 1""")
    c["variacion_heridos_graves_2016_2019"] = variacion(graves["2016"], graves["2019"])
    c["variacion_ilesos_2016_2019"] = variacion(ilesos["2016"], ilesos["2019"])

    c["condados_principales"] = pares(con, """
        SELECT co.nombre, COUNT(*)
        FROM vw_colision v JOIN condado co USING (condado_id)
        GROUP BY 1 ORDER BY 2 DESC LIMIT 5""")
    c["pct_colisiones_los_angeles"] = round(
        100 * c["condados_principales"]["Los Angeles"] / c["colisiones"], 1)
    c["fallecidos_por_100k_2010"], c["fallecidos_por_100k_2019"] = con.execute("""
        SELECT ROUND(100000 * SUM(fallecidos) FILTER (WHERE anio = 2010)
                            / SUM(habitantes) FILTER (WHERE anio = 2010), 2),
               ROUND(100000 * SUM(fallecidos) FILTER (WHERE anio = 2019)
                            / SUM(habitantes) FILTER (WHERE anio = 2019), 2)
        FROM vw_condado_anio""").fetchone()

    c["colisiones_por_dia_semana"] = pares(con, """
        SELECT k.nombre_dia, ROUND(COUNT(v.case_id) / COUNT(DISTINCT k.fecha))
        FROM vw_calendario k
        LEFT JOIN colision v USING (fecha)
        GROUP BY k.dia_semana, k.nombre_dia
        ORDER BY k.dia_semana""")

    c["pct_fallecido_por_banda_edad"] = pares(con, f"""
        SELECT b.etiqueta, {PCT_FALLECIDO}
        FROM vw_colision v
        JOIN banda_edad b ON b.banda_edad_id = v.banda_edad_conductor_culpable_id
        GROUP BY b.banda_edad_id, b.etiqueta
        ORDER BY b.banda_edad_id""")
    c["pct_fallecido_sin_alcohol"], c["pct_fallecido_con_alcohol"] = con.execute(f"""
        SELECT ROUND(100 * AVG(CAST(con_fallecido AS DOUBLE))
                     FILTER (WHERE alcohol_implicado IS NULL), 2),
               ROUND(100 * AVG(CAST(con_fallecido AS DOUBLE))
                     FILTER (WHERE alcohol_implicado), 2)
        FROM vw_colision
        WHERE {CULPABLE_CONDUCTOR}""").fetchone()
    c["pct_fallecido_por_tipo_colision"] = pares(con, f"""
        SELECT t.etiqueta, {PCT_FALLECIDO}
        FROM vw_colision v
        JOIN tipo_colision t USING (tipo_colision_id)
        WHERE {CULPABLE_CONDUCTOR}
        GROUP BY t.tipo_colision_id, t.etiqueta
        ORDER BY t.tipo_colision_id""")

    c["pct_edad_faltante_con_fuga"], c["pct_edad_faltante_sin_fuga"] = con.execute(f"""
        SELECT ROUND(100 * AVG(CAST(edad_conductor_culpable IS NULL AS DOUBLE))
                     FILTER (WHERE hubo_fuga), 1),
               ROUND(100 * AVG(CAST(edad_conductor_culpable IS NULL AS DOUBLE))
                     FILTER (WHERE NOT hubo_fuga), 1)
        FROM vw_colision
        WHERE {CULPABLE_CONDUCTOR}""").fetchone()

    c["pct_con_coordenadas"] = uno(con, """
        SELECT ROUND(100 * AVG(CAST(tiene_coordenadas AS DOUBLE)), 1) FROM vw_colision""")
    c["pct_con_coordenadas_por_anio"] = pares(con, """
        SELECT anio, ROUND(100 * AVG(CAST(tiene_coordenadas AS DOUBLE)), 1)
        FROM vw_colision GROUP BY 1 ORDER BY 1""")
    return c


def main():
    with conectar_lago() as con:
        cifras = calcular(con)
    CIFRAS.parent.mkdir(exist_ok=True)
    CIFRAS.write_text(json.dumps(cifras, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Cifras guardadas en {CIFRAS}")


if __name__ == "__main__":
    main()
