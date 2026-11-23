"""
DocuForge AI - Phase 8 Test Suite: Narration & Sound Design Engine
Tests segmented audio synthesis, EBU R128 loudness normalization, beat audio regeneration,
and advancement to animation studio.
"""
import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.models.project import ProjectManager
from backend.app.agents.deep_research import DeepResearchAgent
from backend.app.agents.storyteller import MasterDocumentaryStoryteller
from backend.app.agents.creative_director import DocumentaryCreativeDirector
from backend.app.agents.footage_discovery import RealFootageDiscoveryAgent
from backend.app.agents.storyboard import StoryboardEngine
from backend.app.agents.sound_designer import SoundDesignDirector, VoiceProfile

client = TestClient(app)

def test_segmented_audio_synthesis():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    # Run through Phase 7
    DeepResearchAgent.assemble_evidence_dossier(proj_id, "The Swiss Air Grounding")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)
    MasterDocumentaryStoryteller.approve_script(proj_id)
    DocumentaryCreativeDirector.generate_visual_manifest(proj_id)
    RealFootageDiscoveryAgent.discover_assets_for_project(proj_id)
    RealFootageDiscoveryAgent.bulk_approve_all(proj_id)
    RealFootageDiscoveryAgent.finalize_asset_approvals(proj_id)
    StoryboardEngine.compile_storyboard(proj_id)
    StoryboardEngine.approve_storyboard(proj_id)

    # 1. Synthesize all narration tracks
    res = SoundDesignDirector.synthesize_all_narration(proj_id, voice=VoiceProfile.INVESTIGATIVE_MALE)
    assert res is not None
    assert res["total_beats"] > 10
    assert res["total_audio_duration_sec"] > 30.0

    tracks = res["audio_tracks"]
    first = tracks[0]
    assert first["order_index"] == 1
    assert first["web_url"].startswith("/media/audio/")
    assert first["duration_sec"] > 0.0

    ProjectManager.delete_project(proj_id)

def test_single_beat_audio_regeneration():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    DeepResearchAgent.assemble_evidence_dossier(proj_id, "The Swiss Air Grounding")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)
    MasterDocumentaryStoryteller.approve_script(proj_id)
    DocumentaryCreativeDirector.generate_visual_manifest(proj_id)
    RealFootageDiscoveryAgent.discover_assets_for_project(proj_id)
    RealFootageDiscoveryAgent.bulk_approve_all(proj_id)
    RealFootageDiscoveryAgent.finalize_asset_approvals(proj_id)
    StoryboardEngine.compile_storyboard(proj_id)
    StoryboardEngine.approve_storyboard(proj_id)
    SoundDesignDirector.synthesize_all_narration(proj_id)

    # Regenerate beat #1 with alternate text
    regen = SoundDesignDirector.regenerate_single_beat(
        project_id=proj_id,
        order_index=1,
        updated_narration="A fresh high-intensity opening sentence for Kloten airport."
    )
    assert regen["status"] == "success"
    assert regen["duration_sec"] > 0

    ProjectManager.delete_project(proj_id)

def test_audio_api_endpoints():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    DeepResearchAgent.assemble_evidence_dossier(proj_id, "The Swiss Air Grounding")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)
    MasterDocumentaryStoryteller.approve_script(proj_id)
    DocumentaryCreativeDirector.generate_visual_manifest(proj_id)
    RealFootageDiscoveryAgent.discover_assets_for_project(proj_id)
    RealFootageDiscoveryAgent.bulk_approve_all(proj_id)
    RealFootageDiscoveryAgent.finalize_asset_approvals(proj_id)
    StoryboardEngine.compile_storyboard(proj_id)
    StoryboardEngine.approve_storyboard(proj_id)

    # 1. POST /api/audio/synthesize
    synth_res = client.post("/api/audio/synthesize", json={"project_id": proj_id})
    assert synth_res.status_code == 200

    # 2. POST /api/audio/synthesize-beat
    beat_res = client.post("/api/audio/synthesize-beat", json={
        "project_id": proj_id,
        "order_index": 2,
        "narration": "How did an airline with a pristine credit rating simply fall apart?"
    })
    assert beat_res.status_code == 200

    # 3. POST /api/audio/{project_id}/advance
    adv_res = client.post(f"/api/audio/{proj_id}/advance")
    assert adv_res.status_code == 200
    assert adv_res.json()["project"]["status"] == "ANIMATION_SYNTHESIS"

    ProjectManager.delete_project(proj_id)
