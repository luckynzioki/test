#!/usr/bin/env python3
"""
Model download script for AI Video Studio
Downloads LTX-2, Wan2.2, and MultiTalk from HuggingFace
"""

import os
import sys
import argparse
from pathlib import Path

def download_model(model_id: str, local_dir: str, token: str = None):
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("Installing huggingface-hub...")
        os.system("pip install huggingface-hub -q")
        from huggingface_hub import snapshot_download

    local_dir = Path(local_dir)
    local_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Downloading: {model_id}")
    print(f"Destination: {local_dir}")
    print(f"{'='*60}")

    try:
        path = snapshot_download(
            model_id,
            local_dir=str(local_dir),
            repo_type="model",
            token=token,
        )
        print(f"✅ Downloaded to: {path}")
        return path
    except Exception as e:
        print(f"❌ Failed to download {model_id}: {e}")
        print(f"   Try manually: huggingface-cli download {model_id} --local-dir {local_dir}")
        return None


MODELS = {
    "ltx2": {
        "id": "Lightricks/LTX-Video",
        "dir": "models/ltx-2",
        "size_gb": 18,
        "description": "Primary video + audio generation model",
    },
    "wan22": {
        "id": "damo-viavi/Wan2.2",
        "dir": "models/wan2.2",
        "size_gb": 16,
        "description": "High-quality visual generation (fallback)",
    },
    "multitalk": {
        "id": "zyx/MultiTalk",
        "dir": "models/multitalk",
        "size_gb": 14,
        "description": "Multi-person conversation generation",
    },
}


def main():
    parser = argparse.ArgumentParser(description="Download AI Video Studio models")
    parser.add_argument("--models", nargs="+", choices=list(MODELS.keys()) + ["all"], default=["ltx2"],
                        help="Which models to download (default: ltx2)")
    parser.add_argument("--token", type=str, default=None,
                        help="HuggingFace token (for gated models)")
    args = parser.parse_args()

    models_to_download = list(MODELS.keys()) if "all" in args.models else args.models

    total_gb = sum(MODELS[m]["size_gb"] for m in models_to_download)
    print(f"\n🚀 AI Video Studio — Model Downloader")
    print(f"   Models to download: {', '.join(models_to_download)}")
    print(f"   Total size: ~{total_gb}GB")
    print(f"   Destination: ./models/")

    confirm = input("\nProceed? [y/N] ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        sys.exit(0)

    results = {}
    for key in models_to_download:
        m = MODELS[key]
        print(f"\n[{key}] {m['description']} (~{m['size_gb']}GB)")
        path = download_model(m["id"], m["dir"], token=args.token)
        results[key] = path

    print("\n\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    for key, path in results.items():
        status = "✅" if path else "❌"
        print(f"{status} {key}: {path or 'FAILED'}")


if __name__ == "__main__":
    main()
