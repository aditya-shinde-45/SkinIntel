# SkinIntel Setup Guide (Linux + Windows)

This guide is the full setup and runbook for SkinIntel.

It includes:
- Docker setup (recommended)
- Local setup without Docker (Linux and Windows)
- Production-style deployment checklist
- Troubleshooting with fallback commands for common errors

---

## 1. Project Overview

SkinIntel runs 3 services in container mode:
- frontend: React + Vite app served by Nginx on port 80
- backend: Flask API (Gunicorn) on port 5000
- ollama: local LLM and vision model runtime

Main endpoints:
- Frontend: http://localhost
- Backend health: http://localhost:5000/api/v1/health
- Analyze API: http://localhost/api/v1/analyze (proxied via frontend) or http://localhost:5000/api/v1/analyze

Detection stack currently:
- Skin type model: backend/models/model.keras (trained model)
- Condition model: Ollama vision model (llava-phi3 by default)
- Explanation model: Ollama text model (mistral by default)

---

## 2. Prerequisites

### 2.1 Linux (Ubuntu/Debian)
Install:
- Git
- Docker Engine + Docker Compose plugin
- Optional for local run: Python 3.10 or 3.11, Node.js 20+, npm

Commands:

```bash
sudo apt update
sudo apt install -y git curl ca-certificates

# Docker install (official convenience script)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

docker --version
docker compose version
```

### 2.2 Windows 10/11
Install:
- Git for Windows
- Docker Desktop (WSL2 backend enabled)
- Optional for local run: Python 3.10/3.11, Node.js 20+

Verify in PowerShell:

```powershell
docker --version
docker compose version
git --version
```

---

## 3. Clone and Prepare

### Linux
```bash
git clone https://github.com/aditya-shinde-45/SkinIntel.git
cd SkinIntel
```

### Windows (PowerShell)
```powershell
git clone https://github.com/aditya-shinde-45/SkinIntel.git
cd SkinIntel
```

---

## 4. Recommended Run Mode: Docker Compose

This is the easiest and closest to production.

### 4.1 First run

```bash
docker compose up --build
```

Expected behavior:
- backend builds and starts Gunicorn
- frontend builds and serves on port 80
- ollama service starts and pulls llava-phi3 on first boot

First startup can take several minutes because model pull is large.

### 4.2 Run in background

```bash
docker compose up --build -d
```

### 4.3 Check service state

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f ollama
```

### 4.4 Stop

```bash
docker compose down
```

### 4.5 Full reset (containers + volumes)

Warning: this removes persisted Ollama model cache and other compose volumes.

```bash
docker compose down -v
```

---

## 5. Environment Configuration

Primary backend env file:
- backend/.env

Template:
- backend/.env.example

Create env file:

### Linux
```bash
cp backend/.env.example backend/.env
```

### Windows (PowerShell)
```powershell
Copy-Item backend/.env.example backend/.env
```

Important keys in backend/.env:
- MODEL_PATH=models/model.keras
- PRODUCTS_CSV_PATH=data/products.csv
- OLLAMA_URL=http://ollama:11434 (inside Docker) or http://localhost:11434 (local non-Docker)
- OLLAMA_MODEL=mistral
- OLLAMA_VISION_MODEL=llava-phi3
- CONDITION thresholds (for sensitivity tuning)

Security notes:
- Never commit real secrets in env/example files
- Keep AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY empty unless required
- Rotate keys immediately if accidentally exposed

---

## 6. Local Run Without Docker (Development)

Use this only if you specifically need local debugging.

### 6.1 Start Ollama locally
Install from https://ollama.com, then:

```bash
ollama serve
```

In a second terminal pull required models:

```bash
ollama pull llava-phi3
ollama pull mistral
```

### 6.2 Backend local run (Linux)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python run.py
```

### 6.3 Backend local run (Windows PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

### 6.4 Frontend local run (Linux and Windows)

```bash
cd frontend
npm install
npm run dev
```

