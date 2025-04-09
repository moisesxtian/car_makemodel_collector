import os
import cv2
import albumentations as A
import numpy as np
from pathlib import Path

# Define your image augmentation pipeline
transform = A.Compose([
    A.HorizontalFlip(p=0.5),  # Cars can be flipped horizontally without losing class meaning
    A.RandomBrightnessContrast(p=0.5),  # Vary lighting conditions
    A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=15, val_shift_limit=10, p=0.4),  # Simulate camera variations
    A.RGBShift(r_shift_limit=10, g_shift_limit=10, b_shift_limit=10, p=0.3),  # Subtle color variations
    A.MotionBlur(blur_limit=3, p=0.2),  # Simulate movement
    A.Rotate(limit=10, p=0.3),  # Small angle rotation (not too large)
    A.GaussNoise(var_limit=(10.0, 25.0), p=0.2)  # Corrected argument

])

def augment_image(image_path, num_augmentations=3):
    image = cv2.imread(image_path)
    if image is None:  # Check if image is loaded properly
        print(f"Error loading image: {image_path}")
        return []

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    augmented_images = []
    for _ in range(num_augmentations):
        augmented = transform(image=image)
        aug_img = cv2.cvtColor(augmented["image"], cv2.COLOR_RGB2BGR)
        augmented_images.append(aug_img)

    return augmented_images


def augment_dataset(input_root, output_root, num_augmentations=3):
    input_root = Path(input_root)
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    for brand in input_root.iterdir():
        if brand.is_dir():
            for model in brand.iterdir():
                if model.is_dir():
                    output_model_dir = output_root / brand.name / model.name
                    output_model_dir.mkdir(parents=True, exist_ok=True)

                    for image_file in model.glob("*.[jp][pn]g"):
                        augmented_images = augment_image(str(image_file), num_augmentations)

                        for idx, aug_img in enumerate(augmented_images):
                            aug_name = f"{image_file.stem}_aug{idx+1}{image_file.suffix}"
                            aug_path = output_model_dir / aug_name
                            cv2.imwrite(str(aug_path), aug_img)

if __name__ == "__main__":
    INPUT_FOLDER = "For Augmentation"  # Your original dataset
    OUTPUT_FOLDER = "Augmented_Dataset"  # Where augmented images will be saved
    NUM_AUGS_PER_IMAGE = 3

    augment_dataset(INPUT_FOLDER, OUTPUT_FOLDER, NUM_AUGS_PER_IMAGE)
