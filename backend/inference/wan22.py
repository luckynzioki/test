"""
Wan2.2 model wrapper
Alibaba Damo Vision — 14B DiT, superior visual quality
HuggingFace: https://huggingface.co/damo-viavi/Wan2.2

Used as a fallback when LTX-2 is unavailable, or for style-heavy videos.
"""

import logging
import torch
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)

MODEL_ID = "damo-viavi/Wan2.2"


class Wan22Pipeline:
    """
    Wrapper around the Wan2.2 text-to-video pipeline.

    This model excels at:
    - Cinematic aesthetics and composition
    - Complex scenes with multiple elements
    - Artistic and stylised content

    It does NOT generate audio natively — pair with a TTS model for sync'd speech.
    """

    def __init__(self, model_path: str = "./models/wan2.2", device: str = "cuda"):
        self.model_path = model_path
        self.device = device
        self.pipe = None
        self.loaded = False

    def load(self):
        """Load Wan2.2 from local weights."""
        if self.loaded:
            return

        logger.info(f"Loading Wan2.2 from {self.model_path} ...")

        try:
            # Wan2.2 is compatible with CogVideoX-style diffusers pipeline.
            # Check the official repo for exact usage.
            from diffusers import CogVideoXPipeline

            self.pipe = CogVideoXPipeline.from_pretrained(
                self.model_path,
                torch_dtype=torch.bfloat16,
            ).to(self.device)

            self.pipe.enable_model_cpu_offload()
            self.pipe.enable_vae_slicing()
            self.pipe.vae.enable_tiling()

            self.loaded = True
            logger.info("Wan2.2 loaded")

        except Exception as exc:
            logger.error(f"Could not load Wan2.2: {exc}")
            raise

    def generate(
        self,
        prompt: str,
        duration: int = 5,
        fps: int = 24,
        height: int = 720,
        width: int = 1280,
        num_inference_steps: int = 50,
        guidance_scale: float = 6.0,
        seed: Optional[int] = None,
    ) -> dict:
        """Generate video frames (no audio — use TTS separately)."""
        if not self.loaded:
            self.load()

        generator = torch.Generator(device=self.device)
        if seed is not None:
            generator.manual_seed(seed)

        num_frames = duration * fps
        logger.info(f"Wan2.2 generating {num_frames} frames @ {width}x{height}")

        output = self.pipe(
            prompt=prompt,
            height=height,
            width=width,
            num_frames=num_frames,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generator,
            output_type="np",
        )

        # [batch, T, H, W, 3]  float32
        frames = (output.frames[0] * 255).astype(np.uint8)

        # Wan2.2 has no native audio — return silence placeholder
        silence = np.zeros(duration * 48000, dtype=np.float32)

        return {
            "frames": frames,
            "audio": silence,
            "fps": fps,
            "sample_rate": 48000,
        }
