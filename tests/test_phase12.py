"""
DocuForge AI - Phase 12 Test Suite: Quality Control System
Tests automated master video, audio loudness, subtitle synchronization,
licensing compliance, mandatory QC approval gate, and repair workflow.
"""
import pytest
import subprocess
from pathlib import Path
from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.config import EXPORTS_DIR
from backend.app.models.project import ProjectManager
from backend.app.agents.deep_research import DeepResearchAgent
from backend.app.agents.storyteller import MasterDocumentaryStoryteller
from backend.app.agents.creative_director import DocumentaryCreativeDirector
from backend.app.agents.footage_discovery import RealFootageDiscoveryAgent
from backend.app.agents.quality_control import QualityControlAgent

client = TestClient(app)

def create_synthetic_test_video(out_path: Path, duration_sec: int = 6):
    """Generates a broadcast-standard 1080p test video with test tone for QC verification."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=navy:s=1920x1080:d={duration_sec}:r=30",
        "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration_sec}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out_path)
    ]
    subprocess.run(cmd, check=True, capture_output=True)

def test_quality_control_agent_inspection():
    proj = ProjectManager.create_project(
        title="Operation Entebbe Rescue",
        pillar="HISTORY",
        target_duration_mins=20
    )
    proj_id = proj["id"]
    proj_dir = EXPORTS_DIR / proj_id
    proj_dir.mkdir(parents=True, exist_ok=True)

    # Setup research and assets
    DeepResearchAgent.assemble_evidence_dossier(proj_id, "Operation Entebbe")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)
    MasterDocumentaryStoryteller.approve_script(proj_id)
    DocumentaryCreativeDirector.generate_visual_manifest(proj_id)
    RealFootageDiscoveryAgent.discover_assets_for_project(proj_id)
    RealFootageDiscoveryAgent.bulk_approve_all(proj_id)
    RealFootageDiscoveryAgent.finalize_asset_approvals(proj_id)

    # Create synthetic test media
    video_path = proj_dir / "documentary.mp4"
    srt_path = proj_dir / "subtitles.srt"
    create_synthetic_test_video(video_path, duration_sec=6)

    srt_content = (
        "1\n00:00:00,000 --> 00:00:03,000\nOperation Entebbe begins in silence.\n\n"
        "2\n00:00:03,000 --> 00:00:05,500\nCommandos land on the runway undetected.\n"
    )
    srt_path.write_text(srt_content, encoding="utf-8")

    # 1. Run Quality Control Inspection
    report = QualityControlAgent.inspect_project(proj_id)
    assert report is not None
    assert report["project_id"] == proj_id
    assert report["passed"] is True
    assert report["verdict"] == "PASSED"
    assert report["overall_score"] >= 85

    checks = {c["name"]: c for c in report["checks"]}
    assert "Resolution & 1080p Standard" in checks
    assert checks["Resolution & 1080p Standard"]["status"] == "PASS"
    assert "Audio Stream Presence" in checks
    assert checks["Audio Stream Presence"]["status"] == "PASS"
    assert "Subtitles File (SRT) Availability" in checks
    assert checks["Subtitles File (SRT) Availability"]["status"] == "PASS"
    assert "Mandatory Visual Asset Approval Gate" in checks
    assert checks["Mandatory Visual Asset Approval Gate"]["status"] == "PASS"

    ProjectManager.delete_project(proj_id)

def test_qc_gate_enforcement_and_failure_blocking():
    proj = ProjectManager.create_project(
        title="Unfinished QC Project",
        pillar="TECH",
        target_duration_mins=15
    )
    proj_id = proj["id"]
    proj_dir = EXPORTS_DIR / proj_id
    proj_dir.mkdir(parents=True, exist_ok=True)

    # Set status to QUALITY_CONTROL directly
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
    ProjectManager.update_status(proj_id, "QUALITY_CONTROL")

    # No video or srt exists -> advance MUST fail
    advance_resp = client.post(f"/api/qc/{proj_id}/advance")
    assert advance_resp.status_code == 400
    res_data = advance_resp.json()
    assert res_data["status"] == "error"
    assert res_data["verdict"] == "FAILED"
    assert len(res_data["failures"]) > 0

    # Test repair request returns status to EDITING_RENDERING
    repair_resp = client.post(f"/api/qc/{proj_id}/request-repair")
    assert repair_resp.status_code == 200
    p = ProjectManager.get_project(proj_id)
    assert p["status"] == "EDITING_RENDERING"

    ProjectManager.delete_project(proj_id)

def test_qc_api_endpoints():
    proj = ProjectManager.create_project(
        title="Apollo Guidance Computer",
        pillar="TECH",
        target_duration_mins=20
    )
    proj_id = proj["id"]
    proj_dir = EXPORTS_DIR / proj_id
    proj_dir.mkdir(parents=True, exist_ok=True)

    DeepResearchAgent.assemble_evidence_dossier(proj_id, "Apollo Guidance Computer")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)
    MasterDocumentaryStoryteller.approve_script(proj_id)
    DocumentaryCreativeDirector.generate_visual_manifest(proj_id)
    RealFootageDiscoveryAgent.discover_assets_for_project(proj_id)
    RealFootageDiscoveryAgent.bulk_approve_all(proj_id)
    RealFootageDiscoveryAgent.finalize_asset_approvals(proj_id)

    # Create synthetic test media
    create_synthetic_test_video(proj_dir / "documentary.mp4", duration_sec=6)
    (proj_dir / "subtitles.srt").write_text("1\n00:00:00,000 --> 00:00:04,000\nApollo 11 guidance test.\n", encoding="utf-8")

    # Project is already at STORYBOARD_REVIEW after finalize_asset_approvals
    ProjectManager.update_status(proj_id, "NARRATION_GENERATION")
    ProjectManager.update_status(proj_id, "ANIMATION_SYNTHESIS")
    ProjectManager.update_status(proj_id, "EDITING_RENDERING")
    ProjectManager.update_status(proj_id, "QUALITY_CONTROL")

    # 1. POST /api/qc/run-inspection
    inspect_resp = client.post("/api/qc/run-inspection", json={"project_id": proj_id})
    assert inspect_resp.status_code == 200
    assert inspect_resp.json()["status"] == "success"

    # 2. GET /api/qc/report/{project_id}
    report_resp = client.get(f"/api/qc/report/{proj_id}")
    assert report_resp.status_code == 200
    assert report_resp.json()["report"]["verdict"] == "PASSED"

    # 3. POST /api/qc/{project_id}/advance
    adv_resp = client.post(f"/api/qc/{proj_id}/advance")
    assert adv_resp.status_code == 200
    assert adv_resp.json()["status"] == "success"
    curr = ProjectManager.get_project(proj_id)
    assert curr["status"] == "EXPORT_READY"

    ProjectManager.delete_project(proj_id)
