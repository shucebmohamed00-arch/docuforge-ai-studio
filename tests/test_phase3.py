"""
DocuForge AI - Phase 3 Test Suite: Deep Research & Fact-Checking Engine
Tests evidence dossier assembly, claim classifications, source traceability, and fact-checking audit.
"""
import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.models.project import ProjectManager
from backend.app.agents.deep_research import DeepResearchAgent, ClaimClassification
from backend.app.agents.fact_checker import FactCheckingAgent

client = TestClient(app)

def test_evidence_dossier_structure_and_classifications():
    # Create test project
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    # Assemble Evidence Dossier
    dossier = DeepResearchAgent.assemble_evidence_dossier(proj_id, "The Swiss Air Grounding")
    assert dossier is not None
    assert "central_question" in dossier
    assert "background_summary" in dossier
    assert len(dossier["key_figures"]) >= 2
    assert len(dossier["timeline_events"]) >= 3
    assert len(dossier["claims"]) >= 3
    assert len(dossier["sources"]) >= 2
    assert dossier["confidence_score"] >= 0.85

    # Verify claim classifications
    classifications = {c["classification"] for c in dossier["claims"]}
    assert ClaimClassification.VERIFIED_FACT in classifications
    assert ClaimClassification.DISPUTED_CLAIM in classifications

    # Verify all sources have URL, publisher, and type
    for s in dossier["sources"]:
        assert s["url"].startswith("http")
        assert s["publisher"] != ""
        assert s["source_type"] != ""

    ProjectManager.delete_project(proj_id)

def test_fact_checking_agent_audit():
    proj = ProjectManager.create_project(
        title="ASML and the Light Trap",
        pillar="TECHNOLOGY",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    # Assemble dossier
    DeepResearchAgent.assemble_evidence_dossier(proj_id, "ASML and the Light Trap")

    # Run Fact Check Audit
    report = FactCheckingAgent.audit_dossier(proj_id)
    assert report is not None
    assert report["outcome"] in ["PASSED", "NEEDS_REVISION"]
    assert report["metrics"]["verified_claims"] > 0
    assert report["dossier_status"] == "VERIFIED"

    ProjectManager.delete_project(proj_id)

def test_research_and_fact_checking_api_endpoints():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    # 1. POST /api/research/build-dossier
    build_res = client.post("/api/research/build-dossier", json={"project_id": proj_id})
    assert build_res.status_code == 200
    assert build_res.json()["status"] == "success"
    assert "dossier" in build_res.json()

    # 2. GET /api/research/dossier/{project_id}
    get_res = client.get(f"/api/research/dossier/{proj_id}")
    assert get_res.status_code == 200
    assert get_res.json()["dossier"]["project_id"] == proj_id

    # 3. POST /api/research/fact-check
    fc_res = client.post("/api/research/fact-check", json={"project_id": proj_id})
    assert fc_res.status_code == 200
    fc_data = fc_res.json()
    assert fc_data["status"] == "success"
    assert fc_data["report"]["outcome"] == "PASSED"

    # Verify project status advanced to SCRIPTING
    updated_proj = ProjectManager.get_project(proj_id)
    assert updated_proj["status"] == "SCRIPTING"

    ProjectManager.delete_project(proj_id)
