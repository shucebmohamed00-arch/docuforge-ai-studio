"""
DocuForge AI - Scripts API Endpoints
"""
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...agents.storyteller import MasterDocumentaryStoryteller

async def generate_script_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    project_id = data.get("project_id")
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    try:
        script = MasterDocumentaryStoryteller.generate_full_script(project_id)
        return JSONResponse({"status": "success", "script": script})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def get_script_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    script = MasterDocumentaryStoryteller.get_project_script(project_id)
    if not script:
        return JSONResponse({"status": "error", "message": f"No script found for project '{project_id}'"}, status_code=404)
    return JSONResponse({"status": "success", "script": script})

async def update_scene_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    scene_number = int(data.get("scene_number", 0))
    updated_text = data.get("narration", "").strip()

    if not scene_number or not updated_text:
        return JSONResponse({"status": "error", "message": "scene_number and narration are required"}, status_code=400)

    try:
        script = MasterDocumentaryStoryteller.update_scene_narration(project_id, scene_number, updated_text)
        return JSONResponse({"status": "success", "script": script})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def approve_script_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    try:
        result = MasterDocumentaryStoryteller.approve_script(project_id)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
