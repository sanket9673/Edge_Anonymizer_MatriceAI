import cv2
import redis
import base64
import logging
import time
from ingress.config import REDIS_HOST, REDIS_PORT, STREAM_NAME, CAMERA_RTSP_URL

# Configure enterprise-grade logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] IngressProducer: %(message)s"
)

class VideoIngressProducer:
    def __init__(self):
        self.stream_name = STREAM_NAME
        self.is_running = False
        
        # Initialize Redis
        try:
            self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
            self.redis_client.ping()
            logging.info(f"Connected to Redis broker at {REDIS_HOST}:{REDIS_PORT}")
        except redis.ConnectionError as e:
            logging.error(f"Failed to connect to Redis: {e}")
            raise

        # Initialize Camera
        self.cap = cv2.VideoCapture(CAMERA_RTSP_URL)
        if not self.cap.isOpened():
            logging.error(f"Failed to open video source: {CAMERA_RTSP_URL}")
            raise RuntimeError("Camera connection failed.")
        else:
            logging.info(f"Successfully connected to video source: {CAMERA_RTSP_URL}")

    def run(self):
        """Main loop to capture, compress, encode, and push frames."""
        self.is_running = True
        logging.info(f"Starting frame ingestion into Redis Stream: '{self.stream_name}'...")
        
        try:
            while self.is_running:
                ret, frame = self.cap.read()
                if not ret:
                    logging.warning("Failed to grab frame. Retrying...")
                    time.sleep(0.1)
                    continue

                # SHRINK FRAME FOR FASTER AI PROCESSING
                frame = cv2.resize(frame, (640, 480))

                # 1. Compress to JPEG (Quality 70 to save bandwidth/RAM)
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                _, buffer = cv2.imencode('.jpg', frame, encode_param)
                
                # 2. Base64 Encode
                b64_frame = base64.b64encode(buffer).decode('utf-8')
                
                # 3. Push to Redis Stream with MAXLEN ~1000 (Circular Buffer)
                # approximate=True (the '~') is highly optimized for Redis performance
                payload = {"frame": b64_frame, "timestamp": str(time.time())}
                self.redis_client.xadd(
                    name=self.stream_name,
                    fields=payload,
                    maxlen=1000,
                    approximate=True
                )
                
                # Optional: Sleep slightly to simulate specific FPS if needed
                # time.sleep(0.03) # ~30 FPS

        except KeyboardInterrupt:
            logging.info("Ingress process stopped by user.")
        except Exception as e:
            logging.error(f"Unexpected error in ingestion loop: {e}")
        finally:
            self.stop()

    def stop(self):
        """Cleanup resources cleanly."""
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
            logging.info("Camera released.")
        if self.redis_client:
            self.redis_client.close()
            logging.info("Redis connection closed.")

if __name__ == "__main__":
    producer = VideoIngressProducer()
    producer.run()
