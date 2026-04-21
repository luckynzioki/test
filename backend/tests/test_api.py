"""
Test suite for AI Video Studio backend
Run with: pytest backend/tests/ -v
"""

import os
import pytest

# Put API in testing mode so no real GPU needed
os.environ["TESTING_MODE"] = "1"
os.environ["DEVICE"] = "cpu"

from fastapi.testclient import TestClient
from backend.api.routes import app

client = TestClient(app)


# ── Health ────────────────────────────────────────────────────────────────────

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AI Video Studio API"


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200


# ── Generation ────────────────────────────────────────────────────────────────

def test_submit_generation_valid():
    response = client.post("/api/generate", json={
        "prompt": "A golden retriever playing fetch in a sunny park",
        "duration": 3,
        "height": 480,
        "width": 640,
        "fps": 24,
        "num_inference_steps": 20,
    })
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"


def test_submit_generation_short_prompt():
    response = client.post("/api/generate", json={
        "prompt": "Too short",   # less than 10 chars → should fail
    })
    assert response.status_code == 422


def test_submit_generation_missing_prompt():
    response = client.post("/api/generate", json={})
    assert response.status_code == 422


# ── Job Status ────────────────────────────────────────────────────────────────

def test_get_job_status_not_found():
    response = client.get("/api/job/nonexistent-job-id")
    assert response.status_code == 404


def test_get_job_status_after_submit():
    submit = client.post("/api/generate", json={
        "prompt": "A cat sleeping on a sunny windowsill in the afternoon",
        "duration": 2,
    })
    assert submit.status_code == 200
    job_id = submit.json()["job_id"]

    status = client.get(f"/api/job/{job_id}")
    assert status.status_code == 200
    data = status.json()
    assert data["job_id"] == job_id
    assert data["status"] in ("queued", "processing", "completed", "failed")


# ── Job List ──────────────────────────────────────────────────────────────────

def test_list_jobs():
    response = client.get("/api/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert isinstance(data["jobs"], list)


# ── Models ────────────────────────────────────────────────────────────────────

def test_list_models():
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) >= 1


# ── Stats ─────────────────────────────────────────────────────────────────────

def test_get_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_jobs" in data


# ── Generator (unit) ─────────────────────────────────────────────────────────

def test_generator_frame_shape():
    import numpy as np
    from backend.inference.generator import VideoGenerator
    gen = VideoGenerator()
    frames = gen._generate_frames(
        prompt="Test prompt for frame generation",
        num_frames=12,
        height=240,
        width=320,
    )
    assert frames.shape == (12, 240, 320, 3)
    assert frames.dtype == np.uint8


def test_generator_audio_shape():
    import numpy as np
    from backend.inference.generator import VideoGenerator
    gen = VideoGenerator()
    audio = gen._generate_audio(prompt="Test prompt for audio generation", duration=2)
    assert audio.dtype == np.float32
    assert len(audio) == 2 * 48000   # 2 seconds @ 48 kHz


def test_full_generate_pipeline(tmp_path):
    """Integration test: generate frames + audio and save files"""
    import os
    os.environ["OUTPUT_PATH"] = str(tmp_path)

    from backend.inference.generator import VideoGenerator
    gen = VideoGenerator()
    gen.output_path = str(tmp_path)

    result = gen.generate(
        prompt="A simple test video of waves on a calm ocean at sunset",
        duration=1,
        fps=12,
        height=240,
        width=320,
        num_inference_steps=5,
    )

    assert "video_path" in result
    assert "audio_path" in result
    from pathlib import Path
    assert Path(result["video_path"]).exists()
    assert Path(result["audio_path"]).exists()
