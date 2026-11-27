"""
DocuForge AI - Frame-Accurate Synchronized Masterpiece Engine
Solves:
1. Exact Word-to-Footage Alignment (Zero drift between spoken words and visual evidence)
2. Zero Letterbox / Black Margins (Full-bleed edge-to-edge 16:9 1920x1080)
3. Dedicated Witness Soundbite Insert (Narration pauses while Corti speaks with translation card)
4. Balanced 5-Track Master Audio (Narration + Corti + Emotional Strings + Restrained Foley + Vinyl)
"""

import os
import sys
import wave
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
TEMP_SHOTS_DIR = BASE_DIR / "data" / "media" / "magnates_sync_shots"

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

def get_audio_duration(wav_path: Path) -> float:
    with wave.open(str(wav_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())

# Documentary-Grade Film Print Emulation Grade - FULL BLEED 16:9 (NO LETTERBOX MARGINS)
CINE_GRADE_FULLBLEED = (
    "colorbalance=rs=-0.02:gs=0.01:bs=0.04:rm=-0.01:gm=0.01:bm=0.02:rh=0.04:gh=0.02:bh=-0.03,"
    "eq=contrast=1.06:brightness=0.02:saturation=1.05,"
    "noise=alls=8:allf=t+u,"
    "vignette=PI/12,"
    "fps=30,format=yuv420p"
)

def render_sync_shot(shot_id: str, asset_path: Path, dur: float, shot_type: str, out_path: Path):
    if out_path.exists() and out_path.stat().st_size > 100000:
        return

    if shot_type == "interview_soundbite":
        overlay_png = OVERLAY_DIR / "corti_translated_overlay.png"
        filter_str = (
            f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080:(in_w-1920)/2:(in_h-1080)/2,{CINE_GRADE_FULLBLEED}[base];"
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
        overlay_png = OVERLAY_DIR / "blick_translated_overlay.png"
        filter_str = (
            f"[0:v]scale=2200:1238:force_original_aspect_ratio=increase,crop=1920:1080:(in_w-1920)/2:(in_h-1080)/2,{CINE_GRADE_FULLBLEED}[base];"
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
            drift = f"(in_w-1920)/2+(t/{dur})*30:(in_h-1080)/2+(t/{dur})*16"
        else:
            drift = f"(in_w-1920)/2-(t/{dur})*30:(in_h-1080)/2+(t/{dur})*16"

        vf = (
            f"scale=2200:1238:force_original_aspect_ratio=increase,"
            f"crop=1920:1080:{drift},"
            f"{CINE_GRADE_FULLBLEED}"
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
        # Full Bleed Video (No black margins, 12% punch-in crop to eliminate borders)
        vf = (
            "scale=2200:1238:force_original_aspect_ratio=increase,"
            "crop=1920:1080:(in_w-1920)/2:(in_h-1080)/2,"
            f"{CINE_GRADE_FULLBLEED}"
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

def main():
    log("=======================================================================")
    log("=== LAUNCHING FRAME-ACCURATE SYNCHRONIZED DOCUMENTARY MASTER ENGINE ===")
    log("=======================================================================")

    # 1. Inspect Exact Audio Beat Durations
    beat_durs = {}
    for b in range(1, 8):
        wav_file = AUDIO_DIR / f"beat_{b}.wav"
        beat_durs[b] = get_audio_duration(wav_file)
        log(f"  Narration Beat {b}: {beat_durs[b]:.3f}s")

    corti_wav = SOUNDBITE_DIR / "soundbite_01_corti_press.wav"
    corti_dur = get_audio_duration(corti_wav)
    log(f"  Mario Corti Live Soundbite: {corti_dur:.3f}s")

    # 2. Build Perfectly Matched Visual Shot List
    # Every sub-shot duration sums up to the EXACT duration of that narration beat!
    
    # Beat 1: "On October 2nd, 2001, a single phone call from Zurich Kloten Airport froze the financial nervous system of Europe." (7.968s)
    b1_dur = beat_durs[1]
    b1_s1 = 4.00
    b1_s2 = round(b1_dur - b1_s1, 3)

    # Beat 2: "An Airbus carrying 180 passengers was taxiing toward the runway when the control tower received an unprecedented directive: fuel suppliers had cut off the kerosene." (12.048s)
    b2_dur = beat_durs[2]
    b2_s1 = 4.00
    b2_s2 = 3.50
    b2_s3 = round(b2_dur - b2_s1 - b2_s2, 3)

    # Beat 3: "The credit lines were dead." (1.872s)
    b3_dur = beat_durs[3]

    # Beat 4: "Within forty-eight hours, every plane belonging to one of the most prestigious airlines on Earth was grounded on tarmac across the globe." (8.832s)
    b4_dur = beat_durs[4]
    b4_s1 = 4.30
    b4_s2 = round(b4_dur - b4_s1, 3)

    # Witness Evidence Soundbite: Mario Corti (4.500s) -> Narration pauses, Corti speaks!
    
    # Beat 5: "To the traveling public, Swissair was not merely a carrier—it was nicknamed 'The Flying Bank', a fortress of Swiss financial invulnerability." (9.432s)
    b5_dur = beat_durs[5]
    b5_s1 = 4.50
    b5_s2 = round(b5_dur - b5_s1, 3)

    # Beat 6: "Yet behind corporate doors, a catastrophic strategy of debt, ambition, and institutional blind spots had quietly driven the company over the edge." (10.440s)
    b6_dur = beat_durs[6]
    b6_s1 = 5.00
    b6_s2 = round(b6_dur - b6_s1, 3)

    # Beat 7: "How does an institution backed by the world's most powerful banking cartel collapse in less than forty-eight hours?" (7.632s)
    b7_dur = beat_durs[7]
    b7_s1 = 3.60
    b7_s2 = round(b7_dur - b7_s1, 3)

    SYNC_SEQUENCE = [
        # BEAT 1 (0.00s -> 7.97s): Kloten Airport phone call & European finance
        ("SYNC_01", AUTHENTIC_DIR / "zurich_uncut_38_foggy_morning_kloten.mp4", b1_s1, "whoosh_cinematic", "video"),
        ("SYNC_02", AUTHENTIC_DIR / "politics_ubs_01_bern_parliament.mp4", b1_s2, "sub_boom_heavy", "video"),

        # BEAT 2 (7.97s -> 20.02s): Airbus taxiing, control tower directive, kerosene cutoff
        ("SYNC_03", AUTHENTIC_DIR / "zurich_uncut_04_cockpit_view.mp4", b2_s1, "freesound_airplane_chime_ding", "video"),
        ("SYNC_04", AUTHENTIC_DIR / "zurich_uncut_11_tower_pan.mp4", b2_s2, "whoosh_cinematic", "video"),
        ("SYNC_05", AI_DIR / "ai_07_fuel_hose_cutoff.jpg", b2_s3, "freesound_jet_engine_tarmac", "ai_drift"),

        # BEAT 3 (20.02s -> 21.89s): "The credit lines were dead"
        ("SYNC_06", AUTHENTIC_DIR / "politics_ubs_06_bank_vault_doors.mp4", b3_dur, "sub_drop_dark", "video"),

        # BEAT 4 (21.89s -> 30.72s): Ground crew wrapping engines, split-flap cancellation board
        ("SYNC_07", AUTHENTIC_DIR / "zurich_uncut_25_engine_cover_wrap.mp4", b4_s1, "tape_recorder_click", "video"),
        ("SYNC_08", AI_DIR / "ai_09_cancelled_departure_board.jpg", b4_s2, "freesound_typewriter_single_key", "ai_drift"),

        # EVIDENCE SOUNDBITE (30.72s -> 35.22s): Mario Corti speaks live at Zurich briefing
        ("SYNC_09", SOUNDBITE_DIR / "soundbite_01_corti_press.mp4", corti_dur, "camera_shutter_snap", "interview_soundbite"),

        # BEAT 5 (35.22s -> 44.65s): "The Flying Bank" & 3D investigation desk dossier
        ("SYNC_10", AUTHENTIC_DIR / "zurich_uncut_09_swissair_cross.mp4", b5_s1, "sub_boom_heavy", "video"),
        ("SYNC_11", STAGE_DIR / "stage_01_mario_corti.mp4", b5_s2, "freesound_camera_shutter_click", "stage"),

        # BEAT 6 (44.65s -> 55.09s): Balance sheet debt inspector & 2.5D Bruggisser parallax
        ("SYNC_12", REMOTION_DIR / "kinetic_document_inspector.mp4", b6_s1, "paper_slide_desk", "remotion"),
        ("SYNC_13", REMOTION_DIR / "parallax_bruggisser.mp4", b6_s2, "whoosh_cinematic", "remotion"),

        # BEAT 7 (55.09s -> 62.72s): Blick headline translation & grounded fleet aerial finale
        ("SYNC_14", PAPER_DIR / "paper_01_blick_grounded.mp4", b7_s1, "sub_drop_dark", "translated_headline"),
        ("SYNC_15", AI_DIR / "ai_08_grounded_fleet_aerial.jpg", b7_s2, "whoosh_cinematic", "ai_drift")
    ]

    log(f"Rendering {len(SYNC_SEQUENCE)} frame-accurately aligned master shots (Full Bleed 16:9)...")
    rendered_shots = []
    sfx_events = []
    cum_t = 0.0

    for i, (shot_id, path, dur, sfx_cue, s_type) in enumerate(SYNC_SEQUENCE, 1):
        out_shot = TEMP_SHOTS_DIR / f"{shot_id}.mp4"
        log(f"  Shot {i:02d}/{len(SYNC_SEQUENCE)} [{shot_id}]: {path.name} ({dur:.2f}s, {s_type})")
        render_sync_shot(shot_id, path, dur, s_type, out_shot)
        rendered_shots.append(out_shot)
        sfx_events.append((cum_t, sfx_cue))
        cum_t += dur

    total_video_dur = cum_t
    log(f"Total Video Timeline: {total_video_dur:.3f}s")

    # 3. Assemble Frame-Accurate Master Narration Track (with Corti soundbite inlined)
    # The narration audio concatenates Beat 1..4, Corti audio, Beat 5..7
    audio_concat_txt = TEMP_SHOTS_DIR / "master_audio_concat.txt"
    with open(audio_concat_txt, "w", encoding="utf-8") as f:
        for b in [1, 2, 3, 4]:
            f.write(f"file '{str(AUDIO_DIR / f'beat_{b}.wav').replace(os.sep, '/')}'\n")
        f.write(f"file '{str(corti_wav).replace(os.sep, '/')}'\n")
        for b in [5, 6, 7]:
            f.write(f"file '{str(AUDIO_DIR / f'beat_{b}.wav').replace(os.sep, '/')}'\n")

    master_speech_wav = TEMP_SHOTS_DIR / "master_speech_synced.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(audio_concat_txt),
        "-c:a", "pcm_s16le", str(master_speech_wav)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    speech_dur = get_audio_duration(master_speech_wav)
    log(f"Total Speech Audio Timeline: {speech_dur:.3f}s (Diff from video: {abs(speech_dur - total_video_dur):.3f}s)")

    # 4. Synthesize Restrained Foley Track (Gentle, warm, non-distracting)
    SR = 44100
    total_samples = int(total_video_dur * SR)
    foley_track = np.zeros(total_samples, dtype=np.float32)

    vinyl_f = FOLEY_DIR / "archival_vinyl_bed.wav"
    if vinyl_f.exists():
        v_samp = load_wav_samples(vinyl_f)
        reps = (total_samples // len(v_samp)) + 1
        foley_track += np.tile(v_samp, reps)[:total_samples] * 0.018

    foley_lib = {
        "whoosh_cinematic": (load_wav_samples(FOLEY_DIR / "whoosh_cinematic.wav"), 0.12),
        "sub_boom_heavy": (load_wav_samples(FOLEY_DIR / "sub_boom_heavy.wav"), 0.14),
        "sub_drop_dark": (load_wav_samples(FOLEY_DIR / "sub_drop_dark.wav"), 0.13),
        "paper_slide_desk": (load_wav_samples(FOLEY_DIR / "paper_slide_desk.wav"), 0.10),
        "camera_shutter_snap": (load_wav_samples(FOLEY_DIR / "camera_shutter_snap.wav"), 0.10),
        "tape_recorder_click": (load_wav_samples(FOLEY_DIR / "tape_recorder_click.wav"), 0.10),
        "freesound_typewriter_single_key": (load_wav_samples(FOLEY_DIR / "freesound_typewriter_single_key.wav"), 0.12),
        "freesound_camera_shutter_click": (load_wav_samples(FOLEY_DIR / "freesound_camera_shutter_click.wav"), 0.12),
        "freesound_airplane_chime_ding": (load_wav_samples(FOLEY_DIR / "freesound_airplane_chime_ding.wav"), 0.14),
        "freesound_jet_engine_tarmac": (load_wav_samples(FOLEY_DIR / "freesound_jet_engine_tarmac.wav"), 0.10)
    }

    for t_s, sfx_name in sfx_events:
        idx = int(t_s * SR)
        if sfx_name in foley_lib and idx < total_samples:
            samp, vol = foley_lib[sfx_name]
            l = min(len(samp), total_samples - idx)
            foley_track[idx:idx+l] += samp[:l] * vol

    foley_wav = TEMP_SHOTS_DIR / "stem_foley_restrained.wav"
    with wave.open(str(foley_wav), "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((np.clip(foley_track, -0.9, 0.9) * 32767).astype(np.int16).tobytes())

    # 5. Emotional Orchestral Strings Score
    score_path = BASE_DIR / "data" / "media" / "audio" / "cinematic_orchestral_tragedy.wav"
    music_wav = TEMP_SHOTS_DIR / "stem_emotional_music.wav"
    fade_out_st = max(0.0, total_video_dur - 2.5)
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(score_path),
        "-t", str(round(total_video_dur, 2)),
        "-af", f"afade=t=in:ss=0:d=1.5,afade=t=out:st={fade_out_st:.2f}:d=2.5",
        "-ar", "44100",
        "-ac", "2",
        str(music_wav)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 6. Balanced Audio Mix
    # Narration & Corti speech: volume=1.0, loudnorm -14 LUFS
    # Music: volume=0.22 (gentle emotional warmth, never drowns speech)
    # Foley: volume=0.15 (gentle background immersion, lowpass 4500Hz)
    master_mix_wav = TEMP_SHOTS_DIR / "master_mix_perfect.wav"
    filter_mix = (
        "[0:a]volume=1.0[speech];"
        "[1:a]volume=0.22[music];"
        "[2:a]lowpass=f=4500,volume=0.15[foley];"
        "[speech][music][foley]amix=inputs=3:duration=first:dropout_transition=2:normalize=0,"
        "loudnorm=I=-14:TP=-1.5:LRA=10[outa]"
    )
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(master_speech_wav),
        "-i", str(music_wav),
        "-i", str(foley_wav),
        "-filter_complex", filter_mix,
        "-map", "[outa]",
        "-ar", "44100",
        str(master_mix_wav)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 7. Video Concat & Multiplex Final Master Video
    video_concat_txt = TEMP_SHOTS_DIR / "shots_concat.txt"
    with open(video_concat_txt, "w", encoding="utf-8") as f:
        for s in rendered_shots:
            f.write(f"file '{str(s).replace(os.sep, '/')}'\n")

    master_mp4 = EXPORT_DIR / "documentary.mp4"
    log(f"Multiplexing final broadcast master -> {master_mp4} (Full Bleed 16:9, FastStart)...")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(video_concat_txt),
        "-i", str(master_mix_wav),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "19",
        "-r", "24",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(master_mp4)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    sz_mb = master_mp4.stat().st_size / (1024 * 1024)
    log(f"=== SYNCHRONIZED MASTERPIECE COMPLETED: {sz_mb:.2f} MB, {total_video_dur:.2f}s ===")

if __name__ == "__main__":
    main()
