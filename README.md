---
title: DocuForge AI Studio
emoji: 🎬
colorFrom: indigo
colorTo: amber
sdk: docker
app_port: 7860
pinned: false
---

# DocuForge AI — Autonomous Documentary Production Studio

An AI-powered documentary production studio built for long-form (20-minute, 1080p) investigative YouTube documentaries (inspired by MagnatesMedia, Fern, and Johnny Harris).

## Core Capabilities
- **13 Specialized Autonomous Agents**: Topic Discovery (100-point matrix), Viral Hook Intelligence, Deep Research & Fact-Checking, Master Documentary Storyteller (10-Beat structure, ~2,800 words), Creative Director (11-point scene-level creative direction), Real Footage Discovery (NASA, Wikimedia Commons, Internet Archive, Pexels, Pixabay), Mandatory Visual Approval Gate, Storyboard Engine, Segmented Narration & Sound Design (ElevenLabs Multilingual v2 + FFmpeg EBU R128 -14 LUFS & -16dB ducking), 1080p Cinematic Animation Engine, 6-Pass Professional Creative Editorial Review, Automated Quality Control, Dual Thumbnail Director, and Full ZIP Package Exporter.
- **Strict $50.00/Month Hard Budget Ceiling**: Auto-blocks non-essential paid calls at $50.00 ($40.00 warning), with $0.00 local/container FFmpeg 1080p rendering.

---

## Deploying to the Cloud for Free

### Option 1: Hugging Face Spaces (Recommended — Free 16GB RAM & 2 vCPU)
Hugging Face Spaces offers **16GB RAM and 2 vCPUs for free** on Docker Spaces, which is ideal for 1080p FFmpeg video compositing and OpenCV motion graphics rendering.

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space).
2. Enter a Space name (e.g., `docuforge-ai`), select **Docker** as the Space SDK (choose **Blank** template), and select **Free (CPU Basic - 2 vCPU, 16 GB RAM)**.
3. In your Space **Settings → Variables and secrets**, add your API keys as Secrets (or paste them directly in the **Studio Settings** tab once deployed):
   - `ANTHROPIC_API_KEY`: Your Claude Sonnet 5.5 / 4.5 key
   - `ELEVENLABS_API_KEY`: Your ElevenLabs key for documentary voiceover
   - `PEXELS_API_KEY`: *(Optional)* Free Pexels API key
4. Push this directory to your Hugging Face Space git repository:
   ```bash
   git init
   git add .
   git commit -m "Deploy DocuForge AI Studio"
   git remote add space https://huggingface.co/spaces/<YOUR_USERNAME>/<YOUR_SPACE_NAME>
   git push --force space main
   ```
   *(Because `README.md` already contains `sdk: docker` and `app_port: 7860`, Hugging Face will automatically build `Dockerfile` and launch the studio!)*

---

### Option 2: Render.com (Free Web Service via `render.yaml`)
1. Push this repository to a GitHub repo.
2. Go to [dashboard.render.com/blueprints](https://dashboard.render.com/blueprints) and click **New Blueprint Instance** (or **New Web Service → Docker**).
3. Connect your GitHub repository. Render will automatically detect `render.yaml` and `Dockerfile` on the **Free** plan.
4. Enter your `ANTHROPIC_API_KEY` and `ELEVENLABS_API_KEY` in the Render environment variables prompt (or configure them inside the **Studio Settings** tab in the browser).

---

### Running Locally
```bash
python run.py
```
Then open **http://127.0.0.1:8000** in your browser.
