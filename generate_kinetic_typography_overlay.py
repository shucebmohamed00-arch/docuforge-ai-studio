"""
DocuForge AI - Broadcast Kinetic Typography Suite (MagnatesMedia Grade)
Synthesizes sample-accurate kinetic text animations with true alpha:
- Animated keyword pop-ins with scale bounce physics
- High-contrast typography (Bahnschrift / DIN) with drop shadows
- Dynamic color highlighting: Swiss Gold (#FFD700) and Emergency Red (#FF3333)
- Translucent dark pill badges for readability over any footage
"""

import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OVERLAY_DIR = Path("data/media/overlays")
TEMP_DIR = Path("data/media/anim_temp/kinetic_subtitles")
OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

try:
    f_huge = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 46)
    f_large = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 36)
    f_sub = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 26)
    f_mono = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 22)
except Exception:
    f_huge = f_large = f_sub = f_mono = ImageFont.load_default()

# Timeline of Kinetic Subtitle Events (start_time, end_time, main_text, highlight_words, color_theme)
KINETIC_CUES = [
    (0.4, 3.8, "ON OCTOBER 2ND, 2001 // 08:42 AM", ["OCTOBER 2ND, 2001"], "red"),
    (4.0, 7.9, "THE UNTHINKABLE HAPPENED IN SWITZERLAND", ["UNTHINKABLE", "SWITZERLAND"], "gold"),
    (8.0, 11.9, "SWISSAIR FLIGHT 111 READY FOR DEPARTURE", ["SWISSAIR FLIGHT 111"], "white"),
    (12.0, 15.4, "GROUND CREWS REFUSED TO MOVE", ["REFUSED TO MOVE"], "red"),
    (15.5, 19.9, "FUEL SUPPLIERS DEMAND IMMEDIATE CASH", ["IMMEDIATE CASH"], "gold"),
    (20.0, 21.8, "SWISSAIR'S CREDIT LINES: DEAD", ["CREDIT LINES: DEAD"], "red"),
    (21.9, 26.1, "WITHIN 48 HOURS...", ["48 HOURS"], "gold"),
    (26.2, 30.6, "260 AIRCRAFT GROUNDED WORLDWIDE", ["GROUNDED WORLDWIDE"], "red"),
    (30.7, 35.1, "MARIO CORTI: 'UBS REFUSED TO BRIDGE FINANCIAL GAP'", ["UBS REFUSED"], "white"),
    (35.2, 39.6, "THE NATIONAL SYMBOL: 'THE FLYING BANK'", ["'THE FLYING BANK'"], "gold"),
    (39.7, 44.5, "A SYMBOL OF SWISS WEALTH & STABILITY", ["WEALTH & STABILITY"], "gold"),
    (44.6, 48.0, "THE ARCHITECT: 'THE HUNTER STRATEGY'", ["'THE HUNTER STRATEGY'"], "gold"),
    (48.1, 51.4, "OVER 17 BILLION FRANCS OF HIDDEN DEBT", ["17 BILLION FRANCS", "HIDDEN DEBT"], "red"),
    (51.5, 55.0, "FORENSIC AUDIT: CATASTROPHIC DEFAULT", ["CATASTROPHIC DEFAULT"], "red"),
    (55.1, 58.6, "GROUNDING: DER SCHWARZE DIENSTAG", ["DER SCHWARZE DIENSTAG"], "red"),
    (58.7, 62.7, "A NATIONAL ICON DESTROYED IN 48 HOURS", ["DESTROYED IN 48 HOURS"], "red")
]

def render_kinetic_text_overlay():
    fps = 30
    total_duration = 62.724
    total_frames = int(total_duration * fps)
    
    print(f"Generating {total_frames} frames of Kinetic Text Animations...")
    
    for f in range(total_frames):
        t = f / float(fps)
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Find active cue
        for start_t, end_t, text, highlights, theme in KINETIC_CUES:
            if start_t <= t <= end_t:
                cue_dur = end_t - start_t
                elapsed = t - start_t
                
                # Entrance scale bounce in first 0.25s
                if elapsed < 0.2:
                    p = elapsed / 0.2
                    scale = 0.8 + 0.25 * math.sin(p * math.pi / 2.0)
                    alpha = int(255 * p)
                elif elapsed > (cue_dur - 0.2):
                    # Exit fade
                    p = (end_t - t) / 0.2
                    scale = 1.0
                    alpha = int(255 * max(0.0, p))
                else:
                    scale = 1.0
                    alpha = 255
                    
                # Kinetic Pill Box at bottom-center
                # Measure text
                bbox = f_huge.getbbox(text)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                
                pad_x, pad_y = 35, 18
                box_w = tw + pad_x * 2
                box_h = th + pad_y * 2
                cx = 960
                cy = 960 # bottom lower third
                
                x0 = int(cx - (box_w * scale) / 2.0)
                y0 = int(cy - (box_h * scale) / 2.0)
                x1 = int(cx + (box_w * scale) / 2.0)
                y1 = int(cy + (box_h * scale) / 2.0)
                
                # Dark translucent pill background with subtle glow
                card_bg = (10, 14, 22, int(205 * (alpha / 255.0)))
                border_c = (235, 35, 35, alpha) if theme == "red" else ((225, 180, 45, alpha) if theme == "gold" else (70, 90, 120, alpha))
                
                draw.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=card_bg, outline=border_c, width=2)
                
                # Draw text with word-level highlight coloring
                # Split words
                words = text.split()
                # Calculate total width to center words
                total_w = sum((f_huge.getbbox(w)[2] - f_huge.getbbox(w)[0]) for w in words) + (len(words) - 1) * 14
                cur_x = cx - total_w / 2.0
                text_y = y0 + pad_y - 4
                
                for w in words:
                    clean_w = w.strip(",./:'\"")
                    w_w = f_huge.getbbox(w)[2] - f_huge.getbbox(w)[0]
                    
                    is_high = any(clean_w.upper() in h.upper() for h in highlights)
                    if is_high:
                        txt_color = (255, 45, 45, alpha) if theme == "red" else ((255, 215, 40, alpha) if theme == "gold" else (255, 255, 255, alpha))
                    else:
                        txt_color = (225, 230, 240, int(alpha * 0.9))
                        
                    # Drop shadow
                    draw.text((cur_x + 2, text_y + 2), w, fill=(0, 0, 0, int(alpha * 0.6)), font=f_huge)
                    draw.text((cur_x, text_y), w, fill=txt_color, font=f_huge)
                    cur_x += w_w + 14
                    
                break # only one main subtitle cue per frame
                
        img.save(str(TEMP_DIR / f"frame_{f:04d}.png"), "PNG")
        
    out_mov = OVERLAY_DIR / "kinetic_subtitles_master.mov"
    print(f"Compiling frames to {out_mov} with true alpha...")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(TEMP_DIR / "frame_%04d.png"),
        "-c:v", "qtrle",
        str(out_mov)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Generated {out_mov} successfully! Size: {out_mov.stat().st_size / (1024*1024):.2f} MB")

if __name__ == "__main__":
    render_kinetic_text_overlay()
