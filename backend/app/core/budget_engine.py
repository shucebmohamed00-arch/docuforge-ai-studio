"""
DocuForge AI - Budget & Cost Tracking Engine
Enforces the $50 monthly hard ceiling, logs all API costs, and tracks spending per agent & project.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from ..database import get_connection
from ..config import MONTHLY_HARD_CEILING_USD, MONTHLY_WARNING_THRESHOLD_USD

logger = logging.getLogger("docuforge.budget")

class BudgetExceededException(Exception):
    """Raised when an operation would exceed the monthly budget limit."""
    pass

class BudgetEngine:
    @staticmethod
    def get_current_month_key() -> str:
        return datetime.now().strftime("%Y-%m")

    @classmethod
    def get_monthly_status(cls, month_key: Optional[str] = None) -> Dict[str, Any]:
        """Returns the current monthly spending, ceiling, and lock status."""
        month = month_key or cls.get_current_month_key()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT month_key, budget_ceiling_usd, warning_threshold_usd, total_spent_usd, is_locked FROM monthly_budgets WHERE month_key = ?",
                (month,)
            )
            row = cursor.fetchone()
            if not row:
                # Initialize month
                cursor.execute(
                    "INSERT INTO monthly_budgets (month_key, budget_ceiling_usd, warning_threshold_usd, total_spent_usd, is_locked) VALUES (?, ?, ?, 0.0, 0)",
                    (month, MONTHLY_HARD_CEILING_USD, MONTHLY_WARNING_THRESHOLD_USD)
                )
                conn.commit()
                return {
                    "month": month,
                    "budget_ceiling_usd": MONTHLY_HARD_CEILING_USD,
                    "warning_threshold_usd": MONTHLY_WARNING_THRESHOLD_USD,
                    "total_spent_usd": 0.0,
                    "remaining_usd": MONTHLY_HARD_CEILING_USD,
                    "is_warning": False,
                    "is_locked": False
                }
            
            spent = float(row["total_spent_usd"])
            ceiling = float(row["budget_ceiling_usd"])
            warning = float(row["warning_threshold_usd"])
            is_locked = bool(row["is_locked"]) or spent >= ceiling
            is_warning = spent >= warning

            return {
                "month": row["month_key"],
                "budget_ceiling_usd": ceiling,
                "warning_threshold_usd": warning,
                "total_spent_usd": round(spent, 4),
                "remaining_usd": round(max(0.0, ceiling - spent), 4),
                "is_warning": is_warning,
                "is_locked": is_locked
            }
        finally:
            conn.close()

    @classmethod
    def can_afford(cls, estimated_cost_usd: float) -> Tuple[bool, Optional[str]]:
        """Checks if an operation with the given estimated cost is within the remaining budget."""
        status = cls.get_monthly_status()
        if status["is_locked"]:
            return False, f"Monthly budget ceiling (${status['budget_ceiling_usd']:.2f}) reached. Spending is locked."
        
        projected = status["total_spent_usd"] + estimated_cost_usd
        if projected > status["budget_ceiling_usd"]:
            return False, f"Operation estimated at ${estimated_cost_usd:.4f} would exceed monthly limit of ${status['budget_ceiling_usd']:.2f} (current spent: ${status['total_spent_usd']:.2f})."
        
        return True, None

    @classmethod
    def record_cost(
        cls,
        agent_name: str,
        operation: str,
        model_or_service: str,
        cost_usd: float,
        project_id: Optional[str] = None,
        tokens_in: int = 0,
        tokens_out: int = 0,
        notes: str = ""
    ) -> Dict[str, Any]:
        """
        Records a cost entry in budget_logs, increments monthly_budgets,
        and updates the project's budget_spent_usd if project_id is provided.
        """
        can_run, reason = cls.can_afford(cost_usd)
        if not can_run and cost_usd > 0:
            logger.error("Budget ceiling blocked operation '%s' by agent '%s': %s", operation, agent_name, reason)
            raise BudgetExceededException(reason)

        month = cls.get_current_month_key()
        log_id = str(uuid.uuid4())
        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                # 1. Log transaction
                cursor.execute("""
                INSERT INTO budget_logs (
                    id, project_id, agent_name, operation, model_or_service,
                    tokens_in, tokens_out, cost_usd, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    log_id, project_id, agent_name, operation, model_or_service,
                    tokens_in, tokens_out, cost_usd, notes
                ))

                # 2. Update monthly total
                cursor.execute("""
                UPDATE monthly_budgets
                SET total_spent_usd = total_spent_usd + ?,
                    is_locked = CASE WHEN (total_spent_usd + ?) >= budget_ceiling_usd THEN 1 ELSE 0 END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE month_key = ?
                """, (cost_usd, cost_usd, month))

                # 3. Update project spent if applicable
                if project_id:
                    cursor.execute("""
                    UPDATE projects
                    SET budget_spent_usd = budget_spent_usd + ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """, (cost_usd, project_id))

            logger.info("Logged cost: $%0.4f by %s for %s", cost_usd, agent_name, operation)
            return {
                "log_id": log_id,
                "agent_name": agent_name,
                "operation": operation,
                "cost_usd": cost_usd,
                "month": month
            }
        finally:
            conn.close()

    @classmethod
    def get_agent_breakdown(cls, month_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns spend breakdown grouped by agent."""
        month = month_key or cls.get_current_month_key()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT agent_name, 
                   COUNT(*) as operation_count, 
                   ROUND(SUM(cost_usd), 4) as total_cost,
                   SUM(tokens_in) as total_tokens_in,
                   SUM(tokens_out) as total_tokens_out
            FROM budget_logs
            WHERE strftime('%Y-%m', created_at) = ?
            GROUP BY agent_name
            ORDER BY total_cost DESC
            """, (month,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @classmethod
    def get_recent_logs(cls, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent cost log entries."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, project_id, agent_name, operation, model_or_service, 
                   tokens_in, tokens_out, cost_usd, notes, created_at
            FROM budget_logs
            ORDER BY created_at DESC
            LIMIT ?
            """, (limit,))
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()
