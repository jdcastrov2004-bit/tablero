import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import json, io
from datetime import datetime

st.set_page_config(page_title="Tablero para dibujo", page_icon="🎨", layout="centered")
st.title("🎨 Tablero para dibujo")

with st.sidebar:
    st.subheader("⚙️ Propiedades del tablero")
    canvas_width  = st.slider("Ancho del tablero", 300, 700, 500, 50)
    canvas_height = st.slider("Alto del tablero", 200, 600, 300, 50)
    drawing_mode  = st.selectbox("Herramienta de dibujo",
                                 ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"))
    stroke_width  = st.slider("Grosor de línea", 1, 30, 15)
    stroke_color  = st.color_picker("🎨 Color de trazo", "#FFFFFF")
    bg_color      = st.color_picker("🖼️ Color de fondo", "#000000")

    st.divider()
    st.subheader("✨ Opciones nuevas")
    fill_hex     = st.color_picker("Color de relleno", "#FFA500")
    fill_opacity = st.slider("Opacidad del relleno", 0.0, 1.0, 0.3, 0.05)
    show_grid    = st.toggle("Fondo con cuadrícula", value=False)
    grid_size    = st.slider("Tamaño de cuadrícula", 10, 100, 25, 5, disabled=not show_grid)
    # NOTA: mantenemos el cargador por si quieres usarlo luego, pero no lo pasamos como background_image
    bg_image_file = st.file_uploader("📸 Imagen de fondo (opcional, no usada en esta versión por compatibilidad)",
                                     type=["png", "jpg", "jpeg"])
    show_handles = st.toggle("Mostrar controladores de forma", value=True)

    st.divider()
    if "clear_seed" not in st.session_state:
        st.session_state.clear_seed = 0
    if st.button("🧽 Limpiar tablero"):
        st.session_state.clear_seed += 1

    download_png = st.checkbox("⬇️ Permitir descarga PNG", value=True)
    show_json    = st.checkbox("📁 Ver/descargar JSON", value=False)
    load_json    = st.file_uploader("📂 Cargar archivo JSON", type=["json"])

# Cargar anotaciones si vienen de JSON
base_json = None
if load_json is not None:
    try:
        base_json = json.load(load_json)
    except Exception:
        st.warning("⚠️ No se pudo leer el archivo JSON. Verifica su formato.")

# Construir la cuadrícula como objetos Fabric (sin usar background_image)
def make_grid_json(w: int, h: int, step: int, stroke="#282828"):
    objects = []
    # Líneas verticales
    for x in range(0, w, step):
        objects.append({
            "type": "line",
            "x1": x, "y1": 0, "x2": x, "y2": h,
            "stroke": stroke,
            "strokeWidth": 1,
            "selectable": False,
            "evented": False,
            "excludeFromExport": True
        })
    # Líneas horizontales
    for y in range(0, h, step):
        objects.append({
            "type": "line",
            "x1": 0, "y1": y, "x2": w, "y2": y,
            "stroke": stroke,
            "strokeWidth": 1,
            "selectable": False,
            "evented": False,
            "excludeFromExport": True
        })
    return {"version": "4.6.0", "objects": objects}

grid_json = make_grid_json(canvas_width, canvas_height, grid_size) if show_grid else {"version": "4.6.0", "objects": []}

# Fusionar: cuadrícula (primero) + lo que el usuario cargue (si hay)
def merge_fabric_json(a, b):
    if a is None and b is None: return None
    if a is None: return b
    if b is None: return a
    return {"version": b.get("version", "4.6.0"), "objects": (a.get("objects", []) + b.get("objects", []))}

initial_json = merge_fabric_json(grid_json, base_json)

# st_canvas SIN background_image (para evitar el crash)
canvas_result = st_canvas(
    fill_color=f"rgba({int(fill_hex[1:3],16)},{int(fill_hex[3:5],16)},{int(fill_hex[5:7],16)},{fill_opacity:.3f})",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    background_image=None,                 # ← clave: no usar background_image
    height=canvas_height,
    width=canvas_width,
    drawing_mode=drawing_mode,
    display_toolbar=show_handles,
    initial_drawing=initial_json,
    key=f"canvas_{canvas_width}_{canvas_height}_{st.session_state.clear_seed}",
)

# Exportar PNG / JSON
import io
from PIL import Image as PILImage
from datetime import datetime

col_a, col_b = st.columns(2)

with col_a:
    if download_png and canvas_result.image_data is not None:
        pil_img = PILImage.fromarray(canvas_result.image_data.astype("uint8"))
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

st.caption("✅ La cuadrícula ahora se dibuja como líneas bloqueadas dentro del lienzo (sin background_image), así que no volverá a fallar.")
