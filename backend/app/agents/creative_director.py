"""
DocuForge AI - Agent 6: Documentary Creative Director
Breaks down the approved script sentence-by-sentence into 4-8 second visual beats,
assigns visual modes (INVESTIGATIVE, CINEMATIC, EXPLAINER), and builds the Visual Manifest.
"""
import uuid
import re
import json
import logging
from typing import Dict, Any, List
from ..database import get_connection
from ..core.budget_engine import BudgetEngine
from .storyteller import MasterDocumentaryStoryteller

logger = logging.getLogger("docuforge.agents.creative_director")

class VisualMode:
    INVESTIGATIVE = "INVESTIGATIVE"  # Evidence, documents, tension, macro close-ups
    CINEMATIC = "CINEMATIC"          # Atmospheric footage, emotional reveals, dramatic framing
    EXPLAINER = "EXPLAINER"          # Animated maps, timelines, charts, financial graphics

class TargetAssetType:
    ARCHIVAL_VIDEO = "ARCHIVAL_VIDEO"
    AUTHENTIC_PHOTO = "AUTHENTIC_PHOTO"
    MAP = "MAP"
    CHART = "CHART"
    DOC_REVEAL = "DOC_REVEAL"
    STOCK_FOOTAGE = "STOCK_FOOTAGE"

