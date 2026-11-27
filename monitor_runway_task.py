import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()
from backend.app.services.runway_service import RunwayService

task_id = "2cd42b3a-a8d7-420a-ba6f-04b54eddf6e7"
output_path = os.path.abspath("data/media/cinematic_ai_assets/ai_07_fuel_hose_cutoff.mp4")

srv = RunwayService()
print(f"Monitoring Runway task {task_id} -> {output_path}...")

success = srv.wait_and_download(task_id=task_id, output_path=output_path, timeout_sec=600)
if success:
    print(f"SUCCESS: Video downloaded to {output_path} (Size: {os.path.getsize(output_path)} bytes)")
else:
    print("FAILED or TIMED OUT")
