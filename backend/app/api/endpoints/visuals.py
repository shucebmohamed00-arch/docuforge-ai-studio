"""
DocuForge AI - Visual Planning API Endpoints
"""
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...agents.creative_director import DocumentaryCreativeDirector
from ...models.project import ProjectManager

async def generate_manifest_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    project_id = data.get("project_id")
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    try:
        result = DocumentaryCreativeDirector.generate_visual_manifest(project_id)
        return JSONResponse({"status": "success", "result": result})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def get_manifest_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    beats = DocumentaryCreativeDirector.get_manifest(project_id)
    return JSONResponse({"status": "success", "count": len(beats), "beats": beats})

async def update_beat_endpoint(request: Request) -> JSONResponse:
    manifest_id = request.path_params.get("manifest_id")
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    visual_concept = data.get("visual_concept", "")
    visual_mode = data.get("visual_mode", "CINEMATIC")
    target_asset_type = data.get("target_asset_type", "ARCHIVAL_VIDEO")
    motion_direction = data.get("motion_direction", "")

    try:
        updated = DocumentaryCreativeDirector.update_beat_treatment(
            manifest_id=manifest_id,
            visual_concept=visual_concept,
            visual_mode=visual_mode,
            target_asset_type=target_asset_type,
            motion_direction=motion_direction
        )
        return JSONResponse({"status": "success", "beat": updated})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def advance_to_footage_discovery_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    try:
        updated = ProjectManager.update_status(project_id, "FOOTAGE_DISCOVERY")
        return JSONResponse({
            "status": "success",
            "message": "Visual Manifest locked. Advanced to Stage 6: Real Footage Discovery.",
            "project": updated
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
