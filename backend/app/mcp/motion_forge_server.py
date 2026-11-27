"""
Motion Forge MCP Server for Antigravity & DocuForge.
Exposes Remotion, Lottie vector animations, and Pixverse AI Video Generation.
"""
import os
import sys
import json
import logging
from typing import Dict, Any, Optional

# Ensure project root in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.services.motion_forge import MotionForge
from backend.app.services.pixverse_client import PixverseClient

from mcp.server.mcpserver import MCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("motion_forge_mcp")

server = MCPServer("motion-forge")
motion_engine = MotionForge()
pixverse_engine = PixverseClient()

@server.tool(
    name="render_remotion",
    description="Renders a Remotion React composition (e.g., KineticTypography, SplitFlapBoard, LottieRadarPulse) to an MP4 video file."
)
def render_remotion(
    composition_id: str,
    output_filename: str,
    props: Optional[str] = None,
    codec: str = "h264",
    fps: int = 30
) -> str:
    parsed_props = json.loads(props) if props else None
    result = motion_engine.render_remotion(
        composition_id=composition_id,
        output_filename=output_filename,
        props=parsed_props,
        codec=codec,
        fps=fps
    )
    return json.dumps(result, indent=2)

@server.tool(
    name="render_lottie",
    description="Renders a Lottie JSON vector animation file into an MP4/ProRes video with alpha transparency."
)
def render_lottie(
    lottie_json_path: str,
    output_filename: str,
    width: int = 1920,
    height: int = 1080,
    duration_in_frames: int = 150,
    fps: int = 30
) -> str:
    result = motion_engine.render_lottie(
        lottie_json_path=lottie_json_path,
        output_filename=output_filename,
        width=width,
        height=height,
        duration_in_frames=duration_in_frames,
        fps=fps
    )
    return json.dumps(result, indent=2)

@server.tool(
    name="generate_pixverse_video",
    description="Dispatches a cinematic AI video generation request to the Pixverse API."
)
def generate_pixverse_video(
    prompt: str,
    negative_prompt: str = "blurry, low quality, cartoon, deformed",
    aspect_ratio: str = "16:9",
    duration: int = 5,
    quality: str = "1080p",
    motion_mode: str = "cinematic"
) -> str:
    result = pixverse_engine.generate_video(
        prompt=prompt,
        negative_prompt=negative_prompt,
        aspect_ratio=aspect_ratio,
        duration=duration,
        quality=quality,
        motion_mode=motion_mode
    )
    return json.dumps(result, indent=2)

@server.tool(
    name="query_pixverse_status",
    description="Checks the generation status of a Pixverse AI video task and returns the downloadable URL."
)
def query_pixverse_status(video_id: str) -> str:
    result = pixverse_engine.query_status(video_id)
    return json.dumps(result, indent=2)

@server.tool(
    name="list_motion_templates",
    description="Lists all available motion graphics templates across Remotion, Lottie, D3.js, and MapLibre in Motion Forge."
)
def list_motion_templates() -> str:
    templates = motion_engine.list_templates()
    return json.dumps(templates, indent=2)

if __name__ == "__main__":
    server.run()
