import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import numpy as np
import io, json
from datetime import datetime

st.set_page_config(page_title="Tablero para dibujo", page_icon="🎨", layout="centered")

st.title("🎨 Tablero para dibujo")
st.write(
    "Dibuja, anota y exporta tu lienzo. Mantuvimos todas tus opciones y añadimos extras: "
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
    bg_image_file = st.file_uploader("Imagen de fondo (opcional)", type=["
