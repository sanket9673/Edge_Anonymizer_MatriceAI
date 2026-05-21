import cv2
import redis
import base64
import numpy as np
import logging
import time
from ingress.config import REDIS_HOST, REDIS_PORT, STREAM_NAME
from processor.engine import AnonymizationEngine

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] VideoConsumer: %(message)s"
)

class VideoConsumer:
    def __init__(self):
        self.stream_name = STREAM_NAME
        try:
            self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
            self.redis_client.ping()
            logging.info(f"Connected to Redis broker at {REDIS_HOST}:{REDIS_PORT}")
        except redis.ConnectionError as e:
            logging.error(f"Failed to connect to Redis: {e}")
            raise

        self.engine = AnonymizationEngine()
        self.last_id = "0-0" 

    def run(self):
        logging.info(f"Listening for frames on Redis stream: '{self.stream_name}'...")
        logging.info("Press 'q' in the video window to quit.")
        
        try:
            while True:
                messages = self.redis_client.xrevrange(self.stream_name, max='+', min='-', count=1)
                if not messages:
                    continue

                message_id, payload = messages[0]
                
                if message_id == self.last_id:
                    time.sleep(0.01)
                    continue
                    
                self.last_id = message_id

                b64_frame = payload.get(b"frame")
                if not b64_frame:
                    continue

                img_data = base64.b64decode(b64_frame.decode('utf-8'))
                np_arr = np.frombuffer(img_data, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if frame is not None:
                    # PASS TO COMPLIANCE ENGINE
                    payload = self.engine.process_frame(frame)
                    
                    # UNPACK ENTERPRISE SCHEMA
                    processed_frame = payload["frame"]
                    metadata = payload["metadata"]
                    status = metadata["status"]
                    redactions = metadata["redacted_count"]
                    latency = metadata["latency_ms"]

                    # UI OVERLAY COLORS
                    if status == "COMPLIANT":
                        color = (0, 255, 0) # Green
                    else:
                        color = (0, 0, 255) # Red for FAIL_CLOSED

                    # DRAW ENTERPRISE HUD
                    cv2.putText(processed_frame, f"STATUS: {status}", (20, 40), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                    cv2.putText(processed_frame, f"Redacted: {redactions}", (20, 75), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(processed_frame, f"AI Latency: {latency}ms", (20, 110), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                    # DISPLAY VIDEO
                    cv2.imshow("Matrice Enterprise Edge Anonymizer", processed_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            logging.info("Consumer process stopped by user.")
        except Exception as e:
            logging.error(f"Unexpected error in consumer loop: {e}")
        finally:
            self.stop()

    def stop(self):
        cv2.destroyAllWindows()
        if self.redis_client:
            self.redis_client.close()
        logging.info("Resources cleaned up gracefully.")

if __name__ == "__main__":
    consumer = VideoConsumer()
    consumer.run()
