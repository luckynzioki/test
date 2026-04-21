"""
FFmpeg utility functions for video stitching, encoding, and processing
"""

import subprocess
import logging
import shutil
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def check_ffmpeg() -> bool:
    """Check if ffmpeg is installed"""
    return shutil.which("ffmpeg") is not None


def merge_video_audio(video_path: str, audio_path: str, output_path: str) -> str:
    """Merge separate video and audio files into one MP4"""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"ffmpeg merge failed: {result.stderr}")
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")
    logger.info(f"Merged video+audio → {output_path}")
    return output_path


def stitch_clips(clip_paths: List[str], output_path: str, crossfade_seconds: float = 0.5) -> str:
    """
    Stitch multiple video clips together with optional crossfade transitions.
    Used for long-form video generation (15+ minutes).
    """
    if not clip_paths:
        raise ValueError("No clips provided")

    if len(clip_paths) == 1:
        shutil.copy(clip_paths[0], output_path)
        return output_path

    # Write concat list file
    list_file = Path(output_path).parent / "concat_list.txt"
    with open(list_file, "w") as f:
        for clip in clip_paths:
            f.write(f"file '{clip}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    list_file.unlink(missing_ok=True)

    if result.returncode != 0:
        logger.error(f"ffmpeg stitch failed: {result.stderr}")
        raise RuntimeError(f"ffmpeg stitch failed: {result.stderr}")

    logger.info(f"Stitched {len(clip_paths)} clips → {output_path}")
    return output_path


def upscale_video(input_path: str, output_path: str, target_width: int = 3840, target_height: int = 2160) -> str:
    """Upscale video to 4K using Lanczos algorithm"""
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", f"scale={target_width}:{target_height}:flags=lanczos",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-c:a", "copy",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"ffmpeg upscale failed: {result.stderr}")
        raise RuntimeError(f"ffmpeg upscale failed: {result.stderr}")
    logger.info(f"Upscaled video to {target_width}x{target_height} → {output_path}")
    return output_path


def get_video_info(video_path: str) -> dict:
    """Get video metadata (duration, fps, resolution)"""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams", "-show_format",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {}
    import json
    try:
        data = json.loads(result.stdout)
        video_stream = next((s for s in data.get("streams", []) if s["codec_type"] == "video"), {})
        return {
            "duration": float(data.get("format", {}).get("duration", 0)),
            "width": video_stream.get("width"),
            "height": video_stream.get("height"),
            "fps": video_stream.get("r_frame_rate", "24/1"),
        }
    except Exception:
        return {}
