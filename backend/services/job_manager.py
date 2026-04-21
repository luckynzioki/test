"""
Job management service for handling video generation tasks
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List
import time
from backend.api.models import GenerationRequest
from backend.inference.generator import VideoGenerator

logger = logging.getLogger(__name__)

class JobManager:
    """Manages video generation jobs"""
    
    def __init__(self):
        self.jobs: Dict[str, Dict] = {}
        self.generator = VideoGenerator()
        
    def create_job(self, job_id: str, prompt: str, request_data: Dict):
        """Create a new job entry"""
        self.jobs[job_id] = {
            "id": job_id,
            "prompt": prompt,
            "status": "queued",
            "progress": 0.0,
            "created_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
            "video_path": None,
            "audio_path": None,
            "error": None,
            "generation_time": None,
            "request": request_data,
        }
        logger.info(f"Job {job_id} created")
        
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        return self.jobs.get(job_id)
        
    def list_jobs(self, limit: int = 50, skip: int = 0) -> List[Dict]:
        """List jobs with pagination"""
        jobs = list(self.jobs.values())
        jobs.sort(key=lambda x: x["created_at"], reverse=True)
        return jobs[skip:skip+limit]
        
    def delete_job(self, job_id: str) -> bool:
        """Delete a job"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            # TODO: Delete video and audio files
            del self.jobs[job_id]
            logger.info(f"Job {job_id} deleted")
            return True
        return False
        
    def get_stats(self) -> Dict:
        """Get generation statistics"""
        total = len(self.jobs)
        completed = sum(1 for j in self.jobs.values() if j["status"] == "completed")
        failed = sum(1 for j in self.jobs.values() if j["status"] == "failed")
        processing = sum(1 for j in self.jobs.values() if j["status"] == "processing")
        
        avg_time = None
        times = [j["generation_time"] for j in self.jobs.values() if j["generation_time"]]
        if times:
            avg_time = sum(times) / len(times)
        
        return {
            "total_jobs": total,
            "completed": completed,
            "failed": failed,
            "processing": processing,
            "average_generation_time": avg_time,
        }
        
    async def process_generation(self, job_id: str, request: GenerationRequest):
        """Process video generation (runs in background)"""
        job = self.jobs[job_id]
        start_time = time.time()
        
        try:
            job["status"] = "processing"
            job["started_at"] = datetime.utcnow().isoformat()
            job["progress"] = 0.1
            
            logger.info(f"Starting generation for job {job_id}")
            
            # Call inference
            result = self.generator.generate(
                prompt=request.prompt,
                duration=request.duration,
                height=request.height,
                width=request.width,
                fps=request.fps,
                seed=request.seed,
                num_inference_steps=request.num_inference_steps,
            )
            
            # Update job with results
            job["status"] = "completed"
            job["progress"] = 1.0
            job["video_path"] = result["video_path"]
            job["audio_path"] = result.get("audio_path")
            job["completed_at"] = datetime.utcnow().isoformat()
            job["generation_time"] = time.time() - start_time
            
            logger.info(f"Job {job_id} completed in {job['generation_time']:.1f}s")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {str(e)}")
            job["status"] = "failed"
            job["error"] = str(e)
            job["completed_at"] = datetime.utcnow().isoformat()
            job["generation_time"] = time.time() - start_time
