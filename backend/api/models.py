"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class GenerationRequest(BaseModel):
    """Request model for video generation"""
    prompt: str = Field(..., min_length=10, max_length=500)
    duration: int = Field(default=5, ge=1, le=20)
    height: int = Field(default=720, ge=360, le=2160)
    width: int = Field(default=1280, ge=360, le=3840)
    fps: int = Field(default=24, ge=12, le=60)
    num_inference_steps: int = Field(default=50, ge=20, le=100)
    seed: Optional[int] = Field(default=None)
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "A woman walking through a rainy city street at night, speaking softly",
                "duration": 5,
                "height": 720,
                "width": 1280,
                "fps": 24,
                "num_inference_steps": 50,
            }
        }

class GenerationResponse(BaseModel):
    """Response model for generation submission"""
    job_id: str
    status: str
    created_at: str
    message: str = "Video generation queued"

class JobStatus(BaseModel):
    """Job status response"""
    job_id: str
    status: str  # queued, processing, completed, failed
    progress: float  # 0.0 to 1.0
    prompt: str
    error: Optional[str] = None
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None

class JobListResponse(BaseModel):
    """Response for job list"""
    total: int
    jobs: list

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    gpu_available: bool
    cuda_device: Optional[str] = None
    vram_gb: Optional[float] = None
