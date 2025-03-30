from ultralytics import YOLO

# Load the YOLO model
model = YOLO('brand-detect.pt')

# Perform inference on the image
results = model('scraped_dataset/toyota_innova/side_2024_Image_27.jpg')

# Process and print the results
for result in results:
    boxes = result.boxes.xyxy  # Bounding box coordinates in (x1, y1, x2, y2) format
    confidences = result.boxes.conf  # Confidence scores
    class_ids = result.boxes.cls  # Class IDs
    class_names = result.names  # Dictionary mapping class IDs to class names

    for box, confidence, class_id in zip(boxes, confidences, class_ids):
        x1, y1, x2, y2 = box.tolist()
        class_name = class_names[int(class_id)]
        print(f"Class: {class_name}, Confidence: {confidence:.2f}, "
              f"Bounding Box: [{x1:.2f}, {y1:.2f}, {x2:.2f}, {y2:.2f}]")
