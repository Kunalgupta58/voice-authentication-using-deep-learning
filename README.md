---
title: VoiceKey Biometric Auth
emoji: "🎤"
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# VoiceKey: Biometric Voice Authentication System

A full-stack voice biometric authentication app with React frontend and FastAPI backend. It uses SpeechBrain ECAPA-TDNN for speaker verification plus liveness checks to reject replay or synthetic audio.

## Deployment Target
This project is ready to deploy as a Hugging Face Space using a custom Docker container.

- Frontend: React + Vite statically built into `dist`
- Backend: FastAPI with model serving and static frontend hosting
- Database: Configurable by `DATABASE_URL`, including Neon Postgres
- Model: `speechbrain/spkrec-ecapa-voxceleb` loaded at runtime
- Audio: `ffmpeg` support provided in the Docker container

## Hugging Face Spaces + Neon Deployment
### What is already supported
- `Dockerfile` is configured for HF Spaces
- `PORT=7860` is exposed and used in the runtime command
- `PRELOAD_MODEL=0` is set by default for faster startup
- `CORS_ORIGINS=*` is enabled in the container for the Spaces frontend
- `DATABASE_URL` is read from the environment and supports Neon
- `postgres://` URIs are automatically rewritten to `postgresql://`

### Required environment variables
Create a Hugging Face secret or `.env` with:

```ini
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
PRELOAD_MODEL=0
CORS_ORIGINS=*
WEB_CONCURRENCY=1
MODEL_CACHE_DIR=/tmp/spkrec-ecapa-voxceleb
TEMP_AUDIO_DIR=/tmp/voicekey_temp_audio
```

> For Neon, use the connection string provided by your Neon dashboard.

### Hugging Face Space setup steps
1. Push this repository to GitHub.
2. Create a new Hugging Face Space.
3. Select `Docker` as the SDK.
4. Connect the repo or upload the source.
5. Add required secrets for `DATABASE_URL`, `SECRET_KEY`, and optional settings.
6. Deploy.

### Notes for Neon
- Neon provides a Postgres-compatible connection string.
- The app uses SQLAlchemy and `psycopg2-binary` to connect.
- Set `DATABASE_URL` in HF Spaces secrets to the Neon URI.

## Local Docker deployment

Build and run locally:

```bash
docker build -t voicekey-app .
docker run -p 7860:7860 \
  -e DATABASE_URL="postgresql://<user>:<pass>@<host>:<port>/<db>" \
  -e SECRET_KEY="super-secret" \
  -e PRELOAD_MODEL=0 \
  voicekey-app
```

## Local development

Install dependencies:

```bash
python -m pip install -r requirements.txt
npm install
npm run build
```

Run backend locally:

```bash
python backend/main.py
```

Open `http://127.0.0.1:8000` after startup.

## How the Neon integration works
- `backend/config.py` reads `DATABASE_URL`
- If the URL begins with `postgres://`, it is rewritten to `postgresql://`
- `backend/database.py` uses the same URL for SQLAlchemy
- `psycopg2-binary` is included in `requirements.txt`

## Important deployment details
- `Dockerfile` installs `ffmpeg` and `libsndfile1` so WebM audio can be converted in the container.
- `backend/main.py` serves the static frontend from `dist` if present.
- `PRELOAD_MODEL=0` prevents heavy model download on startup; the model loads lazily on first request.
- `WEB_CONCURRENCY=1` is recommended for Hugging Face Spaces to reduce memory usage.

## API Overview
- `GET /api/health`
- `GET /api/liveness-phrase`
- `POST /api/register`
- `POST /api/login`
- `GET /api/admin/users`
- `DELETE /api/admin/users/{user_id}`

## Recommended additions
- Add a `.env.example` file for developer and deployment reference.
- Keep secrets out of git.
