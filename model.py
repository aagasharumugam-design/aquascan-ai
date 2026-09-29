import os
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")

# Load trained AQUASCAN YOLO model once when the server starts.
model = YOLO(MODEL_PATH)


def detect_image(image_path):
    results = model(image_path)
    detections = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detected_class = model.names[class_id]
            if detected_class.lower() == "other":
                detected_class = "Anomaly"

            detections.append({
                "class": detected_class,
                "confidence": round(confidence, 2),
                "box": [round(x1), round(y1), round(x2), round(y2)]
            })

    return detections
