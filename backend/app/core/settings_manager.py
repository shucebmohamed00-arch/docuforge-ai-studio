"""
DocuForge AI - Studio Settings & Live Credentials Manager
Persists and retrieves API keys, model selections (Claude Sonnet 5.5 / 4.5, ElevenLabs,
Public Archives, Pexels/Pixabay) in SQLite system_settings with environment variable fallback.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from ..database import get_connection

logger = logging.getLogger("docuforge.settings")

DEFAULT_SETTINGS: Dict[str, Any] = {
    "llm_provider": "anthropic",
    "llm_model": "claude-sonnet-4-5-20250929",
    "custom_model_alias": "claude-sonnet-5.5",
    "anthropic_api_key": "",
    "openai_api_key": "",
    "gemini_api_key": "",
    "tts_provider": "elevenlabs",  # elevenlabs, openai_tts, local_flite
    "elevenlabs_api_key": "",
    "elevenlabs_voice_id": "JBFqnCBsd6RMkjVDRZzb",  # George - Authoritative Documentary Narrator
    "elevenlabs_model_id": "eleven_multilingual_v2",
    "pexels_api_key": "",
    "pixabay_api_key": "",
    "live_archives_enabled": True,  # NASA, Wikimedia Commons, Internet Archive (No key needed)
    "script_target_words": 2800,
    "production_quality_mode": "HUMAN_LEVEL_6_PASS"
}

ENV_FALLBACKS = {
    "anthropic_api_key": "ANTHROPIC_API_KEY",
    "openai_api_key": "OPENAI_API_KEY",
    "gemini_api_key": "GEMINI_API_KEY",
    "elevenlabs_api_key": "ELEVENLABS_API_KEY",
    "pexels_api_key": "PEXELS_API_KEY",
    "pixabay_api_key": "PIXABAY_API_KEY",
}


class SettingsManager:
    @classmethod
    def get_all(cls, mask_secrets: bool = False) -> Dict[str, Any]:
        """Returns complete studio settings dictionary."""
        settings = dict(DEFAULT_SETTINGS)

        # 1. Load environment variable fallbacks
        for key, env_var in ENV_FALLBACKS.items():
            val = os.getenv(env_var, "").strip()
            if val:
                settings[key] = val

        # 2. Override with SQLite persisted settings
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM system_settings")
            for row in cursor.fetchall():
                k = row["key"]
                v = row["value"]
                try:
                    parsed = json.loads(v)
                except Exception:
                    parsed = v
                if k in ENV_FALLBACKS and not parsed and settings.get(k):
                    continue
                settings[k] = parsed
        except Exception as e:
            logger.warning("Failed to read system_settings: %s", e)
        finally:
            conn.close()

        # Compute live connection flags
        settings["status_flags"] = {
            "anthropic_connected": bool(settings.get("anthropic_api_key")),
            "elevenlabs_connected": bool(settings.get("elevenlabs_api_key")),
            "openai_connected": bool(settings.get("openai_api_key")),
            "gemini_connected": bool(settings.get("gemini_api_key")),
            "pexels_connected": bool(settings.get("pexels_api_key")),
            "pixabay_connected": bool(settings.get("pixabay_api_key")),
            "public_archives_connected": bool(settings.get("live_archives_enabled", True)),
        }

        if mask_secrets:
            for secret_key in ENV_FALLBACKS.keys():
                raw = str(settings.get(secret_key, "") or "")
                if len(raw) > 8:
                    settings[secret_key] = f"{raw[:4]}...{raw[-4:]}"
                elif raw:
                    settings[secret_key] = "****"

        return settings

    @classmethod
    def update_settings(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Updates one or more settings in SQLite."""
        conn = get_connection()
        try:
            with conn:
                for k, v in payload.items():
                    if k not in DEFAULT_SETTINGS:
                        continue
                    # Don't overwrite an existing secret with a masked placeholder
                    if k in ENV_FALLBACKS and isinstance(v, str) and ("..." in v or v == "****"):
                        continue
                    conn.execute("""
                    INSERT INTO system_settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(key) DO UPDATE SET
                        value = excluded.value,
                        updated_at = CURRENT_TIMESTAMP
                    """, (k, json.dumps(v)))
        finally:
            conn.close()

        return cls.get_all(mask_secrets=True)
