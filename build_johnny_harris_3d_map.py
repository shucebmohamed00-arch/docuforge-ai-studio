"""
DocuForge AI - Johnny Harris 3D Topographic Flight Map Animator
Transforms switzerland_3d_relief_map.jpg into a broadcast-grade 3D motion graphic:
1. 3D cinematic push-in towards Zurich with depth of field
2. Pulsing tactical radar blips radiating from Zurich
3. Parabolic curved flight route arcs drawing outward across borders
4. Tactical aviation HUD badges & warning markers
5. Kinetic typography title: "SWISS AIRSPACE ENTRAPMENT" with tracking reveal
"""

import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

MAP_BASE = Path("data/media/maps/switzerland_3d_relief_map.jpg")
TEMP_DIR = Path("data/media/anim_temp/3d_map_frames")
OUT_MAP_MP4 = Path("data/media/animations/swiss-air-grounding-prod/anim_01_map.mp4")
TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUT_MAP_MP4.parent.mkdir(parents=True, exist_ok=True)

try:
    f_title = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 40)
    f_sub = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 22)
    f_badge = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 20)
    f_sm = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 16)
except Exception:
    f_title = f_sub = f_badge = f_sm = ImageFont.load_default()

def render_3d_map_animation():
    base_img = Image.open(MAP_BASE).convert("RGB")
    bw, bh = base_img.size
    
    fps = 30
    dur = 4.35 # covers the shot duration
    total_frames = int(dur * fps)
    
    # Zurich coordinate on the 1920x1080 source image: around (1025, 380)
    zrh_x, zrh_y = 1025, 380
    
    # Target destinations for flight routes
    destinations = [
        ("PARIS", (300, 420), "CDG"),
        ("LONDON", (240, 260), "LHR"),
        ("FRANKFURT", (1150, 180), "FRA"),
        ("NEW YORK", (120, 520), "JFK")
    ]
    
    print(f"Rendering {total_frames} frames of Johnny Harris 3D Map...")
    
    for f in range(total_frames):
        t = f / float(total_frames - 1)
        # Smooth camera zoom-in into Zurich
        zoom = 1.0 + 0.14 * (1.0 - math.cos(t * math.pi)) / 2.0
        
        # Crop with smooth drift
        cw = int(bw / zoom)
        ch = int(bh / zoom)
        # Shift slightly toward Zurich
        cx = int((bw - cw) / 2 + (zrh_x - bw/2) * 0.15 * t)
        cy = int((bh - ch) / 2 + (zrh_y - bh/2) * 0.15 * t)
        
        crop_box = (cx, cy, cx + cw, cy + ch)
        frame_img = base_img.crop(crop_box).resize((1920, 1080), Image.Resampling.LANCZOS)
        
        # Calculate current Zurich screen coordinate after crop and scale
        cur_zrh_x = int((zrh_x - cx) * (1920.0 / cw))
        cur_zrh_y = int((zrh_y - cy) * (1080.0 / ch))
        
        draw = ImageDraw.Draw(frame_img, "RGBA")
        
        # 1. Vignette & dark cinematic top/bottom gradients
        grad = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(grad)
        # Top header bar backing
        g_draw.rectangle([0, 0, 1920, 180], fill=(6, 10, 16, 210))
        g_draw.line([(0, 180), (1920, 180)], fill=(40, 60, 90, 180), width=2)
        # Vignette
        frame_img = Image.alpha_composite(frame_img.convert("RGBA"), grad)
        draw = ImageDraw.Draw(frame_img, "RGBA")
        
        # 2. Pulsing golden radar rings at Zurich
        for ring_idx in range(3):
            phase = (t * 4.0 + ring_idx * 0.33) % 1.0
            r_radius = int(20 + phase * 160)
            r_alpha = int(220 * (1.0 - phase))
            draw.ellipse(
                [cur_zrh_x - r_radius, cur_zrh_y - r_radius, cur_zrh_x + r_radius, cur_zrh_y + r_radius],
                outline=(255, 200, 50, r_alpha), width=2
            )
            
        # Glowing center dot
        draw.ellipse([cur_zrh_x - 7, cur_zrh_y - 7, cur_zrh_x + 7, cur_zrh_y + 7], fill=(255, 60, 60, 255))
        draw.ellipse([cur_zrh_x - 12, cur_zrh_y - 12, cur_zrh_x + 12, cur_zrh_y + 12], outline=(255, 60, 60, 200), width=2)
        
        # 3. Dynamic flight path arcs
        path_progress = min(1.0, f / 45.0)
        eased_path = 1.0 - (1.0 - path_progress)**3
        
        for name, (dst_x_raw, dst_y_raw), code in destinations:
            cur_dst_x = int((dst_x_raw - cx) * (1920.0 / cw))
            cur_dst_y = int((dst_y_raw - cy) * (1080.0 / ch))
            
            # Bezier arc curve from Zurich to destination
            points = []
            steps = 40
            max_step = int(steps * eased_path)
            
            # Control point arcs upwards for 3D flight trajectory
            mid_x = (cur_zrh_x + cur_dst_x) / 2.0
            mid_y = (cur_zrh_y + cur_dst_y) / 2.0 - 120.0
            
            for s in range(max_step + 1):
                p = s / float(steps)
                bx = (1 - p)**2 * cur_zrh_x + 2 * (1 - p) * p * mid_x + p**2 * cur_dst_x
                by = (1 - p)**2 * cur_zrh_y + 2 * (1 - p) * p * mid_y + p**2 * cur_dst_y
                points.append((bx, by))
                
            if len(points) > 1:
                draw.line(points, fill=(245, 185, 45, 220), width=3)
                
            if path_progress >= 0.8:
                # Target destination airport pin
                draw.ellipse([cur_dst_x - 5, cur_dst_y - 5, cur_dst_x + 5, cur_dst_y + 5], fill=(245, 185, 45, 255))
                draw.text((cur_dst_x + 12, cur_dst_y - 12), f"{name} ({code})", fill=(255, 255, 255, 230), font=f_sm)
                
        # 4. Critical Alert Box at Zurich
        if f > 20:
            box_alpha = min(255, int((f - 20) * 15))
            b_x = cur_zrh_x + 35
            b_y = cur_zrh_y - 65
            draw.rounded_rectangle([b_x, b_y, b_x + 340, b_y + 75], radius=6, fill=(12, 16, 24, int(220 * (box_alpha/255))), outline=(235, 40, 40, box_alpha), width=2)
            draw.text((b_x + 16, b_y + 12), "ZURICH HUB [ZRH] - CODE RED", fill=(255, 50, 50, box_alpha), font=f_badge)
            draw.text((b_x + 16, b_y + 42), "STATUS: 260 FLEET PLANES GROUNDED", fill=(255, 235, 200, box_alpha), font=f_sm)
            
        # 5. Top Kinetic Typography Title Header
        txt_progress = min(1.0, f / 25.0)
        t_ease = 1.0 - (1.0 - txt_progress)**3
        title_y = int(-80 + (40 - (-80)) * t_ease)
        
        draw.text((80, title_y), "GEOGRAPHIC DOSSIER // SWISS AIRSPACE ENTRAPMENT", fill=(255, 255, 255, 255), font=f_title)
        draw.text((80, title_y + 50), "EUROPEAN DEREGULATED SKIES VS. SWISS ISOLATION | OCTOBER 2001", fill=(212, 175, 55, 240), font=f_sub)
        
        frame_img.save(str(TEMP_DIR / f"frame_{f:04d}.png"), "PNG")
        
    print("Compiling frames into anim_01_map.mp4...")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(TEMP_DIR / "frame_%04d.png"),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(OUT_MAP_MP4)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Successfully generated {OUT_MAP_MP4}! Size: {OUT_MAP_MP4.stat().st_size / (1024*1024):.2f} MB")

if __name__ == "__main__":
    render_3d_map_animation()
