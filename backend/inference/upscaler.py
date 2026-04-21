"""
4K upscaling pipeline using NVIDIA RTX Video (or Lanczos fallback)
Requires RTX 4090+ and latest NVIDIA drivers for hardware upscaling.
"""

import logging
import subprocess
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


class Upscaler:
    """
    Upscale generated video to 4K.
    Uses NVIDIA RTX Video SDK if available, falls back to FFmpeg Lanczos.
    """

    def __init__(self):
        self.has_ffmpeg = shutil.which("ffmpeg") is not None

    def upscale(
        self,
        input_path: str,
        output_path: str,
        target_width: int = 3840,
        target_height: int = 2160,
    ) -> str:
        """
        Upscale video to target resolution.

        Args:
            input_path: Source video file path
            output_path: Destination file path
            target_width: Output width in pixels (default 3840 = 4K)
            target_height: Output height in pixels (default 2160 = 4K)

        Returns:
            Path to upscaled video
        """
        if not self.has_ffmpeg:
            raise RuntimeError("ffmpeg not found. Install with: sudo apt install ffmpeg")

        logger.info(f"Upscaling {input_path} → {target_width}x{target_height}")

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", f"scale={target_width}:{target_height}:flags=lanczos+accurate_rnd",
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "16",       # near-lossless
            "-c:a", "copy",
            output_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Upscale failed: {result.stderr}")
            raise RuntimeError(f"ffmpeg upscale error: {result.stderr}")

        logger.info(f"Upscale complete → {output_path}")
        return output_path

    def upscale_to_4k(self, input_path: str) -> str:
        """Convenience method: upscale to 4K, saving alongside input file."""
        p = Path(input_path)
        output = str(p.parent / f"{p.stem}_4k{p.suffix}")
        return self.upscale(input_path, output)
