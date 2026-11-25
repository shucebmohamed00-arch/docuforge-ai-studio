"""
DocuForge AI - Main Application Server
"""
import os
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse, HTMLResponse, FileResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from .config import STATIC_DIR, MEDIA_DIR, PREVIEWS_DIR, EXPORTS_DIR, DEBUG
from .database import init_db
from .api.endpoints.projects import (
    list_projects_endpoint,
    create_project_endpoint,
    get_project_endpoint,
    get_project_summary_endpoint,
    transition_project_endpoint,
    delete_project_endpoint,
    restore_swissair_endpoint
)
from .api.endpoints.budget import (
    get_budget_status_endpoint,
    get_budget_breakdown_endpoint,
    get_budget_logs_endpoint,
    record_cost_endpoint
)
from .api.endpoints.jobs import (
    get_job_endpoint,
    list_project_jobs_endpoint
)
from .api.endpoints.topics import (
    discover_topics_endpoint,
    get_project_topics_endpoint,
    select_topic_endpoint
)
from .api.endpoints.research import (
    build_dossier_endpoint,
    get_dossier_endpoint,
    run_fact_check_endpoint
)
from .api.endpoints.scripts import (
    generate_script_endpoint,
    get_script_endpoint,
    update_scene_endpoint,
    approve_script_endpoint
)
from .api.endpoints.visuals import (
    generate_manifest_endpoint,
    get_manifest_endpoint,
    update_beat_endpoint,
    advance_to_footage_discovery_endpoint
)
from .api.endpoints.assets import (
    discover_assets_endpoint,
    get_project_assets_endpoint,
    approve_asset_endpoint,
    reject_asset_endpoint,
    replace_asset_endpoint,
    bulk_approve_endpoint,
    finalize_approvals_endpoint
)
from .api.endpoints.storyboard import (
    compile_storyboard_endpoint,
    get_storyboard_endpoint,
    update_storyboard_item_endpoint,
    approve_storyboard_endpoint
)
from .api.endpoints.audio import (
    synthesize_all_audio_endpoint,
    regenerate_beat_audio_endpoint,
    advance_to_animation_endpoint
)
from .api.endpoints.animations import (
    render_all_animations_endpoint,
    get_project_animations_endpoint,
    advance_to_editing_endpoint
)
from .api.endpoints.render import (
    start_render_endpoint,
    get_render_job_endpoint,
    get_project_export_endpoint,
    advance_to_qc_endpoint
)
from .api.endpoints.thumbnails import (
    generate_thumbnails_endpoint,
    get_project_thumbnails_endpoint
)
from .api.endpoints.qc import (
    run_qc_inspection_endpoint,
    get_qc_report_endpoint,
    advance_qc_endpoint,
    request_repair_endpoint
)
from .api.endpoints.exports import (
    build_export_package_endpoint,
    download_package_zip_endpoint,
    get_export_summary_endpoint
)
from .api.endpoints.editing_passes import (
    run_editing_passes_endpoint,
    get_editing_passes_endpoint
)
from .api.endpoints.timeline import (
    get_multitrack_timeline_endpoint,
    update_shot_specification_endpoint,
    trigger_project_directing_endpoint
)
from .api.endpoints.settings import (
    get_settings_endpoint,
    update_settings_endpoint,
    test_live_connections_endpoint
)

# Initialize database on startup
init_db()

async def health_endpoint(request):
    return JSONResponse({
        "status": "healthy",
        "service": "DocuForge AI Studio Core",
        "version": "1.0.0",
        "database": "sqlite3_initialized"
    })

async def dashboard_index(request):
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>DocuForge AI Studio Initialized</h1><p>Frontend static files loading...</p>")

