"""
DocuForge AI - Production Seeder
Ensures default production state is preserved across container restarts / ephemeral cloud storage.
"""
import uuid
import json
import logging
from ..database import get_connection
from ..agents.deep_research import DeepResearchAgent
from ..agents.storyteller import MasterDocumentaryStoryteller
from ..agents.creative_director import DocumentaryCreativeDirector
from ..agents.footage_discovery import RealFootageDiscoveryAgent
from ..agents.storyboard import StoryboardEngine

logger = logging.getLogger("docuforge.seeder")

SWISS_AIR_PROJECT_ID = "swiss-air-grounding-prod"
SWISS_AIR_TITLE = "The Swiss Air Grounding: How Arrogance Destroyed the Bank of the Skies"

def seed_default_production_if_needed():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM projects WHERE id = ? OR title LIKE '%Swiss Air%'", (SWISS_AIR_PROJECT_ID,))
        row = cursor.fetchone()
        if row:
            return row["id"]
        
        logger.info("Auto-seeding primary documentary project: %s", SWISS_AIR_TITLE)
        
        with conn:
            # 1. Project
            conn.execute("""
            INSERT OR REPLACE INTO projects (
                id, title, slug, pillar, target_duration_mins, status,
                budget_allocated_usd, budget_spent_usd, metadata_json, created_at, updated_at
            ) VALUES (?, ?, 'swiss-air-grounding', 'BUSINESS', 15, 'NARRATION_GENERATION', 5.00, 0.26, '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (SWISS_AIR_PROJECT_ID, SWISS_AIR_TITLE))

            # 2. Topic
            topic_id = str(uuid.uuid4())
            conn.execute("""
            INSERT OR REPLACE INTO topics (
                id, project_id, title, pillar, angle, central_conflict, target_audience,
                score_audience_interest, score_storytelling, score_originality,
                score_visual_availability, score_research_depth, score_competition,
                score_feasibility, total_score, status, hooks_json, title_variants_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 18, 19, 14, 14, 14, 9, 5, 93, 'SELECTED', '[]', '[]')
            """, (
                topic_id,
                SWISS_AIR_PROJECT_ID,
                SWISS_AIR_TITLE,
                "BUSINESS",
                "How an aggressive expansion strategy and complex hidden debt collapsed Switzerland's most prestigious corporate symbol overnight.",
                "Swiss Air executives vs. Credit Suisse and UBS over emergency credit lines on the day the planes were grounded.",
                "US, UK, European and global business/finance enthusiasts"
            ))

            conn.execute("UPDATE projects SET selected_topic_id = ? WHERE id = ?", (topic_id, SWISS_AIR_PROJECT_ID))

        # 3. Evidence Dossier
        DeepResearchAgent.compile_evidence_dossier(SWISS_AIR_PROJECT_ID, SWISS_AIR_TITLE)

        # 4. Master Script (10 Scenes)
        MasterDocumentaryStoryteller.generate_full_script(SWISS_AIR_PROJECT_ID)

        # 5. Visual Manifest (Beats)
        DocumentaryCreativeDirector.generate_visual_manifest(SWISS_AIR_PROJECT_ID)

        # 6. Harvest & Approve Assets
        RealFootageDiscoveryAgent.discover_assets_for_project(SWISS_AIR_PROJECT_ID)
        with conn:
            conn.execute("UPDATE visual_assets SET approval_status = 'APPROVED' WHERE project_id = ?", (SWISS_AIR_PROJECT_ID,))

        # 7. Storyboard Compilation & Approval
        StoryboardEngine.compile_storyboard(SWISS_AIR_PROJECT_ID)
        with conn:
            conn.execute("UPDATE storyboard_items SET is_approved = 1 WHERE project_id = ?", (SWISS_AIR_PROJECT_ID,))
            conn.execute("UPDATE projects SET status = 'ANIMATION_SYNTHESIS' WHERE id = ?", (SWISS_AIR_PROJECT_ID,))

        logger.info("Successfully seeded Swiss Air Grounding project to ANIMATION_SYNTHESIS stage!")
        return SWISS_AIR_PROJECT_ID
    except Exception as e:
        logger.exception("Failed to auto-seed default production: %s", e)
        return None
    finally:
        conn.close()
