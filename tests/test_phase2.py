"""
DocuForge AI - Phase 2 Test Suite: Topic Discovery & Viral Hook Intelligence
Tests 100-point scoring formula, mandatory rejection rules, hook generator, and selection endpoint.
"""
import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.models.project import ProjectManager
from backend.app.agents.topic_discovery import TopicDiscoveryAgent
from backend.app.agents.hook_intelligence import ViralHookIntelligenceAgent
from backend.app.core.budget_engine import BudgetEngine

client = TestClient(app)

def test_100_point_scoring_and_rejection():
    # Valid high-scoring topic
    valid_topic = {
        "title": "ASML and Extreme Ultraviolet Lithography",
        "has_primary_sources": True,
        "has_free_archival_footage": True,
        "allegations_verifiable": True,
        "scores": {
            "audience_interest": 20,
            "storytelling": 19,
            "originality": 14,
            "visual_availability": 14,
            "research_depth": 15,
            "competition": 8,
            "feasibility": 5
        }
    }
    total, scores, is_rejected, reasons = TopicDiscoveryAgent.evaluate_topic_scores(valid_topic)
    assert total == 95
    assert is_rejected is False
    assert len(reasons) == 0

    # Ineligible topic failing mandatory evidence checks
    flawed_topic = {
        "title": "Secret Lunar Base Funding",
        "has_primary_sources": False,  # Should trigger mandatory rejection
        "has_free_archival_footage": False,
        "allegations_verifiable": False,
        "scores": {
            "audience_interest": 10,
            "storytelling": 10,
            "originality": 5,
            "visual_availability": 2,
            "research_depth": 2,
            "competition": 5,
            "feasibility": 1
        }
    }
    total_flawed, _, is_rejected_flawed, reasons_flawed = TopicDiscoveryAgent.evaluate_topic_scores(flawed_topic)
    assert is_rejected_flawed is True
    assert any("primary sources" in r for r in reasons_flawed)
    assert any("expensive paid footage" in r for r in reasons_flawed)
    assert any("below threshold" in r for r in reasons_flawed)

def test_viral_hook_intelligence_agent():
    sample_topic = {
        "title": "The Swiss Air Grounding",
        "pillar": "BUSINESS",
        "angle": "Corporate collapse due to hidden debt",
        "central_conflict": "Swiss Air vs Credit Suisse"
    }
    hooks = ViralHookIntelligenceAgent.generate_opening_hooks(sample_topic)
    assert len(hooks) == 3
    for hook in hooks:
        assert "narration_script" in hook
        assert "visual_direction" in hook
        assert "sound_direction" in hook
        assert "curiosity_gap" in hook
        assert "intellectual_stakes" in hook

    titles = ViralHookIntelligenceAgent.generate_title_concepts(sample_topic)
    assert len(titles) >= 3
    assert any("Swiss Air Grounding" in t for t in titles)

def test_topic_discovery_pipeline_and_api():
    # 1. Create a project
    proj = ProjectManager.create_project(
        title="Candidate Discovery Run",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    # 2. Trigger Topic Discovery API
    res = client.post("/api/topics/discover", json={"project_id": proj_id})
    assert res.status_code == 200
    data = res.json()["result"]
    candidates = data["candidates"]
    rejected_log = data["rejected_log"]

    # Verify exactly 5 vetted candidates returned
    assert len(candidates) == 5
    for c in candidates:
        assert c["total_score"] >= 70
        assert len(c["hooks"]) == 3
        assert len(c["title_variants"]) >= 3

    # Verify rejected candidate was properly logged
    assert len(rejected_log) >= 1
    assert any("Antarctica" in r["title"] for r in rejected_log)

    # 3. Retrieve topics for project via GET
    get_res = client.get(f"/api/topics/project/{proj_id}")
    assert get_res.status_code == 200
    fetched_topics = get_res.json()["topics"]
    assert len(fetched_topics) == 5

    # 4. User Selects 1 Topic (Step 2)
    selected_topic = candidates[0]
    select_res = client.post("/api/topics/select", json={
        "project_id": proj_id,
        "topic_id": selected_topic["id"]
    })
    assert select_res.status_code == 200
    res_body = select_res.json()
    assert res_body["status"] == "success"
    assert res_body["project"]["status"] == "RESEARCH_IN_PROGRESS"
    assert res_body["project"]["selected_topic_id"] == selected_topic["id"]

    # Clean up project
    ProjectManager.delete_project(proj_id)
