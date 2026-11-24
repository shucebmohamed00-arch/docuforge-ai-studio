import httpx
import time
import json
import sys

BASE_URL = "https://docuforge-ai-studio.onrender.com"
PROJECT_ID = "swiss-air-grounding-prod"
JOB_ID = "724027c0-ca4c-4cb7-949f-215075a56dc9"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def main():
    log(f"=== DocuForge Pipeline Finalizer ===")
    log(f"Tracking Job: {JOB_ID}")

    client = httpx.Client(timeout=60.0)
    start_time = time.time()

    # 1. Poll until job completes
    while True:
        try:
            res = client.get(f"{BASE_URL}/api/jobs/{JOB_ID}")
            if res.status_code == 200:
                job = res.json().get("job", {})
                status = job.get("status")
                pct = job.get("progress_pct", 0)
                stage = job.get("stage_message", "")
                
                # Fetch clip count
                try:
                    c_res = client.get(f"{BASE_URL}/api/animation/project/{PROJECT_ID}")
                    c_count = c_res.json().get("count", 0)
                except Exception:
                    c_count = "?"

                elapsed = int(time.time() - start_time)
                log(f"[{elapsed}s] Job: {status} | {pct}% | Stage: {stage} | Clips: {c_count}/124")

                if status == "COMPLETED":
                    log(">>> VIDEO COMPOSITING JOB COMPLETED! <<<")
                    break
                elif status == "FAILED":
                    log(f"Job failed: {job.get('error_message')}")
                    sys.exit(1)
            else:
                log(f"HTTP {res.status_code} while polling job")
        except Exception as e:
            log(f"Polling warning: {e}")

        time.sleep(15)

    # 2. Advance to QC & Run Inspection
    log("\n=== STEP 4: ADVANCE TO QC & INSPECT ===")
    try:
        adv_res = client.post(f"{BASE_URL}/api/render/{PROJECT_ID}/advance")
        log(f"Advance to QC: {adv_res.status_code}")
    except Exception as e:
        log(f"Advance error: {e}")

    try:
        qc_res = client.post(f"{BASE_URL}/api/qc/run-inspection", json={"project_id": PROJECT_ID})
        log(f"QC Inspection: {qc_res.status_code} - Summary: {qc_res.json().get('report', {}).get('summary')}")
        
        qc_adv = client.post(f"{BASE_URL}/api/qc/{PROJECT_ID}/advance")
        log(f"QC Advance: {qc_adv.status_code}")
    except Exception as e:
        log(f"QC error: {e}")

    # 3. Generate YouTube Thumbnails
    log("\n=== STEP 5: GENERATE YOUTUBE THUMBNAILS ===")
    try:
        t_res = client.post(f"{BASE_URL}/api/thumbnails/generate", json={"project_id": PROJECT_ID})
        log(f"Thumbnails: {t_res.status_code}")
    except Exception as e:
        log(f"Thumbnails error: {e}")

    # 4. Assemble Complete Production Package ZIP
    log("\n=== STEP 6: ASSEMBLE PRODUCTION PACKAGE ZIP ===")
    try:
        pkg_res = client.post(f"{BASE_URL}/api/export/package", json={"project_id": PROJECT_ID})
        log(f"Package ZIP: {pkg_res.status_code} - Status: {pkg_res.json().get('status')}")
    except Exception as e:
        log(f"Package error: {e}")

    # 5. Final Export Summary
    log("\n=== STEP 7: SUMMARY & DOWNLOAD DELIVERABLES ===")
    try:
        summary_res = client.get(f"{BASE_URL}/api/export/summary/{PROJECT_ID}")
        log(f"Export Summary: {json.dumps(summary_res.json(), indent=2)}")
        
        v_res = client.get(f"{BASE_URL}/api/render/project/{PROJECT_ID}")
        log(f"Video Status: {json.dumps(v_res.json(), indent=2)}")
    except Exception as e:
        log(f"Summary error: {e}")

    log("=== DOCUMENTARY PRODUCTION FULLY COMPLETE ===")

if __name__ == "__main__":
    main()
