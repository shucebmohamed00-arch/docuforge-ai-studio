"""
DocuForge AI - Project Data Model
Encapsulates database operations for Projects, Topics, Scripts, and Assets.
"""
import uuid
import json
import re
from typing import Dict, Any, List, Optional
from ..database import get_connection
from ..core.state_machine import ProjectStatus, validate_transition

class ProjectManager:
    @staticmethod
    def _slugify(text: str) -> str:
        s = re.sub(r'[^\w\s-]', '', text.lower()).strip()
        return re.sub(r'[-\s]+', '-', s)

    @classmethod
    def create_project(
        cls,
        title: str,
        pillar: str,
        target_duration_mins: int = 20,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        project_id = str(uuid.uuid4())
        base_slug = cls._slugify(title)
        slug = f"{base_slug}-{project_id[:8]}"
        meta_str = json.dumps(metadata or {})

        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                INSERT INTO projects (
                    id, title, slug, pillar, target_duration_mins,
                    status, budget_allocated_usd, budget_spent_usd, metadata_json,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 'TOPIC_SELECTION', 5.00, 0.0, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (project_id, title, slug, pillar, target_duration_mins, meta_str))
            return cls.get_project(project_id)
        finally:
            conn.close()

    @classmethod
    def get_project(cls, project_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data["metadata"] = json.loads(data.get("metadata_json") or "{}")
            return data
        finally:
            conn.close()

    @classmethod
    def list_projects(cls) -> List[Dict[str, Any]]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, title, slug, pillar, target_duration_mins, status, 
                   budget_allocated_usd, budget_spent_usd, created_at, updated_at
            FROM projects 
            ORDER BY created_at DESC
            """)
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @classmethod
    def update_status(cls, project_id: str, new_status: str) -> Dict[str, Any]:
        project = cls.get_project(project_id)
        if not project:
            raise ValueError(f"Project '{project_id}' not found.")
        
        valid, error = validate_transition(project["status"], new_status)
        if not valid:
            raise ValueError(error)

        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                UPDATE projects 
                SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
                """, (new_status, project_id))
            return cls.get_project(project_id)
        finally:
            conn.close()

    @classmethod
    def delete_project(cls, project_id: str) -> bool:
        conn = get_connection()
        try:
            with conn:
                cursor = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
                return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def get_project_full_summary(cls, project_id: str) -> Optional[Dict[str, Any]]:
        """Compiles complete state summary for a project including assets, scripts, topics."""
        project = cls.get_project(project_id)
        if not project:
            return None
        
        conn = get_connection()
        try:
            cursor = conn.cursor()

            # Topics
            cursor.execute("SELECT * FROM topics WHERE project_id = ?", (project_id,))
            topics = [dict(r) for r in cursor.fetchall()]

            # Active script
            cursor.execute("SELECT * FROM scripts WHERE project_id = ? ORDER BY version DESC LIMIT 1", (project_id,))
            script_row = cursor.fetchone()
            script = dict(script_row) if script_row else None

            # Evidence dossier
            cursor.execute("SELECT * FROM evidence_dossiers WHERE project_id = ?", (project_id,))
            dossier_row = cursor.fetchone()
            dossier = dict(dossier_row) if dossier_row else None

            # Visual assets counts
            cursor.execute("""
            SELECT approval_status, COUNT(*) as cnt 
            FROM visual_assets 
            WHERE project_id = ? 
            GROUP BY approval_status
            """, (project_id,))
            asset_stats = {r["approval_status"]: r["cnt"] for r in cursor.fetchall()}

            # Active jobs
            cursor.execute("SELECT * FROM render_jobs WHERE project_id = ? ORDER BY created_at DESC LIMIT 5", (project_id,))
            jobs = [dict(r) for r in cursor.fetchall()]

            return {
                "project": project,
                "topics": topics,
                "script": script,
                "evidence_dossier": dossier,
                "asset_stats": asset_stats,
                "recent_jobs": jobs
            }
        finally:
            conn.close()
