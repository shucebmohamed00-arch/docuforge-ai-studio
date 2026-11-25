"""
DocuForge Multi-Agent Graphics Engine - Agent 3: 3D Document Inspector Agent
Creates documentary document animations with real-time orange/yellow highlighter sweeps,
distressed red rubber stamp slams, impact flashes, and dynamic camera recoil physics.
"""
import os
import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from ..core.base_agent import BaseAgent

class DocumentInspectorAgent(BaseAgent):
    def __init__(self, output_dir: Optional[Path] = None):
        super().__init__(
            name="doc_inspector",
            role="3D Document & Rubber Stamp Inspector",
            description="Animates historical balance sheets and news headlines with highlighter sweeps and distressed rubber stamps."
        )
        self.output_dir = output_dir or (Path("c:/Users/Shueb/Desktop/youtu") / "data" / "media" / "advanced_25d")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_rubber_stamp(self, stamp_text: str, sub_text: str = "", stamp_color: tuple = (215, 25, 25)) -> Image.Image:
        SW, SH = 640, 220
        img = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Distressed border lines
        draw.rectangle([12, 12, SW - 12, SH - 12], outline=stamp_color + (240,), width=8)
        draw.rectangle([24, 24, SW - 24, SH - 24], outline=stamp_color + (220,), width=3)

        font_stamp = None
        font_sub = None
        for fp in ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"]:
            if os.path.exists(fp):
                font_stamp = ImageFont.truetype(fp, 60)
                font_sub = ImageFont.truetype(fp, 26)
                break
        if not font_stamp:
            font_stamp = font_sub = ImageFont.load_default()

        draw.text((SW // 2, SH // 2 - (18 if sub_text else 0)), stamp_text.upper(), font=font_stamp, fill=stamp_color + (250,), anchor="mm")
        if sub_text:
            draw.text((SW // 2, SH // 2 + 48), sub_text.upper(), font=font_sub, fill=stamp_color + (220,), anchor="mm")

        # Distress texture
        grit = np.random.randint(0, 255, (SH, SW), dtype=np.uint8)
        grit_mask = grit < 45
        arr = np.array(img)
        arr[grit_mask, 3] = 0
        return Image.fromarray(arr)

    def render_document_inspection(
        self,
        doc_image_or_video: Path,
        out_mp4: Path,
        stamp_title: str,
        stamp_sub: str,
        highlight_box: Optional[tuple] = None, # (x, y, w, h)
        duration: float = 3.2,
        impact_time: float = 1.3
    ) -> Path:
        W, H = 1920, 1080
        FPS = 30
        total_frames = int(duration * FPS)
        impact_frame = int(impact_time * FPS)

        self.log(f"Rendering Document Inspection: Stamp '{stamp_title}' -> {out_mp4.name}...")

        # Prepare base document plate
        if str(doc_image_or_video).endswith(".mp4"):
            temp_doc_img = self.output_dir / "temp_doc_plate.jpg"
            subprocess.run([
                "ffmpeg", "-y", "-ss", "0.5", "-i", str(doc_image_or_video),
                "-vframes", "1", "-s", "1920x1080", str(temp_doc_img)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            doc_plate = Image.open(temp_doc_img).convert("RGBA")
            temp_doc_img.unlink(missing_ok=True)
        else:
            doc_plate = Image.open(doc_image_or_video).convert("RGBA").resize((W, H), Image.LANCZOS)

        # Distressed stamp graphic
        stamp_img = self.create_rubber_stamp(stamp_title, stamp_sub)
        stamp_rot = stamp_img.rotate(-7.5, expand=True, resample=Image.BICUBIC)

        cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo", "-vcodec", "rawvideo",
            "-s", f"{W}x{H}", "-pix_fmt", "rgba", "-r", str(FPS),
            "-i", "-",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "19",
            "-pix_fmt", "yuv420p", str(out_mp4)
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for f_idx in range(total_frames):
            frame = doc_plate.copy()

            # 1. Animated Orange Highlighter Sweep
            if highlight_box:
                hx, hy, hw, hh = highlight_box
                # Sweep completes before stamp impact
                sweep_prog = min(1.0, max(0.0, (f_idx / (impact_frame - 5))))
                cur_w = int(hw * sweep_prog)
                if cur_w > 0:
                    hl_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    draw_hl = ImageDraw.Draw(hl_layer)
                    draw_hl.rectangle([hx, hy, hx + cur_w, hy + hh], fill=(255, 150, 0, 110))
                    frame = Image.alpha_composite(frame, hl_layer)

            # 2. Distressed Rubber Stamp Slam Physics
            if f_idx >= impact_frame:
                sf = f_idx - impact_frame
                # Slam down: rapid shrink with camera impact
                if sf < 4:
                    scale = 1.8 - sf * 0.20
                    alpha = 255
                    shake_x = np.random.randint(-14, 15)
                    shake_y = np.random.randint(-14, 15)
                else:
                    scale = 1.0
                    alpha = 255
                    decay = max(0, 12 - sf)
                    shake_x = int(np.random.randint(-decay, decay + 1)) if decay > 0 else 0
                    shake_y = int(np.random.randint(-decay, decay + 1)) if decay > 0 else 0

                cur_w, cur_h = int(stamp_rot.width * scale), int(stamp_rot.height * scale)
                stamp_scaled = stamp_rot.resize((cur_w, cur_h), Image.BILINEAR)

                sx = W // 2 - cur_w // 2 + shake_x
                sy = H // 2 - cur_h // 2 + shake_y

                # 1-frame impact flash
                if sf == 0:
                    flash = Image.new("RGBA", (W, H), (255, 255, 255, 120))
                    frame = Image.alpha_composite(frame, flash)

                frame.paste(stamp_scaled, (sx, sy), stamp_scaled)

            proc.stdin.write(frame.tobytes())

        proc.stdin.close()
        proc.wait()

        self.log(f"Document inspection rendered successfully: {out_mp4.name} ({out_mp4.stat().st_size / 1024 / 1024:.2f} MB)")
        return out_mp4

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        src = Path(task["document_path"])
        out_name = task.get("out_name", f"doc_stamp_{src.stem}.mp4")
        out_mp4 = self.output_dir / out_name

        self.render_document_inspection(
            doc_image_or_video=src,
            out_mp4=out_mp4,
            stamp_title=task.get("stamp_title", "INSOLVENCY AUDIT"),
            stamp_sub=task.get("stamp_sub", "VERIFIED DEBT SPIKE"),
            highlight_box=task.get("highlight_box", (200, 480, 800, 45)),
            duration=task.get("duration", 3.2),
            impact_time=task.get("impact_time", 1.2)
        )

        return {
            "status": "success",
            "output_path": str(out_mp4),
            "size_mb": out_mp4.stat().st_size / 1024 / 1024
        }
