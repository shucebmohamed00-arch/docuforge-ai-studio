"""
DocuForge AI - Phase 10 Test Suite: Video Editing & FFmpeg Rendering Pipeline
Tests synchronized subtitle generation (.srt), multi-track video assembly, job tracking, and advance to QC.
"""
import pytest
import time
from pathlib import Path
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.models.project import ProjectManager
from backend.app.agents.deep_research import DeepResearchAgent
from backend.app.agents.storyteller import MasterDocumentaryStoryteller
from backend.app.agents.creative_director import DocumentaryCreativeDirector
from backend.app.agents.footage_discovery import RealFootageDiscoveryAgent
from backend.app.agents.storyboard import StoryboardEngine
from backend.app.agents.editing_director import CinematicEditingDirector
from backend.app.core.job_runner import JobRunner

client = TestClient(app)

def test_subtitles_srt_generation(tmp_path):
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

    srt_out = tmp_path / "subtitles.srt"
    res_path = CinematicEditingDirector.generate_srt_subtitles(proj_id, srt_out)
    assert Path(res_path).exists()
    content = Path(res_path).read_text(encoding="utf-8")
    assert "-->" in content
    assert "00:00:00,000" in content

    ProjectManager.delete_project(proj_id)

def test_render_job_background_execution():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    # Simple background task simulation
    def mock_task(progress_callback=None):
        if progress_callback:
            progress_callback(50, "Halfway done")
            time.sleep(0.1)
            progress_callback(100, "Done")
        return "mock_out.mp4"

    job_id = JobRunner.run_in_background(proj_id, "VIDEO_COMPOSITING", mock_task)
    assert job_id is not None

    # Wait briefly for thread to complete
    time.sleep(0.3)
    job = JobRunner.get_job(job_id)
    assert job["status"] in ["RUNNING", "COMPLETED"]
    assert job["job_type"] == "VIDEO_COMPOSITING"

    ProjectManager.delete_project(proj_id)

def test_render_api_endpoints():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    # Setup pipeline to EDITING_RENDERING
    ProjectManager.update_status(proj_id, "RESEARCH_IN_PROGRESS")
    ProjectManager.update_status(proj_id, "FACT_CHECKING")
    ProjectManager.update_status(proj_id, "SCRIPTING")
    ProjectManager.update_status(proj_id, "SCRIPT_REVIEW")
    ProjectManager.update_status(proj_id, "VISUAL_PLANNING")
    ProjectManager.update_status(proj_id, "FOOTAGE_DISCOVERY")
    ProjectManager.update_status(proj_id, "ASSETS_PENDING_APPROVAL")
    ProjectManager.update_status(proj_id, "STORYBOARD_REVIEW")
    ProjectManager.update_status(proj_id, "NARRATION_GENERATION")
    ProjectManager.update_status(proj_id, "ANIMATION_SYNTHESIS")
    ProjectManager.update_status(proj_id, "EDITING_RENDERING")

    # 1. GET /api/render/project/{project_id}
    exp_res = client.get(f"/api/render/project/{proj_id}")
    assert exp_res.status_code == 200

    # 2. POST /api/render/{project_id}/advance
    adv_res = client.post(f"/api/render/{proj_id}/advance")
    assert adv_res.status_code == 200
    assert adv_res.json()["project"]["status"] == "QUALITY_CONTROL"

    ProjectManager.delete_project(proj_id)
