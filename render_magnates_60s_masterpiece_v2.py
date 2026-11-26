"""
DocuForge AI - MagnatesMedia 60-Second Documentary Masterpiece Engine v2
Documentary-Grade 35mm Film Color Grade, Emotional Orchestral Score,
Restrained Immersive Foley, and English Translation Subtitles.

Key Upgrades:
1. Documentary-Grade Color Grading:
   - Kodak Vision3 film print color matrix (deep cyan shadows, warm amber highlights)
   - Fine 35mm organic film grain (noise=alls=10:allf=t+u)
   - 2.35:1 Anamorphic Widescreen Letterbox (drawbox 60px top/bottom)
   - Soft optical lens vignette (PI/12)
2. Emotional Music Score:
   - Real cinematic orchestral tragedy score (mournful strings, piano & cello)
   - Dynamically balanced under voiceover
3. Foley Restraint & Immersion:
   - Reduced volume by -16dB relative to voiceover
   - High-cut filter (lowpass=4500Hz) to prevent ear fatigue and audience disturbance
4. Foreign Language Translation Subtitles:
   - Mario Corti soundbite translated with lower-third broadcast card
   - German headline translated (Blick: "Der schwarze Dienstag" -> "The Black Tuesday")
"""

import os
import sys
import wave
import json
import time
import subprocess
import numpy as np
from pathlib import Path

BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
PROJ_ID = "swiss-air-grounding-prod"
EXPORT_DIR = BASE_DIR / "data" / "exports" / PROJ_ID
AUDIO_DIR = BASE_DIR / "data" / "media" / "audio" / PROJ_ID
FOLEY_DIR = BASE_DIR / "data" / "media" / "master_foley"
STAGE_DIR = BASE_DIR / "data" / "media" / "magnates_stage"
REMOTION_DIR = BASE_DIR / "data" / "media" / "remotion_renders"
SOUNDBITE_DIR = BASE_DIR / "data" / "media" / "archival_soundbites"
AI_DIR = BASE_DIR / "data" / "media" / "cinematic_ai_assets"
AUTHENTIC_DIR = BASE_DIR / "data" / "media" / "authentic_clips"
PAPER_DIR = BASE_DIR / "data" / "media" / "paper_assets"
OVERLAY_DIR = BASE_DIR / "data" / "media" / "overlays"
TEMP_SHOTS_DIR = BASE_DIR / "data" / "media" / "magnates_60s_v2_shots"

TEMP_SHOTS_DIR.mkdir(parents=True, exist_ok=True)
OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def load_wav_samples(wav_path: Path):
    with wave.open(str(wav_path), "rb") as wf:
        n = wf.getnframes()
        data = wf.readframes(n)
        return np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0

