import cv2
import os
from ultralytics import YOLO

def process_images(input_folder):
    # Load the YOLOv8 model pre-trained on the COCO dataset
    model = YOLO('yolov8n.pt')

    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(input_folder, filename)
            image = cv2.imread(image_path)

            # Perform detection
            results = model(image)

            # Initialize variables
            largest_box = None
            largest_area = 0

            for result in results:
                for box in result.boxes:
                    cls = int(box.cls[0])
                    # Check if the object is a car, bus, or truck
                    if cls in [2, 5,6,7]:  # Car, Bus, Truck
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        area = (x2 - x1) * (y2 - y1)
                        # Select the largest detected vehicle
                        if area > largest_area:
                            largest_area = area
                            largest_box = (x1, y1, x2, y2)

            if largest_box:
                x1, y1, x2, y2 = largest_box
                cropped_image = image[y1:y2, x1:x2]
                cv2.imwrite(image_path, cropped_image)
            else:
                print(f"No vehicle detected in {filename}. Skipping cropping.")

if __name__ == "__main__":
    input_folder = "scraped_dataset_2/nissan_urvan"
    process_images(input_folder)
