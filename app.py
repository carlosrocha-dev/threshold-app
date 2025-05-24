from flask import Flask, request, render_template, send_file
import cv2
import numpy as np
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        threshold_value = int(request.form['threshold'])
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        # Processamento com OpenCV
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        _, threshed = cv2.threshold(img, threshold_value, 255, cv2.THRESH_BINARY)

        result_path = os.path.join(RESULT_FOLDER, f"thresh_{file.filename}")
        cv2.imwrite(result_path, threshed)

        return send_file(result_path, mimetype='image/png')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
