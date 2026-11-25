import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PHOTO_DIR = Path("data/media/documentary_photos")
PHOTO_DIR.mkdir(parents=True, exist_ok=True)

# Generate high-resolution 1920x1080 documentary graphic picture cards
def create_airline_card(filename: str, airline_name: str, alliance_name: str,
                        country_text: str, primary_color: tuple, accent_color: tuple,
                        symbol_type: str):
    W, H = 1920, 1080
    img = Image.new("RGBA", (W, H), (14, 18, 24, 255))
    draw = ImageDraw.Draw(img)

    # Background subtle radial gradient
    cx, cy = W // 2, H // 2
    for r in range(W // 2, 0, -25):
        alpha = int(255 * (1 - r / (W // 2)) * 0.25)
        bbox = [cx - r * 1.6, cy - r, cx + r * 1.6, cy + r]
        draw.ellipse(bbox, fill=(primary_color[0] // 3, primary_color[1] // 3, primary_color[2] // 3, alpha))

    # Grid lines / documentary HUD
    for x in range(120, W - 120, 240):
        draw.line([(x, 100), (x, H - 100)], fill=(255, 255, 255, 18), width=1)
    for y in range(120, H - 120, 210):
        draw.line([(100, y), (W - 100, y)], fill=(255, 255, 255, 18), width=1)

    # Outer elegant picture border
    draw.rectangle([140, 100, W - 140, H - 100], outline=(255, 255, 255, 40), width=2)
    # Accent corner brackets
    bracket_len = 40
    for bx, by, dx, dy in [(140, 100, 1, 1), (W - 140, 100, -1, 1),
                           (140, H - 100, 1, -1), (W - 140, H - 100, -1, -1)]:
        draw.line([(bx, by), (bx + dx * bracket_len, by)], fill=accent_color, width=4)
        draw.line([(bx, by), (bx, by + dy * bracket_len)], fill=accent_color, width=4)

    # Central Airline Card Box
    card_w, card_h = 1000, 520
    card_x1 = (W - card_w) // 2
    card_y1 = (H - card_h) // 2 - 20
    card_x2 = card_x1 + card_w
    card_y2 = card_y1 + card_h

    # Card background (dark glass panel)
    draw.rectangle([card_x1, card_y1, card_x2, card_y2], fill=(22, 28, 38, 235), outline=accent_color, width=3)

    # Header badge
    badge_w, badge_h = 360, 44
    bx = (W - badge_w) // 2
    by = card_y1 - 22
    draw.rectangle([bx, by, bx + badge_w, by + badge_h], fill=accent_color)
    
    # Try fonts
    font_bold = None
    font_sub = None
    font_badge = None
    for fpath in ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"]:
        if os.path.exists(fpath):
            font_bold = ImageFont.truetype(fpath, 72)
            font_sub = ImageFont.truetype(fpath, 32)
            font_badge = ImageFont.truetype(fpath, 22)
            break
    if not font_bold:
        font_bold = font_sub = font_badge = ImageFont.load_default()

    # Badge text
    draw.text((W // 2, by + 22), "EUROPEAN MEGA-CARRIER", fill=(10, 10, 15), font=font_badge, anchor="mm")

    # Emblem representation in card
    sym_y = card_y1 + 120
    if symbol_type == "speedbird":
        # British Airways Speedbird stylized ribbon
        pts = [(W // 2 - 160, sym_y + 30), (W // 2 - 40, sym_y - 20), (W // 2 + 160, sym_y - 45),
               (W // 2 + 180, sym_y - 35), (W // 2, sym_y), (W // 2 - 140, sym_y + 40)]
        draw.polygon(pts, fill=(219, 48, 34, 255))
        # Blue ribbon underside
        pts_blue = [(W // 2 - 140, sym_y + 40), (W // 2, sym_y), (W // 2 + 120, sym_y + 15),
                    (W // 2 + 140, sym_y + 25), (W // 2 - 20, sym_y + 25)]
        draw.polygon(pts_blue, fill=(11, 44, 107, 255))
    elif symbol_type == "crane":
        # Lufthansa Crane circle & stylized wing
        draw.ellipse([W // 2 - 70, sym_y - 60, W // 2 + 70, sym_y + 60], outline=accent_color, width=6)
        # Stylized bird wing inside
        draw.polygon([(W // 2 - 45, sym_y + 20), (W // 2 - 10, sym_y - 35), (W // 2 + 50, sym_y - 25),
                      (W // 2 + 10, sym_y - 5), (W // 2 - 25, sym_y + 25)], fill=accent_color)
    elif symbol_type == "tricolor":
        # Air France stylized accent ribbon
        draw.polygon([(W // 2 - 140, sym_y + 25), (W // 2 - 20, sym_y - 35), (W // 2 + 140, sym_y - 45),
                      (W // 2 + 150, sym_y - 35), (W // 2, sym_y - 15), (W // 2 - 120, sym_y + 35)], fill=(237, 28, 36, 255))

    # Airline Name
    name_y = card_y1 + 250
    # Shadow
    draw.text((W // 2 + 3, name_y + 3), airline_name, fill=(0, 0, 0, 200), font=font_bold, anchor="mm")
    draw.text((W // 2, name_y), airline_name, fill=(255, 255, 255), font=font_bold, anchor="mm")

    # Alliance & Scope
    draw.text((W // 2, card_y1 + 350), alliance_name.upper(), fill=accent_color, font=font_sub, anchor="mm")
    draw.text((W // 2, card_y1 + 410), country_text.upper(), fill=(180, 195, 210), font=font_sub, anchor="mm")

    # Bottom caption
    draw.text((W // 2, H - 65), "HISTORICAL ARCHIVE // EUROPEAN DEREGULATION & ALLIANCES (1992-2001)",
              fill=(140, 155, 175), font=font_badge, anchor="mm")

    png_path = PHOTO_DIR / f"{filename}.png"
    img.convert("RGB").save(str(png_path), quality=95)

    # Render into short 1.2s smooth video clip with subtle documentary Ken Burns slow push
    mp4_path = PHOTO_DIR / f"{filename}.mp4"
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(png_path),
        "-t", "1.35",
        "-vf", "zoompan=z='min(zoom+0.0015,1.04)':d=45:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080,format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "19", "-pix_fmt", "yuv420p", "-an",
        str(mp4_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Created Mega Airline Picture Card: {mp4_path.name}")

if __name__ == "__main__":
    create_airline_card(
        filename="photo_07_british_airways",
        airline_name="BRITISH AIRWAYS",
        alliance_name="Founding Member: oneworld Alliance",
        country_text="Dominant Transatlantic Fleet // Formed Massive Alliances",
        primary_color=(11, 44, 107),
        accent_color=(235, 45, 45),
        symbol_type="speedbird"
    )

    create_airline_card(
        filename="photo_08_lufthansa",
        airline_name="LUFTHANSA GROUP",
        alliance_name="Founding Member: Star Alliance",
        country_text="Central European Aviation Giant // Rapid Acquisition Spree",
        primary_color=(5, 25, 60),
        accent_color=(245, 185, 20),
        symbol_type="crane"
    )

    create_airline_card(
        filename="photo_09_air_france",
        airline_name="AIR FRANCE",
        alliance_name="Founding Member: SkyTeam Alliance",
        country_text="Continental Powerhouse // Consolidated French Air Market",
        primary_color=(15, 30, 75),
        accent_color=(235, 35, 45),
        symbol_type="tricolor"
    )
    print("All 3 Mega-Airline Picture Cards generated successfully!")
