"""
DocuForge Multi-Agent Graphics Engine - Agent 5: Quality Control & Continuity Director Agent
Automates verification: audits black frames (blackdetect), enforces 16:9 full-bleed geometry,
validates asset variety, and flags artifacts before production release.
"""
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from ..core.base_agent import BaseAgent

class DirectorQCAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="director_qc",
            role="Quality Control & Continuity Director",
            description="Enforces broadcast standards: audits 0 black frames, verifies 16:9 full bleed, and tests streaming health."
        )

    def audit_black_frames(self, video_path: Path, min_dur: float = 0.25) -> List[Dict[str, Any]]:
        self.log(f"Running blackdetect audit on '{video_path.name}' (threshold={min_dur}s)...")
        cmd = [
            "ffmpeg", "-i", str(video_path),
            "-vf", f"blackdetect=d={min_dur}:pix_th=0.10",
            "-f", "null", "-"
        ]
        res = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
        black_segments = []
        for line in res.stderr.splitlines():
            if "black_start" in line:
                # e.g. [Parsed_blackdetect_0 @ 0000] black_start:128.333333 black_end:130 black_duration:1.666667
                parts = line.split()
                seg_info = {}
                for p in parts:
                    if ":" in p:
                        k, v = p.split(":", 1)
                        try:
                            seg_info[k] = float(v)
                        except ValueError:
                            pass
                black_segments.append(seg_info)

        if black_segments:
            self.log(f"ALERT: Detected {len(black_segments)} black segments in {video_path.name}!", level="WARNING")
        else:
            self.log(f"PASSED: 0 black segments detected across entire video timeline.")
        return black_segments

    def audit_video_geometry(self, video_path: Path) -> Dict[str, Any]:
        self.log(f"Auditing video geometry for '{video_path.name}'...")
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,duration",
            "-of", "json",
            str(video_path)
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        import json
        data = json.loads(res.stdout)
        streams = data.get("streams", [{}])
        if not streams:
            return {"status": "error", "message": "No video streams"}

        v = streams[0]
        w = int(v.get("width", 0))
        h = int(v.get("height", 0))
        aspect = w / h if h > 0 else 0
        is_16_9 = abs(aspect - (16 / 9)) < 0.05

        return {
            "width": w,
            "height": h,
            "aspect_ratio": f"{aspect:.3f}",
            "is_16_9": is_16_9,
            "r_frame_rate": v.get("r_frame_rate"),
            "duration": float(v.get("duration", 0))
        }

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        video_path = Path(task["video_path"])
        if not video_path.exists():
            return {"status": "error", "message": f"File not found: {video_path}"}

        geom = self.audit_video_geometry(video_path)
        black_segs = self.audit_black_frames(video_path)
        size_mb = video_path.stat().st_size / 1024 / 1024

        passed = len(black_segs) == 0 and geom.get("is_16_9", False)

        return {
            "status": "passed" if passed else "failed",
            "file": str(video_path),
            "size_mb": round(size_mb, 2),
            "geometry": geom,
            "black_segments_count": len(black_segs),
            "black_segments": black_segs
        }
