import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()
from backend.app.services.runway_service import RunwayService

srv = RunwayService()

tasks = [
    ("Shot 05 (Fuel Cutoff)", "2cd42b3a-a8d7-420a-ba6f-04b54eddf6e7", "data/media/cinematic_ai_assets/ai_07_fuel_hose_cutoff.mp4"),
    ("Shot 08 (Departure Board)", "c49a910f-2a91-42fc-ba32-8186f2d984b4", "data/media/cinematic_ai_assets/ai_09_cancelled_departure_board.mp4")
]

pending = list(tasks)
print("Monitoring Runway renders...")

start_time = time.time()
while pending and time.time() - start_time < 600:
    for item in list(pending):
        name, tid, out_file = item
        res = srv.check_task_status(tid)
        status = res.get("status")
        print(f"[{int(time.time() - start_time)}s] {name}: {status}")

        if status == "SUCCEEDED":
            out_url = res.get("output", [])[0]
            print(f"Downloading {name} from {out_url}...")
            srv.download_video(out_url, out_file)
            print(f"DONE: {name} saved to {out_file} ({os.path.getsize(out_file)} bytes)")
            pending.remove(item)
        elif status in ("FAILED", "CANCELLED"):
            print(f"ERROR: {name} failed: {res.get('failure')}")
            pending.remove(item)

    if pending:
        time.sleep(10)

print("All pending Runway renders processed!")
