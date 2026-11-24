import os
import math
import subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
GRAPHICS_DIR = BASE_DIR / "data" / "media" / "financial_graphics"
GRAPHICS_DIR.mkdir(parents=True, exist_ok=True)

# System fonts
FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 44)
FONT_SUB = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 26)
FONT_LABEL = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 24)
FONT_TICKER = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 26)
FONT_BIG = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 68)

WIDTH, HEIGHT = 1920, 1080

def create_base_terminal(title: str, subtitle: str, tag: str = "FINANCIAL INTELLIGENCE // HISTORICAL TRADING DATA"):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (12, 16, 24, 255))
    draw = ImageDraw.Draw(img)

    # Grid background
    for x in range(100, WIDTH - 100, 100):
        draw.line([(x, 150), (x, HEIGHT - 100)], fill=(25, 35, 50, 255), width=1)
    for y in range(180, HEIGHT - 100, 80):
        draw.line([(100, y), (WIDTH - 100, y)], fill=(25, 35, 50, 255), width=1)

    # Header bar
    draw.rectangle([(80, 40), (WIDTH - 80, 140)], fill=(18, 26, 38, 255), outline=(45, 65, 95, 255), width=2)
    draw.text((110, 52), tag, font=FONT_TICKER, fill=(80, 180, 255, 255))
    draw.text((110, 84), title, font=FONT_TITLE, fill=(245, 245, 250, 255))

    # Right side badge
    draw.rectangle([(WIDTH - 420, 56), (WIDTH - 105, 124)], fill=(30, 40, 58, 255), outline=(60, 90, 130, 255))
    draw.text((WIDTH - 400, 75), subtitle, font=FONT_LABEL, fill=(235, 75, 75, 255))

    # Bottom status bar
    draw.rectangle([(80, HEIGHT - 80), (WIDTH - 80, HEIGHT - 40)], fill=(15, 22, 32, 255), outline=(40, 55, 80, 255))
    draw.text((110, HEIGHT - 72), "SWX SWISS EXCHANGE ARCHIVE // ZURICH FINANCIAL DISTRICT // CONFIDENTIAL", font=FONT_TICKER, fill=(120, 140, 165, 255))

    return img

