"""
DocuForge AI - Global Configuration
Handles environment settings, storage paths, and budget limits.
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "docuforge.db"
MEDIA_DIR = DATA_DIR / "media"
ASSETS_DIR = DATA_DIR / "assets"
PREVIEWS_DIR = DATA_DIR / "previews"
EXPORTS_DIR = DATA_DIR / "exports"
STATIC_DIR = BASE_DIR / "frontend" / "static"

# Ensure essential directories exist
for p in [DATA_DIR, MEDIA_DIR, ASSETS_DIR, PREVIEWS_DIR, EXPORTS_DIR, STATIC_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Budget Limits
MONTHLY_HARD_CEILING_USD = float(os.getenv("DOCUFORGE_MONTHLY_LIMIT", "50.00"))
MONTHLY_WARNING_THRESHOLD_USD = float(os.getenv("DOCUFORGE_WARNING_THRESHOLD", "40.00"))
TARGET_COST_PER_DOC_USD = 4.00  # Target ~$28/month for 7 documentaries

# LLM & API Configuration (Modular adapters)
DEFAULT_LLM_PROVIDER = os.getenv("DOCUFORGE_LLM_PROVIDER", "gemini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# Server configuration
HOST = os.getenv("DOCUFORGE_HOST", "127.0.0.1")
PORT = int(os.getenv("DOCUFORGE_PORT", "8000"))
DEBUG = os.getenv("DOCUFORGE_DEBUG", "True").lower() == "true"
