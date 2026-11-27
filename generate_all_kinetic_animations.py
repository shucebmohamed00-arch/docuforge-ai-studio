"""
DocuForge AI - Premium Broadcast Motion Graphics Suite (MagnatesMedia Grade)
Generates 5 broadcast-grade kinetic motion graphics with true 32-bit alpha:
1. Incident Date Badge ("October 2, 2001 // 08:42 CET // Zurich Kloten Airport")
2. Tactical Aviation HUD ("Swissair Flight SR 111 // 180 Passengers // Taxiway Bravo")
3. Credit Lines Terminated Rubber Stamp Slam ("CREDIT LINES: DEAD // 0.00 CHF")
4. 48-Hour Rapid Countdown Timer ("48:00:00 -> 00:00:00 // 260 Aircraft Grounded")
5. "The Flying Bank" Gold Corporate Dossier Card ("Swiss National Symbol // Credit Rating: AAA -> 0")
"""

import os
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OVERLAY_DIR = Path("data/media/overlays")
TEMP_DIR = Path("data/media/anim_temp")
OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Modern typography
try:
    f_bahn_lg = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 36)
    f_bahn_md = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 26)
    f_bahn_sm = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 19)
    f_mono_b = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 22)
    f_mono_lg = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 38)
    f_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 32)
    f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20)
    f_stamp = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 52)
except Exception:
    f_bahn_lg = f_bahn_md = f_bahn_sm = f_mono_b = f_mono_lg = f_title = f_sub = f_stamp = ImageFont.load_default()

def compile_frames_to_mov(frames_dir: Path, out_mov: Path, fps: int = 30):
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-c:v", "qtrle",
        str(out_mov)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

