"""
DocuForge Multi-Agent Graphics Engine - Agent 7: Footage Stylist & Motion Pre-Processor Agent
Integrates the Visual Critic and Color Grader to inspect, animate, and grade raw footage:
1. Rejects poor, blurry, or watermarked footage via computer vision inspection.
2. Applies deliberate slow digital push-in / pan (Ken Burns on video).
3. Applies unified documentary color grading (moody micro-contrast, split-toning, vignette, 35mm grain).
4. Delivers production-grade, 100% curated cinema clips ready for assembly.
"""
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from ..core.base_agent import BaseAgent
from ..core.color_grader import CinematicColorGrader
from .visual_critic import VisualCriticAgent

class FootageStylistAgent(BaseAgent):
    def __init__(self, output_dir: Optional[Path] = None):
        super().__init__(
            name="footage_stylist",
            role="Footage Stylist & Motion Pre-Processor",
            description="Inspects clips via computer vision, animates human camera motion, and applies unified cinematic color grading."
        )
        self.output_dir = output_dir or (Path("c:/Users/Shueb/Desktop/youtu") / "data" / "media" / "curated_footage")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.critic = VisualCriticAgent()

    def process_and_animate_footage(
        self,
        src_clip: Path,
        out_clip: Path,
        target_dur: float = 4.0,
        grade_profile: str = "moody_investigative",
        skip_critic: bool = False
    ) -> Optional[Path]:
        # 1. Visual Quality Gate
        if not skip_critic:
            critique = self.critic.inspect_clip(src_clip)
            if critique.get("verdict") == "REJECTED":
                self.log(f"Footage '{src_clip.name}' REJECTED by Visual Critic: {critique.get('rejection_reasons')}. Skipping.", level="WARNING")
                return None

        self.log(f"Pre-editing raw footage '{src_clip.name}' with '{grade_profile}' -> {out_clip.name}...")

        # 2. Camera Motion: Subtle digital push zoom (Ken Burns on video)
        zoom_filter = (
            f"scale=eval=frame:w='1920*(1.0+0.06*t/{target_dur})':h='1080*(1.0+0.06*t/{target_dur})':force_original_aspect_ratio=increase,"
            f"crop=1920:1080:(in_w-1920)/2:(in_h-1080)/2"
        )

        # 3. Unified Color Grading
        color_filter = CinematicColorGrader.get_filter(grade_profile)

        full_filter = f"{zoom_filter},{color_filter},tpad=stop_mode=clone:stop_duration=3,settb=AVTB,setpts=PTS-STARTPTS,format=yuv420p"

        cmd = [
            "ffmpeg", "-y",
            "-ss", "0.2",
            "-t", str(round(target_dur, 2)),
            "-i", str(src_clip),
            "-vf", full_filter,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "19",
            "-pix_fmt", "yuv420p", "-an",
            str(out_clip)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        self.log(f"Footage pre-edited & graded successfully: {out_clip.name} ({out_clip.stat().st_size / 1024 / 1024:.2f} MB)")
        return out_clip

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        src = Path(task["src_path"])
        out_name = task.get("out_name", f"styled_{src.stem}.mp4")
        out_clip = self.output_dir / out_name
        dur = float(task.get("duration", 4.0))
        grade = task.get("grade_profile", "moody_investigative")
        skip_qc = task.get("skip_critic", False)

        res_path = self.process_and_animate_footage(src, out_clip, target_dur=dur, grade_profile=grade, skip_critic=skip_qc)
        if res_path:
            return {
                "status": "success",
                "output_path": str(out_clip),
                "size_mb": out_clip.stat().st_size / 1024 / 1024
            }
        else:
            return {
                "status": "rejected",
                "message": "Clip failed visual quality inspection"
            }
