"""
DocuForge Multi-Agent Graphics Engine - Agent 8: Visual Critic & Aesthetic Inspection Agent
Provides the engine with autonomous computer vision to evaluate footage quality,
measuring sharpness, dynamic contrast, color fidelity, watermark absence, and cinematic suitability.
"""
import os
import cv2
import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from ..core.base_agent import BaseAgent

class VisualCriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="visual_critic",
            role="Visual Quality & Aesthetic Critic",
            description="Autonomous computer vision agent that inspects frames for sharpness, contrast, color balance, and watermarks."
        )

    def extract_keyframes(self, video_path: Path, count: int = 5) -> List[np.ndarray]:
        """
        Extracts representative keyframes across the clip timeline using OpenCV.
        """
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            cap.release()
            return []

        step = max(1, total_frames // (count + 1))
        frames = []
        for i in range(1, count + 1):
            target = i * step
            cap.set(cv2.CAP_PROP_POS_FRAMES, target)
            ret, frame = cap.read()
            if ret and frame is not None:
                frames.append(frame)

        cap.release()
        return frames

    def compute_sharpness(self, frame: np.ndarray) -> float:
        """
        Laplacian variance metric: higher = crisper detail, lower = blurry/mushy.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())

    def compute_contrast_and_exposure(self, frame: np.ndarray) -> Tuple[float, float, bool]:
        """
        Measures dynamic range (standard deviation of luminance) and mean exposure.
        Returns: (contrast_score, mean_brightness, is_well_exposed)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_lum = float(np.mean(gray))
        contrast = float(np.std(gray))
        # Well exposed: not crushed (<20) and not washed out / blown (>235)
        is_well_exposed = 25.0 <= mean_lum <= 220.0 and contrast >= 35.0
        return contrast, mean_lum, is_well_exposed

    def scan_for_watermarks_and_logos(self, frames: List[np.ndarray]) -> Tuple[bool, str]:
        """
        Scans corner quadrants across multiple frames. If high-contrast static text or
        opaque bounding edges persist across frames in the corners, flags potential watermark.
        """
        if len(frames) < 2:
            return False, "Not enough frames to analyze static logos"

        h, w = frames[0].shape[:2]
        cw, ch = int(w * 0.22), int(h * 0.18)

        # Check corners: Top-Left, Top-Right, Bottom-Left, Bottom-Right
        corners = [
            ("top_left", (0, 0, cw, ch)),
            ("top_right", (w - cw, 0, w, ch)),
            ("bottom_left", (0, h - ch, cw, h)),
            ("bottom_right", (w - cw, h - ch, w, h))
        ]

        for corner_name, (x1, y1, x2, y2) in corners:
            corner_crops = [cv2.cvtColor(f[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY) for f in frames]
            
            # Check edge density in corner
            edges = [cv2.Canny(c, 80, 200) for c in corner_crops]
            edge_densities = [np.mean(e) for e in edges]
            
            # If corner has persistent high edge density (e.g. sharp text logo like TELE 24 or TV bug)
            avg_edge = np.mean(edge_densities)
            diff = np.mean(np.abs(corner_crops[0].astype(float) - corner_crops[-1].astype(float)))
            
            # High edge structure with low inter-frame motion in the corner indicates a static watermark
            if avg_edge > 25.0 and diff < 15.0:
                return True, f"Persistent static logo/watermark detected in {corner_name} (edge_density={avg_edge:.1f}, diff={diff:.1f})"

        return False, "Clean corners (no watermarks detected)"

    def inspect_clip(self, video_path: Path) -> Dict[str, Any]:
        """
        Comprehensive visual critique of a video clip.
        Returns visual scores and final pass/reject verdict.
        """
        self.log(f"Visually inspecting clip: '{video_path.name}'...")
        if not video_path.exists():
            return {"status": "error", "message": "File does not exist"}

        frames = self.extract_keyframes(video_path, count=5)
        if not frames:
            return {"status": "rejected", "reason": "Failed to decode valid video frames"}

        sharpness_scores = [self.compute_sharpness(f) for f in frames]
        avg_sharpness = float(np.mean(sharpness_scores))

        contrast_scores = []
        exposure_scores = []
        well_exposed_flags = []
        for f in frames:
            c, e, we = self.compute_contrast_and_exposure(f)
            contrast_scores.append(c)
            exposure_scores.append(e)
            well_exposed_flags.append(we)

        avg_contrast = float(np.mean(contrast_scores))
        avg_exposure = float(np.mean(exposure_scores))
        has_watermark, wm_detail = self.scan_for_watermarks_and_logos(frames)

        # Critique rules:
        rejection_reasons = []
        if avg_sharpness < 85.0:
            rejection_reasons.append(f"Image too blurry/soft (sharpness={avg_sharpness:.1f} < 85.0)")
        if avg_contrast < 30.0:
            rejection_reasons.append(f"Flat/muddy dynamic range (contrast={avg_contrast:.1f} < 30.0)")
        if avg_exposure < 20.0:
            rejection_reasons.append(f"Severely underexposed/black (exposure={avg_exposure:.1f} < 20.0)")
        elif avg_exposure > 225.0:
            rejection_reasons.append(f"Severely blown out/overexposed (exposure={avg_exposure:.1f} > 225.0)")
        if has_watermark:
            rejection_reasons.append(wm_detail)

        passed = len(rejection_reasons) == 0

        # Calculate Overall Visual Quality Score (0-100)
        q_sharp = min(40.0, (avg_sharpness / 300.0) * 40.0)
        q_contrast = min(30.0, (avg_contrast / 70.0) * 30.0)
        q_exposure = 30.0 if all(well_exposed_flags) else 15.0
        quality_score = round(q_sharp + q_contrast + q_exposure - (50.0 if has_watermark else 0.0), 1)
        quality_score = max(0.0, min(100.0, quality_score))

        verdict = "APPROVED" if passed else "REJECTED"
        if passed:
            self.log(f"VERDICT: APPROVED (Quality Score: {quality_score}/100, Sharpness: {avg_sharpness:.1f}, Contrast: {avg_contrast:.1f})")
        else:
            self.log(f"VERDICT: REJECTED - {'; '.join(rejection_reasons)}", level="WARNING")

        return {
            "file": str(video_path),
            "verdict": verdict,
            "quality_score": quality_score,
            "sharpness": round(avg_sharpness, 1),
            "contrast": round(avg_contrast, 1),
            "mean_exposure": round(avg_exposure, 1),
            "has_watermark": has_watermark,
            "watermark_detail": wm_detail,
            "rejection_reasons": rejection_reasons
        }

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        video_path = Path(task["video_path"])
        return self.inspect_clip(video_path)
