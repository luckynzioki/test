#!/usr/bin/env bash
# =============================================================================
#  AI Video Studio — One-Command Setup
#  Usage: chmod +x setup.sh && ./setup.sh
# =============================================================================
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; exit 1; }
info() { echo -e "${BLUE}➜  $1${NC}"; }

echo ""
echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    🎬 AI Video Studio — Setup        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo ""

# ── Check Python ──────────────────────────────────────────────────────────────
info "Checking Python..."
command -v python3 >/dev/null 2>&1 || err "Python 3 not found. Install Python 3.10+"
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
info "Python $PY_VER detected"
[[ $(echo "$PY_VER >= 3.10" | bc -l) -eq 1 ]] || err "Python 3.10+ required (you have $PY_VER)"
ok "Python $PY_VER"

# ── Check Node.js ─────────────────────────────────────────────────────────────
info "Checking Node.js..."
if command -v node >/dev/null 2>&1; then
  ok "Node.js $(node --version)"
else
  warn "Node.js not found — frontend setup will be skipped. Install from https://nodejs.org"
  SKIP_FRONTEND=1
fi

# ── Virtual environment ───────────────────────────────────────────────────────
info "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
  python3 -m venv venv
  ok "Virtual environment created"
else
  warn "Virtual environment already exists — skipping"
fi
source venv/bin/activate
pip install --upgrade pip setuptools wheel -q
ok "pip upgraded"

# ── Copy .env ─────────────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
  cp .env.example .env
  ok ".env created from .env.example"
else
  warn ".env already exists — skipping"
fi

# ── Install Python deps ───────────────────────────────────────────────────────
info "Installing Python dependencies..."
pip install -q python-dotenv fastapi "uvicorn[standard]" pydantic pydantic-settings python-multipart
pip install -q numpy scipy pillow tqdm requests

# PyTorch (try CUDA first, fall back to CPU)
info "Installing PyTorch..."
if python3 -c "import torch; torch.cuda.is_available()" 2>/dev/null; then
  ok "PyTorch already installed with CUDA"
else
  pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 || \
  pip install -q torch torchvision torchaudio  # CPU fallback
fi

# Video/audio libs
pip install -q opencv-python-headless soundfile 2>/dev/null || \
pip install -q opencv-python soundfile

ok "Python dependencies installed"

# ── Check GPU ─────────────────────────────────────────────────────────────────
info "Checking GPU..."
python3 - <<'PYEOF'
import torch, sys
if torch.cuda.is_available():
    name = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"\033[0;32m✅ GPU: {name} ({vram:.1f} GB VRAM)\033[0m")
else:
    print("\033[1;33m⚠️  No CUDA GPU — running on CPU (slow)\033[0m")
PYEOF

# ── Install Node deps ─────────────────────────────────────────────────────────
if [ -z "${SKIP_FRONTEND:-}" ]; then
  info "Installing frontend dependencies..."
  cd frontend
  npm install --silent
  cd ..
  ok "Frontend dependencies installed"
fi

# ── Create required directories ───────────────────────────────────────────────
mkdir -p models outputs
ok "Directories ready"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     🚀 Setup Complete!               ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
echo ""
echo "  Next steps:"
echo ""
echo -e "  ${BLUE}1. Start the API server (Terminal 1):${NC}"
echo "     source venv/bin/activate"
echo "     python -m backend.main"
echo ""
if [ -z "${SKIP_FRONTEND:-}" ]; then
echo -e "  ${BLUE}2. Start the UI (Terminal 2):${NC}"
echo "     cd frontend && npm run dev"
echo ""
echo -e "  ${BLUE}3. Open browser:${NC}"
echo "     http://localhost:3000"
else
echo -e "  ${BLUE}2. Test the API:${NC}"
echo "     curl http://localhost:8000/"
fi
echo ""
echo -e "  ${BLUE}Run tests:${NC}"
echo "     source venv/bin/activate && pytest backend/tests/ -v"
echo ""
