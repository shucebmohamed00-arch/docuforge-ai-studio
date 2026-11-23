"""
DocuForge AI - Projects API Endpoints
"""
import json
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...models.project import ProjectManager
from ...core.state_machine import ProjectStatus

async def list_projects_endpoint(request: Request) -> JSONResponse:
    projects = ProjectManager.list_projects()
    if not projects:
        try:
            from ...core.seeder import seed_default_production_if_needed
            seed_default_production_if_needed()
            projects = ProjectManager.list_projects()
        except Exception:
            pass
    return JSONResponse({"status": "success", "count": len(projects), "projects": projects})

async def create_project_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON body"}, status_code=400)
    
    title = data.get("title", "").strip()
    pillar = data.get("pillar", "BUSINESS").strip().upper()
    duration = int(data.get("target_duration_mins", 20))
    metadata = data.get("metadata", {})

    if not title:
        return JSONResponse({"status": "error", "message": "Project title is required"}, status_code=400)
    
    valid_pillars = ["BUSINESS", "GEOPOLITICS", "TECHNOLOGY", "HISTORY"]
    if pillar not in valid_pillars:
        return JSONResponse({"status": "error", "message": f"Pillar must be one of: {valid_pillars}"}, status_code=400)

    try:
        project = ProjectManager.create_project(title=title, pillar=pillar, target_duration_mins=duration, metadata=metadata)
        return JSONResponse({"status": "success", "project": project}, status_code=201)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def get_project_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    project = ProjectManager.get_project(project_id)
    if not project:
        return JSONResponse({"status": "error", "message": f"Project '{project_id}' not found"}, status_code=404)
    return JSONResponse({"status": "success", "project": project})

async def get_project_summary_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    summary = ProjectManager.get_project_full_summary(project_id)
    if not summary:
        return JSONResponse({"status": "error", "message": f"Project '{project_id}' not found"}, status_code=404)
    return JSONResponse({"status": "success", "summary": summary})

async def transition_project_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON body"}, status_code=400)

    target_status = data.get("target_status")
    if not target_status:
        return JSONResponse({"status": "error", "message": "target_status is required"}, status_code=400)

    try:
        updated = ProjectManager.update_status(project_id, target_status)
        return JSONResponse({"status": "success", "project": updated})
    except ValueError as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def delete_project_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    success = ProjectManager.delete_project(project_id)
    if not success:
        return JSONResponse({"status": "error", "message": f"Project '{project_id}' not found"}, status_code=404)
    return JSONResponse({"status": "success", "message": f"Project '{project_id}' deleted"})
