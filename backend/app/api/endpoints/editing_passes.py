"""
DocuForge AI - Multi-Pass Professional Creative Editing API Endpoints (Directive 27)
"""
import asyncio
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...agents.editing_passes import ProfessionalEditingReviewEngine


async def run_editing_passes_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    project_id = data.get("project_id")
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    try:
        result = await asyncio.to_thread(ProfessionalEditingReviewEngine.run_all_passes, project_id)
        return JSONResponse({"status": "success", "result": result})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


async def get_editing_passes_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    try:
        passes = ProfessionalEditingReviewEngine.get_passes(project_id)
        avg_score = int(round(sum(p["score"] for p in passes) / len(passes))) if passes else 0
        return JSONResponse({
            "status": "success",
            "project_id": project_id,
            "count": len(passes),
            "overall_editorial_score": avg_score,
            "passes": passes
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
