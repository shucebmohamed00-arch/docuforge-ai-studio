"""
DocuForge AI - Agent 11: Cinematic Editing Director
Assembles the complete documentary: concatenates 1080p clips, mixes multi-track audio,
generates synchronized subtitles (.srt), and renders the final documentary.mp4 using FFmpeg.
"""
import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from ..database import get_connection
from ..config import MEDIA_DIR, EXPORTS_DIR
from ..core.budget_engine import BudgetEngine
from ..core.job_runner import JobRunner
from .storyboard import StoryboardEngine
from .editing_passes import ProfessionalEditingReviewEngine

logger = logging.getLogger("docuforge.agents.editing_director")

class CinematicEditingDirector:
    @classmethod
    def generate_srt_subtitles(cls, project_id: str, output_path: Path) -> str:
        """
        Generates broadcast-compliant .srt subtitle file from the project's storyboard items,
        prefixed with Cold Open introductory subtitles.
        """
        items = StoryboardEngine.get_storyboard(project_id)
        srt_lines = []

        def fmt_time(sec: float) -> str:
            hrs = int(sec // 3600)
            mins = int((sec % 3600) // 60)
            secs = int(sec % 60)
            millis = int(round((sec - int(sec)) * 1000))
            return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

        # 0. Cold Open Hook Subtitles (0.0s to 13.5s)
        cold_captions = [
            (0.5, 3.0, "ZURICH AIRPORT — OCTOBER 2, 2001. 12:30 PM."),
            (3.2, 6.0, "FLIGHT SR 356 TO NEW YORK: GROUND REFUSAL."),
            (6.2, 9.5, "OVER 19,000 PASSENGERS STRANDED WORLDWIDE."),
            (9.8, 13.5, "THE SWISS AIR GROUNDING: HOW ARROGANCE DESTROYED THE BANK OF THE SKIES.")
        ]
        s_idx = 1
        for start_s, end_s, text in cold_captions:
            srt_lines.append(str(s_idx))
            srt_lines.append(f"{fmt_time(start_s)} --> {fmt_time(end_s)}")
            srt_lines.append(text)
            srt_lines.append("")
            s_idx += 1

        curr_time = 13.5
        for it in items:
            start_str = fmt_time(curr_time)
            end_time = curr_time + it["duration_sec"]
            end_str = fmt_time(end_time)
            text = it["narration_text"].strip()

            srt_lines.append(str(s_idx))
            srt_lines.append(f"{start_str} --> {end_str}")
            srt_lines.append(text)
            srt_lines.append("")  # Blank separator

            curr_time = end_time
            s_idx += 1

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as sf:
            sf.write("\n".join(srt_lines))

        return str(output_path)

    @classmethod
    def assemble_documentary(
        cls,
        project_id: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> str:
        """
        Assembles and renders the complete 1080p documentary.
        1. Compiles video clips concat list
        2. Compiles audio tracks concat list
        3. Generates subtitles (.srt)
        4. FFmpeg compositing with H.264/AAC at 1080p
        5. Saves to data/exports/{project_id}/documentary.mp4
        """
        def report(pct: int, msg: str):
            if progress_callback:
                progress_callback(pct, msg)
            logger.info("Render progress: %d%% - %s", pct, msg)

        report(5, "Initializing documentary assembly engine...")

        # Record $0 local rendering in budget
        BudgetEngine.record_cost(
            agent_name="CINEMATIC_EDITING_DIRECTOR",
            operation="LOCAL_FFMPEG_TIMELINE_ASSEMBLY",
            model_or_service="FFMPEG_MULTI_TRACK_COMPOSITOR",
            cost_usd=0.00,
            project_id=project_id,
            tokens_in=0,
            tokens_out=0,
            notes="1080p multi-track timeline assembly ($0.00 local software)"
        )

        proj_export_dir = EXPORTS_DIR / project_id
        proj_export_dir.mkdir(parents=True, exist_ok=True)
        final_mp4 = proj_export_dir / "documentary.mp4"
        srt_file = proj_export_dir / "subtitles.srt"

        # 0. Mandatory 6-Pass Professional Creative Editorial Review (Directive 27)
        existing_passes = ProfessionalEditingReviewEngine.get_passes(project_id)
        if len(existing_passes) < 6:
            report(10, "Executing 6-Pass Professional Creative Editorial Review (Narrative, Visual, Motion, Sound, Polish, QC)...")
            ProfessionalEditingReviewEngine.run_all_passes(project_id)

        # 1. Generate Subtitles
        report(18, "Generating synchronized broadcast subtitles (.srt)...")
        cls.generate_srt_subtitles(project_id, srt_file)

        items = StoryboardEngine.get_storyboard(project_id)
        if not items:
            StoryboardEngine.compile_storyboard(project_id)
            items = StoryboardEngine.get_storyboard(project_id)
        if not items:
            raise ValueError(f"No storyboard items found for project '{project_id}'.")

        proj_anim_dir = MEDIA_DIR / "animations" / project_id
        proj_audio_dir = MEDIA_DIR / "audio" / project_id
        proj_anim_dir.mkdir(parents=True, exist_ok=True)
        proj_audio_dir.mkdir(parents=True, exist_ok=True)

        # 2. Prepare Video Concat List & Visual Assets
        report(30, "Checking and compiling video stream assets...")
        video_concat_txt = proj_export_dir / "video_concat.txt"
        audio_concat_txt = proj_export_dir / "audio_concat.txt"

        # Pre-cache visual assets for image-backed beats
        from .footage_discovery import RealFootageDiscoveryAgent
        import httpx
        assets = RealFootageDiscoveryAgent.get_project_assets(project_id)
        asset_map = {a["id"]: a for a in assets}
        asset_cache_dir = MEDIA_DIR / "assets" / project_id
        asset_cache_dir.mkdir(parents=True, exist_ok=True)

        def _get_asset_image_file(asset_id: Optional[str]) -> Optional[str]:
            if not asset_id or asset_id not in asset_map:
                return None
            a = asset_map[asset_id]
            local_fp = a.get("local_file_path")
            if local_fp and os.path.exists(local_fp) and os.path.getsize(local_fp) > 1000:
                return local_fp
            p_url = a.get("preview_url")
            if not p_url:
                return None
            dest = asset_cache_dir / f"{asset_id}.jpg"
            if dest.exists() and dest.stat().st_size > 1000:
                return str(dest)
            try:
                with httpx.Client(timeout=8.0) as client:
                    resp = client.get(p_url, headers={"User-Agent": "Mozilla/5.0"})
                    if resp.status_code == 200 and len(resp.content) > 1000:
                        dest.write_bytes(resp.content)
                        return str(dest)
            except Exception as e:
                logger.warning("Could not download asset preview image %s: %s", p_url, e)
            return None

        from .animation_director import CinematicAnimationDirector
        from .sound_designer import SoundDesignDirector

        video_lines = []
        audio_lines = []

        # 1. Cold Open Sequence (Beat 0: 13.5s dramatic hook)
        report(32, "Rendering cinematic Cold Open hook sequence...")
        cold_open_mp4 = proj_anim_dir / "cold_open.mp4"
        cold_open_wav = proj_audio_dir / "cold_open.wav"
        if not (cold_open_mp4.exists() and cold_open_mp4.stat().st_size > 50000):
            CinematicAnimationDirector.render_cold_open(cold_open_mp4)
        if not (cold_open_wav.exists() and cold_open_wav.stat().st_size > 5000):
            SoundDesignDirector.synthesize_cold_open_audio(cold_open_wav)

        video_lines.append(f"file '{str(cold_open_mp4).replace(os.sep, '/')}'")
        audio_lines.append(f"file '{str(cold_open_wav).replace(os.sep, '/')}'")

        import gc
        for it in items:
            idx = it["order_index"]
            clip_path = proj_anim_dir / f"clip_{idx}.mp4"
            audio_path = proj_audio_dir / f"beat_{idx}.wav"

            # Render clip if missing or legacy small photo slate (< 50KB)
            if not (clip_path.exists() and clip_path.stat().st_size > 50000):
                asset_type = it.get("asset_type", "ARCHIVAL_VIDEO")
                dur = min(float(it.get("duration_sec", 4.0)), 6.0)

                if asset_type == "MAP":
                    CinematicAnimationDirector.render_animated_map(clip_path, duration_sec=dur, title="EUROPEAN AIRSPACE & DEREGULATION CHOKEPOINTS")
                elif asset_type == "CHART":
                    CinematicAnimationDirector.render_financial_chart(clip_path, duration_sec=dur, title="SAIRGROUP ACCUMULATED LIABILITIES (1998-2001)")
                elif asset_type in ["DOCUMENT", "DOC_REVEAL"]:
                    CinematicAnimationDirector.render_document_reveal(clip_path, duration_sec=dur, headline=it.get("visual_summary", "OFFICIAL AUDIT REPORT")[:50])
                else:
                    # Dynamic motion B-roll video clip with chyron
                    cat = CinematicAnimationDirector.determine_broll_category(it.get("visual_summary", "") + " " + it.get("narration_text", ""))
                    offset_sec = (idx * 3.2) % 15.0
                    chyron_title = f"SCENE {it['scene_number']} · INVESTIGATION"
                    chyron_sub = it.get("visual_summary", "Documentary Archival Record")[:60]
                    CinematicAnimationDirector.render_broll_clip(
                        category=cat,
                        output_path=clip_path,
                        duration_sec=dur,
                        offset_sec=offset_sec,
                        chyron_title=chyron_title,
                        chyron_sub=chyron_sub
                    )

            if not audio_path.exists():
                SoundDesignDirector.synthesize_beat_audio(project_id, idx, it["narration_text"])

            # Use forward slashes for FFmpeg concat files on Windows / Linux
            video_lines.append(f"file '{str(clip_path).replace(os.sep, '/')}'")
            audio_lines.append(f"file '{str(audio_path).replace(os.sep, '/')}'")

            if idx % 10 == 0:
                gc.collect()

        with open(video_concat_txt, "w", encoding="utf-8") as vf:
            vf.write("\n".join(video_lines))
        with open(audio_concat_txt, "w", encoding="utf-8") as af:
            af.write("\n".join(audio_lines))

        # 3. Concatenate video stream (zero-copy, memory-efficient)
        report(55, "Concatenating 1080p video stream (zero-copy)...")
        raw_video_mp4 = proj_export_dir / "raw_video.mp4"
        cmd_v = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(video_concat_txt),
            "-c:v", "copy",
            "-threads", "1",
            str(raw_video_mp4)
        ]
        subprocess.run(cmd_v, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # 4. Concatenate narration audio stream
        report(68, "Concatenating narration audio tracks...")
        raw_narration_wav = proj_export_dir / "raw_narration.wav"
        cmd_a = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(audio_concat_txt),
            "-c:a", "copy",
            "-threads", "1",
            str(raw_narration_wav)
        ]
        subprocess.run(cmd_a, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # 5. Synthesize continuous cinematic tension soundtrack and mix
        report(78, "Scoring and mixing cinematic audio bed with broadcast loudness normalization...")
        # Get duration of narration track
        total_audio_sec = 60.0
        try:
            import wave
            with wave.open(str(raw_narration_wav), "rb") as wf:
                total_audio_sec = round(wf.getnframes() / float(wf.getframerate()), 2)
        except Exception:
            pass

        soundtrack_wav = proj_export_dir / "soundtrack.wav"
        mixed_audio_wav = proj_export_dir / "mixed_audio.wav"
        SoundDesignDirector.synthesize_cinematic_soundtrack(total_audio_sec, soundtrack_wav)
        SoundDesignDirector.mix_documentary_audio(raw_narration_wav, soundtrack_wav, mixed_audio_wav)

        # 6. Multiplex Final 1080p Documentary (Zero video re-encoding, low memory footprint, web-optimized faststart)
        report(88, "Multiplexing final 1080p documentary (copy video + aac mixed audio + faststart)...")
        cmd_final = [
            "ffmpeg", "-y",
            "-i", str(raw_video_mp4),
            "-i", str(mixed_audio_wav),
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            "-threads", "1",
            "-shortest",
            str(final_mp4)
        ]
        subprocess.run(cmd_final, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Clean up temporary concats
        raw_video_mp4.unlink(missing_ok=True)
        raw_narration_wav.unlink(missing_ok=True)
        soundtrack_wav.unlink(missing_ok=True)
        mixed_audio_wav.unlink(missing_ok=True)
        video_concat_txt.unlink(missing_ok=True)
        audio_concat_txt.unlink(missing_ok=True)
        
        import gc
        gc.collect()

        report(100, "Documentary rendered successfully!")
        return str(final_mp4)