def render_video_from_frames(frames: list, out_path: Path, fps: int = 30):
    temp_dir = GRAPHICS_DIR / f"temp_{out_path.stem}"
    temp_dir.mkdir(exist_ok=True)
    for i, f in enumerate(frames):
        f.save(temp_dir / f"frame_{i:04d}.png")
    
    cmd = [
        "ffmpeg", "-y", "-framerate", str(fps),
        "-i", str(temp_dir / "frame_%04d.png"),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "19",
        "-pix_fmt", "yuv420p", "-an", str(out_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    for p in temp_dir.glob("*.png"):
        p.unlink()
    temp_dir.rmdir()
    print(f"Generated Graphic: {out_path.name}")

# Graphic 1: Stock Price Plunge (450 CHF down to 1.20 CHF)
def build_stock_crash_graphic():
    frames = []
    num_frames = 75  # 2.5 seconds at 30 fps
    
    data_points = [
        (1998.0, 450.0, "JAN 1998: PEAK VALUATION (450 CHF)"),
        (1999.5, 340.0, "MID 1999: HUNTER ACQUISITIONS"),
        (2000.8, 220.0, "LATE 2000: SABENA LOSSES EXPLODE"),
        (2001.2, 150.0, "JAN 2001: BRUGGISSER FIRED"),
        (2001.7, 75.0,  "SEP 11: GLOBAL AIRLINE CRASH"),
        (2001.76, 1.25, "OCT 2: TRADING HALT (1.25 CHF)")
    ]
    
    x_min, x_max = 180, WIDTH - 260
    y_min, y_max = 220, HEIGHT - 160
    
    for f_idx in range(num_frames):
        progress = f_idx / (num_frames - 1)
        base = create_base_terminal(
            title="SAIRGROUP (SWISSAIR) STOCK COLLAPSE [SWX: AIRN]",
            subtitle="CRASH: -99.7% // TRADING HALT",
            tag="ZURICH STOCK EXCHANGE // TRADING TICKER"
        )
        draw = ImageDraw.Draw(base)
        
        # Draw axes
        draw.line([(x_min, y_max), (x_max, y_max)], fill=(120, 140, 170, 255), width=2)
        draw.line([(x_min, y_min), (x_min, y_max)], fill=(120, 140, 170, 255), width=2)
        
        # Y labels
        for val in [450, 300, 150, 0]:
            y_pos = y_max - int((val / 450.0) * (y_max - y_min))
            draw.text((x_min - 75, y_pos - 12), f"{val}", font=FONT_TICKER, fill=(160, 180, 205, 255))
            draw.line([(x_min - 10, y_pos), (x_min, y_pos)], fill=(120, 140, 170, 255), width=2)
            
        # Animated line
        current_len = max(2, int(len(data_points) * progress) + 1)
        plot_pts = []
        for i in range(min(current_len, len(data_points))):
            pt_prog = i / (len(data_points) - 1)
            x_coord = x_min + int(pt_prog * (x_max - x_min))
            y_coord = y_max - int((data_points[i][1] / 450.0) * (y_max - y_min))
            plot_pts.append((x_coord, y_coord))
            
        for i in range(len(plot_pts) - 1):
            draw.line([plot_pts[i], plot_pts[i+1]], fill=(235, 45, 45, 255), width=5)
            
        for i, (x_c, y_c) in enumerate(plot_pts):
            draw.ellipse([(x_c - 7, y_c - 7), (x_c + 7, y_c + 7)], fill=(255, 80, 80, 255), outline=(255, 255, 255, 255), width=2)
            if i == len(plot_pts) - 1:
                lbl = data_points[i][2]
                draw.rectangle([(x_c + 15, y_c - 20), (x_c + 15 + len(lbl)*13, y_c + 20)], fill=(35, 20, 25, 240), outline=(235, 45, 45, 255), width=1)
                draw.text((x_c + 25, y_c - 10), lbl, font=FONT_LABEL, fill=(255, 220, 220, 255))
                
        # Big current stock price
        curr_price = 450.0 - progress * (450.0 - 1.25)
        draw.rectangle([(WIDTH - 480, 180), (WIDTH - 120, 300)], fill=(25, 18, 25, 245), outline=(235, 45, 45, 255), width=2)
        draw.text((WIDTH - 460, 195), "LAST TRADED PRICE:", font=FONT_LABEL, fill=(180, 190, 210, 255))
        draw.text((WIDTH - 460, 228), f"CHF {curr_price:.2f}", font=FONT_BIG, fill=(255, 60, 60, 255))
        
        frames.append(base)
        
    render_video_from_frames(frames, GRAPHICS_DIR / "graphic_01_stock_crash.mp4")

# Graphic 2: Debt Spiral vs Cash Reserves (17.8B Debt vs 14.5M Cash)
def build_debt_spiral_graphic():
    frames = []
    num_frames = 75
    years = ["1997", "1998", "1999", "2000", "OCT 2001"]
    debt_vals = [3.8, 6.2, 10.4, 15.2, 17.8]  # Billions CHF
    cash_vals = [2.2, 1.8, 0.9, 0.25, 0.0145] # Billions CHF
    
    for f_idx in range(num_frames):
        prog = f_idx / (num_frames - 1)
        base = create_base_terminal(
            title="SAIRGROUP TOTAL LIABILITIES VS LIQUIDITY (1997-2001)",
            subtitle="CRITICAL INSOLVENCY SPIRAL",
            tag="BALANCE SHEET FORENSICS // AUDITED DEBT EXPOSURE"
        )
        draw = ImageDraw.Draw(base)
        
        # Legend
        draw.rectangle([(WIDTH - 540, 160), (WIDTH - 500, 185)], fill=(235, 45, 45, 255))
        draw.text((WIDTH - 485, 162), "TOTAL DEBT (BILLIONS CHF)", font=FONT_LABEL, fill=(235, 235, 240, 255))
        draw.rectangle([(WIDTH - 540, 205), (WIDTH - 500, 230)], fill=(212, 175, 55, 255))
        draw.text((WIDTH - 485, 207), "CASH RESERVES (BILLIONS CHF)", font=FONT_LABEL, fill=(235, 235, 240, 255))
        
        # Bar chart layout
        x_start = 220
        gap = 260
        base_y = HEIGHT - 180
        max_h = 480
        
        for i, yr in enumerate(years):
            x = x_start + i * gap
            current_bar_prog = min(1.0, max(0.0, (prog - i * 0.12) / 0.35))
            
            # Debt Bar (Red)
            d_h = int((debt_vals[i] / 20.0) * max_h * current_bar_prog)
            draw.rectangle([(x, base_y - d_h), (x + 70, base_y)], fill=(225, 45, 45, 255), outline=(255, 100, 100, 255))
            if current_bar_prog > 0.5:
                draw.text((x - 5, base_y - d_h - 32), f"{debt_vals[i]*current_bar_prog:.1f}B", font=FONT_LABEL, fill=(255, 120, 120, 255))
                
            # Cash Bar (Gold)
            c_h = int((cash_vals[i] / 20.0) * max_h * current_bar_prog)
            draw.rectangle([(x + 85, base_y - c_h), (x + 155, base_y)], fill=(212, 175, 55, 255), outline=(255, 220, 120, 255))
            if current_bar_prog > 0.5:
                c_lbl = f"{cash_vals[i]*1000:.0f}M" if cash_vals[i] < 1.0 else f"{cash_vals[i]:.1f}B"
                draw.text((x + 85, base_y - c_h - 32), c_lbl, font=FONT_LABEL, fill=(255, 220, 100, 255))
                
            draw.text((x + 40, base_y + 25), yr, font=FONT_TITLE, fill=(200, 215, 235, 255))
            
        frames.append(base)
        
    render_video_from_frames(frames, GRAPHICS_DIR / "graphic_02_debt_spiral.mp4")

# Graphic 3: The Hunter Strategy Acquisition Web (49% Cap Explainer)
def build_hunter_network_graphic():
    frames = []
    num_frames = 75
    center = (WIDTH // 2, HEIGHT // 2 + 30)
    
    satellites = [
        ("SABENA (BELGIUM)", 49.5, "-1.5M CHF / DAY", -155),
        ("LTU (GERMANY)", 49.9, "-800K CHF / DAY", -75),
        ("AOM (FRANCE)", 49.0, "-600K CHF / DAY", 0),
        ("AIR LITTORAL", 49.0, "-300K CHF / DAY", 75),
        ("VOLARE (ITALY)", 34.0, "-200K CHF / DAY", 155)
    ]
    
    for f_idx in range(num_frames):
        prog = f_idx / (num_frames - 1)
        base = create_base_terminal(
            title="THE 'HUNTER STRATEGY' ACQUISITION WEB",
            subtitle="REGULATORY CAP: 49% OWNERSHIP // 100% LIABILITY",
            tag="CORPORATE GOVERNANCE FORENSICS // OFF-BALANCE-SHEET RISK"
        )
        draw = ImageDraw.Draw(base)
        
        # Center Node: Swissair
        cx, cy = center
        draw.ellipse([(cx - 120, cy - 80), (cx + 120, cy + 80)], fill=(180, 25, 25, 255), outline=(255, 255, 255, 255), width=3)
        draw.text((cx - 85, cy - 35), "SWISSAIR", font=FONT_TITLE, fill=(255, 255, 255, 255))
        draw.text((cx - 80, cy + 10), "SAirGroup (CH)", font=FONT_LABEL, fill=(240, 220, 220, 255))
        
        # Draw connecting laser beams to acquisitions
        radius = 360
        for i, (name, stake, loss, angle_deg) in enumerate(satellites):
            angle_rad = math.radians(angle_deg)
            sat_x = int(cx + radius * math.cos(angle_rad))
            sat_y = int(cy + radius * math.sin(angle_rad) * 0.75)
            
            # Animated connection
            line_prog = min(1.0, max(0.0, (prog - i * 0.12) / 0.35))
            end_x = int(cx + (sat_x - cx) * line_prog)
            end_y = int(cy + (sat_y - cy) * line_prog)
            
            draw.line([(cx, cy), (end_x, end_y)], fill=(235, 45, 45, 200), width=3)
            
            if line_prog > 0.8:
                draw.rectangle([(sat_x - 170, sat_y - 50), (sat_x + 170, sat_y + 50)], fill=(20, 28, 42, 245), outline=(212, 175, 55, 255), width=2)
                draw.text((sat_x - 150, sat_y - 40), name, font=FONT_LABEL, fill=(255, 255, 255, 255))
                draw.text((sat_x - 150, sat_y - 10), f"STAKE: {stake}% (NO CONTROL)", font=FONT_TICKER, fill=(212, 175, 55, 255))
                draw.text((sat_x - 150, sat_y + 16), f"DRAIN: {loss}", font=FONT_TICKER, fill=(255, 80, 80, 255))
                
        frames.append(base)
        
    render_video_from_frames(frames, GRAPHICS_DIR / "graphic_03_hunter_network.mp4")

# Graphic 4: October 2, 2001 Intraday Liquidity Countdown
def build_intraday_countdown_graphic():
    frames = []
    num_frames = 75
    
    timeline_events = [
        ("08:00 AM", "UBS EXPECTED LIQUIDITY TRANCHE", "CHF 250,000,000", "PAYMENT WITHHELD BY UBS", (235, 45, 45)),
        ("11:45 AM", "SWISSAIR MAIN TREASURY BALANCE", "CHF 14,500,000", "INSUFFICIENT FOR FLIGHT OPERATIONS", (212, 175, 55)),
        ("12:15 PM", "MINIMUM REQUIRED FOR KEROSENE", "CHF 18,000,000", "DEFICIT: CHF 3,500,000 SHORT", (235, 45, 45)),
        ("12:30 PM", "FLIGHT SR 356 (ZURICH -> JFK)", "AIRBUS A330-200", "REFUSED REFUELING AT PUMP", (235, 45, 45)),
        ("13:45 PM", "CHIEF EXECUTIVE DIRECTIVE", "GLOBAL FLEET HALT", "ALL 260 PLANES ORDERED GROUNDED", (255, 60, 60))
    ]
    
    for f_idx in range(num_frames):
        prog = f_idx / (num_frames - 1)
        base = create_base_terminal(
            title="INTRADAY LIQUIDITY COLLAPSE TIMELINE // OCTOBER 2, 2001",
            subtitle="TREASURY EXHAUSTION // HOUR-BY-HOUR",
            tag="DISASTER TIMELINE // CRITICAL OPERATIONAL COLLAPSE"
        )
        draw = ImageDraw.Draw(base)
        
        y_start = 180
        gap = 120
        
        for i, (time_str, title_str, val_str, note_str, col) in enumerate(timeline_events):
            item_prog = min(1.0, max(0.0, (prog - i * 0.14) / 0.28))
            if item_prog > 0:
                y = y_start + i * gap
                # Time pill
                draw.rectangle([(120, y), (280, y + 80)], fill=(30, 42, 60, 255), outline=(70, 95, 135, 255), width=2)
                draw.text((140, y + 25), time_str, font=FONT_TITLE, fill=(255, 255, 255, 255))
                
                # Content Box
                draw.rectangle([(300, y), (WIDTH - 120, y + 80)], fill=(18, 25, 36, 255), outline=(45, 60, 85, 255), width=1)
                draw.text((330, y + 14), title_str, font=FONT_LABEL, fill=(230, 235, 245, 255))
                draw.text((330, y + 44), note_str, font=FONT_TICKER, fill=(160, 180, 200, 255))
                
                # Right side value
                draw.text((WIDTH - 520, y + 22), val_str, font=FONT_TITLE, fill=col)
                
        frames.append(base)
        
    render_video_from_frames(frames, GRAPHICS_DIR / "graphic_04_intraday_countdown.mp4")

# Graphic 5: Bailout & Restructure Flowchart
def build_bailout_rescue_graphic():
    frames = []
    num_frames = 75
    
    for f_idx in range(num_frames):
        prog = f_idx / (num_frames - 1)
        base = create_base_terminal(
            title="SWISS FEDERAL BAILOUT & 'PROJECT PHOENIX' RESTRUCTURING",
            subtitle="EMERGENCY STATE CAPITAL INJECTION",
            tag="GOVERNMENT INTERVENTION // CRISIS RESOLUTION"
        )
        draw = ImageDraw.Draw(base)
        
        # Left Box: Swiss Federal Council
        p1 = min(1.0, prog / 0.35)
        if p1 > 0:
            draw.rectangle([(140, 240), (740, 520)], fill=(20, 28, 42, 245), outline=(212, 175, 55, 255), width=2)
            draw.text((170, 265), "SWISS BUNDESRAT (BERN)", font=FONT_TITLE, fill=(255, 255, 255, 255))
            draw.text((170, 325), "EMERGENCY CABINET BAILOUT:", font=FONT_LABEL, fill=(212, 175, 55, 255))
            draw.text((170, 365), "CHF 450,000,000", font=FONT_BIG, fill=(255, 215, 80, 255))
            draw.text((170, 445), "VOTED TO RESTORE ESSENTIAL FLIGHTS", font=FONT_TICKER, fill=(180, 195, 215, 255))
            
        # Right Box: Bank Consortium
        p2 = min(1.0, max(0.0, (prog - 0.25) / 0.35))
        if p2 > 0:
            draw.rectangle([(WIDTH - 740, 240), (WIDTH - 140, 520)], fill=(20, 28, 42, 245), outline=(75, 120, 185, 255), width=2)
            draw.text((WIDTH - 710, 265), "BANK CONSORTIUM (UBS / CS)", font=FONT_TITLE, fill=(255, 255, 255, 255))
            draw.text((WIDTH - 710, 325), "CROSSAIR TAKEOVER FINANCING:", font=FONT_LABEL, fill=(80, 160, 255, 255))
            draw.text((WIDTH - 710, 365), "CHF 1,450,000,000", font=FONT_BIG, fill=(100, 180, 255, 255))
            draw.text((WIDTH - 710, 445), "PURCHASED OPERATIONAL FLEET ONLY", font=FONT_TICKER, fill=(180, 195, 215, 255))
            
        # Bottom Result Banner
        p3 = min(1.0, max(0.0, (prog - 0.55) / 0.35))
        if p3 > 0:
            draw.rectangle([(240, 620), (WIDTH - 240, 820)], fill=(15, 22, 34, 250), outline=(235, 45, 45, 255), width=3)
            draw.text((280, 650), "FINAL OUTCOME: HISTORIC SWISSAIR LIQUIDATED", font=FONT_TITLE, fill=(255, 75, 75, 255))
            draw.text((280, 710), "OLD SWISSAIR 17B DEBT LEFT IN BANKRUPTCY ESTATE", font=FONT_LABEL, fill=(240, 240, 245, 255))
            draw.text((280, 750), "REBORN AS: SWISS INTERNATIONAL AIR LINES (NOW LUFTHANSA GROUP)", font=FONT_TICKER, fill=(212, 175, 55, 255))
            
        frames.append(base)
        
    render_video_from_frames(frames, GRAPHICS_DIR / "graphic_05_bailout_rescue.mp4")

if __name__ == "__main__":
    print("Generating 5 Dedicated Financial & Trading Explainer Motion Graphics...")
    build_stock_crash_graphic()
    build_debt_spiral_graphic()
    build_hunter_network_graphic()
    build_intraday_countdown_graphic()
    build_bailout_rescue_graphic()
    print("All 5 Financial Graphics successfully created!")
