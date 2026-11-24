import httpx
import time
import json
import sys

BASE_URL = "https://docuforge-ai-studio.onrender.com"
PROJECT_ID = "swiss-air-grounding-prod"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def main():
    log("=== DOCUFORGE MASTER RENDERING & RELEASE PIPELINE ===")
    client = httpx.Client(timeout=120.0)

    # 1. Check or start rendering
    log("Checking active render jobs...")
    r_jobs = client.get(f"{BASE_URL}/api/jobs/project/{PROJECT_ID}").json()
    active_job = None
    for j in r_jobs.get("jobs", []):
        if j.get("job_type") == "VIDEO_COMPOSITING" and j.get("status") in ["RUNNING", "QUEUED"]:
            active_job = j.get("id")
            break

    if not active_job:
        log("No active rendering job found. Starting new 1080p compositing job...")
        res = client.post(f"{BASE_URL}/api/render/start", json={"project_id": PROJECT_ID}).json()
        active_job = res.get("job_id")
        log(f"Started job: {active_job}")

    # 2. Poll until render completes
    log(f"Monitoring job {active_job} until completion...")
    start_t = time.time()
    while True:
        try:
            j_res = client.get(f"{BASE_URL}/api/jobs/{active_job}")
            if j_res.status_code == 200:
                job = j_res.json().get("job", {})
                status = job.get("status")
                pct = job.get("progress_pct", 0)
                msg = job.get("stage_message", "")

                # Check clip count
                try:
                    c_cnt = client.get(f"{BASE_URL}/api/animation/project/{PROJECT_ID}").json().get("count", 0)
                except Exception:
                    c_cnt = "?"

                elapsed = int(time.time() - start_t)
                log(f"[{elapsed}s] Status: {status} | {pct}% | Stage: {msg} | Clips: {c_cnt}/124")

                if status == "COMPLETED":
                    log(">>> 1080P DOCUMENTARY COMPOSITED SUCCESSFULLY! <<<")
                    break
                elif status == "FAILED":
                    log(f"Rendering failed: {job.get('error_message')}")
                    sys.exit(1)
            else:
                log(f"HTTP {j_res.status_code} while polling job")
        except Exception as e:
            log(f"Polling retry: {e}")

        time.sleep(12)

    # 3. Advance to QC & Run Inspection
    log("\n=== STEP 4: ADVANCE TO QC & INSPECTION ===")
    try:
        client.post(f"{BASE_URL}/api/render/{PROJECT_ID}/advance")
        qc_res = client.post(f"{BASE_URL}/api/qc/run-inspection", json={"project_id": PROJECT_ID})
        log(f"QC Inspection: {qc_res.status_code}")
        client.post(f"{BASE_URL}/api/qc/{PROJECT_ID}/advance")
    except Exception as e:
        log(f"QC step: {e}")

    # 4. Generate Thumbnails
    log("\n=== STEP 5: GENERATE YOUTUBE THUMBNAILS ===")
    try:
        t_res = client.post(f"{BASE_URL}/api/thumbnails/generate", json={"project_id": PROJECT_ID})
        log(f"Thumbnails: {t_res.status_code}")
    except Exception as e:
        log(f"Thumbnails step: {e}")

    # 5. Assemble Production Package ZIP (Fast ZIP_STORED)
    log("\n=== STEP 6: ASSEMBLE PRODUCTION PACKAGE ZIP ===")
    try:
        pkg_res = client.post(f"{BASE_URL}/api/export/package", json={"project_id": PROJECT_ID})
        log(f"Package ZIP: {pkg_res.status_code} - {pkg_res.text[:100]}")
    except Exception as e:
        log(f"Package step: {e}")

    # 6. Final Summary
    log("\n=== STEP 7: DELIVERABLES SUMMARY ===")
    summary = client.get(f"{BASE_URL}/api/export/summary/{PROJECT_ID}").json()
    log(f"Export summary: {json.dumps(summary, indent=2)}")

    v_stat = client.get(f"{BASE_URL}/api/render/project/{PROJECT_ID}").json()
    log(f"Video export status: {json.dumps(v_stat, indent=2)}")

    log("=== MASTER PIPELINE COMPLETE ===")

if __name__ == "__main__":
    main()
