import streamlit as st
import streamlit.components.v1 as components
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import base64

# Configuração da página
st.set_page_config(page_title="Comparação Interativa", layout="centered")
st.title("Comparação Interativa: Antes vs. Processada")

# Upload na barra lateral
uploaded_file = st.sidebar.file_uploader("Escolha uma imagem", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Ler imagem e converter para grayscale
    data = np.frombuffer(uploaded_file.read(), np.uint8)
    img_bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    img_h, img_w = gray.shape[:2]

    # Slider normalizado para threshold (0 a 10)
    thr_norm = st.slider("Valor do Threshold (0-10)", 0.0, 10.0, 5.0, step=0.1)
    threshold_value = int(thr_norm * 25.5)

    # Aplicar threshold
    _, mask = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    # Suavizar mask com Gaussian Blur (bordas suaves)
    mask_norm = mask.astype(np.float32) / 255.0
    mask_blur = cv2.GaussianBlur(mask_norm, ksize=(0, 0), sigmaX=2)
    final_gray = np.clip(mask_blur * 255, 0, 255).astype(np.uint8)

    # Função para converter para base64
    def to_b64(arr):
        buf = BytesIO()
        Image.fromarray(arr).save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    orig_b64 = to_b64(gray)
    final_b64 = to_b64(final_gray)

    # Ajuste de display
    max_display_w = 800
    scale = min(1.0, max_display_w / img_w)
    display_h = int(img_h * scale)

    # HTML com handle visível no controle deslizante
    html = f"""
    <div style="position:relative; width:100%; max-width:{max_display_w}px;">
      <img src="data:image/png;base64,{orig_b64}" style="width:100%;">
      <img src="data:image/png;base64,{final_b64}" id="after" 
           style="position:absolute; top:0; left:0; width:100%; clip-path: inset(0 50% 0 0);">
      <!-- handle visível -->
      <div id="handle" style="position:absolute; top:0; left:50%; width:4px; height:100%; 
           background:rgba(255,255,255,0.8); pointer-events:none;"></div>
      <!-- input invisível para captura -->
      <input type="range" min="0" max="100" value="50" id="slider"
             style="position:absolute; top:0; left:0; width:100%; height:100%; opacity:0; cursor:ew-resize;">
    </div>
    <script>
      const slider = document.getElementById('slider');
      const after = document.getElementById('after');
      const handle = document.getElementById('handle');
      slider.oninput = () => {{
        const val = slider.value;
        after.style.clipPath = `inset(0 ${100 - val}% 0 0)`;
        handle.style.left = `${val}%`;
      }};
    </script>
    """
    components.html(html, height=display_h)
