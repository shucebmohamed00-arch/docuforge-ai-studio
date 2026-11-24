import os
import sys
import json
import time
import wave
import shutil
import zipfile
import subprocess
import numpy as np
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

with open(BASE_DIR / "backend" / "app" / "agents" / "broll_bank.json", "r", encoding="utf-8") as f:
    BROLL_BANK = json.load(f)

with open(BASE_DIR / "storyboard_items.json", "r", encoding="utf-8") as f:
    STORYBOARD = json.load(f)

ANIMATION_MAPPING = {
    5:  ANIM_DIR / "anim_02_chart.mp4",         # Beat 5: Financial Crash Chart
    9:  ANIM_DIR / "anim_09_vault.mp4",         # Beat 9: 3D Bank Vault
    12: ANIM_DIR / "anim_01_map.mp4",           # Beat 12: Animated Map
    17: ANIM_DIR / "anim_05_parallax.mp4",      # Beat 17: 2.5D Parallax Animation
    23: ANIM_DIR / "anim_07_hunter_wheel.mp4",  # Beat 23: 2D Motion Graphics (Hunter Strategy)
    34: ANIM_DIR / "anim_04_document.mp4",      # Beat 34: Document Reconstruction
    43: ANIM_DIR / "anim_03_kinetic_type.mp4",  # Beat 43: Kinetic Typography ("GROUNDED")
    47: ANIM_DIR / "anim_08_infographic.mp4",   # Beat 47: Infographic Dashboard
    48: ANIM_DIR / "anim_06_hud.mp4",           # Beat 48: HUD Surveillance Interface
    51: ANIM_DIR / "anim_10_embers.mp4"         # Beat 51: Particle Embers Animation
}

MAJOR_TRANSITIONS = {
    1:  "dip_black",    # Scene 1 opening
    12: "dip_black",    # Act 2: European Deregulation & Map
    23: "flash_white",  # Act 3: Aggressive Hunter Acquisitions
    34: "dip_black",    # Act 4: Audit Discoveries
    43: "flash_red",    # Act 5: Climax Grounding Trap
    51: "dip_black"     # Act 6: Aftermath & Collapse
}

