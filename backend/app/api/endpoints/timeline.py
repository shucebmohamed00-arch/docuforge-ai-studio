"""
DocuForge AI - Multitrack Documentary Editing Timeline API
Provides shot-level inspection, multitrack breakdown (Video, Narration, Music, SFX, Graphics, Titles, Transitions),
and selective shot-level updates/regeneration.
"""

import json
import asyncio
from pathlib import Path
from starlette.requests import Request
from starlette.responses import JSONResponse

from ...database import get_connection

try:
    from docuforge_engine.agents.intelligent_director import IntelligentEditingDirector
except ImportError:
    IntelligentEditingDirector = None

async def get_multitrack_timeline_endpoint(request: Request) -> JSONResponse:
    """
    Returns the complete 7-track documentary editing timeline:
    1. Video Track
    2. Narration Track
    3. Music Track
    4. Sound Effects Track
    5. Graphics Track
    6. Titles Track
    7. Transitions Track
    """
    project_id = request.path_params.get("project_id")
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("""
            SELECT * FROM editing_shots
            WHERE project_id = ?
            ORDER BY start_time_sec ASC
        """, (project_id,))
        rows = c.fetchall()

        # If no shots exist yet, trigger initial direction
        if not rows:
            director = IntelligentEditingDirector(Path("."))
            await asyncio.to_thread(director.direct_and_persist_project_timeline, project_id)
            c.execute("""
                SELECT * FROM editing_shots
                WHERE project_id = ?
                ORDER BY start_time_sec ASC
            """, (project_id,))
            rows = c.fetchall()

        video_track = []
        narration_track = []
        music_track = []
        sfx_track = []
        graphics_track = []
        titles_track = []
        transitions_track = []

        total_dur = 0.0
        for r in rows:
            shot_dict = dict(r)
            s_start = shot_dict["start_time_sec"]
            s_end = shot_dict["end_time_sec"]
            s_dur = shot_dict["duration_sec"]
            total_dur = max(total_dur, s_end)

            # 1. Video Track
            video_track.append({
                "shot_id": shot_dict["id"],
                "scene_number": shot_dict["scene_number"],
                "shot_index": shot_dict["shot_index"],
                "start_time": s_start,
                "end_time": s_end,
                "duration": s_dur,
                "asset_ref": shot_dict["approved_asset_ref"],
                "authenticity_class": shot_dict["asset_authenticity_class"],
                "shot_type": shot_dict["shot_type"],
                "composition": shot_dict["composition"],
                "camera_movement": shot_dict["camera_movement"],
                "is_approved": bool(shot_dict["is_approved"]),
                "rendered_clip_path": shot_dict["rendered_clip_path"]
            })

            # 2. Narration Track
            if shot_dict.get("narration_segment"):
                narration_track.append({
                    "shot_id": shot_dict["id"],
                    "start_time": s_start,
                    "end_time": s_end,
                    "text": shot_dict["narration_segment"],
                    "narrative_purpose": shot_dict["narrative_purpose"],
                    "emotional_intention": shot_dict["emotional_intention"]
                })

            # 3. Music Track
            music_track.append({
                "shot_id": shot_dict["id"],
                "start_time": s_start,
                "end_time": s_end,
                "instruction": shot_dict["music_instructions"],
                "is_silence": "SILENCE" in shot_dict["music_instructions"],
                "duck_level_db": -20.0 if "DUCK" in shot_dict["music_instructions"] else 0.0
            })

            # 4. Sound Effects Track
            raw_sfx = shot_dict.get("sound_effects_json")
            sfx_list = json.loads(raw_sfx) if raw_sfx else []
            for sfx_name in sfx_list:
                sfx_track.append({
                    "shot_id": shot_dict["id"],
                    "timestamp": s_start,
                    "effect_name": sfx_name
                })

            # 5. Graphics Track
            anim = shot_dict.get("animation_instructions")
            if anim and anim != "NONE":
                graphics_track.append({
                    "shot_id": shot_dict["id"],
                    "start_time": s_start,
                    "end_time": s_end,
                    "type": anim,
                    "description": f"Motion Graphic: {anim}"
                })

            # 6. Titles / Lower-Third Track
            if "PARALLAX" in (anim or "") or "MACRO" in shot_dict["shot_type"]:
                titles_track.append({
                    "shot_id": shot_dict["id"],
                    "start_time": s_start + 0.5,
                    "end_time": s_end - 0.5,
                    "type": "LOWER_THIRD_DOSSIER_BADGE",
                    "anchor_subject": shot_dict["visual_concept"]
                })

            # 7. Transitions Track
            transitions_track.append({
                "shot_id": shot_dict["id"],
                "timestamp": s_start,
                "transition_in": shot_dict["transition_in"],
                "transition_out": shot_dict["transition_out"]
            })

        return JSONResponse({
            "status": "success",
            "project_id": project_id,
            "total_shots": len(rows),
            "total_duration_sec": round(total_dur, 2),
            "tracks": {
                "video": video_track,
                "narration": narration_track,
                "music": music_track,
                "sound_effects": sfx_track,
                "graphics": graphics_track,
                "titles": titles_track,
                "transitions": transitions_track
            }
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
    finally:
        conn.close()

async def update_shot_specification_endpoint(request: Request) -> JSONResponse:
    """
    Updates individual shot directing parameters without regenerating the entire documentary.
    """
    project_id = request.path_params.get("project_id")
    shot_id = request.path_params.get("shot_id")

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON body"}, status_code=400)

    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT id FROM editing_shots WHERE project_id = ? AND id = ?", (project_id, shot_id))
        row = c.fetchone()
        if not row:
            return JSONResponse({"status": "error", "message": f"Shot '{shot_id}' not found"}, status_code=404)

        updates = []
        params = []
        allowed = [
            "approved_asset_ref", "camera_movement", "transition_in", "transition_out",
            "animation_instructions", "narrative_purpose", "is_approved"
        ]
        for field in allowed:
            if field in body:
                val = body[field]
                if field == "is_approved":
                    val = 1 if val else 0
                updates.append(f"{field} = ?")
                params.append(val)

        if updates:
            params.extend([project_id, shot_id])
            query = f"UPDATE editing_shots SET {', '.join(updates)} WHERE project_id = ? AND id = ?"
            with conn:
                conn.execute(query, tuple(params))

        return JSONResponse({
            "status": "success",
            "shot_id": shot_id,
            "message": f"Shot '{shot_id}' specifications updated."
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
    finally:
        conn.close()

async def trigger_project_directing_endpoint(request: Request) -> JSONResponse:
    """
    Triggers the AI Intelligent Editing Director to re-direct the documentary project.
    """
    try:
        data = await request.json()
        project_id = data.get("project_id")
    except Exception:
        project_id = request.path_params.get("project_id")

    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    if IntelligentEditingDirector is None:
        return JSONResponse({"status": "error", "message": "IntelligentEditingDirector module not available in container"}, status_code=503)

    try:
        director = IntelligentEditingDirector(Path("."))
        shots = await asyncio.to_thread(director.direct_and_persist_project_timeline, project_id)
        return JSONResponse({
            "status": "success",
            "project_id": project_id,
            "shots_directed": len(shots),
            "message": f"Successfully directed {len(shots)} shots for '{project_id}'."
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
