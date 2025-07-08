import streamlit as st
import streamlit.components.v1 as components
import cv2
import numpy as np
import base64

# Configuração da página
st.set_page_config(page_title="Posterização Interativa", layout="centered")
st.title("Comparação Interativa: Antes vs. Posterizado")

# Upload na barra lateral
uploaded_file = st.sidebar.file_uploader("Escolha uma imagem", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Ler imagem e converter para grayscale
    data = np.frombuffer(uploaded_file.read(), np.uint8)
    img_bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    img_h, img_w = gray.shape[:2]

    # Slider de níveis de posterização
    levels = st.slider("Níveis de Posterização", min_value=2, max_value=10, value=4)

    # Posterização: dividir em bins e atribuir valor médio de cada intervalo
    bins = np.linspace(0, 256, levels + 1)
    poster = np.zeros_like(gray)
    for i in range(levels):
        mask = (gray >= bins[i]) & (gray < bins[i+1])
        poster[mask] = int((bins[i] + bins[i+1]) / 2)
    poster[gray >= 255] = int((bins[-2] + bins[-1]) / 2)

    # Converter array para base64 usando OpenCV
    def to_b64(arr):
        _, buffer = cv2.imencode('.png', arr)
        return base64.b64encode(buffer).decode()

    orig_b64 = to_b64(gray)
    poster_b64 = to_b64(poster)

    # Botão de download da imagem posterizada
    _, poster_buffer = cv2.imencode('.png', poster)
    st.download_button(
        label='Download da imagem posterizada',
        data=poster_buffer.tobytes(),
        file_name='posterizada.png',
        mime='image/png'
    )

    # Preparar miniaturas das áreas correspondentes a cada tom
    mid_values = [int((bins[i] + bins[i+1]) / 2) for i in range(levels)]
    thumbs = []
    captions = []
    for v in mid_values:
        mask = poster == v
        coords = np.column_stack(np.where(mask))
        if coords.size:
            y0, x0 = coords.min(axis=0)
            y1, x1 = coords.max(axis=0)
            crop = poster[y0:y1+1, x0:x1+1]
            # Redimensiona para 50x50 mantendo blocos
            thumb = cv2.resize(crop, (50, 50), interpolation=cv2.INTER_NEAREST)
        else:
            thumb = np.full((50, 50), v, dtype=np.uint8)
        thumbs.append(thumb)
        captions.append(str(v))

    st.subheader("Tons gerados na posterização")
    st.image(
        thumbs,
        width=50,
        clamp=True,
        caption=captions
    )

    # Dimensionar display
    max_display_w = 800
    scale = min(1.0, max_display_w / img_w)
    display_h = int(img_h * scale)

    # HTML e JS do slider interativo
    html = f"""
    <div style="position:relative; width:100%; max-width:{max_display_w}px;">
      <img src="data:image/png;base64,{orig_b64}" style="width:100%;">
      <img src="data:image/png;base64,{poster_b64}" id="after"
           style="position:absolute; top:0; left:0; width:100%; clip-path: inset(0 50% 0 0);">
      <div id="handle" style="position:absolute; top:0; left:50%; width:4px; height:100%; background:rgba(255,255,255,0.8); pointer-events:none;"></div>
      <input type="range" min="0" max="100" value="50" id="slider"
             style="position:absolute; top:0; left:0; width:100%; height:100%; opacity:0; cursor:ew-resize;">
    </div>
    <script>
      const slider = document.getElementById('slider');
      const after = document.getElementById('after');
      const handle = document.getElementById('handle');
      slider.oninput = function() {{
        const val = slider.value;
        after.style.clipPath = 'inset(0 ' + (100 - val) + '% 0 0)';
        handle.style.left = val + '%';
      }};
    </script>
    """
    components.html(html, height=display_h)

