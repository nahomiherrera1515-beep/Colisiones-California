"""Análisis de los resultados: los cuatro objetivos de la investigación.

Cada objetivo consulta solo lo que necesita, ya agregado en MotherDuck, y el
resultado queda en caché (datos.consulta). Solo se consulta el objetivo que se
está mirando.
"""

import json
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import estilo
from datos import consulta
from estilo import (ACENTO, AMBAR, AZUL, BORDE, ESCALA, FONDO, GRIS, GRIS_TENUE, REJILLA,
                    ROJO, TEXTO, TEXTO_SUAVE)

BASE = "colisiones_normalizada"
PERIODO = "anio BETWEEN 2010 AND 2019"
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
MESES_LARGOS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                "septiembre", "octubre", "noviembre", "diciembre"]
LOS_ANGELES = 19
TODO_EL_PERIODO = "2010–2019"

estilo.encabezado(
    "Análisis de resultados",
    bajada="Distribución de las colisiones registradas en California entre 2010 y 2019, "
           "organizada según los cuatro objetivos de la investigación. Todas las cifras "
           "describen el universo completo de colisiones.",
    antetitulo="Resultados",
)

OBJETIVOS = ["Tiempo y territorio", "Conductor culpable", "Condiciones del entorno",
             "Vehículo y ocupantes"]
elegido = st.segmented_control("Objetivo", OBJETIVOS, default=OBJETIVOS[0],
                               key="objetivo", label_visibility="collapsed")
objetivo = elegido or OBJETIVOS[0]
st.write("")


def tabla(df, **columnas):
    st.dataframe(df, hide_index=True, width="stretch", column_config=columnas)


def num(etiqueta, formato="localized"):
    return st.column_config.NumberColumn(etiqueta, format=formato)


# ---------------------------------------------------------------------------
# Objetivo 1. Tiempo y territorio
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def geometria():
    ruta = Path(__file__).resolve().parents[1] / "assets" / "california_condados.geojson"
    return json.loads(ruta.read_text(encoding="utf-8"))


def condados_por_anio():
    return consulta(f"""
        SELECT c.condado_id, c.condado, c.anio, c.habitantes, c.colisiones, c.fallecidos,
               g.graves
        FROM {BASE}.vw_condado_anio c
        JOIN (SELECT condado_id, anio, SUM(es_grave::INT) AS graves
              FROM {BASE}.vw_colision WHERE {PERIODO} GROUP BY 1, 2) g
          USING (condado_id, anio)
    """)


METRICAS = {
    "Colisiones por 100.000 hab.": ("tasa", "colisiones por cada 100.000 habitantes"),
    "Fallecidos por 100.000 hab.": ("tasa_fallecidos", "fallecidos por cada 100.000 habitantes"),
    "Colisiones graves (%)": ("pct_graves", "% de colisiones graves (K o A)"),
    "Total de colisiones": ("colisiones", "colisiones"),
}


def resumir_condados(df, anio):
    if anio != TODO_EL_PERIODO:
        df = df[df.anio == anio]
    r = df.groupby(["condado_id", "condado"], as_index=False)[
        ["habitantes", "colisiones", "fallecidos", "graves"]].sum()
    # en el período completo, habitantes suma persona-año: la tasa es un promedio anual
    r["tasa"] = 1e5 * r.colisiones / r.habitantes
    r["tasa_fallecidos"] = 1e5 * r.fallecidos / r.habitantes
    r["pct_graves"] = 100 * r.graves / r.colisiones
    return r


def valor(columna, x):
    if columna == "colisiones":
        return estilo.entero(x)
    if columna == "pct_graves":
        return estilo.porcentaje(x, 2)
    return estilo.decimal(x, 1)


def mapa(r, columna, seleccionado):
    custom = r[["condado", "colisiones", "tasa", "fallecidos", "pct_graves"]].to_numpy()
    # unos pocos condados extremos (como Alpine) aplanarían la escala: se corta en el
    # percentil 95 y los que lo superan se pintan con el color más intenso
    tope = r[columna].quantile(0.95)
    fig = go.Figure(go.Choropleth(
        geojson=geometria(), featureidkey="id", locations=r.condado_id, z=r[columna],
        zmin=r[columna].min(), zmax=tope,
        colorscale=ESCALA, marker_line_color=FONDO, marker_line_width=0.7,
        colorbar=dict(thickness=10, len=0.45, x=0.86, y=0.78, outlinewidth=0,
                      tickfont=dict(color=TEXTO_SUAVE, size=11),
                      tickformat=",.1f" if columna == "pct_graves" else ",.0f"),
        customdata=custom,
        hovertemplate=("<b>%{customdata[0]}</b><br>"
                       "Colisiones: %{customdata[1]:,.0f}<br>"
                       "Por 100.000 hab.: %{customdata[2]:,.1f}<br>"
                       "Fallecidos: %{customdata[3]:,.0f}<br>"
                       "Graves: %{customdata[4]:.2f} %<extra></extra>"),
    ))
    sel = r[r.condado_id == seleccionado]
    if not sel.empty:  # contorno del condado elegido
        fig.add_trace(go.Choropleth(
            geojson=geometria(), featureidkey="id", locations=sel.condado_id, z=[0],
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], showscale=False,
            marker_line_color=TEXTO, marker_line_width=2.2, hoverinfo="skip"))
    fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)",
                    projection_type="mercator")
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), dragmode=False,
                      clickmode="event+select")
    return fig


def ranking(r, columna, etiqueta, seleccionado):
    top = r.nlargest(12, columna).iloc[::-1]
    colores = [ACENTO if c == seleccionado else GRIS for c in top.condado_id]
    fig = go.Figure(go.Bar(
        x=top[columna], y=top.condado, orientation="h", marker_color=colores,
        text=[valor(columna, v) for v in top[columna]], textposition="outside",
        textfont=dict(color=TEXTO_SUAVE, size=12), cliponaxis=False,
        hovertemplate="%{y}: %{x:,.1f}<extra></extra>"))
    fig.update_layout(title=f"Los 12 condados con más {etiqueta}",
                      xaxis=dict(visible=False), yaxis=dict(gridcolor="rgba(0,0,0,0)"),
                      margin=dict(l=8, r=60, t=56, b=8), bargap=0.35)
    return fig


