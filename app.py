# Título: Proyecto 3 - Interfaz Web con Streamlit
# Autor: Diego Vázquez Hernández
# Fecha: 16/11/2026
# Descripción: Interfaz web en Streamlit para administrar la red de nodos.
"""
Objetivo: Agregar conexiones a nodos.csv, ver la red en una tabla y
    calcular la ruta más corta con Dijkstra desde el navegador,
    reutilizando grafo.py e io_handler.py.

Ejecución: streamlit run app.py
"""

import base64
import html
import io
from contextlib import redirect_stdout
from pathlib import Path

import pandas as pd
import streamlit as st

from grafo import Grafo
from io_handler import (
    cargar_grafo,
    formatear_peso,
    guardar_arista,
    normalizar_nodo,
    validar_peso,
)

RUTA_FONDO: Path = Path(__file__).resolve().parent / "fondo.jpg"
DEGRADADO: str = (
    "linear-gradient(180deg, #4a4aa5 0%, #b56aa8 45%, "
    "#ff9f7a 75%, #ffd2a4 100%) fixed"
)

FUENTES: str = (
    "https://fonts.googleapis.com/css2?"
    "family=DM+Sans:wght@400;500;700&family=Unbounded:wght@600"
    "&display=swap"
)

ESTILOS: str = """
<style>
@import url('__FUENTES__');

.stApp {
    background: __FONDO__;
    color: #fff3e8;
    color-scheme: dark;
}
.stApp, .stApp p, .stApp label, .stApp li, .stApp input,
.stApp button, .stApp [role="tab"] {
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stAppDeployButton"], .stDeployButton, footer {
    display: none !important;
}

/* Panel central: la imagen queda visible a los lados */
[data-testid="stMainBlockContainer"], .block-container {
    max-width: 820px !important;
    margin: 0 auto !important;
    padding: 3.5rem 2.2rem 4rem !important;
    background: rgba(22, 11, 44, .86) !important;
    border-left: 1px solid rgba(255, 255, 255, .14);
    border-right: 1px solid rgba(255, 255, 255, .14);
    box-shadow: 0 0 60px rgba(20, 8, 40, .55);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}

/* Colores de texto forzados para que siempre se lean */
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stWidgetLabel"] p,
.stApp label, .stApp li { color: #fff3e8 !important; }

.titulo {
    font-family: 'Unbounded', sans-serif;
    font-weight: 600;
    font-size: clamp(1.5rem, 3.8vw, 2.2rem);
    line-height: 1.12;
    letter-spacing: -0.02em;
    color: #fff;
    margin: 0 0 .9rem;
}
.subtitulo {
    max-width: 34rem;
    font-size: 1.08rem;
    line-height: 1.55;
    color: #ffd9b0;
    margin-bottom: 2rem;
}

/* Barra de sección, como los encabezados del perfil de Steam */
.barra {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 1rem;
    padding: .65rem 1.1rem;
    margin-bottom: .6rem;
    border-radius: 10px;
    background: linear-gradient(90deg, #ff6f9c, #ffa95c);
    color: #1e1038;
    font-weight: 700;
}
.barra small { font-weight: 500; opacity: .8; }

/* Pestañas */
.stTabs [role="tablist"] {
    gap: .3rem !important;
    width: fit-content;
    padding: .3rem !important;
    border-radius: 999px;
    background: rgba(255, 255, 255, .08) !important;
}
.stTabs [role="tab"] {
    height: auto !important;
    padding: .45rem 1.2rem !important;
    border-radius: 999px !important;
    color: #ffe9d6 !important;
}
.stTabs [role="tab"] p { color: #ffe9d6 !important; }
.stTabs [role="tab"][aria-selected="true"] {
    background: linear-gradient(90deg, #ff7aa8, #ffb561) !important;
}
.stApp .stTabs [role="tab"][aria-selected="true"] p {
    color: #1e1038 !important;
    font-weight: 700;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [role="tabpanel"] {
    margin-top: 1rem;
    padding: 1.2rem 1.3rem 1.5rem !important;
    border: 1px solid rgba(255, 255, 255, .12);
    border-radius: 14px;
    background: rgba(0, 0, 0, .28) !important;
}

/* Campos de texto y listas */
[data-testid="stForm"] {
    border: 0 !important;
    padding: 0 !important;
    background: transparent !important;
}
[data-baseweb="input"], [data-baseweb="select"] > div {
    border: 1px solid rgba(255, 255, 255, .22) !important;
    border-radius: 12px !important;
    background: rgba(255, 255, 255, .08) !important;
}
[data-baseweb="input"] > div { background: transparent !important; }
[data-baseweb="input"] input, [data-baseweb="select"] div,
[data-baseweb="select"] span {
    color: #fff !important;
    -webkit-text-fill-color: #fff;
}
[data-baseweb="select"] svg { fill: #fff !important; }
input::placeholder { color: rgba(255, 243, 232, .5) !important; }
[data-baseweb="popover"] > div, [data-baseweb="popover"] ul,
[data-baseweb="popover"] li {
    background: #2b1a4f !important;
    color: #fff3e8 !important;
}
[data-baseweb="popover"] li:hover { background: #4a2f7a !important; }

/* Botón */
[data-testid="stFormSubmitButton"] button {
    border: 0 !important;
    border-radius: 999px !important;
    padding: .5rem 1.7rem !important;
    background: linear-gradient(90deg, #ff6f9c, #ffa95c) !important;
}
.stApp [data-testid="stFormSubmitButton"] button p {
    color: #1e1038 !important;
    font-weight: 700;
}

/* Mensajes, desplegables y tablas */
[data-testid="stAlert"] {
    border: 1px solid rgba(255, 255, 255, .2) !important;
    border-radius: 12px !important;
    background: rgba(255, 255, 255, .1) !important;
}
[data-testid="stAlert"] * { color: #fff3e8 !important; }
[data-testid="stExpander"] details {
    border-color: rgba(255, 255, 255, .15) !important;
    background: rgba(255, 255, 255, .05) !important;
}
[data-testid="stExpander"] * { color: #fff3e8 !important; }
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255, 255, 255, .15);
    border-radius: 12px;
    overflow: hidden;
}
.stApp [data-testid="stCaptionContainer"] p,
.stApp [data-testid="stCaptionContainer"] * {
    color: rgba(255, 243, 232, .72) !important;
}

/* Resultado de la ruta */
ol li::marker { color: #ffb561; font-weight: 700; }
.ruta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: .5rem;
    margin: .6rem 0 .4rem;
}
.pill {
    padding: .35rem 1.05rem;
    border-radius: 999px;
    background: linear-gradient(135deg, #ff7aa8, #ffb561);
    color: #1e1038;
    font-size: 1.15rem;
    font-weight: 700;
}
.sep { color: #ffd9b0; }
.total { color: #ffd9b0; margin-bottom: 1.2rem; }
.total b { color: #fff; font-size: 1.35rem; }
[data-testid="stGraphVizChart"] svg { max-width: 100%; height: auto; }
</style>
"""


