import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
OVERLAY_DIR = BASE_DIR / "data" / "media" / "magnates_overlays"
OVERLAY_DIR.mkdir(parents=True, exist_ok=True)

PUNCH_TEXTS = {
    1:  ("SWITZERLAND'S GREATEST ", "CORPORATE COLLAPSE", (245, 45, 45)),
    3:  ("A FORTRESS BALANCE SHEET ", "ERADICATED IN 48 HOURS", (245, 45, 45)),
    5:  ("NICKNAMED: ", "'THE FLYING BANK'", (255, 205, 30)),
    7:  ("CREDIT LINES: ", "COMPLETELY DEAD", (245, 45, 45)),
    10: ("HOW DOES AN ICON ", "COLLAPSE IN 48 HOURS?", (255, 205, 30)),
    12: ("THE DEBT SPIKE: ", "17 BILLION FRANCS", (245, 45, 45)),
    16: ("LOCKED OUT OF ", "EUROPEAN SKIES", (245, 45, 45)),
    18: ("ENTER: ", "PHILIPPE BRUGGISSER", (255, 205, 30)),
    20: ("THE NOTORIOUS ", "'HUNTER STRATEGY'", (245, 45, 45)),
    24: ("A MULTI-BILLION DOLLAR ", "SHOPPING SPREE", (255, 205, 30)),
    28: ("ALL FINANCIAL RISK ", "ZERO CONTROL", (245, 45, 45)),
    30: ("HEMORRHAGING 3 MILLION ", "EVERY 24 HOURS", (245, 45, 45)),
    32: ("BRUGGISSER FIRED ", "MARIO CORTI ARRIVES", (255, 205, 30)),
    34: ("OFF-BALANCE SHEET DEBT: ", "4.8 BILLION CHF", (245, 45, 45)),
    36: ("SEPTEMBER 11TH: ", "GLOBAL COLLAPSE", (245, 45, 45)),
    38: ("SECRET RESCUE PLAN: ", "'PROJECT PHOENIX'", (255, 205, 30)),
    44: ("OCTOBER 2, 2001: ", "THE TRAP SNAPS SHUT", (245, 45, 45)),
    48: ("ONLY 14.5 MILLION FRANCS ", "REMAINING", (245, 45, 45)),
    51: ("MARIO CORTI ORDERS: ", "FLEET SHUTDOWN", (245, 45, 45)),
    52: ("THE SWISS CROSS ", "GROUNDED", (245, 45, 45)),
    54: ("PROTESTORS CHANT: ", "'SWISSAIR ASSASSINS'", (245, 45, 45)),
    55: ("38,000 PASSENGERS ", "STRANDED GLOBALLY", (255, 205, 30)),
    58: ("SWISSAIR ERADICATED ", "CROSSAIR TAKES OVER", (255, 205, 30)),
    64: ("NO BRAND IS TOO SACRED ", "TO FALL", (245, 45, 45))
}

def generate_magnates_kinetic_card(text_w: str, text_accent: str, accent_color: tuple, out_png: Path):
    """
    Renders pure MagnatesMedia kinetic punch typography:
    - Transparent 1920x1080 canvas (NO solid boxes or borders!)
    - Large Impact / Condensed bold typography (86pt)
    - Clean word separation: Stark white + Vivid Accent (Red/Gold)
    - Multi-directional soft drop-shadow for 100% legibility on any video
    - Subtle cinematic bottom-third dark gradient vignette to anchor text
    """
    WIDTH, HEIGHT = 1920, 1080
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    
    # Bottom-third subtle radial vignette mask (transparent to 40% black)
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    for y in range(400, 750):
        factor = max(0.0, 1.0 - abs(y - 560) / 180.0)
        alpha = int(90 * (factor ** 1.5))
        alpha = max(0, min(110, alpha))
        vdraw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))
    img.paste(vignette, (0, 0), vignette)

    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 86)
    except:
        font = ImageFont.load_default()

    bbox_w = draw.textbbox((0, 0), text_w, font=font)
    bbox_a = draw.textbbox((0, 0), text_accent, font=font)
    w1 = bbox_w[2] - bbox_w[0]
    w2 = bbox_a[2] - bbox_a[0]
    total_w = w1 + w2

    x = (WIDTH - total_w) // 2
    y = 520

    # 1. Soft ambient shadow layer (blurred silhouette)
    shadow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)
    sdraw.text((x, y + 4), text_w, font=font, fill=(0, 0, 0, 220))
    sdraw.text((x + w1, y + 4), text_accent, font=font, fill=(0, 0, 0, 220))
    shadow_blurred = shadow_layer.filter(ImageFilter.GaussianBlur(10))
    img.paste(shadow_blurred, (0, 0), shadow_blurred)

    # 2. Tight high-contrast stroke / drop shadow (8-way)
    for ox in [-4, -2, 0, 2, 4]:
        for oy in [-2, 0, 2, 4, 6]:
            draw.text((x + ox, y + oy), text_w, font=font, fill=(0, 0, 0, 245))
            draw.text((x + w1 + ox, y + oy), text_accent, font=font, fill=(0, 0, 0, 245))

    # 3. Crisp foreground typography
    draw.text((x, y), text_w, font=font, fill=(255, 255, 255, 255))
    draw.text((x + w1, y), text_accent, font=font, fill=accent_color + (255,))

    img.save(str(out_png))
    print(f"Generated kinetic punch overlay: {out_png.name}")

if __name__ == "__main__":
    for beat_num, (tw, ta, col) in PUNCH_TEXTS.items():
        out_p = OVERLAY_DIR / f"punch_{beat_num:02d}.png"
        generate_magnates_kinetic_card(tw, ta, col, out_p)
    print("All MagnatesMedia kinetic overlays generated successfully!")
