FROM python:3.10-slim

# System deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libsndfile1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# HuggingFace Spaces runs containers as a non-root user (uid=1000).
# We create the user here so file permissions work correctly.
RUN useradd -m -u 1000 appuser

WORKDIR /app

COPY requirements.txt .

# Pin numpy FIRST — PyTorch 2.2.x requires numpy < 2.0
RUN pip install --no-cache-dir "numpy>=1.24.0,<2.0.0"
RUN pip install --no-cache-dir -r requirements.txt

ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1
ENV HF_HUB_DISABLE_SYMLINKS=1
ENV NUMBA_CACHE_DIR=/tmp
# HuggingFace Spaces ALWAYS uses port 7860 — do not change this
ENV PORT=7860
ENV WEB_CONCURRENCY=1

COPY --chown=appuser:appuser . .

# Create writable dirs for the non-root user
RUN mkdir -p /app/backend/temp_audio && \
    mkdir -p /app/pretrained_models && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 7860

CMD ["sh", "-c", "gunicorn backend.main:app --workers ${WEB_CONCURRENCY:-1} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:7860 --timeout 180"]
