import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
STREAM_NAME = os.getenv("STREAM_NAME", "video_stream")

# Handle camera URL. If it's '0', convert to int for OpenCV local webcam.
_camera_env = os.getenv("CAMERA_RTSP_URL", "0")
CAMERA_RTSP_URL = int(_camera_env) if _camera_env.isdigit() else _camera_env
