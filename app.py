import streamlit as st
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Threshold Colorido + Bordas Suaves", layout="centered")
st.title("Threshold Colorido e Detecção de Bordas Suaves")

uploaded_file = st.file_uploader("Escolha uma imagem", type=["png", "jpg", "jpeg"])
threshold_value = st.slider("Valor do Threshold", 0, 255, 128)
sigma = st.selectbox(
    "Suavização das bordas (sigma)",
    options=[0, 2, 4, 6, 8],
    index=0
)

if uploaded_file is not None:
    # Carrega e converte a imagem
    file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
    img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    st.subheader("Imagem Original")
    st.image(img_rgb, use_column_width=True)

    # Threshold colorido
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    colored_thresh = cv2.bitwise_and(img_rgb, img_rgb, mask=mask)
    st.subheader("Threshold Colorido")
    st.image(colored_thresh, use_colu

