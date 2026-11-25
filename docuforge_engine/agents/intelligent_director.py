"""
DocuForge AI - Intelligent Documentary Editing & Pacing Director
Benchmark: Premium Investigative Video Essays (MagnatesMedia Tier)

Directs and edits documentaries at the individual shot level (3-10s),
dynamically adjusting narrative pacing, camera dynamics, transitions,
music ducking, silence placement, and visual storytelling sequences.
"""

import json
import logging
import uuid
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("docuforge.engine.intelligent_director")

class NarrativeArcMode:
    INVESTIGATIVE_OPENING = "INVESTIGATIVE_OPENING"
    EXPLANATORY_SECTION = "EXPLANATORY_SECTION"
    DRAMATIC_REVELATION = "DRAMATIC_REVELATION"
    HISTORICAL_BACKGROUND = "HISTORICAL_BACKGROUND"
    FINANCIAL_BREAKDOWN = "FINANCIAL_BREAKDOWN"
    EMOTIONAL_CONSEQUENCE = "EMOTIONAL_CONSEQUENCE"
    FINAL_REFLECTION = "FINAL_REFLECTION"

@dataclass
class ShotSpecification:
    """
    Shot-level editing specification containing the 18 documentary directing parameters.
    """
    shot_id: str
    scene_number: int
    shot_index: int
    start_time_sec: float
    end_time_sec: float
    duration_sec: float
    narration_segment: str
    narrative_purpose: str
    emotional_intention: str
    visual_concept: str
    approved_asset_ref: str
    asset_authenticity_class: str  # AUTHENTIC_EVENT_FOOTAGE, ARCHIVAL_FOOTAGE, OFFICIAL_DOCUMENT, ORIGINAL_ANIMATION, MOTION_GRAPHIC
    shot_type: str                 # WIDE_ESTABLISHING, MEDIUM_SUBJECT, CLOSEUP_DETAIL, MACRO_INSPECTION, TOPDOWN_STAGE
    composition: str               # RULE_OF_THIRDS, CENTER_WEIGHTED, GOLDEN_SPIRAL, ASYMMETRICAL_DEPTH
    subject_positioning: str       # CENTER_RIGHT, LOWER_THIRD, FLOATING_PARALLAX, DESK_SURFACE
    camera_movement: str           # SLOW_PUSH_IN, EXPONENTIAL_ZOOM, ORBIT_PARALLAX, HORIZONTAL_PAN, STATIC_HOLD
    animation_instructions: str    # SVG_HIGHLIGHTER, RED_CIRCLE, RUBBER_STAMP_SLAM, DUST_PARTICLES, KINETIC_TEXT, NONE
    transition_in: str             # DISSOLVE, WIPERIGHT, SMOOTHLEFT, MATCH_CUT, HARD_CUT, FADE_WHITE
    transition_out: str            # SMOOTHLEFT, WIPERIGHT, DISSOLVE, HARD_CUT
    music_instructions: str        # TENSION_BUILD, SILENCE_DROP, LOW_DRONE, SUBTLE_PIANO, SWELL
    sound_effects: List[str]       # ["whoosh", "paper_slide", "sub_boom", "typewriter", "camera_shutter"]
    color_treatment: str           # CINEMATIC_WARM_SHADOWS, BLEACH_BYPASS, 35MM_KODACHROME, ARCHIVAL_SEPIA
    continuity_requirements: str
    is_approved: bool = True
    rendered_clip_path: Optional[str] = None

