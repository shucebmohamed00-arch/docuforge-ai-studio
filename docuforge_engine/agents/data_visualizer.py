"""
DocuForge Multi-Agent Graphics Engine - Agent 4: Data Visualizer Agent
Builds dynamic financial infographics, stock market plunge line charts,
debt spiral waterfalls, alliance network maps, and intraday crisis countdown timers.
"""
import os
import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont
from ..core.base_agent import BaseAgent

class DataVisualizerAgent(BaseAgent):
    def __init__(self, output_dir: Optional[Path] = None):
        super().__init__(
            name="dataviz",
            role="Financial & Infographic Visualizer",
            description="Animates quantitative data, debt waterfalls, network webs, and crisis clocks into broadcast graphics."
        )
        self.output_dir = output_dir or (Path("c:/Users/Shueb/Desktop/youtu") / "data" / "media" / "financial_graphics")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render_stock_crash_chart(
        self,
        out_mp4: Path,
        ticker: str = "SWISSAIR (SR.SW)",
        start_val: float = 380.0,
        end_val: float = 1.25,
        duration: float = 3.5
    ) -> Path:
        W, H = 1920, 1080
        FPS = 30
        total_frames = int(duration * FPS)

        self.log(f"Rendering Financial Plunge Chart: {ticker} ({start_val} -> {end_val}) -> {out_mp4.name}...")

        font_large = None
        font_small = None
        for fp in ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf"]:
            if os.path.exists(fp):
                font_large = ImageFont.truetype(fp, 52)
                font_small = ImageFont.truetype(fp, 26)
                break
        if not font_large:
            font_large = font_small = ImageFont.load_default()

        # Generate realistic exponential decay curve with market noise
        t_steps = np.linspace(0, 1, total_frames)
        curve = start_val * np.exp(-3.5 * t_steps) + np.random.normal(0, 2.0, total_frames)
        curve = np.clip(curve, end_val, start_val)

        chart_x0, chart_y0 = 240, 260
        chart_w, chart_h = 1440, 620

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
            frame = Image.new("RGBA", (W, H), (10, 12, 16, 255))
            draw = ImageDraw.Draw(frame)

            # Grid lines
            for gy in range(chart_y0, chart_y0 + chart_h + 1, chart_h // 5):
                draw.line([(chart_x0, gy), (chart_x0 + chart_w, gy)], fill=(40, 45, 55, 120), width=1)
            for gx in range(chart_x0, chart_x0 + chart_w + 1, chart_w // 6):
                draw.line([(gx, chart_y0), (gx, chart_y0 + chart_h)], fill=(40, 45, 55, 120), width=1)

            # Header info
            draw.text((chart_x0, chart_y0 - 120), ticker, font=font_large, fill=(255, 255, 255, 255))
            cur_price = curve[f_idx]
            pct_down = ((cur_price - start_val) / start_val) * 100
            price_color = (235, 45, 45, 255) if pct_down < 0 else (45, 200, 80, 255)
            draw.text(
                (chart_x0, chart_y0 - 55),
                f"CHF {cur_price:.2f} ({pct_down:.1f}%) | CATASTROPHIC COLLAPSE",
                font=font_small,
                fill=price_color
            )

            # Animated Line Plot
            points = []
            for i in range(f_idx + 1):
                px = chart_x0 + int((i / total_frames) * chart_w)
                py = chart_y0 + chart_h - int(((curve[i] - end_val) / (start_val - end_val)) * chart_h)
                points.append((px, py))

            if len(points) > 1:
                draw.line(points, fill=(235, 40, 40, 255), width=4)
                # Glowing head dot
                hx, hy = points[-1]
                draw.ellipse([hx - 7, hy - 7, hx + 7, hy + 7], fill=(255, 100, 100, 255))

            proc.stdin.write(frame.tobytes())

        proc.stdin.close()
        proc.wait()

        self.log(f"Stock crash chart rendered: {out_mp4.name} ({out_mp4.stat().st_size / 1024 / 1024:.2f} MB)")
        return out_mp4

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        chart_type = task.get("type", "stock_crash")
        out_name = task.get("out_name", f"graphic_{chart_type}.mp4")
        out_mp4 = self.output_dir / out_name

        if chart_type == "stock_crash":
            self.render_stock_crash_chart(
                out_mp4=out_mp4,
                ticker=task.get("ticker", "SWISSAIR (SR.SW) - ZURICH EXCHANGE"),
                start_val=task.get("start_val", 380.0),
                end_val=task.get("end_val", 1.25),
                duration=task.get("duration", 3.5)
            )

        return {
            "status": "success",
            "output_path": str(out_mp4),
            "size_mb": out_mp4.stat().st_size / 1024 / 1024
        }
