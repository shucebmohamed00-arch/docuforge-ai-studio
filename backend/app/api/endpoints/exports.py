"""
DocuForge AI - Production Export Package API Endpoints
"""
import asyncio
import os
from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse
from ...agents.package_exporter import ProductionPackageExporter
from ...config import EXPORTS_DIR

async def build_export_package_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    project_id = data.get("project_id")
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    try:
        result = await asyncio.to_thread(ProductionPackageExporter.assemble_package, project_id)
        return JSONResponse({"status": "success", "result": result})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def download_package_zip_endpoint(request: Request):
    project_id = request.path_params.get("project_id")
    zip_path = EXPORTS_DIR / project_id / "docuforge_package.zip"
    if not zip_path.exists():
        return JSONResponse({
            "status": "error",
            "message": f"Package ZIP not found for project '{project_id}'. Assemble package first."
        }, status_code=404)

    return FileResponse(
        path=str(zip_path),
        filename=f"docuforge_{project_id}_package.zip",
        media_type="application/zip"
    )

async def get_export_summary_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    proj_dir = EXPORTS_DIR / project_id

    zip_path = proj_dir / "docuforge_package.zip"
    report_path = proj_dir / "production_report.json"

    has_zip = zip_path.exists()
    prod_report = None
    if report_path.exists():
        try:
            import json
            prod_report = json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    return JSONResponse({
        "status": "success",
        "project_id": project_id,
        "has_package": has_zip,
        "package_url": f"/api/export/download/{project_id}" if has_zip else None,
        "package_size_mb": round(zip_path.stat().st_size / (1024*1024), 2) if has_zip else 0.0,
        "production_report": prod_report
    })
