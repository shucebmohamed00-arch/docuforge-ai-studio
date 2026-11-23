"""
DocuForge AI - Budget API Endpoints
"""
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...core.budget_engine import BudgetEngine, BudgetExceededException

async def get_budget_status_endpoint(request: Request) -> JSONResponse:
    month = request.query_params.get("month")
    status = BudgetEngine.get_monthly_status(month)
    return JSONResponse({"status": "success", "budget": status})

async def get_budget_breakdown_endpoint(request: Request) -> JSONResponse:
    month = request.query_params.get("month")
    breakdown = BudgetEngine.get_agent_breakdown(month)
    return JSONResponse({"status": "success", "breakdown": breakdown})

async def get_budget_logs_endpoint(request: Request) -> JSONResponse:
    limit = int(request.query_params.get("limit", 50))
    logs = BudgetEngine.get_recent_logs(limit)
    return JSONResponse({"status": "success", "count": len(logs), "logs": logs})

async def record_cost_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    agent_name = data.get("agent_name", "UNKNOWN")
    operation = data.get("operation", "GENERAL")
    model_or_service = data.get("model_or_service", "MOCK")
    cost_usd = float(data.get("cost_usd", 0.0))
    project_id = data.get("project_id")
    tokens_in = int(data.get("tokens_in", 0))
    tokens_out = int(data.get("tokens_out", 0))
    notes = data.get("notes", "")

    try:
        record = BudgetEngine.record_cost(
            agent_name=agent_name,
            operation=operation,
            model_or_service=model_or_service,
            cost_usd=cost_usd,
            project_id=project_id,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            notes=notes
        )
        return JSONResponse({"status": "success", "record": record}, status_code=201)
    except BudgetExceededException as e:
        return JSONResponse({"status": "blocked", "reason": str(e)}, status_code=403)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
