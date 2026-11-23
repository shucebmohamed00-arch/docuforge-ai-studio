"""
DocuForge AI - Background Job Runner
Tracks async tasks (rendering, agent workflows, asset downloads) with persistent SQLite state.
"""
import uuid
import threading
import logging
from datetime import datetime
from typing import Callable, Any, Optional, Dict
from ..database import get_connection

logger = logging.getLogger("docuforge.jobs")

class JobRunner:
    @staticmethod
    def create_job(project_id: str, job_type: str, stage_message: str = "Queued") -> str:
        from ..models.project import ProjectManager
        ProjectManager.ensure_project(project_id)
        job_id = str(uuid.uuid4())
        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                INSERT INTO render_jobs (id, project_id, job_type, status, progress_pct, stage_message, created_at)
                VALUES (?, ?, ?, 'QUEUED', 0, ?, CURRENT_TIMESTAMP)
                """, (job_id, project_id, job_type, stage_message))
            return job_id
        finally:
            conn.close()

    @staticmethod
    def update_job(
        job_id: str,
        status: Optional[str] = None,
        progress_pct: Optional[int] = None,
        stage_message: Optional[str] = None,
        output_path: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        conn = get_connection()
        try:
            updates = []
            params = []
            if status:
                updates.append("status = ?")
                params.append(status)
                if status == "RUNNING":
                    updates.append("started_at = CURRENT_TIMESTAMP")
                elif status in ["COMPLETED", "FAILED", "CANCELLED"]:
                    updates.append("completed_at = CURRENT_TIMESTAMP")
            if progress_pct is not None:
                updates.append("progress_pct = ?")
                params.append(progress_pct)
            if stage_message is not None:
                updates.append("stage_message = ?")
                params.append(stage_message)
            if output_path is not None:
                updates.append("output_path = ?")
                params.append(output_path)
            if error_message is not None:
                updates.append("error_message = ?")
                params.append(error_message)

            if updates:
                params.append(job_id)
                with conn:
                    conn.execute(f"UPDATE render_jobs SET {', '.join(updates)} WHERE id = ?", params)
        finally:
            conn.close()

    @staticmethod
    def get_job(job_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM render_jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @classmethod
    def run_in_background(
        cls,
        project_id: str,
        job_type: str,
        target_func: Callable[..., Any],
        *args,
        **kwargs
    ) -> str:
        """Launches target_func in a background thread and updates job status."""
        job_id = cls.create_job(project_id, job_type, "Initializing task...")

        def _worker():
            cls.update_job(job_id, status="RUNNING", progress_pct=5, stage_message="Task in progress")
            try:
                # Target func can accept a progress_callback(progress_pct, stage_msg)
                def progress_cb(pct: int, msg: str):
                    cls.update_job(job_id, progress_pct=pct, stage_message=msg)

                result = target_func(*args, progress_callback=progress_cb, **kwargs)
                out_path = result if isinstance(result, str) else None
                cls.update_job(job_id, status="COMPLETED", progress_pct=100, stage_message="Completed successfully", output_path=out_path)
            except Exception as e:
                logger.exception("Background job %s failed: %s", job_id, e)
                cls.update_job(job_id, status="FAILED", stage_message="Execution failed", error_message=str(e))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return job_id
