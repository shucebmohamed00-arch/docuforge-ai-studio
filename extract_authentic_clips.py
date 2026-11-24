import subprocess
import os
from pathlib import Path

BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
ARCHIVE_DIR = BASE_DIR / "data" / "media"
CLIPS_DIR = ARCHIVE_DIR / "authentic_clips"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)

srf_src = ARCHIVE_DIR / "archival_srf_grounding.mp4.webm"
rsi_src = ARCHIVE_DIR / "archival_rsi_grounding.mp4.webm"
kloten_src = ARCHIVE_DIR / "archival_kloten_md11.mp4.mkv"

print("Extracting 30 SRF grounding archival clips...")
for i in range(30):
    start = i * 9.5
    out = CLIPS_DIR / f"srf_clip_{i+1:02d}.mp4"
    cmd = [
        "ffmpeg", "-y", "-ss", str(start), "-i", str(srf_src),
        "-t", "10",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,eq=contrast=1.06:brightness=-0.01",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-an",
        str(out)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

print("Extracting 18 RSI grounding archival clips...")
for i in range(18):
    start = i * 8.0
    out = CLIPS_DIR / f"rsi_clip_{i+1:02d}.mp4"
    cmd = [
        "ffmpeg", "-y", "-ss", str(start), "-i", str(rsi_src),
        "-t", "9",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,eq=contrast=1.06:brightness=-0.01",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-an",
        str(out)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

print("Extracting 10 Kloten MD-11 archival clips...")
for i in range(10):
    start = i * 9.5
    out = CLIPS_DIR / f"kloten_clip_{i+1:02d}.mp4"
    cmd = [
        "ffmpeg", "-y", "-ss", str(start), "-i", str(kloten_src),
        "-t", "10",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,eq=contrast=1.06:brightness=-0.01",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-an",
        str(out)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

print(f"Total authentic clips extracted: {len(os.listdir(CLIPS_DIR))}")
