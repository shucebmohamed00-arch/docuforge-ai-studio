"""
DocuForge AI - Phase 11 Test Suite: Thumbnail Director
Tests dual 1280x720 16:9 concepts, mobile scale readability validation, and thumbnail API endpoints.
"""
import pytest
from pathlib import Path
from PIL import Image
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.models.project import ProjectManager
from backend.app.agents.thumbnail_director import ThumbnailDirector

client = TestClient(app)

def test_dual_thumbnail_generation(tmp_path):
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    res = ThumbnailDirector.generate_both_thumbnails(proj_id)
    assert res is not None
    assert len(res["thumbnails"]) == 2

    # Check Concept 1
    c1 = res["thumbnails"][0]
    p1 = Path(c1["file_path"])
    assert p1.exists()
    with Image.open(p1) as im:
        assert im.size == (1280, 720)

    # Check Concept 2
    c2 = res["thumbnails"][1]
    p2 = Path(c2["file_path"])
    assert p2.exists()
    with Image.open(p2) as im:
        assert im.size == (1280, 720)

    # Check Mobile Readability
    m1 = c1["mobile_evaluation"]
    assert m1["mobile_width_px"] == 150
    assert m1["readability_score"] > 60

    ProjectManager.delete_project(proj_id)

def test_thumbnail_api_endpoints():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    # 1. POST /api/thumbnails/generate
    gen_res = client.post("/api/thumbnails/generate", json={"project_id": proj_id})
    assert gen_res.status_code == 200
    assert len(gen_res.json()["result"]["thumbnails"]) == 2

    # 2. GET /api/thumbnails/project/{project_id}
    get_res = client.get(f"/api/thumbnails/project/{proj_id}")
    assert get_res.status_code == 200
    assert len(get_res.json()["thumbnails"]) == 2

    ProjectManager.delete_project(proj_id)