# 1. ANIMATED INCIDENT DATE BADGE (OCTOBER 2, 2001)
def generate_date_badge():
    out_file = OVERLAY_DIR / "anim_01_date_badge.mov"
    f_dir = TEMP_DIR / "date_badge"
    if f_dir.exists(): shutil.rmtree(f_dir)
    f_dir.mkdir(parents=True, exist_ok=True)
    
    total_f = 110 # ~3.66s
    for i in range(total_f):
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Smooth cubic ease-in from left
        progress = min(1.0, i / 14.0)
        t_ease = 1.0 - (1.0 - progress)**3
        curr_x = int(-680 + (80 - (-680)) * t_ease)
        alpha = 255 if i <= 95 else int(255 * (1.0 - (i - 95) / 15.0))
        
        box_w, box_h = 720, 140
        box_y = 90
        
        # Translucent dark glassmorphism card (footage remains visible underneath!)
        card_bg = (10, 16, 26, int(195 * (alpha / 255)))
        draw.rounded_rectangle([curr_x, box_y, curr_x + box_w, box_y + box_h], radius=10, fill=card_bg, outline=(40, 60, 90, int(180 * (alpha / 255))), width=2)
        # Tactical red emergency accent strip
        draw.rounded_rectangle([curr_x + 3, box_y + 3, curr_x + 10, box_y + box_h - 3], radius=4, fill=(235, 30, 35, alpha))
        
        # Pulsing incident radar blip
        blink = (i // 7) % 2 == 0
        dot_c = (245, 45, 45, alpha) if blink else (130, 20, 20, alpha)
        draw.ellipse([curr_x + 28, box_y + 22, curr_x + 44, box_y + 38], fill=dot_c)
        if blink:
            draw.ellipse([curr_x + 24, box_y + 18, curr_x + 48, box_y + 42], outline=(245, 45, 45, int(120 * (alpha / 255))), width=2)
            
        date_txt = "INCIDENT LOG: OCTOBER 2, 2001 // 08:42 CET"
        vis_chars = min(len(date_txt), max(0, int((i - 5) * 1.6)))
        cursor = "_" if (blink and vis_chars < len(date_txt)) else ""
        draw.text((curr_x + 58, box_y + 18), date_txt[:vis_chars] + cursor, fill=(220, 235, 255, alpha), font=f_mono_b)
        
        if i > 12:
            draw.text((curr_x + 28, box_y + 56), "ZURICH KLOTEN AIRPORT", fill=(255, 255, 255, alpha), font=f_bahn_lg)
            draw.text((curr_x + 28, box_y + 100), "STATUS: SYSTEMIC LIQUIDITY COLLAPSE  |  FLEET REFUSED FUEL", fill=(255, 180, 50, alpha), font=f_bahn_sm)
            
        img.save(str(f_dir / f"frame_{i:04d}.png"), "PNG")
        
    compile_frames_to_mov(f_dir, out_file)
    print("Generated anim_01_date_badge.mov with true alpha")

# 2. FLIGHT HUD CARD ("180 PASSENGERS // TAXIWAY BRAVO // KEROSENE REFUSED")
def generate_flight_hud():
    out_file = OVERLAY_DIR / "anim_02_flight_hud.mov"
    f_dir = TEMP_DIR / "flight_hud"
    if f_dir.exists(): shutil.rmtree(f_dir)
    f_dir.mkdir(parents=True, exist_ok=True)
    
    total_f = 110 # ~3.66s
    for i in range(total_f):
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        progress = min(1.0, i / 14.0)
        t_ease = 1.0 - (1.0 - progress)**3
        curr_y = int(1180 - (1180 - 860) * t_ease)
        alpha = 255 if i <= 95 else int(255 * (1.0 - (i - 95) / 15.0))
        
        box_x = 80
        box_w, box_h = 820, 140
        
        # Translucent dark glass card
        card_bg = (10, 14, 22, int(195 * (alpha / 255)))
        draw.rounded_rectangle([box_x, curr_y, box_x + box_w, curr_y + box_h], radius=10, fill=card_bg, outline=(50, 70, 100, int(180 * (alpha / 255))), width=2)
        # Aviation amber stripe
        draw.rounded_rectangle([box_x + 3, curr_y + 3, box_x + 10, curr_y + box_h - 3], radius=4, fill=(245, 175, 30, alpha))
        
        draw.text((box_x + 28, curr_y + 16), "SWISSAIR FLIGHT SR 111", fill=(255, 255, 255, alpha), font=f_bahn_lg)
        draw.text((box_x + 460, curr_y + 22), "|  180 PASSENGERS ONBOARD", fill=(200, 215, 235, alpha), font=f_bahn_md)
        draw.text((box_x + 28, curr_y + 60), "LOCATION: TAXIWAY BRAVO // APPROACHING RUNWAY 16", fill=(185, 200, 220, alpha), font=f_bahn_sm)
        
        # Flashing red emergency warning banner
        flash = (i // 6) % 2 == 0
        banner_c = (225, 25, 30, alpha) if flash else (140, 15, 20, alpha)
        draw.rounded_rectangle([box_x + 24, curr_y + 94, box_x + box_w - 24, curr_y + 128], radius=6, fill=banner_c)
        draw.text((box_x + 36, curr_y + 98), "CRITICAL: FUEL SUPPLIERS DEMAND IMMEDIATE CASH PAYMENT", fill=(255, 255, 255, alpha), font=f_mono_b)
        
        img.save(str(f_dir / f"frame_{i:04d}.png"), "PNG")
        
    compile_frames_to_mov(f_dir, out_file)
    print("Generated anim_02_flight_hud.mov with true alpha")

# 3. KINETIC CREDIT FACILITY TERMINATED STAMP
def generate_credit_stamp():
    out_file = OVERLAY_DIR / "anim_03_stamp_credit_dead.mov"
    f_dir = TEMP_DIR / "credit_stamp"
    if f_dir.exists(): shutil.rmtree(f_dir)
    f_dir.mkdir(parents=True, exist_ok=True)
    
    total_f = 60 # 2.0s
    for i in range(total_f):
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if i < 8:
            scale = 2.4 - (1.4 * (i / 8.0))
            alpha = int(255 * (i / 8.0))
        elif i < 13:
            scale = 1.0 + 0.12 * (1.0 - (i - 8) / 5.0)
            alpha = 255
        else:
            scale = 1.0
            alpha = 255 if i <= 48 else int(255 * (1.0 - (i - 48) / 12.0))
            
        stamp_w = int(760 * scale)
        stamp_h = int(150 * scale)
        cx, cy = 960, 520
        x0, y0 = cx - stamp_w // 2, cy - stamp_h // 2
        
        # Heavy double-border classified red stamp with rubber ink texture
        draw.rectangle([x0, y0, x0 + stamp_w, y0 + stamp_h], outline=(235, 25, 25, alpha), width=max(4, int(7 * scale)))
        draw.rectangle([x0 + 12, y0 + 12, x0 + stamp_w - 12, y0 + stamp_h - 12], outline=(235, 25, 25, int(alpha * 0.75)), width=2)
        
        draw.text((x0 + 45 * scale, y0 + 20 * scale), "CREDIT LINES: DEAD", fill=(245, 30, 30, alpha), font=f_stamp)
        draw.text((x0 + 60 * scale, y0 + 95 * scale), "FACILITY REVOKED // 0.00 CHF CASH AVAILABLE", fill=(255, 210, 210, alpha), font=f_mono_b)
        
        img.save(str(f_dir / f"frame_{i:04d}.png"), "PNG")
        
    compile_frames_to_mov(f_dir, out_file)
    print("Generated anim_03_stamp_credit_dead.mov with true alpha")

# 4. 48-HOUR RAPID COUNTDOWN TIMER
def generate_countdown_48h():
    out_file = OVERLAY_DIR / "anim_04_countdown_48h.mov"
    f_dir = TEMP_DIR / "countdown_48h"
    if f_dir.exists(): shutil.rmtree(f_dir)
    f_dir.mkdir(parents=True, exist_ok=True)
    
    total_f = 130 # ~4.3s
    for i in range(total_f):
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        alpha = 255 if i <= 110 else int(255 * (1.0 - (i - 110) / 20.0))
        box_x = 1180
        box_y = 90
        box_w, box_h = 660, 150
        
        # Translucent glass card
        card_bg = (12, 16, 24, int(195 * (alpha / 255)))
        draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=10, fill=card_bg, outline=(60, 80, 110, int(180 * (alpha / 255))), width=2)
        draw.rounded_rectangle([box_x + 3, box_y + 3, box_x + 10, box_y + box_h - 3], radius=4, fill=(235, 35, 35, alpha))
        
        pct = min(1.0, i / 95.0)
        rem_sec = int(48 * 3600 * (1.0 - pct))
        h = rem_sec // 3600
        m = (rem_sec % 3600) // 60
        s = rem_sec % 60
        ms = int((i % 30) * 3.3)
        time_str = f"{h:02d}:{m:02d}:{s:02d}.{ms:02d}"
        
        draw.text((box_x + 28, box_y + 16), "FLEET GROUNDING COUNTDOWN", fill=(200, 215, 235, alpha), font=f_bahn_sm)
        draw.text((box_x + 28, box_y + 45), time_str, fill=(255, 45, 45, alpha), font=f_mono_lg)
        
        status_txt = "STATUS: 260 FLEET AIRCRAFT GROUNDED WORLDWIDE" if i > 80 else "STATUS: SYSTEMIC LIQUIDATION COLLAPSE"
        draw.text((box_x + 28, box_y + 105), status_txt, fill=(255, 220, 100, alpha), font=f_bahn_sm)
        
        img.save(str(f_dir / f"frame_{i:04d}.png"), "PNG")
        
    compile_frames_to_mov(f_dir, out_file)
    print("Generated anim_04_countdown_48h.mov with true alpha")

# 5. "THE FLYING BANK" GOLD CREDENTIAL BADGE
def generate_flying_bank_badge():
    out_file = OVERLAY_DIR / "anim_05_flying_bank_badge.mov"
    f_dir = TEMP_DIR / "flying_bank"
    if f_dir.exists(): shutil.rmtree(f_dir)
    f_dir.mkdir(parents=True, exist_ok=True)
    
    total_f = 120 # 4.0s
    for i in range(total_f):
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        progress = min(1.0, i / 14.0)
        t_ease = 1.0 - (1.0 - progress)**3
        curr_x = int(-700 + (80 - (-700)) * t_ease)
        alpha = 255 if i <= 100 else int(255 * (1.0 - (i - 100) / 20.0))
        
        box_w, box_h = 740, 140
        box_y = 90
        
        # Translucent glass card with Swiss Gold border
        card_bg = (14, 18, 28, int(195 * (alpha / 255)))
        draw.rounded_rectangle([curr_x, box_y, curr_x + box_w, box_y + box_h], radius=10, fill=card_bg, outline=(180, 140, 40, int(190 * (alpha / 255))), width=2)
        draw.rounded_rectangle([curr_x + 3, box_y + 3, curr_x + 10, box_y + box_h - 3], radius=4, fill=(225, 180, 45, alpha))
        
        draw.text((curr_x + 28, box_y + 16), "SWISSAIR GROUP  |  SWISS NATIONAL SYMBOL", fill=(225, 180, 45, alpha), font=f_bahn_sm)
        draw.text((curr_x + 28, box_y + 44), "'THE FLYING BANK'", fill=(255, 255, 255, alpha), font=f_bahn_lg)
        draw.text((curr_x + 28, box_y + 96), "CREDIT RATING: AAA  ->  [TOTAL COLLAPSE IN 48 HOURS]", fill=(240, 200, 120, alpha), font=f_bahn_sm)
        
        img.save(str(f_dir / f"frame_{i:04d}.png"), "PNG")
        
    compile_frames_to_mov(f_dir, out_file)
    print("Generated anim_05_flying_bank_badge.mov with true alpha")

if __name__ == "__main__":
    generate_date_badge()
    generate_flight_hud()
    generate_credit_stamp()
    generate_countdown_48h()
    generate_flying_bank_badge()
    print("All kinetic animations synthesized with true alpha!")
