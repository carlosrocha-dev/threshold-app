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
    # Ler imagem
    data = np.frombuffer(uploaded_file.read(), np.uint8)
    img_bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_h, img_w = img_rgb.shape[:2]

    # Slider normalizado para threshold (0 a 10)
    thr_norm = st.slider("Valor do Threshold (0-10)", 0.0, 10.0, 5.0, step=0.1)
    threshold_value = int(thr_norm * 25.5)

    # Processamento: Threshold + Canny
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    colored = cv2.bitwise_and(img_rgb, img_rgb, mask=mask)
    low, high = threshold_value, min(threshold_value * 2, 255)
    edges = cv2.Canny(gray, low, high)
    edges_norm = edges.astype(np.float32) / 255.0

    # Overlay vermelho simples
    overlay = colored.astype(np.float32) / 255.0
    red_layer = np.zeros_like(overlay)
    red_layer[..., 0] = 1.0
    w = edges_norm[..., None]
    final = np.clip((overlay * (1 - w) + red_layer * w) * 255, 0, 255).astype(np.uint8)

    # Função para converter para base64
    def to_b64(arr):
        buf = BytesIO()
        Image.fromarray(arr).save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    orig_b64 = to_b64(img_rgb)
    final_b64 = to_b64(final)

    # Determinar altura do componente baseado no tamanho da imagem (max-width 800px)
    max_display_w = 800
    scale = min(1.0, max_display_w / img_w)
    display_h = int(img_h * scale)

    # HTML do controle deslizante na imagem
    html = f"""
    <div style="position:relative; width:100%; max-width:{max_display_w}px;">
      <img src="data:image/png;base64,{orig_b64}" style="width:100%;">  
      <img src="data:image/png;base64,{final_b64}" id="after"  
           style="position:absolute; top:0; left:0; width:100%; clip-path: inset(0 50% 0 0);">  
      <input type="range" min="0" max="100" value="50" id="slider"  
             style="position:absolute; top:0; left:0; width:100%; height:100%; opacity:0; cursor:ew-resize;">  
    </div>
    <script>
      const slider = document.getElementById('slider');
      const after = document.getElementById('after');
      slider.oninput = () => {{ after.style.clipPath = `inset(0 ${{100-slider.value}}% 0 0)`; }};
    </script>
    """
    components.html(html, height=display_h)

