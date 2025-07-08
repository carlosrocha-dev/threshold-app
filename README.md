# Interactive Shadow Reference Generator”

----

## Features:

- Multi-Image Upload: Users can upload one or more PNG/JPG/JPEG files via the sidebar.

- Grayscale Conversion & Posterization: Each image is converted to grayscale and then split into a user-configurable number of tonal “layers.”

- Before-vs-After Slider: An HTML/JS slider overlays the original and posterized grayscale, letting you swipe between them with a draggable handle.

- Layer Thumbnails & Lightbox: For each tonal layer, the app generates a 25%-sized thumbnail (first layer as is; subsequent layers inverted). Clicking a thumbnail opens a full-resolution view in a fullscreen lightbox.

## Download Options:

- A “Download Reference” button exports the combined posterized image.

- A ZIP download bundles the posterized image plus each individual layer as separate PNGs.

Everything is implemented client-side with OpenCV for image processing, base64 encoding for embedding in HTML, and Streamlit’s built-in components for UI and downloads.

-

<img width="1792" alt="Captura de Tela 2025-07-08 às 18 15 17" src="https://github.com/user-attachments/assets/59616168-218b-4545-9b97-1ccc0ac21830" />


[threshold-app](https://threshold-app.streamlit.app/)
