import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import matplotlib.pyplot as plt

def build_model(input_shape=(256, 256, 1)):
    """Builds and compiles the CNN Model."""
    model = Sequential([
        # 1st Convolutional Layer
        Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        MaxPooling2D(pool_size=(2, 2)),
        
        # 2nd Convolutional Layer
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        
        # 3rd Convolutional Layer
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        
        # Flatten and Dense Layers
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5), # Prevent overfitting
        Dense(1, activation='sigmoid') # Binary classification output
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def train_model():
    """Main training pipeline."""
    # Define paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'chest_xray'))
    train_dir = os.path.join(base_dir, 'train')
    val_dir = os.path.join(base_dir, 'val')
    model_save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
    
    os.makedirs(model_save_dir, exist_ok=True)
    
    if not os.path.exists(train_dir):
        print(f"Error: Training directory not found at {train_dir}")
        print("Please extract the Kaggle dataset into the data/ directory.")
        return

    # Image Data Generator with Data Augmentation
    print("Initializing Data Generators...")
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=10,
        width_shift_range=0.1,
        height_shift_range=0.1,
        shear_range=0.1,
        zoom_range=0.1,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    val_datagen = ImageDataGenerator(rescale=1./255)

    # Load images
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(256, 256),
        color_mode="grayscale",
        batch_size=32,
        class_mode='binary'
    )
    
    # Val generator (if available)
    val_generator = None
    if os.path.exists(val_dir) and len(os.listdir(val_dir)) > 0:
        val_generator = val_datagen.flow_from_directory(
            val_dir,
            target_size=(256, 256),
            color_mode="grayscale",
            batch_size=32,
            class_mode='binary'
        )

    print("Building Model...")
    model = build_model()
    model.summary()

    print("Starting Training Loop...")
    epochs = 10
    
    # Train
    history = model.fit(
        train_generator,
        steps_per_epoch=max(1, train_generator.samples // train_generator.batch_size),
        epochs=epochs,
        validation_data=val_generator,
        validation_steps=max(1, val_generator.samples // val_generator.batch_size) if val_generator else None
    )

    # Save Model
    model_save_path = os.path.join(model_save_dir, 'medical_ai_model.h5')
    model.save(model_save_path)
    print(f"Model saved successfully to {model_save_path}")
    
    return history

if __name__ == "__main__":
    train_model()
