import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = "data/media/paper_assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_desk_surface(width=1920, height=1080):
    """
    Generates a full-bleed 16:9 dark textured executive wooden/slate desk surface
    with a warm investigative spotlight and vignette so there are ZERO black bars.
    """
    # Dark charcoal / slate base
    base = np.zeros((height, width, 3), dtype=np.float32)
    base[:, :] = [26, 28, 32] # Dark cinematic slate
    
    # Add subtle wood grain / noise
    grain = np.random.normal(0, 4.0, (height, width, 3))
    base = np.clip(base + grain, 0, 255).astype(np.uint8)
    bg = Image.fromarray(base)
    
    # Warm radial spotlight in center
    spotlight = Image.new("L", (width, height), 0)
    sdraw = ImageDraw.Draw(spotlight)
    sdraw.ellipse([(200, 50), (width - 200, height - 50)], fill=120)
    spotlight = spotlight.filter(ImageFilter.GaussianBlur(180))
    
    # Tint spotlight with subtle warm amber
    warm_layer = Image.new("RGB", (width, height), (42, 38, 32))
    bg = Image.composite(warm_layer, bg, spotlight)
    
    return bg

def generate_paper_texture(width=1920, height=1080, tint=(244, 240, 230)):
    """Generates an authentic aged fibrous paper texture."""
    paper = Image.new("RGB", (width, height), tint)
    arr = np.array(paper, dtype=np.float32)
    noise = np.random.normal(0, 6.0, (height, width, 3))
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def create_newspaper_clipping(headline, subhead, source="BLICK", date="02. OKTOBER 2001", stamp="GROUNDED", filename="paper_01.png"):
    """
    Generates a 100% full-frame 16:9 documentary newspaper inspection scene:
    A high-impact headline clipping with realistic torn paper edges, drop shadow,
    and marker highlights resting on an investigative desk surface (NO black bars!).
    """
    w, h = 1920, 1080
    bg = generate_desk_surface(w, h).convert("RGBA")
    
    # Clipping size - generous size filling the screen
    cw, ch = 1520, 840
    cx, cy = (w - cw) // 2, (h - ch) // 2
    
    # Generate paper piece
    paper = generate_paper_texture(cw, ch, tint=(245, 241, 232)).convert("RGBA")
    
    # Create torn border around this clipping
    clip_mask = Image.new("L", (cw, ch), 0)
    cdraw = ImageDraw.Draw(clip_mask)
    
    points = []
    # Top edge
    for x in range(0, cw, 10):
        points.append((x, random.randint(8, 20)))
    # Right edge
    for y in range(20, ch, 10):
        points.append((cw - random.randint(8, 20), y))
    # Bottom edge
    for x in range(cw, 0, -10):
        points.append((x, ch - random.randint(8, 20)))
    # Left edge
    for y in range(ch, 0, -10):
        points.append((random.randint(8, 20), y))
        
    cdraw.polygon(points, fill=255)
    paper.putalpha(clip_mask)
    
    # Draw newspaper typography onto the paper
    pdraw = ImageDraw.Draw(paper)
    
    font_bold = "C:/Windows/Fonts/impact.ttf" if os.path.exists("C:/Windows/Fonts/impact.ttf") else "C:/Windows/Fonts/arialbd.ttf"
    font_body = "C:/Windows/Fonts/georgia.ttf" if os.path.exists("C:/Windows/Fonts/georgia.ttf") else "C:/Windows/Fonts/times.ttf"
    
    f_source = ImageFont.truetype(font_bold, 40)
    f_date = ImageFont.truetype(font_body, 24)
    f_head = ImageFont.truetype(font_bold, 74)
    f_sub = ImageFont.truetype(font_body, 30)
    f_stamp = ImageFont.truetype(font_bold, 82)
    f_news = ImageFont.truetype(font_body, 22)
    
    # Masthead header line
    pdraw.text((65, 45), source.upper(), fill=(195, 20, 20), font=f_source)
    pdraw.text((cw - 360, 55), date, fill=(75, 75, 75), font=f_date)
    pdraw.line([(65, 102), (cw - 65, 102)], fill=(30, 30, 30), width=4)
    pdraw.line([(65, 110), (cw - 65, 110)], fill=(30, 30, 30), width=1)
    
    # Main Headline
    pdraw.text((65, 140), headline, fill=(15, 15, 15), font=f_head)
    
    # Red Marker Highlighter under key headline word
    bbox = pdraw.textbbox((65, 140), headline, font=f_head)
    marker_y = bbox[3] + 6
    pdraw.line([(65, marker_y), (min(bbox[2] + 25, cw - 65), marker_y)], fill=(225, 30, 30, 225), width=9)
    
    # Subheader / Article Lead
    pdraw.text((65, 250), subhead, fill=(45, 45, 45), font=f_sub)
    pdraw.line([(65, 335), (cw - 65, 335)], fill=(130, 130, 130), width=1)
    
    # News body
    body_text_sample = (
        "Die Flugzeuge blieben am Boden. Um 15:45 Uhr meldete der Flughafen Zurich den volligen "
        "Stillstand des Flugbetriebs der nationalen Airline. 260 Maschinen gegroundet, "
        "Milliardenverluste in wenigen Stunden. Kein Treibstoff ohne Barzahlung vor Ort.\n\n"
        "Die Grossbanken UBS und Credit Suisse verhandeln bis tief in die Nacht unter der Leitung "
        "von Marcel Ospel und Mario Corti. Der Bundesrat tagt in Bern im Krisenmodus."
    )
    pdraw.multiline_text((65, 360), body_text_sample, fill=(65, 65, 65), font=f_news, spacing=10)
    
    # Forensic Stamp
    stamp_img = Image.new("RGBA", (520, 190), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(stamp_img)
    sdraw.rectangle([(10, 10), (500, 170)], outline=(210, 20, 20, 245), width=8)
    sdraw.text((40, 42), stamp, fill=(210, 20, 20, 245), font=f_stamp)
    
    stamp_rot = stamp_img.rotate(random.choice([-14, -10, 12, 14]), expand=True, resample=Image.BICUBIC)
    paper.paste(stamp_rot, (cw - stamp_rot.width - 65, ch - stamp_rot.height - 45), stamp_rot)
    
    # Deep drop shadow for the paper piece onto the desk surface
    shadow_mask = Image.new("L", (cw + 60, ch + 60), 0)
    shadow_mask.paste(clip_mask, (30, 30))
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(24))
    
    shadow = Image.new("RGBA", (cw + 60, ch + 60), (0, 0, 0, 210))
    shadow.putalpha(shadow_mask)
    
    # Composite onto 1080p canvas with ZERO black bars
    bg.paste(shadow, (cx - 30, cy - 15), shadow)
    bg.paste(paper, (cx, cy), paper)
    
    out_path = os.path.join(OUTPUT_DIR, filename)
    bg.convert("RGB").save(out_path, "PNG")
    print(f"Generated 100% Full-Bleed Paper Scene: {out_path}")
    return out_path