# 24 Master Documentary Shots for Exactly 55-60 Seconds
MASTER_SEQUENCE = [
    # Act 1: The Hook & Physical Desk Staging (0.0s - 15.0s)
    ("MAG_01", AUTHENTIC_DIR / "zurich_uncut_38_foggy_morning_kloten.mp4", 2.2, "whoosh_cinematic", "video"),
    ("MAG_02", AI_DIR / "ai_07_fuel_hose_cutoff.jpg", 2.0, "freesound_jet_engine_tarmac", "ai_drift"),
    ("MAG_03", AUTHENTIC_DIR / "zurich_uncut_09_swissair_cross.mp4", 2.0, "sub_boom_heavy", "video"),
    ("MAG_04", STAGE_DIR / "stage_01_mario_corti.mp4", 2.5, "freesound_camera_shutter_click", "stage"),
    ("MAG_05", SOUNDBITE_DIR / "soundbite_01_corti_press.mp4", 3.8, "camera_shutter_snap", "interview_soundbite"),
    ("MAG_06", REMOTION_DIR / "kinetic_document_inspector.mp4", 2.5, "paper_slide_desk", "remotion"),

    # Act 2: The Hunter Strategy & 2.5D Parallax Rigs (15.0s - 35.0s)
    ("MAG_07", REMOTION_DIR / "parallax_bruggisser.mp4", 2.8, "whoosh_cinematic", "remotion"),
    ("MAG_08", STAGE_DIR / "stage_03_ubs_dossier.mp4", 2.5, "freesound_typewriter_single_key", "stage"),
    ("MAG_09", AI_DIR / "ai_04_ubs_boardroom_crisis.jpg", 2.2, "paper_slide_desk", "ai_drift"),
    ("MAG_10", AI_DIR / "ai_03_british_airways_heathrow.jpg", 2.0, "whoosh_cinematic", "ai_drift"),
    ("MAG_11", AI_DIR / "ai_01_lufthansa_takeoff.jpg", 2.0, "whoosh_cinematic", "ai_drift"),
    ("MAG_12", AI_DIR / "ai_02_air_france_747.jpg", 2.0, "whoosh_cinematic", "ai_drift"),
    ("MAG_13", AUTHENTIC_DIR / "zurich_uncut_04_cockpit_view.mp4", 2.2, "freesound_airplane_chime_ding", "video"),
    ("MAG_14", AUTHENTIC_DIR / "politics_ubs_01_bern_parliament.mp4", 2.0, "sub_drop_dark", "video"),

    # Act 3: The Trap Snaps & Grounding Day (35.0s - 60.0s)
    ("MAG_15", AUTHENTIC_DIR / "politics_ubs_06_bank_vault_doors.mp4", 2.2, "sub_boom_heavy", "video"),
    ("MAG_16", AUTHENTIC_DIR / "politics_ubs_08_bundesrat_session.mp4", 2.0, "freesound_typewriter_single_key", "video"),
    ("MAG_17", AI_DIR / "ai_05_bruggisser_hunter_office.jpg", 2.2, "camera_shutter_snap", "ai_drift"),
    ("MAG_18", AUTHENTIC_DIR / "zurich_uncut_11_tower_pan.mp4", 2.0, "whoosh_cinematic", "video"),
    ("MAG_19", AI_DIR / "ai_09_cancelled_departure_board.jpg", 2.2, "freesound_typewriter_single_key", "ai_drift"),
    ("MAG_20", AI_DIR / "ai_10_stranded_passengers_terminal.jpg", 2.0, "paper_slide_desk", "ai_drift"),
    ("MAG_21", PAPER_DIR / "paper_01_blick_grounded.mp4", 2.2, "sub_boom_heavy", "translated_headline"),
    ("MAG_22", AI_DIR / "ai_11_protest_paradeplatz_ubs.jpg", 2.2, "whoosh_cinematic", "ai_drift"),
    ("MAG_23", AUTHENTIC_DIR / "zurich_uncut_25_engine_cover_wrap.mp4", 2.0, "tape_recorder_click", "video"),
    ("MAG_24", AI_DIR / "ai_08_grounded_fleet_aerial.jpg", 2.9, "sub_drop_dark", "ai_drift")
]

# Documentary-Grade Film Print Emulation Grade
# Teal-Cyan shadows, warm amber highlights, 35mm grain, 2.35:1 letterbox
CINE_FILM_GRADE = (
    "colorbalance=rs=-0.02:gs=0.01:bs=0.04:rm=-0.01:gm=0.01:bm=0.02:rh=0.04:gh=0.02:bh=-0.03,"
    "eq=contrast=1.08:brightness=0.02:saturation=1.06,"
    "noise=alls=10:allf=t+u,"
    "vignette=PI/12,"
    "drawbox=y=0:h=60:color=black:t=fill,"
    "drawbox=y=ih-60:h=60:color=black:t=fill,"
    "fps=30,format=yuv420p"
)

