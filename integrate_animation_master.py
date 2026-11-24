import os
import sys
import json
import time
import wave
import shutil
import asyncio
import subprocess
from pathlib import Path

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

PROJ_ID = "swiss-air-grounding-prod"
BASE_DIR = Path(__file__).resolve().parent
EXPORT_DIR = BASE_DIR / "data" / "exports" / PROJ_ID
ANIM_DIR = BASE_DIR / "data" / "media" / "animations" / PROJ_ID
AUDIO_DIR = BASE_DIR / "data" / "media" / "audio" / PROJ_ID
BROLL_DIR = BASE_DIR / "backend" / "data" / "media" / "broll_cache"

EXPORT_DIR.mkdir(parents=True, exist_ok=True)
ANIM_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Load broll bank
with open(BASE_DIR / "backend" / "app" / "agents" / "broll_bank.json", "r", encoding="utf-8") as f:
    BROLL_BANK = json.load(f)

# Load storyboard items
with open(BASE_DIR / "storyboard_items.json", "r", encoding="utf-8") as f:
    STORYBOARD = json.load(f)

# The 10 Dedicated Broadcast Animations mapping to specific beat indices (1-indexed)
ANIMATION_MAPPING = {
    5:  ANIM_DIR / "anim_02_chart.mp4",         # Beat 5: Financial Crash Chart (-85% debt explosion)
    9:  ANIM_DIR / "anim_09_vault.mp4",         # Beat 9: 3D Cinematic Bank Vault (The Flying Bank)
    12: ANIM_DIR / "anim_01_map.mp4",           # Beat 12: Animated Map (European Airspace & Isolation)
    17: ANIM_DIR / "anim_05_parallax.mp4",      # Beat 17: 2.5D Parallax Animation (Philippe Bruggisser)
    23: ANIM_DIR / "anim_07_hunter_wheel.mp4",  # Beat 23: 2D Motion Graphics (The Hunter Strategy Wheel)
    34: ANIM_DIR / "anim_04_document.mp4",      # Beat 34: Document Reconstruction (Confidential Guarantees)
    43: ANIM_DIR / "anim_03_kinetic_type.mp4",  # Beat 43: Kinetic Typography ("OCTOBER 2, 2001 / FLEET GROUNDED")
    47: ANIM_DIR / "anim_08_infographic.mp4",   # Beat 47: Infographic Dashboard (Liquidity 0% & Stock Crash)
    48: ANIM_DIR / "anim_06_hud.mp4",           # Beat 48: HUD / Surveillance Interface (Flight 157 Refused Fuel)
    51: ANIM_DIR / "anim_10_embers.mp4"         # Beat 51: Particle Animation (Glowing Embers & Grounding)
}

