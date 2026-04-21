# 🎬 AI Video Studio

> Professional-grade 4K AI video generation — local, open-source, no subscriptions.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev)

Generate Hollywood-quality videos with synchronized audio using the latest open-source AI models — running 100% on your hardware. No API keys. No monthly fees. No data leaves your machine.

---

## ✨ Features

| Feature | Status |
|---|---|
| Text-to-Video generation | ✅ |
| Synchronized audio (speech, foley, ambient) | ✅ |
| Real-time progress tracking | ✅ |
| Video + audio download | ✅ |
| Job history | ✅ |
| REST API | ✅ |
| Docker deployment | ✅ |
| Image-to-Video | 🔜 |
| Voice cloning | 🔜 |
| 4K upscaling pipeline | 🔜 |
| Long-form stitching (15+ min) | 🔜 |

---

## 🚀 Quick Start (5 minutes)

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/ai-video-studio.git
cd ai-video-studio

# 2. Run automated setup
chmod +x setup.sh
./setup.sh

# 3. Start the API (Terminal 1)
source venv/bin/activate
python -m backend.main

# 4. Start the UI (Terminal 2)
cd frontend && npm run dev

# 5. Open http://localhost:3000
```

---

## 💻 Hardware Requirements

| Tier | GPU | VRAM | Resolution | Generation Speed |
|---|---|---|---|---|
| Minimum | RTX 3060 | 8 GB | 480p | ~3 min / 5s clip |
| Recommended | RTX 4090 | 24 GB | 1080p | ~1.5 min / 5s clip |
| Optimal | RTX 5090 | 32 GB+ | 4K | ~4 min / 5s clip |

> **Mac (Apple Silicon):** Limited support — no CUDA. CPU-only generation is very slow.

---

## 📦 Tech Stack

**Backend:** Python 3.10 · FastAPI · PyTorch · OpenCV · FFmpeg  
**Frontend:** React 18 · Vite  
**Models:** LTX-2 (primary) · Wan2.2 (fallback) · MultiTalk (multi-person)  
**Deployment:** Docker · Docker Compose

---

## 🔌 API Reference

### `POST /api/generate`
Submit a video generation job.

**Request:**
```json
{
  "prompt": "A woman walking through a rainy city street at night",
  "duration": 5,
  "height": 720,
  "width": 1280,
  "fps": 24,
  "num_inference_steps": 50
}
```

**Response:**
```json
{
  "job_id": "abc123...",
  "status": "queued",
  "created_at": "2026-04-21T09:00:00Z"
}
```

### `GET /api/job/{job_id}`
Poll job status. Status values: `queued → processing → completed / failed`

### `GET /api/job/{job_id}/video`
Download the generated video (MP4).

### `GET /api/job/{job_id}/audio`
Download the generated audio (WAV).

### `GET /api/jobs`
List all jobs with pagination.

Full Swagger docs: **http://localhost:8000/docs**

---

## ⚙️ Configuration

Edit `.env` (copied from `.env.example` during setup):

```bash
# GPU
CUDA_VISIBLE_DEVICES=0       # Which GPU (0 = first, 0,1 = multi-GPU)
DEVICE=cuda                  # cuda | cpu

# Quality defaults
DEFAULT_HEIGHT=720
DEFAULT_WIDTH=1280
DEFAULT_INFERENCE_STEPS=50   # Higher = better quality, slower

# Paths
MODEL_PATH=./models
OUTPUT_PATH=./outputs

# API
API_PORT=8000
FRONTEND_URL=http://localhost:3000
```

---

## 🐳 Docker

```bash
docker-compose up --build
# UI: http://localhost:3000
# API: http://localhost:8000
```

---

## 🧪 Testing

```bash
source venv/bin/activate
pytest backend/tests/ -v
```

All tests run in CPU-only mode — no GPU required for the test suite.

---

## 📥 Download Models

```bash
source venv/bin/activate

# Download LTX-2 only (recommended first)
python scripts/download_models.py --models ltx2

# Download all models (~48 GB total)
python scripts/download_models.py --models all

# With HuggingFace token (for gated models)
python scripts/download_models.py --models ltx2 --token hf_xxxx
```

---

## 🏃 Benchmark

```bash
source venv/bin/activate
python scripts/benchmark.py
```

---

## 🗂️ Project Structure

```
ai-video-studio/
├── backend/
│   ├── main.py              # API server entry point
│   ├── config.py            # Configuration
│   ├── api/
│   │   ├── routes.py        # All API endpoints
│   │   └── models.py        # Request/response types
│   ├── inference/
│   │   └── generator.py     # Video generation engine
│   ├── services/
│   │   └── job_manager.py   # Job queue management
│   ├── utils/
│   │   ├── ffmpeg.py        # Video stitching utilities
│   │   └── logger.py        # Logging
│   └── tests/
│       └── test_api.py      # Test suite
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx           # Main app component
│       ├── api.js            # API client
│       └── components/
│           ├── GenerationForm.jsx
│           ├── ProgressIndicator.jsx
│           ├── VideoPlayer.jsx
│           └── JobHistory.jsx
├── scripts/
│   ├── download_models.py
│   └── benchmark.py
├── models/                  # (git-ignored) Model weights
├── outputs/                 # (git-ignored) Generated videos
├── setup.sh                 # One-command setup
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Make changes + add tests
4. Run: `pytest backend/tests/ -v && cd frontend && npm run lint`
5. Open a PR!

---

## 📜 License

Apache 2.0 — free to use, modify, and distribute commercially.  
Model weights have their own licenses — check HuggingFace for details.

---

## 🙏 Acknowledgments

Built on top of: **LTX-2** (Lightricks) · **Wan2.2** (Alibaba) · **MultiTalk** · **FastAPI** · **React**
