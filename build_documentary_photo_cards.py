import os
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PHOTO_DIR = "data/media/documentary_photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

def create_documentary_photo_card(src_frame_path: str, name_title: str, subtitle: str, out_png: str):
    """
    Creates an authentic 1920x1080 documentary historical photo card:
    Full-bleed 16:9 photo with film grain, dark cinematic vignette,
    and a broadcast-standard documentary lower-third title plate.
    """
    w, h = 1920, 1080
    
    # Open source frame and fit full-bleed 16:9
    img = Image.open(src_frame_path).convert("RGB")
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.BICUBIC)
    
    # Center crop to 1920x1080
    left = (nw - w) // 2
    top = (nh - h) // 2
    canvas = img.crop((left, top, left + w, top + h)).convert("RGBA")
    
    # Dark cinematic lower-third gradient and vignette
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    
    # Gradient on bottom 350px for lower-third legibility
    for y in range(h - 320, h):
        alpha = int(220 * ((y - (h - 320)) / 320.0))
        vdraw.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
        
    canvas.paste(vignette, (0, 0), vignette)
    
    # Draw lower third typography
    draw = ImageDraw.Draw(canvas)
    font_bold = "C:/Windows/Fonts/impact.ttf" if os.path.exists("C:/Windows/Fonts/impact.ttf") else "C:/Windows/Fonts/arialbd.ttf"
    font_sub = "C:/Windows/Fonts/arial.ttf"
    
    f_title = ImageFont.truetype(font_bold, 54)
    f_sub = ImageFont.truetype(font_sub, 26)
    
    # Red accent bar
    draw.rectangle([(120, h - 230), (130, h - 130)], fill=(215, 25, 25, 255))
    
    # Main Name/Subject
    draw.text((150, h - 232), name_title.upper(), font=f_title, fill=(255, 255, 255, 255))
    
    # Subtitle / Historical Role
    draw.text((152, h - 165), subtitle.upper(), font=f_sub, fill=(210, 180, 80, 255)) # Warm Gold
    
    canvas.convert("RGB").save(out_png, "PNG")
    print(f"Generated Documentary Photo Card: {out_png}")

def generate_cards():
    # 1. Marcel Ospel
    if os.path.exists("data/media/historical_photos/ubs_headquarters.jpg"):
        create_documentary_photo_card(
            "data/media/historical_photos/ubs_headquarters.jpg",
            "UBS HEADQUARTERS — ZURICH",
            "THE FINANCIAL CONSORTIUM THAT PULLED THE LIQUIDITY PLUG",
            os.path.join(PHOTO_DIR, "photo_01_ubs_hq.png")
        )
        
    # 2. Extract authentic historical frames from archival video for key historical figures
    cuts = [
        # Mario Corti at press conference (around 1:40 in SRF video)
        ("data/media/archival_srf_grounding.mp4.webm", 100, "MARIO CORTI", "CHIEF EXECUTIVE OFFICER & FORMER NESTLE CFO", "photo_02_mario_corti.png"),
        # Marcel Ospel arriving at bank (around 2:40 in SRF video)
        ("data/media/archival_srf_grounding.mp4.webm", 160, "MARCEL OSPEL", "CHAIRMAN & CHIEF EXECUTIVE, UBS", "photo_03_marcel_ospel.png"),
        # Protest crowd outside UBS with banner
        ("data/media/archival_srf_grounding.mp4.webm", 220, "PUBLIC OUTRAGE IN ZURICH", "PROTESTERS SIEGE UBS WITH 'SWISSAIR ASSASSINS' BANNERS", "photo_04_protest.png"),
        # Swiss Parliament in Bern
        ("data/media/archival_swiss_politics_ubs.mp4.webm", 45, "THE FEDERAL PALACE — BERN", "SWISS BUNDESRAT VOTES EMERGENCY 450M EMERGENCY RESCUE", "photo_05_parliament.png"),
        # Philippe Bruggisser / Hunter Strategy
        ("data/media/archival_swiss_politics_ubs.mp4.webm", 380, "PHILIPPE BRUGGISSER", "ARCHITECT OF THE FATAL 'HUNTER STRATEGY' ACQUISITION SPREE", "photo_06_bruggisser.png")
    ]
    
    for vid, sec, title, sub, out_name in cuts:
        if os.path.exists(vid):
            temp_jpg = os.path.join(PHOTO_DIR, f"temp_{out_name}.jpg")
            subprocess.run([
                "ffmpeg", "-y", "-ss", str(sec), "-i", vid,
                "-vframes", "1", "-q:v", "2", temp_jpg
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(temp_jpg):
                out_png = os.path.join(PHOTO_DIR, out_name)
                create_documentary_photo_card(temp_jpg, title, sub, out_png)
                os.remove(temp_jpg)

if __name__ == "__main__":
    generate_cards()
