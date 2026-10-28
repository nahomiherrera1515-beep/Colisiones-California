"""
Crea el esquema en tercera forma normal: catálogos, el núcleo colision, parte y
victima, sus subtipos 1:0..1 y las tablas puente de los grupos repetidos.

Nada que se pueda calcular se guarda; eso vive en las vistas de 04.

Las llaves del núcleo van en comentarios y no se declaran. En DuckDB cada
PRIMARY KEY o FOREIGN KEY crea un índice que, con millones de filas, pesa más
que los propios datos y no acelera las consultas que hacemos.
"""

from catalogos import EXTRAS
from configuracion import BASE, conectar


def crear_catalogos_base(con):
    con.execute("""
        CREATE TABLE kabco (
            kabco            VARCHAR PRIMARY KEY,
            nivel            UTINYINT NOT NULL UNIQUE,   -- 0 (O) a 4 (K)
            etiqueta         VARCHAR NOT NULL,
            severidad_fuente VARCHAR NOT NULL UNIQUE     -- valor de collision_severity
        )
    """)
    con.execute("""
        CREATE TABLE mes (
            mes       UTINYINT PRIMARY KEY,
            nombre    VARCHAR NOT NULL,
            trimestre UTINYINT NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE dia_semana (
            dia_semana    UTINYINT PRIMARY KEY,   -- 1 lunes a 7 domingo (ISO)
            nombre        VARCHAR NOT NULL,
            es_fin_semana BOOLEAN NOT NULL
        )
    """)


def crear_catalogos_de_codigos(con):
    for nombre, extras in EXTRAS.items():
        columnas_extra = "".join(f",\n                {col} {tipo}" for col, tipo in extras)
        con.execute(f"""
            CREATE TABLE {nombre} (
                {nombre}_id UTINYINT PRIMARY KEY,
                codigo      VARCHAR UNIQUE,      -- valor literal de la fuente, NULL en el id 0
                etiqueta    VARCHAR NOT NULL,
                orden       UTINYINT NOT NULL{columnas_extra}
            )
        """)


def crear_catalogos_geograficos(con):
    # condado_id es el código oficial del estado (01 Alameda a 58 Yuba).
    con.execute("""
        CREATE TABLE condado (
            condado_id UTINYINT PRIMARY KEY,
            codigo     VARCHAR UNIQUE,   -- nombre tal como aparece en la fuente
            nombre     VARCHAR NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE rango_poblacion (
            rango_poblacion_id UTINYINT PRIMARY KEY,
            codigo             VARCHAR UNIQUE,
            etiqueta           VARCHAR NOT NULL,
            orden              UTINYINT NOT NULL
        )
    """)
    # county_city_location determina el condado y el rango de población de la
    # ciudad. Esa dependencia queda aquí y no en colision.
    con.execute("""
        CREATE TABLE ubicacion (
            ubicacion_id       USMALLINT PRIMARY KEY,   -- county_city_location como entero
            condado_id         UTINYINT NOT NULL REFERENCES condado (condado_id),
            rango_poblacion_id UTINYINT NOT NULL REFERENCES rango_poblacion (rango_poblacion_id)
        )
    """)
    con.execute("""
        CREATE TABLE poblacion_condado (
            condado_id UTINYINT NOT NULL REFERENCES condado (condado_id),
            anio       USMALLINT NOT NULL,
            habitantes INTEGER NOT NULL,   -- estimación del Census Bureau al 1 de julio
            PRIMARY KEY (condado_id, anio)
        )
    """)


def crear_catalogos_construidos(con):
    con.execute("""
        CREATE TABLE banda_edad (
            banda_edad_id UTINYINT PRIMARY KEY,
            etiqueta      VARCHAR NOT NULL UNIQUE,
            edad_min      UTINYINT,
            edad_max      UTINYINT
        )
    """)
    # Estos dos se arman desde la fuente porque tienen miles de valores.
    con.execute("""
        CREATE TABLE marca_vehiculo (
            marca_vehiculo_id USMALLINT PRIMARY KEY,
            codigo            VARCHAR UNIQUE   -- texto de la fuente, NULL en el id 0
        )
    """)
    con.execute("""
        CREATE TABLE infraccion_vehicular (
            infraccion_vehicular_id USMALLINT PRIMARY KEY,
            seccion                 INTEGER NOT NULL,   -- sección del California Vehicle Code
            inciso                  VARCHAR,            -- letra o número del inciso
            UNIQUE (seccion, inciso)
        )
    """)


