"""
FastAPI routes for AI Video Studio
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid
import logging
from pathlib import Path
import torch

from backend.api.models import (
    GenerationRequest, 
    GenerationResponse, 
    JobStatus,
    HealthResponse
)
from backend.config import API_LOG_LEVEL, FRONTEND_URL
from backend.services.job_manager import JobManager

# Initialize FastAPI app
app = FastAPI(
    title="AI Video Studio API",
    description="Professional-grade 4K video generation with AI",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize job manager (in-memory for MVP)
job_manager = JobManager()

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    gpu_available = torch.cuda.is_available()
    cuda_device = torch.cuda.get_device_name(0) if gpu_available else None
    vram_gb = (torch.cuda.get_device_properties(0).total_memory / 1e9) if gpu_available else None
    
    return {
        "status": "healthy",
        "service": "AI Video Studio API",
        "version": "0.1.0",
        "gpu_available": gpu_available,
        "cuda_device": cuda_device,
        "vram_gb": vram_gb,
    }

@app.get("/api/health", response_model=HealthResponse)
async def api_health():
    """Detailed health check"""
    return await health_check()

@app.get("/docs", include_in_schema=False)
async def get_docs():
    """Redirect to Swagger docs"""
    return {"message": "Visit /docs for API documentation"}

# ============================================================================
# Generation Endpoints
# ============================================================================

@app.post("/api/generate", response_model=GenerationResponse)
async def submit_generation(request: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Submit a video generation request
    
    Returns job_id for status tracking and polling
    """
    job_id = str(uuid.uuid4())
    
    logger.info(f"Job {job_id} submitted with prompt: {request.prompt[:50]}...")
    
    # Create job entry
    job_manager.create_job(
        job_id=job_id,
        prompt=request.prompt,
        request_data=request.dict(),
    )
    
    # Queue generation as background task
    background_tasks.add_task(
        job_manager.process_generation,
        job_id=job_id,
        request=request
    )
    
    return {
        "job_id": job_id,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
        "message": "Video generation queued"
    }

@app.get("/api/job/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get status of a generation job
    
    Status values:
    - queued: Waiting to start processing
    - processing: Currently generating
    - completed: Ready for download
    - failed: Generation failed, check error field
    """
    job = job_manager.get_job(job_id)
    
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job["id"],
        "status": job["status"],
        "progress": job["progress"],
        "prompt": job["prompt"],
        "error": job.get("error"),
        "video_url": f"/api/job/{job_id}/video" if job["video_path"] else None,
        "audio_url": f"/api/job/{job_id}/audio" if job["audio_path"] else None,
        "created_at": job["created_at"],
        "started_at": job.get("started_at"),
        "completed_at": job.get("completed_at"),
        "duration_seconds": job.get("generation_time"),
    }

@app.get("/api/job/{job_id}/video")
async def download_video(job_id: str):
    """Download generated video file"""
    job = job_manager.get_job(job_id)
    
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Job not ready. Current status: {job['status']}"
        )
    
    if not job["video_path"]:
        raise HTTPException(status_code=500, detail="Video file not found")
    
    video_path = Path(job["video_path"])
    if not video_path.exists():
        raise HTTPException(status_code=500, detail="Video file missing or deleted")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"ai-video-{job_id[:8]}.mp4"
    )

@app.get("/api/job/{job_id}/audio")
async def download_audio(job_id: str):
    """Download generated audio file"""
    job = job_manager.get_job(job_id)
    
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not ready")
    
    if not job["audio_path"]:
        raise HTTPException(status_code=400, detail="Audio file not available")
    
    audio_path = Path(job["audio_path"])
    if not audio_path.exists():
        raise HTTPException(status_code=500, detail="Audio file missing")
    
    return FileResponse(
        audio_path,
        media_type="audio/wav",
        filename=f"ai-audio-{job_id[:8]}.wav"
    )

# ============================================================================
# Job Management Endpoints
# ============================================================================

@app.get("/api/jobs")
async def list_jobs(limit: int = 50, skip: int = 0):
    """List all generation jobs"""
    jobs = job_manager.list_jobs(limit=limit, skip=skip)
    
    return {
        "total": len(job_manager.jobs),
        "limit": limit,
        "skip": skip,
        "jobs": [
            {
                "job_id": job["id"],
                "status": job["status"],
                "prompt": job["prompt"][:100],
                "progress": job["progress"],
                "created_at": job["created_at"],
            }
            for job in jobs
        ]
    }

@app.delete("/api/job/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and its files"""
    if job_manager.delete_job(job_id):
        return {"message": f"Job {job_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail="Job not found")

@app.get("/api/stats")
async def get_stats():
    """Get generation statistics"""
    return job_manager.get_stats()

# ============================================================================
# Model Management Endpoints
# ============================================================================

@app.get("/api/models")
async def list_models():
    """List available models"""
    return {
        "models": [
            {
                "id": "ltx-2",
                "name": "LTX-2",
                "description": "4K video + audio generation",
                "params": "14B video + 5B audio",
                "size_gb": 18,
            },
            {
                "id": "wan2.2",
                "name": "Wan2.2",
                "description": "High-quality visual generation",
                "params": "14B DiT",
                "size_gb": 16,
            },
            {
                "id": "multitalk",
                "name": "MultiTalk",
                "description": "Multi-person conversations",
                "params": "14B DiT",
                "size_gb": 14,
            },
        ]
    }

# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Initialize configuration logging
from backend.config import log_config

@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    log_config()
    logger.info("API startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    logger.info("API shutting down")
