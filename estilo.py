"""Estilo común de la aplicación: paleta, plantilla de gráficos y formatos.

Todas las páginas usan estas funciones para que los gráficos y los números se
vean igual en toda la app. La paleta es la del tablero de Power BI del proyecto
y coincide con .streamlit/config.toml.
"""

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# Paleta (la misma del tablero de Power BI)
FONDO = "#1F1F1F"
SUPERFICIE = "#292B30"
BORDE = "#34373D"
REJILLA = "#2C2E33"
TEXTO = "#F5F5F5"
TEXTO_SUAVE = "#A1A1AA"
TEXTO_TENUE = "#8A8A93"
ACENTO = "#14B8A6"       # turquesa: el dato principal y la selección
AZUL = "#3B82F6"         # volúmenes: cantidad de colisiones o víctimas
MARINO = "#1E3A8A"
CELESTE = "#2B98C1"
AMBAR = "#F59E0B"        # gravedad
ROJO = "#DD561D"         # fallecidos
GRIS = "#4B4E56"         # contexto
GRIS_TENUE = "#36383E"   # sin clasificar o desconocido

# Escala secuencial para el mapa y el mapa de calor, como el mapa del tablero
ESCALA = [
    [0.00, "#2A2D33"], [0.25, MARINO], [0.50, AZUL],
    [0.75, ACENTO], [1.00, "#7DF3E1"],
]

# KABCO, de la lesión más grave a la ausencia de lesión
KABCO_ETIQUETAS = {
    "K": "K · Fallecido",
    "A": "A · Lesión incapacitante",
    "B": "B · Lesión visible",
    "C": "C · Posible lesión",
    "O": "O · Sin lesión aparente",
}
KABCO_COLORES = {"K": ROJO, "A": AMBAR, "B": CELESTE, "C": MARINO, "O": "#3A3D44"}

plantilla = go.layout.Template(pio.templates["plotly_dark"])
plantilla.layout.update(
    dict(
        font=dict(family="Inter, system-ui, sans-serif", size=13, color=TEXTO_SUAVE),
        title=dict(font=dict(family="Newsreader, Georgia, serif", size=17, color=TEXTO),
                   x=0, xanchor="left", y=0.98, yanchor="top"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        separators=",.",
        colorway=[ACENTO, AZUL, AMBAR, ROJO, CELESTE],
        margin=dict(l=8, r=16, t=56, b=8),
        xaxis=dict(showgrid=False, zeroline=False, linecolor=BORDE, ticks="outside",
                   tickcolor=BORDE, ticklen=4, title=dict(font=dict(size=12))),
        yaxis=dict(gridcolor=REJILLA, zeroline=False, linecolor=BORDE, ticks="",
                   title=dict(font=dict(size=12))),
        hoverlabel=dict(bgcolor="#2C2F35", bordercolor=BORDE,
                        font=dict(family="Inter, sans-serif", color=TEXTO, size=13)),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, xanchor="left",
                    title=dict(text=""), font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
        coloraxis=dict(colorbar=dict(outlinewidth=0, thickness=10, tickfont=dict(size=11))),
        geo=dict(bgcolor="rgba(0,0,0,0)"),
    )
)
pio.templates["colisiones"] = plantilla
pio.templates.default = "colisiones"

CONFIG_GRAFICO = {"displayModeBar": False, "scrollZoom": False}


def aplicar():
    """Ajustes de presentación que el tema de Streamlit no cubre."""
    st.markdown(
        f"""
        <style>
        .block-container {{ max-width: 1240px; padding-top: 3.4rem; }}
        .antetitulo {{
            color: {ACENTO}; font-size: 0.78rem; font-weight: 600;
            letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.2rem;
        }}
        .bajada {{ color: {TEXTO_SUAVE}; font-size: 1.05rem; line-height: 1.55; max-width: 62rem; }}
        .nota {{ color: {TEXTO_TENUE}; font-size: 0.85rem; line-height: 1.5; }}
        .ficha-etiqueta {{ color: {TEXTO_SUAVE}; font-size: 0.85rem; margin-bottom: 0.15rem; }}
        .ficha-valor {{ color: {TEXTO}; font-size: 1.35rem; font-weight: 600; line-height: 1.25; }}
        .ficha-detalle {{ color: {ACENTO}; font-size: 0.9rem; margin-top: 0.2rem; }}
        .conclusion {{
            border-left: 3px solid {ACENTO}; background: {SUPERFICIE};
            border-radius: 0 0.5rem 0.5rem 0; padding: 0.85rem 1.1rem; margin: 0.2rem 0 1.8rem;
        }}
        .conclusion-titulo {{
            color: {ACENTO}; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em;
            text-transform: uppercase; margin-bottom: 0.3rem;
        }}
        .conclusion p {{ color: {TEXTO}; line-height: 1.6; margin: 0; font-size: 0.97rem; }}
        .pregunta {{
            font-family: "Newsreader", Georgia, serif; font-size: 1.45rem; font-weight: 500;
            line-height: 1.45; color: {TEXTO}; max-width: 58rem;
            border-left: 3px solid {ACENTO}; padding: 0.15rem 0 0.15rem 1.25rem;
            margin: 0.3rem 0 2rem;
        }}
        @media (max-width: 640px) {{ .pregunta {{ font-size: 1.2rem; padding-left: 1rem; }} }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def encabezado(titulo, bajada=None, antetitulo=None):
    if antetitulo:
        st.markdown(f'<div class="antetitulo">{antetitulo}</div>', unsafe_allow_html=True)
    st.title(titulo)
    if bajada:
        st.markdown(f'<p class="bajada">{bajada}</p>', unsafe_allow_html=True)


def ficha(columna, etiqueta, valor, detalle=""):
    """Tarjeta para valores de texto largos, que st.metric cortaría."""
    with columna.container(border=True, height="stretch"):
        st.markdown(f'<div class="ficha-etiqueta">{etiqueta}</div>'
                    f'<div class="ficha-valor">{valor}</div>'
                    f'<div class="ficha-detalle">{detalle}</div>', unsafe_allow_html=True)


def conclusion(texto, titulo="Lo que muestra"):
    """Lectura sencilla de un gráfico, debajo de él."""
    st.markdown(f'<div class="conclusion"><div class="conclusion-titulo">{titulo}</div>'
                f'<p>{texto}</p></div>', unsafe_allow_html=True)


def pregunta(texto):
    """Pregunta de investigación destacada."""
    st.markdown(f'<div class="pregunta">{texto}</div>', unsafe_allow_html=True)


def nota(texto):
    st.markdown(f'<p class="nota">{texto}</p>', unsafe_allow_html=True)


def grafico(fig, alto=None, key=None, **kwargs):
    """Muestra un gráfico de Plotly con la plantilla de la app (no la de Streamlit)."""
    # Streamlit pinta el área del gráfico con el color secundario del tema si la
    # transparencia solo viene de la plantilla; por eso se fija en cada figura
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    if alto:
        fig.update_layout(height=alto)
    return st.plotly_chart(fig, theme=None, width="stretch", config=CONFIG_GRAFICO,
                           key=key, **kwargs)


def entero(n):
    return f"{n:,.0f}".replace(",", ".")


def decimal(x, d=1):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def porcentaje(x, d=1):
    return f"{decimal(x, d)} %"
