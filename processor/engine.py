import cv2
import logging
from ultralytics import YOLO

# Configure logging for the engine
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] AI_Engine: %(message)s"
)

class AnonymizationEngine:
    def __init__(self, model_path="yolov8n.pt"):
        """
        Initializes the YOLOv8 model.
        Automatically downloads yolov8n.pt if it's not present.
        """
        logging.info(f"Loading YOLO model from {model_path}...")
        self.model = YOLO(model_path)
        logging.info("AI Model loaded successfully.")

    def process_frame(self, frame):
        """
        Runs YOLOv8 inference to detect 'person' (Class ID: 0),
        and applies a Gaussian blur to the bounding box.
        """
        # Run inference. classes=[0] ensures we only detect people to save compute
        results = self.model.predict(source=frame, classes=[0], verbose=False)

        # Iterate over detections in the frame
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Extract bounding box coordinates (x-top-left, y-top-left, x-bottom-right, y-bottom-right)
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Extract the Region of Interest (ROI)
                roi = frame[y1:y2, x1:x2]
                
                # Ensure ROI is valid (prevent OpenCV crash on edge cases)
                if roi.shape[0] > 0 and roi.shape[1] > 0:
                    # Apply Gaussian Blur
                    # Using (0,0) and a high sigmaX/Y lets OpenCV auto-calculate kernel size safely
                    blurred_roi = cv2.GaussianBlur(roi, (0, 0), sigmaX=30, sigmaY=30)
                    
                    # Replace the original area with the blurred area
                    frame[y1:y2, x1:x2] = blurred_roi

        return frame