def evolucion_condado(df, condado_id, columna, etiqueta):
    anual = df.groupby("anio")[["habitantes", "colisiones", "fallecidos", "graves"]].sum()
    propio = df[df.condado_id == condado_id].set_index("anio").sort_index()

    def serie(t):
        if columna == "tasa":
            return 1e5 * t.colisiones / t.habitantes
        if columna == "tasa_fallecidos":
            return 1e5 * t.fallecidos / t.habitantes
        if columna == "pct_graves":
            return 100 * t.graves / t.colisiones
        return t.colisiones

    fig = go.Figure()
    if columna != "colisiones":
        fig.add_trace(go.Scatter(x=anual.index, y=serie(anual), name="California",
                                 mode="lines", line=dict(color=GRIS, width=2, dash="dot"),
                                 hovertemplate="California %{x}: %{y:,.1f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=propio.index, y=serie(propio), name=propio.condado.iloc[0],
                             mode="lines+markers", line=dict(color=ACENTO, width=2.5),
                             marker=dict(size=6),
                             hovertemplate="%{x}: %{y:,.1f}<extra></extra>"))
    fig.update_layout(title=f"Evolución de {etiqueta}", title_font_size=14,
                      xaxis=dict(dtick=1, tickangle=0, tickfont=dict(size=10)),
                      margin=dict(l=8, r=8, t=64, b=8), showlegend=columna != "colisiones",
                      legend=dict(y=1.02))
    return fig


def tiempo_y_territorio():
    total = consulta(f"""
        SELECT COUNT(*) AS colisiones, SUM(fallecidos) AS fallecidos,
               SUM(es_grave::INT) AS graves
        FROM {BASE}.vw_colision WHERE {PERIODO}""").iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Colisiones", estilo.entero(total.colisiones), border=True)
    c2.metric("Colisiones graves (K o A)", estilo.entero(total.graves), border=True,
              help="Colisiones con al menos un fallecido (K) o un herido incapacitante (A).")
    c3.metric("Proporción de graves", estilo.porcentaje(100 * total.graves / total.colisiones, 2),
              border=True)
    c4.metric("Fallecidos", estilo.entero(total.fallecidos), border=True)

    # ---- Mapa
    st.subheader("Los condados")
    df = condados_por_anio()
    a, b = st.columns([3, 2], gap="medium")
    nombre_metrica = a.selectbox("Medida", list(METRICAS), key="metrica_mapa")
    anio = b.select_slider("Año", [TODO_EL_PERIODO] + list(range(2010, 2020)),
                           value=TODO_EL_PERIODO, key="anio_mapa")
    columna, etiqueta = METRICAS[nombre_metrica]
    r = resumir_condados(df, anio)

    if "condado" not in st.session_state:
        st.session_state.condado = LOS_ANGELES
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda:
        evento = estilo.grafico(mapa(r, columna, st.session_state.condado), alto=600,
                                key="mapa", on_select="rerun", selection_mode="points")
        puntos = evento.selection.points if evento else []
        clave = tuple(p.get("location") for p in puntos)
        if puntos and clave != st.session_state.get("ultima_seleccion"):
            st.session_state.ultima_seleccion = clave
            if puntos[0].get("location") is not None:
                st.session_state.condado = int(puntos[0]["location"])
                st.rerun()
        estilo.nota("Pulse un condado para ver su ficha. Las tasas usan la población de cada "
                    "condado según el Census Bureau; en el período completo son el promedio "
                    "anual. Los condados pequeños atravesados por carreteras, como Alpine, "
                    "muestran tasas muy altas porque la población cuenta a quienes viven ahí, "
                    "no a quienes circulan.")

    with derecha:
        nombres = dict(zip(r.condado_id, r.condado))
        st.selectbox("Condado", sorted(nombres, key=nombres.get), format_func=nombres.get,
                     key="condado")
        fila = r[r.condado_id == st.session_state.condado].iloc[0]
        puesto = int(r[columna].rank(ascending=False, method="min")[fila.name])
        m1, m2 = st.columns(2)
        m1.metric("Colisiones", estilo.entero(fila.colisiones))
        m2.metric("Por 100.000 hab.", estilo.decimal(fila.tasa, 1))
        m3, m4 = st.columns(2)
        m3.metric("Fallecidos", estilo.entero(fila.fallecidos))
        m4.metric("Graves", estilo.porcentaje(fila.pct_graves, 2))
        st.markdown(f"Puesto **{puesto} de 58** en {etiqueta}"
                    f"{'' if anio == TODO_EL_PERIODO else f' en {anio}'}.")
        estilo.grafico(evolucion_condado(df, fila.condado_id, columna, etiqueta), alto=260)
        estilo.conclusion(texto_condado(fila, r, columna), titulo=f"{fila.condado} en pocas palabras")

    estilo.grafico(ranking(r, columna, etiqueta, st.session_state.condado), alto=430)
    estilo.conclusion(texto_mapa(r, columna, anio))

    # ---- Tiempo
    st.subheader("Patrones en el tiempo")
    anual = consulta(f"""
        SELECT anio, COUNT(*) AS colisiones, SUM(fallecidos) AS fallecidos
        FROM {BASE}.vw_colision WHERE {PERIODO} GROUP BY 1 ORDER BY 1""")
    mensual = consulta(f"""
        SELECT mes, COUNT(*) AS colisiones, COUNT(DISTINCT fecha) AS dias
        FROM {BASE}.vw_colision WHERE {PERIODO} GROUP BY 1 ORDER BY 1""")
    horario = consulta(f"""
        SELECT dia_semana, hora_del_dia, COUNT(*) AS colisiones
        FROM {BASE}.vw_colision WHERE {PERIODO} AND hora_del_dia IS NOT NULL
        GROUP BY 1, 2""")
    dias_semana = consulta(f"""
        SELECT dia_semana, COUNT(DISTINCT fecha) AS dias
        FROM {BASE}.vw_colision WHERE {PERIODO} GROUP BY 1""")

    izquierda, derecha = st.columns(2, gap="large")
    with izquierda:
        estilo.grafico(serie_anual(anual, "colisiones", "Colisiones por año", ACENTO), alto=330)
        estilo.conclusion(texto_colisiones_anuales(anual))
    with derecha:
        estilo.grafico(serie_anual(anual, "fallecidos", "Fallecidos por año", ROJO), alto=330)
        estilo.conclusion(texto_fallecidos_anuales(anual))

    estilo.grafico(mapa_de_calor(horario, dias_semana), alto=360)
    estilo.nota("Promedio de colisiones en cada hora de cada día de la semana. No incluye "
                "las 39.693 colisiones sin hora registrada (0,9 %).")
    estilo.conclusion(texto_semana(horario, dias_semana))

    estilo.grafico(perfil_mensual(mensual), alto=320)
    estilo.nota("Se usa el promedio diario porque los meses no tienen la misma cantidad de "
                "días: comparar totales castigaría a febrero.")
    estilo.conclusion(texto_meses(mensual))

    with st.expander("Tablas de este objetivo"):
        t = r.sort_values(columna, ascending=False)[
            ["condado", "habitantes", "colisiones", "tasa", "fallecidos", "tasa_fallecidos",
             "pct_graves"]]
        tabla(t, condado="Condado", habitantes=num("Habitantes (persona-año)"),
              colisiones=num("Colisiones"), tasa=num("Colisiones por 100.000 hab.", "%.1f"),
              fallecidos=num("Fallecidos"),
              tasa_fallecidos=num("Fallecidos por 100.000 hab.", "%.2f"),
              pct_graves=num("Graves (%)", "%.2f"))
        tabla(anual, anio=st.column_config.NumberColumn("Año", format="%d"),
              colisiones=num("Colisiones"), fallecidos=num("Fallecidos"))