class PacingDirector:
    """
    Analyzes emotional and informational progression to dynamically govern pacing:
    - Cutting frequency (2.5s - 8.0s)
    - Sound design density vs. deliberate silence
    - Camera kinetic velocity
    """
    @staticmethod
    def classify_scene_mode(scene_num: int, total_scenes: int, narration: str) -> str:
        text_lower = narration.lower()
        if scene_num == 1 or "phone call" in text_lower or "mystery" in text_lower or "unthinkable" in text_lower:
            return NarrativeArcMode.INVESTIGATIVE_OPENING
        if "billion" in text_lower or "debt" in text_lower or "balance sheet" in text_lower or "francs" in text_lower:
            return NarrativeArcMode.FINANCIAL_BREAKDOWN
        if "grounded" in text_lower or "crisis" in text_lower or "refused" in text_lower or "collapsed" in text_lower:
            return NarrativeArcMode.DRAMATIC_REVELATION
        if "1992" in text_lower or "history" in text_lower or "decades" in text_lower or "founded" in text_lower:
            return NarrativeArcMode.HISTORICAL_BACKGROUND
        if "passengers stranded" in text_lower or "tears" in text_lower or "workers" in text_lower or "protest" in text_lower:
            return NarrativeArcMode.EMOTIONAL_CONSEQUENCE
        if scene_num >= total_scenes - 1:
            return NarrativeArcMode.FINAL_REFLECTION
        return NarrativeArcMode.EXPLANATORY_SECTION

    @staticmethod
    def get_pacing_parameters(mode: str) -> Dict[str, Any]:
        """
        Returns rhythmic directing parameters tailored to the narrative arc mode.
        """
        pacing_table = {
            NarrativeArcMode.INVESTIGATIVE_OPENING: {
                "target_shot_duration": (3.0, 4.5),
                "camera_velocity": "DYNAMIC_PUSH",
                "music_intensity": "SUSPENSE_RISING",
                "allow_silence": False,
                "preferred_transitions": ["dissolve", "smoothleft"],
                "sfx_frequency": "HIGH",
            },
            NarrativeArcMode.DRAMATIC_REVELATION: {
                "target_shot_duration": (2.5, 3.8),
                "camera_velocity": "RAPID_PUNCH",
                "music_intensity": "SUDDEN_SILENCE_DROP",
                "allow_silence": True,  # Silence is more powerful than music at the reveal
                "preferred_transitions": ["hard_cut", "fadewhite"],
                "sfx_frequency": "MAXIMAL",
            },
            NarrativeArcMode.FINANCIAL_BREAKDOWN: {
                "target_shot_duration": (4.0, 6.0),  # Give audience time to read numbers
                "camera_velocity": "SLOW_INSPECT",
                "music_intensity": "LOW_TENSION_DRONE",
                "allow_silence": False,
                "preferred_transitions": ["wiperight", "smoothleft"],
                "sfx_frequency": "MEDIUM",
            },
            NarrativeArcMode.HISTORICAL_BACKGROUND: {
                "target_shot_duration": (4.5, 7.0),
                "camera_velocity": "GENTLE_DRIFT",
                "music_intensity": "ORCHESTRAL_RETROSPECTIVE",
                "allow_silence": False,
                "preferred_transitions": ["dissolve", "smoothright"],
                "sfx_frequency": "SUBTLE",
            },
            NarrativeArcMode.EMOTIONAL_CONSEQUENCE: {
                "target_shot_duration": (5.0, 8.5),  # Hold on human emotion
                "camera_velocity": "SLOW_PAN",
                "music_intensity": "SUBTLE_PIANO",
                "allow_silence": True,
                "preferred_transitions": ["dissolve", "fadeblack"],
                "sfx_frequency": "MINIMAL",
            },
            NarrativeArcMode.FINAL_REFLECTION: {
                "target_shot_duration": (5.0, 9.0),
                "camera_velocity": "SLOW_PULL_OUT",
                "music_intensity": "RESOLVING_THEME",
                "allow_silence": False,
                "preferred_transitions": ["dissolve"],
                "sfx_frequency": "LOW",
            },
            NarrativeArcMode.EXPLANATORY_SECTION: {
                "target_shot_duration": (3.5, 5.5),
                "camera_velocity": "CONTROLLED_TRACK",
                "music_intensity": "STEADY_UNDERSCORE",
                "allow_silence": False,
                "preferred_transitions": ["smoothleft", "wiperight"],
                "sfx_frequency": "MEDIUM",
            },
        }
        return pacing_table.get(mode, pacing_table[NarrativeArcMode.EXPLANATORY_SECTION])

