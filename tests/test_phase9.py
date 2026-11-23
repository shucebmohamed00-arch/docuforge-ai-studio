"""
DocuForge AI - Phase 9 Test Suite: Cinematic Animation Engine
Tests animated maps, financial data visualizers, document reveals, photo Ken Burns, and API endpoints.
"""
import pytest
from pathlib import Path
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.models.project import ProjectManager
from backend.app.agents.deep_research import DeepResearchAgent
from backend.app.agents.storyteller import MasterDocumentaryStoryteller
from backend.app.agents.creative_director import DocumentaryCreativeDirector
from backend.app.agents.footage_discovery import RealFootageDiscoveryAgent
from backend.app.agents.storyboard import StoryboardEngine
from backend.app.agents.sound_designer import SoundDesignDirector
from backend.app.agents.animation_director import CinematicAnimationDirector

client = TestClient(app)

def test_individual_motion_graphic_renderers(tmp_path):
    # 1. Test Animated Map (60 frames / 2.0s)
    map_path = tmp_path / "test_map.mp4"
    res_map = CinematicAnimationDirector.render_animated_map(map_path, duration_sec=2.0)
    assert Path(res_map).exists()
    assert Path(res_map).stat().st_size > 1000

    # 2. Test Financial Data Visualization
    chart_path = tmp_path / "test_chart.mp4"
    res_chart = CinematicAnimationDirector.render_financial_chart(chart_path, duration_sec=2.0)
    assert Path(res_chart).exists()
    assert Path(res_chart).stat().st_size > 1000

    # 3. Test Document Highlighter Reveal
    doc_path = tmp_path / "test_doc.mp4"
    res_doc = CinematicAnimationDirector.render_document_reveal(doc_path, duration_sec=2.0)
    assert Path(res_doc).exists()
    assert Path(res_doc).stat().st_size > 1000

    # 4. Test Photo Ken Burns Motion
    photo_path = tmp_path / "test_photo.mp4"
    res_photo = CinematicAnimationDirector.render_photo_ken_burns(None, photo_path, duration_sec=2.0)
    assert Path(res_photo).exists()
    assert Path(res_photo).stat().st_size > 1000

def test_animation_api_endpoints():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    # Advance project state to ANIMATION_SYNTHESIS
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

    # Advance to EDITING_RENDERING
    adv_res = client.post(f"/api/animation/{proj_id}/advance")
    assert adv_res.status_code == 200
    assert adv_res.json()["project"]["status"] == "EDITING_RENDERING"

    ProjectManager.delete_project(proj_id)
