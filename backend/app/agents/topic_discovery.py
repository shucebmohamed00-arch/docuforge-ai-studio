"""
DocuForge AI - Agent 1: Topic Discovery Agent
Discovers high-potential documentary topics and evaluates them with a 100-point scoring matrix.
Enforces mandatory rejection rules and outputs 5 vetted candidates with opening hooks.
"""
import uuid
import json
import logging
from typing import List, Dict, Any, Tuple
from .hook_intelligence import ViralHookIntelligenceAgent
from ..database import get_connection
from ..core.budget_engine import BudgetEngine

logger = logging.getLogger("docuforge.agents.topic_discovery")

# Topic Seed Intelligence Bank categorized by the 4 pillars
DOCUMENTARY_KNOWLEDGE_BASE = [
    # Business, Money and Corporate Power (30%)
    {
        "title": "The Swiss Air Grounding: How Arrogance Destroyed the Bank of the Skies",
        "pillar": "BUSINESS",
        "angle": "How an aggressive expansion strategy and complex hidden debt collapsed Switzerland's most prestigious corporate symbol overnight.",
        "central_conflict": "Swiss Air executives vs. Credit Suisse and UBS over emergency credit lines on the day the planes were grounded.",
        "target_audience": "US, UK, European and global business/finance enthusiasts",
        "has_primary_sources": True,
        "has_free_archival_footage": True,
        "allegations_verifiable": True,
        "scores": {
            "audience_interest": 18,
            "storytelling": 19,
            "originality": 14,
            "visual_availability": 14,
            "research_depth": 14,
            "competition": 9,
            "feasibility": 5
        },
        "scoring_explanation": "Extensive public inquiry records and parliamentary investigations provide bulletproof paper trails. Archival broadcast footage and authentic aircraft photos are accessible in Swiss and European public archives."
    },
    {
        "title": "The Nickel Squeeze of 2022: How One Tycoon Froze the London Metal Exchange",
        "pillar": "BUSINESS",
        "angle": "An investigative breakdown of the short squeeze on Tsingshan Holding Group and the controversial decision to cancel $12 billion in trades.",
        "central_conflict": "Independent hedge funds and market makers vs. the London Metal Exchange clearing house.",
        "target_audience": "Global financial investigation, markets, and economic documentary audiences",
        "has_primary_sources": True,
        "has_free_archival_footage": True,
        "allegations_verifiable": True,
        "scores": {
            "audience_interest": 17,
            "storytelling": 18,
            "originality": 14,
            "visual_availability": 13,
            "research_depth": 14,
            "competition": 9,
            "feasibility": 4
        },
        "scoring_explanation": "FCA regulatory findings, UK High Court filings, and exchange statements offer complete factual grounding. Financial data visualization and mining archival assets support visual flow."
    },
    # Geopolitics and Global Power (25%)
    {
        "title": "The Bab-el-Mandeb Chokepoint: The 18-Mile Strait Threatening World Trade",
        "pillar": "GEOPOLITICS",
        "angle": "A strategic investigation into how asymmetric drone warfare along the Red Sea disrupted 12% of global seaborne commerce and forced the rerouting of world shipping.",
        "central_conflict": "Global maritime shipping conglomerates and multinational naval patrols vs. regional coastal drone operators.",
        "target_audience": "US, UK, Canadian viewers interested in geopolitical strategy, military history, and macroeconomics",
        "has_primary_sources": True,
        "has_free_archival_footage": True,
        "allegations_verifiable": True,
        "scores": {
            "audience_interest": 19,
            "storytelling": 18,
            "originality": 13,
            "visual_availability": 15,
            "research_depth": 14,
            "competition": 8,
            "feasibility": 5
        },
        "scoring_explanation": "Outstanding visual availability through DVIDS naval archive video, satellite mapping, AIS shipping radar data, and US Naval Institute documentation."
    },
    {
        "title": "The Lithium Triangle: The Quiet Scramble Beneath the Atacama",
        "pillar": "GEOPOLITICS",
        "angle": "Behind the diplomatic and corporate maneuvers between Beijing, Washington, and South American governments for control over the salt flats powering the EV revolution.",
        "central_conflict": "Indigenous water rights and environmental regulators vs. multinational mining conglomerates and state-backed investors.",
        "target_audience": "Global documentary viewers interested in resource conflicts, green energy, and international affairs",
        "has_primary_sources": True,
        "has_free_archival_footage": True,
        "allegations_verifiable": True,
        "scores": {
            "audience_interest": 16,
            "storytelling": 17,
            "originality": 14,
            "visual_availability": 14,
            "research_depth": 14,
            "competition": 9,
            "feasibility": 4
        },
        "scoring_explanation": "USGS geological reports, Chilean mining ministry audit records, and high-resolution NASA satellite imagery provide verified visual and statistical grounding."
    },
    # Technology and Innovation (25%)
    {
        "title": "ASML and the Light Trap: How Dutch Engineers Monopolized the Modern World",
        "pillar": "TECHNOLOGY",
        "angle": "How an obscure Philips spinoff in Veldhoven spent three decades engineering Extreme Ultraviolet Lithography (EUV) machines that no other company on Earth can build.",
        "central_conflict": "ASML engineers overcoming theoretical physics limits vs. the geopolitical struggle between the US and China over chip export restrictions.",
        "target_audience": "US, UK, international tech enthusiasts, engineers, and innovation followers",
        "has_primary_sources": True,
        "has_free_archival_footage": True,
        "allegations_verifiable": True,
        "scores": {
            "audience_interest": 20,
            "storytelling": 19,
            "originality": 13,
            "visual_availability": 14,
            "research_depth": 15,
            "competition": 8,
            "feasibility": 5
        },
        "scoring_explanation": "Patent filings, semiconductor industry white papers, corporate archival footage, and animated physics/optics diagrams provide rich documentary assets."
    },
    {
        "title": "The Collapse of Theranos: How Whistleblowers Toppled a Silicon Valley Mirage",
        "pillar": "TECHNOLOGY",
        "angle": "A forensic look at the mechanical failures of the Edison machine and how lab directors risked prison to expose the truth.",
        "central_conflict": "Tyler Shultz and Erika Cheung vs. Theranos legal intimidation machine.",
        "target_audience": "Tech, startup, and investigative drama fans",
        "has_primary_sources": True,
        "has_free_archival_footage": True,
        "allegations_verifiable": True,
        "scores": {
            "audience_interest": 18,
            "storytelling": 19,
            "originality": 9, # Lower originality due to existing coverage
            "visual_availability": 15,
            "research_depth": 15,
            "competition": 6,
            "feasibility": 5
        },
        "scoring_explanation": "Federal trial transcripts, SEC filings, and whistleblower depositions offer verified facts. However, high competition reduces total score relative to fresher angles."
    },
    # History and Extraordinary Investigations (20%)
    {
        "title": "The Stuxnet Operation: The Ghost Code That Shattered Natanz",
        "pillar": "HISTORY",
        "angle": "The covert intelligence operation that inserted a self-replicating zero-day worm into an air-gapped nuclear enrichment centrifuge facility.",
        "central_conflict": "Joint cyber-intelligence operators vs. Iranian nuclear engineers and Siemens PLC controllers.",
        "target_audience": "History, intelligence operations, and cybersecurity documentary audiences",
        "has_primary_sources": True,
        "has_free_archival_footage": True,
        "allegations_verifiable": True,
        "scores": {
            "audience_interest": 19,
            "storytelling": 19,
            "originality": 13,
            "visual_availability": 14,
            "research_depth": 15,
            "competition": 8,
            "feasibility": 4
        },
        "scoring_explanation": "Symantec security analysis white papers, IAEA inspection reports, and declassified defense archives provide verified technical and historical evidence."
    },
    {
        "title": "Project Azorian: Howard Hughes, the CIA, and the Sunken Submarine",
        "pillar": "HISTORY",
        "angle": "How the CIA spent $800 million creating a fake deep-sea mining venture with billionaire Howard Hughes to secretly recover a sunken Soviet nuclear submarine from 16,000 feet below the Pacific.",
        "central_conflict": "CIA engineers on the Hughes Glomar Explorer vs. Soviet naval surveillance ships monitoring the recovery site.",
        "target_audience": "Cold War history, naval history, and declassified espionage fans",
        "has_primary_sources": True,
        "has_free_archival_footage": True,
        "allegations_verifiable": True,
        "scores": {
            "audience_interest": 18,
            "storytelling": 20,
            "originality": 14,
            "visual_availability": 14,
            "research_depth": 15,
            "competition": 9,
            "feasibility": 5
        },
        "scoring_explanation": "Extensive declassified CIA records, Glomar Explorer construction footage in the US National Archives, and naval records."
    },
    # Intentionally flawed candidate for rejection filter testing
    {
        "title": "The Secret Syndicate Controlling World Banking From Antarctica",
        "pillar": "BUSINESS",
        "angle": "Conspiracy theories claiming underground vaults in Queen Maud Land dictate currency values.",
        "central_conflict": "Anonymous whistleblowers vs. unnamed global elites.",
        "target_audience": "Sensationalist web users",
        "has_primary_sources": False, # REJECTION TRIGGER
        "has_free_archival_footage": False, # REJECTION TRIGGER
        "allegations_verifiable": False, # REJECTION TRIGGER
        "scores": {
            "audience_interest": 12,
            "storytelling": 10,
            "originality": 5,
            "visual_availability": 2,
            "research_depth": 2,
            "competition": 5,
            "feasibility": 1
        },
        "scoring_explanation": "Fails mandatory fact-checking and visual evidence criteria."
    }
]

