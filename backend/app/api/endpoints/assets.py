"""
DocuForge AI - Footage Discovery & Visual Approval API Endpoints
"""
import asyncio
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...agents.footage_discovery import RealFootageDiscoveryAgent
from ...core.job_runner import JobRunner

async def discover_assets_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    project_id = data.get("project_id")
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    if data.get("async"):
        def _bg_assets(progress_callback=None):
            if progress_callback:
                progress_callback(15, "Scanning Wikimedia Commons, NASA, and Pixabay archives...")
            RealFootageDiscoveryAgent.discover_assets_for_project(project_id)
            if progress_callback:
                progress_callback(100, "Archival footage discovered.")
            return f"/api/assets/project/{project_id}"

        job_id = JobRunner.run_in_background(
            project_id=project_id,
            job_type="ASSET_DISCOVERY",
            target_func=_bg_assets
        )
        return JSONResponse({"status": "queued", "job_id": job_id})

    try:
        result = await asyncio.to_thread(RealFootageDiscoveryAgent.discover_assets_for_project, project_id)
        return JSONResponse({"status": "success", "result": result})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def get_project_assets_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    assets = RealFootageDiscoveryAgent.get_project_assets(project_id)
    return JSONResponse({"status": "success", "count": len(assets), "assets": assets})

async def approve_asset_endpoint(request: Request) -> JSONResponse:
    asset_id = request.path_params.get("asset_id")
    res = RealFootageDiscoveryAgent.approve_asset(asset_id)
    return JSONResponse(res)

async def reject_asset_endpoint(request: Request) -> JSONResponse:
    asset_id = request.path_params.get("asset_id")
    try:
        data = await request.json()
        reason = data.get("reason", "Rejected by operator")
    except Exception:
        reason = "Rejected by operator"

    res = RealFootageDiscoveryAgent.reject_asset(asset_id, reason)
    return JSONResponse(res)

async def replace_asset_endpoint(request: Request) -> JSONResponse:
    asset_id = request.path_params.get("asset_id")
    res = RealFootageDiscoveryAgent.replace_asset(asset_id)
    return JSONResponse(res)

async def bulk_approve_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    project_id = data.get("project_id")
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    res = RealFootageDiscoveryAgent.bulk_approve_all(project_id)
    return JSONResponse(res)

async def finalize_approvals_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    try:
        res = RealFootageDiscoveryAgent.finalize_asset_approvals(project_id)
        return JSONResponse(res)
    except ValueError as e:
        return JSONResponse({"status": "blocked", "message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