def render_master_shot(shot_id: str, asset_path: Path, dur: float, shot_type: str, out_path: Path):
    if out_path.exists() and out_path.stat().st_size > 100000:
        return

    if shot_type == "interview_soundbite":
        # Mario Corti Soundbite with lower third AND English Translation Subtitle
        overlay_png = OVERLAY_DIR / "corti_translated_overlay.png"
        filter_str = (
            f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080:(in_w-1920)/2:(in_h-1080)/2,{CINE_FILM_GRADE}[base];"
            f"[base][1:v]overlay=0:0[v]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-ss", "0.2",
            "-i", str(asset_path),
            "-i", str(overlay_png),
            "-t", str(round(dur, 2)),
            "-filter_complex", filter_str,
            "-map", "[v]",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "19",
            "-an",
            str(out_path)
        ]
    elif shot_type == "translated_headline":
        # Blick Newspaper with English Headline Translation Card
        overlay_png = OVERLAY_DIR / "blick_translated_overlay.png"
        filter_str = (
            f"[0:v]scale=2200:1238:force_original_aspect_ratio=increase,crop=1920:1080:(in_w-1920)/2:(in_h-1080)/2,{CINE_FILM_GRADE}[base];"
            f"[base][1:v]overlay=0:0[v]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-ss", "0.2",
            "-i", str(asset_path),
            "-i", str(overlay_png),
            "-t", str(round(dur, 2)),
            "-filter_complex", filter_str,
            "-map", "[v]",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "19",
            "-an",
            str(out_path)
        ]
    elif shot_type == "ai_drift":
        idx_hash = sum(ord(c) for c in shot_id)
        if idx_hash % 2 == 0:
            drift = f"(in_w-1920)/2+(t/{dur})*35:(in_h-1080)/2+(t/{dur})*18"
        else:
            drift = f"(in_w-1920)/2-(t/{dur})*35:(in_h-1080)/2+(t/{dur})*18"

        vf = (
            f"scale=2200:1238:force_original_aspect_ratio=increase,"
            f"crop=1920:1080:{drift},"
            f"{CINE_FILM_GRADE}"
        )
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(asset_path),
            "-t", str(round(dur, 2)),
            "-vf", vf,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "19",
            "-an",
            str(out_path)
        ]
    else:
        # Standard video / stage / remotion with 12% punch-in crop and film grade
        vf = (
            "scale=2200:1238:force_original_aspect_ratio=increase,"
            "crop=1920:1080:(in_w-1920)/2:(in_h-1080)/2,"
            f"{CINE_FILM_GRADE}"
        )
        cmd = [
            "ffmpeg", "-y",
            "-ss", "0.2",
            "-i", str(asset_path),
            "-t", str(round(dur, 2)),
            "-vf", vf,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "19",
            "-an",
            str(out_path)
        ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def prepare_emotional_score(total_sec: float, out_wav: Path):
    score_path = BASE_DIR / "data" / "media" / "audio" / "cinematic_orchestral_tragedy.wav"
    fade_out_st = max(0.0, total_sec - 2.5)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(score_path),
        "-t", str(round(total_sec, 2)),
        "-af", f"afade=t=in:ss=0:d=1.5,afade=t=out:st={fade_out_st:.2f}:d=2.5",
        "-ar", "44100",
        "-ac", "2",
        str(out_wav)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def build_multitrack_audio(total_sec: float, sfx_events: list, soundbite_t: float, soundbite_dur: float, out_wav: Path):
    SR = 44100
    total_samples = int(total_sec * SR)
    
    # 1. Narration Dialogue
    narration_wav = TEMP_SHOTS_DIR / "narration_60s.wav"
    narration_beats = [AUDIO_DIR / f"beat_{i}.wav" for i in range(1, 8)]
    with open(TEMP_SHOTS_DIR / "narr_concat.txt", "w") as f:
        for nb in narration_beats:
            f.write(f"file '{str(nb).replace(os.sep, '/')}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(TEMP_SHOTS_DIR / "narr_concat.txt"),
        "-t", str(round(total_sec, 2)),
        "-c:a", "pcm_s16le", str(narration_wav)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 2. Authentic Corti Interview Soundbite (German audio)
    soundbite_wav = SOUNDBITE_DIR / "soundbite_01_corti_press.wav"
    corti_track = np.zeros(total_samples, dtype=np.float32)
    if soundbite_wav.exists():
        c_samp = load_wav_samples(soundbite_wav)
        idx0 = int(soundbite_t * SR)
        l = min(len(c_samp), total_samples - idx0)
        corti_track[idx0:idx0+l] = c_samp[:l] * 0.90

    # 3. Master Foley & Freesound Track (Gentle, warm, non-distracting)
    foley_track = np.zeros(total_samples, dtype=np.float32)
    vinyl_f = FOLEY_DIR / "archival_vinyl_bed.wav"
    if vinyl_f.exists():
        v_samp = load_wav_samples(vinyl_f)
        reps = (total_samples // len(v_samp)) + 1
        foley_track += np.tile(v_samp, reps)[:total_samples] * 0.020

    # Balanced Foley levels (subtle immersion, zero ear disturbance)
    foley_lib = {
        "whoosh_cinematic": (load_wav_samples(FOLEY_DIR / "whoosh_cinematic.wav"), 0.14),
        "sub_boom_heavy": (load_wav_samples(FOLEY_DIR / "sub_boom_heavy.wav"), 0.16),
        "sub_drop_dark": (load_wav_samples(FOLEY_DIR / "sub_drop_dark.wav"), 0.15),
        "paper_slide_desk": (load_wav_samples(FOLEY_DIR / "paper_slide_desk.wav"), 0.12),
        "camera_shutter_snap": (load_wav_samples(FOLEY_DIR / "camera_shutter_snap.wav"), 0.12),
        "tape_recorder_click": (load_wav_samples(FOLEY_DIR / "tape_recorder_click.wav"), 0.12),
        "freesound_typewriter_single_key": (load_wav_samples(FOLEY_DIR / "freesound_typewriter_single_key.wav"), 0.15),
        "freesound_camera_shutter_click": (load_wav_samples(FOLEY_DIR / "freesound_camera_shutter_click.wav"), 0.14),
        "freesound_airplane_chime_ding": (load_wav_samples(FOLEY_DIR / "freesound_airplane_chime_ding.wav"), 0.18),
        "freesound_jet_engine_tarmac": (load_wav_samples(FOLEY_DIR / "freesound_jet_engine_tarmac.wav"), 0.12)
    }

    for t_s, sfx_name in sfx_events:
        idx = int(t_s * SR)
        if sfx_name in foley_lib and idx < total_samples:
            samp, vol = foley_lib[sfx_name]
            l = min(len(samp), total_samples - idx)
            foley_track[idx:idx+l] += samp[:l] * vol

    # Save stems
    corti_wav = TEMP_SHOTS_DIR / "stem_corti.wav"
    with wave.open(str(corti_wav), "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((corti_track * 32767).astype(np.int16).tobytes())

    foley_wav = TEMP_SHOTS_DIR / "stem_foley.wav"
    with wave.open(str(foley_wav), "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((np.clip(foley_track, -0.9, 0.9) * 32767).astype(np.int16).tobytes())

    music_wav = TEMP_SHOTS_DIR / "stem_emotional_score.wav"
    prepare_emotional_score(total_sec, music_wav)

    # 4. Balanced Broadcast 4-Stem Master Mix
    # - Narration voiceover: -14 LUFS, pristine clarity
    # - Mario Corti soundbite: Narration ducks down to 0.05 while he speaks
    # - Emotional orchestral score: volume=0.28 (warm and expressive, ducked during Corti)
    # - Foley track: gentle low-pass filter at 4500Hz to eliminate ear-piercing highs
    filter_mix = (
        f"[0:a]volume=enable='between(t,{soundbite_t:.2f},{soundbite_t+soundbite_dur:.2f})':volume=0.05[narr];"
        f"[1:a]volume=0.90[corti];"
        f"[2:a]volume=enable='between(t,{soundbite_t:.2f},{soundbite_t+soundbite_dur:.2f})':volume=0.18,volume=0.28[music];"
        f"[3:a]lowpass=f=4500,volume=0.16[foley];"
        f"[narr][corti][music][foley]amix=inputs=4:duration=first:dropout_transition=2:normalize=0,"
        f"loudnorm=I=-14:TP=-1.5:LRA=10[outa]"
    )
    cmd_mix = [
        "ffmpeg", "-y",
        "-i", str(narration_wav),
        "-i", str(corti_wav),
        "-i", str(music_wav),
        "-i", str(foley_wav),
        "-filter_complex", filter_mix,
        "-map", "[outa]",
        "-ar", "44100",
        str(out_wav)
    ]
    subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def main():
    log("=======================================================================")
    log("=== LAUNCHING MAGNATESMEDIA DOCUMENTARY MASTER v2 (FILMIC & EMOTIONAL) ===")
    log("=======================================================================")

    rendered_shots = []
    sfx_events = []
    cum_t = 0.0
    soundbite_t = 0.0
    soundbite_dur = 0.0

    total_shots = len(MASTER_SEQUENCE)
    for i, (shot_id, path, dur, sfx_cue, s_type) in enumerate(MASTER_SEQUENCE, 1):
        out_shot = TEMP_SHOTS_DIR / f"{shot_id}.mp4"
        if not path.exists():
            log(f"WARNING: Asset {path} missing, skipping...")
            continue
        
        if s_type == "interview_soundbite":
            soundbite_t = cum_t
            soundbite_dur = dur

        if not out_shot.exists():
            log(f"  Rendering Shot {i:02d}/{total_shots} [{shot_id}]: {path.name} ({dur}s, {s_type})")
            render_master_shot(shot_id, path, dur, s_type, out_shot)
        else:
            log(f"  Shot {i:02d}/{total_shots} [{shot_id}]: Cached OK")

        rendered_shots.append(out_shot)
        sfx_events.append((cum_t, sfx_cue))
        cum_t += dur

    total_sec = cum_t
    log(f"All {len(rendered_shots)} master shots ready! Sequence duration: {total_sec:.2f}s")

    # Build Master Video Concat
    concat_list = TEMP_SHOTS_DIR / "shots_concat.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for s in rendered_shots:
            f.write(f"file '{str(s).replace(os.sep, '/')}'\n")

    # Build Balanced Audio Mix with Emotional Orchestral Score & Restrained Foley
    master_mix_wav = TEMP_SHOTS_DIR / "master_mixed_audio_v2.wav"
    log("Building 5-track synchronized audio mix (Voiceover, Corti Soundbite, Emotional Strings, Restrained Foley)...")
    build_multitrack_audio(total_sec, sfx_events, soundbite_t, soundbite_dur, master_mix_wav)

    # Multiplex Final Master Video
    master_mp4 = EXPORT_DIR / "documentary.mp4"
    log(f"Multiplexing final broadcast master -> {master_mp4} (24 FPS, FastStart)...")
    mux_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-i", str(master_mix_wav),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-r", "24",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(master_mp4)
    ]
    subprocess.run(mux_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    sz_mb = master_mp4.stat().st_size / (1024 * 1024)
    log(f"=== MASTERPIECE v2 COMPLETED: {sz_mb:.2f} MB, {total_sec:.2f}s ===")

if __name__ == "__main__":
    main()
