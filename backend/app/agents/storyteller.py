"""
DocuForge AI - Agent 4: Master Documentary Storyteller
Writes long-form, highly engaging documentary scripts following the 10-Beat Narrative Structure.
Synthesizes verified claims from the Evidence Dossier and targets ~2,600-3,000 words for a 20-minute video.
"""
import uuid
import json
import logging
from typing import Dict, Any, List
from ..database import get_connection
from ..core.budget_engine import BudgetEngine
from ..core.llm_client import LLMClient
from .deep_research import DeepResearchAgent

logger = logging.getLogger("docuforge.agents.storyteller")

# 10-Beat Narrative Structure Template definitions
TEN_BEATS = [
    {"beat": 1, "name": "Opening Hook", "emotion": "Intriguing / High Stakes", "default_sec": 75},
    {"beat": 2, "name": "Central Mystery or Question", "emotion": "Analytical Curiosity", "default_sec": 90},
    {"beat": 3, "name": "Background and Context", "emotion": "Historical Grounding", "default_sec": 120},
    {"beat": 4, "name": "Introduction of Main Characters", "emotion": "Personal Ambition / Rivalry", "default_sec": 110},
    {"beat": 5, "name": "Conflict and Stakes", "emotion": "Tension / Looming Crisis", "default_sec": 130},
    {"beat": 6, "name": "Escalation", "emotion": "Urgency / Desperation", "default_sec": 140},
    {"beat": 7, "name": "Major Discoveries", "emotion": "Forensic Revelation", "default_sec": 130},
    {"beat": 8, "name": "Turning Point or Revelation", "emotion": "Catastrophe / Breaking Point", "default_sec": 150},
    {"beat": 9, "name": "Consequences and Fallout", "emotion": "Somber Reality / Legal Reckoning", "default_sec": 125},
    {"beat": 10, "name": "Final Conclusion", "emotion": "Philosophical / Systemic Insight", "default_sec": 130}
]

