import os
import sys
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

load_dotenv()
from backend.app.services.runway_service import RunwayService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("runway_chapter_anchors")

OUTPUT_DIR = Path("c:/Users/Shueb/Desktop/youtu/data/media/cinematic_ai_assets")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Hybrid Model Strategy:
# Kling 3.0 Pro (1080p) for high-stakes dramatic centerpiece (Corti press conference)
# Kling 4 Flash (720p) for cinematic narrative anchor scenes
ANCHOR_DISPATCHES = [
    {
        "key": "AIV_04",
        "chapter": 2,
        "filename": "ai_14_referendum_ballot_box.mp4",
        "model": "kling_4_flash",
        "ratio": "1280:720",
        "duration": 5,
        "prompt": "Cinematic macro shot of an antique Swiss referendum wooden ballot box with red painted Swiss cross, voters in wool coats dropping white paper ballots into slot, warm tungsten archival documentary lighting, authentic 1990s texture --ar 16:9"
    },
    {
        "key": "AIV_07",
        "chapter": 3,
        "filename": "ai_15_confidential_contract_signing.mp4",
        "model": "kling_4_flash",
        "ratio": "1280:720",
        "duration": 5,
        "prompt": "Cinematic macro shot of a fountain pen signing a binding legal contract on heavy parchment paper, gold cufflinks gleaming under dim lamp light, thick dossier labeled CONFIDENTIAL SHARE PURCHASE AGREEMENT, dust motes in light beams, chiaroscuro --ar 16:9"
    },
    {
        "key": "AIV_10",
        "chapter": 4,
        "filename": "ai_16_corti_press_conference.mp4",
        "model": "kling3.0_pro",
        "ratio": "1920:1080",
        "duration": 5,
        "prompt": "Cinematic low angle shot of Swiss executive Mario Corti in dark suit speaking into a battery of vintage news microphones, hundreds of camera flashes strobing aggressively in a crowded press conference room, tense documentary atmosphere, 35mm film grain, 8k --ar 16:9"
    },
    {
        "key": "AIV_11",
        "chapter": 5,
        "filename": "ai_17_ubs_boardroom_night.mp4",
        "model": "kling_4_flash",
        "ratio": "1280:720",
        "duration": 5,
        "prompt": "Cinematic dark corporate boardroom at night overlooking Zurich city skyline, silhouettes of three bank directors leaning over financial blueprint documents labeled PROJECT PHOENIX, moody blue corporate lighting, high tension --ar 16:9"
    },
    {
        "key": "AIV_13",
        "chapter": 6,
        "filename": "ai_18_paradeplatz_protest.mp4",
        "model": "kling_4_flash",
        "ratio": "1280:720",
        "duration": 5,
        "prompt": "Authentic documentary handheld tracking shot outside UBS headquarters Zurich Paradeplatz, angry crowd of grounded airline workers in uniforms and citizens holding protest signs in autumn rain, flashbulbs popping --ar 16:9"
    }
]

def main():
    rs = RunwayService()
    if not rs.is_configured():
        logger.error("RunwayService is not configured. Check RUNWAY_API_KEY.")
        sys.exit(1)

    logger.info("RunwayService connected! Starting dispatch of anchor scenes...")
    active_tasks = {}

    for item in ANCHOR_DISPATCHES:
        out_file = OUTPUT_DIR / item["filename"]
        if out_file.exists() and out_file.stat().st_size > 500000:
            logger.info(f"Skipping {item['key']} ({item['filename']}) - already exists ({out_file.stat().st_size} bytes).")
            continue

        logger.info(f"Dispatching {item['key']} (Chapter {item['chapter']}) via model '{item['model']}' ({item['ratio']})...")
        res = rs.generate_text_to_video(
            prompt=item["prompt"],
            model=item["model"],
            duration=item["duration"],
            ratio=item["ratio"]
        )
        if res.get("status") == "submitted":
            task_id = res["task_id"]
            logger.info(f"-> Submitted {item['key']} with task_id: {task_id}")
            active_tasks[task_id] = (item, out_file)
        else:
            logger.error(f"-> Failed to submit {item['key']}: {res}")

    if not active_tasks:
        logger.info("All anchor videos already generated and downloaded!")
        return

    logger.info(f"Monitoring {len(active_tasks)} active Runway video generation tasks...")
    completed = set()

    start_time = time.time()
    while len(completed) < len(active_tasks):
        for task_id, (item, out_file) in active_tasks.items():
            if task_id in completed:
                continue
            status = rs.check_task_status(task_id)
            stat = status.get("status")
            logger.info(f"Task {task_id} [{item['key']} - {item['model']}]: {stat}")

            if stat in ("SUCCEEDED", "COMPLETED"):
                outputs = status.get("output", [])
                if outputs:
                    video_url = outputs[0]
                    logger.info(f"Downloading {item['key']} from {video_url} to {out_file}...")
                    ok = rs.download_video(video_url, str(out_file))
                    if ok and out_file.exists():
                        size_mb = out_file.stat().st_size / (1024 * 1024)
                        logger.info(f"SUCCESS: {item['key']} saved ({size_mb:.2f} MB)")
                        completed.add(task_id)
                    else:
                        logger.error(f"Failed to download video from {video_url}")
                else:
                    logger.error(f"No output in status: {status}")
                    completed.add(task_id)
            elif stat in ("FAILED", "CANCELLED"):
                logger.error(f"Task {task_id} failed: {status.get('failure')}")
                completed.add(task_id)

        if len(completed) < len(active_tasks):
            time.sleep(10)

    logger.info("All Runway dispatches finished successfully!")

if __name__ == "__main__":
    main()
