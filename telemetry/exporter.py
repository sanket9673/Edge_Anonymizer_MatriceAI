import json
import redis
import logging
from ingress.config import REDIS_HOST, REDIS_PORT

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] Telemetry: %(message)s")

class TelemetryExporter:
    def __init__(self):
        self.stream_name = "telemetry_stream"
        try:
            self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
            self.redis_client.ping()
            logging.info(f"TelemetryExporter connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        except Exception as e:
            logging.error(f"Failed to connect to Redis for Telemetry: {e}")
            self.redis_client = None

    def export(self, metadata: dict):
        """
        Pushes telemetry metrics to the Redis stream using XADD.
        """
        if not self.redis_client:
            return
            
        try:
            payload = {"data": json.dumps(metadata)}
            # maxlen=1000 approximate (~), keeps Redis RAM usage highly optimized
            self.redis_client.xadd(self.stream_name, payload, maxlen=1000, approximate=True)
        except Exception as e:
            logging.error(f"Failed to export telemetry data: {e}")
