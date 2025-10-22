import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import numpy as np
import io, json
from datetime import datetime

st.set_page_config(page_title="Tablero para dibujo", page_icon="🎨", layout="centered")

st.title("🎨 Tablero para dibujo")
st.write(
    "Dibuja, anota y exporta tu lienzo. Mantuvimos todas tus opciones y añadimos extras útiles: "
    "**relleno con opacidad**, **fondo con imagen o cuadrícula**, **borrar rápido**, "
    "**descargar PNG**, **guardar/cargar JSON** y **marcadores de tamaño**."
)

with st.sidebar:
    st.subheader("Propiedades del Tablero")
    st.subheader("Dimensiones del Tablero")
    canvas_width = st.slider("Ancho del tablero", 300, 700, 500, 50)
    canvas_height = st.slider("Alto del tablero", 200, 600, 300, 50)

    drawing_mode = st.selectbox(
        "Herramienta de Dibujo:",
        ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
    )

    stroke_width = st.slider("Selecciona el ancho de línea", 1, 30, 15)
    stroke_color = st.color_picker("Color de trazo", "#FFFFFF")
    bg_color = st.color_picker("Color de fondo", "#000000")

    st.divider()
    st.subheader("Opciones nuevas")
    fill_hex = st.color_picker("Color de relleno", "#FFA500")
    fill_opacity = st.slider("Opacidad del relleno", 0.0, 1.0, 0.3, 0.05)
    show_grid = st.toggle("Fondo con cuadrícula", value=False)
    grid_size = st.slider("Tamaño de celda", 10, 100, 25, 5, disabled=not show_grid)
    bg_image_file = st.file_uploader("Imagen de fondo (opcional)", type=["png", "jpg", "jpeg"])
    show_handles = st.toggle("Mostrar marcadores de tamaño", value=True)

    st.divider()
    if "clear_seed" not in st.session_state:
        st.session_state.clear_seed = 0
    if st.button("🧽 Limpiar tablero"):
        st.session_state.clear_seed += 1

    download_png = st.checkbox("Preparar descarga PNG", value=True)
    show_json = st.checkbox("Ver/descargar JSON de anotaciones", value=False)
    load_json_file = st.file_uploader("Cargar JSON de anotaciones", type=["json"])

initial_json = None
if load_json_file is not None:
    try:
        initial_json = json.load(load_json_file)
    except Exception:
        st.warning("No se pudo leer el JSON. Verifica el formato.")

def rgba_from_hex(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha:.3f})"

bg_image = None
if show_grid:
    grid = Image.new("RGB", (canvas_width, canvas_height), color=(0, 0, 0))
    draw = ImageDraw.Draw(grid)
    for x in range(0, canvas_width, grid_size):
        draw.line([(x, 0), (x, canvas_height)], fill=(40, 40, 40))
    for y in range(0, canvas_height, grid_size):
        draw.line([(0, y), (canvas_width, y)], fill=(40, 40, 40))
    bg_image = grid
elif bg_image_file is not None:
    img = Image.open(bg_image_file).convert("RGB")
    bg_image = img.resize((canvas_width, canvas_height))

canvas_result = st_canvas(
    fill_color=rgba_from_hex(fill_hex, fill_opacity),
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=None if bg_image is not None else bg_color,
    background_image=bg_image if bg_image is not None else None,
    height=canvas_height,
    width=canvas_width,
    drawing_mode=drawing_mode,
    display_toolbar=show_handles,
    initial_drawing=initial_json,
    key=f"canvas_{canvas_width}_{canvas_height}_{st.session_state.clear_seed}",
)

col_a, col_b = st.columns(2)

with col_a:
    if download_png and canvas_result.image_data is not None:
        pil_img = Image.fromarray(canvas_result.image_data.astype("uint8"))
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        buf.seek(0)
        fname = f"canvas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        st.download_button("⬇️ Descargar PNG", data=buf, file_name=fname, mime="image/png")

with col_b:
    if show_json and canvas_result.json_data is not None:
        json_str = json.dumps(canvas_result.json_data, ensure_ascii=False, indent=2)
        st.code(json_str, language="json")
        st.download_button(
            "💾 Descargar JSON",
            data=json_str.encode("utf-8"),
            file_name=f"canvas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )

st.caption("Tip: activa el fondo con cuadrícula para guiar trazos y alineación; ajusta la opacidad del relleno para ver el contenido debajo mientras dibujas.")