@st.cache_data
def estilos() -> str:
    """Devuelve el CSS con la imagen de fondo incrustada (o un degradado)."""
    fondo = DEGRADADO
    if RUTA_FONDO.exists():
        datos = base64.b64encode(RUTA_FONDO.read_bytes()).decode()
        fondo = (
            "linear-gradient(rgba(30, 16, 56, .15), rgba(30, 16, 56, .15)), "
            f"url(data:image/jpeg;base64,{datos}) center / cover fixed"
        )
    css = ESTILOS.replace("__FUENTES__", FUENTES)
    return css.replace("__FONDO__", fondo)


def barra(titulo: str, detalle: str = "") -> str:
    """Devuelve el HTML de una barra de sección (estilo perfil de Steam)."""
    extra = f"<small>{html.escape(detalle)}</small>" if detalle else ""
    nombre = html.escape(titulo)
    return f'<div class="barra"><span>{nombre}</span>{extra}</div>'


def obtener_grafo() -> Grafo:
    """Devuelve el grafo guardado en st.session_state.

    El CSV se lee del disco solo la primera vez que se ejecuta la sesión
    (cuando la clave 'grafo' todavía no existe). En las demás
    interacciones se reutiliza el objeto que ya está en memoria.
    """
    if "grafo" not in st.session_state:
        # cargar_grafo() imprime sus avisos; se capturan para mostrarlos
        salida = io.StringIO()
        with redirect_stdout(salida):
            st.session_state["grafo"] = cargar_grafo()
        lineas = [lin.strip() for lin in salida.getvalue().splitlines()]
        st.session_state["avisos"] = [lin for lin in lineas if lin]
    return st.session_state["grafo"]


def comillas(texto: str) -> str:
    """Escapa un nombre de nodo para usarlo en el lenguaje DOT."""
    return '"' + texto.replace("\\", "\\\\").replace('"', '\\"') + '"'


