import os
import subprocess
import glob
from PIL import Image

PAPER_DIR = "data/media/paper_assets"
os.makedirs(PAPER_DIR, exist_ok=True)

# Generate 2.5-second cinematic motion video clips for each newspaper clipping
def generate_newspaper_video_clips():
    pngs = glob.glob(os.path.join(PAPER_DIR, "paper_*.png"))
    for png in pngs:
        base = os.path.splitext(os.path.basename(png))[0]
        out_mp4 = os.path.join(PAPER_DIR, f"{base}.mp4")
        if not os.path.exists(out_mp4):
            # Dynamic slow zoom in (Ken burns 1.0 -> 1.06) with subtle dark vignette
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", png,
                "-t", "2.5",
                "-vf", "zoompan=z='min(zoom+0.0008,1.06)':d=75:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30,vignette=PI/4,format=yuv420p",
                "-c:v", "libx264", "-preset", "fast", "-crf", "20", out_mp4
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Generated Paper Newspaper Video: {out_mp4}")

if __name__ == "__main__":
    generate_newspaper_video_clips()
