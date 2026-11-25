"""
DocuForge Multi-Agent Graphics Engine - Agent 11: 3D Stage Compositor Agent (MagnatesMedia Tier)
Transforms flat images, documents, and portraits into tangible 3D physical stage assets:
mahogany wood surfaces, overhead volumetric spotlights, torn-paper edges, and drop shadows.
"""
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
from ..core.base_agent import BaseAgent
from ..core.stage_engine import MagnatesStageEngine

class StageCompositorAgent(BaseAgent):
    def __init__(self, output_dir: Optional[Path] = None):
        super().__init__(
            name="stage_compositor",
            role="3D Stage & Volumetric Desk Compositor",
            description="Composites torn-paper archival documents and character case files onto 3D mahogany desks with overhead spotlights."
        )
        self.output_dir = output_dir or (Path("c:/Users/Shueb/Desktop/youtu") / "data" / "media" / "magnates_stage")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render_case_file_shot(
        self,
        src_image_path: Path,
        out_mp4_path: Path,
        card_title: str = "CONFIDENTIAL CASE FILE",
        stamp_text: Optional[str] = "VERIFIED AUDIT",
        duration: float = 3.5,
        rotation_deg: float = -4.5
    ) -> Path:
        self.log(f"Compositing 3D Stage Case File: '{card_title}' (Stamp: {stamp_text}) -> {out_mp4_path.name}...")
        with Image.open(src_image_path) as im:
            # Resize source to fitting document dimensions on the 1080p desk (e.g. 1100x750)
            doc_img = im.resize((1100, 750), Image.LANCZOS)
            MagnatesStageEngine.render_3d_stage_case_file(
                document_img=doc_img,
                out_mp4=out_mp4_path,
                card_title=card_title,
                stamp_text=stamp_text,
                duration=duration,
                rotation_deg=rotation_deg
            )

        self.log(f"3D Stage Case File rendered: {out_mp4_path.name} ({out_mp4_path.stat().st_size / 1024 / 1024:.2f} MB)")
        return out_mp4_path

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        src = Path(task["src_image"])
        out_name = task.get("out_name", f"stage_{src.stem}.mp4")
        out_mp4 = self.output_dir / out_name
        title = task.get("title", "CONFIDENTIAL CASE FILE")
        stamp = task.get("stamp_text")
        dur = float(task.get("duration", 3.5))
        rot = float(task.get("rotation_deg", -4.5))

        self.render_case_file_shot(src, out_mp4, card_title=title, stamp_text=stamp, duration=dur, rotation_deg=rot)
        return {
            "status": "success",
            "output_path": str(out_mp4),
            "size_mb": out_mp4.stat().st_size / 1024 / 1024
        }