def serie_anual(anual, columna, titulo, color):
    y = anual[columna]
    fig = go.Figure(go.Scatter(
        x=anual.anio, y=y, mode="lines+markers", line=dict(color=color, width=2.5),
        marker=dict(size=7), fill="tozeroy",
        fillcolor=f"rgba({int(color[1:3], 16)},{int(color[3:5], 16)},{int(color[5:7], 16)},0.08)",
        hovertemplate="%{x}: %{y:,.0f}<extra></extra>"))
    for i, texto in ((y.idxmin(), "mínimo"), (y.idxmax(), "máximo")):
        ancla = "left" if i == y.index[0] else "right" if i == y.index[-1] else "center"
        fig.add_annotation(x=anual.anio[i], y=y[i], text=f"{estilo.entero(y[i])} ({texto})",
                           showarrow=False, xanchor=ancla,
                           yshift=16 if texto == "máximo" else -16,
                           font=dict(size=11, color=TEXTO))
    rango = y.max() - y.min()
    fig.update_layout(title=titulo, xaxis=dict(dtick=1, range=[2009.6, 2019.4]),
                      yaxis=dict(range=[y.min() - rango * 0.6, y.max() + rango * 0.35],
                                 tickformat=",.0f"))
    return fig


def mapa_de_calor(horario, dias_semana):
    t = horario.merge(dias_semana, on="dia_semana")
    t["promedio"] = t.colisiones / t.dias
    matriz = t.pivot(index="dia_semana", columns="hora_del_dia", values="promedio")
    matriz = matriz.reindex(index=range(1, 8), columns=range(24))
    fig = go.Figure(go.Heatmap(
        z=matriz.values, x=[f"{h} h" for h in range(24)], y=DIAS, colorscale=ESCALA,
        xgap=2, ygap=2, colorbar=dict(thickness=10, outlinewidth=0, len=0.9),
        hovertemplate="%{y}, %{x}: %{z:.1f} colisiones en promedio<extra></extra>"))
    fig.update_layout(title="Colisiones por día de la semana y hora",
                      yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
                      xaxis=dict(ticks="", tickfont=dict(size=11)))
    return fig


def perfil_mensual(mensual):
    m = mensual.assign(promedio=mensual.colisiones / mensual.dias)
    maximo, minimo = m.promedio.idxmax(), m.promedio.idxmin()
    colores = [ACENTO if i == maximo else AZUL if i == minimo else GRIS for i in m.index]
    fig = go.Figure(go.Bar(
        x=[MESES[x - 1] for x in m.mes], y=m.promedio, marker_color=colores,
        text=[estilo.decimal(v, 0) for v in m.promedio], textposition="outside",
        textfont=dict(size=11, color=TEXTO_SUAVE), cliponaxis=False,
        hovertemplate="%{x}: %{y:,.0f} colisiones por día<extra></extra>"))
    fig.update_layout(title="Promedio diario de colisiones por mes", bargap=0.3,
                      yaxis=dict(range=[m.promedio.min() * 0.85, m.promedio.max() * 1.06],
                                 tickformat=",.0f"))
    return fig


# ---------------------------------------------------------------------------
# Objetivo 2. Conductor culpable
# ---------------------------------------------------------------------------

GRUPOS_EDAD = ["16 a 24", "25 a 34", "35 a 44", "45 a 54", "55 a 64", "65 o más", "Desconocida"]


def conductor_culpable():
    df = consulta(f"""
        SELECT CASE
                   WHEN edad_conductor_culpable BETWEEN 16 AND 24 THEN '16 a 24'
                   WHEN edad_conductor_culpable BETWEEN 25 AND 34 THEN '25 a 34'
                   WHEN edad_conductor_culpable BETWEEN 35 AND 44 THEN '35 a 44'
                   WHEN edad_conductor_culpable BETWEEN 45 AND 54 THEN '45 a 54'
                   WHEN edad_conductor_culpable BETWEEN 55 AND 64 THEN '55 a 64'
                   WHEN edad_conductor_culpable >= 65 THEN '65 o más'
                   ELSE 'Desconocida'
               END AS grupo,
               COALESCE(alcohol_implicado, FALSE) AS alcohol,
               COALESCE(hubo_fuga, FALSE) AS fuga,
               COUNT(*) AS colisiones,
               SUM(es_grave::INT) AS graves
        FROM {BASE}.vw_colision
        WHERE {PERIODO} AND hay_conductor_culpable
        GROUP BY ALL""")

    sin_fugas = st.toggle(
        "Excluir colisiones con fuga", key="sin_fugas",
        help="En las colisiones con fuga casi nunca se conoce la edad del culpable, por lo que "
             "el grupo de edad desconocida está formado sobre todo por fugas.")
    if sin_fugas:
        df = df[~df.fuga]

    total, graves = df.colisiones.sum(), df.graves.sum()
    con = df[df.alcohol]
    sin = df[~df.alcohol]
    pct_con = 100 * con.graves.sum() / con.colisiones.sum()
    pct_sin = 100 * sin.graves.sum() / sin.colisiones.sum()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Colisiones analizadas", estilo.entero(total), border=True,
              help="Colisiones del período cuyo culpable fue un conductor.")
    c2.metric("Proporción de graves", estilo.porcentaje(100 * graves / total, 2), border=True)
    c3.metric("Con alcohol reportado", estilo.porcentaje(100 * con.colisiones.sum() / total),
              border=True)
    c4.metric("Gravedad con alcohol", f"{estilo.decimal(pct_con / pct_sin, 1)} veces más",
              border=True, help=f"{estilo.porcentaje(pct_con, 2)} de colisiones graves con "
                                f"alcohol reportado frente a {estilo.porcentaje(pct_sin, 2)} sin "
                                f"alcohol reportado.")

    grupos = (df.groupby("grupo")[["colisiones", "graves"]].sum()
              .reindex([g for g in GRUPOS_EDAD if g in set(df.grupo)]))
    grupos["pct"] = 100 * grupos.graves / grupos.colisiones
    estilo.grafico(volumen_y_gravedad(grupos, 100 * graves / total), alto=420)
    estilo.conclusion(texto_edades(grupos, total))

    por_alcohol = df.groupby(["grupo", "alcohol"])[["colisiones", "graves"]].sum().reset_index()
    por_alcohol["pct"] = 100 * por_alcohol.graves / por_alcohol.colisiones
    estilo.grafico(pesas_alcohol(por_alcohol), alto=420)
    estilo.nota("La fuente solo marca el alcohol cuando se confirmó: «sin alcohol reportado» no "
                "significa que el conductor estuviera sobrio.")
    estilo.conclusion(texto_alcohol(por_alcohol, pct_con / pct_sin))

    with st.expander("Tabla de este objetivo"):
        t = por_alcohol.pivot(index="grupo", columns="alcohol",
                              values=["colisiones", "pct"]).reindex(grupos.index)
        t.columns = ["colisiones_sin", "colisiones_con", "pct_sin", "pct_con"]
        tabla(t.reset_index(), grupo="Edad del culpable",
              colisiones_sin=num("Colisiones sin alcohol reportado"),
              colisiones_con=num("Colisiones con alcohol"),
              pct_sin=num("Graves sin alcohol (%)", "%.2f"),
              pct_con=num("Graves con alcohol (%)", "%.2f"))


