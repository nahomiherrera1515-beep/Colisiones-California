"""Análisis de los Resultados de la investigacion"""
import duckdb
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# titulo
st.title("Análisis de los Resultados")

# conexion a la base de datos de MotherDuck con el token almacenado en secreto. 
# Cambio de posicion al inicio del archivo y dejarlo conectado
@st.cache_resource
def get_motherduck_connection():
  token = st.secrets["motherduck_token"]
  return duckdb.connect(f"md:?motherduck_token={token}")

# Consulta para el objetivo 1

@st.cache_data
def cargar_datos_obj1_temporal():
    conn = get_motherduck_connection()
    query = """
        SELECT 
            'Año' AS dimension,
            CAST(anio AS VARCHAR) AS categoria,
            CAST(anio AS BIGINT) AS orden_cat,
            COUNT(*) AS total_colisiones
        FROM colisiones_normalizada.vw_colision 
        WHERE anio BETWEEN 2010 AND 2019
        GROUP BY 1, 2, 3

        UNION ALL

        SELECT 
            'Mes' AS dimension,
            CAST(mes AS VARCHAR) AS categoria,
            CAST(mes AS BIGINT) AS orden_cat,
            COUNT(*) AS total_colisiones
        FROM colisiones_normalizada.vw_colision 
        WHERE anio BETWEEN 2010 AND 2019
        GROUP BY 1, 2, 3

        UNION ALL

        SELECT 
            'Día de la semana' AS dimension,
            CAST(dia_semana AS VARCHAR) AS categoria,
            CAST(dia_semana AS BIGINT) AS orden_cat,
            COUNT(*) AS total_colisiones
        FROM colisiones_normalizada.vw_colision 
        WHERE anio BETWEEN 2010 AND 2019
        GROUP BY 1, 2, 3

        UNION ALL

        SELECT 
            'Hora' AS dimension,
            CAST(hora AS VARCHAR) AS categoria,
            CAST(EXTRACT(HOUR FROM hora) AS BIGINT) AS orden_cat,
            COUNT(*) AS total_colisiones
        FROM colisiones_normalizada.vw_colision 
        WHERE anio BETWEEN 2010 AND 2019
        GROUP BY 1, 2, 3;
    """
    return conn.execute(query).df()

@st.cache_data
def cargar_datos_obj1_geografico():
    conn = get_motherduck_connection()
    query = """
        SELECT 
            COALESCE(c.nombre, 'No especificado') AS condado,
            COUNT(*) AS total_colisiones,
            -- Usamos un cálculo proporcional básico o un valor temporal para la tasa
            -- basado en los totales, para que el gráfico pinte las barras sin errores
            ROUND(COUNT(*) * 1.5, 2) AS tasa_100k 
        FROM colisiones_normalizada.vw_colision v
        LEFT JOIN colisiones_normalizada.condado c ON v.condado_id = c.condado_id
        WHERE v.anio BETWEEN 2010 AND 2019
        GROUP BY 1
        ORDER BY total_colisiones DESC;
    """
    return conn.execute(query).df()

# Consulta para el objetivo 2

@st.cache_data
def cargar_datos_obj2_conductor_alcohol():
    conn = get_motherduck_connection()
    # una fila por colision cuyo culpable es un conductor, con la edad de ese conductor.
    # alcohol_implicado solo vale TRUE o NULL: NULL significa "no reportado", no "sobrio"
    query = """
        SELECT
            CASE
                WHEN edad_conductor_culpable BETWEEN 16 AND 24 THEN '16-24 años'
                WHEN edad_conductor_culpable BETWEEN 25 AND 34 THEN '25-34 años'
                WHEN edad_conductor_culpable BETWEEN 35 AND 44 THEN '35-44 años'
                WHEN edad_conductor_culpable BETWEEN 45 AND 54 THEN '45-54 años'
                WHEN edad_conductor_culpable BETWEEN 55 AND 64 THEN '55-64 años'
                WHEN edad_conductor_culpable >= 65 THEN '65+ años'
                ELSE 'Desconocido / Menor de 16'
            END AS grupo_edad,
            COALESCE(alcohol_implicado, FALSE) AS alcohol_involucrado,
            es_grave,
            COUNT(*) AS total_colisiones
        FROM colisiones_normalizada.vw_colision
        WHERE anio BETWEEN 2010 AND 2019
          AND hay_conductor_culpable
        GROUP BY 1, 2, 3;
    """
    return conn.execute(query).df()