routes = [
    # Health & Meta
    Route("/api/health", health_endpoint, methods=["GET"]),
    
    # Projects API
    Route("/api/projects", list_projects_endpoint, methods=["GET"]),
    Route("/api/projects", create_project_endpoint, methods=["POST"]),
    Route("/api/projects/restore-swissair", restore_swissair_endpoint, methods=["GET", "POST"]),
    Route("/api/projects/{project_id}", get_project_endpoint, methods=["GET"]),
    Route("/api/projects/{project_id}/summary", get_project_summary_endpoint, methods=["GET"]),
    Route("/api/projects/{project_id}/transition", transition_project_endpoint, methods=["POST"]),
    Route("/api/projects/{project_id}", delete_project_endpoint, methods=["DELETE"]),

    # Budget & Cost API
    Route("/api/budget/status", get_budget_status_endpoint, methods=["GET"]),
    Route("/api/budget/breakdown", get_budget_breakdown_endpoint, methods=["GET"]),
    Route("/api/budget/logs", get_budget_logs_endpoint, methods=["GET"]),
    Route("/api/budget/record", record_cost_endpoint, methods=["POST"]),

    # Jobs API
    Route("/api/jobs/{job_id}", get_job_endpoint, methods=["GET"]),
    Route("/api/jobs/project/{project_id}", list_project_jobs_endpoint, methods=["GET"]),

    # Topics API (Phase 2)
    Route("/api/topics/discover", discover_topics_endpoint, methods=["POST"]),
    Route("/api/topics/project/{project_id}", get_project_topics_endpoint, methods=["GET"]),
    Route("/api/topics/select", select_topic_endpoint, methods=["POST"]),

    # Research & Fact-Checking API (Phase 3)
    Route("/api/research/build-dossier", build_dossier_endpoint, methods=["POST"]),
    Route("/api/research/dossier/{project_id}", get_dossier_endpoint, methods=["GET"]),
    Route("/api/research/fact-check", run_fact_check_endpoint, methods=["POST"]),

    # Script Studio API (Phase 4)
    Route("/api/script/generate", generate_script_endpoint, methods=["POST"]),
    Route("/api/script/{project_id}", get_script_endpoint, methods=["GET"]),
    Route("/api/script/{project_id}/update-scene", update_scene_endpoint, methods=["PUT"]),
    Route("/api/script/{project_id}/approve", approve_script_endpoint, methods=["POST"]),

    # Visual Planning API (Phase 5)
    Route("/api/visuals/generate-manifest", generate_manifest_endpoint, methods=["POST"]),
    Route("/api/visuals/manifest/{project_id}", get_manifest_endpoint, methods=["GET"]),
    Route("/api/visuals/manifest/{manifest_id}", update_beat_endpoint, methods=["PUT"]),
    Route("/api/visuals/{project_id}/advance", advance_to_footage_discovery_endpoint, methods=["POST"]),

    # Footage Discovery & Mandatory Asset Approval API (Phase 6)
    Route("/api/assets/discover", discover_assets_endpoint, methods=["POST"]),
    Route("/api/assets/project/{project_id}", get_project_assets_endpoint, methods=["GET"]),
    Route("/api/assets/{asset_id}/approve", approve_asset_endpoint, methods=["POST"]),
    Route("/api/assets/{asset_id}/reject", reject_asset_endpoint, methods=["POST"]),
    Route("/api/assets/{asset_id}/replace", replace_asset_endpoint, methods=["POST"]),
    Route("/api/assets/bulk-approve", bulk_approve_endpoint, methods=["POST"]),
    Route("/api/assets/{project_id}/finalize", finalize_approvals_endpoint, methods=["POST"]),

    # Storyboard Engine API (Phase 7)
    Route("/api/storyboard/compile", compile_storyboard_endpoint, methods=["POST"]),
    Route("/api/storyboard/{project_id}", get_storyboard_endpoint, methods=["GET"]),
    Route("/api/storyboard/{item_id}", update_storyboard_item_endpoint, methods=["PUT"]),
    Route("/api/storyboard/{project_id}/approve", approve_storyboard_endpoint, methods=["POST"]),

    # Narration & Sound Design API (Phase 8)
    Route("/api/audio/synthesize", synthesize_all_audio_endpoint, methods=["POST"]),
    Route("/api/audio/synthesize-beat", regenerate_beat_audio_endpoint, methods=["POST"]),
    Route("/api/audio/{project_id}/advance", advance_to_animation_endpoint, methods=["POST"]),

    # Animation Studio API (Phase 9)
    Route("/api/animation/render-all", render_all_animations_endpoint, methods=["POST"]),
    Route("/api/animation/project/{project_id}", get_project_animations_endpoint, methods=["GET"]),
    Route("/api/animation/{project_id}/advance", advance_to_editing_endpoint, methods=["POST"]),

    # Video Rendering Pipeline & 6-Pass Creative Editing API (Phase 10 & Directive 27)
    Route("/api/editing/run-passes", run_editing_passes_endpoint, methods=["POST"]),
    Route("/api/editing/passes/{project_id}", get_editing_passes_endpoint, methods=["GET"]),
    Route("/api/timeline/{project_id}", get_multitrack_timeline_endpoint, methods=["GET"]),
    Route("/api/timeline/{project_id}/shots/{shot_id}", update_shot_specification_endpoint, methods=["PUT"]),
    Route("/api/timeline/{project_id}/direct", trigger_project_directing_endpoint, methods=["POST"]),
    Route("/api/render/start", start_render_endpoint, methods=["POST"]),
    Route("/api/render/job/{job_id}", get_render_job_endpoint, methods=["GET"]),
    Route("/api/render/project/{project_id}", get_project_export_endpoint, methods=["GET"]),
    Route("/api/render/{project_id}/advance", advance_to_qc_endpoint, methods=["POST"]),

    # Thumbnails API (Phase 11)
    Route("/api/thumbnails/generate", generate_thumbnails_endpoint, methods=["POST"]),
    Route("/api/thumbnails/project/{project_id}", get_project_thumbnails_endpoint, methods=["GET"]),

    # Quality Control API (Phase 12)
    Route("/api/qc/run-inspection", run_qc_inspection_endpoint, methods=["POST"]),
    Route("/api/qc/report/{project_id}", get_qc_report_endpoint, methods=["GET"]),
    Route("/api/qc/{project_id}/advance", advance_qc_endpoint, methods=["POST"]),
    Route("/api/qc/{project_id}/request-repair", request_repair_endpoint, methods=["POST"]),

    # Export Package API (Phase 13)
    Route("/api/export/package", build_export_package_endpoint, methods=["POST"]),
    Route("/api/export/download/{project_id}", download_package_zip_endpoint, methods=["GET"]),
    Route("/api/export/summary/{project_id}", get_export_summary_endpoint, methods=["GET"]),

    # Studio Settings & Live Connection Diagnostics API
    Route("/api/settings", get_settings_endpoint, methods=["GET"]),
    Route("/api/settings", update_settings_endpoint, methods=["POST"]),
    Route("/api/settings/test-connection", test_live_connections_endpoint, methods=["POST"]),

    # UI Dashboard
    Route("/", dashboard_index, methods=["GET"]),

    # Static Assets & Media Mounts
    Mount("/static", app=StaticFiles(directory=str(STATIC_DIR)), name="static"),
    Mount("/media", app=StaticFiles(directory=str(MEDIA_DIR)), name="media"),
    Mount("/previews", app=StaticFiles(directory=str(PREVIEWS_DIR)), name="previews"),
    Mount("/exports", app=StaticFiles(directory=str(EXPORTS_DIR)), name="exports"),
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True
    )
]

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    init_db()
    try:
        from .core.seeder import seed_default_production_if_needed
        import asyncio
        await asyncio.to_thread(seed_default_production_if_needed)
    except Exception as e:
        import logging
        logging.getLogger("docuforge").warning("Startup seeder notice: %s", e)
    yield

app = Starlette(debug=DEBUG, routes=routes, middleware=middleware, lifespan=lifespan)
