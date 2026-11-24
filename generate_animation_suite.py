import os
import sys
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import subprocess
from pathlib import Path

BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
ANIM_DIR = BASE_DIR / "data" / "media" / "animations" / "swiss-air-grounding-prod"
ANIM_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 1920
HEIGHT = 1080
FPS = 24

def save_and_reencode(temp_raw: Path, final_mp4: Path):
    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_raw),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(final_mp4)
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    temp_raw.unlink(missing_ok=True)
    print(f"  -> Generated {final_mp4.name} ({final_mp4.stat().st_size / (1024*1024):.2f} MB)")

# ==========================================
# 1. ANIMATED MAP (Vox / Johnny Harris style)
# ==========================================
def render_anim_01_map(out_path: Path, dur_sec: float = 6.0):
    print("Rendering 1/10: Animated Map (Flight Radar & European Airspace)...")
    temp_raw = out_path.with_suffix(".temp.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(temp_raw), fourcc, FPS, (WIDTH, HEIGHT))
    total_frames = int(dur_sec * FPS)

    nodes = {
        "Zurich": (960, 560),
        "Brussels": (760, 410),
        "Paris": (660, 480),
        "Frankfurt": (930, 400),
        "London": (590, 350),
        "New York": (180, 520)
    }

    for f in range(total_frames):
        p = f / float(total_frames)
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        frame[:] = (20, 16, 12) # Dark navy

        # Cartographic Grid
        for x in range(0, WIDTH, 100):
            cv2.line(frame, (x, 0), (x, HEIGHT), (35, 28, 20), 1)
        for y in range(0, HEIGHT, 100):
            cv2.line(frame, (0, y), (WIDTH, y), (35, 28, 20), 1)

        # Draw European boundary
        poly_pts = np.array([[500, 260], [1250, 260], [1320, 780], [450, 780]], np.int32)
        cv2.polylines(frame, [poly_pts], True, (55, 45, 35), 2)
        cv2.putText(frame, "EUROPEAN ECONOMIC AREA (EEA) - DEREGULATED SKIES", (520, 245),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (160, 140, 100), 1, cv2.LINE_AA)

        # Switzerland central pulse
        zh = nodes["Zurich"]
        pulse_r = int(45 + 12 * math.sin(p * 8 * math.pi))
        cv2.circle(frame, zh, pulse_r, (40, 40, 180), -1)
        cv2.circle(frame, zh, pulse_r + 6, (80, 80, 240), 2)
        cv2.circle(frame, zh, pulse_r + 16, (50, 50, 150), 1)

        # Radiating vector corridors
        reach = min(1.0, p * 1.5)
        for name, coord in nodes.items():
            if name == "Zurich":
                continue
            cur_x = int(zh[0] + (coord[0] - zh[0]) * reach)
            cur_y = int(zh[1] + (coord[1] - zh[1]) * reach)
            # Glowing line
            cv2.line(frame, zh, (cur_x, cur_y), (240, 180, 40), 2, cv2.LINE_AA)
            cv2.circle(frame, (cur_x, cur_y), 5, (255, 220, 80), -1)
            cv2.putText(frame, name, (coord[0] + 10, coord[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (230, 230, 230), 1, cv2.LINE_AA)

        # Highlight denial over Paris/Brussels if p > 0.5
        if p > 0.5:
            cv2.putText(frame, "ACCESS DENIED - 49% CABOTAGE CAP", (620, 450),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (40, 40, 240), 2, cv2.LINE_AA)

        # Header HUD
        cv2.rectangle(frame, (60, 60), (950, 150), (14, 12, 10), -1)
        cv2.rectangle(frame, (60, 60), (66, 150), (220, 180, 60), -1)
        cv2.putText(frame, "GEOGRAPHIC DOSSIER: SWISS AIRSPACE ENTRAPMENT", (85, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "DECEMBER 1992 REFERENDUM: SWITZERLAND REJECTS EEA ENTRY", (85, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 170, 70), 1, cv2.LINE_AA)

        # Radar scanner sweep
        angle = p * 4 * math.pi
        sweep_x = int(zh[0] + 350 * math.cos(angle))
        sweep_y = int(zh[1] + 350 * math.sin(angle))
        cv2.line(frame, zh, (sweep_x, sweep_y), (100, 80, 30), 1, cv2.LINE_AA)

        writer.write(frame)

    writer.release()
    save_and_reencode(temp_raw, out_path)

# ==========================================
# 2. FINANCIAL CRASH CHART (Data Visualization)
# ==========================================
def render_anim_02_chart(out_path: Path, dur_sec: float = 6.0):
    print("Rendering 2/10: Financial Crash Chart (Data Visualization)...")
    temp_raw = out_path.with_suffix(".temp.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(temp_raw), fourcc, FPS, (WIDTH, HEIGHT))
    total_frames = int(dur_sec * FPS)

    points = [
        ("1998", 280, 760, 0.8),
        ("1999", 580, 640, 1.8),
        ("2000", 880, 460, 3.2),
        ("2001", 1180, 260, 4.2)
    ]

    for f in range(total_frames):
        p = f / float(total_frames)
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        frame[:] = (16, 12, 10)

        # Grid
        for y in range(200, 850, 100):
            cv2.line(frame, (180, y), (1450, y), (35, 28, 22), 1)

        # Axes
        cv2.line(frame, (180, 820), (1450, 820), (90, 80, 70), 2)
        cv2.line(frame, (180, 180), (180, 820), (90, 80, 70), 2)

        # Plot points & curve
        active_pts = []
        for year, x, y, val in points:
            t_thresh = (x - 200) / 1200.0
            if p >= t_thresh:
                active_pts.append((x, y))
                cv2.circle(frame, (x, y), 8, (50, 50, 240), -1)
                cv2.circle(frame, (x, y), 14, (80, 80, 255), 2)
                cv2.putText(frame, year, (x - 25, 855), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (180, 180, 180), 1, cv2.LINE_AA)
                cv2.putText(frame, f"{val:.1f}B CHF", (x - 50, y - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 130, 255), 2, cv2.LINE_AA)

        if len(active_pts) > 1:
            for i in range(len(active_pts) - 1):
                cv2.line(frame, active_pts[i], active_pts[i+1], (40, 40, 240), 5, cv2.LINE_AA)

        # Ticking counter
        debt_amt = int(4200000000 * min(1.0, p * 1.3))
        cv2.rectangle(frame, (1150, 80), (1800, 190), (12, 10, 8), -1)
        cv2.rectangle(frame, (1150, 80), (1158, 190), (40, 40, 240), -1)
        cv2.putText(frame, f"{debt_amt:,} CHF", (1175, 135), cv2.FONT_HERSHEY_SIMPLEX, 1.05, (50, 60, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "TOTAL SAIRGROUP ACCUMULATED DEBT", (1175, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA)

        # Header
        cv2.putText(frame, "FORENSIC AUDIT: THE CATASTROPHIC DEBT EXPLOSION", (80, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "E&Y SPECIAL LIQUIDATION REPORT (1998 - 2001)", (80, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 180, 60), 1, cv2.LINE_AA)

        writer.write(frame)

    writer.release()
    save_and_reencode(temp_raw, out_path)

# ==========================================
# 3. KINETIC TYPOGRAPHY ("THE COLLAPSE")
# ==========================================
def render_anim_03_kinetic_type(out_path: Path, dur_sec: float = 5.0):
    print("Rendering 3/10: Kinetic Typography (The Grounding Moment)...")
    temp_raw = out_path.with_suffix(".temp.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(temp_raw), fourcc, FPS, (WIDTH, HEIGHT))
    total_frames = int(dur_sec * FPS)

    for f in range(total_frames):
        p = f / float(total_frames)
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        frame[:] = (10, 10, 12)

        # Phase 1: 0 - 30% -> OCTOBER 2, 2001
        if p < 0.32:
            scale_p = min(1.0, p / 0.15)
            font_size = 1.6 + 0.3 * (1.0 - scale_p)
            cv2.putText(frame, "OCTOBER 2, 2001", (WIDTH//2 - 420, HEIGHT//2 - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 255, 255), 4, cv2.LINE_AA)
            cv2.putText(frame, "ZURICH-KLOTEN INTERNATIONAL AIRPORT", (WIDTH//2 - 380, HEIGHT//2 + 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (220, 180, 60), 2, cv2.LINE_AA)

        # Phase 2: 32% - 65% -> 12:30 PM: FUEL REFUSED
        elif p < 0.65:
            p_sub = (p - 0.32) / 0.33
            # Red flash on transition
            if p_sub < 0.1:
                frame[:] = (40, 20, 20)
            cv2.putText(frame, "12:30 PM", (WIDTH//2 - 220, HEIGHT//2 - 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2.0, (40, 40, 240), 5, cv2.LINE_AA)
            cv2.putText(frame, "BP FUEL TRUCKS ORDERED TO HALT SERVICE", (WIDTH//2 - 480, HEIGHT//2 + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (240, 240, 240), 2, cv2.LINE_AA)
            cv2.putText(frame, "REASON: SWISSAIR CASH ACCOUNTS ARE EMPTY", (WIDTH//2 - 420, HEIGHT//2 + 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 160, 60), 1, cv2.LINE_AA)

        # Phase 3: 65% - 100% -> FLEET GROUNDED
        else:
            p_sub = (p - 0.65) / 0.35
            # Heavy red strobe
            pulse = int(20 * math.sin(p_sub * 10 * math.pi))
            r_val = max(0, min(255, 30 + pulse))
            frame[:] = (r_val, 10, 12)
            cv2.putText(frame, "GROUNDED", (WIDTH//2 - 380, HEIGHT//2 - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 2.6, (30, 30, 240), 7, cv2.LINE_AA)
            cv2.putText(frame, "ENTIRE GLOBAL FLEET ORDERED TO STAND STILL", (WIDTH//2 - 460, HEIGHT//2 + 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, "38,000 PASSENGERS STRANDED WORLDWIDE", (WIDTH//2 - 390, HEIGHT//2 + 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 180, 60), 2, cv2.LINE_AA)

        writer.write(frame)

    writer.release()
    save_and_reencode(temp_raw, out_path)

# ==========================================
# 4. HISTORICAL DOCUMENT REVEAL (Highlighter & Stamp)
# ==========================================
def render_anim_04_document(out_path: Path, dur_sec: float = 6.0):
    print("Rendering 4/10: Document Reconstruction (Highlighter Wipe & Stamp)...")
    temp_raw = out_path.with_suffix(".temp.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(temp_raw), fourcc, FPS, (WIDTH, HEIGHT))
    total_frames = int(dur_sec * FPS)

    headline = "SPECIAL INVESTIGATION REPORT - SAIRGROUP LIQUIDATION"
    highlight_text = "OFF-BALANCE-SHEET GUARANTEES EXCEEDED 4.2 BILLION CHF"

    lines = [
        "Pursuant to Article 42 of the Swiss Aviation Act, the special liquidators examined",
        "all off-balance-sheet agreements executed by SAirGroup executives between 1998 and 2001.",
        "The findings confirm that multiple guarantees were provided without board authorization.",
        highlight_text,
        "As a consequence, liquidity was exhausted prior to the scheduled October asset transfer."
    ]

    for f in range(total_frames):
        p = f / float(total_frames)
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        frame[:] = (225, 235, 240) # Aged paper

        # Document border
        cv2.rectangle(frame, (180, 90), (1740, 990), (150, 160, 170), 2)
        cv2.rectangle(frame, (190, 100), (1730, 980), (190, 200, 210), 1)

        # Header
        cv2.putText(frame, "CONFIDENTIAL / SWISS FEDERAL AUDIT COMMISSION", (240, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 110), 2, cv2.LINE_AA)
        cv2.putText(frame, headline, (240, 220),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 20), 2, cv2.LINE_AA)

        # Body text
        y_pos = 320
        for line in lines:
            if line == highlight_text:
                hl_w = int(1220 * min(1.0, max(0.0, (p - 0.25) * 2.2)))
                if hl_w > 0:
                    overlay = frame.copy()
                    cv2.rectangle(overlay, (230, y_pos - 32), (230 + hl_w, y_pos + 12), (0, 235, 255), -1) # Yellow
                    cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)
                cv2.putText(frame, line, (240, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (10, 10, 10), 2, cv2.LINE_AA)
            else:
                cv2.putText(frame, line, (240, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.68, (60, 60, 60), 1, cv2.LINE_AA)
            y_pos += 68

        # Red Stamp Slam at p > 0.6
        if p > 0.6:
            stamp_p = min(1.0, (p - 0.6) / 0.15)
            # Stamp coordinates
            sx, sy = 1450, 750
            r = max(10, int(75 * stamp_p))
            cv2.circle(frame, (sx, sy), r, (30, 30, 200), 4)
            cv2.circle(frame, (sx, sy), max(2, r - 8), (30, 30, 200), 1)
            cv2.putText(frame, "CONFIDENTIAL", (sx - 65, sy - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (30, 30, 200), 2, cv2.LINE_AA)
            cv2.putText(frame, "CLASSIFIED", (sx - 55, sy + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (30, 30, 200), 2, cv2.LINE_AA)

        writer.write(frame)

    writer.release()
    save_and_reencode(temp_raw, out_path)

# ==========================================
# 5. 2.5D PARALLAX (Executive Depth & Light Streak)
# ==========================================
def render_anim_05_parallax(out_path: Path, dur_sec: float = 5.5):
    print("Rendering 5/10: 2.5D Parallax Animation (Executive Dossier)...")
    temp_raw = out_path.with_suffix(".temp.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(temp_raw), fourcc, FPS, (WIDTH, HEIGHT))
    total_frames = int(dur_sec * FPS)

    for f in range(total_frames):
        p = f / float(total_frames)
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

        # Background: slow moving boardroom bokeh
        bg_drift = int(40 * p)
        frame[:] = (22, 18, 16)
        # Soft blurred lights in background
        cv2.circle(frame, (350 + bg_drift, 300), 180, (35, 28, 22), -1)
        cv2.circle(frame, (1400 - bg_drift, 450), 220, (30, 25, 20), -1)

        # Foreground 2.5D Executive Silhouette sliding at different speed
        fg_drift = int(70 * p)
        cx = 960 + fg_drift
        cy = 580
        # Draw executive silhouette
        cv2.circle(frame, (cx, cy - 140), 90, (12, 10, 8), -1) # Head
        pts = np.array([[cx - 220, cy + 300], [cx - 160, cy - 40], [cx + 160, cy - 40], [cx + 220, cy + 300]], np.int32)
        cv2.fillPoly(frame, [pts], (12, 10, 8)) # Shoulders / suit

        # Anamorphic Light Streak sweeping across lens
        flare_x = int(WIDTH * (p * 1.4 - 0.2))
        cv2.line(frame, (flare_x - 300, 380), (flare_x + 300, 380), (220, 180, 60), 2, cv2.LINE_AA)
        cv2.circle(frame, (flare_x, 380), 20, (255, 240, 140), -1)

        # Dossier Card
        cv2.rectangle(frame, (100, 860), (1200, 960), (14, 12, 10), -1)
        cv2.rectangle(frame, (100, 860), (110, 960), (220, 180, 60), -1)
        cv2.putText(frame, "EXECUTIVE DOSSIER: PHILIPPE BRUGGISSER", (135, 900), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (220, 180, 60), 2, cv2.LINE_AA)
        cv2.putText(frame, "ARCHITECT OF THE HUNTER STRATEGY • PURSUED DEBT EXPANSION", (135, 935), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (230, 235, 240), 1, cv2.LINE_AA)

        writer.write(frame)

    writer.release()
    save_and_reencode(temp_raw, out_path)

# ==========================================
# 6. HUD / SURVEILLANCE INTERFACE
# ==========================================
def render_anim_06_hud(out_path: Path, dur_sec: float = 5.0):
    print("Rendering 6/10: HUD / Surveillance Interface (Fuel Refusal Alert)...")
    temp_raw = out_path.with_suffix(".temp.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(temp_raw), fourcc, FPS, (WIDTH, HEIGHT))
    total_frames = int(dur_sec * FPS)

    for f in range(total_frames):
        p = f / float(total_frames)
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        frame[:] = (12, 14, 16) # Night monitoring tint

        # HUD Corner Brackets
        c_len = 80
        # Top-Left
        cv2.line(frame, (80, 80), (80 + c_len, 80), (0, 200, 120), 2)
        cv2.line(frame, (80, 80), (80, 80 + c_len), (0, 200, 120), 2)
        # Top-Right
        cv2.line(frame, (WIDTH - 80, 80), (WIDTH - 80 - c_len, 80), (0, 200, 120), 2)
        cv2.line(frame, (WIDTH - 80, 80), (WIDTH - 80, 80 + c_len), (0, 200, 120), 2)
        # Bottom-Left
        cv2.line(frame, (80, HEIGHT - 80), (80 + c_len, HEIGHT - 80), (0, 200, 120), 2)
        cv2.line(frame, (80, HEIGHT - 80), (80, HEIGHT - 80 - c_len), (0, 200, 120), 2)
        # Bottom-Right
        cv2.line(frame, (WIDTH - 80, HEIGHT - 80), (WIDTH - 80 - c_len, HEIGHT - 80), (0, 200, 120), 2)
        cv2.line(frame, (WIDTH - 80, HEIGHT - 80), (WIDTH - 80, HEIGHT - 80 - c_len), (0, 200, 120), 2)

        # Center Targeting Reticle
        cx, cy = WIDTH // 2, HEIGHT // 2
        cv2.circle(frame, (cx, cy), 120, (0, 180, 100), 1)
        cv2.circle(frame, (cx, cy), 8, (0, 220, 120), -1)
        cv2.line(frame, (cx - 150, cy), (cx - 40, cy), (0, 180, 100), 1)
        cv2.line(frame, (cx + 40, cy), (cx + 150, cy), (0, 180, 100), 1)
        cv2.line(frame, (cx, cy - 150), (cx, cy - 40), (0, 180, 100), 1)
        cv2.line(frame, (cx, cy + 40), (cx, cy + 150), (0, 180, 100), 1)

        # Running Technical Timecode
        sec = int(p * 5.0)
        msec = int((p * 5.0 - sec) * 100)
        cv2.putText(frame, f"REC ● 12:30:{14 + sec:02d}.{msec:02d} KLOTEN-TOWER", (120, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (40, 60, 240), 2, cv2.LINE_AA)

        # Audio Waveform Visualizer Bars
        for b in range(24):
            bar_h = int(15 + 40 * abs(math.sin(p * 20 + b * 0.4)))
            bx = 120 + b * 18
            cv2.line(frame, (bx, 960), (bx, 960 - bar_h), (0, 220, 140), 3)

        # Blinking Alert Banner
        blink = (int(p * 8) % 2) == 0
        if blink:
            cv2.rectangle(frame, (WIDTH//2 - 450, HEIGHT - 180), (WIDTH//2 + 450, HEIGHT - 100), (20, 20, 220), -1)
            cv2.putText(frame, "CRITICAL ALERT: FLIGHT 157 REFUSED FUEL DISPENSATION", (WIDTH//2 - 420, HEIGHT - 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

        writer.write(frame)

    writer.release()
    save_and_reencode(temp_raw, out_path)

# ==========================================
# 7. 2D MOTION GRAPHICS ("HUNTER STRATEGY")
# ==========================================
def render_anim_07_hunter_wheel(out_path: Path, dur_sec: float = 6.0):
    print("Rendering 7/10: 2D Motion Graphics (The Hunter Strategy Wheel)...")
    temp_raw = out_path.with_suffix(".temp.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(temp_raw), fourcc, FPS, (WIDTH, HEIGHT))
    total_frames = int(dur_sec * FPS)

    subs = [
        ("SABENA (BELGIUM)", "49.5% STAKE", (550, 360)),
        ("LTU (GERMANY)", "49.9% STAKE", (1370, 360)),
        ("AOM (FRANCE)", "49.0% STAKE", (550, 720)),
        ("VOLARE (ITALY)", "49.8% STAKE", (1370, 720))
    ]

    for f in range(total_frames):
        p = f / float(total_frames)
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        frame[:] = (18, 14, 12)

        cx, cy = WIDTH // 2, HEIGHT // 2

        # Central Swissair Hub
        cv2.circle(frame, (cx, cy), 95, (40, 40, 220), -1) # Swiss Red
        cv2.circle(frame, (cx, cy), 105, (220, 180, 60), 3)
        # White Swiss Cross
        cv2.rectangle(frame, (cx - 16, cy - 50), (cx + 16, cy + 50), (255, 255, 255), -1)
        cv2.rectangle(frame, (cx - 50, cy - 16), (cx + 50, cy + 16), (255, 255, 255), -1)
        cv2.putText(frame, "SAirGroup", (cx - 55, cy + 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 2, cv2.LINE_AA)

        # Radiating Spokes & Satellite Nodes
        reach = min(1.0, p * 1.4)
        for name, stake, (sx, sy) in subs:
            nx = int(cx + (sx - cx) * reach)
            ny = int(cy + (sy - cy) * reach)

            # Cash drain line
            cv2.line(frame, (cx, cy), (nx, ny), (220, 160, 40), 2, cv2.LINE_AA)
            cv2.circle(frame, (nx, ny), 45, (30, 25, 20), -1)
            cv2.circle(frame, (nx, ny), 45, (40, 40, 200), 2)
            cv2.putText(frame, name, (nx - 110, ny + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, stake, (nx - 60, ny + 95), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 180, 60), 1, cv2.LINE_AA)

        # Header
        cv2.putText(frame, "THE HUNTER STRATEGY: MINORITY ACQUISITION WHEEL", (80, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "ACQUIRED CHRONICALLY UNPROFITABLE CARRIERS TO BYPASS CABOTAGE RULES", (80, 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (200, 170, 70), 1, cv2.LINE_AA)

        writer.write(frame)

    writer.release()
    save_and_reencode(temp_raw, out_path)

# ==========================================
# 8. INFOGRAPHIC ANIMATION (Liquidity Burn)
# ==========================================
def render_anim_08_infographic(out_path: Path, dur_sec: float = 5.5):
    print("Rendering 8/10: Infographic Animation (Liquidity Burn Dashboard)...")
    temp_raw = out_path.with_suffix(".temp.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(temp_raw), fourcc, FPS, (WIDTH, HEIGHT))
    total_frames = int(dur_sec * FPS)

    for f in range(total_frames):
        p = f / float(total_frames)
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        frame[:] = (14, 14, 16)

        # Card 1: Liquidity Dial (Left)
        cv2.rectangle(frame, (100, 200), (850, 850), (22, 22, 26), -1)
        cv2.rectangle(frame, (100, 200), (850, 850), (45, 45, 55), 2)
        cv2.putText(frame, "OPERATIONAL LIQUIDITY RESERVES", (140, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 180, 60), 2, cv2.LINE_AA)

        # Circular Gauge dropping to 0
        gx, gy = 475, 480
        gauge_p = max(0.0, 1.0 - p * 1.2)
        cv2.circle(frame, (gx, gy), 140, (35, 35, 45), 16)
        # Active arc
        end_angle = int(360 * gauge_p)
        if end_angle > 0:
            cv2.ellipse(frame, (gx, gy), (140, 140), 0, -90, -90 + end_angle, (40, 60, 240), 16)
        cv2.putText(frame, f"{int(gauge_p * 100)}%", (gx - 55, gy + 20), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 255, 255), 4, cv2.LINE_AA)
        cv2.putText(frame, "STATUS: INSOLVENT (0 CHF)", (gx - 160, gy + 220), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (40, 40, 240), 2, cv2.LINE_AA)

        # Card 2: Stock Crash Meter (Right)
        cv2.rectangle(frame, (920, 200), (1820, 850), (22, 22, 26), -1)
        cv2.rectangle(frame, (920, 200), (1820, 850), (45, 45, 55), 2)
        cv2.putText(frame, "SAIRGROUP (SWX) STOCK PRICE COLLAPSE", (960, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 180, 60), 2, cv2.LINE_AA)

        price = int(400 - (400 - 14) * min(1.0, p * 1.2))
        cv2.putText(frame, f"{price} CHF", (1000, 440), cv2.FONT_HERSHEY_SIMPLEX, 2.4, (40, 40, 240), 5, cv2.LINE_AA)
        cv2.putText(frame, "-96.5% VALUE ERADICATED", (1000, 520), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (220, 60, 60), 2, cv2.LINE_AA)
        cv2.putText(frame, "PEAK: 400 CHF (1998) -> CRASH: 14 CHF (OCT 2001)", (1000, 590), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1, cv2.LINE_AA)

        # Header
        cv2.putText(frame, "FINANCIAL METRICS: THE FINAL HOURS BEFORE SHUTDOWN", (80, 95),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        writer.write(frame)

    writer.release()
    save_and_reencode(temp_raw, out_path)

# ==========================================
# 9. 3D OBJECT / BANK VAULT ANIMATION
# ==========================================
def render_anim_09_vault(out_path: Path, dur_sec: float = 5.5):
    print("Rendering 9/10: 3D Cinematic Vault Animation (Bank of the Skies)...")
    temp_raw = out_path.with_suffix(".temp.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(temp_raw), fourcc, FPS, (WIDTH, HEIGHT))
    total_frames = int(dur_sec * FPS)

    for f in range(total_frames):
        p = f / float(total_frames)
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        frame[:] = (12, 12, 14)

        # 3D Perspective Vault Room
        # Back wall
        cv2.rectangle(frame, (400, 200), (1520, 880), (22, 22, 26), -1)
        # Vault perspective walls
        cv2.line(frame, (0, 0), (400, 200), (45, 45, 50), 2)
        cv2.line(frame, (WIDTH, 0), (1520, 200), (45, 45, 50), 2)
        cv2.line(frame, (0, HEIGHT), (400, 880), (45, 45, 50), 2)
        cv2.line(frame, (WIDTH, HEIGHT), (1520, 880), (45, 45, 50), 2)

        # Stacked 3D Gold Bars in Center
        gold_drift = int(15 * math.sin(p * 2 * math.pi))
        for layer in range(3):
            ly = 680 - layer * 55
            for col in range(4 - layer):
                lx = 760 + col * 120 + layer * 60 + gold_drift
                # Front face
                cv2.rectangle(frame, (lx, ly), (lx + 100, ly + 45), (30, 180, 225), -1) # Gold BGR
                # Top face (perspective 3D)
                pts_top = np.array([[lx, ly], [lx + 20, ly - 15], [lx + 120, ly - 15], [lx + 100, ly]], np.int32)
                cv2.fillPoly(frame, [pts_top], (60, 210, 250))
                # Side face
                pts_side = np.array([[lx + 100, ly], [lx + 120, ly - 15], [lx + 120, ly + 30], [lx + 100, ly + 45]], np.int32)
                cv2.fillPoly(frame, [pts_side], (20, 140, 190))

        # Heavy Vault Door Closing Overlay at p > 0.65
        if p > 0.65:
            door_p = (p - 0.65) / 0.35
            door_w = int(WIDTH // 2 * door_p)
            # Left door
            cv2.rectangle(frame, (0, 0), (door_w, HEIGHT), (16, 18, 22), -1)
            cv2.line(frame, (door_w, 0), (door_w, HEIGHT), (220, 180, 60), 4)
            # Right door
            cv2.rectangle(frame, (WIDTH - door_w, 0), (WIDTH, HEIGHT), (16, 18, 22), -1)
            cv2.line(frame, (WIDTH - door_w, 0), (WIDTH - door_w, HEIGHT), (220, 180, 60), 4)

        # Header
        cv2.putText(frame, "THE FLYING BANK: SWITZERLAND'S NATIONAL BULWARK", (80, 95),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "AAA SOVEREIGN CREDIT STANDING ERADICATED IN 48 HOURS", (80, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (220, 180, 60), 1, cv2.LINE_AA)

        writer.write(frame)

    writer.release()
    save_and_reencode(temp_raw, out_path)

# ==========================================
# 10. PARTICLE / ATMOSPHERIC EMBERS
# ==========================================
def render_anim_10_embers(out_path: Path, dur_sec: float = 5.5):
    print("Rendering 10/10: Particle Animation (Atmospheric Glowing Embers)...")
    temp_raw = out_path.with_suffix(".temp.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(temp_raw), fourcc, FPS, (WIDTH, HEIGHT))
    total_frames = int(dur_sec * FPS)

    # Initialize 75 particles with random (x, y, vx, vy, size, hue)
    np.random.seed(42)
    particles = []
    for _ in range(80):
        particles.append({
            "x": np.random.uniform(100, WIDTH - 100),
            "y": np.random.uniform(200, HEIGHT + 100),
            "vx": np.random.uniform(-0.8, 0.8),
            "vy": np.random.uniform(-2.5, -0.8),
            "size": np.random.randint(2, 6),
            "brightness": np.random.randint(180, 255)
        })

    for f in range(total_frames):
        p = f / float(total_frames)
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        frame[:] = (10, 8, 8) # Smokey charcoal

        # Silhouette of grounded airliner tail with Swiss Cross
        tail_x = 960
        tail_pts = np.array([[tail_x - 140, 850], [tail_x - 40, 320], [tail_x + 90, 320], [tail_x + 180, 850]], np.int32)
        cv2.fillPoly(frame, [tail_pts], (22, 16, 16))
        # Swiss red square
        cv2.rectangle(frame, (tail_x - 20, 420), (tail_x + 70, 510), (30, 30, 190), -1)
        # White cross
        cv2.rectangle(frame, (tail_x + 15, 435), (tail_x + 35, 495), (240, 240, 240), -1)
        cv2.rectangle(frame, (tail_x - 5, 455), (tail_x + 55, 475), (240, 240, 240), -1)

        # Update and draw floating embers
        for pt in particles:
            pt["x"] += pt["vx"] + 0.5 * math.sin(f * 0.1)
            pt["y"] += pt["vy"]
            if pt["y"] < 50:
                pt["y"] = HEIGHT + np.random.uniform(10, 50)
                pt["x"] = np.random.uniform(100, WIDTH - 100)

            px, py = int(pt["x"]), int(pt["y"])
            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                b = pt["brightness"]
                cv2.circle(frame, (px, py), pt["size"], (20, int(b * 0.6), b), -1)
                # Soft glow
                cv2.circle(frame, (px, py), pt["size"] + 3, (10, int(b * 0.3), int(b * 0.7)), 1)

        # Dramatic Text Reveal
        cv2.putText(frame, "OCTOBER 2, 2001", (WIDTH//2 - 240, 750),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(frame, "THE COLLAPSE OF AN UNTOUCHABLE EMPIRE", (WIDTH//2 - 380, 800),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 180, 60), 2, cv2.LINE_AA)

        writer.write(frame)

    writer.release()
    save_and_reencode(temp_raw, out_path)

def main():
    print("=== COMMENCING MASTER ANIMATION SUITE GENERATION (10 POPULAR DOCUMENTARY STYLES) ===")
    render_anim_01_map(ANIM_DIR / "anim_01_map.mp4")
    render_anim_02_chart(ANIM_DIR / "anim_02_chart.mp4")
    render_anim_03_kinetic_type(ANIM_DIR / "anim_03_kinetic_type.mp4")
    render_anim_04_document(ANIM_DIR / "anim_04_document.mp4")
    render_anim_05_parallax(ANIM_DIR / "anim_05_parallax.mp4")
    render_anim_06_hud(ANIM_DIR / "anim_06_hud.mp4")
    render_anim_07_hunter_wheel(ANIM_DIR / "anim_07_hunter_wheel.mp4")
    render_anim_08_infographic(ANIM_DIR / "anim_08_infographic.mp4")
    render_anim_09_vault(ANIM_DIR / "anim_09_vault.mp4")
    render_anim_10_embers(ANIM_DIR / "anim_10_embers.mp4")
    print("=== ALL 10 DOCUMENTARY ANIMATIONS SUCCESSFULLY GENERATED! ===")

if __name__ == "__main__":
    main()
