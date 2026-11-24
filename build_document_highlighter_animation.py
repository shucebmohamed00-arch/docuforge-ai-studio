import os
import subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
OUT_DIR = BASE_DIR / "data" / "media" / "paper_assets"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def render_highlighter_scene(out_mp4: Path, dur_sec: float = 3.0, fps: int = 30):
    total_frames = int(dur_sec * fps)
    temp_frames_dir = OUT_DIR / "temp_highlighter_frames"
    temp_frames_dir.mkdir(exist_ok=True)

    # 1. Base Document Canvas (1920x1080)
    # Textured aged Swiss executive memorandum paper on dark slate desk
    bg = Image.new("RGBA", (1920, 1080), (22, 25, 30, 255))
    
    # Paper sheet dimensions
    pw, ph = 1580, 880
    px, py = (1920 - pw) // 2, (1080 - ph) // 2
    paper = Image.new("RGBA", (pw, ph), (248, 244, 235, 255))
    
    # Add subtle paper fiber noise
    p_arr = np.array(paper, dtype=np.float32)
    noise = np.random.normal(0, 4.0, (ph, pw, 4))
    p_arr = np.clip(p_arr + noise, 0, 255).astype(np.uint8)
    paper = Image.fromarray(p_arr)

    pdraw = ImageDraw.Draw(paper)
    
    font_bold = "C:/Windows/Fonts/georgiab.ttf" if os.path.exists("C:/Windows/Fonts/georgiab.ttf") else "C:/Windows/Fonts/arialbd.ttf"
    font_body = "C:/Windows/Fonts/georgia.ttf" if os.path.exists("C:/Windows/Fonts/georgia.ttf") else "C:/Windows/Fonts/times.ttf"

    f_header = ImageFont.truetype(font_bold, 36)
    f_sub = ImageFont.truetype(font_body, 24)
    f_body = ImageFont.truetype(font_body, 32)
    f_highlight = ImageFont.truetype(font_bold, 34)

    # Header / Meta
    pdraw.text((80, 60), "SWISSAIR GROUP // CRISIS MANAGEMENT BULLETIN", font=f_header, fill=(160, 20, 20, 255))
    pdraw.text((80, 110), "ZURICH-KLOTEN // 02. OKTOBER 2001 // VERTRAULICH", font=f_sub, fill=(90, 95, 105, 255))
    pdraw.line([(80, 150), (pw - 80, 150)], fill=(40, 40, 40, 255), width=3)
    pdraw.line([(80, 156), (pw - 80, 156)], fill=(120, 120, 120, 255), width=1)

    # Body Paragraphs
    body_1 = (
        "Die Swissair bedauert diese vor allem fuer die Passagiere und die\n"
        "Mitarbeitenden drastische Massnahme. Sie kommt im gewoehnlich\n"
        "ertragsstaerksten Monat des Jahres und betrifft nebst den\n"
        "Abertausenden von Passagieren auch Tausende von Arbeitsplaetzen."
    )
    pdraw.multiline_text((80, 210), body_1, font=f_body, fill=(35, 38, 42, 255), spacing=18)

    # The Key Sentence to be highlighted (as shown in user reference Screenshot 3)
    highlight_text = "Damit sind weit mehr als die gestern kommunizierten 2650 Arbeitsplaetze gefaehrdet."
    hx = 80
    hy = 460
    pdraw.text((hx, hy), highlight_text, font=f_highlight, fill=(15, 15, 15, 255))

    # Follow-up Paragraph
    body_2 = (
        "Die Grossbanken UBS und Credit Suisse haben trotz intensiver Verhandlungen\n"
        "keine weiteren Ueberbrueckungskredite fuer den laufenden Flugbetrieb freigegeben.\n"
        "Der weltweite Flugbetrieb bleibt bis auf weiteres vollstaendig eingestellt."
    )
    pdraw.multiline_text((80, 560), body_2, font=f_body, fill=(65, 70, 75, 255), spacing=16)

    # Calculate exact bounding box of the highlighted sentence
    bbox = pdraw.textbbox((hx, hy), highlight_text, font=f_highlight)
    hl_x1, hl_y1, hl_x2, hl_y2 = bbox
    hl_width = hl_x2 - hl_x1
    hl_height = hl_y2 - hl_y1

    # Base composite with paper drop shadow on desk
    shadow_mask = Image.new("L", (pw + 40, ph + 40), 0)
    sdraw = ImageDraw.Draw(shadow_mask)
    sdraw.rectangle([(20, 20), (pw + 20, ph + 20)], fill=200)
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(18))
    shadow = Image.new("RGBA", (pw + 40, ph + 40), (0, 0, 0, 220))
    shadow.putalpha(shadow_mask)

    bg.paste(shadow, (px - 20, py - 10), shadow)
    bg.paste(paper, (px, py), paper)

    # Render Frames with animated orange highlighter sweep and Ken Burns zoom
    print("Generating animated highlighter frames...")
    for frame_i in range(total_frames):
        t = frame_i / float(fps)
        frame_img = bg.copy()

        # Highlighter animation starts at t=0.5s and finishes at t=2.0s
        if t >= 0.5:
            progress = min(1.0, (t - 0.5) / 1.5)
            curr_w = int(hl_width * progress)
            
            if curr_w > 0:
                # Orange marker layer (vibrant translucent orange like reference)
                marker_layer = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
                mdraw = ImageDraw.Draw(marker_layer)
                
                # Global coordinates on frame
                mx1 = px + hl_x1 - 12
                my1 = py + hl_y1 - 6
                mx2 = mx1 + curr_w + 35
                my2 = py + hl_y2 + 8
                
                # Realistic rounded highlighter marker stroke (semi-transparent glowing orange)
                mdraw.rounded_rectangle([(mx1, my1), (mx2, my2)], radius=10, fill=(255, 120, 15, 155))
                # Core saturation line
                mdraw.line([(mx1 + 5, (my1 + my2) // 2), (mx2 - 5, (my1 + my2) // 2)], fill=(255, 95, 0, 100), width=18)
                
                # Soft marker bleed
                marker_blurred = marker_layer.filter(ImageFilter.GaussianBlur(1.5))
                frame_img.paste(marker_blurred, (0, 0), marker_blurred)

        # Dynamic subtle Ken Burns push-in centered on the highlighted sentence
        # Zoom from 1.0 to 1.08 over the clip
        zoom = 1.0 + (frame_i / float(total_frames)) * 0.08
        center_x = px + hl_x1 + hl_width // 2
        center_y = py + hy + 20
        
        crop_w = int(1920 / zoom)
        crop_h = int(1080 / zoom)
        crop_x = max(0, min(1920 - crop_w, center_x - crop_w // 2))
        crop_y = max(0, min(1080 - crop_h, center_y - crop_h // 2))

        cropped = frame_img.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
        scaled = cropped.resize((1920, 1080), Image.BICUBIC)

        out_frame_p = temp_frames_dir / f"frame_{frame_i:04d}.png"
        scaled.save(out_frame_p)

    # Encode to MP4 using ffmpeg
    cmd = [
        "ffmpeg", "-y", "-framerate", str(fps),
        "-i", str(temp_frames_dir / "frame_%04d.png"),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-an", str(out_mp4)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Highlighter Video Rendered: {out_mp4}")

    # Clean up temp frames
    for f in temp_frames_dir.glob("*.png"):
        f.unlink()
    temp_frames_dir.rmdir()

if __name__ == "__main__":
    out_file = OUT_DIR / "paper_highlighter_job_loss.mp4"
    render_highlighter_scene(out_file)

def render_nzz_debt_highlighter(out_mp4: Path, dur_sec: float = 3.0, fps: int = 30):
    total_frames = int(dur_sec * fps)
    temp_frames_dir = OUT_DIR / "temp_nzz_frames"
    temp_frames_dir.mkdir(exist_ok=True)

    bg = Image.new("RGBA", (1920, 1080), (20, 22, 28, 255))
    pw, ph = 1680, 900
    px, py = (1920 - pw) // 2, (1080 - ph) // 2
    paper = Image.new("RGBA", (pw, ph), (246, 242, 233, 255))
    
    p_arr = np.array(paper, dtype=np.float32)
    noise = np.random.normal(0, 4.0, (ph, pw, 4))
    p_arr = np.clip(p_arr + noise, 0, 255).astype(np.uint8)
    paper = Image.fromarray(p_arr)

    pdraw = ImageDraw.Draw(paper)
    font_bold = "C:/Windows/Fonts/impact.ttf" if os.path.exists("C:/Windows/Fonts/impact.ttf") else "C:/Windows/Fonts/arialbd.ttf"
    font_serif = "C:/Windows/Fonts/georgia.ttf" if os.path.exists("C:/Windows/Fonts/georgia.ttf") else "C:/Windows/Fonts/times.ttf"

    f_mast = ImageFont.truetype(font_serif, 44)
    f_date = ImageFont.truetype(font_serif, 24)
    f_head = ImageFont.truetype(font_bold, 64)
    f_body = ImageFont.truetype(font_serif, 30)

    # Newspaper Masthead
    pdraw.text((80, 50), "Neue Zurcher Zeitung", font=f_mast, fill=(20, 20, 20, 255))
    pdraw.text((pw - 380, 65), "03. OKTOBER 2001 // NR. 229", font=f_date, fill=(80, 80, 80, 255))
    pdraw.line([(80, 115), (pw - 80, 115)], fill=(30, 30, 30, 255), width=4)
    pdraw.line([(80, 122), (pw - 80, 122)], fill=(30, 30, 30, 255), width=1)

    # Main Headline
    pdraw.text((80, 160), "DAS ENDE EINES SCHWEIZER MYTHOS", font=f_head, fill=(15, 15, 15, 255))

    # Sentence to highlight
    hl_text = "Die Gesamtverbindlichkeiten der SAirGroup belaufen sich auf 17.8 Milliarden Franken."
    hx = 80
    hy = 280
    pdraw.text((hx, hy), hl_text, font=ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 34), fill=(10, 10, 10, 255))

    # Body
    body_text = (
        "Die aggressive Akquisitionsstrategie der vergangenen fuenf Jahre unter Philippe Bruggisser\n"
        "hat das Eigenkapital der traditionsreichen Fluggesellschaft vollstaendig aufgezehrt.\n"
        "Beteiligungen an defizitaeren europaeischen Fluggesellschaften wie Sabena, LTU und AOM\n"
        "hinterlassen einen Schuldenberg, den selbst die fuehrenden Schweizer Banken nicht mehr tragen wollen."
    )
    pdraw.multiline_text((80, 380), body_text, font=f_body, fill=(50, 55, 60, 255), spacing=16)

    # Stamp
    stamp_img = Image.new("RGBA", (480, 160), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(stamp_img)
    sdraw.rectangle([(10, 10), (460, 140)], outline=(200, 25, 25, 240), width=7)
    sdraw.text((35, 35), "17.8 MRD. CHF", font=ImageFont.truetype(font_bold, 58), fill=(200, 25, 25, 240))
    stamp_rot = stamp_img.rotate(10, expand=True, resample=Image.BICUBIC)
    paper.paste(stamp_rot, (pw - stamp_rot.width - 90, ph - stamp_rot.height - 70), stamp_rot)

    # Shadow & Composite
    shadow_mask = Image.new("L", (pw + 40, ph + 40), 0)
    sdraw = ImageDraw.Draw(shadow_mask)
    sdraw.rectangle([(20, 20), (pw + 20, ph + 20)], fill=200)
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(18))
    shadow = Image.new("RGBA", (pw + 40, ph + 40), (0, 0, 0, 220))
    shadow.putalpha(shadow_mask)

    bg.paste(shadow, (px - 20, py - 10), shadow)
    bg.paste(paper, (px, py), paper)

    bbox = pdraw.textbbox((hx, hy), hl_text, font=ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 34))
    hl_w = bbox[2] - bbox[0]
    hl_h = bbox[3] - bbox[1]

    for frame_i in range(total_frames):
        t = frame_i / float(fps)
        frame_img = bg.copy()
        if t >= 0.5:
            progress = min(1.0, (t - 0.5) / 1.5)
            curr_w = int(hl_w * progress)
            if curr_w > 0:
                marker_layer = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
                mdraw = ImageDraw.Draw(marker_layer)
                mx1 = px + hx - 12
                my1 = py + hy - 6
                mx2 = mx1 + curr_w + 35
                my2 = py + hy + hl_h + 8
                mdraw.rounded_rectangle([(mx1, my1), (mx2, my2)], radius=10, fill=(255, 120, 15, 155))
                mdraw.line([(mx1 + 5, (my1 + my2) // 2), (mx2 - 5, (my1 + my2) // 2)], fill=(255, 95, 0, 100), width=18)
                marker_blurred = marker_layer.filter(ImageFilter.GaussianBlur(1.5))
                frame_img.paste(marker_blurred, (0, 0), marker_blurred)

        zoom = 1.0 + (frame_i / float(total_frames)) * 0.08
        center_x = px + hx + hl_w // 2
        center_y = py + hy + 20
        crop_w = int(1920 / zoom)
        crop_h = int(1080 / zoom)
        crop_x = max(0, min(1920 - crop_w, center_x - crop_w // 2))
        crop_y = max(0, min(1080 - crop_h, center_y - crop_h // 2))

        cropped = frame_img.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
        scaled = cropped.resize((1920, 1080), Image.BICUBIC)
        scaled.save(temp_frames_dir / f"frame_{frame_i:04d}.png")

    cmd = [
        "ffmpeg", "-y", "-framerate", str(fps),
        "-i", str(temp_frames_dir / "frame_%04d.png"),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-an", str(out_mp4)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"NZZ Highlighter Rendered: {out_mp4}")
    for f in temp_frames_dir.glob("*.png"):
        f.unlink()
    temp_frames_dir.rmdir()
