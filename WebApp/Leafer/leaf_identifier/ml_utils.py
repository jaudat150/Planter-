from django.conf import settings
import numpy as np
from tensorflow.keras.models import load_model#type:ignore
from tensorflow.keras.preprocessing.image import img_to_array, load_img#type:ignore
import os
from django.conf import settings


IMG_SIZE = (224, 224)
# Load model once when the module is imported (on server run so we dont have to load it again on each request)
MODEL_PATH = os.path.join(settings.MODELS_DIR, 'best_model ID_2.h5')
model = load_model(MODEL_PATH)
print(f"✅ Model loaded from: {MODEL_PATH}")


CLASS_NAMES = [
    "bacterial_spot",
    "early_blight",
    "healthy",
    "late_blight",
    "powdery_mildew",
    "rust"]
def predict_image(image_file):
    """
    Takes a Django UploadedFile object (from request.FILES),
    processes it, and returns the predicted class and confidence.
    """
    try:
        # Save the uploaded image temporarily to disk
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_upload.jpg')

        # Write the uploaded file to a temporary location
        with open(temp_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        # Load and preprocess the image
        img = load_img(temp_path, target_size=IMG_SIZE)
        img_array = img_to_array(img) / 255.0
        img_batch = np.expand_dims(img_array, axis=0)

        # Predict
        prediction = model.predict(img_batch)
        predicted_class_index = np.argmax(prediction[0])
        confidence = float(np.max(prediction[0]))  

        return CLASS_NAMES[predicted_class_index], confidence

    except Exception as e:
        return f"Error: {str(e)}", 0.0

    finally:
        # Clean up: remove the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)