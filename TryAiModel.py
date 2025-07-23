# Import required libraries
from tensorflow.keras.models import load_model #type:ignore
from tensorflow.keras.preprocessing.image import load_img, img_to_array #type:ignore
import numpy as np

# Define image size (must match the input shape of the model)
img_size = (224, 224)

# Load the trained model
# model_path=r"C:\Users\jauda\Desktop\SemesterProject\current model 3 6 2025\best_model ID_1.h5" #rust 68 healthy 56 powdery 99


# Class names (assuming these are the same as during training)
class_names = [
    "bacterial_spot",
    "early_blight",
    "healthy",
    "late_blight",
    "powdery_mildew",
    "rust"
]

# Prediction function
def predict_image(img_path):
    """Predict the class of a single image"""
    try:
        # Load and preprocess the image
        img = load_img(img_path, target_size=img_size)
        img_array = img_to_array(img)  
        img_array /= 255.0  # Normalize the image
        #add one more dimension (batch size = 1 in this case )
        img_batch = np.expand_dims(img_array, axis=0)  # Add batch dimension
        
        # Get prediction
        prediction = model.predict(img_batch)
        predicted_class = np.argmax(prediction[0])#finds index of highest probability 
        confidence = np.max(prediction[0])#find the value of the highest probability 
        
        return class_names[predicted_class], confidence
    except Exception as e:
        return f"Error: {str(e)}", 0

# Example usage
images=[r'Testing the project\rust_1.jpeg',r'c:\Users\jauda\Desktop\lat eblight 97.jpg',r'Testing the project\bacterial 97.jpeg',r'Testing the project\coffee-rust 97.png',r'Testing the project\Rustt 97.jpeg',r'Testing the project\powderyy 97.jpeg',r'Testing the project\healthy_97.jpeg']
if __name__ == "__main__":
  
    model_path = r"\ID_2 new model 21 6 2025\best_model ID_2.h5" #rust 95 healthy 70 powdery 96 rust 96
    model = load_model(model_path)
    print(f"Model loaded from: {model_path}")
    
    for i in images:
        predicted_class, confidence = predict_image(i)
        # Print the result
        print("-"*20,model_path[59:],"-"*20)
        print(f"img : {i[23:-5]} Predicted class: {predicted_class} with {confidence:.2%} confidence")
        

    print("-"*60)
    model_path=r"\ID_6 model Better\best_model.h5"
    model = load_model(model_path)
    print(f"Model loaded from: {model_path}")
    for i in images:
        predicted_class, confidence = predict_image(i)
        # Print the result
        print("-"*20,model_path[62:],"-"*20)
        print(f"img : {i[23:-5]} Predicted class: {predicted_class} with {confidence:.2%} confidence")
        