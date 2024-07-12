from flask import Flask, render_template, request
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import os
app = Flask(__name__)
UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# Load the deepfake detection model
model = load_model('./model/deepfake_detection_model.h5')

# Render the index page
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/prediction')
def redirect():
    return render_template('prediction.html')
@app.route('/predict', methods=['GET', 'POST'])
def prediction():
    if request.method == 'POST':
        # Check if the file is uploaded
        if 'file' not in request.files:
            return render_template('prediction.html', prediction_result='No file uploaded')

        # Get the uploaded image file
        uploaded_image = request.files['file']

        # Check if the file is empty
        if uploaded_image.filename == '':
            return render_template('prediction.html', prediction_result='No file selected')

        # Check if the file format is allowed
        if uploaded_image and allowed_file(uploaded_image.filename):
            # Save the uploaded image
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            uploaded_image.save(os.path.join(app.config['UPLOAD_FOLDER'], "image"))

        # Get the image file path for preview
            image_path = os.path.join(app.config['UPLOAD_FOLDER'],"image")
            # Preprocess the uploaded image for prediction
            print(image_path)
            img = Image.open(image_path)
            img = img.resize((128, 128))
            img_array = np.array(img)
            img_array = img_array / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            # Make prediction using the loaded model
            prediction = model.predict(img_array)
            pre=prediction[0][0]
            scores=float(prediction[0][0])
            score=round(scores,4)
            # Interpret the prediction
            if pre > 0.5:
                result = f'This image contains a deepfake with confidence of {score*100}%'
            else:
                result = f'This image is real with confidence of {(1-score)*100}%'

            return render_template('prediction.html', uploaded_image=image_path, prediction_result=result)
        else:
            return render_template('prediction.html', prediction_result='Invalid file format')
    else:
        return render_template('prediction.html')
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

if __name__ == '__main__':
    app.run(debug=True)