def volumen_y_gravedad(grupos, promedio):
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, column_widths=[0.56, 0.44],
                        horizontal_spacing=0.06,
                        subplot_titles=("Colisiones", "Colisiones graves (%)"))
    etiquetas = list(grupos.index)
    colores = [AZUL if g != "Desconocida" else GRIS_TENUE for g in etiquetas]
    fig.add_trace(go.Bar(
        x=grupos.colisiones, y=etiquetas, orientation="h", marker_color=colores,
        text=[estilo.entero(v) for v in grupos.colisiones], textposition="inside",
        insidetextanchor="end", textfont=dict(color=TEXTO, size=12),
        hovertemplate="%{y}: %{x:,.0f} colisiones<extra></extra>"), 1, 1)
    fig.add_trace(go.Scatter(
        x=grupos.pct, y=etiquetas, mode="markers+text",
        marker=dict(size=13, color=[AMBAR if g != "Desconocida" else GRIS for g in etiquetas]),
        text=[estilo.porcentaje(v, 2) for v in grupos.pct], textposition="middle right",
        textfont=dict(size=12, color=TEXTO), cliponaxis=False,
        hovertemplate="%{y}: %{x:.2f} % graves<extra></extra>"), 1, 2)
    fig.add_vline(x=promedio, line=dict(color=TEXTO_SUAVE, dash="dot", width=1), row=1, col=2)
    fig.add_annotation(x=promedio, y=0, yref="paper", xref="x2",
                       text=f"promedio {estilo.porcentaje(promedio, 2)}", showarrow=False,
                       xanchor="right", yanchor="bottom", xshift=-4,
                       font=dict(size=11, color=TEXTO_SUAVE))
    fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
    fig.update_xaxes(visible=False, row=1, col=1)
    fig.update_xaxes(showgrid=True, gridcolor=REJILLA, ticksuffix=" %", row=1, col=2,
                     range=[0, grupos.pct.max() * 1.35])
    fig.update_annotations(font=dict(family="Newsreader, Georgia, serif", size=15, color=TEXTO),
                           selector=dict(text="Colisiones"))
    fig.update_annotations(font=dict(family="Newsreader, Georgia, serif", size=15, color=TEXTO),
                           selector=dict(text="Colisiones graves (%)"))
    fig.update_layout(showlegend=False, margin=dict(l=8, r=40, t=40, b=8), bargap=0.3)
    return fig


def pesas_alcohol(t):
    t = t[t.grupo != "Desconocida"]
    orden = [g for g in GRUPOS_EDAD if g in set(t.grupo)]
    sin = t[~t.alcohol].set_index("grupo").reindex(orden)
    con = t[t.alcohol].set_index("grupo").reindex(orden)
    fig = go.Figure()
    for g in orden:
        fig.add_trace(go.Scatter(x=[sin.pct[g], con.pct[g]], y=[g, g], mode="lines",
                                 line=dict(color=BORDE, width=6), hoverinfo="skip",
                                 showlegend=False))
    fig.add_trace(go.Scatter(x=sin.pct, y=orden, mode="markers", name="Sin alcohol reportado",
                             marker=dict(size=14, color=AZUL),
                             hovertemplate="%{y}, sin alcohol: %{x:.2f} %<extra></extra>"))
    fig.add_trace(go.Scatter(x=con.pct, y=orden, mode="markers+text", name="Con alcohol",
                             marker=dict(size=14, color=AMBAR),
                             text=[estilo.porcentaje(v, 1) for v in con.pct],
                             textposition="middle right", textfont=dict(size=12, color=TEXTO),
                             hovertemplate="%{y}, con alcohol: %{x:.2f} %<extra></extra>"))
    fig.update_layout(title="Colisiones graves (%) según presencia de alcohol, por edad del "
                            "culpable",
                      xaxis=dict(ticksuffix=" %", showgrid=True, gridcolor=REJILLA,
                                 range=[0, con.pct.max() * 1.2]),
                      yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
                      legend=dict(y=-0.08, yanchor="top"), margin=dict(b=40))
    return fig


# ---------------------------------------------------------------------------
# Objetivo 3. Condiciones del entorno
# ---------------------------------------------------------------------------

DIMENSIONES = {"Iluminación": "iluminacion", "Clima": "clima",
               "Superficie de la calzada": "superficie"}
AL_FINAL = {"Sin clasificar", "Otro"}


