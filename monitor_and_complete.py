import httpx
import time
import json
import sys

BASE_URL = "https://docuforge-ai-studio.onrender.com"
PROJECT_ID = "swiss-air-grounding-prod"
JOB_ID = "449933e7-0555-4d6c-83f8-ed74731a72fb"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def main():
    log(f"=== DocuForge Autonomous Production Pipeline Monitor ===")
    log(f"Target Project: {PROJECT_ID}")
    log(f"Active Job ID:  {JOB_ID}")

    client = httpx.Client(timeout=45.0)

    # 1. Poll until render job completes
    consecutive_errors = 0
    start_time = time.time()

    while True:
        try:
            # Keep Render server awake & get job status
            res = client.get(f"{BASE_URL}/api/jobs/{JOB_ID}")
            if res.status_code == 200:
                consecutive_errors = 0
                job_data = res.json().get("job", {})
                status = job_data.get("status")
                pct = job_data.get("progress_pct", 0)
                stage_msg = job_data.get("stage_message", "")
                err = job_data.get("error_message")

                # Also get current clip count
                try:
                    c_res = client.get(f"{BASE_URL}/api/animation/project/{PROJECT_ID}")
                    c_count = c_res.json().get("count", 0)
                except Exception:
                    c_count = "?"

                elapsed = int(time.time() - start_time)
                log(f"[{elapsed}s] Job Status: {status} | Progress: {pct}% | Stage: {stage_msg} | Clips: {c_count}/124")

                if status == "COMPLETED":
                    log(">>> VIDEO COMPOSITING JOB COMPLETED SUCCESSFULLY! <<<")
                    break
                elif status == "FAILED":
                    log(f"FATAL: Rendering failed with error: {err}")
                    sys.exit(1)
            else:
                log(f"HTTP {res.status_code} from /api/jobs/{JOB_ID}")
        except Exception as e:
            consecutive_errors += 1
            log(f"Polling error ({consecutive_errors}): {e}")
            if consecutive_errors > 15:
                log("Too many consecutive errors. Exiting.")
                sys.exit(1)

        time.sleep(12)

    # 2. Advance to QC (Phase 11)
    log("\n=== STEP 4: ADVANCE TO QUALITY CONTROL ===")
    try:
        r_adv = client.post(f"{BASE_URL}/api/render/{PROJECT_ID}/advance")
        log(f"Advance to QC response: {r_adv.status_code} {r_adv.text}")
    except Exception as e:
        log(f"Error advancing to QC: {e}")

    log("Running automated 10-point QC inspection...")
    try:
        qc_res = client.post(f"{BASE_URL}/api/qc/run-inspection", json={"project_id": PROJECT_ID})
        log(f"QC Inspection: {qc_res.status_code} - Summary: {qc_res.json().get('report', {}).get('summary')}")
        
        # Advance through QC gate
        qc_adv = client.post(f"{BASE_URL}/api/qc/{PROJECT_ID}/advance")
        log(f"Advance through QC gate: {qc_adv.status_code} {qc_adv.text}")
    except Exception as e:
        log(f"Error in QC execution: {e}")

    # 3. Generate YouTube Thumbnails (Phase 12)
    log("\n=== STEP 5: GENERATE YOUTUBE THUMBNAILS ===")
    try:
        t_res = client.post(f"{BASE_URL}/api/thumbnails/generate", json={"project_id": PROJECT_ID})
        log(f"Thumbnails response: {t_res.status_code} {t_res.text}")
    except Exception as e:
        log(f"Error generating thumbnails: {e}")

    # 4. Assemble Complete Production Package ZIP (Phase 13)
    log("\n=== STEP 6: ASSEMBLE PRODUCTION PACKAGE ZIP ===")
    try:
        pkg_res = client.post(f"{BASE_URL}/api/export/package", json={"project_id": PROJECT_ID})
        log(f"Package ZIP assembly: {pkg_res.status_code} {pkg_res.text}")
    except Exception as e:
        log(f"Error assembling package: {e}")

    # 5. Final Export Summary & Deliverables Verification
    log("\n=== STEP 7: FINAL DELIVERABLES SUMMARY ===")
    try:
        summary_res = client.get(f"{BASE_URL}/api/export/summary/{PROJECT_ID}")
        summary = summary_res.json()
        log(f"Export Summary: {json.dumps(summary, indent=2)}")

        # Also verify video export endpoint
        v_res = client.get(f"{BASE_URL}/api/render/project/{PROJECT_ID}")
        log(f"Video Export Status: {json.dumps(v_res.json(), indent=2)}")
    except Exception as e:
        log(f"Error fetching summary: {e}")

    log("=== PIPELINE EXECUTION COMPLETE ===")

if __name__ == "__main__":
    main()
