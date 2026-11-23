"""
DocuForge AI - Audio & Sound API Endpoints
"""
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...agents.sound_designer import SoundDesignDirector, VoiceProfile
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

    try:
        result = SoundDesignDirector.synthesize_all_narration(project_id, voice=voice)
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
