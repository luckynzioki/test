#!/usr/bin/env python3
"""
AI Video Studio - Main API Server
Runs the FastAPI backend for video generation
"""

import logging
import uvicorn
from backend.api.routes import app
from backend.config import API_HOST, API_PORT, API_LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=getattr(logging, API_LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info(f"Starting AI Video Studio API on {API_HOST}:{API_PORT}")
    logger.info(f"API Docs: http://{API_HOST}:{API_PORT}/docs")
    logger.info(f"ReDoc: http://{API_HOST}:{API_PORT}/redoc")
    
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level=API_LOG_LEVEL,
        reload=False,
    )