def dibujar_red(grafo: Grafo, camino: list[str]) -> str:
    """Genera el grafo en formato DOT, resaltando los nodos de la ruta."""
    ruta = {frozenset(par) for par in zip(camino, camino[1:])}
    lineas = [
        "graph {",
        'bgcolor="transparent"; rankdir=LR; pad=0.2;',
        'node [shape=circle, style=filled, fontname="Helvetica", '
        "fontsize=13, penwidth=1.5];",
        'edge [fontname="Helvetica", fontsize=11];',
    ]
    for nombre in sorted(grafo.nodos):
        if nombre in camino:
            estilo = 'fillcolor="#FF8FB1", color="#FFD9B0", '
            estilo += 'fontcolor="#1E1038"'
        else:
            estilo = 'fillcolor="#2B1A4F", color="#C9A7E8", '
            estilo += 'fontcolor="#FFFFFF"'
        lineas.append(f"{comillas(nombre)} [{estilo}];")

    for origen, destino, peso in grafo.conexiones():
        if frozenset((origen, destino)) in ruta:
            estilo = 'color="#FFB561", fontcolor="#FFB561", penwidth=3.5'
        else:
            estilo = 'color="#FFFFFF66", fontcolor="#FFE9D6"'
        lineas.append(
            f'{comillas(origen)} -- {comillas(destino)} '
            f'[label="{formatear_peso(peso)}", {estilo}];'
        )
    lineas.append("}")
    return "\n".join(lineas)


def tabla_conexiones(grafo: Grafo) -> pd.DataFrame:
    """Construye un DataFrame con cada conexión (Origen, Destino, Peso)."""
    datos = pd.DataFrame(
        grafo.conexiones(), columns=["Origen", "Destino", "Peso"]
    )
    return datos.sort_values(["Origen", "Destino"], ignore_index=True)


def tabla_nodos(grafo: Grafo) -> pd.DataFrame:
    """Construye un DataFrame con el catálogo de nodos y sus vecinos."""
    filas = [
        {
            "Nodo": nombre,
            "Conexiones": len(nodo.vecinos),
            "Vecinos": ", ".join(sorted(nodo.vecinos)),
        }
        for nombre, nodo in sorted(grafo.nodos.items())
    ]
    return pd.DataFrame(filas, columns=["Nodo", "Conexiones", "Vecinos"])


def seccion_explicacion() -> None:
    """Pestaña con la explicación de uso."""
    st.markdown(barra("Cómo funciona"), unsafe_allow_html=True)
    st.markdown(
        "Tu red está hecha de **nodos** (estaciones, paradas, ciudades) "
        "unidos por **conexiones** con un peso: la distancia, el tiempo o "
        "el costo de ir de uno a otro. El algoritmo de Dijkstra compara "
        "todos los caminos posibles y te da el de menor peso total."
    )
    st.markdown(
        "1. En **Agregar conexión**, escribe dos nodos y el peso que los "
        "une.\n"
        "2. En **Calcular ruta**, escribe dónde empiezas y dónde "
        "terminas.\n"
        "3. Revisa el recorrido, el peso total y el mapa con la ruta "
        "resaltada.\n"
        "4. En **Ver red**, consulta la tabla con todas las conexiones."
    )
    st.caption(
        "Las conexiones van en ambos sentidos. Los nombres se guardan en "
        "mayúsculas (a y A son el mismo nodo). El peso debe ser un número "
        "mayor o igual a cero, con punto decimal. Si repites una conexión, "
        "se conserva el último peso."
    )


def seccion_agregar(grafo: Grafo) -> None:
    """Pestaña con el formulario para guardar una nueva conexión."""
    st.markdown(
        barra("Nueva conexión", "se guarda en nodos.csv"),
        unsafe_allow_html=True,
    )
    with st.form("nueva_conexion", clear_on_submit=True):
        col1, col2 = st.columns(2)
        origen_txt = col1.text_input("Nodo origen", placeholder="A")
        destino_txt = col2.text_input("Nodo destino", placeholder="B")
        peso_txt = st.text_input(
            "Peso de la conexión",
            placeholder="4.5",
            help="Número mayor o igual a cero, con punto decimal.",
        )
        enviado = st.form_submit_button("Guardar conexión")

    if not enviado:
        return
    try:
        origen = normalizar_nodo(origen_txt)
        destino = normalizar_nodo(destino_txt)
        if origen == destino:
            raise ValueError("El destino debe ser distinto al origen.")
        peso = validar_peso(peso_txt)
        guardar_arista(origen, destino, peso)
    except ValueError as error:
        st.error(str(error))
    except PermissionError:
        st.error("No hay permiso para escribir en nodos.csv.")
    except OSError as error:
        st.error(f"No se pudo guardar en el archivo: {error}")
    else:
        # Se actualiza el grafo en memoria sin volver a leer el CSV
        grafo.agregar_arista(origen, destino, peso)
        st.session_state.pop("ruta", None)  # la ruta anterior ya no aplica
        st.success(
            f"Conexión guardada: {origen} ↔ {destino} "
            f"(peso {formatear_peso(peso)})."
        )


