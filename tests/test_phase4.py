"""
DocuForge AI - Phase 4 Test Suite: Master Documentary Storyteller
Tests 10-beat narrative script generation, word counts, scene editing, and human approval gate.
"""
import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.models.project import ProjectManager
from backend.app.agents.deep_research import DeepResearchAgent
from backend.app.agents.storyteller import MasterDocumentaryStoryteller

client = TestClient(app)

def test_storyteller_10_beat_generation():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    # Build evidence dossier first
    DeepResearchAgent.assemble_evidence_dossier(proj_id, "The Swiss Air Grounding")

    # Generate Script
    script = MasterDocumentaryStoryteller.generate_full_script(proj_id)
    assert script is not None
    assert script["word_count"] > 1000
    assert script["estimated_duration_sec"] > 600

    scenes = script["scenes"]
    assert len(scenes) == 10, f"Expected 10 narrative scenes, got {len(scenes)}"

    # Check each scene has required directions
    expected_beats = [
        "Opening Hook", "Central Mystery or Question", "Background and Context",
        "Introduction of Main Characters", "Conflict and Stakes", "Escalation",
        "Major Discoveries", "Turning Point or Revelation", "Consequences and Fallout",
        "Final Conclusion"
    ]
    for i, sc in enumerate(scenes):
        assert sc["scene_number"] == i + 1
        assert sc["narrative_beat"] == expected_beats[i]
        assert len(sc["narration"]) > 50
        assert "visual_direction" in sc
        assert "sound_direction" in sc
        assert "transition_intention" in sc
        assert len(sc["evidence_refs"]) > 0

    ProjectManager.delete_project(proj_id)

def test_script_scene_update_and_approval():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]
    DeepResearchAgent.assemble_evidence_dossier(proj_id, "The Swiss Air Grounding")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)

    # 1. Update scene 1 narration
    new_intro = "On a gray October morning in Zurich, air traffic control made a call that signaled the end of an era."
    updated = MasterDocumentaryStoryteller.update_scene_narration(proj_id, 1, new_intro)
    assert updated["scenes"][0]["narration"] == new_intro
    assert updated["scenes"][0]["word_count"] == len(new_intro.split())

    # 2. Checkpoint 1: Approve script
    approve_res = MasterDocumentaryStoryteller.approve_script(proj_id)
    assert approve_res["status"] == "success"
    assert approve_res["new_status"] == "VISUAL_PLANNING"

    # Verify project status in DB
    updated_proj = ProjectManager.get_project(proj_id)
    assert updated_proj["status"] == "VISUAL_PLANNING"

    ProjectManager.delete_project(proj_id)

def test_script_api_endpoints():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]
    DeepResearchAgent.assemble_evidence_dossier(proj_id, "The Swiss Air Grounding")

    # 1. POST /api/script/generate
    gen_res = client.post("/api/script/generate", json={"project_id": proj_id})
    assert gen_res.status_code == 200
    assert gen_res.json()["status"] == "success"

    # 2. GET /api/script/{project_id}
    get_res = client.get(f"/api/script/{proj_id}")
    assert get_res.status_code == 200
    assert len(get_res.json()["script"]["scenes"]) == 10

    # 3. PUT /api/script/{project_id}/update-scene
    put_res = client.put(f"/api/script/{proj_id}/update-scene", json={
        "scene_number": 2,
        "narration": "How does a multi-billion dollar carrier simply vanish into insolvency overnight?"
    })
    assert put_res.status_code == 200

    # 4. POST /api/script/{project_id}/approve [CHECKPOINT 1]
    app_res = client.post(f"/api/script/{proj_id}/approve")
    assert app_res.status_code == 200
    assert app_res.json()["new_status"] == "VISUAL_PLANNING"

    ProjectManager.delete_project(proj_id)
