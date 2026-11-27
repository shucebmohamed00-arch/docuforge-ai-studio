"""
DocuForge AI - Master Motion Graphics & Animation Suite
Procedurally synthesizes 5 broadcast-grade kinetic motion graphics:
1. Animated Incident Date Badge ("October 2, 2001 // 08:42 CET")
2. Flight SR 111 Tactical HUD ("180 Passengers // Fuel Cutoff Alert")
3. Credit Lines Terminated Rubber Stamp Slam
4. 48-Hour Rapid Countdown Timer ("48:00:00 -> 00:00:00")
5. "The Flying Bank" Gold Corporate Dossier Card
"""

import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OVERLAY_DIR = Path("data/media/overlays")
TEMP_DIR = Path("data/media/anim_temp")
OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

try:
    f_mono_b = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 24)
    f_mono_lg = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 36)
    f_title = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 32)
    f_sub = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
    f_stamp = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 46)
except Exception:
    f_mono_b = f_mono_lg = f_title = f_sub = f_stamp = ImageFont.load_default()

def compile_frames_to_webm(frames_dir: Path, out_webm: Path, fps: int = 30):
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-c:v", "libvpx-vp9",
        "-pix_fmt", "yuva420p",
        "-b:v", "0",
        "-crf", "28",
        str(out_webm)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

