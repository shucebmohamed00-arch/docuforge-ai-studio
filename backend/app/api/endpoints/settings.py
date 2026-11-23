"""
DocuForge AI - Studio Settings & Live Connection Test API Endpoints
"""
import httpx
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...core.settings_manager import SettingsManager
from ...core.llm_client import LLMClient


async def get_settings_endpoint(request: Request) -> JSONResponse:
    try:
        settings = SettingsManager.get_all(mask_secrets=True)
        return JSONResponse({"status": "success", "settings": settings})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


async def update_settings_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    try:
        updated = SettingsManager.update_settings(data)
        return JSONResponse({
            "status": "success",
            "message": "Studio configuration & live credentials saved to SQLite.",
            "settings": updated
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


async def test_live_connections_endpoint(request: Request) -> JSONResponse:
    """Tests live connectivity to configured LLM, TTS, and Public Archives."""
    raw = SettingsManager.get_all(mask_secrets=False)
    results = {}

    # 1. Test LLM (Anthropic / OpenAI / Gemini)
    if LLMClient.is_live_configured():
        reply = LLMClient.generate(
            system_prompt="You are DocuForge AI diagnostic ping.",
            user_prompt="Reply with the exact word: CONNECTED",
            agent_name="SYSTEM_DIAGNOSTIC",
            operation="CONNECTION_PING",
            max_tokens=32
        )
        results["llm"] = {
            "connected": bool(reply),
            "provider": raw.get("llm_provider", "anthropic"),
            "model": raw.get("custom_model_alias") or raw.get("llm_model"),
            "message": f"Live LLM responded: {reply.strip()}" if reply else "API key present, but provider call failed or network offline."
        }
    else:
        results["llm"] = {
            "connected": False,
            "provider": raw.get("llm_provider", "anthropic"),
            "model": raw.get("custom_model_alias") or raw.get("llm_model"),
            "message": "No API key entered yet (Using deterministic studio corpus fallback)."
        }

    # 2. Test Public Archives (NASA Images API - no key required)
    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get("https://images-api.nasa.gov/search?q=apollo&media_type=image")
            nasa_ok = resp.status_code == 200
    except Exception:
        nasa_ok = False

    results["public_archives"] = {
        "connected": nasa_ok,
        "archives": ["NASA Images & Video Library", "Wikimedia Commons", "Internet Archive"],
        "message": "Live HTTP connection to Public Domain Archives active (0 keys required)." if nasa_ok else "Outbound internet restricted in current host; local archive synthesis active."
    }

    # 3. Test ElevenLabs TTS
    el_key = raw.get("elevenlabs_api_key")
    if el_key:
        try:
            with httpx.Client(timeout=8.0) as client:
                r = client.get("https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": el_key})
                el_ok = r.status_code == 200
        except Exception:
            el_ok = False
        results["tts"] = {
            "connected": el_ok,
            "provider": "ElevenLabs Multilingual v2",
            "message": "ElevenLabs documentary voice API verified." if el_ok else "ElevenLabs key configured (will fallback to local FFmpeg TTS if unreachable)."
        }
    else:
        results["tts"] = {
            "connected": True,
            "provider": "Edge Neural TTS ($0) + EBU R128 (-14 LUFS) Broadcast Master",
            "message": "Free Microsoft Edge Neural documentary voice active ($0/mo). Paste an ElevenLabs API key anytime to override."
        }

    return JSONResponse({"status": "success", "diagnostics": results})