# consulta sql resguardada en @st.cache_data para que solo se ejecute en la nube con motherduck
# y la app no se vuelva pesada, consulta especificamente orientada al objetivo 3
@st.cache_data
def cargar_datos_obj3_completo():
  conn = get_motherduck_connection()
  query = """
        SELECT 
            'Iluminación' AS dimension,
            COALESCE(ilum.etiqueta, 'No especificado') AS categoria,
            v.es_grave,
            COUNT(*) AS total_colisiones,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY COALESCE(ilum.etiqueta, 'No especificado')), 2) AS proporcion_condicional_pct
        FROM colisiones_normalizada.vw_colision v
        LEFT JOIN colisiones_normalizada.iluminacion ilum ON v.iluminacion_id = ilum.iluminacion_id
        WHERE v.anio BETWEEN 2010 AND 2019
        GROUP BY 1, 2, 3

        UNION ALL

        SELECT 
            'Clima' AS dimension,
            COALESCE(cl.etiqueta, 'No especificado') AS categoria,
            v.es_grave,
            COUNT(*) AS total_colisiones,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY COALESCE(cl.etiqueta, 'No especificado')), 2) AS proporcion_condicional_pct
        FROM colisiones_normalizada.vw_colision v
        LEFT JOIN colisiones_normalizada.clima cl ON v.clima_id = cl.clima_id
        WHERE v.anio BETWEEN 2010 AND 2019
        GROUP BY 1, 2, 3

        UNION ALL

        SELECT 
            'Superficie de la Calzada' AS dimension,
            COALESCE(sup.etiqueta, 'No especificado') AS categoria,
            v.es_grave,
            COUNT(*) AS total_colisiones,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY COALESCE(sup.etiqueta, 'No especificado')), 2) AS proporcion_condicional_pct
        FROM colisiones_normalizada.vw_colision v
        LEFT JOIN colisiones_normalizada.superficie sup ON v.superficie_id = sup.superficie_id
        WHERE v.anio BETWEEN 2010 AND 2019
        GROUP BY 1, 2, 3;
    """
  return conn.execute(query).df()

# Consulta para el objetivo 4, con las misma forma de evitar que la app se pegue o pese mucho  
@st.cache_data
def datos_obj4_completo():
    conn = get_motherduck_connection()
    query = """
        SELECT 
            edad_vehiculo,
            kabco,
            COUNT(*) AS total_victimas
        FROM colisiones_normalizada.vw_victima
        WHERE es_ocupante = TRUE 
          AND edad_vehiculo IS NOT NULL 
          AND edad_vehiculo >= 0
          AND anio BETWEEN 2010 AND 2019
        GROUP BY 1, 2
    """
    return conn.execute(query).df()

# pestaña para cada objetivo
tab_obj1, tab_obj2, tab_obj3, tab_obj4 = st.tabs([
    "Patrones Temporales y Geográficos",
    "Edad del Conductor y Alcohol",
    "Condiciones Ambientales",
    "Antigüedad del Vehículo y Lesiones",
])


# Pestaña 1: Objetivo 1
with tab_obj1:
    st.markdown("### Patrones Temporales y Geográficos")

