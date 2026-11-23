"""
DocuForge AI - Phase 7 Test Suite: Storyboard Engine
Tests sequential storyboard compilation, audio/visual alignment, cell updates, and Checkpoint #3 approval.
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

client = TestClient(app)

def test_storyboard_compilation_and_sequence():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    # Pipeline setup through Phase 6
    DeepResearchAgent.assemble_evidence_dossier(proj_id, "The Swiss Air Grounding")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)
    MasterDocumentaryStoryteller.approve_script(proj_id)
    DocumentaryCreativeDirector.generate_visual_manifest(proj_id)
    RealFootageDiscoveryAgent.discover_assets_for_project(proj_id)
    RealFootageDiscoveryAgent.bulk_approve_all(proj_id)
    RealFootageDiscoveryAgent.finalize_asset_approvals(proj_id)

    # 1. Compile Storyboard
    res = StoryboardEngine.compile_storyboard(proj_id)
    assert res is not None
    assert res["total_items"] > 10
    assert res["total_duration_sec"] > 200

    items = res["storyboard"]
    first = items[0]
    assert first["order_index"] == 1
    assert "narration_text" in first
    assert "camera_movement" in first
    assert "transition" in first
    assert "sfx_cue" in first
    assert "bgm_mood" in first
    assert first["duration_sec"] >= 4.0

    ProjectManager.delete_project(proj_id)

def test_storyboard_cell_update_and_approval_gate():
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
    comp = StoryboardEngine.compile_storyboard(proj_id)
    first_item_id = comp["storyboard"][0]["id"]

    # 1. Update storyboard cell
    updated = StoryboardEngine.update_storyboard_item(
        item_id=first_item_id,
        camera_movement="Dramatic whip pan into tarmac rain",
        transition="Hard cut on thunderclap",
        sfx_cue="Thunderclap and rain splatter",
        bgm_mood="Dark minor cello ostinato"
    )
    assert updated["transition"] == "Hard cut on thunderclap"
    assert "thunderclap" in updated["sfx_cue"].lower()

    # 2. Checkpoint #3 Approval
    app_res = StoryboardEngine.approve_storyboard(proj_id)
    assert app_res["status"] == "success"
    assert app_res["new_status"] == "NARRATION_GENERATION"

    # Verify project status in DB
    updated_proj = ProjectManager.get_project(proj_id)
    assert updated_proj["status"] == "NARRATION_GENERATION"

    ProjectManager.delete_project(proj_id)

def test_storyboard_api_endpoints():
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

    # 1. POST /api/storyboard/compile
    comp_res = client.post("/api/storyboard/compile", json={"project_id": proj_id})
    assert comp_res.status_code == 200

    # 2. GET /api/storyboard/{project_id}
    get_res = client.get(f"/api/storyboard/{proj_id}")
    assert get_res.status_code == 200
    items = get_res.json()["storyboard"]
    assert len(items) > 0

    # 3. PUT /api/storyboard/{item_id}
    item_id = items[0]["id"]
    put_res = client.put(f"/api/storyboard/{item_id}", json={
        "camera_movement": "Slow zoom in",
        "transition": "Cross dissolve",
        "sfx_cue": "Sub-drone",
        "bgm_mood": "Tense"
    })
    assert put_res.status_code == 200

    # 4. POST /api/storyboard/{project_id}/approve [CHECKPOINT 3]
    app_res = client.post(f"/api/storyboard/{proj_id}/approve")
    assert app_res.status_code == 200
    assert app_res.json()["new_status"] == "NARRATION_GENERATION"

    ProjectManager.delete_project(proj_id)