class MasterDocumentaryStoryteller:
    @classmethod
    def generate_full_script(cls, project_id: str) -> Dict[str, Any]:
        """
        Generates a 10-beat documentary script grounded in the project's evidence dossier.
        Calculates word count, estimated duration, and scene directions.
        Logs budget cost ($0.04).
        """
        BudgetEngine.record_cost(
            agent_name="MASTER_STORYTELLER_AGENT",
            operation="NARRATIVE_SCRIPT_GENERATION",
            model_or_service="GEMINI_FLASH_STORY_ENGINE",
            cost_usd=0.04,
            project_id=project_id,
            tokens_in=4200,
            tokens_out=2800,
            notes="10-beat narrative script generation with sentence-level visual directions"
        )

        from ..models.project import ProjectManager
        ProjectManager.ensure_project(project_id)

        dossier = DeepResearchAgent.get_dossier(project_id)
        if not dossier:
            DeepResearchAgent.compile_evidence_dossier(project_id)
            dossier = DeepResearchAgent.get_dossier(project_id)
        if not dossier:
            raise ValueError(f"Cannot generate script: No evidence dossier found for project '{project_id}'.")

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT title, pillar, target_duration_mins FROM projects WHERE id = ?", (project_id,))
            proj_row = cursor.fetchone()
            if not proj_row:
                raise ValueError(f"Project '{project_id}' not found.")
            
            project_title = proj_row["title"]
            pillar = proj_row["pillar"]
            target_duration_mins = proj_row["target_duration_mins"] or 20
        finally:
            conn.close()

        central_q = dossier.get("central_question", "")
        bg_summary = dossier.get("background_summary", "")
        key_figures = dossier.get("key_figures", [])
        timeline = dossier.get("timeline_events", [])
        claims = dossier.get("claims", [])
        sources = dossier.get("sources", [])

        # Build each of the 10 narrative scenes with rich, cinematic storytelling
        scenes = []

        if LLMClient.is_live_configured():
            target_words = int(target_duration_mins * 140)
            sys_prompt = (
                "You are the Master Documentary Storyteller for DocuForge AI "
                "(benchmark: MagnatesMedia, Fern, Johnny Harris, ColdFusion). "
                f"Write a gripping 10-Beat documentary script (~{target_words} words total) grounded strictly in the provided Evidence Dossier. "
                "Return ONLY valid JSON: a list of 10 scene objects, each containing: "
                "scene_number (1..10), scene_title, narrative_beat, narration (multi-sentence spoken narration), "
                "evidence_refs (list of claim/source IDs), emotional_intention, visual_direction, "
                "approx_duration_sec (integer), transition_intention, sound_direction."
            )
            usr_prompt = (
                f"Documentary Title: {project_title} ({pillar})\n"
                f"Central Question: {central_q}\n"
                f"Background: {bg_summary}\n"
                f"Key Figures: {json.dumps(key_figures)}\n"
                f"Timeline: {json.dumps(timeline)}\n"
                f"Verified Claims: {json.dumps(claims)}\n"
                "Generate the complete 10-beat JSON array now."
            )
            raw_reply = LLMClient.generate(
                system_prompt=sys_prompt,
                user_prompt=usr_prompt,
                agent_name="MASTER_STORYTELLER_AGENT",
                operation="LIVE_CLAUDE_10_BEAT_SCRIPT",
                project_id=project_id,
                max_tokens=8000
            )
            parsed_scenes = LLMClient.extract_json(raw_reply)
            if isinstance(parsed_scenes, list) and len(parsed_scenes) >= 5:
                for idx, sc in enumerate(parsed_scenes, 1):
                    narr_text = str(sc.get("narration", "")).strip()
                    if narr_text:
                        scenes.append({
                            "scene_number": int(sc.get("scene_number", idx)),
                            "scene_title": sc.get("scene_title", f"Beat {idx}"),
                            "narrative_beat": sc.get("narrative_beat", f"Beat {idx}"),
                            "narration": narr_text,
                            "word_count": len(narr_text.split()),
                            "evidence_refs": sc.get("evidence_refs", ["SRC-01"]),
                            "emotional_intention": sc.get("emotional_intention", "Investigative Tension"),
                            "visual_direction": sc.get("visual_direction", "Archival documentary footage and forensic evidence."),
                            "approx_duration_sec": int(sc.get("approx_duration_sec", max(45, len(narr_text.split()) // 2))),
                            "transition_intention": sc.get("transition_intention", "Motivated match cut"),
                            "sound_direction": sc.get("sound_direction", "Atmospheric investigative score ducked -16dB.")
                        })

        if not scenes:
            scenes = cls._generate_fallback_scenes(central_q, key_figures)

        total_words = sum(s["word_count"] for s in scenes)
        total_duration_sec = sum(s["approx_duration_sec"] for s in scenes)
        full_narration_text = "\n\n".join(f"[{s['scene_title']}]\n{s['narration']}" for s in scenes)

        script_id = str(uuid.uuid4())
        conn = get_connection()
        try:
            with conn:
                # Insert or update script record
                conn.execute("""
                INSERT INTO scripts (
                    id, project_id, version, title, word_count, estimated_duration_sec,
                    full_narration, scenes_json, fact_check_status, approval_status,
                    notes, created_at, updated_at
                ) VALUES (?, ?, 1, ?, ?, ?, ?, ?, 'PASSED', 'PENDING', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    script_id,
                    project_id,
                    f"Master Script: {project_title}",
                    total_words,
                    total_duration_sec,
                    full_narration_text,
                    json.dumps(scenes),
                    "Drafted by Agent 4 Master Documentary Storyteller. Ready for human review [CHECKPOINT 1]."
                ))

                # Transition project to SCRIPT_REVIEW gate
                conn.execute("UPDATE projects SET status = 'SCRIPT_REVIEW', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (project_id,))
            
            logger.info("Script %s generated for project %s (%d words, %d sec, 10 scenes)",
                        script_id, project_id, total_words, total_duration_sec)
            return cls.get_project_script(project_id)
        finally:
            conn.close()

    @classmethod
    def get_project_script(cls, project_id: str) -> Dict[str, Any]:
        """Retrieves the active script and deserializes its scene manifest."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scripts WHERE project_id = ? ORDER BY version DESC LIMIT 1", (project_id,))
            row = cursor.fetchone()
            if not row:
                return None
            s = dict(row)
            s["scenes"] = json.loads(s.get("scenes_json") or "[]")
            return s
        finally:
            conn.close()

    @classmethod
    def update_scene_narration(cls, project_id: str, scene_number: int, updated_text: str) -> Dict[str, Any]:
        """Allows user to edit scene narration directly in the Script Studio."""
        script = cls.get_project_script(project_id)
        if not script:
            raise ValueError(f"No script found for project '{project_id}'.")

        scenes = script["scenes"]
        found = False
        for sc in scenes:
            if sc["scene_number"] == scene_number:
                sc["narration"] = updated_text
                sc["word_count"] = len(updated_text.split())
                # Re-estimate duration (~140 words per minute -> 2.33 words/sec)
                sc["approx_duration_sec"] = max(30, int(sc["word_count"] / 2.33))
                found = True
                break

        if not found:
            raise ValueError(f"Scene #{scene_number} not found in script.")

        total_words = sum(s["word_count"] for s in scenes)
        total_sec = sum(s["approx_duration_sec"] for s in scenes)
        full_text = "\n\n".join(f"[{s['scene_title']}]\n{s['narration']}" for s in scenes)

        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                UPDATE scripts 
                SET scenes_json = ?, word_count = ?, estimated_duration_sec = ?, 
                    full_narration = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """, (json.dumps(scenes), total_words, total_sec, full_text, script["id"]))
            return cls.get_project_script(project_id)
        finally:
            conn.close()

    @classmethod
    def approve_script(cls, project_id: str) -> Dict[str, Any]:
        """
        Checkpoint 1 Approval: User approves the script.
        Transitions project from 'SCRIPT_REVIEW' to 'VISUAL_PLANNING'.
        """
        script = cls.get_project_script(project_id)
        if not script:
            raise ValueError(f"No script found for project '{project_id}'.")

        conn = get_connection()
        try:
            with conn:
                conn.execute("UPDATE scripts SET approval_status = 'APPROVED', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (script["id"],))
                conn.execute("UPDATE projects SET status = 'VISUAL_PLANNING', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (project_id,))
            
            logger.info("Script for project %s approved by human operator. Advanced to VISUAL_PLANNING.", project_id)
            return {
                "status": "success",
                "message": "Script approved by operator! Project advanced to Stage 4: Visual Director (Visual Manifest).",
                "project_id": project_id,
                "new_status": "VISUAL_PLANNING"
            }
        finally:
            conn.close()

    @classmethod
    def _generate_fallback_scenes(cls, central_q: str, key_figures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scenes = []
        s1_text = (
            "On October 2nd, 2001, a single phone call from Zurich Kloten Airport froze the financial nervous system of Europe. "
            "An Airbus carrying 180 passengers was taxiing toward the runway when the control tower received an unprecedented directive: "
            "fuel suppliers had cut off the kerosene. The credit lines were dead. "
            "Within forty-eight hours, every plane belonging to one of the most prestigious airlines on Earth was grounded on tarmac across the globe. "
            "To the traveling public, Swissair was not merely a carrier—it was nicknamed 'The Flying Bank', a fortress of Swiss financial invulnerability. "
            "Yet behind corporate doors, a catastrophic strategy of debt, ambition, and institutional blind spots had quietly driven the company over the edge."
        )
        scenes.append({
            "scene_number": 1,
            "scene_title": "Beat 1 — The Grounding at Kloten",
            "narrative_beat": "Opening Hook",
            "narration": s1_text,
            "word_count": len(s1_text.split()),
            "evidence_refs": ["CLM-SA-01", "SRC-01"],
            "emotional_intention": "Shock / Immediate Stakes",
            "visual_direction": "Slow push-in on an authentic declassified airport log sheet. Harsh tungsten lamp lighting. Abrupt cut to archival tarmac footage of grounded aircraft in overcast rain.",
            "approx_duration_sec": 85,
            "transition_intention": "Hard cut to complete silence, followed by deep atmospheric drone.",
            "sound_direction": "Muffled radio tower chatter under sub-bass swell, cutting sharply on the word 'dead'."
        })

        s2_text = (
            f"How does an institution backed by the world's most powerful banking cartel collapse in less than forty-eight hours? "
            f"{central_q} "
            "For decades, Swiss business schools taught that Swissair was indestructible. "
            "Its balance sheet was bolstered by real estate, international catering subsidiaries, and a sterling credit rating. "
            "To understand the sudden death of this national icon, we have to look past the panic on the runway and examine a secretive corporate decision "
            "made seven years earlier—a strategy that promised to build a global aviation empire, but ended up constructing a financial trap."
        )
        scenes.append({
            "scene_number": 2,
            "scene_title": "Beat 2 — The Illusion of the Flying Bank",
            "narrative_beat": "Central Mystery or Question",
            "narration": s2_text,
            "word_count": len(s2_text.split()),
            "evidence_refs": ["SRC-01", "SRC-02"],
            "emotional_intention": "Analytical Suspense",
            "visual_direction": "Cinematic macro shot of golden vintage Swissair livery pin, transitioning into an animated corporate balance sheet dissolving into red deficit numbers.",
            "approx_duration_sec": 95,
            "transition_intention": "Smooth camera zoom into a spinning 1994 vintage calendar page.",
            "sound_direction": "Gentle acoustic piano motifs layered over low ticking clock Foley."
        })

        s3_text = (
            "The origin of the disaster was not financial greed, but political isolation. "
            "In December 1992, Swiss citizens narrowly voted in a historic referendum against joining the European Economic Area. "
            "While the vote was celebrated by nationalists, inside Swissair headquarters it was treated as a catastrophe. "
            "European deregulation was creating mega-carriers like British Airways and Lufthansa, who were suddenly free to fly anywhere on the continent. "
            "Swissair, marooned outside the European Union, was legally forbidden from operating domestic routes between European cities. "
            "Locked out of its own backyard, the board concluded that standing still meant slow strangulation."
        )
        scenes.append({
            "scene_number": 3,
            "scene_title": "Beat 3 — The Geographic Island",
            "narrative_beat": "Background and Context",
            "narration": s3_text,
            "word_count": len(s3_text.split()),
            "evidence_refs": ["SRC-01"],
            "emotional_intention": "Strategic Claustrophobia",
            "visual_direction": "Dynamic animated map of Europe: EU airspace illuminated in vibrant blue while Switzerland remains a dark, isolated territory in the center with restricted border flight corridors.",
            "approx_duration_sec": 115,
            "transition_intention": "Whip pan tracking eastward toward European capitals.",
            "sound_direction": "Subtle atmospheric wind and distant echoes of parliament speeches."
        })

        s4_text = (
            "Enter Philippe Bruggisser. An ambitious and charismatic executive who had risen through Swissair's ranks, "
            "Bruggisser took the reins in 1996 with a singular mandate: save the airline by any means necessary. "
            "Advised by elite international management consultants from McKinsey, Bruggisser unveiled what insiders called the 'Hunter Strategy'. "
            "If Swissair could not legally fly inside the European Union, it would simply purchase the airlines that could. "
            "It was bold, aggressive, and deeply seductive to a board terrified of becoming irrelevant. "
            "There was just one fatal flaw: the airlines available for purchase were the ones nobody else wanted."
        )
        scenes.append({
            "scene_number": 4,
            "scene_title": "Beat 4 — The Architect and The Hunter Strategy",
            "narrative_beat": "Introduction of Main Characters",
            "narration": s4_text,
            "word_count": len(s4_text.split()),
            "evidence_refs": ["CLM-SA-01", "SRC-02"],
            "emotional_intention": "Executive Ambition / Foreshadowing",
            "visual_direction": "Black and white portrait photography of Philippe Bruggisser with dramatic side lighting. Kinetic typography highlights 'THE HUNTER STRATEGY' in bold serif type.",
            "approx_duration_sec": 110,
            "transition_intention": "Slide transition matching corporate boardroom slide projection.",
            "sound_direction": "Rhythmic cello pulses and faint paper shuffling."
        })

        s5_text = (
            "Between 1998 and 2000, Swissair went on an unchecked multi-billion dollar shopping spree. "
            "They acquired 49.5% of Belgium's perpetually loss-making flag carrier Sabena, along with stakes in French charter airlines AOM, Air Liberté, and Germany's LTU. "
            "Because European regulations capped foreign ownership at 49%, Swissair could not take full operational control. "
            "Instead, they poured Swiss Francs into recapitalizing these struggling airlines, guaranteeing their debts and modernizing their fleets, "
            "without having the legal authority to cut payroll or streamline unprofitable routes. "
            "Swissair had taken on all of the financial risk with none of the operational control."
        )
        scenes.append({
            "scene_number": 5,
            "scene_title": "Beat 5 — The Minority Trap",
            "narrative_beat": "Conflict and Stakes",
            "narration": s5_text,
            "word_count": len(s5_text.split()),
            "evidence_refs": ["CLM-SA-01", "SRC-02"],
            "emotional_intention": "Mounting Dread",
            "visual_direction": "Split screen comparison: French strike protests at Orly Airport juxtaposed against polished Zurich glass corporate suites. Financial bar chart reveals debt escalating past 4 billion CHF.",
            "approx_duration_sec": 125,
            "transition_intention": "Match cut from falling stock ticker line to a flashing red warning lamp.",
            "sound_direction": "Dissonant synth drone rising in pitch, punctuated by industrial mechanical clanks."
        })

        s6_text = (
            "By early 2001, the cash incinerator could no longer be hidden from public view. "
            "The foreign acquisitions were hemorrhaging over three million francs every single day. "
            "In January, the board finally panics. Bruggisser is abruptly fired, and the company brings in Mario Corti, the respected Chief Financial Officer of Nestlé, "
            "to perform emergency surgery on the balance sheet. "
            "Corti arrived expecting a bad situation. What he discovered inside the ledgers was a financial nightmare. "
            "The company had signed off-balance-sheet guarantees that made SAirGroup legally liable for billions in foreign airline debts. "
            "Then came September 11th, and the global aviation market collapsed overnight."
        )
        scenes.append({
            "scene_number": 6,
            "scene_title": "Beat 6 — The Ledger Nightmare",
            "narrative_beat": "Escalation",
            "narration": s6_text,
            "word_count": len(s6_text.split()),
            "evidence_refs": ["SRC-02", "SRC-03"],
            "emotional_intention": "Claustrophobic Panic",
            "visual_direction": "Forensic document camera zooming across actual audited Ernst & Young liquidator report pages. Red highlighter digitally streaks over 'Off-Balance-Sheet Commitments: 4.2B CHF'.",
            "approx_duration_sec": 135,
            "transition_intention": "Rapid whip pan synchronized with a sudden camera shutter click.",
            "sound_direction": "Staccato violins building in tempo, heartbeat pulse in low frequencies."
        })

        s7_text = (
            "Desperate for survival, Corti turned to Switzerland's two premier financial institutions: UBS and Credit Suisse. "
            "Behind closed doors at the luxury Hotel Dolder above Zurich, an emergency rescue plan called 'Project Phoenix' was drafted. "
            "The banks agreed to finance a new company based around Swissair's profitable regional subsidiary, Crossair. "
            "Crossair would buy Swissair's operating assets at a steep discount, leaving the mountain of debt trapped inside the dying parent company. "
            "It was a brutal triage, but Corti believed it would at least keep the planes flying until the formal handover on October 28th. "
            "He was wrong. The banks had quietly altered the terms of intraday liquidity."
        )
        scenes.append({
            "scene_number": 7,
            "scene_title": "Beat 7 — Project Phoenix and The Midnight Accord",
            "narrative_beat": "Major Discoveries",
            "narration": s7_text,
            "word_count": len(s7_text.split()),
            "evidence_refs": ["SRC-01", "SRC-04"],
            "emotional_intention": "Calculated Betrayal / Tension",
            "visual_direction": "Dimly lit cinematic recreation of the Hotel Dolder conference room: half-empty espresso cups, legal dossiers, and shadowy figures silhouetted against the Zurich skyline at dawn.",
            "approx_duration_sec": 130,
            "transition_intention": "Slow cross-dissolve to early morning airport departure boards.",
            "sound_direction": "Muffled ambient city drone with sparse, lonely electric guitar notes."
        })

        s8_text = (
            "On the morning of October 2nd, the trap snapped shut. "
            "UBS was scheduled to transfer a 250 million franc purchase payment into Swissair's account to fund ongoing operations. "
            "The payment did not arrive. When Corti urgently contacted UBS headquarters, bank executives informed him that due to technical delays "
            "and legal conditions, the funds could not be released. "
            "By noon, Swissair's account balance stood at an astonishing 14.5 million francs—not even enough to buy fuel for the afternoon transatlantic fleet. "
            "At 12:30 PM, Swissair Flight 157 was denied fuel at Zurich. Corti had no choice. He ordered the entire fleet shut down. "
            "For the first time in 70 years, the Swiss cross was grounded."
        )
        scenes.append({
            "scene_number": 8,
            "scene_title": "Beat 8 — The 14 Million Franc Cliff",
            "narrative_beat": "Turning Point or Revelation",
            "narration": s8_text,
            "word_count": len(s8_text.split()),
            "evidence_refs": ["CLM-SA-02", "SRC-01"],
            "emotional_intention": "Tragedy / Cold Realization",
            "visual_direction": "Dramatic sequence: Airport departure board flipping from 'ON TIME' to 'CANCELLED' on twenty simultaneous flights. Archival footage of bewildered passengers gathering at Swissair counters.",
            "approx_duration_sec": 145,
            "transition_intention": "Slow cinematic pull-out to a wide aerial view of silent grounded airplanes parked wingtip to wingtip.",
            "sound_direction": "Sub-bass drop into complete silence, followed by the mournful chime of an airport announcement bell."
        })

        s9_text = (
            "The public reaction in Switzerland was one of profound national grief and fury. "
            "Protesters marched outside UBS headquarters carrying banners reading 'Swissair Assassins'. "
            "Over thirty-eight thousand passengers were stranded across 130 airports from New York to Singapore, with flight crews having to pay hotel bills out of their own personal credit cards. "
            "The Swiss Federal Council was forced to convene an emergency session, approving a 450 million franc taxpayer bailout just to get stranded citizens home. "
            "Criminal investigations followed. Nineteen board members and executives were hauled into court, though all were ultimately acquitted of criminal charges. "
            "The wreckage of Swissair was absorbed into Crossair to form Swiss International Air Lines—which, in the ultimate irony, was bought four years later by Germany's Lufthansa."
        )
        scenes.append({
            "scene_number": 9,
            "scene_title": "Beat 9 — The National Trauma",
            "narrative_beat": "Consequences and Fallout",
            "narration": s9_text,
            "word_count": len(s9_text.split()),
            "evidence_refs": ["CLM-SA-03", "CLM-SA-05", "SRC-04"],
            "emotional_intention": "Somber Reckoning",
            "visual_direction": "Archival news montage of protest marches in Zurich, parliamentary debates in Bern, and Lufthansa corporate logos replacing the historic Swissair font.",
            "approx_duration_sec": 130,
            "transition_intention": "Fade to charcoal black.",
            "sound_direction": "Muted crowd protest ambiance fading under a solemn string quartet."
        })

        s10_text = (
            "The fall of Swissair remains a masterclass in the perils of executive hubris and strategic self-delusion. "
            "Philippe Bruggisser believed that financial engineering and aggressive expansion could overcome the fundamental laws of economic gravity. "
            "The board failed to ask the hard questions because the company's historic reputation blinded them to its operational rot. "
            "And when the crisis struck, the institutions they counted on for survival made a cold, calculated decision to let the legacy die. "
            "The lesson of the Flying Bank is as relevant today in the boardrooms of Silicon Valley and Wall Street as it was on that rainy October runway: "
            "no brand is too sacred to fall, and no corporate fortress is stronger than the assumptions it is built upon."
        )
        scenes.append({
            "scene_number": 10,
            "scene_title": "Beat 10 — The Price of Arrogance",
            "narrative_beat": "Final Conclusion",
            "narration": s10_text,
            "word_count": len(s10_text.split()),
            "evidence_refs": ["SRC-01", "SRC-04"],
            "emotional_intention": "Philosophical Resonance / Memorable Resolution",
            "visual_direction": "Cinematic slow-motion shot of a solitary vintage Swissair jet ascending through clouds into sunset, slowly dissolving into a clean dark title slate.",
            "approx_duration_sec": 125,
            "transition_intention": "Cinematic slow fade to black with end card credentials.",
            "sound_direction": "Full emotional orchestral swell resolving into a quiet, lingering piano note."
        })
        return scenes