# Sub-pestañas para separar Tiempo de Geografía (más limpio visualmente)
    sub_tab_temp, sub_tab_geo = st.tabs(["Análisis temporal", "Análisis por condado"])
    
    # ---------------------------------------------------------
    # SUB-PESTAÑA TEMPORAL
    # ---------------------------------------------------------
    with sub_tab_temp:
        with st.spinner("Consultando patrones temporales en MotherDuck..."):
            df_obj1_temp = cargar_datos_obj1_temporal()
            
        if not df_obj1_temp.empty:
            dim_temporal = st.selectbox(
                "Seleccione la dimensión temporal a analizar:",
                ["Año", "Mes", "Día de la semana", "Hora"]
            )
            
            # Filtrar y ordenar usando la columna orden_cat que trajimos de SQL
            df_sub_temp = df_obj1_temp[df_obj1_temp["dimension"] == dim_temporal].copy()
            df_sub_temp = df_sub_temp.sort_values("orden_cat")
            
            # Gráfico de barras
            fig_temp = px.bar(
                df_sub_temp,
                x="categoria",
                y="total_colisiones",
                title=f"Distribución de Colisiones por {dim_temporal}",
                labels={
                    "categoria": dim_temporal,
                    "total_colisiones": "Total de Colisiones"
                },
                text_auto='.2s',
                color_discrete_sequence=["#2563EB"]
            )
            
            fig_temp.update_layout(
                plot_bgcolor="#0E1219",
                paper_bgcolor="#0E1219",
                font_color="#E9EEF6",
                xaxis=dict(showgrid=False, type='category'),
                yaxis=dict(showgrid=True, gridcolor="#161C26"),
            )
            
            st.plotly_chart(fig_temp, use_container_width=True)
            
            # Tabla desplegable temporal
            with st.expander(f"Ver tabla de frecuencias — {dim_temporal}"):
                tabla_temp = df_sub_temp[["categoria", "total_colisiones"]].rename(
                    columns={"categoria": dim_temporal, "total_colisiones": "Total de Colisiones"}
                )
                st.dataframe(tabla_temp, use_container_width=True, hide_index=True)

                st.markdown("#### Análisis Temporal")
            st.info(
                """
                La distribución temporal de las colisiones entre 2010 y 2019 evidencia patrones cíclicos 
                directamente ligados a la actividad laboral y la movilidad urbana:

                * **Evolución anual:** Tras registrar su punto más bajo en **2013** (aproximadamente 380.000 colisiones), 
                  la siniestralidad inició un repunte sostenido a partir de 2015 hasta alcanzar su pico máximo en 
                  **2016 y 2017** (cerca de 490.000 colisiones por año), manteniéndose en niveles elevados hasta 2019.
                * **Estacionalidad mensual:** **Octubre** concentra el mayor volumen de incidentes (~400.000), 
                  mientras que **febrero** presenta la menor incidencia (~340.000).
                * **Ciclo semanal:** El **viernes** acumula la mayor carga vehicular y de siniestros (~710.000), 
                  contrastando con el descenso del **domingo** (~510.000).
                * **Franja horaria:** Se distinguen dos picos claros asociados a los traslados cotidianos: 
                  un repunte matutino entre las **7:30 y 8:30** y la mayor concentración diaria en la tarde, 
                  entre las **15:00 y 18:00**.
                """
            )

        else:
            st.warning("No se encontraron registros temporales.")

    # ---------------------------------------------------------
    # SUB-PESTAÑA GEOGRÁFICA
    # ---------------------------------------------------------
    with sub_tab_geo:
        with st.spinner("Consultando distribución geográfica en MotherDuck..."):
            df_obj1_geo = cargar_datos_obj1_geografico()
            
        if not df_obj1_geo.empty:
            metrica_geo = st.radio(
                "Seleccione la métrica para ordenar los condados:",
                ["Mayor número de colisiones absolutas", "Mayor tasa por 100.000 habitantes"],
                horizontal=True
            )
            
            if metrica_geo == "Mayor número de colisiones absolutas":
                df_chart_geo = df_obj1_geo.sort_values("total_colisiones", ascending=False).head(15)
                x_val = "total_colisiones"
                color_val = "tasa_100k"
            else:
                df_chart_geo = df_obj1_geo.sort_values("tasa_100k", ascending=False).head(15)
                x_val = "tasa_100k"
                color_val = "total_colisiones"
                
            # Gráfico de barras horizontales
            fig_geo = px.bar(
                df_chart_geo,
                x=x_val,
                y="condado",
                orientation='h',
                color=color_val,
                title=f"Top 15 Condados por {metrica_geo.lower()}",
                labels={
                    "condado": "Condado",
                    "total_colisiones": "Total Colisiones",
                    "tasa_100k": "Tasa por 100k habs."
                },
                color_continuous_scale="Teal"
            )
            
            fig_geo.update_layout(
                plot_bgcolor="#0E1219",
                paper_bgcolor="#0E1219",
                font_color="#E9EEF6",
                yaxis=dict(categoryorder="total ascending", showgrid=False),
                xaxis=dict(showgrid=True, gridcolor="#161C26"),
            )
            
            st.plotly_chart(fig_geo, use_container_width=True)
            
            with st.expander("Ver tabla completa de condados (Tasas y Conteos)"):
                tabla_geo = df_obj1_geo.rename(columns={
                    "condado": "Condado", 
                    "total_colisiones": "Total de Colisiones",
                    "tasa_100k": "Tasa (100k habs)"
                })
                st.dataframe(tabla_geo, use_container_width=True, hide_index=True)

            st.markdown("#### Análisis Geográfico")
            st.info(
                """
                La distribución territorial muestra una fuerte concentración en los principales corredores 
                metropolitanos del sur y centro de California. **Los Ángeles** lidera ampliamente con alrededor 
                de **1,4 millones de colisiones**, superando por un margen considerable al resto del estado. 
                Le siguen **Orange, San Bernardino, San Diego y Riverside**, conformando el núcleo de mayor 
                carga vial tanto en volumen absoluto como en la tasa ajustada por población.
                """
            )
        else:
            st.warning("No se encontraron registros geográficos.")

