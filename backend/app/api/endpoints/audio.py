"""
DocuForge AI - Audio & Sound API Endpoints
"""
import asyncio
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...agents.sound_designer import SoundDesignDirector, VoiceProfile
from ...core.job_runner import JobRunner
from ...models.project import ProjectManager

async def synthesize_all_audio_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    project_id = data.get("project_id")
    voice = data.get("voice", VoiceProfile.INVESTIGATIVE_MALE)
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    if data.get("async"):
        def _bg_audio(progress_callback=None):
            if progress_callback:
                progress_callback(15, "Synthesizing ElevenLabs / Neural narration & mastering to -14 LUFS...")
            SoundDesignDirector.synthesize_all_narration(project_id, voice=voice)
            if progress_callback:
                progress_callback(100, "All narration audio tracks synthesized.")
            return f"/api/storyboard/{project_id}"

        job_id = JobRunner.run_in_background(
            project_id=project_id,
            job_type="NARRATION_TTS",
            target_func=_bg_audio
        )
        return JSONResponse({"status": "queued", "job_id": job_id})

    try:
        result = await asyncio.to_thread(SoundDesignDirector.synthesize_all_narration, project_id, voice)
        return JSONResponse({"status": "success", "result": result})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def regenerate_beat_audio_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    project_id = data.get("project_id")
    order_index = int(data.get("order_index", 1))
    updated_narration = data.get("narration")
    voice = data.get("voice", VoiceProfile.INVESTIGATIVE_MALE)

    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    try:
        result = SoundDesignDirector.regenerate_single_beat(
            project_id=project_id,
            order_index=order_index,
            updated_narration=updated_narration,
            voice=voice
        )
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def advance_to_animation_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    try:
        updated = ProjectManager.update_status(project_id, "ANIMATION_SYNTHESIS")
        return JSONResponse({
            "status": "success",
            "message": "Narration & audio tracks locked. Advanced to Stage 9: Animation Studio.",
            "project": updated
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
