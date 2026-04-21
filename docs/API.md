# API Reference

Base URL: `http://localhost:8000`

Full interactive docs: `http://localhost:8000/docs`

---

## Endpoints

### `GET /`
Health check.

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Video Studio API",
  "version": "0.1.0",
  "gpu_available": true,
  "cuda_device": "NVIDIA RTX 4090",
  "vram_gb": 24.0
}
```

---

### `POST /api/generate`
Submit a video generation job.

**Request body:**
```json
{
  "prompt":               "string (10-500 chars, required)",
  "duration":             5,
  "height":               720,
  "width":                1280,
  "fps":                  24,
  "num_inference_steps":  50,
  "seed":                 null
}
```

| Field | Type | Default | Range | Notes |
|---|---|---|---|---|
| `prompt` | string | — | 10-500 chars | Required |
| `duration` | int | 5 | 1-20 | Seconds |
| `height` | int | 720 | 360-2160 | Pixels |
| `width` | int | 1280 | 360-3840 | Pixels |
| `fps` | int | 24 | 12-60 | Frames per second |
| `num_inference_steps` | int | 50 | 20-100 | Higher = better quality |
| `seed` | int\|null | null | any | For reproducibility |

**Response:**
```json
{
  "job_id":     "uuid",
  "status":     "queued",
  "created_at": "2026-04-21T09:00:00Z",
  "message":    "Video generation queued"
}
```

---

### `GET /api/job/{job_id}`
Poll job status.

**Response:**
```json
{
  "job_id":          "uuid",
  "status":          "processing",
  "progress":        0.45,
  "prompt":          "A cat sleeping...",
  "error":           null,
  "video_url":       null,
  "audio_url":       null,
  "created_at":      "2026-04-21T09:00:00Z",
  "started_at":      "2026-04-21T09:00:01Z",
  "completed_at":    null,
  "duration_seconds": null
}
```

**Status values:**
- `queued` — Waiting to start
- `processing` — Generating frames and audio
- `completed` — Ready to download
- `failed` — Error occurred (see `error` field)

**Poll every 1-2 seconds** until `status` is `completed` or `failed`.

---

### `GET /api/job/{job_id}/video`
Download generated video as MP4.

Returns binary MP4 file. `Content-Disposition: attachment; filename="ai-video-{id}.mp4"`

Only available when `status == "completed"`.

---

### `GET /api/job/{job_id}/audio`
Download generated audio as WAV.

Returns binary WAV file. Only available when `status == "completed"`.

---

### `GET /api/jobs`
List all jobs.

**Query params:**
- `limit` (int, default 50)
- `skip` (int, default 0)

**Response:**
```json
{
  "total": 12,
  "limit": 50,
  "skip": 0,
  "jobs": [
    {
      "job_id": "uuid",
      "status": "completed",
      "prompt": "A cat sleeping...",
      "progress": 1.0,
      "created_at": "2026-04-21T09:00:00Z"
    }
  ]
}
```

---

### `DELETE /api/job/{job_id}`
Delete a job and its files.

**Response:**
```json
{ "message": "Job abc123 deleted" }
```

---

### `GET /api/stats`
Generation statistics.

**Response:**
```json
{
  "total_jobs": 10,
  "completed":  8,
  "failed":     1,
  "processing": 1,
  "average_generation_time": 87.5
}
```

---

### `GET /api/models`
List available models.

**Response:**
```json
{
  "models": [
    {
      "id": "ltx-2",
      "name": "LTX-2",
      "description": "4K video + audio generation",
      "params": "14B video + 5B audio",
      "size_gb": 18
    }
  ]
}
```

---

## Example: Full Workflow (curl)

```bash
# 1. Submit generation
JOB=$(curl -s -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"A golden retriever playing fetch in a sunny park","duration":5}')

JOB_ID=$(echo $JOB | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")
echo "Job ID: $JOB_ID"

# 2. Poll until complete
while true; do
  STATUS=$(curl -s http://localhost:8000/api/job/$JOB_ID | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['status'],d['progress'])")
  echo $STATUS
  echo $STATUS | grep -q completed && break
  echo $STATUS | grep -q failed && break
  sleep 2
done

# 3. Download
curl -o my_video.mp4 http://localhost:8000/api/job/$JOB_ID/video
echo "Downloaded: my_video.mp4"
```

## Example: Full Workflow (Python)

```python
import requests, time

API = "http://localhost:8000"

# Submit
r = requests.post(f"{API}/api/generate", json={
    "prompt": "A golden retriever playing fetch in a sunny park",
    "duration": 5,
    "height": 720,
    "width": 1280,
})
job_id = r.json()["job_id"]
print(f"Job: {job_id}")

# Poll
while True:
    status = requests.get(f"{API}/api/job/{job_id}").json()
    print(f"  {status['status']} — {status['progress']*100:.0f}%")
    if status["status"] in ("completed", "failed"):
        break
    time.sleep(2)

# Download
if status["status"] == "completed":
    video = requests.get(f"{API}/api/job/{job_id}/video")
    with open("my_video.mp4", "wb") as f:
        f.write(video.content)
    print("Saved: my_video.mp4")
else:
    print("Failed:", status["error"])
```