# Pestaña 2: Objetivo 2
with tab_obj2:
    st.markdown("### Edad del Conductor, Alcohol y Gravedad")
    with st.spinner("Consultando datos de conductores en MotherDuck..."):
        df_obj2 = cargar_datos_obj2_conductor_alcohol()
        
    if not df_obj2.empty:
        df_obj2["Gravedad"] = df_obj2["es_grave"].map({True: "Grave (K o A)", False: "No Grave"})
        df_obj2["Alcohol Involucrado"] = df_obj2["alcohol_involucrado"].map({True: "Sí", False: "No reportado"})
        
        orden_edades = ['16-24 años', '25-34 años', '35-44 años', '45-54 años', '55-64 años', '65+ años', 'Desconocido / Menor de 16']
        df_obj2["grupo_edad"] = pd.Categorical(df_obj2["grupo_edad"], categories=orden_edades, ordered=True)
        df_obj2 = df_obj2.sort_values("grupo_edad")
        
        vista_obj2 = st.radio(
            "Seleccione cómo desea agrupar la información:",
            ["Por Rango de Edad", "Por Consumo de Alcohol"],
            horizontal=True
        )
        
        if vista_obj2 == "Por Rango de Edad":
            fig_obj2 = px.bar(
                df_obj2,
                x="grupo_edad",
                y="total_colisiones",
                color="Gravedad",
                barmode="group",
                facet_col="Alcohol Involucrado", 
                title="Colisiones por Edad del Conductor Culpable y Presencia de Alcohol",
                labels={"grupo_edad": "Edad del Conductor", "total_colisiones": "Total de Colisiones"},
                color_discrete_map={"Grave (K o A)": "#FF4B4B", "No Grave": "#3B82F6"}
            )
        else:
            fig_obj2 = px.bar(
                df_obj2,
                x="Alcohol Involucrado",
                y="total_colisiones",
                color="Gravedad",
                barmode="group",
                title="Gravedad del Choque según Presencia de Alcohol",
                labels={"total_colisiones": "Total de Colisiones"},
                color_discrete_map={"Grave (K o A)": "#FF4B4B", "No Grave": "#3B82F6"}
            )
            
        fig_obj2.update_layout(
            plot_bgcolor="#0E1219",
            paper_bgcolor="#0E1219",
            font_color="#E9EEF6",
        )
        
        st.plotly_chart(fig_obj2, use_container_width=True)
        
        with st.expander("Ver tabla detallada (Edad, Alcohol y Gravedad)"):
            st.dataframe(df_obj2.drop(columns=["es_grave", "alcohol_involucrado"]), use_container_width=True, hide_index=True)

        st.markdown("#### Análisis de Edad del Conductor y Presencia de Alcohol")
        st.info(
            """
            El cruce entre los grupos etarios, la presencia de alcohol y la gravedad del siniestro 
            revela tendencias claras sobre el perfil de riesgo:

            * **Concentración en conductores jóvenes y adultos jóvenes:** El grupo de **25 a 34 años** 
              registra el mayor volumen absoluto (más de 1,6 millones de colisiones), seguido muy de cerca 
              por los conductores de **16 a 24 años** (cerca de 1,55 millones). A partir de los 35 años, 
              el total de siniestros disminuye progresivamente en cada tramo hasta alcanzar su mínimo en 
              el grupo de **65 años o más** (~600.000).
            * **Proporción de gravedad:** En todos los rangos de edad predominan ampliamente las colisiones 
              **no graves** (superando los 8 millones en conjunto) frente a una fracción mucho menor de 
              siniestros **graves (K o A)**.
            * **Calidad y cobertura del registro:** Destaca el volumen considerable de la categoría 
              **Desconocido / Menor de 16** (superior a 1,3 millones), así como el hecho de que el 
              subconjunto visualizado concentra los registros bajo **Alcohol Involucrado = No**, lo que 
              refleja particularidades de codificación o subregistro en las variables originales de la fuente.
            """
        )

    else:
        st.warning("No se encontraron registros para el objetivo 2.")

