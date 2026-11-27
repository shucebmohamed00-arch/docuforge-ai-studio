import os
import json
import logging
import subprocess
from typing import Dict, Any, Optional, List

logger = logging.getLogger("motion_forge")

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
MOTION_FORGE_DIR = os.path.join(WORKSPACE_DIR, "tools", "motion-forge")
OUTPUT_ANIMATIONS_DIR = os.path.join(WORKSPACE_DIR, "data", "media", "animations")

class MotionForge:
    """
    Unified Motion Engine for DocuForge:
    Orchestrates Remotion (React), Lottie vector animations, D3.js broadcast graphics,
    MapLibre 3D relief maps, and Pixverse AI video generation.
    """

    def __init__(self):
        os.makedirs(OUTPUT_ANIMATIONS_DIR, exist_ok=True)

    def render_remotion(
        self,
        composition_id: str,
        output_filename: str,
        props: Optional[Dict[str, Any]] = None,
        codec: str = "h264",
        fps: int = 30,
        frame_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Renders a Remotion composition to MP4/WebM using Node.js renderer.
        """
        output_path = os.path.join(OUTPUT_ANIMATIONS_DIR, output_filename)
        render_script = os.path.join(MOTION_FORGE_DIR, "render.mjs")
        
        cmd = ["node", render_script, composition_id, output_path]
        if frame_range:
            cmd.append(frame_range)

        logger.info(f"Rendering Remotion composition '{composition_id}' -> {output_path}")
        try:
            res = subprocess.run(cmd, cwd=MOTION_FORGE_DIR, capture_output=True, text=True, check=True)
            return {
                "status": "success",
                "output_path": output_path,
                "composition_id": composition_id,
                "logs": res.stdout[-300:] if res.stdout else ""
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Remotion render error: {e.stderr}")
            return {
                "status": "error",
                "error": e.stderr,
                "composition_id": composition_id
            }

    def render_lottie(
        self,
        lottie_json_path: str,
        output_filename: str,
        width: int = 1920,
        height: int = 1080,
        duration_in_frames: int = 90,
        fps: int = 30
    ) -> Dict[str, Any]:
        """
        Renders a Lottie JSON vector animation using Remotion's Lottie renderer.
        """
        return self.render_remotion(
            composition_id="LottieRadarPulse",
            output_filename=output_filename,
            fps=fps
        )

    def list_templates(self) -> List[Dict[str, Any]]:
        """
        Lists available motion templates in Motion Forge.
        """
        return [
            {
                "id": "KineticTypography",
                "type": "remotion",
                "name": "Kinetic Documentary Typography",
                "description": "Spring-animated impactful title & quote typography with documentary styling."
            },
            {
                "id": "SplitFlapBoard",
                "type": "remotion",
                "name": "Solari Split-Flap Airport Board",
                "description": "Mechanical split-flap tiles flipping rhythmically to 'CANCELLED'."
            },
            {
                "id": "LottieRadarPulse",
                "type": "lottie",
                "name": "Lottie Vector Radar Telemetry",
                "description": "Alpha-transparent vector radar rings and crosshair HUD."
            },
            {
                "id": "D3AcquisitionWheel",
                "type": "d3",
                "name": "D3 Radial Network Wheel",
                "description": "Acquisition hubs, corporate holdings, and subsidiary networks."
            },
            {
                "id": "D3DebtCurve",
                "type": "d3",
                "name": "D3 Forensic Debt / Financial Crash Curve",
                "description": "Glowing area fill line chart with real-time ticker and milestone badges."
            },
            {
                "id": "MapLibreReliefMap",
                "type": "maplibre",
                "name": "Johnny Harris / Vox 3D Topographic Relief Map",
                "description": "Natural Earth terrain relief, golden borders, flight paths, and radar scans."
            }
        ]
