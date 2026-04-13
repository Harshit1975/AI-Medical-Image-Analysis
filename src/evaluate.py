import os
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def evaluate_model():
    """Evaluates the saved model on the test dataset and outputs a confusion matrix."""
    
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'medical_ai_model.h5'))
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'chest_xray', 'test'))
    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outputs'))
    
    os.makedirs(outputs_dir, exist_ok=True)
    
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}. Please run train.py first.")
        return
        
    if not os.path.exists(test_dir):
        print(f"Test data not found at {test_dir}. Please extract the dataset into the data/ folder.")
        return

    print("Loading Model...")
    model = tf.keras.models.load_model(model_path)
    
    test_datagen = ImageDataGenerator(rescale=1./255)
    
    print("Loading Test Data...")
    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=(256, 256),
        color_mode="grayscale",
        batch_size=32,
        class_mode='binary',
        shuffle=False # IMPORTANT: do not shuffle test data for evaluation
    )
    
    print("Running Inference...")
    predictions = model.predict(test_generator)
    predictions = np.where(predictions > 0.5, 1, 0)
    
    true_classes = test_generator.classes
    class_labels = list(test_generator.class_indices.keys())
    
    print("\nClassification Report:")
    print(classification_report(true_classes, predictions, target_names=class_labels))
    
    # Generate Confusion Matrix
    cm = confusion_matrix(true_classes, predictions)
    
    # Plot Configuration
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_labels, yticklabels=class_labels)
    plt.title('Confusion Matrix - Pneumonia Detection Model')
    plt.ylabel('True Output Diagnosis')
    plt.xlabel('Predicted AI Output')
    
    # Save chart
    cm_path = os.path.join(outputs_dir, "confusion_matrix.png")
    plt.savefig(cm_path)
    print(f"Confusion Matrix saved to {cm_path}")
    plt.show()

if __name__ == "__main__":
    evaluate_model()