def condiciones_del_entorno():
    partes = [f"""
        SELECT '{nombre}' AS dimension, COALESCE(k.etiqueta, 'Sin clasificar') AS categoria,
               COUNT(*) AS colisiones, SUM(v.es_grave::INT) AS graves
        FROM {BASE}.vw_colision v
        LEFT JOIN {BASE}.{tabla_} k USING ({tabla_}_id)
        WHERE v.{PERIODO}
        GROUP BY 1, 2""" for nombre, tabla_ in DIMENSIONES.items()]
    df = consulta(" UNION ALL ".join(partes))

    dimension = st.segmented_control("Condición", list(DIMENSIONES), default="Iluminación",
                                     key="dimension") or "Iluminación"
    t = df[df.dimension == dimension].copy()
    total = t.colisiones.sum()
    promedio = 100 * t.graves.sum() / total
    t["pct_total"] = 100 * t.colisiones / total
    t["pct_graves"] = 100 * t.graves / t.colisiones
    t["al_final"] = t.categoria.isin(AL_FINAL)
    t = t.sort_values(["al_final", "pct_graves"], ascending=[True, False])

    peor = t[~t.al_final].iloc[0]
    mayor = t[~t.al_final].sort_values("colisiones").iloc[-1]
    c1, c2, c3 = st.columns(3)
    estilo.ficha(c1, "Condición más frecuente", mayor.categoria,
                 f"{estilo.porcentaje(mayor.pct_total)} de las colisiones")
    estilo.ficha(c2, "Mayor proporción de colisiones graves", peor.categoria,
                 f"{estilo.porcentaje(peor.pct_graves, 2)} de sus colisiones")
    estilo.ficha(c3, "Proporción de graves en todas las colisiones",
                 estilo.porcentaje(promedio, 2))

    estilo.grafico(frecuencia_y_gravedad(t, promedio, dimension), alto=120 + 52 * len(t))
    estilo.nota("A la izquierda, qué parte de todas las colisiones ocurrió en cada condición. "
                "A la derecha, qué proporción de las colisiones de esa condición fue grave: es "
                "una proporción condicional, no dice dónde ocurre la mayoría de las graves.")

    estilo.conclusion(texto_entorno(t, dimension))

    with st.expander("Tabla de este objetivo"):
        tabla(t[["categoria", "colisiones", "pct_total", "graves", "pct_graves"]],
              categoria=dimension, colisiones=num("Colisiones"),
              pct_total=num("% del total", "%.2f"), graves=num("Graves"),
              pct_graves=num("Graves (%)", "%.2f"))


def frecuencia_y_gravedad(t, promedio, dimension):
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, column_widths=[0.5, 0.5],
                        horizontal_spacing=0.05,
                        subplot_titles=("Parte de todas las colisiones (%)",
                                        "Colisiones graves dentro de la condición (%)"))
    color_fila = [AZUL if not f else GRIS_TENUE for f in t.al_final]
    fig.add_trace(go.Bar(
        x=t.pct_total, y=t.categoria, orientation="h", marker_color=color_fila,
        text=[estilo.porcentaje(v) for v in t.pct_total], textposition="outside",
        textfont=dict(size=12, color=TEXTO_SUAVE), cliponaxis=False,
        customdata=t.colisiones,
        hovertemplate="%{y}: %{x:.2f} % (%{customdata:,.0f} colisiones)<extra></extra>"), 1, 1)
    fig.add_trace(go.Bar(
        x=t.pct_graves, y=t.categoria, orientation="h",
        marker_color=[GRIS_TENUE if f else AMBAR if v > promedio else GRIS
                      for f, v in zip(t.al_final, t.pct_graves)],
        text=[estilo.porcentaje(v, 2) for v in t.pct_graves], textposition="outside",
        textfont=dict(size=12, color=TEXTO), cliponaxis=False,
        hovertemplate="%{y}: %{x:.2f} % graves<extra></extra>"), 1, 2)
    fig.add_vline(x=promedio, line=dict(color=TEXTO_SUAVE, dash="dot", width=1), row=1, col=2)
    fig.add_annotation(x=promedio, y=0, yref="paper", xref="x2",
                       text=f"promedio {estilo.porcentaje(promedio, 2)}", showarrow=False,
                       xanchor="left", yanchor="top", xshift=4, yshift=-2,
                       font=dict(size=11, color=TEXTO_SUAVE))
    fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
    fig.update_xaxes(visible=False)
    fig.update_xaxes(range=[0, t.pct_total.max() * 1.25], row=1, col=1)
    fig.update_xaxes(range=[0, t.pct_graves.max() * 1.3], row=1, col=2)
    fig.update_annotations(font=dict(family="Newsreader, Georgia, serif", size=15, color=TEXTO),
                           selector=lambda a: a.text != f"promedio {estilo.porcentaje(promedio, 2)}")
    fig.update_layout(showlegend=False, margin=dict(l=8, r=40, t=44, b=28), bargap=0.32)
    return fig


# ---------------------------------------------------------------------------
# Objetivo 4. Vehículo y ocupantes
# ---------------------------------------------------------------------------

def vehiculo_y_ocupantes():
    df = consulta(f"""
        SELECT edad_vehiculo, kabco, COUNT(*) AS victimas
        FROM {BASE}.vw_victima
        WHERE es_ocupante AND edad_vehiculo BETWEEN 0 AND 25 AND {PERIODO}
        GROUP BY 1, 2""")
    t = df.pivot(index="edad_vehiculo", columns="kabco", values="victimas").fillna(0)
    t = t.reindex(columns=list("KABCO"), fill_value=0)
    t["total"] = t.sum(axis=1)
    t["pct_ka"] = 100 * (t.K + t.A) / t.total
    t["pct_k"] = 100 * t.K / t.total

    total = t.total.sum()
    pct_ka = 100 * (t.K.sum() + t.A.sum()) / total
    nuevos = t.loc[0:5]
    viejos = t.loc[15:25]
    c1, c2, c3 = st.columns(3)
    c1.metric("Ocupantes víctimas (vehículos de 0 a 25 años)", estilo.entero(total), border=True)
    c2.metric("Fallecidos o heridos incapacitantes", estilo.porcentaje(pct_ka, 2), border=True)
    pct_viejos = 100 * (viejos.K.sum() + viejos.A.sum()) / viejos.total.sum()
    pct_nuevos = 100 * (nuevos.K.sum() + nuevos.A.sum()) / nuevos.total.sum()
    c3.metric("Vehículos de 15 a 25 años frente a 0 a 5",
              f"{estilo.decimal(pct_viejos / pct_nuevos, 2)} veces",
              border=True,
              help=f"Fallecidos o heridos incapacitantes: {estilo.porcentaje(pct_viejos, 2)} en "
                   f"vehículos de 15 a 25 años frente a {estilo.porcentaje(pct_nuevos, 2)} en "
                   f"vehículos de 0 a 5 años.")

    estilo.grafico(gravedad_por_antiguedad(t), alto=520)
    estilo.conclusion(texto_antiguedad(t))
    estilo.grafico(composicion_kabco(t), alto=400)
    estilo.nota("En 2017 SWITRS cambió los códigos de lesión, lo que afecta sobre todo a las "
                "categorías B, C y O. Los fallecidos (K) no cambian de definición.")
    estilo.conclusion(texto_composicion(t))

    with st.expander("Tabla de este objetivo"):
        s = t.reset_index()
        tabla(s[["edad_vehiculo", "K", "A", "B", "C", "O", "total", "pct_ka"]],
              edad_vehiculo=st.column_config.NumberColumn("Antigüedad (años)", format="%d"),
              K=num("K"), A=num("A"), B=num("B"), C=num("C"), O=num("O"),
              total=num("Total"), pct_ka=num("K o A (%)", "%.2f"))


