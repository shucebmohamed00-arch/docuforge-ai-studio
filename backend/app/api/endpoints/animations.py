"""
DocuForge AI - Animation Studio API Endpoints
"""
import asyncio
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...agents.animation_director import CinematicAnimationDirector
from ...core.job_runner import JobRunner
from ...models.project import ProjectManager
from ...config import MEDIA_DIR

async def render_all_animations_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    project_id = data.get("project_id")
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    if data.get("async"):
        def _bg_anim(progress_callback=None):
            if progress_callback:
                progress_callback(15, "Rendering 1080p motion graphics, maps, and Ken Burns clips...")
            CinematicAnimationDirector.render_all_animations(project_id)
            if progress_callback:
                progress_callback(100, "All 1080p animation clips rendered.")
            return f"/api/animation/project/{project_id}"

        job_id = JobRunner.run_in_background(
            project_id=project_id,
            job_type="ANIMATION_GEN",
            target_func=_bg_anim
        )
        return JSONResponse({"status": "queued", "job_id": job_id})

    try:
        result = await asyncio.to_thread(CinematicAnimationDirector.render_all_animations, project_id)
        return JSONResponse({"status": "success", "result": result})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def get_project_animations_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    anim_dir = MEDIA_DIR / "animations" / project_id
    clips = []
    if anim_dir.exists():
        for f in sorted(anim_dir.glob("clip_*.mp4")):
            clips.append({
                "filename": f.name,
                "web_url": f"/media/animations/{project_id}/{f.name}"
            })
    return JSONResponse({"status": "success", "count": len(clips), "clips": clips})

async def advance_to_editing_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    try:
        updated = ProjectManager.update_status(project_id, "EDITING_RENDERING")
        return JSONResponse({
            "status": "success",
            "message": "Animation synthesis complete! Advanced to Stage 10: Video Editing & FFmpeg Rendering Pipeline.",
            "project": updated
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