Frontend default local URL is usually shown by Vite (commonly http://localhost:5173).

---

## 7. Production-Ready Deployment Notes

For production-like operation use Docker with detached mode and restart policies already defined in compose.

Recommended hardening checklist:
- Set ENV=prod in backend/.env
- Use strong JWT_SECRET
- Restrict ALLOWED_ORIGIN to your real domain
- Use HTTPS at reverse proxy/load balancer level
- Use monitored logging (backend + frontend + ollama)
- Set resource limits in orchestration platform
- Keep model and image versions pinned
- Rotate and store secrets outside git

Suggested startup:

```bash
docker compose up --build -d
docker compose ps
```

Health checks:

```bash
curl -f http://localhost:5000/api/v1/health
curl -I http://localhost
```

---

## 8. Troubleshooting and Fallbacks

### 8.1 Backend shows unhealthy in docker compose ps
Symptoms:
- backend status shows unhealthy

Actions:

```bash
docker compose logs --tail=200 backend
curl -f http://localhost:5000/api/v1/health
```

Common fixes:
- Ensure model exists at backend/models/model.keras
- Ensure dataset exists at backend/data/products.csv (or configured path)
- Rebuild backend:

```bash
docker compose up --build -d backend
```

### 8.2 Condition detection returns empty (for example: raw results {})
Symptoms in backend logs:
- Condition pass (broad) raw results: {}
- Condition pass (focused) raw results: {}

Actions:

```bash
docker compose logs -f backend
docker compose logs -f ollama
```

Fix sequence:
1. Rebuild backend so latest parser logic is active:

```bash
docker compose up --build -d backend
```

2. Verify vision model is available in Ollama:

```bash
docker compose exec ollama ollama list
```

3. Pull stronger model and switch if needed:

```bash
docker compose exec ollama ollama pull llava
```

Then set in backend/.env:
- OLLAMA_VISION_MODEL=llava

Restart backend:

```bash
docker compose up --build -d backend
```

4. Tune sensitivity in backend/.env if still missing subtle conditions:
- CONDITION_THRESHOLD_ACNE=0.08 (or 0.06)
- CONDITION_THRESHOLD_DARK_CIRCLES=0.18 (or 0.15)
- CONDITION_THRESHOLD_HYPERPIGMENTATION=0.18 (or 0.15)
- CONDITION_THRESHOLD_WRINKLES=0.16 (or 0.14)
- CONDITION_FOCUSED_RESCUE_MARGIN=0.06 (or 0.08)

Restart backend after each change.

### 8.3 Ollama connection errors
Symptoms:
- backend logs show vision or ollama request failure

Checks:
- In Docker mode, backend must use OLLAMA_URL=http://ollama:11434
- In local mode, backend should use OLLAMA_URL=http://localhost:11434

Commands:

```bash
docker compose logs --tail=100 ollama
docker compose exec backend printenv | grep OLLAMA_URL
```

### 8.4 Port already in use
Symptoms:
- bind errors for 80 or 5000

Find process (Linux):

```bash
sudo lsof -i :80
sudo lsof -i :5000
```

Or change port mapping in docker-compose.yml and restart.

### 8.5 Frontend builds but API calls fail
Checks:
- frontend container should proxy /api to backend via Nginx
- backend health endpoint should return 200

Commands:

```bash
curl -f http://localhost:5000/api/v1/health
docker compose logs --tail=100 frontend
docker compose logs --tail=100 backend
```

### 8.6 Python import error: No module named app
Cause:
- Running scripts from wrong current directory in local mode

Fix:

```bash
cd backend
python run.py
```

Or set PYTHONPATH explicitly:

```bash
PYTHONPATH=/absolute/path/to/SkinIntel/backend python -m app
```

### 8.7 Windows execution policy blocks venv activation
PowerShell fix (Admin):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate venv again.

### 8.8 GitHub push blocked by secret scanning
Symptoms:
- GH013 push protection error

Fix:
- Remove secrets from commit history
- Use placeholders in .env.example files
- Amend commit and push with force-with-lease only when necessary

---

## 9. Useful Operations

Rebuild only backend:

```bash
docker compose up --build -d backend
```

Rebuild only frontend:

```bash
docker compose up --build -d frontend
```

Tail all logs:

```bash
docker compose logs -f
```

Check current branch changes:

```bash
git status --short
git diff
```

---

## 10. Verification Checklist

After setup is complete:
- Frontend opens at http://localhost
- Health endpoint returns 200
- Analyze request completes without backend errors
- Backend logs show condition pass outputs
- Detected conditions are non-empty on obvious test images

If any checklist item fails, use section 8 directly.
