"""
DocuForge AI - Thumbnails API Endpoints
"""
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...agents.thumbnail_director import ThumbnailDirector
from ...config import EXPORTS_DIR

async def generate_thumbnails_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    project_id = data.get("project_id")
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    try:
        result = ThumbnailDirector.generate_both_thumbnails(project_id)
        return JSONResponse({"status": "success", "result": result})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def get_project_thumbnails_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    proj_dir = EXPORTS_DIR / project_id
    t1_path = proj_dir / "thumbnail-1.jpg"
    t2_path = proj_dir / "thumbnail-2.jpg"

    thumbnails = []
    if t1_path.exists():
        thumbnails.append({
            "concept_number": 1,
            "title": "Forensic / Direct Evidence Drama",
            "web_url": f"/exports/{project_id}/thumbnail-1.jpg",
            "mobile_evaluation": ThumbnailDirector.evaluate_mobile_readability(t1_path)
        })
    if t2_path.exists():
        thumbnails.append({
            "concept_number": 2,
            "title": "Systemic Financial Mystery Drama",
            "web_url": f"/exports/{project_id}/thumbnail-2.jpg",
            "mobile_evaluation": ThumbnailDirector.evaluate_mobile_readability(t2_path)
        })

    return JSONResponse({"status": "success", "count": len(thumbnails), "thumbnails": thumbnails})