def crear_nucleo(con):
    con.execute("""
        CREATE TABLE colision (
            case_id                 INTEGER NOT NULL,     -- PK
            fecha                   DATE NOT NULL,
            hora                    TIME,                 -- NULL = hora desconocida
            ubicacion_id            USMALLINT NOT NULL,   -- FK ubicacion
            jurisdiccion            USMALLINT,            -- agencia que levantó el parte
            iluminacion_id          UTINYINT NOT NULL,    -- FK iluminacion
            superficie_id           UTINYINT NOT NULL,    -- FK superficie
            dispositivo_control_id  UTINYINT NOT NULL,    -- FK dispositivo_control
            tipo_colision_id        UTINYINT NOT NULL,    -- FK tipo_colision
            implicado_con_id        UTINYINT NOT NULL,    -- FK implicado_con
            factor_primario_id      UTINYINT NOT NULL,    -- FK factor_primario
            categoria_infraccion_id UTINYINT NOT NULL,    -- FK categoria_infraccion
            infraccion_vehicular_id USMALLINT,            -- FK infraccion_vehicular
            fuga_id                 UTINYINT NOT NULL,    -- FK fuga
            accion_peaton_id        UTINYINT NOT NULL,    -- FK accion_peaton
            en_interseccion         BOOLEAN,
            vehiculo_remolcado      BOOLEAN,
            carretera_estatal       BOOLEAN,
            condicion_especial      BOOLEAN
        )
    """)
    # Si la fila existe, la colisión tiene coordenadas o datos de Caltrans.
    con.execute("""
        CREATE TABLE colision_geo (
            case_id  INTEGER NOT NULL,         -- PK, FK colision
            latitud  DECIMAL(8, 5) NOT NULL,   -- la fuente trae hasta 5 decimales
            longitud DECIMAL(8, 5) NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE colision_carretera (
            case_id               INTEGER NOT NULL,    -- PK, FK colision
            condado_caltrans_id   UTINYINT NOT NULL,   -- FK condado
            distrito_caltrans     UTINYINT,
            ruta_estatal          USMALLINT,
            prefijo_postmile      VARCHAR,
            postmile              DECIMAL(6, 3),
            tipo_ubicacion_id     UTINYINT NOT NULL,   -- FK tipo_ubicacion
            sentido_id            UTINYINT NOT NULL,   -- FK sentido
            rampa_interseccion_id UTINYINT             -- FK rampa_interseccion
        )
    """)
    con.execute("""
        CREATE TABLE parte (
            case_id                       INTEGER NOT NULL,    -- PK, FK colision
            numero_parte                  UTINYINT NOT NULL,   -- PK
            tipo_parte_id                 UTINYINT NOT NULL,   -- FK tipo_parte
            culpable                      BOOLEAN NOT NULL,
            sexo_id                       UTINYINT NOT NULL,   -- FK sexo
            edad                          UTINYINT,
            edad_en_cuarentena            BOOLEAN NOT NULL,
            raza_id                       UTINYINT NOT NULL,   -- FK raza
            sobriedad_id                  UTINYINT NOT NULL,   -- FK sobriedad
            droga_fisica_id               UTINYINT NOT NULL,   -- FK droga_fisica
            direccion_id                  UTINYINT NOT NULL,   -- FK direccion
            movimiento_previo_id          UTINYINT NOT NULL,   -- FK movimiento_previo
            tipo_vehiculo_id              UTINYINT NOT NULL,   -- FK tipo_vehiculo
            anio_vehiculo                 USMALLINT,
            anio_vehiculo_en_cuarentena   BOOLEAN NOT NULL,
            marca_vehiculo_id             USMALLINT NOT NULL,  -- FK marca_vehiculo
            vehiculo_chp_id               UTINYINT NOT NULL,   -- FK vehiculo_chp
            remolque_chp_id               UTINYINT NOT NULL,   -- FK vehiculo_chp
            responsabilidad_financiera_id UTINYINT NOT NULL,   -- FK responsabilidad_financiera
            uso_celular_id                UTINYINT NOT NULL,   -- FK uso_celular
            materiales_peligrosos         BOOLEAN,             -- TRUE o NULL
            relacion_bus_escolar          BOOLEAN,             -- TRUE o NULL
            otra_infraccion_categoria_id  UTINYINT,            -- FK otra_infraccion_categoria
            otra_infraccion_vehicular_id  USMALLINT            -- FK infraccion_vehicular
        )
    """)
    # La fuente no numera las víctimas; numero_victima se asigna al cargar.
    con.execute("""
        CREATE TABLE victima (
            case_id            INTEGER NOT NULL,    -- PK, FK parte
            numero_parte       UTINYINT NOT NULL,   -- PK, FK parte
            numero_victima     UTINYINT NOT NULL,   -- PK
            rol_victima_id     UTINYINT NOT NULL,   -- FK rol_victima
            sexo_id            UTINYINT NOT NULL,   -- FK sexo
            edad               UTINYINT,
            edad_en_cuarentena BOOLEAN NOT NULL,
            lesion_id          UTINYINT NOT NULL,   -- FK lesion
            asiento_id         UTINYINT NOT NULL,   -- FK asiento
            eyeccion_id        UTINYINT NOT NULL    -- FK eyeccion
        )
    """)


