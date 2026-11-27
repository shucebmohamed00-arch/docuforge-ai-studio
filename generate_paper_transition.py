"""
DocuForge AI - Procedural Paper Tear & Rip Transition Generator
Creates broadcast-grade Johnny Harris / MagnatesMedia torn paper wipes with alpha channel:
1. paper_tear_wipe_left.mov: Jagged fibrous paper edge sweeping left-to-right with soft drop shadow.
"""

import math
import random
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import subprocess

OUT_DIR = Path("data/media/overlays")
TEMP_DIR = Path("data/media/anim_temp/paper_tear")
OUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def generate_torn_edge(height, amp=25, freq=0.03):
    # Generates organic jagged torn paper boundary
    random.seed(42)
    edge = []
    curr = 0
    for y in range(height):
        # Multi-octave organic wobble
        wobble = (
            math.sin(y * freq) * amp +
            math.sin(y * freq * 2.7) * (amp * 0.4) +
            math.sin(y * freq * 6.3) * (amp * 0.15) +
            (random.random() - 0.5) * 6 # Paper fiber micro-roughness
        )
        edge.append(wobble)
    return edge

def create_paper_wipe():
    width, height = 1920, 1080
    fps = 30
    total_frames = 18 # 0.6 seconds fast dynamic whip
    edge_noise = generate_torn_edge(height)
    
    # Base paper tone with subtle vintage paper grain
    paper_base = (244, 240, 230)
    shadow_color = (15, 18, 25, 120)
    
    for f in range(total_frames):
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Eased sweep across screen: from x = -200 to x = 2150
        t = f / float(total_frames - 1)
        # Cubic ease-in-out
        if t < 0.5:
            ease = 4 * t * t * t
        else:
            ease = 1 - pow(-2 * t + 2, 3) / 2
            
        x_base = int(-300 + ease * (width + 600))
        
        # 1. Draw Drop Shadow first (offset slightly left of the torn edge)
        shadow_poly = []
        for y in range(height):
            x_edge = x_base + edge_noise[y]
            shadow_poly.append((x_edge + 15, y))
        shadow_poly.append((0, height))
        shadow_poly.append((0, 0))
        
        # Soft shadow mask
        sh_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        sh_draw = ImageDraw.Draw(sh_img)
        sh_draw.polygon(shadow_poly, fill=(0, 0, 0, 90))
        sh_img = sh_img.filter(ImageFilter.GaussianBlur(radius=8))
        img.paste(sh_img, (0, 0), sh_img)
        
        # 2. Draw Torn Paper polygon
        paper_poly = []
        for y in range(height):
            x_edge = x_base + edge_noise[y]
            paper_poly.append((x_edge, y))
        paper_poly.append((0, height))
        paper_poly.append((0, 0))
        
        draw.polygon(paper_poly, fill=(*paper_base, 255))
        
        # 3. Add highlighted white fibrous torn paper fringe along the edge
        fiber_points = []
        for y in range(0, height, 2):
            x_edge = x_base + edge_noise[y]
            fiber_points.append((x_edge, y))
        draw.line(fiber_points, fill=(255, 255, 255, 220), width=3)
        
        # Add subtle paper texture lines
        for y in range(0, height, 4):
            x_edge = x_base + edge_noise[y]
            if x_edge > 20:
                draw.line([(x_edge - 10, y), (x_edge - 2, y)], fill=(230, 225, 215, 140), width=1)
                
        img.save(str(TEMP_DIR / f"frame_{f:04d}.png"), "PNG")
        
    out_mov = OUT_DIR / "paper_tear_wipe.mov"
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(TEMP_DIR / "frame_%04d.png"),
        "-c:v", "qtrle",
        str(out_mov)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Generated {out_mov} successfully!")

if __name__ == "__main__":
    create_paper_wipe()
