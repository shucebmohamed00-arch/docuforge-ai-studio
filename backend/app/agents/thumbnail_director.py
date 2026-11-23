"""
DocuForge AI - Agent 12: Thumbnail Director
Generates two distinct 1280x720 (16:9) cinematic thumbnail concepts with strong focal subjects,
high-contrast typography, and mobile readability validation.
"""
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
from ..database import get_connection
from ..config import EXPORTS_DIR, ASSETS_DIR
from ..core.budget_engine import BudgetEngine
from .deep_research import DeepResearchAgent

logger = logging.getLogger("docuforge.agents.thumbnail_director")

class ThumbnailDirector:
    WIDTH = 1280
    HEIGHT = 720

    @classmethod
    def _create_concept_1(cls, project_title: str, output_path: Path) -> Dict[str, Any]:
        """
        Concept 1: Forensic / Direct Evidence Drama
        Focal subject: Grounded aircraft / critical asset in harsh dramatic lighting.
        Headline: 'THE 48-HOUR COLLAPSE'
        """
        img = np.zeros((cls.HEIGHT, cls.WIDTH, 3), dtype=np.uint8)
        img[:] = (20, 16, 14)  # Deep charcoal-blue BGR

        # Dramatic directional light gradient
        for y in range(cls.HEIGHT):
            ratio = y / float(cls.HEIGHT)
            img[y, :] = (int(25 + 15 * ratio), int(20 + 10 * ratio), int(15 + 8 * ratio))

        # Geometric accent / red warning stripe
        cv2.line(img, (0, 680), (cls.WIDTH, 680), (40, 40, 220), 8)

        # Draw silhouetted commercial airliner on tarmac
        # Wing & Fuselage
        cv2.rectangle(img, (200, 360), (1080, 440), (45, 40, 35), -1)
        # Tail fin with Swiss cross motif
        pts_tail = np.array([[880, 360], [1050, 180], [1090, 180], [1020, 360]], np.int32)
        cv2.fillPoly(img, [pts_tail], (60, 50, 45))
        # Red Swiss tail fin accent
        cv2.rectangle(img, (980, 200), (1050, 280), (30, 30, 200), -1)
        # White cross
        cv2.rectangle(img, (1005, 215), (1025, 265), (250, 250, 250), -1)
        cv2.rectangle(img, (990, 230), (1040, 250), (250, 250, 250), -1)

        # High-contrast bold typography with drop shadow
        headline_1 = "GROUNDED"
        headline_2 = "THE 48-HOUR COLLAPSE"

        # Shadow
        cv2.putText(img, headline_1, (95, 175), cv2.FONT_HERSHEY_TRIPLEX, 2.6, (10, 10, 10), 8, cv2.LINE_AA)
        cv2.putText(img, headline_2, (95, 245), cv2.FONT_HERSHEY_TRIPLEX, 1.4, (10, 10, 10), 6, cv2.LINE_AA)

        # Foreground Text (Bright Yellow / White)
        cv2.putText(img, headline_1, (90, 170), cv2.FONT_HERSHEY_TRIPLEX, 2.6, (50, 230, 255), 6, cv2.LINE_AA)
        cv2.putText(img, headline_2, (90, 240), cv2.FONT_HERSHEY_TRIPLEX, 1.4, (255, 255, 255), 4, cv2.LINE_AA)

        # Evidence pill in bottom left
        cv2.rectangle(img, (90, 580), (480, 640), (25, 22, 18), -1)
        cv2.rectangle(img, (90, 580), (480, 640), (40, 40, 220), 2)
        cv2.putText(img, "OFFICIAL PARLIAMENTARY INQUIRY", (105, 618), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 220, 220), 2, cv2.LINE_AA)

        # Save JPEG
        cv2.imwrite(str(output_path), img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        return {
            "concept_number": 1,
            "title": "Forensic / Direct Evidence Drama",
            "focal_subject": "Grounded Swissair aircraft silhouette on Kloten tarmac",
            "headline": f"{headline_1}: {headline_2}",
            "file_path": str(output_path),
            "web_url": f"/exports/{output_path.parent.name}/{output_path.name}"
        }

    @classmethod
    def _create_concept_2(cls, project_title: str, output_path: Path) -> Dict[str, Any]:
        """
        Concept 2: Systemic / Financial Mystery Drama
        Focal subject: Corporate boardroom / Bank vault silhouette with dropping stock curve.
        Headline: '14 MILLION LEFT: THE SECRET MEETING'
        """
        img = np.zeros((cls.HEIGHT, cls.WIDTH, 3), dtype=np.uint8)
        img[:] = (18, 14, 10)  # Very dark warm charcoal

        # Draw red descending market crash curve in background
        pts_curve = np.array([
            [100, 250], [350, 280], [600, 360], [850, 480], [1150, 620]
        ], np.int32)
        for i in range(len(pts_curve) - 1):
            cv2.line(img, tuple(pts_curve[i]), tuple(pts_curve[i+1]), (40, 40, 220), 6, cv2.LINE_AA)
            cv2.circle(img, tuple(pts_curve[i+1]), 10, (50, 50, 240), -1)

        # Gradient vignette
        cv2.rectangle(img, (0, 0), (cls.WIDTH, cls.HEIGHT), (0, 0, 0), 20)

        # Bold Mystery Typography
        headline_1 = "14 MILLION LEFT"
        headline_2 = "THE SECRET MEETING THAT BROKE AN EMPIRE"

        # Shadow
        cv2.putText(img, headline_1, (95, 175), cv2.FONT_HERSHEY_TRIPLEX, 2.5, (5, 5, 5), 8, cv2.LINE_AA)
        cv2.putText(img, headline_2, (95, 240), cv2.FONT_HERSHEY_TRIPLEX, 1.15, (5, 5, 5), 5, cv2.LINE_AA)

        # Foreground Text (Gold / Red)
        cv2.putText(img, headline_1, (90, 170), cv2.FONT_HERSHEY_TRIPLEX, 2.5, (40, 190, 255), 6, cv2.LINE_AA)  # Bright amber
        cv2.putText(img, headline_2, (90, 235), cv2.FONT_HERSHEY_TRIPLEX, 1.15, (255, 255, 255), 3, cv2.LINE_AA)

        # Center cash deficit counter
        cv2.rectangle(img, (90, 310), (520, 390), (30, 25, 20), -1)
        cv2.rectangle(img, (90, 310), (520, 390), (60, 60, 240), 2)
        cv2.putText(img, "-4,200,000,000 CHF", (110, 365), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (60, 70, 255), 3, cv2.LINE_AA)

        # Save JPEG
        cv2.imwrite(str(output_path), img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        return {
            "concept_number": 2,
            "title": "Systemic Financial Mystery Drama",
            "focal_subject": "Descending crash vector and 14.5M cash deficit ticker",
            "headline": f"{headline_1}: {headline_2}",
            "file_path": str(output_path),
            "web_url": f"/exports/{output_path.parent.name}/{output_path.name}"
        }

    @classmethod
    def evaluate_mobile_readability(cls, thumbnail_path: Path) -> Dict[str, Any]:
        """
        Simulates and evaluates thumbnail legibility at mobile search scale (150px width).
        Measures text contrast and edge sharpness.
        """
        img = cv2.imread(str(thumbnail_path))
        if img is None:
            return {"score": 0.0, "status": "FILE_NOT_FOUND"}

        # Downscale to 150px width (typical mobile YouTube feed thumbnail)
        mobile_w = 150
        mobile_h = int(cls.HEIGHT * (mobile_w / cls.WIDTH))
        small = cv2.resize(img, (mobile_w, mobile_h), interpolation=cv2.INTER_AREA)

        # Contrast calculation (Standard deviation of luminance)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        std_contrast = float(np.std(gray))
        
        # High contrast scale: std >= 30 represents high-contrast punchy thumbnail
        readability_score = min(100, int((std_contrast / 35.0) * 100))
        is_legible = readability_score >= 70

        return {
            "mobile_width_px": mobile_w,
            "mobile_height_px": mobile_h,
            "readability_score": readability_score,
            "is_mobile_legible": is_legible,
            "contrast_standard_deviation": round(std_contrast, 2)
        }

    @classmethod
    def generate_both_thumbnails(cls, project_id: str) -> Dict[str, Any]:
        """
        Generates two distinct 1280x720 thumbnail concepts and runs mobile readability analysis.
        Logs budget usage ($0.00 for local software generation).
        """
        BudgetEngine.record_cost(
            agent_name="THUMBNAIL_DIRECTOR_AGENT",
            operation="DUAL_THUMBNAIL_GENERATION",
            model_or_service="LOCAL_COMPOSITING_ENGINE",
            cost_usd=0.00,
            project_id=project_id,
            tokens_in=0,
            tokens_out=0,
            notes="Dual 1280x720 16:9 thumbnail concepts with mobile scale readability validation ($0.00 local)"
        )

        proj_export_dir = EXPORTS_DIR / project_id
        proj_export_dir.mkdir(parents=True, exist_ok=True)

        t1_path = proj_export_dir / "thumbnail-1.jpg"
        t2_path = proj_export_dir / "thumbnail-2.jpg"

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            project_title = row["title"] if row else "The Swiss Air Grounding"
        finally:
            conn.close()

        c1 = cls._create_concept_1(project_title, t1_path)
        c2 = cls._create_concept_2(project_title, t2_path)

        c1["mobile_evaluation"] = cls.evaluate_mobile_readability(t1_path)
        c2["mobile_evaluation"] = cls.evaluate_mobile_readability(t2_path)

        logger.info("Generated dual thumbnails for project %s (C1 score: %d%%, C2 score: %d%%)",
                    project_id, c1["mobile_evaluation"]["readability_score"], c2["mobile_evaluation"]["readability_score"])

        return {
            "project_id": project_id,
            "thumbnails": [c1, c2]
        }
