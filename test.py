import tensorflow as tf
import numpy as np
import cv2

# Load the TFLite model
interpreter = tf.lite.Interpreter(model_path="Tesla_ModelClassifier_MobNet.tflite")
interpreter.allocate_tensors()

# Get input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Define Tesla models (update if necessary)
tesla_models = ["Model S", "Model 3", "Model X", "Model Y"]

def preprocess_image(image_path):
    """Loads an image, resizes it to 224x224, and normalizes it."""
    image = cv2.imread(image_path)  # Read image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB
    image = cv2.resize(image, (224, 224))  # Resize to match model input
    image = image.astype(np.float32) / 255.0  # Normalize to [0,1]
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

def predict(image_path):
    """Runs inference on a given image and returns predicted Tesla model & confidence."""
    image = preprocess_image(image_path)

    # Set model input
    interpreter.set_tensor(input_details[0]['index'], image)

    # Run inference
    interpreter.invoke()

    # Get model output
    output_data = interpreter.get_tensor(output_details[0]['index'])
    prediction = np.squeeze(output_data)  # Remove batch dimension

    # Get the best prediction
    predicted_index = np.argmax(prediction)
    confidence = prediction[predicted_index]

    return tesla_models[predicted_index], confidence

# Example usage
image_path = "D:/Repositories_2/Car Dataset Collector/scraped_dataset_2/Tesla/tesla_model x/side_2025_000021.png"  # Change to your image path
model_name, confidence = predict(image_path)

print(f"Model: {model_name}, Confidence: {confidence:.2f}")
