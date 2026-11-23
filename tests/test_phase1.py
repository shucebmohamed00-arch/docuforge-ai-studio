"""
DocuForge AI - Phase 1 Test Suite
Tests Database initialization, State Machine, Project Management, Budget Tracking, and API endpoints.
"""
import pytest
import sqlite3
from backend.app.config import DATABASE_PATH
from backend.app.database import init_db, get_connection
from backend.app.core.state_machine import ProjectStatus, validate_transition
from backend.app.core.budget_engine import BudgetEngine, BudgetExceededException
from backend.app.models.project import ProjectManager

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_database_initialization():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row["name"] for row in cursor.fetchall()]
    conn.close()

    expected_tables = [
        "projects", "topics", "evidence_dossiers", "scripts", 
        "visual_manifests", "visual_assets", "storyboard_items", 
        "render_jobs", "budget_logs", "monthly_budgets"
    ]
    for table in expected_tables:
        assert table in tables, f"Expected table '{table}' not found in database."

def test_state_machine_transitions():
    # Valid transition: TOPIC_SELECTION -> RESEARCH_IN_PROGRESS
    valid, err = validate_transition(ProjectStatus.TOPIC_SELECTION.value, ProjectStatus.RESEARCH_IN_PROGRESS.value)
    assert valid is True
    assert err is None

    # Invalid transition: TOPIC_SELECTION -> EDITING_RENDERING (skipping research, script, approval)
    invalid, err = validate_transition(ProjectStatus.TOPIC_SELECTION.value, ProjectStatus.EDITING_RENDERING.value)
    assert invalid is False
    assert "Illegal transition" in err

    # Gate checkpoint: SCRIPT_REVIEW can transition to VISUAL_PLANNING or back to SCRIPTING
    valid_approve, _ = validate_transition(ProjectStatus.SCRIPT_REVIEW.value, ProjectStatus.VISUAL_PLANNING.value)
    valid_rewrite, _ = validate_transition(ProjectStatus.SCRIPT_REVIEW.value, ProjectStatus.SCRIPTING.value)
    assert valid_approve is True
    assert valid_rewrite is True

def test_project_crud():
    title = "The Global Semiconductor War"
    pillar = "TECHNOLOGY"
    project = ProjectManager.create_project(title=title, pillar=pillar, target_duration_mins=20)
    
    assert project is not None
    assert project["title"] == title
    assert project["pillar"] == pillar
    assert project["status"] == ProjectStatus.TOPIC_SELECTION.value
    project_id = project["id"]

    # Transition to RESEARCH_IN_PROGRESS
    updated = ProjectManager.update_status(project_id, ProjectStatus.RESEARCH_IN_PROGRESS.value)
    assert updated["status"] == ProjectStatus.RESEARCH_IN_PROGRESS.value

    # Full summary inspection
    summary = ProjectManager.get_project_full_summary(project_id)
    assert summary is not None
    assert summary["project"]["id"] == project_id
    assert "asset_stats" in summary

    # Cleanup
    deleted = ProjectManager.delete_project(project_id)
    assert deleted is True

def test_budget_engine_tracking_and_limit():
    status = BudgetEngine.get_monthly_status()
    assert status["budget_ceiling_usd"] == 50.00
    assert status["total_spent_usd"] >= 0.0

    # Record small valid cost
    record = BudgetEngine.record_cost(
        agent_name="RESEARCH_AGENT",
        operation="SEARCH_TEST",
        model_or_service="GEMINI_FLASH",
        cost_usd=0.05,
        notes="Phase 1 test cost"
    )
    assert record["cost_usd"] == 0.05

    # Check that can_afford rejects costs that exceed the $50 ceiling
    can_afford_huge, reason = BudgetEngine.can_afford(60.00)
    assert can_afford_huge is False
    assert "exceed monthly limit" in reason

    # Attempting to record cost that breaches the ceiling raises BudgetExceededException
    with pytest.raises(BudgetExceededException):
        BudgetEngine.record_cost(
            agent_name="ROGUE_AGENT",
            operation="EXPENSIVE_VIDEO_GEN",
            model_or_service="CLOUD_GPU",
            cost_usd=100.00
        )
