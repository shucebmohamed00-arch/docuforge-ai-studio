"""
DocuForge AI - Storyboard Engine
Compiles the complete scene-by-scene storyboard sequence in narration order,
synchronizing spoken text, approved visual assets, camera motions, transitions, and sound cues.
"""
import uuid
import json
import logging
from typing import Dict, Any, List
from ..database import get_connection
from ..core.budget_engine import BudgetEngine
from .creative_director import DocumentaryCreativeDirector
from .footage_discovery import RealFootageDiscoveryAgent

logger = logging.getLogger("docuforge.agents.storyboard")

class StoryboardEngine:
    @classmethod
    def compile_storyboard(cls, project_id: str) -> Dict[str, Any]:
        """
        Synthesizes the complete sequential storyboard for a project from
        its visual manifest beats and approved visual assets.
        Stores items in the storyboard_items table.
        Logs budget usage ($0.02).
        """
        BudgetEngine.record_cost(
            agent_name="STORYBOARD_ENGINE",
            operation="STORYBOARD_TIMELINE_SYNTHESIS",
            model_or_service="TIMELINE_SEQUENCER",
            cost_usd=0.02,
            project_id=project_id,
            tokens_in=1500,
            tokens_out=800,
            notes="Compiled approved assets, narration, camera movements, and SFX cues into chronological storyboard"
        )

        manifest_beats = DocumentaryCreativeDirector.get_manifest(project_id)
        if not manifest_beats:
            DocumentaryCreativeDirector.generate_visual_manifest(project_id)
            manifest_beats = DocumentaryCreativeDirector.get_manifest(project_id)
        if not manifest_beats:
            raise ValueError(f"No visual manifest found for project '{project_id}'.")

        assets = RealFootageDiscoveryAgent.get_project_assets(project_id)
        # Create map from asset_id to asset object
        asset_map = {a["id"]: a for a in assets}

        conn = get_connection()
        try:
            with conn:
                # Clear previous storyboard items
                conn.execute("DELETE FROM storyboard_items WHERE project_id = ?", (project_id,))

                storyboard_items = []
                current_time = 0.0

                for idx, beat in enumerate(manifest_beats, 1):
                    item_id = str(uuid.uuid4())
                    matched_asset_id = beat.get("matched_asset_id")
                    asset_obj = asset_map.get(matched_asset_id) if matched_asset_id else None
                    matched_asset_id = matched_asset_id if asset_obj else None

                    visual_summary = asset_obj["title"] if asset_obj else beat["visual_concept"]
                    asset_type = asset_obj["asset_type"] if asset_obj else beat["target_asset_type"]
                    duration = beat["target_duration_sec"]

                    # Determine BGM mood based on scene beat
                    scene_num = beat["scene_number"]
                    if scene_num in [1, 2]:
                        bgm_mood = "Tense Investigative Sub-Drone (Minor Key)"
                    elif scene_num in [3, 4]:
                        bgm_mood = "Historical Contextual Piano & Low Strings"
                    elif scene_num in [5, 6, 7]:
                        bgm_mood = "Mounting Corporate Tension & Clock Ticks"
                    elif scene_num == 8:
                        bgm_mood = "Climactic Catastrophe Drop & Deep Silence"
                    else:
                        bgm_mood = "Somber Orchestral Strings & Reflective Resolution"

                    narrative_purpose = beat.get("narrative_purpose") or f"Advance scene {scene_num} narrative investigation."
                    emotional_intention = beat.get("emotional_intention") or "Sustained investigative focus and dramatic tension."
                    shot_composition = beat.get("shot_composition") or "Balanced cinematic rule-of-thirds framing with foreground depth."
                    animation_instructions = beat.get("animation_instructions") or "Smooth 60fps keyframe motion with organic atmospheric grain."
                    transition_in = beat.get("transition_in") or "Motivated match cut."
                    transition_out = beat.get("transition_out") or "Clean cut on audio transient."
                    continuity_requirements = beat.get("continuity_requirements") or "Maintain consistent lighting temperature and eye-trace alignment."

                    conn.execute("""
                    INSERT INTO storyboard_items (
                        id, project_id, order_index, scene_number, beat_number,
                        narration_text, asset_id, asset_type, visual_summary,
                        camera_movement, transition, sfx_cue, bgm_mood,
                        duration_sec, narrative_purpose, emotional_intention,
                        shot_composition, animation_instructions, transition_in,
                        transition_out, continuity_requirements, is_approved, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
                    """, (
                        item_id,
                        project_id,
                        idx,
                        beat["scene_number"],
                        beat["beat_number"],
                        beat["narration_segment"],
                        matched_asset_id,
                        asset_type,
                        visual_summary,
                        beat["motion_direction"],
                        transition_in,
                        beat["sound_cue"],
                        bgm_mood,
                        duration,
                        narrative_purpose,
                        emotional_intention,
                        shot_composition,
                        animation_instructions,
                        transition_in,
                        transition_out,
                        continuity_requirements
                    ))

                    storyboard_items.append({
                        "id": item_id,
                        "order_index": idx,
                        "scene_number": beat["scene_number"],
                        "beat_number": beat["beat_number"],
                        "start_timestamp_sec": current_time,
                        "duration_sec": duration,
                        "narration_text": beat["narration_segment"],
                        "asset_id": matched_asset_id,
                        "asset_title": visual_summary,
                        "asset_type": asset_type,
                        "preview_url": asset_obj.get("preview_url") if asset_obj else None,
                        "license_type": asset_obj.get("license_type") if asset_obj else None,
                        "camera_movement": beat["motion_direction"],
                        "transition": transition_in,
                        "transition_in": transition_in,
                        "transition_out": transition_out,
                        "sfx_cue": beat["sound_cue"],
                        "bgm_mood": bgm_mood,
                        "narrative_purpose": narrative_purpose,
                        "emotional_intention": emotional_intention,
                        "shot_composition": shot_composition,
                        "animation_instructions": animation_instructions,
                        "continuity_requirements": continuity_requirements,
                        "is_approved": False
                    })

                    current_time += duration

            logger.info("Compiled %d storyboard items for project %s (Total Timeline: %0.1fs)",
                        len(storyboard_items), project_id, current_time)

            return {
                "project_id": project_id,
                "total_items": len(storyboard_items),
                "total_duration_sec": round(current_time, 1),
                "storyboard": storyboard_items
            }
        finally:
            conn.close()

    @classmethod
    def get_storyboard(cls, project_id: str) -> List[Dict[str, Any]]:
        """Retrieves all storyboard items in chronological narration order with asset previews."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT si.*, va.preview_url, va.license_type, va.authenticity_class
            FROM storyboard_items si
            LEFT JOIN visual_assets va ON si.asset_id = va.id
            WHERE si.project_id = ?
            ORDER BY si.order_index ASC
            """, (project_id,))
            rows = cursor.fetchall()

            items = []
            curr_time = 0.0
            for r in rows:
                d = dict(r)
                d["start_timestamp_sec"] = round(curr_time, 1)
                curr_time += d["duration_sec"]
                items.append(d)
            return items
        finally:
            conn.close()

    @classmethod
    def update_storyboard_item(
        cls,
        item_id: str,
        camera_movement: str,
        transition: str,
        sfx_cue: str,
        bgm_mood: str
    ) -> Dict[str, Any]:
        """Allows operator to adjust transition or audio directives on a specific storyboard cell."""
        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                UPDATE storyboard_items 
                SET camera_movement = ?, transition = ?, sfx_cue = ?, bgm_mood = ?
                WHERE id = ?
                """, (camera_movement, transition, sfx_cue, bgm_mood, item_id))

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM storyboard_items WHERE id = ?", (item_id,))
            return dict(cursor.fetchone())
        finally:
            conn.close()

    @classmethod
    def approve_storyboard(cls, project_id: str) -> Dict[str, Any]:
        """
        Checkpoint #3 Approval:
        Operator reviews and approves the full documentary storyboard sequence.
        Advances project state from 'STORYBOARD_REVIEW' to 'NARRATION_GENERATION'.
        """
        conn = get_connection()
        try:
            with conn:
                conn.execute("UPDATE storyboard_items SET is_approved = 1 WHERE project_id = ?", (project_id,))
                conn.execute("UPDATE projects SET status = 'NARRATION_GENERATION', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (project_id,))

            logger.info("Project %s passed Checkpoint #3 Storyboard Review. Advanced to NARRATION_GENERATION.", project_id)
            return {
                "status": "success",
                "message": "Storyboard sequence approved by operator! Advanced to Stage 8: Narration & Sound Production.",
                "project_id": project_id,
                "new_status": "NARRATION_GENERATION"
            }
        finally:
            conn.close()
