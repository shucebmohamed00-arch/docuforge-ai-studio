"""
DocuForge AI - Database Manager
Handles SQLite connection, schema migrations, and transaction management.
"""
import sqlite3
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from .config import DATABASE_PATH

logger = logging.getLogger("docuforge.database")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initializes the database schema if tables do not exist."""
    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        
        # 1. Projects Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            slug TEXT UNIQUE,
            pillar TEXT NOT NULL, -- Business, Geopolitics, Technology, History
            target_duration_mins INTEGER DEFAULT 20,
            status TEXT NOT NULL DEFAULT 'TOPIC_SELECTION',
            selected_topic_id TEXT,
            budget_allocated_usd REAL DEFAULT 5.0,
            budget_spent_usd REAL DEFAULT 0.0,
            metadata_json TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Topics Table (Topic Discovery proposals)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            title TEXT NOT NULL,
            pillar TEXT NOT NULL,
            angle TEXT NOT NULL,
            central_conflict TEXT,
            target_audience TEXT,
            score_audience_interest INTEGER DEFAULT 0,
            score_storytelling INTEGER DEFAULT 0,
            score_originality INTEGER DEFAULT 0,
            score_visual_availability INTEGER DEFAULT 0,
            score_research_depth INTEGER DEFAULT 0,
            score_competition INTEGER DEFAULT 0,
            score_feasibility INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            scoring_explanation TEXT,
            rejection_reasons TEXT,
            status TEXT DEFAULT 'CANDIDATE', -- CANDIDATE, SELECTED, REJECTED
            hooks_json TEXT DEFAULT '[]',
            title_variants_json TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        """)

        # 3. Evidence Dossier Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence_dossiers (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL UNIQUE,
            central_question TEXT NOT NULL,
            background_summary TEXT,
            key_figures_json TEXT DEFAULT '[]',
            timeline_events_json TEXT DEFAULT '[]',
            claims_json TEXT DEFAULT '[]',
            sources_json TEXT DEFAULT '[]',
            research_gaps_json TEXT DEFAULT '[]',
            confidence_score REAL DEFAULT 0.0,
            status TEXT DEFAULT 'DRAFT', -- DRAFT, VERIFIED, NEEDS_REVIEW
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        """)

        # 4. Scripts Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scripts (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            version INTEGER DEFAULT 1,
            title TEXT NOT NULL,
            word_count INTEGER DEFAULT 0,
            estimated_duration_sec INTEGER DEFAULT 0,
            full_narration TEXT NOT NULL,
            scenes_json TEXT NOT NULL DEFAULT '[]',
            fact_check_status TEXT DEFAULT 'PENDING', -- PENDING, PASSED, FAILED
            approval_status TEXT DEFAULT 'PENDING', -- PENDING, APPROVED, REJECTED
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        """)

        # 5. Visual Manifests Table (Narration-to-Visual breakdown)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS visual_manifests (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            scene_number INTEGER NOT NULL,
            beat_number INTEGER NOT NULL,
            narration_segment TEXT NOT NULL,
            visual_concept TEXT NOT NULL,
            visual_mode TEXT DEFAULT 'INVESTIGATIVE', -- INVESTIGATIVE, CINEMATIC, EXPLAINER
            target_asset_type TEXT NOT NULL, -- ARCHIVAL_VIDEO, AUTHENTIC_PHOTO, MAP, CHART, DOC_REVEAL, STOCK
            target_duration_sec REAL DEFAULT 5.0,
            start_timestamp_sec REAL DEFAULT 0.0,
            matched_asset_id TEXT,
            match_confidence REAL DEFAULT 0.0,
            match_explanation TEXT,
            motion_direction TEXT,
            transition_in TEXT,
            sound_cue TEXT,
            narrative_purpose TEXT,
            emotional_intention TEXT,
            shot_composition TEXT,
            animation_instructions TEXT,
            transition_out TEXT,
            continuity_requirements TEXT,
            status TEXT DEFAULT 'PLANNED',
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        """)

        # Check and add columns to visual_manifests if missing from previous migrations
        cursor.execute("PRAGMA table_info(visual_manifests);")
        vm_cols = {col["name"] for col in cursor.fetchall()}
        vm_new_cols = [
            ("narrative_purpose", "TEXT"),
            ("emotional_intention", "TEXT"),
            ("shot_composition", "TEXT"),
            ("animation_instructions", "TEXT"),
            ("transition_out", "TEXT"),
            ("continuity_requirements", "TEXT")
        ]
        for col_name, col_type in vm_new_cols:
            if col_name not in vm_cols:
                cursor.execute(f"ALTER TABLE visual_manifests ADD COLUMN {col_name} {col_type};")

        # 6. Visual Assets Table (Archive / Media assets)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS visual_assets (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            title TEXT NOT NULL,
            source_name TEXT NOT NULL, -- NASA, US_ARCHIVES, INTERNET_ARCHIVE, WIKIMEDIA, LOC, DVIDS, PEXELS, PIXABAY
            source_url TEXT NOT NULL,
            creator TEXT,
            license_type TEXT NOT NULL, -- PUBLIC_DOMAIN, CC0, CC_BY, PEXELS_FREE, PIXABAY_FREE
            attribution_text TEXT,
            asset_type TEXT NOT NULL, -- VIDEO, PHOTO, DOCUMENT, ANIMATION, GRAPHIC
            authenticity_class TEXT NOT NULL, -- AUTHENTIC_EVENT_FOOTAGE, ARCHIVAL_FOOTAGE, AUTHENTIC_PHOTO, OFFICIAL_DOCUMENT, LICENSED_STOCK, ORIGINAL_ANIMATION
            resolution TEXT DEFAULT '1920x1080',
            duration_sec REAL DEFAULT 0.0,
            local_file_path TEXT,
            preview_url TEXT,
            approval_status TEXT DEFAULT 'PENDING', -- PENDING, APPROVED, REJECTED
            rejection_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        """)

        # 7. Storyboard Items Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS storyboard_items (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            order_index INTEGER NOT NULL,
            scene_number INTEGER NOT NULL,
            beat_number INTEGER NOT NULL,
            narration_text TEXT NOT NULL,
            asset_id TEXT,
            asset_type TEXT,
            visual_summary TEXT,
            camera_movement TEXT,
            transition TEXT,
            sfx_cue TEXT,
            bgm_mood TEXT,
            duration_sec REAL NOT NULL,
            narrative_purpose TEXT,
            emotional_intention TEXT,
            shot_composition TEXT,
            animation_instructions TEXT,
            transition_in TEXT,
            transition_out TEXT,
            continuity_requirements TEXT,
            is_approved INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (asset_id) REFERENCES visual_assets(id) ON DELETE SET NULL
        );
        """)

        # Check and add columns to storyboard_items if missing from previous migrations
        cursor.execute("PRAGMA table_info(storyboard_items);")
        existing_cols = {col["name"] for col in cursor.fetchall()}
        creative_cols = [
            ("narrative_purpose", "TEXT"),
            ("emotional_intention", "TEXT"),
            ("shot_composition", "TEXT"),
            ("animation_instructions", "TEXT"),
            ("transition_in", "TEXT"),
            ("transition_out", "TEXT"),
            ("continuity_requirements", "TEXT")
        ]
        for col_name, col_type in creative_cols:
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE storyboard_items ADD COLUMN {col_name} {col_type};")

        # 7b. Creative Editing Passes Table (Non-Negotiable Professional Multi-Pass Review)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS creative_editing_passes (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            pass_number INTEGER NOT NULL,
            pass_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'COMPLETED', -- PENDING, IN_PROGRESS, COMPLETED, REVISION_REQUIRED
            score INTEGER DEFAULT 100,
            critique_summary TEXT,
            weaknesses_identified_json TEXT DEFAULT '[]',
            refinements_applied_json TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        """)

        # 8. Render Jobs Table (Async job tracking)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS render_jobs (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            job_type TEXT NOT NULL, -- NARRATION_TTS, ANIMATION_GEN, VIDEO_COMPOSITING, QC_CHECK, EXPORT
            status TEXT NOT NULL DEFAULT 'QUEUED', -- QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
            progress_pct INTEGER DEFAULT 0,
            stage_message TEXT DEFAULT '',
            output_path TEXT,
            error_message TEXT,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        """)

        # 9. Budget Tracking Table (Logs every API / resource cost)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget_logs (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            agent_name TEXT NOT NULL,
            operation TEXT NOT NULL,
            model_or_service TEXT NOT NULL,
            tokens_in INTEGER DEFAULT 0,
            tokens_out INTEGER DEFAULT 0,
            cost_usd REAL NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
        );
        """)

        # 10. Monthly Budget Ledger Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS monthly_budgets (
            month_key TEXT PRIMARY KEY, -- 'YYYY-MM'
            budget_ceiling_usd REAL DEFAULT 50.00,
            warning_threshold_usd REAL DEFAULT 40.00,
            total_spent_usd REAL DEFAULT 0.0,
            is_locked INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 11. Performance Tracking Table (Post-publish analytics feedback)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_records (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL UNIQUE,
            youtube_video_id TEXT,
            published_at TIMESTAMP,
            views_7d INTEGER DEFAULT 0,
            views_14d INTEGER DEFAULT 0,
            views_30d INTEGER DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            ctr_pct REAL DEFAULT 0.0,
            first_30s_retention_pct REAL DEFAULT 0.0,
            avg_view_duration_sec REAL DEFAULT 0.0,
            returning_viewers INTEGER DEFAULT 0,
            subscriber_growth INTEGER DEFAULT 0,
            top_traffic_source TEXT,
            lessons_learned TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        """)

        # 12. Settings / Configurations
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Ensure current month exists in monthly_budgets
        curr_month = datetime.now().strftime("%Y-%m")
        cursor.execute("""
        INSERT OR IGNORE INTO monthly_budgets (month_key, budget_ceiling_usd, warning_threshold_usd, total_spent_usd, is_locked)
        VALUES (?, 50.00, 40.00, 0.0, 0);
        """, (curr_month,))

    conn.close()
    logger.info("Database initialized successfully at %s", DATABASE_PATH)
