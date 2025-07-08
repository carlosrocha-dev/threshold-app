import streamlit as st
import streamlit.components.v1 as components
import cv2
import numpy as np
import base64

# Configuração da página
st.set_page_config(page_title="Posterização Interativa", layout="centered")
st.title("Comparação Interativa: Antes vs. Posterizado")

# Upload na barra lateral para múltiplas imagens
downloads = []
uploaded_files = st.sidebar.file_uploader(
    "Escolha imagens (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"], accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.header(f"Imagem: {uploaded_file.name}")
        # Ler imagem e converter para grayscale
        data = np.frombuffer(uploaded_file.read(), np.uint8)
        img_bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        img_h, img_w = gray.shape[:2]

        # Slider de níveis de posterização
        levels = st.slider(f"Níveis de Posterização ({uploaded_file.name})", min_value=2, max_value=10, value=4)

        # Posterização: dividir em bins e atribuir valor médio de cada intervalo
        bins = np.linspace(0, 256, levels + 1)
        poster = np.zeros_like(gray)
        for i in range(levels):
            mask = (gray >= bins[i]) & (gray < bins[i+1])
            poster[mask] = int((bins[i] + bins[i+1]) / 2)
        poster[gray >= 255] = int((bins[-2] + bins[-1]) / 2)

        # Botão de download da imagem posterizada
        _, poster_buffer = cv2.imencode('.png', poster)
        st.download_button(
            label=f'Download da posterizada ({uploaded_file.name})',
            data=poster_buffer.tobytes(),
            file_name=f'posterizada_{uploaded_file.name}',
            mime='image/png'
        )

        # Preparar miniaturas das áreas correspondentes a cada tom
        mid_values = [int((bins[i] + bins[i+1]) / 2) for i in range(levels)]
        thumbs = []
        captions = []
        # tamanho da thumb como metade da imagem original
        thumb_w, thumb_h = img_w // 2, img_h // 2
        for v in mid_values:
            mask_v = (poster == v)
            coords = np.column_stack(np.where(mask_v))
            if coords.size:
                y0, x0 = coords.min(axis=0)
                y1, x1 = coords.max(axis=0)
                crop_mask = mask_v[y0:y1+1, x0:x1+1]
                # criar imagem onde só o tom aparece, fundo branco
                thumb_img = np.full(crop_mask.shape, 255, dtype=np.uint8)
                thumb_img[crop_mask] = v
            else:
                # se não encontrou pixels, criar bloco do tom
                thumb_img = np.full((1,1), v, dtype=np.uint8)
            # redimensiona para metade da imagem original
            thumb = cv2.resize(thumb_img, (thumb_w, thumb_h), interpolation=cv2.INTER_NEAREST)
            thumbs.append(thumb)
            # legenda em porcentagem do tom
            pct = v / 255 * 100
            captions.append(f"{pct:.1f}%")

        st.subheader("Tons gerados na posterização")
        st.image(
            thumbs,
            width=None,
            caption=captions,
            clamp=True
        )

        # Converter array para base64 para o slider interativo
        def to_b64(arr):
            _, buffer = cv2.imencode('.png', arr)
            return base64.b64encode(buffer).decode()

        orig_b64 = to_b64(gray)
        poster_b64 = to_b64(poster)

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
