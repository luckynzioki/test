# Troubleshooting Guide

## Common Issues

### 1. "CUDA out of memory"
**Symptoms:** `RuntimeError: CUDA out of memory`

**Fixes (try in order):**
```bash
# A) Lower resolution in .env
DEFAULT_HEIGHT=480
DEFAULT_WIDTH=640

# B) Lower inference steps
DEFAULT_INFERENCE_STEPS=30

# C) Use CPU offloading (already enabled in pipeline wrappers)
# D) Restart server to free VRAM: Ctrl+C then python -m backend.main
```

**VRAM guide:**
| VRAM | Max resolution |
|------|---------------|
| 8 GB | 480p |
| 12 GB | 720p |
| 24 GB | 1080p |
| 32 GB+ | 4K |

---

### 2. Model download fails
```bash
# Fix A: Login to HuggingFace
pip install huggingface-hub
huggingface-cli login

# Fix B: Increase timeout
HF_HUB_DOWNLOAD_TIMEOUT=600 python scripts/download_models.py --models ltx2

# Fix C: Manual download via browser
# Go to https://huggingface.co/Lightricks/LTX-Video
# Download all files to ./models/ltx-2/
```

---

### 3. API server won't start
```bash
# Check port is free
lsof -i :8000
# Kill if occupied: kill -9 <PID>

# Check Python environment is activated
source venv/bin/activate
python -c "import fastapi; print('OK')"

# Run with verbose logging
API_LOG_LEVEL=debug python -m backend.main
```

---

### 4. Frontend won't connect to API
```bash
# Check API is running
curl http://localhost:8000/

# Check CORS — frontend .env
echo "VITE_API_URL=http://localhost:8000" > frontend/.env.local

# Check proxy in vite.config.js — should have:
# proxy: { '/api': { target: 'http://localhost:8000' } }
```

---

### 5. Video file is empty or corrupt
```bash
# Check opencv is installed
python -c "import cv2; print(cv2.__version__)"

# Install if missing
pip install opencv-python-headless

# Check ffmpeg
ffmpeg -version
# Install: sudo apt install ffmpeg
```

---

### 6. CUDA not detected
```bash
# Check NVIDIA driver
nvidia-smi

# Check PyTorch sees GPU
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"

# Reinstall PyTorch with CUDA
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

### 7. Generation is very slow (CPU mode)
Expected times on CPU only:
- 5 sec clip @ 480p, 20 steps → ~15-20 minutes

To confirm GPU is being used:
```bash
# Watch GPU utilisation during generation
watch -n 1 nvidia-smi
```

---

### 8. Tests fail
```bash
# Run with verbose output
TESTING_MODE=1 DEVICE=cpu pytest backend/tests/ -v --tb=long

# Common fix: install test deps
pip install httpx pytest
```

---

## Getting More Help

1. Check `outputs/` for any partially generated files
2. Check server logs in Terminal 1 for stack traces
3. Run the benchmark: `python scripts/benchmark.py`
4. Open a GitHub issue with the full error message
