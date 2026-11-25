import os
import subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
PAPER_DIR = BASE_DIR / "data" / "media" / "paper_assets"
ADV_DIR = BASE_DIR / "data" / "media" / "advanced_25d"

ADV_DIR.mkdir(parents=True, exist_ok=True)

def create_rubber_stamp_img(stamp_text: str, sub_text: str = "", stamp_color: tuple = (215, 25, 25)) -> Image.Image:
    """
    Creates an authentic distressed red ink rubber stamp graphic with double borders.
    """
    SW, SH = 640, 220
    img = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Outer distressed box
    draw.rectangle([12, 12, SW - 12, SH - 12], outline=stamp_color + (240,), width=8)
    # Inner border
    draw.rectangle([24, 24, SW - 24, SH - 24], outline=stamp_color + (220,), width=3)

    font_stamp = None
    font_sub = None
    for fpath in ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"]:
        if os.path.exists(fpath):
            font_stamp = ImageFont.truetype(fpath, 60)
            font_sub = ImageFont.truetype(fpath, 26)
            break
    if not font_stamp:
        font_stamp = font_sub = ImageFont.load_default()

    # Main Stamp Text
    draw.text((SW // 2, SH // 2 - (18 if sub_text else 0)), stamp_text.upper(), font=font_stamp, fill=stamp_color + (250,), anchor="mm")
    if sub_text:
        draw.text((SW // 2, SH // 2 + 48), sub_text.upper(), font=font_sub, fill=stamp_color + (220,), anchor="mm")

    # Add rubber ink grit / distress
    grit = np.random.randint(0, 255, (SH, SW), dtype=np.uint8)
    grit_mask = grit < 45  # 18% eroded pixels
    arr = np.array(img)
    arr[grit_mask, 3] = 0

    return Image.fromarray(arr)

def render_document_with_stamp_slam(
    src_video: Path,
    out_mp4: Path,
    stamp_text: str,
    sub_text: str,
    slam_sec: float = 1.2,
    total_dur: float = 3.2,
    stamp_angle: float = -14.0
):
    """
    Takes an existing document/highlighter video and overlays an authentic
    kinetic rubber stamp slam with camera shake and impact flash!
    """
    W, H = 1920, 1080
    FPS = 30
    total_frames = int(total_dur * FPS)
    slam_frame = int(slam_sec * FPS)

    stamp_img = create_rubber_stamp_img(stamp_text, sub_text)
    stamp_rotated = stamp_img.rotate(stamp_angle, expand=True, resample=Image.BICUBIC)

    # Extract source video frames
    temp_dir = ADV_DIR / f"temp_doc_{out_mp4.stem}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    cmd_extract = [
        "ffmpeg", "-y", "-i", str(src_video),
        "-t", str(total_dur),
        "-r", str(FPS),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080:(in_w-1920)/2:(in_h-1080)/2",
        str(temp_dir / "src_%04d.png")
    ]
    subprocess.run(cmd_extract, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    print(f"Compositing rubber stamp slam for {out_mp4.name}...")

    # Target position for stamp (center-right)
    tx, ty = W // 2 + 100, H // 2 - 30

    for f_idx in range(total_frames):
        src_f = temp_dir / f"src_{f_idx+1:04d}.png"
        if src_f.exists():
            frame = Image.open(src_f).convert("RGBA")
        else:
            frame = Image.new("RGBA", (W, H), (240, 238, 230, 255))

        # Check if stamp should be visible
        if f_idx >= slam_frame:
            frames_since_slam = f_idx - slam_frame

            if frames_since_slam == 0:
                # Frame of impact: giant scale 1.8x, motion blur, white flash
                scale = 1.8
                alpha_mult = 0.7
                shake_x = np.random.randint(-15, 15)
                shake_y = np.random.randint(-15, 15)
            elif frames_since_slam == 1:
                # Rebound frame
                scale = 1.15
                alpha_mult = 0.95
                shake_x = np.random.randint(-8, 8)
                shake_y = np.random.randint(-8, 8)
            elif frames_since_slam == 2:
                scale = 0.98
                alpha_mult = 1.0
                shake_x = np.random.randint(-4, 4)
                shake_y = np.random.randint(-4, 4)
            else:
                # Settle at 1.0x with subtle breathing
                scale = 1.0 + (f_idx - slam_frame) * 0.001
                alpha_mult = 1.0
                shake_x = 0
                shake_y = 0

            # Scale stamp
            sw = int(stamp_rotated.width * scale)
            sh = int(stamp_rotated.height * scale)
            cur_stamp = stamp_rotated.resize((sw, sh), Image.LANCZOS)

            # Paste stamp with shake
            px = int(tx - sw // 2 + shake_x)
            py = int(ty - sh // 2 + shake_y)
            frame.paste(cur_stamp, (px, py), cur_stamp)

            # Impact flash on frame 0
            if frames_since_slam <= 1:
                flash = Image.new("RGBA", (W, H), (255, 255, 255, 45 if frames_since_slam == 0 else 20))
                frame.paste(flash, (0, 0), flash)

        # Save composited frame
        frame.convert("RGB").save(temp_dir / f"comp_{f_idx:04d}.png")

    # Encode with FFmpeg
    cmd_enc = [
        "ffmpeg", "-y",
        "-r", str(FPS),
        "-i", str(temp_dir / "comp_%04d.png"),
        "-t", str(total_dur),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-an",
        str(out_mp4)
    ]
    subprocess.run(cmd_enc, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Cleanup temp
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"Successfully rendered Document Stamp Slam: {out_mp4.name}")

if __name__ == "__main__":
    # Test on NZZ 17.8B Debt Newspaper
    nzz_src = PAPER_DIR / "paper_highlighter_nzz_debts.mp4"
    if nzz_src.exists():
        render_document_with_stamp_slam(
            src_video=nzz_src,
            out_mp4=ADV_DIR / "doc_01_nzz_audit_stamp.mp4",
            stamp_text="INSOLVENCY AUDIT",
            sub_text="17.8 BILLION DEBT VERIFIED",
            slam_sec=1.1,
            total_dur=3.2,
            stamp_angle=-12.0
        )

    # Test on Job Loss Document
    job_src = PAPER_DIR / "paper_highlighter_job_loss.mp4"
    if job_src.exists():
        render_document_with_stamp_slam(
            src_video=job_src,
            out_mp4=ADV_DIR / "doc_02_job_loss_stamp.mp4",
            stamp_text="FLEET GROUNDED",
            sub_text="2,650 POSITIONS TERMINATED",
            slam_sec=1.1,
            total_dur=3.2,
            stamp_angle=10.0
        )
