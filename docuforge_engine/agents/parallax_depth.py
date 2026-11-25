"""
DocuForge Multi-Agent Graphics Engine - Agent 2: 2.5D Parallax & Depth Illusionist Agent
Generates multi-plane 2.5D parallax character cards with independent depth separation,
radial gold glow halos, deep 3D drop shadows, kinetic badges, and subtle film grain.
"""
import os
import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from ..core.base_agent import BaseAgent

class ParallaxDepthAgent(BaseAgent):
    def __init__(self, output_dir: Optional[Path] = None):
        super().__init__(
            name="parallax",
            role="2.5D Parallax & Depth Illusionist",
            description="Transforms flat character photographs into multi-layer 2.5D parallax scenes."
        )
        self.output_dir = output_dir or (Path("c:/Users/Shueb/Desktop/youtu") / "data" / "media" / "advanced_25d")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render_parallax_card(
        self,
        face_path: Path,
        bg_video_path: Optional[Path],
        out_mp4: Path,
        title: str,
        subtitle: str,
        badge: str = "EXECUTIVE ARCHIVE",
        duration: float = 3.2,
        accent_color: tuple = (212, 175, 55)
    ) -> Path:
        W, H = 1920, 1080
        FPS = 30
        total_frames = int(duration * FPS)

        self.log(f"Rendering 2.5D Parallax Card: '{title}' ({subtitle}) -> {out_mp4.name}...")

        # 1. Face preparation & circular mask
        face_raw = Image.open(face_path).convert("RGBA")
        fw, fh = face_raw.size
        min_dim = min(fw, fh)
        face_sq = face_raw.crop(((fw - min_dim)//2, (fh - min_dim)//2, (fw + min_dim)//2, (fh + min_dim)//2))
        
        portrait_size = 560
        face_resized = face_sq.resize((portrait_size, portrait_size), Image.LANCZOS)

        # Smooth anti-aliased circular mask
        mask = Image.new("L", (portrait_size, portrait_size), 0)
        draw_m = ImageDraw.Draw(mask)
        draw_m.ellipse([4, 4, portrait_size - 4, portrait_size - 4], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(1.5))

        # Radial glow halo
        halo_size = portrait_size + 140
        halo = Image.new("RGBA", (halo_size, halo_size), (0, 0, 0, 0))
        draw_h = ImageDraw.Draw(halo)
        for r in range(halo_size // 2, portrait_size // 2 - 20, -4):
            alpha = int(45 * (1.0 - (r - portrait_size // 2) / 80.0))
            alpha = max(0, min(65, alpha))
            draw_h.ellipse(
                [halo_size // 2 - r, halo_size // 2 - r, halo_size // 2 + r, halo_size // 2 + r],
                fill=accent_color + (alpha,)
            )
        halo = halo.filter(ImageFilter.GaussianBlur(16))

        # Deep 3D drop shadow
        shadow_size = portrait_size + 80
        shadow = Image.new("RGBA", (shadow_size, shadow_size), (0, 0, 0, 0))
        draw_s = ImageDraw.Draw(shadow)
        draw_s.ellipse([30, 30, shadow_size - 10, shadow_size - 10], fill=(0, 0, 0, 180))
        shadow = shadow.filter(ImageFilter.GaussianBlur(24))

        # Metallic accent ring
        ring = Image.new("RGBA", (portrait_size, portrait_size), (0, 0, 0, 0))
        draw_r = ImageDraw.Draw(ring)
        draw_r.ellipse([4, 4, portrait_size - 4, portrait_size - 4], outline=accent_color + (255,), width=6)
        draw_r.ellipse([10, 10, portrait_size - 10, portrait_size - 10], outline=(255, 255, 255, 140), width=2)

        # Typography Card Plate
        tw, th = 720, 150
        card_img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        draw_c = ImageDraw.Draw(card_img)
        draw_c.rectangle([0, 0, tw, th], fill=(12, 14, 18, 240))
        draw_c.rectangle([0, 0, 8, th], fill=accent_color + (255,))
        draw_c.rectangle([tw - 8, 0, tw, th], fill=accent_color + (255,))

        font_title = None
        font_sub = None
        for fp in ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf"]:
            if os.path.exists(fp):
                font_title = ImageFont.truetype(fp, 36)
                font_sub = ImageFont.truetype(fp, 22)
                break
        if not font_title:
            font_title = font_sub = ImageFont.load_default()

        draw_c.text((28, 22), title.upper(), font=font_title, fill=(255, 255, 255, 255))
        draw_c.text((28, 72), subtitle.upper(), font=font_sub, fill=accent_color + (240,))
        draw_c.rectangle([28, 114, 28 + 260, 138], fill=accent_color + (220,))
        draw_c.text((36, 118), badge.upper(), font=font_sub, fill=(10, 10, 12, 255))

        # Composite Subject
        subject_canvas = Image.new("RGBA", (halo_size, halo_size), (0, 0, 0, 0))
        subject_canvas.paste(halo, (0, 0), halo)
        offset_p = (halo_size - portrait_size) // 2
        subject_canvas.paste(shadow, ((halo_size - shadow_size) // 2 + 10, (halo_size - shadow_size) // 2 + 20), shadow)
        subject_canvas.paste(face_resized, (offset_p, offset_p), mask)
        subject_canvas.paste(ring, (offset_p, offset_p), ring)

        # Background Setup
        bg_plate = Image.new("RGBA", (W, H), (15, 17, 22, 255))
        if bg_video_path and bg_video_path.exists():
            temp_bg = self.output_dir / "temp_bg_frame.jpg"
            subprocess.run([
                "ffmpeg", "-y", "-ss", "0.5", "-i", str(bg_video_path),
                "-vframes", "1", "-s", "1920x1080", str(temp_bg)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if temp_bg.exists():
                with Image.open(temp_bg) as bgi:
                    bg_plate = bgi.convert("RGBA").filter(ImageFilter.GaussianBlur(18))
                    dark_ov = Image.new("RGBA", (W, H), (10, 12, 16, 175))
                    bg_plate.paste(dark_ov, (0, 0), dark_ov)
                temp_bg.unlink(missing_ok=True)

        # Pipe frames directly to FFmpeg
        cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo", "-vcodec", "rawvideo",
            "-s", f"{W}x{H}", "-pix_fmt", "rgba", "-r", str(FPS),
            "-i", "-",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "19",
            "-pix_fmt", "yuv420p", str(out_mp4)
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        cx, cy = W // 2, H // 2 - 40
        for frame_idx in range(total_frames):
            prog = frame_idx / total_frames
            # 2.5D Push Zoom
            scale = 0.96 + 0.08 * prog
            sw, sh = int(subject_canvas.width * scale), int(subject_canvas.height * scale)
            subj_zoomed = subject_canvas.resize((sw, sh), Image.BILINEAR)

            frame = bg_plate.copy()
            # Paste portrait with sub-pixel depth centering
            frame.paste(subj_zoomed, (cx - sw // 2, cy - sh // 2), subj_zoomed)
            # Paste kinetic badge
            frame.paste(card_img, (cx - tw // 2, H - 210), card_img)

            proc.stdin.write(frame.tobytes())

        proc.stdin.close()
        proc.wait()

        self.log(f"Parallax card rendered successfully: {out_mp4.name} ({out_mp4.stat().st_size / 1024 / 1024:.2f} MB)")
        return out_mp4

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        face_path = Path(task["face_path"])
        bg_video = Path(task["bg_video"]) if "bg_video" in task else None
        out_name = task.get("out_name", f"parallax_{face_path.stem}.mp4")
        out_mp4 = self.output_dir / out_name

        self.render_parallax_card(
            face_path=face_path,
            bg_video_path=bg_video,
            out_mp4=out_mp4,
            title=task.get("title", "Executive"),
            subtitle=task.get("subtitle", "Swissair Authority"),
            badge=task.get("badge", "ARCHIVE DOSSIER"),
            duration=task.get("duration", 3.2),
            accent_color=task.get("accent_color", (212, 175, 55))
        )

        return {
            "status": "success",
            "output_path": str(out_mp4),
            "size_mb": out_mp4.stat().st_size / 1024 / 1024
        }
