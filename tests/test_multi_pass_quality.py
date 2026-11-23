"""
DocuForge AI - Directive 27 Test Suite: Professional Human-Level Production Quality
Tests:
1. 11-Point Scene-Level Creative Direction on every manifest beat and storyboard cell.
2. 6-Pass Professional Creative Editorial Engine (Narrative, Visual, Motion, Sound, Polish, Final QC).
3. Multi-Pass Editing API endpoints (/api/editing/run-passes, /api/editing/passes/{project_id}).
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
from backend.app.agents.editing_passes import ProfessionalEditingReviewEngine

client = TestClient(app)


def test_eleven_point_scene_creative_direction():
    proj = ProjectManager.create_project(
        title="The Swissair Grounding Crisis",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    DeepResearchAgent.assemble_evidence_dossier(proj_id, "The Swissair Grounding Crisis")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)
    MasterDocumentaryStoryteller.approve_script(proj_id)
    DocumentaryCreativeDirector.generate_visual_manifest(proj_id)
    RealFootageDiscoveryAgent.discover_assets_for_project(proj_id)
    RealFootageDiscoveryAgent.bulk_approve_all(proj_id)
    RealFootageDiscoveryAgent.finalize_asset_approvals(proj_id)

    sb = StoryboardEngine.compile_storyboard(proj_id)
    items = sb["storyboard"]
    assert len(items) > 10

    mandatory_fields = [
        "narrative_purpose",
        "emotional_intention",
        "asset_title",
        "shot_composition",
        "camera_movement",
        "animation_instructions",
        "transition_in",
        "transition_out",
        "sfx_cue",
        "bgm_mood",
        "duration_sec",
        "continuity_requirements"
    ]

    for it in items:
        for field in mandatory_fields:
            assert it.get(field) is not None and str(it.get(field)).strip() != "", (
                f"Scene {it['scene_number']}.{it['beat_number']} missing mandatory creative direction: {field}"
            )

    ProjectManager.delete_project(proj_id)


def test_six_pass_professional_editing_engine():
    proj = ProjectManager.create_project(
        title="The Concorde Supersonic Economics",
        pillar="TECHNOLOGY",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    DeepResearchAgent.assemble_evidence_dossier(proj_id, "The Concorde Supersonic Economics")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)
    MasterDocumentaryStoryteller.approve_script(proj_id)
    DocumentaryCreativeDirector.generate_visual_manifest(proj_id)
    RealFootageDiscoveryAgent.discover_assets_for_project(proj_id)
    RealFootageDiscoveryAgent.bulk_approve_all(proj_id)
    RealFootageDiscoveryAgent.finalize_asset_approvals(proj_id)
    StoryboardEngine.compile_storyboard(proj_id)

    # Execute all 6 editing passes
    res = ProfessionalEditingReviewEngine.run_all_passes(proj_id)
    assert res["total_passes_executed"] == 6
    assert res["editorial_standard_met"] is True
    assert res["overall_editorial_score"] >= 90
    assert res["total_refinements_applied"] >= 6

    passes = res["passes"]
    assert len(passes) == 6
    assert passes[0]["pass_number"] == 1 and "Narrative" in passes[0]["pass_name"]
    assert passes[1]["pass_number"] == 2 and "Visual" in passes[1]["pass_name"]
    assert passes[2]["pass_number"] == 3 and "Motion" in passes[2]["pass_name"]
    assert passes[3]["pass_number"] == 4 and "Sound" in passes[3]["pass_name"]
    assert passes[4]["pass_number"] == 5 and "Cinematic Polish" in passes[4]["pass_name"]
    assert passes[5]["pass_number"] == 6 and "Quality-Control" in passes[5]["pass_name"]

    # Verify refinements were persisted back to storyboard_items
    updated_items = StoryboardEngine.get_storyboard(proj_id)
    assert any("LUT" in (it.get("continuity_requirements") or "") for it in updated_items)
    assert any("J-cut" in (it.get("transition_in") or "") or "L-cut" in (it.get("transition_in") or "") for it in updated_items)

    ProjectManager.delete_project(proj_id)


def test_multi_pass_editing_api_endpoints():
    proj = ProjectManager.create_project(
        title="Panama Canal Geopolitical Chokepoint",
        pillar="GEOPOLITICS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    DeepResearchAgent.assemble_evidence_dossier(proj_id, "Panama Canal Geopolitical Chokepoint")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)
    MasterDocumentaryStoryteller.approve_script(proj_id)
    DocumentaryCreativeDirector.generate_visual_manifest(proj_id)
    RealFootageDiscoveryAgent.discover_assets_for_project(proj_id)
    RealFootageDiscoveryAgent.bulk_approve_all(proj_id)
    RealFootageDiscoveryAgent.finalize_asset_approvals(proj_id)
    StoryboardEngine.compile_storyboard(proj_id)

    # 1. POST /api/editing/run-passes
    post_resp = client.post("/api/editing/run-passes", json={"project_id": proj_id})
    assert post_resp.status_code == 200
    data = post_resp.json()
    assert data["status"] == "success"
    assert data["result"]["total_passes_executed"] == 6

    # 2. GET /api/editing/passes/{project_id}
    get_resp = client.get(f"/api/editing/passes/{proj_id}")
    assert get_resp.status_code == 200
    gdata = get_resp.json()
    assert gdata["status"] == "success"
    assert gdata["count"] == 6
    assert gdata["overall_editorial_score"] >= 90

    ProjectManager.delete_project(proj_id)
