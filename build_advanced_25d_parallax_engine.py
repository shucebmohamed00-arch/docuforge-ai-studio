import os
import subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
PHOTO_DIR = BASE_DIR / "data" / "media" / "documentary_photos"
ADV_DIR = BASE_DIR / "data" / "media" / "advanced_25d"
CLIPS_DIR = BASE_DIR / "data" / "media" / "authentic_clips"

ADV_DIR.mkdir(parents=True, exist_ok=True)

def create_circular_cutout_card(
    face_src: Path,
    bg_video: Path,
    out_mp4: Path,
    title_text: str,
    role_text: str,
    badge_text: str,
    duration: float = 3.2,
    accent_color: tuple = (212, 175, 55)
):
    """
    Renders an advanced 2.5D Parallax Documentary Card (MagnatesMedia Style):
    - Layer 0: Dark vignette canvas + slow panning blurred archival background
    - Layer 1: Radial golden glow halo
    - Layer 2: Deep 3D drop shadow
    - Layer 3: Subject cutout framed in a dynamic brushed gold / metallic ring
    - Layer 4: Kinetic lower-third badge with accent borders
    - Layer 5: Film grain / dust particles
    """
    W, H = 1920, 1080
    FPS = 30
    total_frames = int(duration * FPS)

    # 1. Extract and prepare face image
    face_raw = Image.open(face_src).convert("RGBA")
    fw, fh = face_raw.size
    min_dim = min(fw, fh)
    left = (fw - min_dim) // 2
    top = (fh - min_dim) // 2
    face_square = face_raw.crop((left, top, left + min_dim, top + min_dim))
    
    portrait_size = 560
    face_resized = face_square.resize((portrait_size, portrait_size), Image.LANCZOS)

    # Circular mask with smooth anti-aliased edge
    mask = Image.new("L", (portrait_size, portrait_size), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse([4, 4, portrait_size - 4, portrait_size - 4], fill=255)
    
    # Gold border ring
    ring_img = Image.new("RGBA", (portrait_size + 24, portrait_size + 24), (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(ring_img)
    rdraw.ellipse([0, 0, portrait_size + 23, portrait_size + 23], fill=accent_color)
    rdraw.ellipse([8, 8, portrait_size + 15, portrait_size + 15], fill=(0, 0, 0, 0))

    # Inner circular portrait
    portrait_composite = Image.new("RGBA", (portrait_size + 24, portrait_size + 24), (0, 0, 0, 0))
    portrait_composite.paste(face_resized, (12, 12), mask)
    portrait_composite.paste(ring_img, (0, 0), ring_img)

    # Deep drop shadow for portrait
    shadow_pad = 60
    shadow_img = Image.new("RGBA", (portrait_size + 24 + shadow_pad * 2, portrait_size + 24 + shadow_pad * 2), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_img)
    sdraw.ellipse([shadow_pad + 15, shadow_pad + 25, shadow_pad + portrait_size + 15, shadow_pad + portrait_size + 25], fill=(0, 0, 0, 190))
    shadow_blurred = shadow_img.filter(ImageFilter.GaussianBlur(28))

    # Fonts
    font_title = None
    font_sub = None
    font_badge = None
    for fpath in ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"]:
        if os.path.exists(fpath):
            font_title = ImageFont.truetype(fpath, 64)
            font_sub = ImageFont.truetype(fpath, 28)
            font_badge = ImageFont.truetype(fpath, 22)
            break
    if not font_title:
        font_title = font_sub = font_badge = ImageFont.load_default()

    # Pre-render background video frames using FFmpeg
    temp_frames_dir = ADV_DIR / f"temp_{out_mp4.stem}"
    temp_frames_dir.mkdir(parents=True, exist_ok=True)

    bg_raw_pngs = ADV_DIR / f"bg_{out_mp4.stem}_%04d.jpg"
    cmd_bg = [
        "ffmpeg", "-y", "-ss", "0.5", "-t", str(duration),
        "-i", str(bg_video),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080:(in_w-1920)/2:(in_h-1080)/2,gblur=sigma=18,format=yuv420p",
        "-r", str(FPS), str(bg_raw_pngs)
    ]
    subprocess.run(cmd_bg, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Render animated 2.5D composite frames
    print(f"Compositing {total_frames} 2.5D parallax frames for {out_mp4.name}...")

    # Portrait anchor position
    cx_base, cy_base = 560, 480

    for f_idx in range(total_frames):
        t = f_idx / float(FPS)
        progress = f_idx / float(total_frames)

        # 1. Background frame
        bg_file = ADV_DIR / f"bg_{out_mp4.stem}_{f_idx+1:04d}.jpg"
        if bg_file.exists():
            frame = Image.open(bg_file).convert("RGBA")
        else:
            frame = Image.new("RGBA", (W, H), (12, 16, 22, 255))

        # Dark overlay with radial vignette for contrast
        darkness = Image.new("RGBA", (W, H), (8, 12, 18, 175))
        frame.paste(darkness, (0, 0), darkness)

        # 2. Radial warm glow behind character
        glow_rad = int(380 + np.sin(progress * np.pi) * 40)
        glow_img = Image.new("RGBA", (glow_rad * 2, glow_rad * 2), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow_img)
        gdraw.ellipse([0, 0, glow_rad * 2, glow_rad * 2], fill=(accent_color[0], accent_color[1], accent_color[2], 42))
        glow_blurred = glow_img.filter(ImageFilter.GaussianBlur(65))
        frame.paste(glow_blurred, (int(cx_base - glow_rad), int(cy_base - glow_rad)), glow_blurred)

        # 3. Dynamic 2.5D Parallax Zoom on Portrait
        # Subject scales from 0.96 to 1.05 (pushing towards camera)
        scale_p = 0.96 + progress * 0.09
        cur_w = int(portrait_composite.width * scale_p)
        cur_h = int(portrait_composite.height * scale_p)
        
        # Position with subtle breathing motion
        px = int(cx_base - cur_w // 2)
        py = int(cy_base - cur_h // 2 + np.sin(progress * np.pi) * 10)

        # Shadow scales and moves slightly down-right
        sh_w = int(shadow_blurred.width * scale_p)
        sh_h = int(shadow_blurred.height * scale_p)
        sh_scaled = shadow_blurred.resize((sh_w, sh_h), Image.BILINEAR)
        frame.paste(sh_scaled, (px - int(shadow_pad * scale_p), py - int(shadow_pad * scale_p)), sh_scaled)

        # Paste Portrait
        p_scaled = portrait_composite.resize((cur_w, cur_h), Image.LANCZOS)
        frame.paste(p_scaled, (px, py), p_scaled)

        # 4. Kinetic Lower-Third Badge Plate (slides in from left between 0.0s and 0.4s)
        slide_in = min(1.0, t / 0.35)
        # Ease-out cubic
        ease = 1.0 - (1.0 - slide_in) ** 3
        badge_x = int(900 - (1.0 - ease) * 400)
        badge_y = 380

        draw = ImageDraw.Draw(frame)

        # Category Tag Badge
        tag_w, tag_h = 240, 38
        draw.rectangle([badge_x, badge_y - 48, badge_x + tag_w, badge_y - 10], fill=accent_color)
        draw.text((badge_x + tag_w // 2, badge_y - 29), badge_text.upper(), font=font_badge, fill=(10, 10, 15), anchor="mm")

        # Main Name with drop shadow
        draw.text((badge_x + 3, badge_y + 3), title_text.upper(), font=font_title, fill=(0, 0, 0, 220))
        draw.text((badge_x, badge_y), title_text.upper(), font=font_title, fill=(255, 255, 255))

        # Golden Accent underline bar
        line_w = int(680 * ease)
        draw.rectangle([badge_x, badge_y + 80, badge_x + line_w, badge_y + 86], fill=accent_color)

        # Role & Historical Context
        draw.text((badge_x, badge_y + 110), role_text.upper(), font=font_sub, fill=(215, 225, 235))

        # Secondary historical subtitle
        draw.text((badge_x, badge_y + 160), "ARCHIVE DOSSIER // SWISSAIR GROUNDING INQUIRY", font=font_badge, fill=(140, 155, 175))

        # 5. Film Grain / Subtle Dust overlay
        grain = np.random.randint(-14, 14, (H, W, 3), dtype=np.int16)
        frame_rgb = np.array(frame.convert("RGB"), dtype=np.int16)
        frame_grained = np.clip(frame_rgb + grain, 0, 255).astype(np.uint8)

        out_frame_file = temp_frames_dir / f"frame_{f_idx:04d}.png"
        Image.fromarray(frame_grained).save(out_frame_file)

        if f_idx % 30 == 0 or f_idx == total_frames - 1:
            print(f"  Frame {f_idx}/{total_frames} rendered...")

    # Encode with FFmpeg
    cmd_enc = [
        "ffmpeg", "-y",
        "-r", str(FPS),
        "-i", str(temp_frames_dir / "frame_%04d.png"),
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-an",
        str(out_mp4)
    ]
    subprocess.run(cmd_enc, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Cleanup temp frames
    shutil.rmtree(temp_frames_dir, ignore_errors=True)
    for bg_f in ADV_DIR.glob(f"bg_{out_mp4.stem}_*.jpg"):
        try:
            bg_f.unlink()
        except Exception:
            pass

    print(f"Successfully created 2.5D Parallax Card: {out_mp4.name} ({out_mp4.stat().st_size / (1024*1024):.2f} MB)")

def build_all_25d_cards():
    import shutil
    print("=== BUILDING MAGNATESMEDIA 2.5D PARALLAX SUITE ===")

    # 1. Mario Corti
    create_circular_cutout_card(
        face_src=PHOTO_DIR / "photo_02_mario_corti.png",
        bg_video=CLIPS_DIR / "politics_ubs_09_mario_corti_mic.mp4",
        out_mp4=ADV_DIR / "parallax_01_mario_corti.mp4",
        title_text="MARIO CORTI",
        role_text="CHIEF EXECUTIVE OFFICER & FORMER NESTLE CFO",
        badge_text="KEY WITNESS // 2001",
        duration=3.0,
        accent_color=(235, 45, 45)  # Urgent red
    )

    # 2. Philippe Bruggisser
    create_circular_cutout_card(
        face_src=PHOTO_DIR / "photo_06_bruggisser.png",
        bg_video=CLIPS_DIR / "zurich_uncut_04_cockpit_view.mp4",
        out_mp4=ADV_DIR / "parallax_02_philippe_bruggisser.mp4",
        title_text="PHILIPPE BRUGGISSER",
        role_text="ARCHITECT OF THE FATAL 'HUNTER STRATEGY'",
        badge_text="CHIEF EXECUTIVE (1996-2001)",
        duration=3.0,
        accent_color=(212, 175, 55)  # Executive gold
    )

    # 3. Marcel Ospel
    create_circular_cutout_card(
        face_src=PHOTO_DIR / "photo_03_marcel_ospel.png",
        bg_video=CLIPS_DIR / "politics_ubs_03_ubs_headquarters.mp4",
        out_mp4=ADV_DIR / "parallax_03_marcel_ospel.mp4",
        title_text="MARCEL OSPEL",
        role_text="CHAIRMAN & CHIEF EXECUTIVE, UBS",
        badge_text="THE BANK CONSORTIUM",
        duration=3.0,
        accent_color=(212, 175, 55)  # Gold
    )

    # 4. UBS Headquarters Dossier
    create_circular_cutout_card(
        face_src=PHOTO_DIR / "photo_01_ubs_hq.png",
        bg_video=CLIPS_DIR / "politics_ubs_20_financial_district_zurich.mp4",
        out_mp4=ADV_DIR / "parallax_04_ubs_dossier.mp4",
        title_text="UBS HEADQUARTERS",
        role_text="THE PARADEPLATZ TOWER THAT FROZE SWISSAIR",
        badge_text="ZURICH FINANCIAL CARTEL",
        duration=3.0,
        accent_color=(235, 45, 45)  # Red
    )

    print("All 2.5D Parallax Cards generated successfully!")

if __name__ == "__main__":
    import shutil
    build_all_25d_cards()
