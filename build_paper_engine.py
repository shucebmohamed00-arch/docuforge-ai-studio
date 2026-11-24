import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = "data/media/paper_assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_torn_edge_mask(width=1920, height=1080, orientation="horizontal", tear_position=0.5, roughness=25):
    """
    Creates a high-resolution binary mask of a jagged, fibrous paper tear.
    White (255) is paper, Black (0) is transparent/cutout.
    """
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    
    if orientation == "horizontal":
        base_y = int(height * tear_position)
        points = [(0, 0)]
        curr_y = base_y
        for x in range(0, width + 10, 8):
            curr_y += random.randint(-roughness, roughness)
            # clamp
            curr_y = max(base_y - 120, min(base_y + 120, curr_y))
            points.append((x, curr_y))
        points.append((width, 0))
        draw.polygon(points, fill=255)
    else: # vertical tear (left to right)
        base_x = int(width * tear_position)
        points = [(0, 0)]
        curr_x = base_x
        for y in range(0, height + 10, 8):
            curr_x += random.randint(-roughness, roughness)
            curr_x = max(base_x - 120, min(base_x + 120, curr_x))
            points.append((curr_x, y))
        points.append((0, height))
        draw.polygon(points, fill=255)
        
    return mask

def generate_paper_texture(width=1920, height=1080, tint=(242, 238, 228)):
    """Generates an authentic aged fibrous paper texture."""
    # Base tinted image
    paper = Image.new("RGB", (width, height), tint)
    arr = np.array(paper, dtype=np.float32)
    
    # Add subtle Gaussian noise for grain
    noise = np.random.normal(0, 7.0, (height, width, 3))
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    
    img = Image.fromarray(arr)
    return img

def create_newspaper_clipping(headline, subhead, source="BLICK", date="02. OKTOBER 2001", stamp="GROUNDED", filename="paper_01.png"):
    """
    Generates a high-impact documentary newspaper cutout with torn paper edges,
    aged paper texture, red marker underline, and dramatic forensic stamp.
    """
    w, h = 1920, 1080
    bg = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    
    # Clipping size
    cw, ch = 1400, 760
    cx, cy = (w - cw) // 2, (h - ch) // 2
    
    # Generate paper piece
    paper = generate_paper_texture(cw, ch, tint=(245, 240, 230)).convert("RGBA")
    
    # Create torn border around this clipping
    clip_mask = Image.new("L", (cw, ch), 0)
    cdraw = ImageDraw.Draw(clip_mask)
    
    # Ripped perimeter
    points = []
    # Top edge
    for x in range(0, cw, 10):
        points.append((x, random.randint(8, 22)))
    # Right edge
    for y in range(20, ch, 10):
        points.append((cw - random.randint(8, 22), y))
    # Bottom edge
    for x in range(cw, 0, -10):
        points.append((x, ch - random.randint(8, 22)))
    # Left edge
    for y in range(ch, 0, -10):
        points.append((random.randint(8, 22), y))
        
    cdraw.polygon(points, fill=255)
    paper.putalpha(clip_mask)
    
    # Draw newspaper typography onto the paper
    pdraw = ImageDraw.Draw(paper)
    
    # Fonts
    font_bold = "C:/Windows/Fonts/impact.ttf" if os.path.exists("C:/Windows/Fonts/impact.ttf") else "C:/Windows/Fonts/arialbd.ttf"
    font_body = "C:/Windows/Fonts/georgia.ttf" if os.path.exists("C:/Windows/Fonts/georgia.ttf") else "C:/Windows/Fonts/times.ttf"
    
    f_source = ImageFont.truetype(font_bold, 36)
    f_date = ImageFont.truetype(font_body, 22)
    f_head = ImageFont.truetype(font_bold, 68)
    f_sub = ImageFont.truetype(font_body, 28)
    f_stamp = ImageFont.truetype(font_bold, 76)
    
    # Masthead header line
    pdraw.text((60, 45), source.upper(), fill=(190, 20, 20), font=f_source)
    pdraw.text((cw - 320, 52), date, fill=(70, 70, 70), font=f_date)
    pdraw.line([(60, 95), (cw - 60, 95)], fill=(30, 30, 30), width=4)
    pdraw.line([(60, 102), (cw - 60, 102)], fill=(30, 30, 30), width=1)
    
    # Main Headline
    pdraw.text((60, 130), headline, fill=(15, 15, 15), font=f_head)
    
    # Red Marker Highlighter under key headline word
    bbox = pdraw.textbbox((60, 130), headline, font=f_head)
    marker_y = bbox[3] + 4
    # Marker stroke with slight jitter
    pdraw.line([(60, marker_y), (min(bbox[2] + 20, cw - 60), marker_y)], fill=(220, 30, 30, 220), width=8)
    
    # Subheader / Article Lead
    pdraw.text((60, 230), subhead, fill=(40, 40, 40), font=f_sub)
    
    # Column lines to simulate authentic broadsheet print
    pdraw.line([(60, 310), (cw - 60, 310)], fill=(120, 120, 120), width=1)
    
    # Simulated news column blocks (authentic Latin/news snippets)
    body_text_sample = (
        "Die Flugzeuge blieben am Boden. Um 15:45 Uhr meldete der Flughafen Zurich den volligen "
        "Stillstand des Flugbetriebs der nationalen Airline. 260 Maschinen gegroundet, "
        "Milliardenverluste in wenigen Stunden. Kein Treibstoff ohne Barzahlung vor Ort.\n\n"
        "Die Grossbanken UBS und Credit Suisse verhandeln bis tief in die Nacht unter der Leitung "
        "von Marcel Ospel und Mario Corti. Der Bundesrat tagt in Bern im Krisenmodus."
    )
    f_news = ImageFont.truetype(font_body, 20)
    pdraw.multiline_text((60, 330), body_text_sample, fill=(60, 60, 60), font=f_news, spacing=8)
    
    # Forensic Stamp (Rotated RED stamp in corner e.g. "GROUNDED", "LIQUIDATION")
    stamp_img = Image.new("RGBA", (500, 180), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(stamp_img)
    sdraw.rectangle([(10, 10), (480, 160)], outline=(210, 20, 20, 240), width=8)
    sdraw.text((35, 38), stamp, fill=(210, 20, 20, 240), font=f_stamp)
    
    # Rotate stamp
    stamp_rot = stamp_img.rotate(random.choice([-14, -11, 12, 15]), expand=True, resample=Image.BICUBIC)
    paper.paste(stamp_rot, (cw - stamp_rot.width - 60, ch - stamp_rot.height - 40), stamp_rot)
    
    # Drop shadow for the paper piece onto the 1080p canvas
    shadow_mask = Image.new("L", (cw + 40, ch + 40), 0)
    shadow_mask.paste(clip_mask, (20, 20))
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(18))
    
    shadow = Image.new("RGBA", (cw + 40, ch + 40), (0, 0, 0, 180))
    shadow.putalpha(shadow_mask)
    
    # Composite onto 1080p canvas with slight random tilt
    bg.paste(shadow, (cx - 20, cy - 10), shadow)
    bg.paste(paper, (cx, cy), paper)
    
    out_path = os.path.join(OUTPUT_DIR, filename)
    bg.save(out_path, "PNG")
    print(f"Generated Paper Cutout: {out_path}")
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
