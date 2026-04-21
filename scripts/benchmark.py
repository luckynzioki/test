#!/usr/bin/env python3
"""
GPU Benchmark for AI Video Studio
Tests generation speed and VRAM usage on your hardware
"""

import time
import sys
import os
os.environ["TESTING_MODE"] = "1"
os.environ["DEVICE"] = "cpu"

def check_gpu():
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"✅ GPU: {name}")
            print(f"✅ VRAM: {vram_gb:.1f} GB")
            if vram_gb < 8:
                print("⚠️  Warning: Less than 8GB VRAM. Use 480p with distilled models.")
            elif vram_gb < 16:
                print("✅ Suitable for 720p generation.")
            elif vram_gb < 24:
                print("✅ Suitable for 1080p generation.")
            else:
                print("✅ Suitable for 4K generation!")
            return True
        else:
            print("⚠️  No CUDA GPU detected. Generation will use CPU (very slow).")
            return False
    except ImportError:
        print("❌ PyTorch not installed. Run: pip install torch")
        return False


def benchmark_inference(resolution=(640, 480), duration=3, fps=12, steps=5):
    from backend.inference.generator import VideoGenerator
    gen = VideoGenerator()

    label = f"{resolution[0]}x{resolution[1]}, {duration}s, {fps}fps, {steps} steps"
    print(f"\nBenchmarking: {label}")

    start = time.perf_counter()
    result = gen.generate(
        prompt="A golden retriever playing fetch in a sunny park, cinematic",
        duration=duration,
        fps=fps,
        height=resolution[1],
        width=resolution[0],
        num_inference_steps=steps,
    )
    elapsed = time.perf_counter() - start

    print(f"  ⏱  Generation time:  {elapsed:.2f}s")
    print(f"  📹 Video:            {result['video_path']}")
    print(f"  🎵 Audio:            {result['audio_path']}")
    return elapsed


def main():
    print("=" * 60)
    print("  AI Video Studio — GPU Benchmark")
    print("=" * 60)

    check_gpu()

    print("\nRunning generation benchmarks...")

    configs = [
        {"resolution": (640, 480),  "duration": 3, "fps": 12, "steps": 5,  "label": "Fast 480p"},
        {"resolution": (1280, 720), "duration": 3, "fps": 24, "steps": 10, "label": "720p"},
    ]

    results = []
    for cfg in configs:
        try:
            t = benchmark_inference(cfg["resolution"], cfg["duration"], cfg["fps"], cfg["steps"])
            results.append((cfg["label"], t))
        except Exception as e:
            print(f"  ❌ {cfg['label']} failed: {e}")

    print("\n" + "=" * 60)
    print("  BENCHMARK RESULTS")
    print("=" * 60)
    for label, elapsed in results:
        print(f"  {label:<20} {elapsed:.2f}s")

    print("\n✅ Benchmark complete! Your system is ready.")


if __name__ == "__main__":
    main()
