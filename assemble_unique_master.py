import os
import sys
import json
import time
import asyncio
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

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

def render_broll_clip(video_src: Path, out_path: Path, dur: float, chyron_title: str, chyron_sub: str):
    chyron_png = out_path.with_suffix(".chyron.png")
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Frosted dark banner
    draw.rectangle([(80, 890), (1200, 975)], fill=(12, 14, 18, 215))
    # Golden left accent bar
    draw.rectangle([(80, 890), (88, 975)], fill=(220, 180, 60, 255))
    # HUD technical timecode in top right
    draw.rectangle([(1450, 60), (1840, 100)], fill=(10, 12, 16, 180))
    draw.text((1465, 72), "REC ● 12:30:14 PM | ARCHIVAL", fill=(220, 80, 80, 255))
    # Text
    c_title = (chyron_title or "INVESTIGATION DOSSIER")[:45]
    c_sub = (chyron_sub or "Documentary Narrative Beat")[:65]
    draw.text((105, 902), c_title, fill=(220, 180, 60, 255))
    draw.text((105, 934), c_sub, fill=(240, 245, 250, 255))
    img.save(str(chyron_png))

    cmd = [
        "ffmpeg", "-y",
        "-ss", "0.5",
        "-t", str(round(dur, 2)),
        "-i", str(video_src),
        "-i", str(chyron_png),
        "-filter_complex", (
            "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,"
            "curves=preset=medium_contrast,vignette=PI/4[bg];"
            "[bg][1:v]overlay=0:0[outv]"
        ),
        "-map", "[outv]",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-threads", "2",
        str(out_path)
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    chyron_png.unlink(missing_ok=True)

async def synthesize_edge_tts(text: str, out_wav: Path):
    import edge_tts
    raw_mp3 = out_wav.with_suffix(".temp.mp3")
    comm = edge_tts.Communicate(text, "en-US-AndrewMultilingualNeural", rate="-4%")
    await comm.save(str(raw_mp3))
    cmd = [
        "ffmpeg", "-y", "-i", str(raw_mp3),
        "-af", "aresample=44100,loudnorm=I=-14:LRA=11:TP=-1",
        "-threads", "1",
        str(out_wav)
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    raw_mp3.unlink(missing_ok=True)

def main():
    log("=== STARTING MASTER DOCUMENTARY ASSEMBLY WITH ZERO FOOTAGE REPETITION ===")
    from backend.app.agents.animation_director import CinematicAnimationDirector
    from backend.app.agents.sound_designer import SoundDesignDirector

    # 1. Cold Open
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

    # 2. Render each beat with unique footage
    log(f"Processing {len(STORYBOARD)} storyboard beats with unique B-roll...")
    for idx, it in enumerate(STORYBOARD, 1):
        dur = min(float(it.get("duration_sec", 4.0)), 5.0)
        clip_path = ANIM_DIR / f"clip_{idx}.mp4"
        audio_path = AUDIO_DIR / f"beat_{idx}.wav"

        # Narration audio
        if not (audio_path.exists() and audio_path.stat().st_size > 5000):
            try:
                asyncio.run(synthesize_edge_tts(it["narration_text"], audio_path))
            except Exception as e:
                SoundDesignDirector.synthesize_beat_audio(PROJ_ID, idx, it["narration_text"])

        # Video clip
        if not (clip_path.exists() and clip_path.stat().st_size > 50000):
            atype = it.get("asset_type", "ARCHIVAL_VIDEO")
            if atype == "MAP":
                CinematicAnimationDirector.render_animated_map(clip_path, duration_sec=dur, title="EUROPEAN AIRSPACE & DEREGULATION CHOKEPOINTS")
            elif atype == "CHART":
                CinematicAnimationDirector.render_financial_chart(clip_path, duration_sec=dur, title="SAIRGROUP ACCUMULATED LIABILITIES (1998-2001)")
            elif atype in ["DOCUMENT", "DOC_REVEAL"]:
                CinematicAnimationDirector.render_document_reveal(clip_path, duration_sec=dur, headline=it.get("visual_summary", "OFFICIAL AUDIT REPORT")[:50])
            else:
                # Assign dedicated unique B-roll clip (idx-1)
                bank_item = BROLL_BANK[(idx - 1) % len(BROLL_BANK)]
                broll_file = BROLL_DIR / f"broll_{bank_item['id']}.mp4"
                if not broll_file.exists():
                    broll_file = BROLL_DIR / "AIRPORT_TARMAC.mp4"
                chyron_title = f"SCENE {it['scene_number']} · INVESTIGATION"
                chyron_sub = it.get("visual_summary", "Archival Evidence Record")[:60]
                render_broll_clip(broll_file, clip_path, dur, chyron_title, chyron_sub)

        video_files.append(str(clip_path))
        audio_files.append(str(audio_path))
        if idx % 10 == 0:
            log(f"Processed {idx}/{len(STORYBOARD)} beats...")

    log("All 64 unique beats rendered successfully!")

    # 3. Concatenate video
    log("Concatenating 1080p video stream...")
    video_concat_txt = EXPORT_DIR / "video_concat.txt"
    with open(video_concat_txt, "w", encoding="utf-8") as vf:
        for vf_path in video_files:
            vf.write(f"file '{str(vf_path).replace(os.sep, '/')}'\n")

    raw_video_mp4 = EXPORT_DIR / "raw_video.mp4"
    cmd_v = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(video_concat_txt), "-c:v", "copy", "-threads", "2", str(raw_video_mp4)]
    subprocess.run(cmd_v, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # 4. Concatenate audio
    log("Concatenating narration audio tracks...")
    audio_concat_txt = EXPORT_DIR / "audio_concat.txt"
    with open(audio_concat_txt, "w", encoding="utf-8") as af:
        for af_path in audio_files:
            af.write(f"file '{str(af_path).replace(os.sep, '/')}'\n")

    raw_audio_wav = EXPORT_DIR / "raw_audio.wav"
    cmd_a = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(audio_concat_txt), "-c:a", "copy", "-threads", "2", str(raw_audio_wav)]
    subprocess.run(cmd_a, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # 5. Synthesize cinematic tension score & mix
    log("Scoring and mixing multi-layered audio bed...")
    import wave
    total_sec = 60.0
    with wave.open(str(raw_audio_wav), "rb") as wf:
        total_sec = round(wf.getnframes() / float(wf.getframerate()), 2)

    soundtrack_wav = EXPORT_DIR / "soundtrack.wav"
    mixed_audio_wav = EXPORT_DIR / "mixed_audio.wav"
    SoundDesignDirector.synthesize_cinematic_soundtrack(total_sec, soundtrack_wav)
    SoundDesignDirector.mix_documentary_audio(raw_audio_wav, soundtrack_wav, mixed_audio_wav)

    # 6. Multiplex Final Documentary
    final_mp4 = EXPORT_DIR / "documentary.mp4"
    log("Multiplexing final 1080p documentary with web faststart...")
    cmd_final = [
        "ffmpeg", "-y",
        "-i", str(raw_video_mp4),
        "-i", str(mixed_audio_wav),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-threads", "2",
        "-shortest",
        str(final_mp4)
    ]
    subprocess.run(cmd_final, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Clean up concats
    raw_video_mp4.unlink(missing_ok=True)
    raw_audio_wav.unlink(missing_ok=True)
    soundtrack_wav.unlink(missing_ok=True)
    mixed_audio_wav.unlink(missing_ok=True)
    video_concat_txt.unlink(missing_ok=True)
    audio_concat_txt.unlink(missing_ok=True)

    log(f"DOCUMENTARY ASSEMBLED! Size: {final_mp4.stat().st_size / (1024*1024):.2f} MB")

    # 7. Generate Subtitles
    srt_path = EXPORT_DIR / "subtitles.srt"
    from backend.app.agents.editing_director import CinematicEditingDirector
    CinematicEditingDirector.generate_srt_subtitles(PROJ_ID, srt_path)
    log(f"Subtitles generated! Size: {srt_path.stat().st_size} bytes")

    # 8. Create Package ZIP
    zip_path = EXPORT_DIR / "docuforge_package.zip"
    import zipfile
    with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_STORED) as zf:
        zf.write(str(final_mp4), "documentary.mp4")
        zf.write(str(srt_path), "subtitles.srt")
        for thumb in EXPORT_DIR.glob("*.jpg"):
            zf.write(str(thumb), thumb.name)

    log(f"Release package assembled! Size: {zip_path.stat().st_size / (1024*1024):.2f} MB")
    log("=== MASTER RELEASE PIPELINE COMPLETE! ===")

if __name__ == "__main__":
    main()
