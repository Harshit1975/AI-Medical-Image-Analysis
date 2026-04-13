import os
import cv2
import numpy as np

def create_mock_dataset():
    # Define paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'chest_xray'))
    
    dirs = [
        os.path.join(base_dir, 'train', 'NORMAL'),
        os.path.join(base_dir, 'train', 'PNEUMONIA'),
        os.path.join(base_dir, 'val', 'NORMAL'),
        os.path.join(base_dir, 'val', 'PNEUMONIA'),
        os.path.join(base_dir, 'test', 'NORMAL'),
        os.path.join(base_dir, 'test', 'PNEUMONIA')
    ]
    
    # Create directories if they don't exist
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    print("Creating mock dataset...")
    
    # Generate 10 images per folder to ensure code runs
    for folder in dirs:
        for i in range(10):
            # Create a 256x256 grayscale image (random noise to simulate scan)
            # NORMAL gets lighter images, PNEUMONIA gets darker, just so model can quickly distinguish
            is_pneumonia = 'PNEUMONIA' in folder
            base_intensity = np.random.randint(50, 100) if is_pneumonia else np.random.randint(150, 200)
            
            img = np.random.normal(base_intensity, 20, (256, 256)).astype(np.uint8)
            
            # Draw fake lungs
            cv2.ellipse(img, (80, 128), (40, 80), 0, 0, 360, (0, 0, 0), -1)
            cv2.ellipse(img, (176, 128), (40, 80), 0, 0, 360, (0, 0, 0), -1)
            
            # If pneumonia, add some "opacity" (white spots) in the lungs
            if is_pneumonia:
                 noise = np.random.normal(200, 30, (256, 256)).astype(np.uint8)
                 mask = np.zeros_like(img)
                 cv2.ellipse(mask, (176, 128), (30, 60), 0, 0, 360, (255, 255, 255), -1)
                 img = np.where(mask > 0, img * 0.5 + noise * 0.5, img)
            
            img_path = os.path.join(folder, f'mock_{i}.jpeg')
            cv2.imwrite(img_path, img)

    print("Mock dataset created successfully at data/chest_xray/")

if __name__ == "__main__":
    create_mock_dataset()
