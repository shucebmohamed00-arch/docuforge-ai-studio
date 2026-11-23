FROM python:3.12-slim

# Install FFmpeg, Flite TTS, and OpenCV system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    flite \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (UID 1000 required for Hugging Face Spaces free tier)
RUN useradd -m -u 1000 docuforge
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy studio application
COPY --chown=docuforge:docuforge . .

# Ensure persistent data & export directories exist and are writable
RUN mkdir -p /app/data/media/audio /app/data/media/animations /app/data/previews /app/data/exports \
    && chown -R docuforge:docuforge /app/data

USER docuforge

ENV HOST=0.0.0.0
ENV PORT=7860
EXPOSE 7860

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
