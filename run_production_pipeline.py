import httpx
import time
import json

BASE_URL = "https://docuforge-ai-studio.onrender.com"
PROJECT_ID = "swiss-air-grounding-prod"

def main():
    with httpx.Client(timeout=180.0) as client:
        print("=== STEP 1: VERIFY PROJECT ===")
        res = client.get(f"{BASE_URL}/api/projects/{PROJECT_ID}")
        print("Project check:", res.status_code, res.json().get("project", {}).get("title"))

        print("\n=== STEP 2: RUN 6-PASS EDITORIAL REVIEW ===")
        res_pass = client.post(f"{BASE_URL}/api/editing/run-passes", json={"project_id": PROJECT_ID})
        print("6-Pass Review:", res_pass.status_code, res_pass.json().get("status"))

        print("\n=== STEP 3: START 1080P DOCUMENTARY COMPOSITING ===")
        res_render = client.post(f"{BASE_URL}/api/render/start", json={"project_id": PROJECT_ID})
        r_json = res_render.json()
        print("Render start:", r_json)
        job_id = r_json.get("job_id")

        if not job_id:
            print("Failed to start rendering.")
            return

        print(f"Waiting for render job {job_id}...")
        for i in range(300):
            time.sleep(5)
            try:
                job_res = client.get(f"{BASE_URL}/api/jobs/{job_id}").json()
                job = job_res.get("job", {})
                status = job.get("status")
                pct = job.get("progress_pct")
                msg = job.get("stage_message")
                print(f"[{i*5}s] Progress: {pct}% | Stage: {msg} | Status: {status}")

                if status == "COMPLETED":
                    print("\n>>> 1080p Documentary Render Complete! <<<")
                    break
                elif status == "FAILED":
                    print("\nRendering failed:", job.get("error_message"))
                    return
            except Exception as e:
                print(f"[{i*5}s] Polling retry: {e}")

        print("\n=== STEP 4: ADVANCE TO QC & INSPECT ===")
        client.post(f"{BASE_URL}/api/render/{PROJECT_ID}/advance")
        qc_res = client.post(f"{BASE_URL}/api/qc/run-inspection", json={"project_id": PROJECT_ID})
        print("QC Report:", qc_res.json().get("report", {}).get("summary"))
        client.post(f"{BASE_URL}/api/qc/{PROJECT_ID}/advance")

        print("\n=== STEP 5: GENERATE YOUTUBE THUMBNAILS ===")
        t_res = client.post(f"{BASE_URL}/api/thumbnails/generate", json={"project_id": PROJECT_ID})
        print("Thumbnails generated:", t_res.json().get("status"))

        print("\n=== STEP 6: ASSEMBLE PRODUCTION PACKAGE ZIP ===")
        pkg_res = client.post(f"{BASE_URL}/api/export/package", json={"project_id": PROJECT_ID})
        print("Package ZIP assembly:", pkg_res.json().get("status"))

        print("\n=== STEP 7: SUMMARY & DOWNLOAD URLS ===")
        summary_res = client.get(f"{BASE_URL}/api/export/summary/{PROJECT_ID}").json()
        print("Export Summary:", json.dumps(summary_res, indent=2))

if __name__ == "__main__":
    main()
