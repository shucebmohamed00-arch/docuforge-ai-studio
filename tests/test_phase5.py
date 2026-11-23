"""
DocuForge AI - Phase 5 Test Suite: Documentary Creative Director & Visual Manifest
Tests sentence-level segmentation, visual mode assignment, manifest generation, and pipeline transition.
"""
import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.models.project import ProjectManager
from backend.app.agents.deep_research import DeepResearchAgent
from backend.app.agents.storyteller import MasterDocumentaryStoryteller
from backend.app.agents.creative_director import (
    DocumentaryCreativeDirector,
    VisualMode,
    TargetAssetType
)

client = TestClient(app)

def test_creative_director_manifest_generation():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    # Research and script setup
    DeepResearchAgent.assemble_evidence_dossier(proj_id, "The Swiss Air Grounding")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)
    MasterDocumentaryStoryteller.approve_script(proj_id)

    # Generate Visual Manifest
    result = DocumentaryCreativeDirector.generate_visual_manifest(proj_id)
    assert result is not None
    assert result["total_beats"] > 20
    assert result["total_duration_sec"] > 200

    manifest = result["manifest"]
    # Check beat fields
    first_beat = manifest[0]
    assert "scene_number" in first_beat
    assert "beat_number" in first_beat
    assert "narration_segment" in first_beat
    assert "visual_concept" in first_beat
    assert "visual_mode" in first_beat
    assert "target_asset_type" in first_beat
    assert "motion_direction" in first_beat
    assert "transition_in" in first_beat
    assert "sound_cue" in first_beat
    assert first_beat["target_duration_sec"] >= 4.0

    # Verify presence of multiple visual modes (Investigative, Cinematic, Explainer)
    modes = {b["visual_mode"] for b in manifest}
    assert VisualMode.INVESTIGATIVE in modes or VisualMode.CINEMATIC in modes

    ProjectManager.delete_project(proj_id)

def test_beat_treatment_update():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]
    DeepResearchAgent.assemble_evidence_dossier(proj_id, "The Swiss Air Grounding")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)
    MasterDocumentaryStoryteller.approve_script(proj_id)
    res = DocumentaryCreativeDirector.generate_visual_manifest(proj_id)
    first_beat_id = res["manifest"][0]["id"]

    # Update beat
    updated = DocumentaryCreativeDirector.update_beat_treatment(
        manifest_id=first_beat_id,
        visual_concept="Cinematic telephoto zoom on Swissair Flight 157 waiting on runway.",
        visual_mode=VisualMode.CINEMATIC,
        target_asset_type=TargetAssetType.ARCHIVAL_VIDEO,
        motion_direction="Telephoto tracking pan left to right."
    )
    assert updated["visual_mode"] == VisualMode.CINEMATIC
    assert "Flight 157" in updated["visual_concept"]

    ProjectManager.delete_project(proj_id)

def test_visual_api_endpoints():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]
    DeepResearchAgent.assemble_evidence_dossier(proj_id, "The Swiss Air Grounding")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)
    MasterDocumentaryStoryteller.approve_script(proj_id)

    # 1. POST /api/visuals/generate-manifest
    gen_res = client.post("/api/visuals/generate-manifest", json={"project_id": proj_id})
    assert gen_res.status_code == 200
    assert gen_res.json()["status"] == "success"

    # 2. GET /api/visuals/manifest/{project_id}
    get_res = client.get(f"/api/visuals/manifest/{proj_id}")
    assert get_res.status_code == 200
    beats = get_res.json()["beats"]
    assert len(beats) > 10

    # 3. PUT /api/visuals/manifest/{manifest_id}
    beat_id = beats[0]["id"]
    put_res = client.put(f"/api/visuals/manifest/{beat_id}", json={
        "visual_concept": "High-altitude satellite view of the Alps and Kloten runway.",
        "visual_mode": "EXPLAINER",
        "target_asset_type": "MAP",
        "motion_direction": "Satellite camera orbital rotation."
    })
    assert put_res.status_code == 200
    assert put_res.json()["beat"]["target_asset_type"] == "MAP"

    # 4. POST /api/visuals/{project_id}/advance
    adv_res = client.post(f"/api/visuals/{proj_id}/advance")
    assert adv_res.status_code == 200
    assert adv_res.json()["project"]["status"] == "FOOTAGE_DISCOVERY"

    ProjectManager.delete_project(proj_id)