def crear_tablas_puente(con):
    # Una fila por cada posición (1 o 2) que la fuente llenó.
    con.execute("""
        CREATE TABLE colision_clima (
            case_id  INTEGER NOT NULL,    -- PK, FK colision
            orden    UTINYINT NOT NULL,   -- PK
            clima_id UTINYINT NOT NULL    -- FK clima
        )
    """)
    con.execute("""
        CREATE TABLE colision_condicion_via (
            case_id          INTEGER NOT NULL,    -- PK, FK colision
            orden            UTINYINT NOT NULL,   -- PK
            condicion_via_id UTINYINT NOT NULL    -- FK condicion_via
        )
    """)
    con.execute("""
        CREATE TABLE parte_equipo_seguridad (
            case_id             INTEGER NOT NULL,    -- PK, FK parte
            numero_parte        UTINYINT NOT NULL,   -- PK, FK parte
            orden               UTINYINT NOT NULL,   -- PK
            equipo_seguridad_id UTINYINT NOT NULL    -- FK equipo_seguridad
        )
    """)
    con.execute("""
        CREATE TABLE parte_factor_asociado (
            case_id            INTEGER NOT NULL,    -- PK, FK parte
            numero_parte       UTINYINT NOT NULL,   -- PK, FK parte
            orden              UTINYINT NOT NULL,   -- PK
            factor_asociado_id UTINYINT NOT NULL    -- FK factor_asociado
        )
    """)
    con.execute("""
        CREATE TABLE victima_equipo_seguridad (
            case_id             INTEGER NOT NULL,    -- PK, FK victima
            numero_parte        UTINYINT NOT NULL,   -- PK, FK victima
            numero_victima      UTINYINT NOT NULL,   -- PK, FK victima
            orden               UTINYINT NOT NULL,   -- PK
            equipo_seguridad_id UTINYINT NOT NULL    -- FK equipo_seguridad
        )
    """)


def main():
    for ruta in (BASE, BASE.with_suffix(".duckdb.wal")):
        ruta.unlink(missing_ok=True)

    with conectar() as con:
        crear_catalogos_base(con)
        crear_catalogos_de_codigos(con)
        crear_catalogos_geograficos(con)
        crear_catalogos_construidos(con)
        crear_nucleo(con)
        crear_tablas_puente(con)
    print(f"Esquema creado en {BASE.name}")


if __name__ == "__main__":
    main()
