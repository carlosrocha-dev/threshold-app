 de referencia import streamlit as st
import streamlit.components.v1 as components
import cv2
import numpy as np
import base64
import io
import zipfile

# Configuração da página
st.set_page_config(page_title="Gerador de Referencia de Sombra Interativa", layout="centered")
st.title("Comparação Interativa")

# Upload na barra lateral para múltiplas imagens
uploaded_files = st.sidebar.file_uploader(
    "Escolha imagens (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"], accept_multiple_files=True
)

# Função para converter array em base64
def to_b64(arr):
    _, buffer = cv2.imencode('.png', arr)
    return base64.b64encode(buffer).decode()

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.header(f"Imagem: {uploaded_file.name}")
        # Ler imagem e converter para grayscale
        data = np.frombuffer(uploaded_file.read(), np.uint8)
        img_bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        img_h, img_w = gray.shape[:2]

        # Slider de níveis de posterização
        levels = st.slider(
            f"Níveis de Camadas ({uploaded_file.name})", min_value=2, max_value=10, value=4
        )

        # Posterização e máscaras
        bins = np.linspace(0, 256, levels + 1)
        poster = np.zeros_like(gray)
        masks = []
        for i in range(levels):
            mask = (gray >= bins[i]) & (gray < bins[i+1])
            masks.append(mask)
            poster[mask] = int((bins[i] + bins[i+1]) / 2)
        poster[gray >= bins[-2]] = int((bins[-2] + bins[-1]) / 2)

        # Converter para base64 para o slider comparativo
        orig_b64 = to_b64(gray)
        poster_b64 = to_b64(poster)

        # Dimensionar display do slider
        max_display_w = 800
        scale = min(1.0, max_display_w / img_w)
        display_h = int(img_h * scale)

        # HTML e JS do slider interativo com handle
        slider_html = f"""
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
        components.html(slider_html, height=display_h)

        # Preparar miniaturas (25% do tamanho original)
        thumb_w, thumb_h = img_w // 4, img_h // 4
        thumbs_b64 = []
        captions = []
        mid_values = [int((bins[i] + bins[i+1]) / 2) for i in range(levels)]

        for idx, v in enumerate(mid_values):
            mask = masks[idx]
            # primeira normal, demais invertidas
            display = mask if idx == 0 else ~mask
            coords = np.column_stack(np.where(display))
            if coords.size:
                y0, x0 = coords.min(axis=0)
                y1, x1 = coords.max(axis=0)
                crop = display[y0:y1+1, x0:x1+1]
                thumb_img = np.full(crop.shape, 255, dtype=np.uint8)
                thumb_img[crop] = v
            else:
                thumb_img = np.full((1,1), v, dtype=np.uint8)
            thumb = cv2.resize(thumb_img, (thumb_w, thumb_h), interpolation=cv2.INTER_NEAREST)
            thumbs_b64.append(to_b64(thumb))
            pct = v / 255 * 100
            captions.append(f"{pct:.1f}%")

        # Grid interativo com lightbox
        html = f"""
        <style>
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax({thumb_w}px, 1fr)); gap: 10px; }}
        .grid img {{ width: 100%; cursor: pointer; }}
        #lightbox {{ position: fixed; display: none; top: 0; left: 0; width: 100%; height: 100%;
                     background: rgba(0,0,0,0.8); align-items: center; justify-content: center; }}
        #lightbox img {{ max-width: 90%; max-height: 90%; }}
        #close {{ position: absolute; top: 20px; right: 30px; color: white; font-size: 2rem; cursor: pointer; }}
        </style>
        <div class="grid">
        """
        for b64, cap in zip(thumbs_b64, captions):
            html += f'<img src="data:image/png;base64,{b64}" alt="{cap}" />'
        html += """
        </div>
        <div id="lightbox" onclick="if(event.target.id=='lightbox')this.style.display='none';">
            <span id="close" onclick="document.getElementById('lightbox').style.display='none'">&times;</span>
            <img src="" alt="">
        </div>
        <script>
        document.querySelectorAll('.grid img').forEach(img => {
            img.onclick = () => {
                let lb = document.getElementById('lightbox');
                lb.querySelector('img').src = img.src;
                lb.style.display = 'flex';
            }
        });
        </script>
        """
        components.html(html, height=thumb_h*2 + 50)

        # Botões de download
        _, buf_poster = cv2.imencode('.png', poster)
        st.download_button(f'Download da referência', buf_poster.tobytes(),
                           file_name=f'posterizada_{uploaded_file.name}.png', mime='image/png')

        # ZIP com camadas
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w') as zf:
            zf.writestr(f'posterizada_{uploaded_file.name}.png', buf_poster.tobytes())
            for b64, cap in zip(thumbs_b64, captions):
                thumb_data = base64.b64decode(b64)
                zf.writestr(f'{uploaded_file.name}_tom_{cap.replace('.',',')}.png', thumb_data)
        st.download_button(f'Download das camadas e referencia (.ZIP)', zip_buf.getvalue(),
                           file_name=f'conjunto_{uploaded_file.name}.zip', mime='application/zip')
