"""
DocuForge AI - Jobs API Endpoints
"""
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...core.job_runner import JobRunner
from ...database import get_connection

async def get_job_endpoint(request: Request) -> JSONResponse:
    job_id = request.path_params.get("job_id")
    job = JobRunner.get_job(job_id)
    if not job:
        return JSONResponse({"status": "error", "message": f"Job '{job_id}' not found"}, status_code=404)
    return JSONResponse({"status": "success", "job": job})

async def list_project_jobs_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM render_jobs WHERE project_id = ? ORDER BY created_at DESC LIMIT 20", (project_id,))
        jobs = [dict(r) for r in cursor.fetchall()]
        return JSONResponse({"status": "success", "count": len(jobs), "jobs": jobs})
    finally:
        conn.close()