def render_anim_clip(src_anim: Path, out_path: Path, dur: float):
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", str(src_anim),
        "-t", str(round(dur, 2)),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-threads", "2",
        str(out_path)
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def main():
    log("=== ASSEMBLING MASTER TIMELINE WITH 10 POPULAR DOCUMENTARY ANIMATIONS ===")
    from backend.app.agents.animation_director import CinematicAnimationDirector
    from backend.app.agents.sound_designer import SoundDesignDirector

    # 1. Cold Open (13.5s hook)
    cold_mp4 = ANIM_DIR / "cold_open.mp4"
    cold_wav = AUDIO_DIR / "cold_open.wav"
    if not (cold_mp4.exists() and cold_mp4.stat().st_size > 50000):
        log("Rendering Cold Open hook sequence...")
        CinematicAnimationDirector.render_cold_open(cold_mp4)
    if not (cold_wav.exists() and cold_wav.stat().st_size > 5000):
        log("Synthesizing Cold Open audio bed...")
        SoundDesignDirector.synthesize_cold_open_audio(cold_wav)

    video_files = [str(cold_mp4)]
    audio_files = [str(cold_wav)]

    # 2. Build 64 Beats
    log("Integrating 10 custom documentary animations and unique B-roll clips...")
    for idx, it in enumerate(STORYBOARD, 1):
        dur = min(float(it.get("duration_sec", 4.0)), 5.5)
        clip_path = ANIM_DIR / f"clip_{idx}.mp4"
        audio_path = AUDIO_DIR / f"beat_{idx}.wav"

        # Check if this beat is one of the 10 dedicated animations
        if idx in ANIMATION_MAPPING:
            anim_src = ANIMATION_MAPPING[idx]
            log(f"  [Beat {idx:02d}] -> Applying Animation: {anim_src.name}")
            render_anim_clip(anim_src, clip_path, dur)
        else:
            # Check if clip exists or render with unique B-roll
            if not (clip_path.exists() and clip_path.stat().st_size > 20000):
                bank_item = BROLL_BANK[(idx - 1) % len(BROLL_BANK)]
                broll_file = BROLL_DIR / f"broll_{bank_item['id']}.mp4"
                if not broll_file.exists():
                    broll_file = BROLL_DIR / "AIRPORT_TARMAC.mp4"
                from assemble_unique_master import render_broll_clip
                chyron_title = f"SCENE {it['scene_number']} · INVESTIGATION"
                chyron_sub = it.get("visual_summary", "Archival Evidence Record")[:60]
                render_broll_clip(broll_file, clip_path, dur, chyron_title, chyron_sub)

        video_files.append(str(clip_path))
        audio_files.append(str(audio_path))

    log("All 64 timeline segments prepared!")

    # 3. Concatenate video stream
    log("Concatenating 1080p video stream...")
    video_concat_txt = EXPORT_DIR / "video_concat.txt"
    with open(video_concat_txt, "w", encoding="utf-8") as vf:
        for vf_path in video_files:
            vf.write(f"file '{str(vf_path).replace(os.sep, '/')}'\n")

    raw_video_mp4 = EXPORT_DIR / "raw_video.mp4"
    cmd_v = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(video_concat_txt), "-c:v", "copy", "-threads", "2", str(raw_video_mp4)]
    subprocess.run(cmd_v, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # 4. Concatenate audio stream
    log("Concatenating narration audio tracks...")
    audio_concat_txt = EXPORT_DIR / "audio_concat.txt"
    with open(audio_concat_txt, "w", encoding="utf-8") as af:
        for af_path in audio_files:
            af.write(f"file '{str(af_path).replace(os.sep, '/')}'\n")

    raw_audio_wav = EXPORT_DIR / "raw_audio.wav"
    cmd_a = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(audio_concat_txt), "-c:a", "copy", "-threads", "2", str(raw_audio_wav)]
    subprocess.run(cmd_a, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # 5. Score tension soundtrack & mix
    log("Scoring continuous tension soundtrack...")
    total_sec = 60.0
    with wave.open(str(raw_audio_wav), "rb") as wf:
        total_sec = round(wf.getnframes() / float(wf.getframerate()), 2)

    soundtrack_wav = EXPORT_DIR / "soundtrack.wav"
    mixed_audio_wav = EXPORT_DIR / "mixed_audio.wav"
    SoundDesignDirector.synthesize_cinematic_soundtrack(total_sec, soundtrack_wav)
    SoundDesignDirector.mix_documentary_audio(raw_audio_wav, soundtrack_wav, mixed_audio_wav)

    # 6. Final Multiplex to Master (Constant 24 FPS, Web Faststart, < 35MB)
    final_mp4 = EXPORT_DIR / "documentary.mp4"
    log("Encoding broadcast master (constant 24 fps, yuv420p, +faststart)...")
    cmd_final = [
        "ffmpeg", "-y",
        "-i", str(raw_video_mp4),
        "-i", str(mixed_audio_wav),
        "-vf", "fps=24",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-movflags", "+faststart",
        "-threads", "4",
        "-shortest",
        str(final_mp4)
    ]
    subprocess.run(cmd_final, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Clean intermediate raw files
    raw_video_mp4.unlink(missing_ok=True)
    raw_audio_wav.unlink(missing_ok=True)
    soundtrack_wav.unlink(missing_ok=True)
    mixed_audio_wav.unlink(missing_ok=True)
    video_concat_txt.unlink(missing_ok=True)
    audio_concat_txt.unlink(missing_ok=True)

    log(f"FINAL DOCUMENTARY RENDERED! Size: {final_mp4.stat().st_size / (1024*1024):.2f} MB")

    # 7. Subtitles
    srt_path = EXPORT_DIR / "subtitles.srt"
    from backend.app.agents.editing_director import CinematicEditingDirector
    CinematicEditingDirector.generate_srt_subtitles(PROJ_ID, srt_path)
    log(f"Subtitles generated! Size: {srt_path.stat().st_size} bytes")

    # 8. Package ZIP
    zip_path = EXPORT_DIR / "docuforge_package.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(str(final_mp4), "documentary.mp4")
        zf.write(str(srt_path), "subtitles.srt")
        for thumb in sorted(EXPORT_DIR.glob("*.jpg")):
            zf.write(str(thumb), thumb.name)

    log(f"Release package assembled! Size: {zip_path.stat().st_size / (1024*1024):.2f} MB")
    log("=== MASTER RELEASE WITH 10 ANIMATIONS COMPLETE! ===")

if __name__ == "__main__":
    import zipfile
    main()
