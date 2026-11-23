"""
DocuForge AI - Quality Control API Endpoints
"""
from starlette.requests import Request
from starlette.responses import JSONResponse
from ...agents.quality_control import QualityControlAgent
from ...models.project import ProjectManager

async def run_qc_inspection_endpoint(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    project_id = data.get("project_id")
    if not project_id:
        return JSONResponse({"status": "error", "message": "project_id is required"}, status_code=400)

    try:
        report = QualityControlAgent.inspect_project(project_id)
        return JSONResponse({"status": "success", "report": report})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def get_qc_report_endpoint(request: Request) -> JSONResponse:
    project_id = request.path_params.get("project_id")
    report = QualityControlAgent.get_report(project_id)
    if not report:
        return JSONResponse({"status": "error", "message": f"No QC report found for project '{project_id}'"}, status_code=404)
    return JSONResponse({"status": "success", "report": report})

async def advance_qc_endpoint(request: Request) -> JSONResponse:
    """
    Enforces the mandatory QC completion gate:
    Only advances the project if the documentary passed all QC checks.
    """
    project_id = request.path_params.get("project_id")
    report = QualityControlAgent.get_report(project_id)

    # If no report on disk, run inspection first
    if not report:
        try:
            report = QualityControlAgent.inspect_project(project_id)
        except Exception as e:
            return JSONResponse({"status": "error", "message": f"Could not execute QC inspection: {e}"}, status_code=500)

    if not report.get("passed", False):
        failures = [c["details"] for c in report.get("checks", []) if c.get("status") == "FAIL"]
        return JSONResponse({
            "status": "error",
            "message": "Quality Control inspection FAILED. Mandatory gate prohibits export until issues are repaired.",
            "verdict": "FAILED",
            "score": report.get("overall_score", 0),
            "failures": failures,
            "repair_recommendations": report.get("repair_recommendations", [])
        }, status_code=400)

    try:
        updated = ProjectManager.update_status(project_id, "EXPORT_READY")
        return JSONResponse({
            "status": "success",
            "message": f"QC Certification PASSED ({report.get('overall_score')}%). Advanced to Stage 13: Final Export Package.",
            "project": updated,
            "report_summary": report.get("summary")
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

async def request_repair_endpoint(request: Request) -> JSONResponse:
    """
    Transitions project back to EDITING_RENDERING or FOOTAGE_DISCOVERY for remediation.
    """
    project_id = request.path_params.get("project_id")
    try:
        updated = ProjectManager.update_status(project_id, "EDITING_RENDERING")
        return JSONResponse({
            "status": "success",
            "message": "Project returned to Video Rendering for repair and asset adjustments.",
            "project": updated
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