def gravedad_por_antiguedad(t):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.55, 0.45],
                        vertical_spacing=0.1,
                        subplot_titles=("Víctimas fallecidas o con lesión incapacitante (%)",
                                        "Víctimas ocupantes"))
    fig.add_trace(go.Scatter(
        x=t.index, y=t.pct_ka, name="K o A", mode="lines+markers",
        line=dict(color=AMBAR, width=2.5), marker=dict(size=6),
        hovertemplate="%{x} años: %{y:.2f} % K o A<extra></extra>"), 1, 1)
    fig.add_trace(go.Scatter(
        x=t.index, y=t.pct_k, name="Solo K (fallecidos)", mode="lines",
        line=dict(color=ROJO, width=2, dash="dot"),
        hovertemplate="%{x} años: %{y:.2f} % fallecidos<extra></extra>"), 1, 1)
    fig.add_trace(go.Bar(
        x=t.index, y=t.total, name="Víctimas", marker_color=AZUL, showlegend=False,
        hovertemplate="%{x} años: %{y:,.0f} víctimas<extra></extra>"), 2, 1)
    fig.update_yaxes(ticksuffix=" %", rangemode="tozero", row=1, col=1)
    fig.update_yaxes(tickformat=",.0f", row=2, col=1)
    fig.update_xaxes(dtick=1, range=[-0.6, 25.6], row=2, col=1,
                     title_text="Antigüedad del vehículo (años)")
    fig.update_xaxes(dtick=1, range=[-0.6, 25.6], row=1, col=1)
    fig.update_annotations(font=dict(family="Newsreader, Georgia, serif", size=15, color=TEXTO),
                           x=0, xanchor="left")
    fig.update_layout(margin=dict(l=8, r=16, t=70, b=8), bargap=0.25,
                      legend=dict(y=1.08, x=1, xanchor="right"))
    return fig


def composicion_kabco(t):
    fig = go.Figure()
    for k in "OCBAK":
        fig.add_trace(go.Scatter(
            x=t.index, y=t[k], name=estilo.KABCO_ETIQUETAS[k], mode="lines",
            stackgroup="uno", groupnorm="percent", line=dict(width=0.5, color=FONDO),
            fillcolor=estilo.KABCO_COLORES[k],
            hovertemplate=f"{estilo.KABCO_ETIQUETAS[k]}, %{{x}} años: %{{y:.1f}} %<extra></extra>"))
    fig.update_layout(title="Composición de las lesiones según la antigüedad del vehículo",
                      xaxis=dict(dtick=1, title="Antigüedad del vehículo (años)"),
                      yaxis=dict(ticksuffix=" %", range=[0, 100]),
                      legend=dict(traceorder="reversed", y=1.0))
    return fig



# ---------------------------------------------------------------------------
# Conclusiones: se escriben con los mismos datos de cada gráfico, para que
# cambien solas si se elige otra medida, otro año o se excluyen las fugas
# ---------------------------------------------------------------------------

def lista(nombres):
    nombres = list(nombres)
    return nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " y " + nombres[-1]


def de_cada_100(x):
    return f"{estilo.decimal(x, 1)} de cada 100"


def texto_condado(fila, r, columna):
    nombre = fila.condado
    if columna == "colisiones":
        parte = 100 * fila.colisiones / r.colisiones.sum()
        return (f"En {nombre} ocurrió el {estilo.porcentaje(parte, 1)} de todas las colisiones "
                f"del estado en el período elegido.")
    if columna == "tasa":
        estado, propio, que = 1e5 * r.colisiones.sum() / r.habitantes.sum(), fila.tasa, \
            "la cantidad de choques por habitante"
    elif columna == "tasa_fallecidos":
        estado, propio, que = 1e5 * r.fallecidos.sum() / r.habitantes.sum(), fila.tasa_fallecidos, \
            "la cantidad de muertes por habitante"
    else:
        estado, propio, que = 100 * r.graves.sum() / r.colisiones.sum(), fila.pct_graves, \
            "la parte de los choques que fue grave"
    diferencia = 100 * (propio / estado - 1)
    if abs(diferencia) < 5:
        return f"En {nombre}, {que} es muy parecida al promedio de California."
    return (f"En {nombre}, {que} es un {estilo.porcentaje(abs(diferencia), 0)} "
            f"{'más alta' if diferencia > 0 else 'más baja'} que el promedio de California.")


