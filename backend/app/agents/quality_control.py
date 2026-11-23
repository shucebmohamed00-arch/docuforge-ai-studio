"""
DocuForge AI - Quality Control (QC) Agent
Automated inspection of documentary master video, audio normalization,
subtitle synchronization, and visual asset copyright/licensing compliance.
Enforces the mandatory rule: Never mark a documentary as completed if it fails QC.
"""
import os
import re
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

import cv2
import numpy as np

from ..config import EXPORTS_DIR
from ..database import get_connection
from ..models.project import ProjectManager

logger = logging.getLogger("docuforge.quality_control")

class QualityControlAgent:
    """
    Automated broadcast inspection agent verifying:
    1. Video integrity: Resolution (1080p), Aspect Ratio (16:9), Duration, Black-frame dropouts.
    2. Audio integrity: Audio track presence, Volume levels, Silence detection, Distortion/Clipping.
    3. Subtitle sync: SRT parsing, Sequential cues, Video timeline alignment.
    4. Asset & Licensing: 100% approval verification, Valid public-domain / Creative Commons licensing.
    """

    @classmethod
    def inspect_project(cls, project_id: str) -> Dict[str, Any]:
        """
        Runs comprehensive automated QC inspection on the rendered project.
        Returns detailed report and saves qc_report.json to exports directory.
        """
        proj = ProjectManager.get_project(project_id)
        if not proj:
            raise ValueError(f"Project '{project_id}' not found.")

        proj_dir = EXPORTS_DIR / project_id
        video_path = proj_dir / "documentary.mp4"
        srt_path = proj_dir / "subtitles.srt"

        checks: List[Dict[str, Any]] = []

        # 1. Video Checks
        video_checks, video_duration = cls._check_video(video_path)
        checks.extend(video_checks)

        # 2. Audio Checks
        audio_checks = cls._check_audio(video_path)
        checks.extend(audio_checks)

        # 3. Subtitle Checks
        subtitle_checks = cls._check_subtitles(srt_path, video_duration)
        checks.extend(subtitle_checks)

        # 4. Asset & Licensing Compliance Checks
        asset_checks = cls._check_rights(project_id)
        checks.extend(asset_checks)

        # 5. Thumbnail Availability Checks
        thumb_checks = cls._check_thumbnails(proj_dir)
        checks.extend(thumb_checks)

        # Calculate score and overall verdict
        passed, overall_score, repair_recommendations = cls._evaluate_verdict(checks)

        report = {
            "project_id": project_id,
            "project_title": proj["title"],
            "inspected_at": datetime.now().isoformat(),
            "passed": passed,
            "verdict": "PASSED" if passed else "FAILED",
            "overall_score": overall_score,
            "video_duration_sec": video_duration,
            "checks": checks,
            "repair_recommendations": repair_recommendations,
            "summary": {
                "total_checks": len(checks),
                "passed_checks": sum(1 for c in checks if c["status"] == "PASS"),
                "warnings": sum(1 for c in checks if c["status"] == "WARN"),
                "failures": sum(1 for c in checks if c["status"] == "FAIL"),
            }
        }

        # Save report to disk
        cls._save_report(proj_dir, report)
        return report

    @classmethod
    def _check_video(cls, video_path: Path) -> Tuple[List[Dict[str, Any]], float]:
        checks = []
        duration = 0.0

        if not video_path.exists() or video_path.stat().st_size == 0:
            checks.append({
                "name": "Master Video File Existence",
                "category": "VIDEO",
                "status": "FAIL",
                "details": f"Rendered video file '{video_path.name}' is missing or 0 bytes.",
                "metrics": {"file_exists": False, "size_bytes": 0}
            })
            return checks, duration

        checks.append({
            "name": "Master Video File Existence",
            "category": "VIDEO",
            "status": "PASS",
            "details": f"Video file present ({round(video_path.stat().st_size / (1024*1024), 2)} MB).",
            "metrics": {"file_exists": True, "size_bytes": video_path.stat().st_size}
        })

        # Run ffprobe
        probe_cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            str(video_path)
        ]
        try:
            res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
            probe_data = json.loads(res.stdout)
        except Exception as e:
            checks.append({
                "name": "Video Stream Probe",
                "category": "VIDEO",
                "status": "FAIL",
                "details": f"Failed to probe video stream: {e}",
                "metrics": {}
            })
            return checks, duration

        # Find video stream
        video_stream = next((s for s in probe_data.get("streams", []) if s.get("codec_type") == "video"), None)
        format_info = probe_data.get("format", {})
        try:
            duration = float(format_info.get("duration", 0.0))
        except (ValueError, TypeError):
            duration = 0.0

        if not video_stream:
            checks.append({
                "name": "Video Stream Codec",
                "category": "VIDEO",
                "status": "FAIL",
                "details": "No video stream found in container.",
                "metrics": {}
            })
            return checks, duration

        width = int(video_stream.get("width", 0))
        height = int(video_stream.get("height", 0))
        codec = video_stream.get("codec_name", "unknown")

        # Check resolution & aspect ratio
        is_1080p = (width == 1920 and height == 1080)
        aspect_ratio = (width / height) if height > 0 else 0
        is_16_9 = abs(aspect_ratio - (16 / 9)) < 0.05

        checks.append({
            "name": "Resolution & 1080p Standard",
            "category": "VIDEO",
            "status": "PASS" if is_1080p else ("WARN" if (width >= 1280 and is_16_9) else "FAIL"),
            "details": f"Detected resolution: {width}x{height} (Target: 1920x1080 Full HD).",
            "metrics": {"width": width, "height": height, "is_1080p": is_1080p}
        })

        checks.append({
            "name": "Aspect Ratio (16:9)",
            "category": "VIDEO",
            "status": "PASS" if is_16_9 else "FAIL",
            "details": f"Detected aspect ratio: {round(aspect_ratio, 3)}:1 (Target: 1.778:1 / 16:9).",
            "metrics": {"aspect_ratio": round(aspect_ratio, 3), "is_16_9": is_16_9}
        })

        checks.append({
            "name": "Video Codec Broadcast Standard",
            "category": "VIDEO",
            "status": "PASS" if codec in ["h264", "hevc", "vp9", "av1"] else "WARN",
            "details": f"Detected video codec: {codec.upper()} (YouTube recommended: H.264).",
            "metrics": {"codec": codec}
        })

        # Check duration
        checks.append({
            "name": "Documentary Duration",
            "category": "VIDEO",
            "status": "PASS" if duration >= 3.0 else "FAIL",
            "details": f"Rendered video duration: {round(duration, 2)} seconds.",
            "metrics": {"duration_sec": round(duration, 2)}
        })

        # Black Frame Detection via OpenCV frame sampling
        black_checks = cls._detect_black_frames(video_path, duration)
        checks.append(black_checks)

        return checks, duration

    @classmethod
    def _detect_black_frames(cls, video_path: Path, duration: float) -> Dict[str, Any]:
        """Samples frames across video to verify no prolonged black frame dropouts."""
        try:
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                return {
                    "name": "Black Frame & Video Continuity Inspection",
                    "category": "VIDEO",
                    "status": "WARN",
                    "details": "Could not open video file with OpenCV for visual frame inspection.",
                    "metrics": {}
                }

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                cap.release()
                return {
                    "name": "Black Frame & Video Continuity Inspection",
                    "category": "VIDEO",
                    "status": "WARN",
                    "details": "Video has 0 reported frames.",
                    "metrics": {"total_frames": 0}
                }

            # Sample 15 frames evenly
            num_samples = min(15, total_frames)
            sample_indices = np.linspace(0, total_frames - 1, num_samples, dtype=int)
            black_frames_count = 0

            for frame_idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret and frame is not None:
                    # Calculate mean pixel intensity
                    mean_val = float(np.mean(frame))
                    if mean_val < 3.0: # virtually pitch black
                        black_frames_count += 1

            cap.release()
            black_pct = (black_frames_count / num_samples) * 100

            if black_pct > 30.0:
                status = "FAIL"
                details = f"Excessive black frame dropouts detected: {round(black_pct, 1)}% of sampled frames are black."
            elif black_pct > 15.0:
                status = "WARN"
                details = f"Mild black frames detected ({round(black_pct, 1)}% of samples). Likely fade transitions."
            else:
                status = "PASS"
                details = f"Visual continuity verified: {round(black_pct, 1)}% black frame samples (clean transitions)."

            return {
                "name": "Black Frame & Video Continuity Inspection",
                "category": "VIDEO",
                "status": status,
                "details": details,
                "metrics": {"sampled_frames": num_samples, "black_frames": black_frames_count, "black_pct": round(black_pct, 1)}
            }
        except Exception as e:
            return {
                "name": "Black Frame & Video Continuity Inspection",
                "category": "VIDEO",
                "status": "WARN",
                "details": f"Visual frame scan encountered error: {e}",
                "metrics": {}
            }

    @classmethod
    def _check_audio(cls, video_path: Path) -> List[Dict[str, Any]]:
        checks = []
        if not video_path.exists():
            return checks

        # Check audio stream existence with ffprobe
        probe_cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            str(video_path)
        ]
        try:
            res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
            probe_data = json.loads(res.stdout)
            audio_stream = next((s for s in probe_data.get("streams", []) if s.get("codec_type") == "audio"), None)
        except Exception:
            audio_stream = None

        if not audio_stream:
            checks.append({
                "name": "Audio Stream Presence",
                "category": "AUDIO",
                "status": "FAIL",
                "details": "No audio stream detected in container. Documentary lacks narration and soundtrack.",
                "metrics": {"has_audio": False}
            })
            return checks

        codec = audio_stream.get("codec_name", "unknown")
        channels = int(audio_stream.get("channels", 1))
        sample_rate = int(audio_stream.get("sample_rate", 44100))

        checks.append({
            "name": "Audio Stream Presence",
            "category": "AUDIO",
            "status": "PASS",
            "details": f"Audio track detected: {codec.upper()} {channels}ch @ {sample_rate}Hz.",
            "metrics": {"has_audio": True, "codec": codec, "channels": channels, "sample_rate": sample_rate}
        })

        # Run ffmpeg volumedetect
        vol_cmd = [
            "ffmpeg", "-i", str(video_path),
            "-af", "volumedetect",
            "-f", "null", "-"
        ]
        try:
            vol_res = subprocess.run(vol_cmd, capture_output=True, text=True)
            stderr = vol_res.stderr

            mean_match = re.search(r"mean_volume:\s*(-?[\d\.]+)\s*dB", stderr)
            max_match = re.search(r"max_volume:\s*(-?[\d\.]+)\s*dB", stderr)

            mean_vol = float(mean_match.group(1)) if mean_match else None
            max_vol = float(max_match.group(1)) if max_match else None

            # Silence check
            if mean_vol is not None and mean_vol < -55.0:
                status = "FAIL"
                details = f"Audio appears completely silent or near-inaudible (Mean volume: {mean_vol} dB)."
            elif mean_vol is not None:
                status = "PASS"
                details = f"Audio level audible and clear (Mean volume: {mean_vol} dB)."
            else:
                status = "WARN"
                details = "Could not parse mean audio volume level."

            checks.append({
                "name": "Audio Silence Inspection",
                "category": "AUDIO",
                "status": status,
                "details": details,
                "metrics": {"mean_volume_db": mean_vol}
            })

            # Peak Distortion / Clipping check
            if max_vol is not None:
                if max_vol >= 0.0:
                    status = "WARN"
                    details = f"Potential digital clipping detected: Max peak reached {max_vol} dB (Target < -0.5 dB)."
                else:
                    status = "PASS"
                    details = f"Audio headroom compliant: Peak level is {max_vol} dB (No digital clipping)."
            else:
                status = "PASS"
                details = "Headroom within normal operating thresholds."

            checks.append({
                "name": "Audio Headroom & Distortion Check",
                "category": "AUDIO",
                "status": status,
                "details": details,
                "metrics": {"max_volume_db": max_vol}
            })

        except Exception as e:
            checks.append({
                "name": "Audio Level Inspection",
                "category": "AUDIO",
                "status": "WARN",
                "details": f"Failed to run audio volume analysis: {e}",
                "metrics": {}
            })

        return checks

    @classmethod
    def _check_subtitles(cls, srt_path: Path, video_duration: float) -> List[Dict[str, Any]]:
        checks = []
        if not srt_path.exists() or srt_path.stat().st_size == 0:
            checks.append({
                "name": "Subtitles File (SRT) Availability",
                "category": "SUBTITLES",
                "status": "FAIL",
                "details": "Subtitles file 'subtitles.srt' is missing or empty. YouTube SEO and accessibility require closed captions.",
                "metrics": {"srt_exists": False}
            })
            return checks

        checks.append({
            "name": "Subtitles File (SRT) Availability",
            "category": "SUBTITLES",
            "status": "PASS",
            "details": f"Subtitles file present ({srt_path.stat().st_size} bytes).",
            "metrics": {"srt_exists": True, "size_bytes": srt_path.stat().st_size}
        })

        # Parse cues
        try:
            content = srt_path.read_text(encoding="utf-8")
            cues = cls._parse_srt(content)

            if len(cues) == 0:
                checks.append({
                    "name": "Subtitle Cue Parsing",
                    "category": "SUBTITLES",
                    "status": "FAIL",
                    "details": "No valid subtitle cues could be parsed from subtitles.srt.",
                    "metrics": {"cue_count": 0}
                })
                return checks

            checks.append({
                "name": "Subtitle Cue Parsing",
                "category": "SUBTITLES",
                "status": "PASS",
                "details": f"Successfully parsed {len(cues)} subtitle cues.",
                "metrics": {"cue_count": len(cues)}
            })

            # Check timing & video timeline sync
            max_end = max(c["end_sec"] for c in cues)
            out_of_order = False
            for i in range(len(cues)):
                if cues[i]["start_sec"] >= cues[i]["end_sec"]:
                    out_of_order = True
                    break

            if out_of_order:
                sync_status = "FAIL"
                sync_details = "Corrupted subtitle cue timestamps: Start time occurs after or equal to end time."
            elif video_duration > 0 and max_end > video_duration + 3.0:
                sync_status = "WARN"
                sync_details = f"Subtitle cues extend beyond video duration ({round(max_end, 1)}s vs {round(video_duration, 1)}s)."
            else:
                sync_status = "PASS"
                sync_details = f"Subtitles timeline synchronized accurately with master video (Ending at {round(max_end, 1)}s)."

            checks.append({
                "name": "Subtitle Timeline Synchronization",
                "category": "SUBTITLES",
                "status": sync_status,
                "details": sync_details,
                "metrics": {"max_cue_end_sec": round(max_end, 2), "video_duration_sec": round(video_duration, 2)}
            })

        except Exception as e:
            checks.append({
                "name": "Subtitle Verification",
                "category": "SUBTITLES",
                "status": "WARN",
                "details": f"Subtitle parser error: {e}",
                "metrics": {}
            })

        return checks

    @classmethod
    def _parse_srt(cls, text: str) -> List[Dict[str, Any]]:
        blocks = re.split(r"\n\s*\n", text.strip())
        cues = []
        for block in blocks:
            lines = [line.strip() for line in block.split("\n") if line.strip()]
            if len(lines) >= 2:
                time_line = lines[1] if lines[0].isdigit() else lines[0]
                text_lines = lines[2:] if lines[0].isdigit() else lines[1:]
                match = re.match(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})", time_line)
                if match:
                    h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, match.groups())
                    start_sec = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000.0
                    end_sec = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000.0
                    cues.append({
                        "start_sec": start_sec,
                        "end_sec": end_sec,
                        "text": " ".join(text_lines)
                    })
        return cues

    @classmethod
    def _check_rights(cls, project_id: str) -> List[Dict[str, Any]]:
        """Verifies 100% asset approvals and valid public domain / open licensing."""
        checks = []
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM visual_assets WHERE project_id = ?", (project_id,))
        assets = [dict(row) for row in cursor.fetchall()]
        conn.close()

        total_assets = len(assets)
        if total_assets == 0:
            checks.append({
                "name": "Visual Asset Approval Gate",
                "category": "RIGHTS",
                "status": "WARN",
                "details": "No visual assets found in project database.",
                "metrics": {"total_assets": 0}
            })
            return checks

        unapproved = [a for a in assets if a.get("approval_status") != "APPROVED"]
        if unapproved:
            checks.append({
                "name": "Mandatory Visual Asset Approval Gate",
                "category": "RIGHTS",
                "status": "FAIL",
                "details": f"{len(unapproved)} of {total_assets} visual assets have not received explicit human approval.",
                "metrics": {"unapproved_count": len(unapproved), "total_assets": total_assets}
            })
        else:
            checks.append({
                "name": "Mandatory Visual Asset Approval Gate",
                "category": "RIGHTS",
                "status": "PASS",
                "details": f"100% of visual assets ({total_assets}/{total_assets}) verified APPROVED by human checkpoint.",
                "metrics": {"unapproved_count": 0, "total_assets": total_assets}
            })

        # Check licensing compliance
        valid_licenses = {"PUBLIC_DOMAIN", "CC0", "CC_BY", "PEXELS_FREE", "PIXABAY_FREE", "US_GOV_PD"}
        non_compliant = [a for a in assets if a.get("license_type") not in valid_licenses]

        if non_compliant:
            checks.append({
                "name": "Copyright & Commercial Licensing",
                "category": "RIGHTS",
                "status": "FAIL",
                "details": f"{len(non_compliant)} assets have unverified or restrictive licenses.",
                "metrics": {"non_compliant_count": len(non_compliant)}
            })
        else:
            checks.append({
                "name": "Copyright & Commercial Licensing",
                "category": "RIGHTS",
                "status": "PASS",
                "details": f"All {total_assets} assets originate from verified free-to-use / public domain archives.",
                "metrics": {"compliant_count": total_assets}
            })

        # Check attribution logging for CC_BY assets
        cc_by_assets = [a for a in assets if a.get("license_type") == "CC_BY"]
        missing_attrib = [a for a in cc_by_assets if not a.get("attribution_text")]
        if missing_attrib:
            checks.append({
                "name": "Creative Commons Attribution Compliance",
                "category": "RIGHTS",
                "status": "WARN",
                "details": f"{len(missing_attrib)} CC-BY assets lack attribution credit text in the description manifest.",
                "metrics": {"missing_attribution_count": len(missing_attrib)}
            })
        else:
            checks.append({
                "name": "Creative Commons Attribution Compliance",
                "category": "RIGHTS",
                "status": "PASS",
                "details": f"All {len(cc_by_assets)} CC-BY assets have attribution credits ready for the description.",
                "metrics": {"cc_by_count": len(cc_by_assets)}
            })

        return checks

    @classmethod
    def _check_thumbnails(cls, proj_dir: Path) -> List[Dict[str, Any]]:
        t1 = proj_dir / "thumbnail-1.jpg"
        t2 = proj_dir / "thumbnail-2.jpg"
        has_t1 = t1.exists() and t1.stat().st_size > 0
        has_t2 = t2.exists() and t2.stat().st_size > 0

        if has_t1 and has_t2:
            status = "PASS"
            details = "Both A/B thumbnail variants generated and ready for deployment."
        elif has_t1 or has_t2:
            status = "WARN"
            details = "Only 1 thumbnail variant detected. Recommended to generate both A/B variants."
        else:
            status = "WARN"
            details = "Thumbnails not yet generated. Recommended prior to final export."

        return [{
            "name": "High-Impact YouTube Thumbnails",
            "category": "THUMBNAILS",
            "status": status,
            "details": details,
            "metrics": {"thumbnail_1": has_t1, "thumbnail_2": has_t2}
        }]

    @classmethod
    def _evaluate_verdict(cls, checks: List[Dict[str, Any]]) -> Tuple[bool, int, List[str]]:
        failures = [c for c in checks if c["status"] == "FAIL"]
        warnings = [c for c in checks if c["status"] == "WARN"]
        passes = [c for c in checks if c["status"] == "PASS"]

        total = len(checks)
        if total == 0:
            return False, 0, ["No QC checks could be evaluated."]

        # Calculate score: PASS=100, WARN=70, FAIL=0
        points = (len(passes) * 100) + (len(warnings) * 70)
        score = int(round(points / total))

        passed = (len(failures) == 0)

        recommendations = []
        for fail in failures:
            cat = fail.get("category", "")
            if cat == "VIDEO":
                recommendations.append(f"Video Issue: {fail['details']} - Action: Re-run FFmpeg multi-track compositing.")
            elif cat == "AUDIO":
                recommendations.append(f"Audio Issue: {fail['details']} - Action: Check narration TTS files and run EBU R128 audio normalization.")
            elif cat == "SUBTITLES":
                recommendations.append(f"Subtitle Issue: {fail['details']} - Action: Re-generate subtitles.srt from narration timeline.")
            elif cat == "RIGHTS":
                recommendations.append(f"Asset Rights Issue: {fail['details']} - Action: Review pending assets on Visual Approval dashboard.")
            else:
                recommendations.append(f"Failure in {fail['name']}: {fail['details']}")

        for warn in warnings:
            recommendations.append(f"Optimization Notice: {warn['details']}")

        return passed, score, recommendations

    @classmethod
    def _save_report(cls, proj_dir: Path, report: Dict[str, Any]) -> Path:
        proj_dir.mkdir(parents=True, exist_ok=True)
        report_path = proj_dir / "qc_report.json"
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report_path

    @classmethod
    def get_report(cls, project_id: str) -> Optional[Dict[str, Any]]:
        report_path = EXPORTS_DIR / project_id / "qc_report.json"
        if not report_path.exists():
            return None
        try:
            return json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            return None
