"""
DocuForge Multi-Agent Graphics Engine - 3D Physical Stage & Torn Paper Engine (MagnatesMedia Tier)
Generates physical 3D desk environments: dark mahogany executive wood, overhead volumetric spotlights,
jagged torn-paper archival edges, multi-layer contact drop shadows, and cinematic depth of field.
"""
import os
import cv2
import subprocess
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class MagnatesStageEngine:
    W, H = 1920, 1080
    FPS = 30

    @classmethod
    def create_mahogany_desk_texture(cls) -> Image.Image:
        """
        Synthesizes a rich, dark mahogany/walnut executive desk surface with wood grain,
        specular sheen, and an overhead warm volumetric spotlight pool.
        """
        desk_arr = np.zeros((cls.H, cls.W, 3), dtype=np.float32)

        # 1. Base dark walnut wood tones
        # Horizontal wood grain with micro-variations
        y_coords = np.linspace(0, 1, cls.H)[:, None]
        x_coords = np.linspace(0, 1, cls.W)[None, :]

        # Wood grain frequency
        grain = np.sin(y_coords * 90.0 + np.sin(x_coords * 12.0) * 2.5) * 0.5 + 0.5
        grain_fine = np.sin(y_coords * 280.0) * 0.5 + 0.5
        wood_pattern = 0.7 * grain + 0.3 * grain_fine

        # Base mahogany RGB: R ~ 28-40, G ~ 14-22, B ~ 10-15
        desk_arr[:, :, 0] = 24.0 + 16.0 * wood_pattern
        desk_arr[:, :, 1] = 12.0 + 9.0 * wood_pattern
        desk_arr[:, :, 2] = 8.0 + 6.0 * wood_pattern

        # 2. Overhead Volumetric Spotlight (Warm Amber Beam)
        cx, cy = cls.W // 2, cls.H // 2 - 40
        dist_sq = (np.arange(cls.W)[None, :] - cx) ** 2 + ((np.arange(cls.H)[:, None] - cy) * 1.35) ** 2
        radius = 700.0
        spotlight = np.exp(-dist_sq / (2.0 * (radius ** 2)))

        # Spotlight warm color boost (golden amber glow in the center)
        desk_arr[:, :, 0] += spotlight * 45.0
        desk_arr[:, :, 1] += spotlight * 30.0
        desk_arr[:, :, 2] += spotlight * 15.0

        # Clip and convert to PIL Image
        desk_arr = np.clip(desk_arr, 0, 255).astype(np.uint8)
        desk_img = Image.fromarray(desk_arr).convert("RGBA")

        # 3. Add subtle vignette border around the perimeter
        vignette_mask = Image.new("L", (cls.W, cls.H), 0)
        vdraw = ImageDraw.Draw(vignette_mask)
        vdraw.ellipse([80, 40, cls.W - 80, cls.H - 40], fill=255)
        vignette_mask = vignette_mask.filter(ImageFilter.GaussianBlur(160))

        vignette_layer = Image.new("RGBA", (cls.W, cls.H), (6, 4, 3, 210))
        inv_mask = Image.eval(vignette_mask, lambda a: 255 - a)
        desk_img.paste(vignette_layer, (0, 0), inv_mask)

        return desk_img

    @classmethod
    def apply_torn_paper_edge(cls, src_img: Image.Image, border_tear: int = 14) -> Image.Image:
        """
        Crops image with an organic, jagged torn-paper border and white paper-core fringe.
        """
        w, h = src_img.size
        # Generate jagged alpha mask using random walk along perimeter
        mask = Image.new("L", (w, h), 255)
        m_arr = np.array(mask)

        # Top & Bottom jagged edge
        top_offset = np.random.randint(0, border_tear, w)
        bot_offset = np.random.randint(0, border_tear, w)
        for x in range(w):
            m_arr[:top_offset[x], x] = 0
            m_arr[h - bot_offset[x]:, x] = 0

        # Left & Right jagged edge
        left_offset = np.random.randint(0, border_tear, h)
        right_offset = np.random.randint(0, border_tear, h)
        for y in range(h):
            m_arr[y, :left_offset[y]] = 0
            m_arr[y, w - right_offset[y]:] = 0

        mask_torn = Image.fromarray(m_arr).filter(ImageFilter.GaussianBlur(0.8))

        # Create paper plate with white fiber fringe backing
        paper_canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        white_backing = Image.new("RGBA", (w, h), (245, 243, 238, 255))
        
        # Slightly dilated mask for white torn paper fringe
        white_mask = mask_torn.filter(ImageFilter.MaxFilter(5))
        paper_canvas.paste(white_backing, (0, 0), white_mask)

        # Paste actual content inside
        content_rgba = src_img.convert("RGBA")
        paper_canvas.paste(content_rgba, (0, 0), mask_torn)

        return paper_canvas

    @classmethod
    def render_3d_stage_case_file(
        cls,
        document_img: Image.Image,
        out_mp4: Path,
        card_title: str = "CONFIDENTIAL CASE FILE",
        stamp_text: Optional[str] = "VERIFIED AUDIT",
        duration: float = 3.5,
        rotation_deg: float = -4.5
    ) -> Path:
        """
        Renders a physical 3D scene:
        - Mahogany wood desk background with spotlight
        - Multi-layer soft contact drop shadows cast onto desk
        - Document drops/slides onto desk with organic settle physics
        - Subtle camera push-in (Ken Burns)
        """
        total_frames = int(duration * cls.FPS)
        desk_bg = cls.create_mahogany_desk_texture()

        # Prepare torn paper document
        paper_doc = cls.apply_torn_paper_edge(document_img)
        dw, dh = paper_doc.size

        # Distressed stamp if requested
        if stamp_text:
            stamp_layer = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
            sdraw = ImageDraw.Draw(stamp_layer)
            sfont = None
            for fp in ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"]:
                if os.path.exists(fp):
                    sfont = ImageFont.truetype(fp, 56)
                    break
            if not sfont:
                sfont = ImageFont.load_default()

            # Stamp box
            sb_w, sb_h = 560, 110
            sb_x, sb_y = dw // 2 - sb_w // 2, dh // 2 - sb_h // 2
            sdraw.rectangle([sb_x, sb_y, sb_x + sb_w, sb_y + sb_h], outline=(215, 25, 25, 240), width=6)
            sdraw.text((dw // 2, dh // 2), stamp_text.upper(), font=sfont, fill=(215, 25, 25, 245), anchor="mm")
            
            # Erode stamp
            s_arr = np.array(stamp_layer)
            grit = np.random.randint(0, 255, (dh, dw), dtype=np.uint8)
            s_arr[grit < 40, 3] = 0
            stamp_layer = Image.fromarray(s_arr).rotate(8.0, resample=Image.BICUBIC)
            paper_doc.paste(stamp_layer, (0, 0), stamp_layer)

        # Rotate document with slight organic tilt
        doc_rotated = paper_doc.rotate(rotation_deg, expand=True, resample=Image.BICUBIC)
        rw, rh = doc_rotated.size

        # Multi-layer drop shadows
        shadow_soft = Image.new("RGBA", (rw + 80, rh + 80), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow_soft)
        s_draw.rectangle([40, 40, rw + 40, rh + 40], fill=(0, 0, 0, 140))
        shadow_soft = shadow_soft.filter(ImageFilter.GaussianBlur(28))

        shadow_contact = Image.new("RGBA", (rw + 30, rh + 30), (0, 0, 0, 0))
        sc_draw = ImageDraw.Draw(shadow_contact)
        sc_draw.rectangle([15, 15, rw + 15, rh + 15], fill=(0, 0, 0, 220))
        shadow_contact = shadow_contact.filter(ImageFilter.GaussianBlur(8))

        # Composite base card + shadows onto static plate
        card_plate = Image.new("RGBA", (rw + 80, rh + 80), (0, 0, 0, 0))
        card_plate.paste(shadow_soft, (15, 25), shadow_soft)
        card_plate.paste(shadow_contact, (6, 10), shadow_contact)
        card_plate.paste(doc_rotated, (20, 20), doc_rotated)

        pw, ph = card_plate.size
        cx, cy = cls.W // 2, cls.H // 2

        # Pipe frames directly to FFmpeg
        out_mp4.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo", "-vcodec", "rawvideo",
            "-s", f"{cls.W}x{cls.H}", "-pix_fmt", "rgba", "-r", str(cls.FPS),
            "-i", "-",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "19",
            "-pix_fmt", "yuv420p", str(out_mp4)
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for f_idx in range(total_frames):
            prog = f_idx / total_frames
            # Physical camera push-in: 0.98 -> 1.05
            cam_scale = 0.98 + 0.07 * prog
            
            # Subtle paper drop settle in first 10 frames
            if f_idx < 10:
                drop_scale = 1.08 - (f_idx / 10.0) * 0.08
                current_scale = cam_scale * drop_scale
            else:
                current_scale = cam_scale

            nw, nh = int(pw * current_scale), int(ph * current_scale)
            scaled_plate = card_plate.resize((nw, nh), Image.BILINEAR)

            frame = desk_bg.copy()
            frame.paste(scaled_plate, (cx - nw // 2, cy - nh // 2), scaled_plate)

            proc.stdin.write(frame.tobytes())

        proc.stdin.close()
        proc.wait()
        return out_mp4
