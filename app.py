import streamlit as st
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Threshold Colorido + Edge Detection", layout="centered")
st.title("Threshold Colorido e Detecção de Bordas")

uploaded_file = st.file_uploader("Escolha uma imagem", type=["png", "jpg", "jpeg"])
threshold_value = st.slider("Valor do Threshold", 0, 255, 128)

if uploaded_file is not None:
    file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
    img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    st.subheader("Imagem Original")
    st.image(img_rgb, use_column_width=True)

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)

    colored_thresh = cv2.bitwise_and(img_rgb, img_rgb, mask=mask)
    st.subheader("Threshold Colorido")
    st.image(colored_thresh, use_column_width=True)

    # faz edge detection (Canny) usando threshold_value e threshold_value*2
    low = threshold_value
    high = min(threshold_value * 2, 255)
    edges = cv2.Canny(gray, low, high)

    # overlay em vermelho dos contornos sobre a imagem thresholded
    overlay = colored_thresh.copy()
    overlay[edges > 0] = [255, 0, 0]  # pixels de contorno em vermelho

    st.subheader("Detecção de Bordas (overlay vermelho)")
    st.image(overlay, use_column_width=True)

    # botão de download do resultado final
    buf = BytesIO()
    Image.fromarray(overlay).save(buf, format="PNG")
    st.download_button(
        label="Download da Imagem Processada",
        data=buf.getvalue(),
        file_name="threshold_edges.png",
        mime="image/png"
    )