# 1. ANIMATED INCIDENT DATE BADGE (OCTOBER 2, 2001)
def generate_date_badge():
    out_file = OVERLAY_DIR / "anim_01_date_badge.webm"
    if out_file.exists(): return
    f_dir = TEMP_DIR / "date_badge"
    f_dir.mkdir(parents=True, exist_ok=True)
    total_f = 110 # 3.66s
    for i in range(total_f):
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        progress = min(1.0, i / 14.0)
        t_ease = 1.0 - (1.0 - progress)**3
        curr_x = int(-520 + (80 - (-520)) * t_ease)
        alpha = 255 if i <= 95 else int(255 * (1.0 - (i - 95) / 15.0))
        
        box_w, box_h = 660, 135
        box_y = 110
        draw.rectangle([curr_x, box_y, curr_x + box_w, box_y + box_h], fill=(10, 14, 20, int(235 * (alpha/255))))
        draw.rectangle([curr_x, box_y, curr_x + 6, box_y + box_h], fill=(225, 25, 30, alpha))
        
        # Red pulsing incident beacon
        blink = (i // 8) % 2 == 0
        dot_c = (235, 35, 35, alpha) if blink else (130, 20, 20, alpha)
        draw.ellipse([curr_x + 22, box_y + 20, curr_x + 36, box_y + 34], fill=dot_c)
        
        date_txt = "DATE: OCTOBER 2, 2001 // 08:42 CET"
        vis_chars = min(len(date_txt), max(0, int((i - 6) * 1.6)))
        draw.text((curr_x + 48, box_y + 16), date_txt[:vis_chars], fill=(240, 245, 255, alpha), font=f_mono_b)
        
        if i > 16:
            draw.text((curr_x + 22, box_y + 54), "ZURICH KLOTEN AIRPORT", fill=(255, 255, 255, alpha), font=f_title)
            draw.text((curr_x + 22, box_y + 96), "INCIDENT: EMERGENCY LIQUIDITY FAILURE", fill=(200, 210, 225, alpha), font=f_sub)
        img.save(str(f_dir / f"frame_{i:04d}.png"), "PNG")
    compile_frames_to_webm(f_dir, out_file)
    print("Generated anim_01_date_badge.webm")

# 2. FLIGHT HUD CARD ("180 PASSENGERS // TAXIWAY BRAVO // KEROSENE REFUSED")
def generate_flight_hud():
    out_file = OVERLAY_DIR / "anim_02_flight_hud.webm"
    if out_file.exists(): return
    f_dir = TEMP_DIR / "flight_hud"
    f_dir.mkdir(parents=True, exist_ok=True)
    total_f = 105 # 3.5s
    for i in range(total_f):
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        progress = min(1.0, i / 14.0)
        t_ease = 1.0 - (1.0 - progress)**3
        curr_y = int(1200 - (1200 - 870) * t_ease)
        alpha = 255 if i <= 90 else int(255 * (1.0 - (i - 90) / 15.0))
        
        box_x = 70
        box_w, box_h = 760, 130
        draw.rectangle([box_x, curr_y, box_x + box_w, curr_y + box_h], fill=(10, 12, 18, int(235 * (alpha/255))))
        draw.rectangle([box_x, curr_y, box_x + 6, curr_y + box_h], fill=(235, 175, 40, alpha))
        
        # Flight tactical details
        draw.text((box_x + 24, curr_y + 16), "SWISSAIR FLIGHT SR 111  |  180 PASSENGERS", fill=(255, 255, 255, alpha), font=f_title)
        draw.text((box_x + 24, curr_y + 58), "LOCATION: TAXIWAY BRAVO // APPROACHING RUNWAY 16", fill=(200, 205, 215, alpha), font=f_sub)
        
        # Flashing alert banner
        flash = (i // 6) % 2 == 0
        banner_c = (220, 30, 30, alpha) if flash else (140, 20, 20, alpha)
        draw.rectangle([box_x + 24, curr_y + 90, box_x + box_w - 24, curr_y + 120], fill=banner_c)
        draw.text((box_x + 32, curr_y + 94), "WARNING: FUEL SUPPLIERS CUT OFF KEROSENE", fill=(255, 255, 255, alpha), font=f_mono_b)
        img.save(str(f_dir / f"frame_{i:04d}.png"), "PNG")
    compile_frames_to_webm(f_dir, out_file)
    print("Generated anim_02_flight_hud.webm")

# 3. KINETIC CREDIT FACILITY TERMINATED STAMP
def generate_credit_stamp():
    out_file = OVERLAY_DIR / "anim_03_stamp_credit_dead.webm"
    if out_file.exists(): return
    f_dir = TEMP_DIR / "credit_stamp"
    f_dir.mkdir(parents=True, exist_ok=True)
    total_f = 56 # 1.86s
    for i in range(total_f):
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Slam animation with bounce at frame 8
        if i < 8:
            scale = 2.5 - (1.5 * (i / 8.0))
            alpha = int(255 * (i / 8.0))
        elif i < 12:
            scale = 1.0 + 0.15 * (1.0 - (i - 8) / 4.0)
            alpha = 255
        else:
            scale = 1.0
            alpha = 255 if i <= 46 else int(255 * (1.0 - (i - 46) / 10.0))
            
        stamp_w = int(720 * scale)
        stamp_h = int(140 * scale)
        cx, cy = 960, 540
        x0, y0 = cx - stamp_w // 2, cy - stamp_h // 2
        
        draw.rectangle([x0, y0, x0 + stamp_w, y0 + stamp_h], outline=(230, 30, 30, alpha), width=max(4, int(6 * scale)))
        draw.rectangle([x0 + 10, y0 + 10, x0 + stamp_w - 10, y0 + stamp_h - 10], outline=(230, 30, 30, int(alpha * 0.7)), width=2)
        draw.text((x0 + 40 * scale, y0 + 20 * scale), "CREDIT LINES: DEAD", fill=(240, 30, 30, alpha), font=f_stamp)
        draw.text((x0 + 55 * scale, y0 + 85 * scale), "FACILITY REVOKED // 0.00 CHF REMAINING", fill=(240, 200, 200, alpha), font=f_mono_b)
        img.save(str(f_dir / f"frame_{i:04d}.png"), "PNG")
    compile_frames_to_webm(f_dir, out_file)
    print("Generated anim_03_stamp_credit_dead.webm")

# 4. 48-HOUR RAPID COUNTDOWN TIMER
def generate_countdown_48h():
    out_file = OVERLAY_DIR / "anim_04_countdown_48h.webm"
    if out_file.exists(): return
    f_dir = TEMP_DIR / "countdown_48h"
    f_dir.mkdir(parents=True, exist_ok=True)
    total_f = 125 # 4.16s
    for i in range(total_f):
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        alpha = 255 if i <= 105 else int(255 * (1.0 - (i - 105) / 20.0))
        
        box_x = 1200
        box_y = 110
        box_w, box_h = 640, 140
        draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=(12, 14, 20, int(235 * (alpha/255))))
        draw.rectangle([box_x, box_y, box_x + 6, box_y + box_h], fill=(235, 35, 35, alpha))
        
        # Countdown time calculation from 48:00:00 down to 00:00:00
        pct = min(1.0, i / 90.0)
        rem_sec = int(48 * 3600 * (1.0 - pct))
        h = rem_sec // 3600
        m = (rem_sec % 3600) // 60
        s = rem_sec % 60
        ms = int(((rem_sec % 1.0) if hasattr(rem_sec, '__mod__') else (i % 30)) * 3.3)
        time_str = f"{h:02d}:{m:02d}:{s:02d}.{ms:02d}"
        
        draw.text((box_x + 24, box_y + 16), "FLEET GROUNDING COUNTDOWN", fill=(200, 205, 215, alpha), font=f_sub)
        draw.text((box_x + 24, box_y + 46), time_str, fill=(245, 40, 40, alpha), font=f_mono_lg)
        
        status_txt = "STATUS: 260 FLEET AIRCRAFT GROUNDED WORLDWIDE" if i > 80 else "STATUS: CANCELING FLIGHTS ACROSS EUROPE"
        draw.text((box_x + 24, box_y + 98), status_txt, fill=(255, 255, 255, alpha), font=f_sub)
        img.save(str(f_dir / f"frame_{i:04d}.png"), "PNG")
    compile_frames_to_webm(f_dir, out_file)
    print("Generated anim_04_countdown_48h.webm")

# 5. "THE FLYING BANK" GOLD CREDENTIAL BADGE
def generate_flying_bank_badge():
    out_file = OVERLAY_DIR / "anim_05_flying_bank_badge.webm"
    if out_file.exists(): return
    f_dir = TEMP_DIR / "flying_bank"
    f_dir.mkdir(parents=True, exist_ok=True)
    total_f = 120 # 4.0s
    for i in range(total_f):
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        progress = min(1.0, i / 14.0)
        t_ease = 1.0 - (1.0 - progress)**3
        curr_x = int(-550 + (80 - (-550)) * t_ease)
        alpha = 255 if i <= 100 else int(255 * (1.0 - (i - 100) / 20.0))
        
        box_w, box_h = 680, 130
        box_y = 110
        draw.rectangle([curr_x, box_y, curr_x + box_w, box_y + box_h], fill=(14, 16, 22, int(235 * (alpha/255))))
        draw.rectangle([curr_x, box_y, curr_x + 6, box_y + box_h], fill=(212, 175, 55, alpha)) # Swiss gold
        
        draw.text((curr_x + 24, box_y + 16), "SWISSAIR GROUP  |  SWISS NATIONAL SYMBOL", fill=(212, 175, 55, alpha), font=f_sub)
        draw.text((curr_x + 24, box_y + 44), "'THE FLYING BANK'", fill=(255, 255, 255, alpha), font=f_title)
        draw.text((curr_x + 24, box_y + 90), "CREDIT RATING: AAA -> [TOTAL COLLAPSE IN 48 HOURS]", fill=(220, 225, 235, alpha), font=f_sub)
        img.save(str(f_dir / f"frame_{i:04d}.png"), "PNG")
    compile_frames_to_webm(f_dir, out_file)
    print("Generated anim_05_flying_bank_badge.webm")

if __name__ == "__main__":
    generate_date_badge()
    generate_flight_hud()
    generate_credit_stamp()
    generate_countdown_48h()
    generate_flying_bank_badge()
    print("All kinetic animations synthesized successfully!")
