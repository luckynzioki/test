"""
Storage service — manages generated video/audio files on disk.
"""

import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from backend.config import OUTPUT_PATH, CLEANUP_OLD_OUTPUTS_DAYS

logger = logging.getLogger(__name__)


class StorageService:
    """Handles saving and cleaning up generated video/audio files."""

    def __init__(self, base_path: str = OUTPUT_PATH):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_video(self, data: bytes, job_id: str) -> str:
        """Save raw video bytes and return the file path."""
        path = self.base_path / f"video_{job_id}.mp4"
        path.write_bytes(data)
        logger.info(f"Video saved: {path} ({len(data) / 1e6:.1f} MB)")
        return str(path)

    def save_audio(self, data: bytes, job_id: str) -> str:
        """Save raw audio bytes and return the file path."""
        path = self.base_path / f"audio_{job_id}.wav"
        path.write_bytes(data)
        logger.info(f"Audio saved: {path}")
        return str(path)

    def get_video_path(self, job_id: str) -> Optional[str]:
        """Return path if video exists, else None."""
        path = self.base_path / f"video_{job_id}.mp4"
        return str(path) if path.exists() else None

    def delete_job_files(self, job_id: str):
        """Delete all files associated with a job."""
        for pattern in [f"video_{job_id}.mp4", f"audio_{job_id}.wav"]:
            p = self.base_path / pattern
            if p.exists():
                p.unlink()
                logger.info(f"Deleted {p}")

    def list_outputs(self) -> List[dict]:
        """List all files in the output directory."""
        files = []
        for p in self.base_path.iterdir():
            if p.is_file() and p.name != ".gitkeep":
                files.append({
                    "name": p.name,
                    "size_mb": p.stat().st_size / 1e6,
                    "modified": datetime.fromtimestamp(p.stat().st_mtime).isoformat(),
                })
        return sorted(files, key=lambda x: x["modified"], reverse=True)

    def cleanup_old_files(self, days: int = CLEANUP_OLD_OUTPUTS_DAYS):
        """Delete output files older than `days` days."""
        cutoff = datetime.now() - timedelta(days=days)
        deleted = 0
        for p in self.base_path.iterdir():
            if p.is_file() and p.name != ".gitkeep":
                mtime = datetime.fromtimestamp(p.stat().st_mtime)
                if mtime < cutoff:
                    p.unlink()
                    deleted += 1
        if deleted:
            logger.info(f"Cleaned up {deleted} old output files (>{days} days)")
        return deleted

    def get_total_size_gb(self) -> float:
        """Return total disk usage of outputs in GB."""
        total = sum(
            p.stat().st_size
            for p in self.base_path.iterdir()
            if p.is_file() and p.name != ".gitkeep"
        )
        return total / 1e9
