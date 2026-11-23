"""
DocuForge AI - Video Rendering API Endpoints
"""
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...agents.editing_director import CinematicEditingDirector
from ...models.project import ProjectManager
from ...core.job_runner import JobRunner
from ...config import EXPORTS_DIR

async def start_render_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    project_id = data.get("project_id")
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    try:
        def _render_worker(progress_callback=None):
            return CinematicEditingDirector.assemble_documentary(project_id, progress_callback=progress_callback)

        # Launch documentary assembly in a background worker thread
        job_id = JobRunner.run_in_background(
            project_id=project_id,
            job_type="VIDEO_COMPOSITING",
            target_func=_render_worker
        )
        return JSONResponse({
            "status": "success",
            "message": "Documentary rendering started in background worker.",
            "job_id": job_id
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def get_render_job_endpoint(request: Request) -> JSONResponse:
    job_id = request.path_params.get("job_id")
    job = JobRunner.get_job(job_id)
    if not job:
        return JSONResponse({"status": "error", "message": f"Job '{job_id}' not found"}, status_code=404)
    return JSONResponse({"status": "success", "job": job})

async def get_project_export_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    proj_dir = EXPORTS_DIR / project_id
    video_path = proj_dir / "documentary.mp4"
    srt_path = proj_dir / "subtitles.srt"

    has_video = video_path.exists()
    has_srt = srt_path.exists()

    return JSONResponse({
        "status": "success",
        "has_video": has_video,
        "has_subtitles": has_srt,
        "video_url": f"/exports/{project_id}/documentary.mp4" if has_video else None,
        "subtitles_url": f"/exports/{project_id}/subtitles.srt" if has_srt else None,
        "file_size_mb": round(video_path.stat().st_size / (1024 * 1024), 2) if has_video else 0.0
    })

async def advance_to_qc_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    try:
        updated = ProjectManager.update_status(project_id, "QUALITY_CONTROL")
        return JSONResponse({
            "status": "success",
            "message": "Video rendering locked! Advanced to Stage 11: Quality Control Agent.",
            "project": updated
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