if __name__ == "__main__":
    headlines = [
        ("DAS ENDE DER SWISSAIR", "DER NATIONALE STOLZ DER SCHWEIZ AM BODEN ZERBROCHEN", "BLICK", "02.10.2001", "GROUNDED", "paper_01_blick_grounded.png"),
        ("17 MILLIARDEN SCHULDEN", "DIE 'HUNTER-STRATEGIE' ENDET IM HISTORISCHEN DEBAKEL", "NZZ", "03.10.2001", "BANKRUPT", "paper_02_nzz_debts.png"),
        ("UBS VERWEIGERT KREDIT", "KEINE MILLIONEN FUR TREIBSTOFF: TANKWAGEN BLEIBEN WEG", "TAGES-ANZEIGER", "02.10.2001", "REJECTED", "paper_03_ubs_refusal.png"),
        ("39,000 PASSAGIERE GESTRANDET", "CHAOS AN DEN WELTWEITEN FLUGHAFEN - TICKETS WERTLOS", "LE TEMPS", "03.10.2001", "STRANDED", "paper_04_passengers.png"),
        ("BUNDESRAT IM KRISENMODUS", "NOTKREDIT VON 450 MILLIONEN SOLL RESTRUKTURIERUNG RETTEN", "FINANCIAL TIMES", "04.10.2001", "BAILOUT", "paper_05_bailout.png"),
        ("SABENA FOLGT IN DEN ABGRUND", "BELGISCHE TOCHTER REISST DIE SWISSAIR-KASSA LEER", "LE SOIR", "05.10.2001", "COLLAPSE", "paper_06_sabena.png")
    ]
    
    for h, sub, src, date, st, fn in headlines:
        create_newspaper_clipping(h, sub, src, date, st, fn)
