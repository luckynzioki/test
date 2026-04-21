# Setup Guide

## Prerequisites

| Requirement | Minimum | Notes |
|---|---|---|
| Python | 3.10+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| GPU | RTX 3060 8 GB | CPU works but is very slow |
| Disk | 40 GB free | For one model + outputs |
| OS | Ubuntu 22 / Windows 10 WSL2 / macOS | |

---

## Linux / WSL2 (Recommended)

```bash
# 1. Clone
git clone https://github.com/yourusername/ai-video-studio.git
cd ai-video-studio

# 2. One-command setup
chmod +x setup.sh && ./setup.sh

# 3. Download the LTX-2 model (~18 GB)
source venv/bin/activate
python scripts/download_models.py --models ltx2

# 4. Start the backend (Terminal 1)
source venv/bin/activate
python -m backend.main

# 5. Start the frontend (Terminal 2)
cd frontend && npm run dev

# 6. Open http://localhost:3000
```

---

## Windows (Native)

1. Install Python 3.10+ from [python.org](https://python.org)
2. Install Node 18+ from [nodejs.org](https://nodejs.org)
3. Install Git from [git-scm.com](https://git-scm.com)
4. Open **PowerShell** and run:

```powershell
git clone https://github.com/yourusername/ai-video-studio.git
cd ai-video-studio

python -m venv venv
venv\Scripts\activate

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install fastapi uvicorn pydantic python-dotenv numpy scipy pillow opencv-python soundfile python-multipart

copy .env.example .env

# Terminal 1 — backend
python -m backend.main

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

---

## macOS (Apple Silicon / Intel)

> Note: No CUDA on macOS. Generation runs on CPU — expect 10-20 min per clip.

```bash
git clone https://github.com/yourusername/ai-video-studio.git
cd ai-video-studio

python3 -m venv venv
source venv/bin/activate

# CPU PyTorch
pip install torch torchvision torchaudio
pip install fastapi uvicorn pydantic python-dotenv numpy scipy pillow opencv-python soundfile python-multipart

cp .env.example .env
# Edit .env: set DEVICE=cpu

python -m backend.main   # Terminal 1
cd frontend && npm install && npm run dev   # Terminal 2
```

---

## Docker (Any Platform)

```bash
git clone https://github.com/yourusername/ai-video-studio.git
cd ai-video-studio

# Build and start everything
docker-compose up --build

# UI: http://localhost:3000
# API: http://localhost:8000
```

> Requires NVIDIA Container Toolkit for GPU support in Docker:
> https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

---

## Environment Variables

All settings live in `.env` (copied from `.env.example` during setup):

```bash
# Which GPU to use (0 = first GPU)
CUDA_VISIBLE_DEVICES=0
DEVICE=cuda          # or cpu

# Default generation quality
DEFAULT_HEIGHT=720
DEFAULT_WIDTH=1280
DEFAULT_INFERENCE_STEPS=50

# Where models and outputs are stored
MODEL_PATH=./models
OUTPUT_PATH=./outputs

# API binding
API_HOST=0.0.0.0
API_PORT=8000
```

---

## Verifying Your Install

```bash
source venv/bin/activate

# 1. Check GPU
python -c "import torch; print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None (CPU mode)')"

# 2. Run tests (no GPU required)
pytest backend/tests/ -v

# 3. Start server and check health
python -m backend.main &
curl http://localhost:8000/
# Should return: {"status":"healthy",...}
```
