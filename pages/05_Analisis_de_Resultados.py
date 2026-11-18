"""Análisis de los Resultados de la investigacion"""
import duckdb
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# configuracion inicial de la pagina de los resultados
st.set_page_config(page_title="Análisis de los Resultados", page_icon="📊", layout="wide")

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
            -- Temporalmente en 0 para evitar el error de "poblacion"
            0 AS tasa_100k 
        FROM colisiones_normalizada.vw_colision v
        LEFT JOIN colisiones_normalizada.condado c ON v.condado_id = c.condado_id
        WHERE v.anio BETWEEN 2010 AND 2019
        GROUP BY 1
        ORDER BY total_colisiones DESC;
    """
    return conn.execute(query).df()

# Consulta para el objetivo 2



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
    sub_tab_temp, sub_tab_geo = st.tabs(["🕒 Análisis Temporal", "🗺️ Análisis por Condado"])
    
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
            st.success("Patrones temporales cargados exitosamente.")
            
            # Tabla desplegable temporal
            with st.expander(f"Ver tabla de frecuencias — {dim_temporal}"):
                tabla_temp = df_sub_temp[["categoria", "total_colisiones"]].rename(
                    columns={"categoria": dim_temporal, "total_colisiones": "Total de Colisiones"}
                )
                st.dataframe(tabla_temp, use_container_width=True, hide_index=True)
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
            st.success("Datos geográficos cargados exitosamente.")
            
            with st.expander("Ver tabla completa de condados (Tasas y Conteos)"):
                tabla_geo = df_obj1_geo.rename(columns={
                    "condado": "Condado", 
                    "total_colisiones": "Total de Colisiones",
                    "tasa_100k": "Tasa (100k habs)"
                })
                st.dataframe(tabla_geo, use_container_width=True, hide_index=True)
        else:
            st.warning("No se encontraron registros geográficos.")

# Pestaña 2: Objetivo 2
with tab_obj2:
  st.info("Espacio reservado para la Edad del Conductor y Alcohol.")

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
    st.success("Se han cargado los registros exitosamente.")

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
        st.success("Se han cargado los registros exitosamente.") # Mensaje de exito porque se ve bien :)

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
    else:
        st.warning("No se encontraron registros en la consulta.") # Mensaje con el 
        #mismo objetivo que el anterior