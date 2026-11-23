"""
DocuForge AI - Phase 6 Test Suite: Footage Discovery & Mandatory Visual Approval Dashboard
Tests free archive harvesting, license validation, individual approval/rejection/replacement,
and hard gate enforcement preventing editing before 100% asset approval.
"""
import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.models.project import ProjectManager
from backend.app.agents.deep_research import DeepResearchAgent
from backend.app.agents.storyteller import MasterDocumentaryStoryteller
from backend.app.agents.creative_director import DocumentaryCreativeDirector
from backend.app.agents.footage_discovery import (
    RealFootageDiscoveryAgent,
    LicenseType,
    AuthenticityClass
)

client = TestClient(app)

def test_footage_discovery_and_license_validation():
    proj = ProjectManager.create_project(
        title="The Swiss Air Grounding",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]

    # Setup pipeline to visual planning
    DeepResearchAgent.assemble_evidence_dossier(proj_id, "The Swiss Air Grounding")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)
    MasterDocumentaryStoryteller.approve_script(proj_id)
    DocumentaryCreativeDirector.generate_visual_manifest(proj_id)

    # 1. Discover assets
    res = RealFootageDiscoveryAgent.discover_assets_for_project(proj_id)
    assert res is not None
    assert res["total_assets"] > 10
    assert res["approval_gate"] == "MANDATORY_ASSET_APPROVAL_REQUIRED"

    assets = res["assets"]
    # Verify licenses are exclusively free / public domain
    valid_licenses = {
        LicenseType.PUBLIC_DOMAIN,
        LicenseType.CC0,
        LicenseType.CC_BY,
        LicenseType.PEXELS_FREE,
        LicenseType.PIXABAY_FREE
    }
    for a in assets:
        assert a["license_type"] in valid_licenses
        assert a["approval_status"] == "PENDING"
        assert a["preview_url"].startswith("http")

    ProjectManager.delete_project(proj_id)

def test_asset_approval_rejection_and_gate_enforcement():
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
    harvest = RealFootageDiscoveryAgent.discover_assets_for_project(proj_id)
    first_asset_id = harvest["assets"][0]["asset_id"]

    # 1. Gate enforcement: Attempt to finalize when assets are PENDING -> MUST FAIL
    with pytest.raises(ValueError, match="Mandatory Approval Gate Blocked"):
        RealFootageDiscoveryAgent.finalize_asset_approvals(proj_id)

    # 2. Reject first asset
    rej_res = RealFootageDiscoveryAgent.reject_asset(first_asset_id, "Low visual clarity")
    assert rej_res["approval_status"] == "REJECTED"

    # Attempting to finalize with rejected asset -> MUST FAIL
    with pytest.raises(ValueError, match="Mandatory Approval Gate Blocked"):
        RealFootageDiscoveryAgent.finalize_asset_approvals(proj_id)

    # 3. Replace rejected asset with alternate candidate
    rep_res = RealFootageDiscoveryAgent.replace_asset(first_asset_id)
    assert rep_res["status"] == "success"

    # 4. Bulk approve all assets
    bulk_res = RealFootageDiscoveryAgent.bulk_approve_all(proj_id)
    assert bulk_res["status"] == "success"

    # 5. Now finalize approvals -> MUST PASS and advance project to STORYBOARD_REVIEW
    fin_res = RealFootageDiscoveryAgent.finalize_asset_approvals(proj_id)
    assert fin_res["status"] == "success"
    assert fin_res["new_status"] == "STORYBOARD_REVIEW"

    # Verify project status in DB
    updated_proj = ProjectManager.get_project(proj_id)
    assert updated_proj["status"] == "STORYBOARD_REVIEW"

    ProjectManager.delete_project(proj_id)

def test_asset_api_endpoints():
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

    # 1. POST /api/assets/discover
    disc_res = client.post("/api/assets/discover", json={"project_id": proj_id})
    assert disc_res.status_code == 200
    assert disc_res.json()["status"] == "success"

    # 2. GET /api/assets/project/{project_id}
    get_res = client.get(f"/api/assets/project/{proj_id}")
    assert get_res.status_code == 200
    assets = get_res.json()["assets"]
    assert len(assets) > 0

    # 3. POST /api/assets/{asset_id}/approve
    asset_id = assets[0]["id"]
    appr_res = client.post(f"/api/assets/{asset_id}/approve")
    assert appr_res.status_code == 200

    # 4. POST /api/assets/bulk-approve
    bulk_res = client.post("/api/assets/bulk-approve", json={"project_id": proj_id})
    assert bulk_res.status_code == 200

    # 5. POST /api/assets/{project_id}/finalize
    fin_res = client.post(f"/api/assets/{proj_id}/finalize")
    assert fin_res.status_code == 200
    assert fin_res.json()["new_status"] == "STORYBOARD_REVIEW"

    ProjectManager.delete_project(proj_id)
