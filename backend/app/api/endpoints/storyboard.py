"""
DocuForge AI - Storyboard API Endpoints
"""
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...agents.storyboard import StoryboardEngine

async def compile_storyboard_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    project_id = data.get("project_id")
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    try:
        result = StoryboardEngine.compile_storyboard(project_id)
        return JSONResponse({"status": "success", "result": result})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def get_storyboard_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    items = StoryboardEngine.get_storyboard(project_id)
    return JSONResponse({"status": "success", "count": len(items), "storyboard": items})

async def update_storyboard_item_endpoint(request: Request) -> JSONResponse:
    item_id = request.path_params.get("item_id")
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    camera_movement = data.get("camera_movement", "")
    transition = data.get("transition", "")
    sfx_cue = data.get("sfx_cue", "")
    bgm_mood = data.get("bgm_mood", "")

    try:
        updated = StoryboardEngine.update_storyboard_item(
            item_id=item_id,
            camera_movement=camera_movement,
            transition=transition,
            sfx_cue=sfx_cue,
            bgm_mood=bgm_mood
        )
        return JSONResponse({"status": "success", "item": updated})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def approve_storyboard_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    try:
        res = StoryboardEngine.approve_storyboard(project_id)
        return JSONResponse(res)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