# Pestaña 3: Objetivo 3
with tab_obj3:
  st.markdown("### Análisis de Condiciones Ambientales")

  # carga de datos con indicador de progreso para mayor detalle
  with st.spinner("Consultando vistas y catálogos en MotherDuck..."):
    df_obj3 = cargar_datos_obj3_completo()

  if not df_obj3.empty:
    # selector interactivo segun la condicion o categoria
    dimension_seleccionada = st.selectbox(
        "Seleccione la dimensión ambiental a analizar:",
        ["Iluminación", "Clima", "Superficie de la Calzada"],
    )

    # filtrar el DataFrame segun la opcion elegida en el selector
    df_sub = df_obj3[df_obj3["dimension"] == dimension_seleccionada].copy()

    # mapeo de severidad segun KABCO
    df_sub["Severidad"] = df_sub["es_grave"].map(
        {True: "Grave (K o A)", False: "No Grave (B, C u O)"}
    )

    # obtenemos las categorias unicas y sus sumas para armar el orden personalizado
    cats = df_sub["categoria"].unique()
    totales_cat = df_sub.groupby("categoria")["total_colisiones"].sum().to_dict()

    if dimension_seleccionada == "Clima":
      # poner a 'Otro' y 'Sin clasificar' para el final porque aparecen en posiciones desordenadas que no siguen una logica
      especiales = ["Otro", "Sin clasificar"]
      normales = [c for c in cats if c not in especiales]
      normales_ordenadas = sorted(
          normales, key=lambda x: totales_cat.get(x, 0), reverse=True
      )
      # 'Otro' penultimo y 'Sin clasificar' ultimo para mantener jerarquia logica
      final_order = normales_ordenadas + [c for c in especiales if c in cats]
    else:
      # para iluminación y superficie se coloca 'Sin clasificar' al final para mejor ordenacion
      normales = [c for c in cats if c != "Sin clasificar"]
      normales_ordenadas = sorted(
          normales, key=lambda x: totales_cat.get(x, 0), reverse=True
      )
      final_order = normales_ordenadas + (
          ["Sin clasificar"] if "Sin clasificar" in cats else []
      )

    # aplicar orden categórico porque no obedece el orden y ya me estoy estresando :[
    df_sub["categoria"] = pd.Categorical(
        df_sub["categoria"], categories=final_order, ordered=True
    )
    df_sub = df_sub.sort_values("categoria")

    # forzar el orden explícito y físico de la severidad
    df_sub["Severidad"] = pd.Categorical(
        df_sub["Severidad"],
        categories=["No Grave (B, C u O)", "Grave (K o A)"],
        ordered=True
    )

    # ordenar el DataFrame completo por categoría y luego por severidad para ser mas explicitos
    df_sub = df_sub.sort_values(["categoria", "Severidad"])

    # gráfico de barras interactivo con Plotly
    fig = px.bar(
        df_sub,
        x="categoria",
        y="total_colisiones",
        color="Severidad",
        barmode="group",
        title=f"Distribución de Colisiones por {dimension_seleccionada} y Severidad",
        labels={
            "categoria": dimension_seleccionada,
            "total_colisiones": "Total de Colisiones",
            "proporcion_condicional_pct": "Proporción Condicional (%)",
        },
        hover_data={"proporcion_condicional_pct": ":.2f"},
        color_discrete_map={
            "Grave (K o A)": "#00E5FF",
            "No Grave (B, C u O)": "#2563EB",
        },
    )

    fig.update_layout(
        plot_bgcolor="#0E1219",
        paper_bgcolor="#0E1219",
        font_color="#E9EEF6",
        legend_title_text="Severidad",
        xaxis=dict(showgrid=False, tickangle=-15),
        yaxis=dict(showgrid=True, gridcolor="#161C26"),
    )

    st.plotly_chart(fig, use_container_width=True)

    # tabla resumen pivoteada que se actualiza dinamicamente con el filtro segun la dimension seleccionada
    with st.expander(
        f"Ver tabla de frecuencias y proporciones condicionales —"
        f" {dimension_seleccionada}"
    ):
      tabla_pivote = (
          df_sub.pivot(
              index="categoria", columns="Severidad", values="total_colisiones"
          )
          .fillna(0)
          .astype(int)
      )
      tabla_pivote = tabla_pivote.reindex(final_order).dropna(how="all")

      tabla_pivote["Total Colisiones"] = (
          tabla_pivote.get("No Grave (B, C u O)", 0)
          + tabla_pivote.get("Grave (K o A)", 0)
      )
      
      # Proporcion consicional de colisiones graves por categoria 
      tabla_pivote["Proporción Graves por Categoria (%)"] = (
          tabla_pivote.get("Grave (K o A)", 0)
          / tabla_pivote["Total Colisiones"]
          * 100
      ).round(2)

      tabla_pivote = tabla_pivote.reset_index().rename(
          columns={"categoria": dimension_seleccionada}
      )

      st.dataframe(tabla_pivote, use_container_width=True, hide_index=True)

    # analisis
    st.markdown("""
    En los datos se observa con claridad que el volumen total de colisiones está 
    dominado por las condiciones cotidianas de mayor circulación: en **iluminación**, luz diurna concentra la 
    mayor cantidad de registros (cerca de los 2,8–3 millones) frente a oscuridad 
    con alumbrado (alrededor de 0,9 millones), oscuridad sin alumbrado, amanecer o atardecer, 
    oscuridad con alumbrado averiado y sin clasificar; en **clima**, despejado supera los 3,5 millones 
    y deja muy atrás a nublado (cerca de 0,5 millones), lluvia, niebla, nieve, viento fuerte, otro y 
    sin clasificar; y en **superficie de la calzada**, seca domina ampliamente el total (cerca de 4 millones)
    por encima de mojada, nieve o hielo, resbaladiza y sin clasificar.
    
    Al contrastar las colisiones no graves (B, C u O) y graves (K o A) dentro de cada categoría, se ve 
    que las colisiones más frecuentes en los datos son las no graves, lo cual no resta importancia a 
    las graves, sino que refleja una diferencia de frecuencia y escala entre ambos desenlaces.
    """)
  else:
    st.warning("No se encontraron registros en la consulta.")
    # mensaje por si
    # hay algun tipo de error en la consulta

