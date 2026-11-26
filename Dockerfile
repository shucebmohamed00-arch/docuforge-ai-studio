FROM python:3.12-slim

# Install FFmpeg, Flite TTS, and OpenCV system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    flite \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy studio application
COPY . .

# Ensure persistent data & export directories exist and are writable
RUN mkdir -p /app/data/media/audio /app/data/media/animations /app/data/previews /app/data/exports \
    && chmod -R 777 /app

ENV HOST=0.0.0.0
ENV PORT=7860
ENV PYTHONPATH="/app"
EXPOSE 7860

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