class IntelligentEditingDirector:
    """
    Master Documentary Post-Production Directing Engine.
    Converts scripts and approved asset pools into shot-by-shot directing sequences.
    """
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.pacing_director = PacingDirector()

    def direct_scene(
        self,
        scene_number: int,
        total_scenes: int,
        narration: str,
        total_duration: float,
        available_assets: List[Path],
        start_timestamp: float = 0.0
    ) -> List[ShotSpecification]:
        """
        Directs a single scene into multiple narrative-serving shots (3-8 seconds each).
        Translates narration into a meaningful visual progression:
        (e.g., Establishing -> Evidence Dossier -> Kinetic Graphic -> Archival Consequence).
        """
        mode = self.pacing_director.classify_scene_mode(scene_number, total_scenes, narration)
        pacing = self.pacing_director.get_pacing_parameters(mode)
        min_d, max_d = pacing["target_shot_duration"]

        # Calculate optimal number of shots for scene duration
        raw_shots = max(2, int(round(total_duration / 4.2)))
        shot_duration = round(total_duration / raw_shots, 2)
        
        # Enforce realistic bounds
        if shot_duration < min_d and raw_shots > 2:
            raw_shots -= 1
            shot_duration = round(total_duration / raw_shots, 2)

        shots = []
        curr_time = start_timestamp

        # Split narration into meaningful sub-clauses
        words = narration.split()
        words_per_shot = max(3, len(words) // raw_shots)

        for s_idx in range(raw_shots):
            shot_id = f"SC{scene_number:02d}_SH{s_idx + 1:02d}"
            seg_start = s_idx * words_per_shot
            seg_end = (s_idx + 1) * words_per_shot if s_idx < raw_shots - 1 else len(words)
            shot_narration = " ".join(words[seg_start:seg_end])

            # Select asset with contextual visual storytelling logic
            asset_ref = available_assets[s_idx % len(available_assets)] if available_assets else Path("data/media/fallback.mp4")
            asset_str = str(asset_ref).lower()

            # Determine authenticity class & animation instructions
            if "remotion" in asset_str or "inspector" in asset_str:
                auth_class = "OFFICIAL_DOCUMENT"
                anim_instr = "SVG_HIGHLIGHTER_RED_CIRCLE_STAMP"
                shot_type = "MACRO_INSPECTION"
                composition = "GOLDEN_SPIRAL"
                sfx = ["paper_slide", "sub_boom"]
            elif "stage_" in asset_str:
                auth_class = "OFFICIAL_DOCUMENT"
                anim_instr = "3D_DESK_PHYSICAL_DROP_SHADOW"
                shot_type = "TOPDOWN_STAGE"
                composition = "CENTER_WEIGHTED"
                sfx = ["paper_slide", "typewriter"]
            elif "parallax" in asset_str:
                auth_class = "AUTHENTIC_PHOTO"
                anim_instr = "2.5D_MULTI_PLANE_PARALLAX_DUST"
                shot_type = "MEDIUM_SUBJECT"
                composition = "RULE_OF_THIRDS"
                sfx = ["whoosh", "camera_shutter"]
            elif "graphic" in asset_str or "chart" in asset_str:
                auth_class = "MOTION_GRAPHIC"
                anim_instr = "ANIMATED_VECTOR_CHART"
                shot_type = "CLOSEUP_DETAIL"
                composition = "ASYMMETRICAL_DEPTH"
                sfx = ["whoosh", "typewriter"]
            elif "uncut" in asset_str or "politics" in asset_str or "soundbite" in asset_str:
                auth_class = "AUTHENTIC_EVENT_FOOTAGE"
                anim_instr = "NONE"
                shot_type = "WIDE_ESTABLISHING"
                composition = "RULE_OF_THIRDS"
                sfx = ["camera_shutter"]
            else:
                auth_class = "LICENSED_STOCK"
                anim_instr = "SUBTLE_35MM_GRAIN"
                shot_type = "MEDIUM_SUBJECT"
                composition = "RULE_OF_THIRDS"
                sfx = ["whoosh"]

            # Visual Storytelling Narrative Purpose
            if s_idx == 0:
                purpose = f"Establish {mode} spatial anchor and dramatic premise."
                camera_mvmt = "SLOW_PUSH_IN"
                trans_in = "DISSOLVE"
                trans_out = "SMOOTHLEFT"
            elif s_idx == 1:
                purpose = "Introduce concrete primary evidence / financial filing to validate narrative claim."
                camera_mvmt = "ORBIT_PARALLAX" if "parallax" in asset_str else "SLOW_PUSH_IN"
                trans_in = "WIPERIGHT"
                trans_out = "SMOOTHLEFT"
            else:
                purpose = "Reveal the acute systemic consequence / human impact of preceding claim."
                camera_mvmt = "HORIZONTAL_PAN"
                trans_in = "SMOOTHLEFT"
                trans_out = "DISSOLVE"

            # Music instructions & Silence Placement
            if mode == NarrativeArcMode.DRAMATIC_REVELATION and s_idx == raw_shots - 1:
                music_inst = "SILENCE_DROP_BEFORE_REVELATION"
            elif "soundbite" in asset_str:
                music_inst = "NARRATOR_PAUSE_AUDIO_DUCK_MINUS_20DB"
            else:
                music_inst = "STEADY_TENSION_UNDERSCORE"

            shot = ShotSpecification(
                shot_id=shot_id,
                scene_number=scene_number,
                shot_index=s_idx + 1,
                start_time_sec=round(curr_time, 2),
                end_time_sec=round(curr_time + shot_duration, 2),
                duration_sec=round(shot_duration, 2),
                narration_segment=shot_narration,
                narrative_purpose=purpose,
                emotional_intention=f"Evoke {mode.replace('_', ' ').lower()} engagement without emotional exhaustion.",
                visual_concept=f"Visual anchor: {asset_ref.stem}",
                approved_asset_ref=str(asset_ref),
                asset_authenticity_class=auth_class,
                shot_type=shot_type,
                composition=composition,
                subject_positioning="CENTER_RIGHT",
                camera_movement=camera_mvmt,
                animation_instructions=anim_instr,
                transition_in=trans_in,
                transition_out=trans_out,
                music_instructions=music_inst,
                sound_effects=sfx,
                color_treatment="CINEMATIC_WARM_SHADOWS",
                continuity_requirements=f"Maintain lighting and scale continuity into shot #{s_idx + 2}" if s_idx < raw_shots - 1 else "Prepare transition to next scene block"
            )
            shots.append(shot)
            curr_time += shot_duration

        return shots

    def direct_and_persist_project_timeline(self, project_id: str, script_json_path: Optional[Path] = None) -> List[ShotSpecification]:
        """
        Directs an entire documentary project into shot-by-shot specifications
        and commits them to the SQLite database `editing_shots` table.
        """
        import sqlite3
        from backend.app.database import get_connection

        beats = []
        if script_json_path and script_json_path.exists():
            with open(script_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            beats = data.get("beats", [])

        if not beats:
            # Query directly from database storyboard_items
            conn = get_connection()
            try:
                c = conn.cursor()
                c.execute("""
                    SELECT order_index, scene_number, beat_number, narration_text, duration_sec
                    FROM storyboard_items
                    WHERE project_id = ?
                    ORDER BY order_index ASC
                """, (project_id,))
                rows = c.fetchall()
                for r in rows:
                    beats.append({
                        "order_index": r["order_index"],
                        "scene_number": r["scene_number"],
                        "narration": r["narration_text"],
                        "duration": r["duration_sec"]
                    })
            finally:
                conn.close()

        if not beats:
            logger.warning(f"No storyboard items or script beats found for project '{project_id}'.")
            return []

        all_shots: List[ShotSpecification] = []
        curr_time = 13.5  # After Cold Open

        # Asset pools
        clips_dir = self.workspace_dir / "data" / "media" / "authentic_clips"
        remotion_dir = self.workspace_dir / "data" / "media" / "remotion_renders"
        stage_dir = self.workspace_dir / "data" / "media" / "magnates_stage"
        fin_dir = self.workspace_dir / "data" / "media" / "financial_graphics"

        total_beats = len(beats)
        for idx, beat in enumerate(beats):
            scene_num = idx + 1
            narration = beat.get("narration", "")
            dur = float(beat.get("duration", 6.5))

            # Contextual asset mapping for high-narrative beats
            contextual = []
            if scene_num == 7:
                contextual = [stage_dir / "stage_03_ubs_dossier.mp4", clips_dir / "politics_ubs_06_bank_vault_doors.mp4"]
            elif scene_num == 18:
                contextual = [remotion_dir / "parallax_bruggisser.mp4", clips_dir / "zurich_uncut_04_cockpit_view.mp4"]
            elif scene_num == 25:
                contextual = [remotion_dir / "kinetic_document_inspector.mp4", clips_dir / "politics_ubs_18_banker_handshake.mp4"]
            elif scene_num == 33:
                contextual = [remotion_dir / "parallax_mario_corti.mp4", clips_dir / "politics_ubs_09_mario_corti_mic.mp4"]
            elif scene_num == 36:
                contextual = [stage_dir / "stage_01_mario_corti.mp4", clips_dir / "politics_ubs_09_mario_corti_mic.mp4"]
            elif scene_num % 4 == 0:
                contextual = [fin_dir / "graphic_02_debt_spiral.mp4", clips_dir / "politics_ubs_10_stock_chart_screen.mp4"]
            else:
                # Authentic archival default
                cand1 = clips_dir / f"zurich_uncut_{(scene_num % 30) + 1:02d}_md11_wingtip.mp4"
                cand2 = clips_dir / f"politics_ubs_{(scene_num % 20) + 1:02d}_financial_district_zurich.mp4"
                contextual = [c for c in [cand1, cand2] if c.exists()]
                if not contextual:
                    contextual = list(clips_dir.glob("*.mp4"))[:2]

            scene_shots = self.direct_scene(
                scene_number=scene_num,
                total_scenes=total_beats,
                narration=narration,
                total_duration=dur,
                available_assets=contextual,
                start_timestamp=curr_time
            )
            all_shots.extend(scene_shots)
            curr_time += dur

        # Persist to database
        conn = get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM editing_shots WHERE project_id = ?", (project_id,))
                for s in all_shots:
                    conn.execute("""
                    INSERT INTO editing_shots (
                        id, project_id, scene_number, shot_index, start_time_sec, end_time_sec,
                        duration_sec, narration_segment, narrative_purpose, emotional_intention,
                        visual_concept, approved_asset_ref, asset_authenticity_class, shot_type,
                        composition, subject_positioning, camera_movement, animation_instructions,
                        transition_in, transition_out, music_instructions, sound_effects_json,
                        color_treatment, continuity_requirements, is_approved
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        s.shot_id, project_id, s.scene_number, s.shot_index, s.start_time_sec, s.end_time_sec,
                        s.duration_sec, s.narration_segment, s.narrative_purpose, s.emotional_intention,
                        s.visual_concept, s.approved_asset_ref, s.asset_authenticity_class, s.shot_type,
                        s.composition, s.subject_positioning, s.camera_movement, s.animation_instructions,
                        s.transition_in, s.transition_out, s.music_instructions, json.dumps(s.sound_effects),
                        s.color_treatment, s.continuity_requirements, 1 if s.is_approved else 0
                    ))
        finally:
            conn.close()

        logger.info(f"Successfully directed and persisted {len(all_shots)} shot specifications for project '{project_id}'.")
        return all_shots