def mostrar_resultado() -> list[str]:
    """Muestra la última ruta calculada y devuelve su camino."""
    resultado = st.session_state.get("ruta")
    if resultado is None:
        return []

    inicio, destino, distancia, camino = resultado
    if not camino:
        st.warning(f"No existe una ruta entre {inicio} y {destino}.")
        return []

    pasos = '<span class="sep">→</span>'.join(
        f'<span class="pill">{html.escape(n)}</span>' for n in camino
    )
    st.markdown(
        f'<div class="ruta">{pasos}</div>'
        f'<div class="total">Peso total: '
        f"<b>{formatear_peso(distancia)}</b></div>",
        unsafe_allow_html=True,
    )
    return camino


def seccion_ruta(grafo: Grafo) -> None:
    """Pestaña para calcular la ruta más corta con Dijkstra."""
    st.markdown(
        barra("Ruta más corta", f"{len(grafo.nodos)} nodos"),
        unsafe_allow_html=True,
    )
    if not grafo.nodos:
        st.info("Todavía no hay conexiones. Agrega la primera para empezar.")
        return

    with st.form("calcular_ruta"):
        col1, col2 = st.columns(2)
        inicio_txt = col1.text_input("Desde", placeholder="A")
        destino_txt = col2.text_input("Hasta", placeholder="F")
        enviado = st.form_submit_button("Calcular ruta")
    st.caption("Nodos disponibles: " + ", ".join(sorted(grafo.nodos)))

    if enviado:
        try:
            inicio = normalizar_nodo(inicio_txt)
            destino = normalizar_nodo(destino_txt)
            # Validar que ambos nodos existan antes de correr Dijkstra
            for nombre in (inicio, destino):
                if nombre not in grafo.nodos:
                    raise KeyError(nombre)
            distancia, camino = grafo.dijkstra(inicio, destino)
        except ValueError as error:
            st.error(str(error))
        except KeyError as error:
            st.error(f"El nodo '{error.args[0]}' no existe en la red.")
        else:
            st.session_state["ruta"] = (inicio, destino, distancia, camino)

    camino = mostrar_resultado()
    st.graphviz_chart(dibujar_red(grafo, camino))


def seccion_red(grafo: Grafo) -> None:
    """Pestaña con la red actual en tablas de pandas."""
    conexiones = tabla_conexiones(grafo)
    st.markdown(
        barra("Red actual", f"{len(conexiones)} conexiones"),
        unsafe_allow_html=True,
    )
    if conexiones.empty:
        st.info("Todavía no hay conexiones registradas.")
        return

    st.dataframe(conexiones, hide_index=True)
    with st.expander(f"Catálogo de nodos ({len(grafo.nodos)})"):
        st.dataframe(tabla_nodos(grafo), hide_index=True)


def main() -> None:
    """Construye la página."""
    st.set_page_config(page_title="Ruta más corta", page_icon="🌴")
    st.markdown(estilos(), unsafe_allow_html=True)
    st.markdown(
        '<div class="titulo">Encuentra la ruta más corta</div>'
        '<div class="subtitulo">Conecta los puntos de tu red de transporte '
        "y descubre el camino de menor peso entre dos de ellos.</div>",
        unsafe_allow_html=True,
    )

    grafo = obtener_grafo()

    # Avisos de la lectura inicial del CSV (archivo faltante, filas malas)
    for aviso in st.session_state.get("avisos", []):
        st.warning(aviso)

    tab_info, tab_agregar, tab_ruta, tab_red = st.tabs(
        ["Cómo funciona", "Agregar conexión", "Calcular ruta", "Ver red"]
    )
    with tab_info:
        seccion_explicacion()
    with tab_agregar:
        seccion_agregar(grafo)
    with tab_ruta:
        seccion_ruta(grafo)
    with tab_red:
        seccion_red(grafo)


main()
