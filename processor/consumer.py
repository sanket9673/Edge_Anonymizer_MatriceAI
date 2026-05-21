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
        # Connect to Redis
        try:
            self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
            self.redis_client.ping()
            logging.info(f"Connected to Redis broker at {REDIS_HOST}:{REDIS_PORT}")
        except redis.ConnectionError as e:
            logging.error(f"Failed to connect to Redis: {e}")
            raise

        # Initialize the AI Engine
        self.engine = AnonymizationEngine()
        
        # We use '$' initially to only read NEW messages that arrive after the consumer starts
        self.last_id = "$" 

    def run(self):
        logging.info(f"Listening for frames on Redis stream: '{self.stream_name}'...")
        logging.info("Press 'q' in the video window to quit.")
        
        try:
            while True:
                # 1. Read from Redis Stream (blocking for 100ms max)
                messages = self.redis_client.xread(
                    streams={self.stream_name: self.last_id}, 
                    count=1, 
                    block=100
                )

                if not messages:
                    # Stream is empty/no new frames, just loop again
                    continue

                # 2. Extract payload
                stream, records = messages[0]
                message_id, payload = records[0]
                
                # Update last_id to the message we just read to move forward in the stream
                self.last_id = message_id

                # 3. Decode Base64 to Image Matrix
                b64_frame = payload.get(b"frame")
                if not b64_frame:
                    logging.warning("Received message without a frame payload.")
                    continue

                img_data = base64.b64decode(b64_frame.decode('utf-8'))
                np_arr = np.frombuffer(img_data, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if frame is not None:
                    # 4. Pass frame to AI Anonymization Engine
                    start_time = time.time()
                    processed_frame = self.engine.process_frame(frame)
                    fps = int(1.0 / (time.time() - start_time))
                    
                    # Overlay FPS on the screen
                    cv2.putText(processed_frame, f"AI FPS: {fps}", (20, 40), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    # 5. Display the anonymized frame
                    cv2.imshow("Edge Anonymizer - Live Feed", processed_frame)

                # 6. Break condition (Press 'q' to stop)
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
