"""
DocuForge AI - Agent 9: Cinematic Visual and Animation Director
Builds animated maps, financial data visualizations, document text reveals,
and photo Ken Burns motions as 1080p broadcast video clips using OpenCV, PIL, and FFmpeg.
"""
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..database import get_connection
from ..config import MEDIA_DIR
from ..core.budget_engine import BudgetEngine
from .storyboard import StoryboardEngine

logger = logging.getLogger("docuforge.agents.animation_director")

ANIMATIONS_DIR = MEDIA_DIR / "animations"
ANIMATIONS_DIR.mkdir(parents=True, exist_ok=True)
BROLL_CACHE_DIR = MEDIA_DIR / "broll_cache"
BROLL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

BROLL_LIBRARY = {
    "AIRPORT_TARMAC": "https://cdn.pixabay.com/video/2016/11/15/6414-191719619_medium.mp4",
    "COCKPIT_FLIGHT": "https://cdn.pixabay.com/video/2015/08/10/242-135867058_medium.mp4",
    "JET_TAKEOFF": "https://cdn.pixabay.com/video/2020/02/27/32975-394513987_medium.mp4",
    "BOARDROOM_MEETING": "https://cdn.pixabay.com/video/2015/10/27/1191-143842658_medium.mp4",
    "EXECUTIVE_BUSINESS": "https://cdn.pixabay.com/video/2016/02/29/2340-157269921_medium.mp4",
    "STOCK_MARKET_CRASH": "https://cdn.pixabay.com/video/2020/03/19/33974-399148659_medium.mp4",
    "COUNTING_MONEY": "https://cdn.pixabay.com/video/2020/09/23/50622-460909288_medium.mp4",
    "BANK_FINANCE": "https://cdn.pixabay.com/video/2023/07/23/172892-848187888_medium.mp4",
    "CAMERA_REPORTER": "https://cdn.pixabay.com/video/2025/11/28/318654_medium.mp4",
    "NEWS_BROADCAST": "https://cdn.pixabay.com/video/2019/12/08/29982-378308905_medium.mp4",
    "PASSENGER_TERMINAL": "https://cdn.pixabay.com/video/2020/04/18/36510-411342239_medium.mp4",
    "RAIN_RUNWAY": "https://cdn.pixabay.com/video/2015/08/10/283-135881214_medium.mp4",
    "CLOUDS_FLIGHT": "https://cdn.pixabay.com/video/2015/10/23/1154-143492926_medium.mp4"
}

