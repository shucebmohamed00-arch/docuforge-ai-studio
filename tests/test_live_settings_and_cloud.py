"""
DocuForge AI - Live Connectors & Free Cloud Deployment Test Suite
Tests:
1. SettingsManager persistence, Claude Sonnet 5.5 model selection, and secret masking.
2. /api/settings GET & POST endpoints + /api/settings/test-connection diagnostic endpoint.
3. Cloud deployment artifacts (Dockerfile, render.yaml, requirements.txt, HF Spaces README header).
"""
from pathlib import Path
from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.config import BASE_DIR
from backend.app.core.settings_manager import SettingsManager
from backend.app.core.llm_client import LLMClient

client = TestClient(app)


def test_settings_manager_and_secret_masking():
    # Update settings with Claude Sonnet 5.5 and a test key
    updated = SettingsManager.update_settings({
        "llm_provider": "anthropic",
        "custom_model_alias": "claude-sonnet-5.5",
        "anthropic_api_key": "sk-ant-api03-testkey1234567890",
        "tts_provider": "elevenlabs",
        "elevenlabs_voice_id": "JBFqnCBsd6RMkjVDRZzb",
        "script_target_words": 2800
    })

    # Masked output should hide full key
    assert updated["custom_model_alias"] == "claude-sonnet-5.5"
    assert "..." in updated["anthropic_api_key"]
    assert updated["status_flags"]["anthropic_connected"] is True
    assert updated["status_flags"]["public_archives_connected"] is True

    # Reset test key so other tests run in deterministic offline mode
    SettingsManager.update_settings({"anthropic_api_key": ""})
    raw = SettingsManager.get_all(mask_secrets=False)
    assert raw["anthropic_api_key"] == ""


def test_settings_and_diagnostics_api_endpoints():
    # 1. GET /api/settings
    get_res = client.get("/api/settings")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["status"] == "success"
    assert "llm_provider" in data["settings"]

    # 2. POST /api/settings
    post_res = client.post("/api/settings", json={
        "llm_provider": "anthropic",
        "custom_model_alias": "claude-sonnet-5.5",
        "script_target_words": 2900
    })
    assert post_res.status_code == 200
    assert post_res.json()["settings"]["script_target_words"] == 2900

    # 3. POST /api/settings/test-connection
    diag_res = client.post("/api/settings/test-connection")
    assert diag_res.status_code == 200
    diag = diag_res.json()["diagnostics"]
    assert "llm" in diag
    assert "public_archives" in diag
    assert "tts" in diag


def test_cloud_deployment_configurations():
    dockerfile = BASE_DIR / "Dockerfile"
    render_yaml = BASE_DIR / "render.yaml"
    reqs = BASE_DIR / "requirements.txt"
    readme = BASE_DIR / "README.md"

    assert dockerfile.exists()
    df_text = dockerfile.read_text(encoding="utf-8")
    assert "ffmpeg" in df_text
    assert "7860" in df_text

    assert render_yaml.exists()
    ry_text = render_yaml.read_text(encoding="utf-8")
    assert "ANTHROPIC_API_KEY" in ry_text
    assert "ELEVENLABS_API_KEY" in ry_text

    assert reqs.exists()
    assert readme.exists()
    rm_text = readme.read_text(encoding="utf-8")
    assert "sdk: docker" in rm_text
    assert "app_port: 7860" in rm_text
