"""
DocuForge AI - API Integration Tests
Tests /api/health, /api/projects, /api/budget endpoints.
"""
from starlette.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "DocuForge AI Studio Core"

def test_api_project_lifecycle():
    # 1. Create Project
    payload = {
        "title": "The Collapse of Enron: Accounting Fraud",
        "pillar": "BUSINESS",
        "target_duration_mins": 25
    }
    create_res = client.post("/api/projects", json=payload)
    assert create_res.status_code == 201
    proj = create_res.json()["project"]
    proj_id = proj["id"]
    assert proj["title"] == payload["title"]
    assert proj["status"] == "TOPIC_SELECTION"

    # 2. Get Project
    get_res = client.get(f"/api/projects/{proj_id}")
    assert get_res.status_code == 200
    assert get_res.json()["project"]["id"] == proj_id

    # 3. Transition Status
    trans_res = client.post(f"/api/projects/{proj_id}/transition", json={"target_status": "RESEARCH_IN_PROGRESS"})
    assert trans_res.status_code == 200
    assert trans_res.json()["project"]["status"] == "RESEARCH_IN_PROGRESS"

    # 4. Summary
    sum_res = client.get(f"/api/projects/{proj_id}/summary")
    assert sum_res.status_code == 200
    assert sum_res.json()["summary"]["project"]["id"] == proj_id

    # 5. Delete Project
    del_res = client.delete(f"/api/projects/{proj_id}")
    assert del_res.status_code == 200

def test_api_budget_endpoints():
    res = client.get("/api/budget/status")
    assert res.status_code == 200
    b = res.json()["budget"]
    assert b["budget_ceiling_usd"] == 50.00
    assert "remaining_usd" in b

    # Test record endpoint
    record_res = client.post("/api/budget/record", json={
        "agent_name": "API_TEST",
        "operation": "UNIT_TEST",
        "model_or_service": "TEST_MOCK",
        "cost_usd": 0.01,
        "notes": "Testing record endpoint"
    })
    assert record_res.status_code == 201
    assert record_res.json()["status"] == "success"

    # Test breakdown endpoint
    breakdown_res = client.get("/api/budget/breakdown")
    assert breakdown_res.status_code == 200
    assert "breakdown" in breakdown_res.json()
