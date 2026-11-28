import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

load_dotenv()
from backend.app.services.runway_service import RunwayService

rs = RunwayService()
task_id = "85cf09e7-bd74-4210-a1e2-696e615eea31"
out_file = Path("data/media/cinematic_ai_assets/ai_16_corti_press_conference.mp4")

print(f"Waiting for AIV_10 (task_id: {task_id}) to complete...")
success = rs.wait_and_download(task_id, str(out_file), timeout_sec=600)
if success and out_file.exists():
    print(f"AIV_10 downloaded successfully! Size: {out_file.stat().st_size / (1024*1024):.2f} MB")
else:
    print(f"Failed to download AIV_10 or timed out.")