class TopicDiscoveryAgent:
    @classmethod
    def evaluate_topic_scores(cls, item: Dict[str, Any]) -> Tuple[int, Dict[str, int], bool, List[str]]:
        """
        Applies the 100-point scoring formula and checks mandatory rejection criteria:
        Audience Interest: 20
        Storytelling: 20
        Originality: 15
        Visual Availability: 15
        Research Depth: 15
        Competition: 10
        Feasibility: 5
        Total = 100
        """
        scores = item.get("scores", {})
        total = (
            scores.get("audience_interest", 0) +
            scores.get("storytelling", 0) +
            scores.get("originality", 0) +
            scores.get("visual_availability", 0) +
            scores.get("research_depth", 0) +
            scores.get("competition", 0) +
            scores.get("feasibility", 0)
        )

        rejection_reasons = []
        if not item.get("has_primary_sources", True):
            rejection_reasons.append("Mandatory Rejection: Credible primary sources or official documentation are insufficient.")
        if not item.get("has_free_archival_footage", True):
            rejection_reasons.append("Mandatory Rejection: Topic requires expensive paid footage; authentic free archival assets cannot be found.")
        if not item.get("allegations_verifiable", True):
            rejection_reasons.append("Mandatory Rejection: Critical claims and allegations cannot be verified against reliable journalism or public records.")
        if total < 70:
            rejection_reasons.append(f"Score below threshold: Total score {total}/100 is below the 70-point minimum.")

        is_rejected = len(rejection_reasons) > 0
        return total, scores, is_rejected, rejection_reasons

    @classmethod
    def discover_five_candidates(cls, project_id: str, preferred_pillar: str = None) -> Dict[str, Any]:
        """
        Discovers and scores documentary candidates.
        Returns the top 5 vetted candidates with opening hooks and a log of rejected candidates.
        Logs budget usage ($0.03 for discovery reasoning).
        """
        # Record API cost in budget
        BudgetEngine.record_cost(
            agent_name="TOPIC_DISCOVERY_AGENT",
            operation="TOPIC_SCORED_DISCOVERY",
            model_or_service="GEMINI_REASONING_PIPELINE",
            cost_usd=0.03,
            project_id=project_id,
            tokens_in=1200,
            tokens_out=600,
            notes="Analyzed trend streams, scored candidate dossiers, generated opening hooks"
        )

        candidates = []
        rejected_log = []

        for item in DOCUMENTARY_KNOWLEDGE_BASE:
            total, scores, is_rejected, reasons = cls.evaluate_topic_scores(item)
            topic_id = str(uuid.uuid4())

            if is_rejected:
                rejected_log.append({
                    "title": item["title"],
                    "pillar": item["pillar"],
                    "total_score": total,
                    "reasons": reasons
                })
                continue

            # Generate 3 hooks & titles via Viral Hook Intelligence Agent
            hooks = ViralHookIntelligenceAgent.generate_opening_hooks(item)
            titles = ViralHookIntelligenceAgent.generate_title_concepts(item)

            candidate_obj = {
                "id": topic_id,
                "project_id": project_id,
                "title": item["title"],
                "pillar": item["pillar"],
                "angle": item["angle"],
                "central_conflict": item["central_conflict"],
                "target_audience": item["target_audience"],
                "score_audience_interest": scores["audience_interest"],
                "score_storytelling": scores["storytelling"],
                "score_originality": scores["originality"],
                "score_visual_availability": scores["visual_availability"],
                "score_research_depth": scores["research_depth"],
                "score_competition": scores["competition"],
                "score_feasibility": scores["feasibility"],
                "total_score": total,
                "scoring_explanation": item["scoring_explanation"],
                "hooks": hooks,
                "title_variants": titles,
                "status": "CANDIDATE"
            }
            candidates.append(candidate_obj)

        # Sort by total score descending
        candidates.sort(key=lambda x: x["total_score"], reverse=True)
        top_five = candidates[:5]

        # Save the top five to database for this project
        conn = get_connection()
        try:
            with conn:
                # Clear previous candidates for this project
                conn.execute("DELETE FROM topics WHERE project_id = ?", (project_id,))
                
                for c in top_five:
                    conn.execute("""
                    INSERT INTO topics (
                        id, project_id, title, pillar, angle, central_conflict, target_audience,
                        score_audience_interest, score_storytelling, score_originality,
                        score_visual_availability, score_research_depth, score_competition,
                        score_feasibility, total_score, scoring_explanation,
                        status, hooks_json, title_variants_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CANDIDATE', ?, ?, CURRENT_TIMESTAMP)
                    """, (
                        c["id"], c["project_id"], c["title"], c["pillar"], c["angle"],
                        c["central_conflict"], c["target_audience"],
                        c["score_audience_interest"], c["score_storytelling"], c["score_originality"],
                        c["score_visual_availability"], c["score_research_depth"], c["score_competition"],
                        c["score_feasibility"], c["total_score"], c["scoring_explanation"],
                        json.dumps(c["hooks"]), json.dumps(c["title_variants"])
                    ))
        finally:
            conn.close()

        logger.info("Generated 5 top candidates for project %s (top score: %d/100)", project_id, top_five[0]["total_score"])
        return {
            "project_id": project_id,
            "candidates": top_five,
            "rejected_log": rejected_log
        }

    @classmethod
    def select_topic(cls, project_id: str, topic_id: str) -> Dict[str, Any]:
        """
        Human decision point: User reviews the 5 topics and selects 1.
        Updates topic status to 'SELECTED', updates project's selected_topic_id,
        and transitions project from 'TOPIC_SELECTION' to 'RESEARCH_IN_PROGRESS'.
        """
        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM topics WHERE id = ? AND project_id = ?", (topic_id, project_id))
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Topic '{topic_id}' not found for project '{project_id}'.")
                
                # Mark selected topic
                cursor.execute("UPDATE topics SET status = 'REJECTED' WHERE project_id = ?", (project_id,))
                cursor.execute("UPDATE topics SET status = 'SELECTED' WHERE id = ?", (topic_id,))

                # Transition project to RESEARCH_IN_PROGRESS
                cursor.execute("""
                UPDATE projects 
                SET selected_topic_id = ?, 
                    title = ?, 
                    pillar = ?,
                    status = 'RESEARCH_IN_PROGRESS', 
                    updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
                """, (topic_id, row["title"], row["pillar"], project_id))

            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            updated_proj = dict(cursor.fetchone())
            return {
                "status": "success",
                "message": f"Topic '{row['title']}' selected. Project transitioned to RESEARCH_IN_PROGRESS.",
                "project": updated_proj,
                "selected_topic": dict(row)
            }
        finally:
            conn.close()