def texto_mapa(r, columna, anio):
    anios = 10 if anio == TODO_EL_PERIODO else 1
    r = r.assign(poblacion=r.habitantes / anios).sort_values(columna, ascending=False)
    altos, bajos = r.head(3), r.tail(3).iloc[::-1]
    pequenos = (altos.poblacion < 50_000).all()
    cuando = "al año" if anio == TODO_EL_PERIODO else f"en {anio}"
    la = r[r.condado_id == LOS_ANGELES].iloc[0]

    if columna == "tasa":
        estado = 1e5 * r.colisiones.sum() / r.habitantes.sum()
        texto = (f"En todo California hubo en promedio {estilo.decimal(estado, 0)} choques por "
                 f"cada 100.000 habitantes {cuando}. Las tasas más altas están en "
                 f"{lista(altos.condado)}")
        texto += (", condados donde vive muy poca gente pero pasa mucho tránsito por sus "
                  "carreteras, así que unos pocos choques alcanzan para que la tasa se dispare."
                  if pequenos else ".")
        texto += (f" {la.condado}, el condado más poblado, tiene {estilo.decimal(la.tasa, 0)}, "
                  f"{'por encima' if la.tasa > estado else 'por debajo'} del promedio. Las más "
                  f"bajas están en {lista(bajos.condado)}.")
        return texto
    if columna == "tasa_fallecidos":
        estado = 1e5 * r.fallecidos.sum() / r.habitantes.sum()
        texto = (f"En todo California murieron en promedio {estilo.decimal(estado, 1)} personas "
                 f"por cada 100.000 habitantes {cuando}. Las cifras más altas están en "
                 f"{lista(altos.condado)}{', condados rurales con muy poca población' if pequenos else ''}, "
                 f"y las más bajas en {lista(bajos.condado)}.")
        urbanos = r[r.poblacion > 1_000_000].tasa_fallecidos.median()
        rurales = r[r.poblacion < 100_000].tasa_fallecidos.median()
        if urbanos < rurales:
            texto += (" En las ciudades grandes hay muchos choques, pero en relación con su "
                      "población mueren menos personas que en el campo.")
        return texto
    if columna == "pct_graves":
        estado = 100 * r.graves.sum() / r.colisiones.sum()
        texto = (f"En todo el estado, {de_cada_100(estado)} choques fueron graves. La proporción "
                 f"más alta está en {lista(altos.condado)} y la más baja en "
                 f"{lista(bajos.condado)}.")
        if pequenos:
            texto += (" Otra vez aparecen condados rurales: allí hay pocos choques, pero una "
                      "parte mayor termina en una muerte o en una lesión grave.")
        return texto
    parte = 100 * la.colisiones / r.colisiones.sum()
    cinco = 100 * r.head(5).colisiones.sum() / r.colisiones.sum()
    return (f"{la.condado} concentra el {estilo.porcentaje(parte, 0)} de todas las colisiones del "
            f"estado, y junto con {lista(r.iloc[1:5].condado)} suma el "
            f"{estilo.porcentaje(cinco, 0)}. Los totales siguen sobre todo al tamaño de la "
            f"población, por eso conviene mirar también las tasas por habitante.")


def texto_colisiones_anuales(anual):
    y = anual.set_index("anio").colisiones
    primero, ultimo = y.index[0], y.index[-1]
    minimo, maximo = y.idxmin(), y.idxmax()
    texto = (f"Los choques bajaron entre {primero} y {minimo} (de {estilo.entero(y[primero])} a "
             f"{estilo.entero(y[minimo])}) y después subieron con fuerza hasta {maximo}, cuando "
             f"llegaron a {estilo.entero(y[maximo])}.")
    if maximo != ultimo:
        texto += (f" En los años siguientes bajaron un poco, pero {ultimo} terminó con un "
                  f"{estilo.porcentaje(100 * (y[ultimo] / y[primero] - 1), 0)} más de choques "
                  f"que {primero}.")
    return texto


def texto_fallecidos_anuales(anual):
    datos = anual.set_index("anio")
    f, c = datos.fallecidos, datos.colisiones
    primero, maximo = f.index[0], f.idxmax()
    siempre = (f.loc[:maximo].diff().dropna() > 0).all()
    texto = (f"Las muertes {'subieron todos los años' if siempre else 'tendieron a subir'} hasta "
             f"{maximo}: de {estilo.entero(f[primero])} en {primero} a "
             f"{estilo.entero(f[maximo])}, un {estilo.porcentaje(100 * (f[maximo] / f[primero] - 1), 0)} más.")
    baja = c.idxmin()
    if baja > primero and f[baja] > f[primero]:
        texto += (f" A diferencia de los choques, no bajaron a comienzos de la década: entre "
                  f"{primero} y {baja} hubo menos choques, pero murió más gente.")
    return texto


def texto_semana(horario, dias_semana):
    t = horario.merge(dias_semana, on="dia_semana")
    t["promedio"] = t.colisiones / t.dias
    laborales = t[t.dia_semana <= 5].groupby("hora_del_dia").promedio.mean()
    finde = t[t.dia_semana >= 6].groupby("hora_del_dia").promedio.mean()
    manana = laborales.loc[5:10].idxmax()
    tarde = laborales.loc[12:20].idxmax()
    peor = t.loc[t.promedio.idxmax()]
    madrugada = finde.loc[0:4].mean() / laborales.loc[0:4].mean()
    return (f"Los choques siguen el ritmo de la semana de trabajo. De lunes a viernes hay dos "
            f"horas pico: una en la mañana, alrededor de las {manana} h, y otra más fuerte en la "
            f"tarde, que llega a su punto más alto a las {tarde} h; las dos coinciden con las "
            f"horas de entrada y salida del trabajo. El peor momento de toda la semana es el "
            f"{DIAS[int(peor.dia_semana) - 1].lower()} a las {int(peor.hora_del_dia)} h. Los "
            f"fines de semana no hay pico en la mañana, pero en la madrugada (de 0 a 4 h) hay "
            f"{estilo.decimal(madrugada, 1)} veces más choques que entre semana.")


def texto_meses(mensual):
    m = mensual.assign(promedio=mensual.colisiones / mensual.dias).set_index("mes")
    alto, bajo = m.promedio.idxmax(), m.promedio.idxmin()
    texto = (f"Ningún mes se aleja mucho de los demás: todos están entre "
             f"{estilo.decimal(m.promedio.min(), 0)} y {estilo.decimal(m.promedio.max(), 0)} "
             f"choques por día. {MESES_LARGOS[alto - 1].capitalize()} es el mes con más choques "
             f"por día y {MESES_LARGOS[bajo - 1]} el que menos.")
    if m.colisiones.idxmin() == 2 and bajo != 2:
        texto += (" Si se cuentan los totales, febrero parece el mes más tranquilo, pero es "
                  "solo porque tiene menos días.")
    return texto


def texto_edades(grupos, total):
    g = grupos.drop(index="Desconocida", errors="ignore")
    mayor = g.colisiones.idxmax()
    parte = 100 * g.colisiones[mayor] / total
    baja_con_edad = (g.colisiones.loc[mayor:].diff().dropna() < 0).all()
    jovenes, viejos = g.loc["16 a 24"], g.loc["65 o más"]
    texto = (f"Los conductores de {mayor} años son los culpables de más choques: "
             f"{estilo.entero(g.colisiones[mayor])}, el {estilo.porcentaje(parte, 0)} del total. ")
    texto += ("A medida que sube la edad hay cada vez menos choques" if baja_con_edad
              else "Con la edad, en general, hay menos choques")
    if viejos.pct > jovenes.pct:
        texto += (f", pero cuando el culpable es mayor el choque suele ser más serio: con "
                  f"conductores de 65 años o más, {de_cada_100(viejos.pct)} choques fueron "
                  f"graves, frente a {de_cada_100(jovenes.pct)} con los de 16 a 24.")
    else:
        texto += "."
    if "Desconocida" in grupos.index:
        texto += (f" El grupo de edad desconocida tiene muy pocos choques graves "
                  f"({de_cada_100(grupos.pct['Desconocida'])}): en su mayoría son choques con "
                  f"fuga, en los que no se identificó al conductor.")
    return texto


