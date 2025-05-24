import streamlit as st
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Threshold Colorido + Bordas Suaves", layout="centered")
st.title("Threshold Colorido e Detecção de Bordas Suaves")

# Upload
uploaded_file = st.file_uploader("Escolha uma imagem", type=["png", "jpg", "jpeg"])

# Slider de threshold
threshold_value = st.slider("Valor do Threshold", 0, 255, 128)

# Pré-definições de suavização (sigma para GaussianBlur)
sigma = st.selectbox(
    "Suavização das bordas (sigma)",
    options=[0, 2, 4, 6, 8],
    index=0
)

if uploaded_file is not None:
    # Leitura da imagem em BGR e conversão para RGB
    file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
    img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    st.subheader("Imagem Original")
    st.image(img_rgb, use_column_width=True)

    # --- Threshold colorido ---
    # cria máscara a partir de luminância
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    colored_thresh = cv2.bitwise_and(img_rgb, img_rgb, mask=mask)

    st.subheader("Threshold Colorido")
    st.image(colored_thresh, use_column_width=True)

    # --- Detecção de bordas ---
    low = threshold_value
    high = min(threshold_value * 2, 255)
    edges = cv2.Canny(gray, low, high)

    # --- Suavização das bordas ---
    if sigma > 0:
        # normalize edges mask para [0,1]
        edges_norm = (edges.astype(np.float32) / 255.0)
        # aplica Gaussian Blur no mapa de bordas
        edges_blur = cv2.GaussianBlur(edges_norm, ksize=(0, 0), sigmaX=sigma)
    else:
        edges_blur = (edges.astype(np.float32) / 255.0)

    # --- Overlay vermelho suave ---
    # gera overlay a partir de weighted blend
    overlay = colored_thresh.astype(np.float32) / 255.0
    red_layer = np.zeros_like(overlay)
    red_layer[..., 0] = 1.0  # canal R em 1

    # blend: final = orig*(1 - w) + red*w
    w = edges_blur[..., None]  # shape H×W×1
    final = overlay * (1.0 - w) + red_layer * w
    final = np.clip(final * 255, 0, 255).astype(np.uint8)

    st.subheader("Bordas (overlay vermelho suave)")
    st.image(final, use_column_width=True)

    # --- Download ---
    buf = BytesIO()
    Image.fromarray(final).save(buf, format="PNG")
    st.download_button(
        label="Download da Imagem Processada",
        data=buf.getvalue(),
        file_name="threshold_edges_suaves.png",
        mime="image/png"
    )
