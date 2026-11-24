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
        Generates broadcast-compliant .srt subtitle file from the project's storyboard items.
        """
        items = StoryboardEngine.get_storyboard(project_id)
        srt_lines = []

        def fmt_time(sec: float) -> str:
            hrs = int(sec // 3600)
            mins = int((sec % 3600) // 60)
            secs = int(sec % 60)
            millis = int(round((sec - int(sec)) * 1000))
            return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

        curr_time = 0.0
        for idx, it in enumerate(items, 1):
            start_str = fmt_time(curr_time)
            end_time = curr_time + it["duration_sec"]
            end_str = fmt_time(end_time)
            text = it["narration_text"].strip()

            srt_lines.append(str(idx))
            srt_lines.append(f"{start_str} --> {end_str}")
            srt_lines.append(text)
            srt_lines.append("")  # Blank separator

            curr_time = end_time

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

        # 2. Prepare Video Concat List
        report(30, "Checking and compiling video stream assets...")
        video_concat_txt = proj_export_dir / "video_concat.txt"
        audio_concat_txt = proj_export_dir / "audio_concat.txt"

        video_lines = []
        audio_lines = []

        import gc
        for it in items:
            idx = it["order_index"]
            clip_path = proj_anim_dir / f"clip_{idx}.mp4"
            audio_path = proj_audio_dir / f"beat_{idx}.wav"

            # Fallback if clip wasn't rendered yet
            if not clip_path.exists():
                from .animation_director import CinematicAnimationDirector
                CinematicAnimationDirector.render_photo_ken_burns(None, clip_path, duration_sec=it["duration_sec"])

            if not audio_path.exists():
                from .sound_designer import SoundDesignDirector
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
        report(50, "Concatenating 1080p video stream (zero-copy)...")
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

        # 4. Concatenate audio stream
        report(65, "Concatenating narration audio tracks...")
        raw_audio_wav = proj_export_dir / "raw_audio.wav"
        cmd_a = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(audio_concat_txt),
            "-c:a", "copy",
            "-threads", "1",
            str(raw_audio_wav)
        ]
        subprocess.run(cmd_a, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # 5. Multiplex Final 1080p Documentary (Zero video re-encoding, low memory footprint)
        report(80, "Multiplexing final 1080p documentary (copy video + aac audio)...")
        cmd_final = [
            "ffmpeg", "-y",
            "-i", str(raw_video_mp4),
            "-i", str(raw_audio_wav),
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-threads", "1",
            "-shortest",
            str(final_mp4)
        ]
        subprocess.run(cmd_final, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Clean up temporary concats
        raw_video_mp4.unlink(missing_ok=True)
        raw_audio_wav.unlink(missing_ok=True)
        video_concat_txt.unlink(missing_ok=True)
        audio_concat_txt.unlink(missing_ok=True)
        
        import gc
        gc.collect()

        report(100, "Documentary rendered successfully!")
        return str(final_mp4)