def texto_alcohol(t, veces):
    t = t[t.grupo != "Desconocida"]
    sin, con = t[~t.alcohol].pct, t[t.alcohol].pct
    return (f"En todas las edades, los choques con alcohol reportado son mucho más graves. Sin "
            f"alcohol reportado, entre {estilo.decimal(sin.min(), 1)} y "
            f"{estilo.decimal(sin.max(), 1)} de cada 100 choques son graves; con alcohol, entre "
            f"{estilo.decimal(con.min(), 1)} y {estilo.decimal(con.max(), 1)}. En total, la "
            f"proporción de choques graves es unas {estilo.decimal(veces, 1)} veces mayor cuando "
            f"hay alcohol de por medio.")


FRASES_ENTORNO = {
    "Iluminación": {"Luz diurna": "de día", "Oscuridad sin alumbrado": "de noche sin alumbrado",
                    "Oscuridad con alumbrado": "de noche con alumbrado",
                    "Oscuridad con alumbrado averiado": "de noche con el alumbrado averiado",
                    "Amanecer o atardecer": "al amanecer o al atardecer"},
    "Clima": {"Despejado": "con cielo despejado", "Nublado": "con cielo nublado",
              "Lluvia": "con lluvia", "Niebla": "con niebla", "Nieve": "con nieve",
              "Viento fuerte": "con viento fuerte"},
    "Superficie de la calzada": {"Seca": "con la calzada seca", "Mojada": "con la calzada mojada",
                                 "Nieve o hielo": "con nieve o hielo en la calzada",
                                 "Resbaladiza": "con la calzada resbaladiza"},
}


def texto_entorno(t, dimension):
    frase = lambda c: FRASES_ENTORNO[dimension].get(c, f"con {c.lower()}")
    pct = t.set_index("categoria").pct_graves
    normales = t[~t.al_final]
    mayor = normales.sort_values("colisiones").iloc[-1]
    peor = normales.iloc[0]
    texto = (f"La gran mayoría de los choques ocurre {frase(mayor.categoria)} "
             f"({estilo.porcentaje(mayor.pct_total, 0)} del total). Pero la proporción de choques "
             f"graves es más alta {frase(peor.categoria)}: {de_cada_100(peor.pct_graves)}, frente a "
             f"{estilo.decimal(mayor.pct_graves, 1)} {frase(mayor.categoria)}")
    texto += (", aunque es una situación muy poco frecuente." if peor.pct_total < 1 else ".")
    if dimension == "Iluminación" and {"Oscuridad con alumbrado", "Oscuridad sin alumbrado"} <= set(pct.index):
        texto += (f" De noche, la diferencia entre calles con y sin luz es grande: con alumbrado "
                  f"son {de_cada_100(pct['Oscuridad con alumbrado'])}.")
    if dimension == "Clima" and {"Lluvia", "Despejado"} <= set(pct.index) and pct["Lluvia"] < pct["Despejado"]:
        texto += (f" Algo que llama la atención: con lluvia hay menos choques graves "
                  f"({de_cada_100(pct['Lluvia'])}) que con cielo despejado. Una explicación "
                  f"posible es que con lluvia se maneja con más cuidado, pero estos datos no "
                  f"permiten comprobarlo.")
    if dimension == "Superficie de la calzada" and {"Mojada", "Seca"} <= set(pct.index) and pct["Mojada"] < pct["Seca"]:
        texto += (f" Igual que con la lluvia, con la calzada mojada hay algo menos de choques "
                  f"graves ({de_cada_100(pct['Mojada'])}) que con la calzada seca.")
    return texto


def texto_antiguedad(t):
    nuevo, viejo = t.pct_ka.iloc[0], t.pct_ka.iloc[-1]
    pico = int(t.total.idxmax())
    return (f"Cuanto más viejo es el auto, más serias suelen ser las lesiones de quienes viajan "
            f"en él: en autos del año, {de_cada_100(nuevo)} víctimas murieron o quedaron con una "
            f"lesión incapacitante; en autos de {int(t.index[-1])} años, {de_cada_100(viejo)}, "
            f"{estilo.decimal(viejo / nuevo, 1)} veces más. Al mismo tiempo, hay muchas menos "
            f"víctimas en autos viejos: el máximo está en los autos de {pico} "
            f"{'año' if pico == 1 else 'años'} y desde los 12 años la cantidad baja rápido, lo que "
            f"probablemente refleja que quedan menos autos de esa edad en la calle (no hay datos "
            f"del parque vehicular para confirmarlo).")


def texto_composicion(t):
    parte = lambda fila, k: 100 * fila[list(k)].sum() / fila.total
    nuevo, viejo = t.iloc[0], t.iloc[-1]
    texto = ""
    if all(parte(f, "OC") > 50 for _, f in t.iterrows()):
        texto = ("En autos de cualquier edad, la mayoría de las víctimas sale sin lesión aparente "
                 "o con una posible lesión leve. ")
    return texto + (
        f"Pero esa mayoría se achica con los años: las víctimas sin lesión aparente pasan del "
        f"{estilo.porcentaje(parte(nuevo, 'O'), 0)} en autos del año al "
        f"{estilo.porcentaje(parte(viejo, 'O'), 0)} en autos de {int(t.index[-1])} años, mientras "
        f"que las lesiones visibles, incapacitantes y mortales pasan del "
        f"{estilo.porcentaje(parte(nuevo, 'BAK'), 0)} al {estilo.porcentaje(parte(viejo, 'BAK'), 0)}.")

# ---------------------------------------------------------------------------

SECCIONES = {
    "Tiempo y territorio": tiempo_y_territorio,
    "Conductor culpable": conductor_culpable,
    "Condiciones del entorno": condiciones_del_entorno,
    "Vehículo y ocupantes": vehiculo_y_ocupantes,
}
with st.spinner("Consultando MotherDuck..."):
    SECCIONES[objetivo]()
