"""
LTX-2 model wrapper
Lightricks LTX-Video — 14B video + 5B audio parameters
HuggingFace: https://huggingface.co/Lightricks/LTX-Video

To download the model weights:
    python scripts/download_models.py --models ltx2

The actual inference calls (self.pipe.generate) are documented below.
In testing/demo mode the generator.py mock is used instead.
"""

import logging
import torch
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

MODEL_ID = "Lightricks/LTX-Video"


class LTX2Pipeline:
    """
    Wrapper around the LTX-2 diffusion pipeline.

    Usage (once model is downloaded):
        pipe = LTX2Pipeline(model_path="./models/ltx-2")
        pipe.load()
        result = pipe.generate("A cat sleeping on a sunny windowsill", duration=5)
    """

    def __init__(self, model_path: str = "./models/ltx-2", device: str = "cuda"):
        self.model_path = model_path
        self.device = device
        self.pipe = None
        self.loaded = False

    def load(self):
        """Load the LTX-2 pipeline from local weights."""
        if self.loaded:
            return

        logger.info(f"Loading LTX-2 from {self.model_path} ...")

        try:
            # LTX-Video uses a custom pipeline class.
            # Check the official repo for the exact import path:
            # https://github.com/Lightricks/LTX-Video
            from diffusers import LTXPipeline  # may require diffusers >= 0.26

            self.pipe = LTXPipeline.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16,
            ).to(self.device)

            # Memory optimisations
            self.pipe.enable_model_cpu_offload()
            self.pipe.enable_vae_slicing()

            self.loaded = True
            logger.info("LTX-2 loaded successfully")

        except Exception as exc:
            logger.error(f"Could not load LTX-2: {exc}")
            raise

    def generate(
        self,
        prompt: str,
        duration: int = 5,
        fps: int = 24,
        height: int = 720,
        width: int = 1280,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
    ) -> dict:
        """
        Generate video + audio from a text prompt.

        Returns:
            {
                "frames":  np.ndarray  [T, H, W, 3] uint8,
                "audio":   np.ndarray  [samples]    float32,
                "fps":     int,
                "sample_rate": int,
            }
        """
        if not self.loaded:
            self.load()

        generator = torch.Generator(device=self.device)
        if seed is not None:
            generator.manual_seed(seed)

        num_frames = duration * fps

        logger.info(f"LTX-2 generating {num_frames} frames @ {width}x{height}")

        # The actual diffusers call — adjust kwargs to match your diffusers version
        output = self.pipe(
            prompt=prompt,
            height=height,
            width=width,
            num_frames=num_frames,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generator,
            output_type="np",        # returns numpy frames
        )

        # output.frames: [batch, T, H, W, 3]  float32 0-1
        import numpy as np
        frames = (output.frames[0] * 255).astype(np.uint8)

        # LTX-2 also returns synchronised audio
        # output.audios: [batch, samples]  float32
        audio = output.audios[0] if hasattr(output, "audios") else np.zeros(duration * 48000, dtype=np.float32)

        return {
            "frames": frames,
            "audio": audio,
            "fps": fps,
            "sample_rate": 48000,
        }
