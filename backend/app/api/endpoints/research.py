"""
DocuForge AI - Research & Fact Checking API Endpoints
"""
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...agents.deep_research import DeepResearchAgent
from ...agents.fact_checker import FactCheckingAgent
from ...models.project import ProjectManager
from ...database import get_connection

async def build_dossier_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    project_id = data.get("project_id")
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    project = ProjectManager.get_project(project_id)
    if not project:
        return JSONResponse({"status": "error", "message": f"Project '{project_id}' not found"}, status_code=404)

    topic_title = project.get("title", "")
    try:
        dossier = DeepResearchAgent.assemble_evidence_dossier(project_id, topic_title)
        return JSONResponse({"status": "success", "dossier": dossier})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def get_dossier_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    dossier = DeepResearchAgent.get_dossier(project_id)
    if not dossier:
        return JSONResponse({"status": "error", "message": f"No dossier found for project '{project_id}'"}, status_code=404)
    return JSONResponse({"status": "success", "dossier": dossier})

async def run_fact_check_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    project_id = data.get("project_id")
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    try:
        report = FactCheckingAgent.audit_dossier(project_id)
        # If passed, advance project status to SCRIPTING
        if report["outcome"] == "PASSED":
            conn = get_connection()
            try:
                with conn:
                    conn.execute("UPDATE projects SET status = 'SCRIPTING', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (project_id,))
            finally:
                conn.close()

        return JSONResponse({"status": "success", "report": report})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
