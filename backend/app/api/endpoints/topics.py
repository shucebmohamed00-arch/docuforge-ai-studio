"""
DocuForge AI - Topics API Endpoints
"""
import json
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...agents.topic_discovery import TopicDiscoveryAgent
from ...database import get_connection

async def discover_topics_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)
    
    project_id = data.get("project_id")
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    try:
        result = TopicDiscoveryAgent.discover_five_candidates(project_id)
        return JSONResponse({"status": "success", "result": result})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def get_project_topics_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM topics WHERE project_id = ? ORDER BY total_score DESC", (project_id,))
        rows = cursor.fetchall()
        topics = []
        for r in rows:
            d = dict(r)
            d["hooks"] = json.loads(d.get("hooks_json") or "[]")
            d["title_variants"] = json.loads(d.get("title_variants_json") or "[]")
            topics.append(d)
        return JSONResponse({"status": "success", "count": len(topics), "topics": topics})
    finally:
        conn.close()

async def select_topic_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)
    
    project_id = data.get("project_id")
    topic_id = data.get("topic_id")

    if not project_id or not topic_id:
        return JSONResponse({"status": "error", "message": "project_id and topic_id are required"}, status_code=400)

    try:
        res = TopicDiscoveryAgent.select_topic(project_id, topic_id)
        return JSONResponse(res)
    except ValueError as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
