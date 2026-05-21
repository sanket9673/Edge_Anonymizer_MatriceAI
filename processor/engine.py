import cv2
import logging
from ultralytics import YOLO
from processor.compliance import fail_closed_compliance

# Configure logging for the engine
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] AI_Engine: %(message)s"
)

class AnonymizationEngine:
    def __init__(self, model_path="yolov8n.pt"):
        """
        Initializes the YOLOv8 model.
        """
        logging.info(f"Loading YOLO model from {model_path}...")
        self.model = YOLO(model_path)
        logging.info("AI Model loaded successfully.")

    # Wrap the process_frame method with our enterprise compliance filter
    # Timeout set to 800ms to accommodate CPU-based edge devices safely.
    @fail_closed_compliance(timeout_ms=800)
    def process_frame(self, frame):
        """
        Runs YOLOv8 inference to detect 'person' (Class ID: 0),
        and applies a Gaussian blur to the bounding box.
        Returns the blurred frame and the count of redactions.
        """
        results = self.model.predict(source=frame, classes=[0], verbose=False)

        redacted_count = 0

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                roi = frame[y1:y2, x1:x2]
                
                if roi.shape[0] > 0 and roi.shape[1] > 0:
                    # Apply Gaussian Blur
                    blurred_roi = cv2.GaussianBlur(roi, (0, 0), sigmaX=30, sigmaY=30)
                    frame[y1:y2, x1:x2] = blurred_roi
                    redacted_count += 1

        # Must return tuple so the Compliance Filter can construct the Metadata Dict
        return frame, redacted_count
