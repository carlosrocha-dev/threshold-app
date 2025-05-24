import streamlit as st
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Threshold de Imagem", layout="centered")
st.title("Aplicação de Threshold em Imagens")

uploaded_file = st.file_uploader("Escolha uma imagem", type=["png", "jpg", "jpeg"])
threshold_value = st.slider("Valor do threshold", 0, 255, 128)

if uploaded_file is not None:
    # Mostrar preview
    image = Image.open(uploaded_file).convert("L")
    img_array = np.array(image)

    st.subheader("Pré-visualização da Imagem Original")
    st.image(image, use_column_width=True, caption="Imagem em tons de cinza")

    # Aplicar threshold
    _, threshed = cv2.threshold(img_array, threshold_value, 255, cv2.THRESH_BINARY)
    result_image = Image.fromarray(threshed)

    st.subheader("Resultado da Imagem com Threshold")
    st.image(result_image, use_column_width=True, caption="Imagem binarizada")

    # Gerar imagem para download
    buf = BytesIO()
    result_image.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="Download da Imagem Processada",
        data=byte_im,
        file_name="threshold_result.png",
        mime="image/png"
    )
