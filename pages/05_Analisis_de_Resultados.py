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

# Consulta para el objetivo 1

# Consulta para el objetivo 2

# conexion a la base de datos de MotherDuck con el token almacenado en secreto. Objetivo 3
@st.cache_resource
def get_motherduck_connection():
  token = st.secrets["motherduck_token"]
  return duckdb.connect(f"md:?motherduck_token={token}")

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

# Consulta para el objetivo 4

# pestaña para cada objetivo
tab_obj1, tab_obj2, tab_obj3, tab_obj4 = st.tabs([
    "Patrones Temporales y Geográficos",
    "Edad del Conductor y Alcohol",
    "Condiciones Ambientales",
    "Antigüedad del Vehículo y Lesiones",
])

# Pestaña 1: Objetivo 1
with tab_obj1:
  st.info("Espacio reservado para Patrones Temporales y Geográficos.")

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

    # aplicar orden categórico porque no obedece el orden
    df_sub["categoria"] = pd.Categorical(
        df_sub["categoria"], categories=final_order, ordered=True
    )
    df_sub = df_sub.sort_values("categoria")

    # 1. Forzar el orden explícito y físico de la severidad
    df_sub["Severidad"] = pd.Categorical(
        df_sub["Severidad"],
        categories=["No Grave (B, C u O)", "Grave (K o A)"],
        ordered=True
    )

    # 2. Ordenar el DataFrame completo por categoría y luego por severidad
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
  st.info("Espacio reservado para Antigüedad del Vehículo y Lesiones.")