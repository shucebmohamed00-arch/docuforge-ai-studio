"""
DocuForge Multi-Agent Graphics Engine - Agent 9: Timeline Reviewer & Vision Inspector
Inspects the assembled documentary video across its entire timeline, sampling frames,
analyzing aesthetics, checking visual coherence, and producing visual contact sheets.
"""
import os
import cv2
import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
from ..core.base_agent import BaseAgent
from .visual_critic import VisualCriticAgent

class TimelineReviewerAgent(BaseAgent):
    def __init__(self, review_dir: Optional[Path] = None):
        super().__init__(
            name="timeline_reviewer",
            role="Documentary Visual Reviewer & Inspector",
            description="Samples and visually reviews the entire documentary timeline to audit aesthetic consistency and quality."
        )
        self.review_dir = review_dir or (Path("c:/Users/Shueb/Desktop/youtu") / "data" / "exports" / "visual_audit")
        self.review_dir.mkdir(parents=True, exist_ok=True)
        self.critic = VisualCriticAgent()

    def sample_timeline_frames(self, video_path: Path, sample_interval_sec: float = 25.0) -> List[Dict[str, Any]]:
        self.log(f"Sampling timeline frames from '{video_path.name}' every {sample_interval_sec}s...")
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_sec = total_frames / fps

        sample_times = np.arange(5.0, duration_sec - 5.0, sample_interval_sec)
        sampled_data = []

        for ts in sample_times:
            frame_num = int(ts * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            if ret and frame is not None:
                # Save preview frame image
                frame_filename = f"review_at_{int(ts):03d}s.jpg"
                frame_path = self.review_dir / frame_filename
                cv2.imwrite(str(frame_path), frame)

                sharpness = self.critic.compute_sharpness(frame)
                contrast, exposure, is_well_exp = self.critic.compute_contrast_and_exposure(frame)

                sampled_data.append({
                    "timestamp_sec": round(float(ts), 1),
                    "frame_path": str(frame_path),
                    "sharpness": round(sharpness, 1),
                    "contrast": round(contrast, 1),
                    "exposure": round(exposure, 1),
                    "well_exposed": is_well_exp
                })

        cap.release()
        self.log(f"Successfully sampled and visually analyzed {len(sampled_data)} timeline frames.")
        return sampled_data

    def generate_contact_sheet(self, samples: List[Dict[str, Any]], out_path: Optional[Path] = None) -> Path:
        """
        Creates a high-density visual contact sheet of the entire documentary for immediate visual review.
        """
        if not samples:
            return None

        out_path = out_path or (self.review_dir / "documentary_contact_sheet.jpg")
        cols = 4
        rows = (len(samples) + cols - 1) // cols
        thumb_w, thumb_h = 480, 270

        sheet = Image.new("RGB", (cols * thumb_w, rows * thumb_h), (12, 14, 18))
        draw = ImageDraw.Draw(sheet)

        font = None
        for fp in ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf"]:
            if os.path.exists(fp):
                font = ImageFont.truetype(fp, 18)
                break
        if not font:
            font = ImageFont.load_default()

        for idx, sample in enumerate(samples):
            r = idx // cols
            c = idx % cols
            img_p = Path(sample["frame_path"])
            if img_p.exists():
                with Image.open(img_p) as im:
                    thumb = im.resize((thumb_w, thumb_h), Image.BILINEAR)
                    sheet.paste(thumb, (c * thumb_w, r * thumb_h))

            # Overlay metadata
            ts_str = f"{int(sample['timestamp_sec'] // 60):02d}:{int(sample['timestamp_sec'] % 60):02d}"
            draw.rectangle([c * thumb_w + 8, r * thumb_h + 8, c * thumb_w + 140, r * thumb_h + 36], fill=(0, 0, 0, 180))
            draw.text((c * thumb_w + 14, r * thumb_h + 12), f"Time: {ts_str}", font=font, fill=(255, 215, 0))

        sheet.save(str(out_path), quality=90)
        self.log(f"Visual contact sheet compiled: {out_path.name} ({out_path.stat().st_size / 1024:.1f} KB)")
        return out_path

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        video_path = Path(task["video_path"])
        interval = float(task.get("interval_sec", 25.0))
        samples = self.sample_timeline_frames(video_path, sample_interval_sec=interval)
        sheet_path = self.generate_contact_sheet(samples)

        return {
            "status": "success",
            "samples_count": len(samples),
            "contact_sheet": str(sheet_path) if sheet_path else None,
            "samples": samples
        }
