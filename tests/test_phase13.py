"""
DocuForge AI - Phase 13 Test Suite: Final Export Package & Production Report
Tests assembly of documentary package, YouTube descriptions with CC-BY attributions,
comprehensive research_sources dossier, production_report.json, zip bundling,
and download endpoints.
"""
import pytest
import zipfile
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
from backend.app.agents.thumbnail_director import ThumbnailDirector
from backend.app.agents.quality_control import QualityControlAgent
from backend.app.agents.package_exporter import ProductionPackageExporter

client = TestClient(app)

def create_synthetic_test_video(out_path: Path, duration_sec: int = 6):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=darkgreen:s=1920x1080:d={duration_sec}:r=30",
        "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration_sec}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out_path)
    ]
    subprocess.run(cmd, check=True, capture_output=True)

def test_production_package_assembly():
    proj = ProjectManager.create_project(
        title="The Silk Road Trade Collapse",
        pillar="BUSINESS",
        target_duration_mins=20
    )
    proj_id = proj["id"]
    proj_dir = EXPORTS_DIR / proj_id
    proj_dir.mkdir(parents=True, exist_ok=True)

    # 1. Pipeline progression
    DeepResearchAgent.assemble_evidence_dossier(proj_id, "The Silk Road Trade Collapse")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)
    MasterDocumentaryStoryteller.approve_script(proj_id)
    DocumentaryCreativeDirector.generate_visual_manifest(proj_id)
    RealFootageDiscoveryAgent.discover_assets_for_project(proj_id)
    RealFootageDiscoveryAgent.bulk_approve_all(proj_id)
    RealFootageDiscoveryAgent.finalize_asset_approvals(proj_id)

    # 2. Generate media
    create_synthetic_test_video(proj_dir / "documentary.mp4", duration_sec=6)
    (proj_dir / "subtitles.srt").write_text("1\n00:00:00,000 --> 00:00:05,000\nSilk Road trading networks unravel.\n", encoding="utf-8")
    ThumbnailDirector.generate_both_thumbnails(proj_id)

    # 3. Transition pipeline to EXPORT_READY
    ProjectManager.update_status(proj_id, "NARRATION_GENERATION")
    ProjectManager.update_status(proj_id, "ANIMATION_SYNTHESIS")
    ProjectManager.update_status(proj_id, "EDITING_RENDERING")
    ProjectManager.update_status(proj_id, "QUALITY_CONTROL")
    ProjectManager.update_status(proj_id, "EXPORT_READY")

    # 4. Quality control
    QualityControlAgent.inspect_project(proj_id)

    # 5. Assemble package
    pkg = ProductionPackageExporter.assemble_package(proj_id)
    assert pkg["status"] == "success"
    assert pkg["package_zip_size_mb"] >= 0.0
    assert (proj_dir / "docuforge_package.zip").exists()
    assert (proj_dir / "research_sources.txt").exists()
    assert (proj_dir / "youtube_description.txt").exists()
    assert (proj_dir / "production_report.json").exists()

    # 5. Check ZIP contents
    with zipfile.ZipFile(proj_dir / "docuforge_package.zip", "r") as zf:
        namelist = zf.namelist()
        assert "documentary.mp4" in namelist
        assert "thumbnail-1.jpg" in namelist
        assert "thumbnail-2.jpg" in namelist
        assert "subtitles.srt" in namelist
        assert "research_sources.txt" in namelist
        assert "youtube_description.txt" in namelist
        assert "production_report.json" in namelist
        assert "qc_report.json" in namelist

    # 6. Check production report metrics
    report = pkg["production_report"]
    assert report["project_metadata"]["status"] == "COMPLETED"
    assert report["financial_audit"]["local_gpu_rendering_cost_usd"] == 0.0
    assert report["visual_manifest_summary"]["all_assets_approved"] is True

    # 7. Check project status advanced to COMPLETED
    curr = ProjectManager.get_project(proj_id)
    assert curr["status"] == "COMPLETED"

    ProjectManager.delete_project(proj_id)

def test_export_package_api_endpoints():
    proj = ProjectManager.create_project(
        title="The ENIAC Secret Code",
        pillar="TECH",
        target_duration_mins=20
    )
    proj_id = proj["id"]
    proj_dir = EXPORTS_DIR / proj_id
    proj_dir.mkdir(parents=True, exist_ok=True)

    DeepResearchAgent.assemble_evidence_dossier(proj_id, "The ENIAC Secret Code")
    MasterDocumentaryStoryteller.generate_full_script(proj_id)
    MasterDocumentaryStoryteller.approve_script(proj_id)
    DocumentaryCreativeDirector.generate_visual_manifest(proj_id)
    RealFootageDiscoveryAgent.discover_assets_for_project(proj_id)
    RealFootageDiscoveryAgent.bulk_approve_all(proj_id)
    RealFootageDiscoveryAgent.finalize_asset_approvals(proj_id)

    create_synthetic_test_video(proj_dir / "documentary.mp4", duration_sec=6)
    (proj_dir / "subtitles.srt").write_text("1\n00:00:00,000 --> 00:00:05,000\nENIAC electronic computing starts.\n", encoding="utf-8")
    ThumbnailDirector.generate_both_thumbnails(proj_id)
    QualityControlAgent.inspect_project(proj_id)

    ProjectManager.update_status(proj_id, "NARRATION_GENERATION")
    ProjectManager.update_status(proj_id, "ANIMATION_SYNTHESIS")
    ProjectManager.update_status(proj_id, "EDITING_RENDERING")
    ProjectManager.update_status(proj_id, "QUALITY_CONTROL")
    ProjectManager.update_status(proj_id, "EXPORT_READY")

    # 1. POST /api/export/package
    build_resp = client.post("/api/export/package", json={"project_id": proj_id})
    assert build_resp.status_code == 200
    assert build_resp.json()["status"] == "success"

    # 2. GET /api/export/summary/{project_id}
    sum_resp = client.get(f"/api/export/summary/{proj_id}")
    assert sum_resp.status_code == 200
    sum_data = sum_resp.json()
    assert sum_data["has_package"] is True
    assert sum_data["package_url"].endswith(f"/api/export/download/{proj_id}")

    # 3. GET /api/export/download/{project_id}
    down_resp = client.get(f"/api/export/download/{proj_id}")
    assert down_resp.status_code == 200
    assert down_resp.headers["content-type"] == "application/zip"
    assert len(down_resp.content) > 1000

    ProjectManager.delete_project(proj_id)