class CinematicAnimationDirector:
    WIDTH = 1920
    HEIGHT = 1080
    FPS = 30

    @classmethod
    def _encode_or_fallback(cls, temp_raw: Path, output_path: Path, duration_sec: float) -> str:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if temp_raw.exists() and temp_raw.stat().st_size > 1000:
            cmd = ["ffmpeg", "-y", "-i", str(temp_raw), "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", "-pix_fmt", "yuv420p", "-threads", "1", str(output_path)]
            try:
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                temp_raw.unlink(missing_ok=True)
                return str(output_path)
            except Exception as e:
                logger.warning("Temp re-encode failed: %s, falling back to lavfi", e)

        cmd_fallback = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=0x141824:s=1920x1080:d={duration_sec}",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-threads", "1",
            str(output_path)
        ]
        try:
            subprocess.run(cmd_fallback, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError as err:
            err_text = err.stderr.decode(errors="replace") if err.stderr else str(err)
            logger.error("FFmpeg fallback failed: %s", err_text)
            raise RuntimeError(f"FFmpeg render error: {err_text}")
        finally:
            temp_raw.unlink(missing_ok=True)
        return str(output_path)

    @classmethod
    def render_animated_map(
        cls,
        output_path: Path,
        duration_sec: float = 6.0,
        title: str = "EUROPEAN AIRSPACE & DEREGULATION CORRIDORS",
        subtitle: str = "SWITZERLAND: ISOLATED OUTSIDE EEA ZONE (1992-2001)"
    ) -> str:
        """
        Renders a 1080p animated geographic map with pulsing route vectors,
        territorial highlights, and satellite tracking.
        """
        total_frames = int(duration_sec * cls.FPS)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        temp_raw = output_path.with_suffix(".temp.mp4")
        writer = cv2.VideoWriter(str(temp_raw), fourcc, cls.FPS, (cls.WIDTH, cls.HEIGHT))

        # Base coordinates for simulated European nodes (Zurich, Brussels, Paris, Frankfurt, London)
        nodes = {
            "Zurich": (960, 560),
            "Brussels": (780, 430),
            "Paris": (680, 490),
            "Frankfurt": (920, 420),
            "London": (620, 370)
        }

        for f in range(total_frames):
            progress = f / float(total_frames)
            # Create dark navy cartographic background
            frame = np.zeros((cls.HEIGHT, cls.WIDTH, 3), dtype=np.uint8)
            frame[:] = (20, 16, 12)  # Dark blue-gray BGR

            # Draw cartographic grid lines
            for x in range(0, cls.WIDTH, 120):
                cv2.line(frame, (x, 0), (x, cls.HEIGHT), (35, 28, 22), 1)
            for y in range(0, cls.HEIGHT, 120):
                cv2.line(frame, (0, y), (cls.WIDTH, y), (35, 28, 22), 1)

            # Draw European airspace boundary zone
            poly_pts = np.array([[550, 250], [1250, 250], [1300, 750], [500, 750]], np.int32)
            cv2.polylines(frame, [poly_pts], True, (60, 50, 40), 2)

            # Highlight Switzerland territory in center
            swiss_center = nodes["Zurich"]
            swiss_radius = int(50 + 5 * np.sin(progress * 6 * np.pi))
            cv2.circle(frame, swiss_center, swiss_radius, (40, 40, 160), -1)  # Reddish accent
            cv2.circle(frame, swiss_center, swiss_radius + 4, (60, 60, 220), 2)

            # Animated route vectors radiating outward from Zurich
            current_reach = min(1.0, progress * 1.4)
            for name, coord in nodes.items():
                if name == "Zurich":
                    continue
                end_x = int(swiss_center[0] + (coord[0] - swiss_center[0]) * current_reach)
                end_y = int(swiss_center[1] + (coord[1] - swiss_center[1]) * current_reach)
                # Glowing route line
                cv2.line(frame, swiss_center, (end_x, end_y), (220, 160, 40), 2, cv2.LINE_AA)
                cv2.circle(frame, (end_x, end_y), 6, (240, 200, 60), -1)
                cv2.putText(frame, name, (coord[0] + 12, coord[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1, cv2.LINE_AA)

            # Central label
            cv2.putText(frame, "SWISS AIRSPACE [ISOLATED]", (swiss_center[0] - 130, swiss_center[1] + 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (100, 100, 255), 2, cv2.LINE_AA)

            # Header Banner
            cv2.putText(frame, title, (80, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, subtitle, (80, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 160, 80), 1, cv2.LINE_AA)

            # Vignette overlay
            writer.write(frame)

        writer.release()
        return cls._encode_or_fallback(temp_raw, output_path, duration_sec)

    @classmethod
    def render_financial_chart(
        cls,
        output_path: Path,
        duration_sec: float = 6.0,
        title: str = "SAIRGROUP ACCUMULATED LIABILITIES (1998-2001)",
        max_figure: str = "4,200,000,000 CHF"
    ) -> str:
        """
        Renders a 1080p dynamic financial chart showing exponential debt curve,
        animated coordinate points, and kinetic data reveal.
        """
        total_frames = int(duration_sec * cls.FPS)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        temp_raw = output_path.with_suffix(".temp.mp4")
        writer = cv2.VideoWriter(str(temp_raw), fourcc, cls.FPS, (cls.WIDTH, cls.HEIGHT))

        # Coordinates for curve across 4 years (1998: 800M, 1999: 1.8B, 2000: 3.2B, 2001: 4.2B)
        data_points = [
            ("1998", 300, 750, 0.8),
            ("1999", 600, 620, 1.8),
            ("2000", 900, 440, 3.2),
            ("2001", 1200, 280, 4.2)
        ]

        for f in range(total_frames):
            progress = f / float(total_frames)
            frame = np.zeros((cls.HEIGHT, cls.WIDTH, 3), dtype=np.uint8)
            frame[:] = (18, 14, 10)  # Dark charcoal BGR

            # Grid lines
            for y in range(250, 850, 100):
                cv2.line(frame, (200, y), (1400, y), (35, 30, 25), 1)

            # Chart Axes
            cv2.line(frame, (200, 800), (1400, 800), (80, 70, 60), 2)  # X-axis
            cv2.line(frame, (200, 200), (200, 800), (80, 70, 60), 2)  # Y-axis

            # Draw animated curve
            visible_points = []
            for year, px, py, val in data_points:
                t_reveal = (px - 200) / 1200.0
                if progress >= t_reveal:
                    visible_points.append((px, py))
                    # Draw node
                    cv2.circle(frame, (px, py), 7, (60, 60, 240), -1)
                    cv2.circle(frame, (px, py), 12, (80, 80, 255), 2)
                    cv2.putText(frame, year, (px - 25, 835), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1, cv2.LINE_AA)
                    cv2.putText(frame, f"{val:.1f}B CHF", (px - 45, py - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 120, 255), 2, cv2.LINE_AA)

            if len(visible_points) > 1:
                for i in range(len(visible_points) - 1):
                    cv2.line(frame, visible_points[i], visible_points[i+1], (50, 50, 230), 4, cv2.LINE_AA)

            # Dynamic counter in upper right
            cur_amt = int(4200000000 * min(1.0, progress * 1.2))
            cv2.putText(frame, f"{cur_amt:,} CHF", (1100, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (60, 70, 255), 3, cv2.LINE_AA)
            cv2.putText(frame, "TOTAL ACCUMULATED DEBT", (1100, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (160, 160, 160), 1, cv2.LINE_AA)

            # Header
            cv2.putText(frame, title, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, "SOURCE: ERNST & YOUNG AUDITED LIQUIDATION DOSSIER", (100, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 180, 220), 1, cv2.LINE_AA)

            writer.write(frame)

        writer.release()
        return cls._encode_or_fallback(temp_raw, output_path, duration_sec)

    @classmethod
    def render_document_reveal(
        cls,
        output_path: Path,
        duration_sec: float = 6.0,
        headline: str = "SPECIAL INVESTIGATION REPORT - SAIRGROUP RESTURCTURING",
        highlight_text: str = "OFF-BALANCE-SHEET GUARANTEES EXCEEDED 4.2 BILLION CHF"
    ) -> str:
        """
        Renders a 1080p document investigation reveal with aged paper texture
        and animated translucent yellow highlighter tracking across critical evidence.
        """
        total_frames = int(duration_sec * cls.FPS)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        temp_raw = output_path.with_suffix(".temp.mp4")
        writer = cv2.VideoWriter(str(temp_raw), fourcc, cls.FPS, (cls.WIDTH, cls.HEIGHT))

        for f in range(total_frames):
            progress = f / float(total_frames)
            frame = np.zeros((cls.HEIGHT, cls.WIDTH, 3), dtype=np.uint8)
            frame[:] = (220, 230, 235)  # Aged parchment BGR

            # Draw official document border
            cv2.rectangle(frame, (180, 100), (1740, 980), (160, 170, 180), 2)
            cv2.rectangle(frame, (190, 110), (1730, 970), (190, 200, 205), 1)

            # Document Header Stamp
            cv2.putText(frame, "CONFIDENTIAL / SWISS FEDERAL AUDIT COMMISSION", (240, 170),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (40, 40, 120), 2, cv2.LINE_AA)
            cv2.putText(frame, headline, (240, 230),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 20), 2, cv2.LINE_AA)

            # Body Paragraph text lines
            lines = [
                "Pursuant to Article 42 of the Swiss Aviation Act, the special liquidators examined",
                "all off-balance-sheet agreements executed by SAirGroup executives between 1998 and 2001.",
                "The findings confirm that multiple guarantees were provided without board authorization.",
                highlight_text,
                "As a consequence, liquidity was exhausted prior to the scheduled October asset transfer."
            ]

            y_offset = 320
            for i, line in enumerate(lines):
                # Check if this is the highlighted evidence line
                if line == highlight_text:
                    hl_width = int(1200 * min(1.0, max(0.0, (progress - 0.2) * 2.0)))
                    if hl_width > 0:
                        overlay = frame.copy()
                        cv2.rectangle(overlay, (230, y_offset - 30), (230 + hl_width, y_offset + 10), (0, 230, 255), -1)  # Yellow BGR
                        cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)

                    cv2.putText(frame, line, (240, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (10, 10, 10), 2, cv2.LINE_AA)
                else:
                    cv2.putText(frame, line, (240, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (60, 60, 60), 1, cv2.LINE_AA)
                y_offset += 65

            # Official Stamp
            cv2.circle(frame, (1550, 750), 65, (40, 40, 180), 3)
            cv2.putText(frame, "VERIFIED", (1510, 755), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (40, 40, 180), 2, cv2.LINE_AA)

            writer.write(frame)

        writer.release()
        return cls._encode_or_fallback(temp_raw, output_path, duration_sec)

    @classmethod
    def get_or_download_broll(cls, category: str) -> Optional[Path]:
        """
        Retrieves cached B-roll video clip or downloads it from Pixabay archive bank.
        """
        clean_cat = category.upper()
        if clean_cat not in BROLL_LIBRARY:
            clean_cat = "AIRPORT_TARMAC"
        
        target_path = BROLL_CACHE_DIR / f"{clean_cat}.mp4"
        if target_path.exists() and target_path.stat().st_size > 10000:
            return target_path
            
        url = BROLL_LIBRARY[clean_cat]
        try:
            import httpx
            with httpx.Client(timeout=25.0) as client:
                r = client.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                if r.status_code == 200 and len(r.content) > 10000:
                    target_path.write_bytes(r.content)
                    return target_path
        except Exception as e:
            logger.warning("Could not download B-roll video %s: %s", clean_cat, e)
            
        # If specific category fails, try fallback to AIRPORT_TARMAC
        if clean_cat != "AIRPORT_TARMAC":
            return cls.get_or_download_broll("AIRPORT_TARMAC")
        return None

    @classmethod
    def determine_broll_category(cls, text: str) -> str:
        """
        Analyzes narrative or visual prompt text to match the best cinematic B-roll category.
        """
        low = text.lower()
        if any(w in low for w in ["cockpit", "pilot", "instrument", "altimeter", "radio", "ground control", "refuse"]):
            return "COCKPIT_FLIGHT"
        if any(w in low for w in ["board", "meeting", "bruggisser", "corti", "ceo", "executive", "hunter", "strategy", "director", "table"]):
            return "BOARDROOM_MEETING"
        if any(w in low for w in ["stock", "market", "crash", "loss", "plunge", "collapse", "debt", "shareholder", "fall", "freefall"]):
            return "STOCK_MARKET_CRASH"
        if any(w in low for w in ["money", "cash", "franc", "million", "billion", "payment", "bank", "vault", "credit", "ubs", "paradeplatz"]):
            return "COUNTING_MONEY"
        if any(w in low for w in ["press", "media", "camera", "reporter", "news", "broadcast", "journalist", "headline"]):
            return "CAMERA_REPORTER"
        if any(w in low for w in ["terminal", "passenger", "crowd", "ticket", "gate", "stranded", "baggage", "protest", "line", "fury"]):
            return "PASSENGER_TERMINAL"
        if any(w in low for w in ["rain", "runway", "grounded", "night", "storm", "wet", "standstill", "freeze", "october"]):
            return "RAIN_RUNWAY"
        if any(w in low for w in ["takeoff", "landing", "fly", "air", "fleet", "aircraft", "jet", "swiss", "sky", "alps", "altitude"]):
            return "JET_TAKEOFF"
        return "AIRPORT_TARMAC"

    @classmethod
    def render_broll_clip(
        cls,
        category: str,
        output_path: Path,
        duration_sec: float = 4.0,
        offset_sec: float = 0.0,
        chyron_title: str = "SWISSAIR INVESTIGATION",
        chyron_sub: str = "Grounding Protocol Active"
    ) -> str:
        """
        Renders a 1080p documentary B-roll video clip with cinematic grading (vignette + contrast)
        and modern YouTube broadcast lower-third chyron badge.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dur = max(2.5, duration_sec)
        src_video = cls.get_or_download_broll(category)
        
        if not src_video or not src_video.exists():
            return cls.render_photo_ken_burns(None, output_path, duration_sec=dur, caption=chyron_sub)
            
        # 1. Synthesize PNG chyron overlay via Pillow (zero fontconfig dependency)
        chyron_png = output_path.with_suffix(".chyron.png")
        try:
            img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            # Frosted dark banner
            draw.rectangle([(80, 890), (1180, 975)], fill=(12, 14, 18, 215))
            # Golden left accent bar
            draw.rectangle([(80, 890), (88, 975)], fill=(220, 180, 60, 255))
            # Text
            c_title = (chyron_title or "INVESTIGATIVE DOSSIER")[:45]
            c_sub = (chyron_sub or "Documentary Evidence Beat")[:65]
            draw.text((105, 902), c_title, fill=(220, 180, 60, 255))
            draw.text((105, 934), c_sub, fill=(240, 245, 250, 255))
            img.save(str(chyron_png))
        except Exception as e:
            logger.warning("Pillow chyron generation skipped: %s", e)
            chyron_png = None

        # 2. FFmpeg trim, scale, grade, and overlay
        if chyron_png and chyron_png.exists():
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(round(offset_sec, 2)),
                "-t", str(round(dur, 2)),
                "-i", str(src_video),
                "-i", str(chyron_png),
                "-filter_complex", (
                    "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,"
                    "curves=preset=medium_contrast,vignette=PI/4[bg];"
                    "[bg][1:v]overlay=0:0[outv]"
                ),
                "-map", "[outv]",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-threads", "1",
                str(output_path)
            ]
        else:
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(round(offset_sec, 2)),
                "-t", str(round(dur, 2)),
                "-i", str(src_video),
                "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,curves=preset=medium_contrast,vignette=PI/4",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-threads", "1",
                str(output_path)
            ]

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        finally:
            if chyron_png and chyron_png.exists():
                chyron_png.unlink(missing_ok=True)
                
        return str(output_path)

    @classmethod
    def render_cold_open(cls, output_path: Path) -> str:
        """
        Renders an explosive 13.5-second Cold Open hook clip featuring rapid cuts,
        emergency location chyrons, and a dramatic title card slam.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cold_temp_dir = output_path.parent / "cold_open_temp"
        cold_temp_dir.mkdir(parents=True, exist_ok=True)

        shots = [
            ("RAIN_RUNWAY", 2.5, 0.0, "ZURICH AIRPORT — OCTOBER 2, 2001", "12:30 PM — Fuel Trucks Refuse Service to Swissair"),
            ("COCKPIT_FLIGHT", 2.5, 2.0, "FLIGHT SR 356 TO NEW YORK", "Captain Receives Ground Order from Kloten Tower"),
            ("STOCK_MARKET_CRASH", 2.5, 1.0, "SWISS STOCK EXCHANGE (SWX)", "SAirGroup Shares Collapse 85% Into Freefall"),
            ("PASSENGER_TERMINAL", 2.0, 3.0, "GLOBAL AIRLINE CHAOS", "19,000 Passengers Stranded in 40 Countries")
        ]

        sub_clips = []
        for s_idx, (cat, s_dur, s_off, title, sub) in enumerate(shots):
            sub_p = cold_temp_dir / f"shot_{s_idx}.mp4"
            cls.render_broll_clip(cat, sub_p, duration_sec=s_dur, offset_sec=s_off, chyron_title=title, chyron_sub=sub)
            sub_clips.append(sub_p)

        # Title Card Slam (4.0s)
        title_card_img = cold_temp_dir / "title_card.jpg"
        img = Image.new("RGB", (1920, 1080), color=(10, 12, 16))
        draw = ImageDraw.Draw(img)
        draw.rectangle([(80, 80), (1840, 1000)], outline=(40, 48, 60), width=2)
        draw.rectangle([(100, 100), (1820, 980)], outline=(25, 30, 38), width=1)
        draw.text((960, 320), "DOCUFORGE INVESTIGATIVE SPECIAL", fill=(220, 180, 60), anchor="mm")
        draw.text((960, 420), "THE SWISS AIR GROUNDING", fill=(255, 255, 255), anchor="mm")
        draw.rectangle([(480, 480), (1440, 484)], fill=(220, 180, 60))
        draw.text((960, 540), "HOW ARROGANCE DESTROYED THE BANK OF THE SKIES", fill=(180, 190, 205), anchor="mm")
        draw.text((960, 660), "OCTOBER 2, 2001 — THE COLLAPSE OF AN EMPIRE", fill=(120, 130, 145), anchor="mm")
        img.save(str(title_card_img), "JPEG", quality=95)

        title_clip = cold_temp_dir / "title_clip.mp4"
        cmd_title = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(title_card_img),
            "-t", "4.0",
            "-vf", "scale=1920:1080,zoompan=z='min(zoom+0.0008,1.06)':d=96:s=1920x1080:fps=24",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", "-pix_fmt", "yuv420p", "-threads", "1",
            str(title_clip)
        ]
        subprocess.run(cmd_title, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        sub_clips.append(title_clip)

        # Concatenate into Cold Open MP4
        concat_txt = cold_temp_dir / "cold_concat.txt"
        with open(concat_txt, "w", encoding="utf-8") as cf:
            for sc in sub_clips:
                cf.write(f"file '{sc.name}'\n")

        cmd_concat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
            "-c:v", "copy", "-threads", "1", str(output_path)
        ]
        subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Clean up temp files
        for sc in sub_clips:
            sc.unlink(missing_ok=True)
        title_card_img.unlink(missing_ok=True)
        concat_txt.unlink(missing_ok=True)
        try:
            cold_temp_dir.rmdir()
        except Exception:
            pass

        return str(output_path)

    @classmethod
    def render_photo_ken_burns(
        cls,
        image_input_path: Optional[str],
        output_path: Path,
        duration_sec: float = 6.0,
        caption: str = "ARCHIVAL RECORD - EXECUTIVE BRIEFING"
    ) -> str:
        """
        Renders a 1080p archival video clip with Ken Burns push-in / slow zoom.
        If image_input_path is missing, synthesizes a high-contrast broadcast graphic slate.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dur = max(2.0, duration_sec)
        clean_cap = (caption or "SWISSAIR ARCHIVE INVESTIGATION").replace("'", "").replace('"', '').replace(':', ' -')[:50]

        temp_slate_path = None
        target_img = image_input_path

        if not (target_img and os.path.exists(target_img) and os.path.getsize(target_img) > 1000):
            # Synthesize high-contrast broadcast slate image via Pillow
            temp_slate_path = output_path.with_suffix(".slate.jpg")
            try:
                from PIL import Image, ImageDraw
                img = Image.new("RGB", (1920, 1080), color=(22, 18, 16))
                draw = ImageDraw.Draw(img)
                # Outer and inner framing
                draw.rectangle([(60, 60), (1860, 1020)], outline=(60, 50, 45), width=3)
                draw.rectangle([(80, 80), (1840, 1000)], outline=(35, 30, 26), width=1)
                # Lower third banner
                draw.rectangle([(100, 870), (1200, 960)], fill=(12, 10, 8))
                draw.rectangle([(100, 870), (112, 960)], fill=(220, 180, 60))  # Gold accent
                draw.text((130, 885), "SWISSAIR GROUNDING INVESTIGATION", fill=(220, 180, 60))
                draw.text((130, 918), clean_cap, fill=(240, 240, 240))
                img.save(str(temp_slate_path), "JPEG", quality=90)
                target_img = str(temp_slate_path)
            except Exception as e:
                logger.warning("Pillow slate synthesis fallback: %s", e)
                target_img = None

        if target_img and os.path.exists(target_img):
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", target_img,
                "-t", str(dur),
                "-vf", f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(zoom+0.001,1.10)':d={int(dur*24)}:s=1920x1080:fps=24",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-threads", "1",
                str(output_path)
            ]
        else:
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", f"color=c=0x181512:s=1920x1080:r=24:d={dur}",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-threads", "1",
                str(output_path)
            ]

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        finally:
            if temp_slate_path:
                temp_slate_path.unlink(missing_ok=True)

        return str(output_path)

    @classmethod
    def render_all_animations(cls, project_id: str) -> Dict[str, Any]:
        """
        Synthesizes all animated maps, data visualizations, document reveals,
        and photo motions for the project.
        Logs budget usage ($0.00 for local rendering).
        """
        BudgetEngine.record_cost(
            agent_name="ANIMATION_DIRECTOR_AGENT",
            operation="ANIMATION_SYNTHESIS_1080P",
            model_or_service="LOCAL_OPENCV_FFMPEG_ENGINE",
            cost_usd=0.00,
            project_id=project_id,
            tokens_in=0,
            tokens_out=0,
            notes="Rendered 1080p animated maps, financial curves, and document reveals ($0.00 local software)"
        )

        proj_anim_dir = ANIMATIONS_DIR / project_id
        proj_anim_dir.mkdir(parents=True, exist_ok=True)

        items = StoryboardEngine.get_storyboard(project_id)
        if not items:
            StoryboardEngine.compile_storyboard(project_id)
            items = StoryboardEngine.get_storyboard(project_id)

        rendered_clips = []

        for it in items:
            order_idx = it["order_index"]
            asset_type = it.get("asset_type", "ARCHIVAL_VIDEO")
            out_clip = proj_anim_dir / f"clip_{order_idx}.mp4"
            dur = min(float(it.get("duration_sec", 4.0)), 4.5)

            if asset_type == "MAP":
                anim_type = "ANIMATED_MAP"
                if not (out_clip.exists() and out_clip.stat().st_size > 5000):
                    cls.render_animated_map(out_clip, duration_sec=dur, title="EUROPEAN AIRSPACE & DEREGULATION CHOKEPOINTS")
            elif asset_type == "CHART":
                anim_type = "DATA_VISUALIZATION"
                if not (out_clip.exists() and out_clip.stat().st_size > 5000):
                    cls.render_financial_chart(out_clip, duration_sec=dur, title="SAIRGROUP OFF-BALANCE-SHEET DEBT ESCALATION")
            elif asset_type == "DOCUMENT":
                anim_type = "DOCUMENT_REVEAL"
                if not (out_clip.exists() and out_clip.stat().st_size > 5000):
                    cls.render_document_reveal(out_clip, duration_sec=dur, headline=it["visual_summary"][:50])
            else:
                cat = cls.determine_broll_category(it.get("visual_summary", "") + " " + it.get("narration_text", ""))
                anim_type = f"BROLL_{cat}"
                if not (out_clip.exists() and out_clip.stat().st_size > 50000):
                    offset_sec = (order_idx * 3.2) % 15.0
                    chyron_title = f"SCENE {it['scene_number']} · INVESTIGATION"
                    chyron_sub = it.get("visual_summary", "Documentary Archival Beat")[:60]
                    cls.render_broll_clip(
                        category=cat,
                        output_path=out_clip,
                        duration_sec=dur,
                        offset_sec=offset_sec,
                        chyron_title=chyron_title,
                        chyron_sub=chyron_sub
                    )

            web_url = f"/media/animations/{project_id}/clip_{order_idx}.mp4"
            rendered_clips.append({
                "order_index": order_idx,
                "scene_number": it["scene_number"],
                "animation_type": anim_type,
                "duration_sec": dur,
                "web_url": web_url,
                "file_path": str(out_clip)
            })

        logger.info("Rendered %d animation video clips for project %s", len(rendered_clips), project_id)
        return {
            "project_id": project_id,
            "total_rendered": len(rendered_clips),
            "clips": rendered_clips
        }