def get_audio_duration(wav_path: Path) -> float:
    with wave.open(str(wav_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())

def render_clip_with_transition(src_video: Path, out_path: Path, dur: float, transition_type: str = "crossfade", chyron_title: str = None, chyron_sub: str = None):
    # Cinematic Transition Envelopes
    d_in = 0.35
    d_out = 0.35
    st_out = max(0.1, dur - d_out)

    if transition_type == "dip_black":
        fade_str = f"fade=t=in:st=0:d={d_in}:color=black,fade=t=out:st={st_out}:d={d_out}:color=black"
    elif transition_type == "flash_white":
        fade_str = f"fade=t=in:st=0:d=0.25:color=white,fade=t=out:st={st_out}:d=0.25:color=black"
    elif transition_type == "flash_red":
        fade_str = f"fade=t=in:st=0:d=0.25:color=0x991111,fade=t=out:st={st_out}:d=0.25:color=black"
    else:
        # Standard smooth cinema dissolve
        fade_str = f"fade=t=in:st=0:d={d_in},fade=t=out:st={st_out}:d={d_out}"

    filter_str = f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,eq=contrast=1.10:brightness=-0.02,{fade_str}"

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", str(src_video),
        "-t", str(round(dur, 2)),
        "-vf", filter_str,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-threads", "4",
        str(out_path)
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def compose_cinematic_music_score(total_sec: float, out_wav: Path):
    SR = 44100
    total_samples = int(total_sec * SR)
    t = np.linspace(0, total_sec, total_samples, endpoint=False)

    log(f"Composing {total_sec:.1f}s multi-instrument cinematic tension score...")

    # 1. Deep Sub-bass & Drone
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.12 * t)
    sub = (0.32 * np.sin(2 * np.pi * 32.7 * t) + 0.20 * np.sin(2 * np.pi * 65.4 * t)) * (0.65 + 0.35 * lfo)

    # 2. Vectorized String Chord Progression (C min -> Ab maj -> F min -> G sus)
    pos = t % 16.0
    chord_idx = (pos // 4.0).astype(int) % 4
    roots = np.array([130.81, 103.83, 87.31, 98.00])[chord_idx]
    thirds = np.array([155.56, 130.81, 130.81, 146.83])[chord_idx]
    fifths = np.array([196.00, 155.56, 207.65, 196.00])[chord_idx]

    phase_root = np.cumsum(2 * np.pi * roots / SR)
    phase_third = np.cumsum(2 * np.pi * thirds / SR)
    phase_fifth = np.cumsum(2 * np.pi * fifths / SR)

    env = np.sin((pos % 4.0) / 4.0 * np.pi)
    strings = (
        np.sin(phase_root) + 0.55 * np.sin(2 * phase_root) + 0.25 * np.sin(3 * phase_root) +
        np.sin(phase_third) + 0.50 * np.sin(2 * phase_third) +
        np.sin(phase_fifth) + 0.50 * np.sin(2 * phase_fifth)
    ) * env * 0.16

    # 3. Ticking Ostinato (120 BPM clock pulse)
    tick_pos = t % 0.5
    tick_env = np.exp(-tick_pos * 40.0)
    tick = np.sin(2 * np.pi * 1800.0 * t) * tick_env * 0.08

    # 4. Cinematic Heartbeat / Sub Kick (1.0s interval)
    kick_pos = t % 1.0
    kick_env = np.exp(-kick_pos * 14.0)
    kick = np.sin(2 * np.pi * (65.0 - 25.0 * kick_pos) * t) * kick_env * 0.24

    # 5. Tension Risers & Swells (every 32s)
    riser_pos = t % 32.0
    riser_env = np.where(riser_pos > 26.0, (riser_pos - 26.0) / 6.0, 0.0)
    noise = np.random.uniform(-1, 1, total_samples).astype(np.float32)
    riser = noise * (riser_env ** 2) * 0.07

    mix = sub + strings + tick + kick + riser

    # Master Fade In / Out
    fade_in = int(3.0 * SR)
    fade_out = int(4.0 * SR)
    mix[:fade_in] *= np.linspace(0, 1, fade_in)
    mix[-fade_out:] *= np.linspace(1, 0, fade_out)

    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = (mix / peak) * 0.82

    int_data = (mix * 32767).astype(np.int16)
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(int_data.tobytes())

    log(f"Soundtrack composition ready! ({total_sec:.2f}s, {out_wav.stat().st_size / (1024*1024):.2f} MB)")

def main():
    log("=== COMMENCING CINEMATIC MASTERPIECE ASSEMBLY ===")
    from backend.app.agents.animation_director import CinematicAnimationDirector

    # 1. Cold Open (13.5s hook)
    cold_mp4 = ANIM_DIR / "cold_open.mp4"
    cold_wav = AUDIO_DIR / "cold_open.wav"
    if not (cold_mp4.exists() and cold_mp4.stat().st_size > 50000):
        log("Rendering Cold Open hook...")
        CinematicAnimationDirector.render_cold_open(cold_mp4)

    video_files = [str(cold_mp4)]
    audio_files = [str(cold_wav)]

    # 2. Render and Align All 64 Beats
    log("Assembling all 64 beats with Edge-TTS voiceover, 10 animations, and cinematic transitions...")
    for idx, it in enumerate(STORYBOARD, 1):
        audio_path = AUDIO_DIR / f"beat_{idx}.wav"
        clip_path = ANIM_DIR / f"cinematic_clip_{idx}.mp4"

        dur = get_audio_duration(audio_path)
        tr_type = MAJOR_TRANSITIONS.get(idx, "crossfade")

        if idx in ANIMATION_MAPPING:
            anim_src = ANIMATION_MAPPING[idx]
            render_clip_with_transition(anim_src, clip_path, dur, transition_type=tr_type)
        else:
            bank_item = BROLL_BANK[(idx - 1) % len(BROLL_BANK)]
            broll_file = BROLL_DIR / f"broll_{bank_item['id']}.mp4"
            if not broll_file.exists():
                broll_file = BROLL_DIR / "AIRPORT_TARMAC.mp4"
            render_clip_with_transition(broll_file, clip_path, dur, transition_type=tr_type)

        video_files.append(str(clip_path))
        audio_files.append(str(audio_path))

        if idx % 10 == 0 or idx == len(STORYBOARD):
            log(f"Processed {idx}/64 timeline beats...")

    # 3. Concatenate Dialogue Audio
    log("Concatenating Edge-TTS neural dialogue tracks...")
    audio_concat_txt = EXPORT_DIR / "a_concat.txt"
    with open(audio_concat_txt, "w", encoding="utf-8") as af:
        for af_path in audio_files:
            af.write(f"file '{str(af_path).replace(os.sep, '/')}'\n")

    raw_audio_wav = EXPORT_DIR / "raw_dialogue.wav"
    cmd_a = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(audio_concat_txt), "-c:a", "copy", "-threads", "2", str(raw_audio_wav)]
    subprocess.run(cmd_a, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # 4. Compose Cinematic Soundtrack & Dynamic Audio Mix
    total_doc_sec = get_audio_duration(raw_audio_wav)
    soundtrack_wav = EXPORT_DIR / "soundtrack_master.wav"
    compose_cinematic_music_score(total_doc_sec, soundtrack_wav)

    # Mix dialogue + background music (Music at -18dB relative to voiceover)
    mixed_audio_wav = EXPORT_DIR / "mixed_final_audio.wav"
    log("Mixing dialogue and cinematic music bed (-14 LUFS broadcast standard)...")
    cmd_mix = [
        "ffmpeg", "-y",
        "-i", str(raw_audio_wav),
        "-i", str(soundtrack_wav),
        "-filter_complex", (
            "[0:a]volume=1.0[voice];"
            "[1:a]volume=0.22[music];"
            "[voice][music]amix=inputs=2:duration=first:dropout_transition=2,"
            "loudnorm=I=-14:LRA=9:TP=-1[outa]"
        ),
        "-map", "[outa]",
        "-c:a", "pcm_s16le",
        "-threads", "2",
        str(mixed_audio_wav)
    ]
    subprocess.run(cmd_mix, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # 5. Multiplex Broadcast Master (Continuous stream decode, NO concat copy truncation)
    video_concat_txt = EXPORT_DIR / "v_concat.txt"
    with open(video_concat_txt, "w", encoding="utf-8") as vf:
        for vf_path in video_files:
            vf.write(f"file '{str(vf_path).replace(os.sep, '/')}'\n")

    final_mp4 = EXPORT_DIR / "documentary.mp4"
    log("Multiplexing continuous broadcast master documentary (decoding all 65 scenes)...")
    cmd_final = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(video_concat_txt),
        "-i", str(mixed_audio_wav),
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

    # Cleanup temp concats
    raw_audio_wav.unlink(missing_ok=True)
    soundtrack_wav.unlink(missing_ok=True)
    mixed_audio_wav.unlink(missing_ok=True)
    video_concat_txt.unlink(missing_ok=True)
    audio_concat_txt.unlink(missing_ok=True)

    log(f"MASTERPIECE RENDERED! File: {final_mp4.name} ({final_mp4.stat().st_size / (1024*1024):.2f} MB)")

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
    log("=== CINEMATIC MASTERPIECE PIPELINE COMPLETE! ===")

if __name__ == "__main__":
    main()