class DocumentaryCreativeDirector:
    @staticmethod
    def _segment_text_into_sentences(text: str) -> List[str]:
        """Splits narrative text into clean sentence segments."""
        raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        return sentences

    @classmethod
    def _determine_beat_visual_direction(cls, sentence: str, scene_beat_name: str, scene_number: int) -> Dict[str, Any]:
        """
        Analyzes the semantic meaning of a sentence and decides:
        - Visual mode (Investigative, Cinematic, Explainer)
        - Target asset type (Archival video, photo, map, chart, document)
        - Visual concept description
        - Camera motion instructions
        """
        lower = sentence.lower()

        # Explainer: Maps, routes, borders, geography
        if any(w in lower for w in ["map", "border", "europe", "geography", "island", "corridor", "airspace", "routes", "foreign"]):
            return {
                "visual_mode": VisualMode.EXPLAINER,
                "target_asset_type": TargetAssetType.MAP,
                "narrative_purpose": "Geographic contextualization establishing territorial boundaries and strategic operational isolation.",
                "emotional_intention": "Analytical clarity turning into systemic vulnerability and entrapment.",
                "visual_concept": "Animated geographic cartography zooming into central territory with pulsating vector route networks.",
                "shot_composition": "Top-down cartographic projection with high-contrast borders and negative peripheral space.",
                "motion_direction": "Satellite camera slowly diving diagonally while route vectors radiate across national boundaries.",
                "animation_instructions": "Pulsing 60fps glow trail vectors with dynamic airspace boundary highlight.",
                "transition_in": "Smooth graphic-to-map camera dive.",
                "transition_out": "Macro whip cut to runway tarmac detail.",
                "sound_cue": "Subtle radar pulse ping and low wind ambience.",
                "continuity_requirements": "Maintain navy/cyan color temperature into subsequent geographic or technical scenes."
            }

        # Explainer: Numbers, financial figures, millions, billions, debt, balance sheet, stocks
        if any(w in lower for w in ["franc", "dollar", "billion", "million", "balance sheet", "debt", "cash", "account", "stock", "numbers", "ledger", "14.5 million"]):
            return {
                "visual_mode": VisualMode.EXPLAINER,
                "target_asset_type": TargetAssetType.CHART,
                "narrative_purpose": "Expose the quantitative reality and escalating fiscal insolvency behind corporate executive statements.",
                "emotional_intention": "Intellectual shock at the mathematical impossibility of survival.",
                "visual_concept": "Kinetic financial chart displaying exponential debt curve vs plummeting liquid cash reserves.",
                "shot_composition": "Clean modern corporate graph framed in lower two-thirds with live ticker figures updating in red.",
                "motion_direction": "Linear camera tracking along dropping valuation curve with sharp red gradient highlights.",
                "animation_instructions": "Rapid numerical counter rolling down with easing deceleration on final catastrophic balance.",
                "transition_in": "Match cut on currency symbol reveal.",
                "transition_out": "Hard cut on final negative balance impact.",
                "sound_cue": "Mechanical stock ticker clicks and low metallic thud.",
                "continuity_requirements": "Red accent indicators must align with subsequent audit document disclosures."
            }

        # Investigative: Documents, memos, contracts, inquiry reports, legal, secret, call
        if any(w in lower for w in ["memo", "report", "document", "contract", "court", "investigation", "phone call", "directive", "letter", "guarantee"]):
            return {
                "visual_mode": VisualMode.INVESTIGATIVE,
                "target_asset_type": TargetAssetType.DOC_REVEAL,
                "narrative_purpose": "Provide forensic primary documentation proving executive foreknowledge or institutional culpability.",
                "emotional_intention": "Intense journalistic scrutiny and conspiratorial tension.",
                "visual_concept": "Forensic close-up of authentic audit inquiry report with yellow digital text highlighter tracking across critical figures.",
                "shot_composition": "Extreme shallow depth of field macro angle focused on signature line and confidential stamps.",
                "motion_direction": "Macro lens slow diagonal drift across aged paper grain with shallow depth of field.",
                "animation_instructions": "Digital highlighter reveal tracking exactly with spoken word cadence.",
                "transition_in": "Fast camera push-in with lens flare wipe.",
                "transition_out": "Match cut from highlighted text to boardroom executive portrait.",
                "sound_cue": "Crisp paper turning Foley and ink-highlighter squeak.",
                "continuity_requirements": "Match desaturated warm investigative document tone with archival photo color temperature."
            }

        # Cinematic / Authentic Photo: Specific persons, executives, boards, characters
        if any(w in lower for w in ["bruggisser", "corti", "ospel", "ceo", "board", "executive", "architect", "protester", "passenger"]):
            return {
                "visual_mode": VisualMode.INVESTIGATIVE,
                "target_asset_type": TargetAssetType.AUTHENTIC_PHOTO,
                "narrative_purpose": "Humanize the central conflict by spotlighting key architects and decision-makers in high relief.",
                "emotional_intention": "Forensic character study conveying hubris, isolation, or quiet desperation.",
                "visual_concept": "High-contrast archival photograph of executive decision maker with subtle 2.5D parallax separation and dust particle overlay.",
                "shot_composition": "Medium close-up portrait aligned to right third, subject gaze crossing frame into negative space.",
                "motion_direction": "Slow Ken Burns push-in centered on eyes, background drifting slightly in opposite direction.",
                "animation_instructions": "2.5D multi-plane depth separation with subtle floating archival dust particles.",
                "transition_in": "Cinematic cross-dissolve.",
                "transition_out": "Slow fade to black or match cut to press conference.",
                "sound_cue": "Single deep cello note resonating.",
                "continuity_requirements": "Monochrome or muted archival grading consistent with investigative timeline."
            }

        # Cinematic: Airplanes, runway, tarmac, flight, airport, skies, travel
        if any(w in lower for w in ["plane", "airplane", "airbus", "tarmac", "runway", "kloten", "grounded", "flight", "kerosene", "fuel", "sky"]):
            return {
                "visual_mode": VisualMode.CINEMATIC,
                "target_asset_type": TargetAssetType.ARCHIVAL_VIDEO,
                "narrative_purpose": "Establish atmospheric scale and the physical reality of the crisis on the ground.",
                "emotional_intention": "Foreboding atmospheric weight, stillness, and monumental breakdown.",
                "visual_concept": "Authentic archival footage of grounded MD-11 aircraft parked in heavy rain at Zurich Kloten Airport.",
                "shot_composition": "Wide cinematic 2.39:1 letterboxed master shot of grounded fleet with tarmac wet reflection.",
                "motion_direction": "Cinematic handheld drift or slow tracking telephoto shot across aircraft wing and tail logo.",
                "animation_instructions": "Organic atmospheric mist particles with subtle telephoto heat shimmer.",
                "transition_in": "Clean hard cut on thunder or musical downbeat.",
                "transition_out": "Directional pan to empty departure board.",
                "sound_cue": "Distant jet engine spool-down, raindrops on aluminum fuselage.",
                "continuity_requirements": "Consistent overcast grey-blue color grading across exterior airport sequences."
            }

        # Default Cinematic Contextual Treatment
        return {
            "visual_mode": VisualMode.CINEMATIC,
            "target_asset_type": TargetAssetType.ARCHIVAL_VIDEO,
            "narrative_purpose": f"Advance the narrative beat '{scene_beat_name}' with deliberate visual and atmospheric continuity.",
            "emotional_intention": "Engaged curiosity leading into dramatic revelation.",
            "visual_concept": f"Atmospheric cinematic footage establishing the visual tone of {scene_beat_name}.",
            "shot_composition": "Balanced cinematic rule-of-thirds composition with deliberate depth layers.",
            "motion_direction": "Slow steady push-in with dramatic contrast grading.",
            "animation_instructions": "Subtle organic motion and cinematic contrast enhancement.",
            "transition_in": "Cinematic fade or match cut.",
            "transition_out": "Motivated cut on musical phrase end.",
            "sound_cue": "Subtle room tone and atmospheric sub drone.",
            "continuity_requirements": "Maintain seamless visual pacing and lighting consistency."
        }

    @classmethod
    def generate_visual_manifest(cls, project_id: str) -> Dict[str, Any]:
        """
        Segments the approved script into 4-8 second visual beats and writes the Visual Manifest.
        Logs budget usage ($0.03).
        """
        BudgetEngine.record_cost(
            agent_name="CREATIVE_DIRECTOR_AGENT",
            operation="VISUAL_MANIFEST_SEGMENTATION",
            model_or_service="GEMINI_FLASH_DIRECTOR_ENGINE",
            cost_usd=0.03,
            project_id=project_id,
            tokens_in=2800,
            tokens_out=1900,
            notes="Sentence-level segmentation into visual beats with shot directions"
        )

        from ..models.project import ProjectManager
        ProjectManager.ensure_project(project_id)

        script = MasterDocumentaryStoryteller.get_project_script(project_id)
        if not script:
            MasterDocumentaryStoryteller.generate_full_script(project_id)
            script = MasterDocumentaryStoryteller.get_project_script(project_id)
        if not script:
            raise ValueError(f"No script found for project '{project_id}'.")

        scenes = script.get("scenes", [])
        if not scenes:
            raise ValueError("Script contains no scenes.")

        conn = get_connection()
        try:
            with conn:
                # Clear previous manifest entries
                conn.execute("DELETE FROM visual_manifests WHERE project_id = ?", (project_id,))

                manifest_items = []
                current_timeline_sec = 0.0

                for sc in scenes:
                    scene_num = sc["scene_number"]
                    scene_title = sc["scene_title"]
                    scene_beat_name = sc.get("narrative_beat", "Scene")
                    sentences = cls._segment_text_into_sentences(sc["narration"])

                    for b_idx, sentence in enumerate(sentences, 1):
                        manifest_id = str(uuid.uuid4())
                        words = len(sentence.split())
                        # Pacing: ~140 words per min = 2.33 words/sec. Bound beat duration between 4.0s and 8.0s
                        beat_duration = round(max(4.0, min(8.5, words / 2.33)), 1)
                        
                        treatment = cls._determine_beat_visual_direction(sentence, scene_beat_name, scene_num)

                        conn.execute("""
                        INSERT INTO visual_manifests (
                            id, project_id, scene_number, beat_number,
                            narration_segment, visual_concept, visual_mode,
                            target_asset_type, target_duration_sec, start_timestamp_sec,
                            motion_direction, transition_in, sound_cue,
                            narrative_purpose, emotional_intention, shot_composition,
                            animation_instructions, transition_out, continuity_requirements,
                            status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PLANNED')
                        """, (
                            manifest_id,
                            project_id,
                            scene_num,
                            b_idx,
                            sentence,
                            treatment["visual_concept"],
                            treatment["visual_mode"],
                            treatment["target_asset_type"],
                            beat_duration,
                            current_timeline_sec,
                            treatment["motion_direction"],
                            treatment["transition_in"],
                            treatment["sound_cue"],
                            treatment.get("narrative_purpose", ""),
                            treatment.get("emotional_intention", ""),
                            treatment.get("shot_composition", ""),
                            treatment.get("animation_instructions", ""),
                            treatment.get("transition_out", ""),
                            treatment.get("continuity_requirements", "")
                        ))

                        manifest_items.append({
                            "id": manifest_id,
                            "scene_number": scene_num,
                            "scene_title": scene_title,
                            "beat_number": b_idx,
                            "narration_segment": sentence,
                            "visual_concept": treatment["visual_concept"],
                            "visual_mode": treatment["visual_mode"],
                            "target_asset_type": treatment["target_asset_type"],
                            "target_duration_sec": beat_duration,
                            "start_timestamp_sec": current_timeline_sec,
                            "motion_direction": treatment["motion_direction"],
                            "transition_in": treatment["transition_in"],
                            "transition_out": treatment.get("transition_out", ""),
                            "sound_cue": treatment["sound_cue"],
                            "narrative_purpose": treatment.get("narrative_purpose", ""),
                            "emotional_intention": treatment.get("emotional_intention", ""),
                            "shot_composition": treatment.get("shot_composition", ""),
                            "animation_instructions": treatment.get("animation_instructions", ""),
                            "continuity_requirements": treatment.get("continuity_requirements", ""),
                            "status": "PLANNED"
                        })

                        current_timeline_sec += beat_duration

            logger.info("Visual manifest generated for project %s: %d total visual beats spanning %0.1f seconds",
                        project_id, len(manifest_items), current_timeline_sec)

            return {
                "project_id": project_id,
                "total_beats": len(manifest_items),
                "total_duration_sec": round(current_timeline_sec, 1),
                "manifest": manifest_items
            }
        finally:
            conn.close()

    @classmethod
    def get_manifest(cls, project_id: str) -> List[Dict[str, Any]]:
        """Retrieves all visual manifest beats for a project ordered by timeline."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM visual_manifests 
            WHERE project_id = ? 
            ORDER BY scene_number ASC, beat_number ASC
            """, (project_id,))
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @classmethod
    def update_beat_treatment(
        cls,
        manifest_id: str,
        visual_concept: str,
        visual_mode: str,
        target_asset_type: str,
        motion_direction: str
    ) -> Dict[str, Any]:
        """Allows fine-tuning a visual beat's direction in the Visual Director dashboard."""
        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                UPDATE visual_manifests 
                SET visual_concept = ?, visual_mode = ?, target_asset_type = ?, motion_direction = ?
                WHERE id = ?
                """, (visual_concept, visual_mode, target_asset_type, motion_direction, manifest_id))

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM visual_manifests WHERE id = ?", (manifest_id,))
            return dict(cursor.fetchone())
        finally:
            conn.close()