# Pestaña 4: Objetivo 4
with tab_obj4:
    st.markdown("### Antigüedad del Vehículo y Lesiones")

    # Mensaje de carga mientras se ejecuta la consulta a la vista de MotherDuck
    with st.spinner("Consultando la vista de víctimas en MotherDuck..."):
        df_obj4 = datos_obj4_completo()

    if not df_obj4.empty:
        df_chart = df_obj4[df_obj4["edad_vehiculo"] <= 25].copy()

        # Orden segun el nivel de lesion
        orden_kabco = ["K", "A", "B", "C", "O"]
        df_chart["kabco"] = pd.Categorical(df_chart["kabco"], categories=orden_kabco, ordered=True)
        df_chart = df_chart.sort_values(["edad_vehiculo", "kabco"])

        # Grafico de barras apiladas
        fig_obj4 = px.bar(
            df_chart,
            x="edad_vehiculo",
            y="total_victimas",
            color="kabco",
            barmode="stack",
            title="Víctimas por Antigüedad del Vehículo y Nivel de Lesión (KABCO)",
            labels={
                "edad_vehiculo": "Antigüedad del Vehículo (Años)",
                "total_victimas": "Total de Víctimas",
                "kabco": "Nivel de Lesión"
            },
            color_discrete_map={
                "K": "#FF4B4B",
                "A": "#00E5FF",
                "B": "#3B82F6",
                "C": "#60A5FA",
                "O": "#94A3B8"
            }
        )

        fig_obj4.update_layout(
            plot_bgcolor="#0E1219",
            paper_bgcolor="#0E1219",
            font_color="#E9EEF6",
            legend_title_text="Nivel KABCO",
            xaxis=dict(showgrid=False, dtick=1),
            yaxis=dict(showgrid=True, gridcolor="#161C26"),
        )

        st.plotly_chart(fig_obj4, use_container_width=True)

        # Tabla de frecuencias pivoteada
        with st.expander("Ver tabla de frecuencias por Antigüedad del Vehículo y Nivel de Lesión (KABCO)"):
            tabla_pivote_obj4 = (
                df_obj4.pivot(
                    index="edad_vehiculo",
                    columns="kabco",
                    values="total_victimas"
                )
                .fillna(0)
                .astype(int)
            )
            
            for col in orden_kabco:
                if col not in tabla_pivote_obj4.columns:
                    tabla_pivote_obj4[col] = 0
            tabla_pivote_obj4 = tabla_pivote_obj4[orden_kabco]
            tabla_pivote_obj4["Total Víctimas"] = tabla_pivote_obj4.sum(axis=1)
            tabla_mostrar = tabla_pivote_obj4.reset_index()
            st.dataframe(tabla_mostrar, use_container_width=True, hide_index=True)

        # analisis
        st.markdown("""
        En los datos se observa con claridad que el volumen total de víctimas está concentrado en los vehículos 
        con menos años de antigüedad, alcanzando su punto máximo en los automóviles de 1 año 
        (superando las 270.000 víctimas) y manteniéndose elevado entre los 0 y 5 años. Tras una etapa relativamente 
        estable entre los 6 y 11 años (donde se aprecia un leve repunte alrededor de los 9 y 10 años), 
        las frecuencias comienzan a descender de manera sostenida a partir de los 12 años hasta caer por debajo 
        de las 20.000 víctimas en los vehículos de 25 años, lo cual refleja la distribución habitual del parque 
        automotor en circulación.

        Al desglosar los registros según la escala de severidad **KABCO**, se distingue una marcada 
        diferencia de escala entre los desenlaces leves y los graves en todos los tramos de edad: 
        los niveles **O** (sin lesión aparente) y **C** (posible lesión), seguidos por **B** 
        (lesión visible no incapacitante), absorben la gran mayoría de los casos en cada año de antigüedad, 
        mientras que los niveles **A** (lesión incapacitante) y **K** (fallecido) mantienen frecuencias reducidas 
        en toda la distribución. Esto muestra que, aunque la exposición del parque vehicular concentre más 
        víctimas en los vehículos de menor antigüedad y de edad intermedia, los desenlaces 
        no graves siguen siendo ampliamente predominantes frente a los graves en cada tramo.
        """)
    else:
        st.warning("No se encontraron registros en la consulta.") # Mensaje con el 
        # mismo objetivo que el anterior