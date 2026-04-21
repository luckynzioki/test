"""
Configuration module for AI Video Studio backend
Loads settings from environment variables and .env file
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    load_dotenv(env_file)

# GPU Configuration
CUDA_VISIBLE_DEVICES = os.getenv("CUDA_VISIBLE_DEVICES", "0")
DEVICE = os.getenv("DEVICE", "cuda")
os.environ["CUDA_VISIBLE_DEVICES"] = CUDA_VISIBLE_DEVICES

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_LOG_LEVEL = os.getenv("API_LOG_LEVEL", "info")

# Model Paths
MODEL_PATH = os.getenv("MODEL_PATH", "./models")
LTX2_MODEL_ID = os.getenv("LTX2_MODEL_ID", "Lightricks/LTX-Video")
WAN22_MODEL_ID = os.getenv("WAN22_MODEL_ID", "damo-viavi/Wan2.2")
MULTITALK_MODEL_ID = os.getenv("MULTITALK_MODEL_ID", "zyx/MultiTalk")

# Generation Defaults
DEFAULT_DURATION = int(os.getenv("DEFAULT_DURATION", 5))
DEFAULT_HEIGHT = int(os.getenv("DEFAULT_HEIGHT", 720))
DEFAULT_WIDTH = int(os.getenv("DEFAULT_WIDTH", 1280))
DEFAULT_FPS = int(os.getenv("DEFAULT_FPS", 24))
DEFAULT_INFERENCE_STEPS = int(os.getenv("DEFAULT_INFERENCE_STEPS", 50))

# Output Configuration
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "./outputs")
MAX_OUTPUT_GB = int(os.getenv("MAX_OUTPUT_GB", 1000))
CLEANUP_OLD_OUTPUTS_DAYS = int(os.getenv("CLEANUP_OLD_OUTPUTS_DAYS", 30))

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./videos.db")

# Frontend URL
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Create required directories
Path(MODEL_PATH).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

# Print configuration on import
import logging
logger = logging.getLogger(__name__)

def log_config():
    """Log configuration at startup"""
    logger.info("=" * 60)
    logger.info("AI VIDEO STUDIO CONFIGURATION")
    logger.info("=" * 60)
    logger.info(f"GPU Device: {DEVICE}")
    logger.info(f"CUDA Visible Devices: {CUDA_VISIBLE_DEVICES}")
    logger.info(f"API Host: {API_HOST}:{API_PORT}")
    logger.info(f"Model Path: {MODEL_PATH}")
    logger.info(f"Output Path: {OUTPUT_PATH}")
    logger.info(f"Default Resolution: {DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
    logger.info(f"Default Duration: {DEFAULT_DURATION}s")
    logger.info(f"Inference Steps: {DEFAULT_INFERENCE_STEPS}")
    logger.info("=" * 60)
