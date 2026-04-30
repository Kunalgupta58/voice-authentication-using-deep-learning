# Stage 1: Build the React frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Build the Python backend
FROM python:3.10-slim

# Install system dependencies, specifically FFmpeg which is required for pydub to function correctly
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libsndfile1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set up a non-root user (required for Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy requirement file
COPY --chown=user requirements.txt .

# Install python packages (CPU only versions matching constraints)
# Added --no-cache-dir to keep image lean
RUN pip install --user --no-cache-dir -r requirements.txt

# Disable HuggingFace symlinks and force CPU Usage via ENV
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1
ENV HF_HUB_DISABLE_SYMLINKS=1
ENV NUMBA_CACHE_DIR=/tmp
ENV MODEL_CACHE_DIR=/tmp/spkrec-ecapa-voxceleb
ENV TEMP_AUDIO_DIR=/tmp/voicekey_temp_audio
ENV PRELOAD_MODEL=0
ENV CORS_ORIGINS=*

# Port configuration for HF Spaces
ENV PORT=7860

# Copy all application files
COPY --chown=user . .

# Copy built frontend from stage 1
COPY --chown=user --from=frontend-builder /app/dist ./dist

# Expose port 7860
EXPOSE 7860

# Start Gunicorn with a single worker by default for lower RAM usage on Spaces.
# WEB_CONCURRENCY can be overridden by environment variable when needed.
CMD gunicorn backend.main:app --workers ${WEB_CONCURRENCY:-1} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 180 --graceful-timeout 120 --keep-alive 30
