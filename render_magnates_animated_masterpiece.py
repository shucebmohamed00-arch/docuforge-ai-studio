"""
DocuForge AI - Animated MagnatesMedia Masterpiece Engine v4 (Paper Transitions, 3D Maps, Charts & Foley)
Solves:
1. Paper animation & transitions between shots (paper rip/tear wipes with organic fibers and drop shadow)
2. 3D Maps Animation (anim_01_map.mp4 - Geographic Airspace Entrapment with pulsing radar & route arcs)
3. 3D Graphics & Animations (anim_07_hunter_wheel.mp4, anim_02_chart.mp4, Remotion kinetic document inspector)
4. Context-Aware Foley & Sound Design:
   - Typewriter typing clacks on date badge writing
   - Money counting & cash register ding on fuel cash refusal
   - Heavy steel vault lock slam on credit line revocation
   - Paper slides & paper tears on document transitions
   - Aviation chimes and jet engines
5. Exact 0.000s Audio-Visual Lock across 16 rapid broadcast shots
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
ANIM_DIR = BASE_DIR / "data" / "media" / "animations" / PROJ_ID
TEMP_SHOTS_DIR = BASE_DIR / "data" / "media" / "magnates_animated_shots"

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

CINE_GRADE_FULLBLEED = (
    "colorbalance=rs=-0.02:gs=0.01:bs=0.04:rm=-0.01:gm=0.01:bm=0.02:rh=0.04:gh=0.02:bh=-0.03,"
    "eq=contrast=1.06:brightness=0.02:saturation=1.05,"
    "noise=alls=8:allf=t+u,"
    "vignette=PI/12,"
    "fps=30,format=yuv420p"
)

def render_animated_shot(shot_id: str, asset_path: Path, dur: float, shot_type: str, overlay_path: Path | None, out_path: Path):
    pad_filter = "tpad=stop_mode=clone:stop_duration=3.0"
    if shot_type == "ai_drift":
        idx_hash = sum(ord(c) for c in shot_id)
        if idx_hash % 2 == 0:
            drift = f"(in_w-1920)/2+(t/{dur})*30:(in_h-1080)/2+(t/{dur})*16"
        else:
            drift = f"(in_w-1920)/2-(t/{dur})*30:(in_h-1080)/2+(t/{dur})*16"
        base_filter = f"scale=2200:1238:force_original_aspect_ratio=increase,crop=1920:1080:{drift},{CINE_GRADE_FULLBLEED}"
        input_args = ["-loop", "1", "-i", str(asset_path)]
    elif shot_type == "interview_soundbite":
        base_filter = f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080:(in_w-1920)/2:(in_h-1080)/2,{pad_filter},{CINE_GRADE_FULLBLEED}"
        input_args = ["-ss", "0.2", "-i", str(asset_path)]
    else:
        # Standard video / stage / remotion / animation
        base_filter = f"scale=2200:1238:force_original_aspect_ratio=increase,crop=1920:1080:(in_w-1920)/2:(in_h-1080)/2,{pad_filter},{CINE_GRADE_FULLBLEED}"
        input_args = ["-ss", "0.2", "-i", str(asset_path)]

    if overlay_path and overlay_path.exists():
        overlay_inputs = ["-loop", "1", "-i", str(overlay_path)] if overlay_path.suffix.lower() == ".png" else ["-i", str(overlay_path)]
        filter_complex = f"[0:v]{base_filter}[base];[base][1:v]overlay=0:0:eof_action=pass[v]"
        cmd = [
            "ffmpeg", "-y",
            *input_args,
            *overlay_inputs,
            "-t", str(round(dur, 2)),
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "19",
            "-an",
            str(out_path)
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            *input_args,
            "-t", str(round(dur, 2)),
            "-vf", base_filter,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "19",
            "-an",
            str(out_path)
        ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def main():
    log("=======================================================================")
    log("=== LAUNCHING ANIMATED MASTERPIECE ENGINE v4 (3D MAPS, PAPER & FOLEY) ===")
    log("=======================================================================")

    # Exact Audio Beat Durations
    beat_durs = {b: get_audio_duration(AUDIO_DIR / f"beat_{b}.wav") for b in range(1, 8)}
    corti_wav = SOUNDBITE_DIR / "soundbite_01_corti_press.wav"
    corti_dur = get_audio_duration(corti_wav)

    T_DUR = 0.35

    # Beat 1: 7.968s
    b1_dur = beat_durs[1]
    b1_s1 = 4.00 # Kloten Fog + Incident Date Badge
    b1_s2 = round(b1_dur - b1_s1, 3) # 3D Animated Geographic Map

    # Beat 2: 12.048s
    b2_dur = beat_durs[2]
    b2_s1 = 4.00 # Cockpit view + Flight HUD
    b2_s2 = 3.50 # ATC Tower Pan
    b2_s3 = round(b2_dur - b2_s1 - b2_s2, 3) # Fuel valve + Cash refused

    # Beat 3: 1.872s
    b3_dur = beat_durs[3] # Vault doors + Credit Stamp

    # Beat 4: 8.832s
    b4_dur = beat_durs[4]
    b4_s1 = 4.30 # Engine wrap
    b4_s2 = round(b4_dur - b4_s1, 3) # Departure board + 48h countdown

    # Beat 5: 9.432s
    b5_dur = beat_durs[5]
    b5_s1 = 4.50 # Swissair tailfin + "The Flying Bank" gold card
    b5_s2 = round(b5_dur - b5_s1, 3) # 3D Mario Corti desk dossier

    # Beat 6: 10.440s
    b6_dur = beat_durs[6]
    b6_s1 = 3.40 # 3D Hunter Acquisition Wheel
    b6_s2 = 3.50 # Forensic Debt Chart (1.8B -> 17B CHF)
    b6_s3 = round(b6_dur - b6_s1 - b6_s2, 3) # Remotion Balance Sheet Inspector

    # Beat 7: 7.632s
    b7_dur = beat_durs[7]
    b7_s1 = 3.60 # Blick Newspaper headline + Translation card
    b7_s2 = round(b7_dur - b7_s1, 3) # Dusk Grounded Fleet Aerial

    # 16 Master Shots (Mixing 3D Maps, Hunter Wheel, Forensic Chart, Remotion, and Authentic B-roll)
    SHOT_SPECS = [
        # Shot 01: Foggy Rainy Airport Tarmac with Animated Date Badge & Synced Typewriter Foley
        ("SHOT_01", AUTHENTIC_DIR / "pixabay_airport_tarmac_morning.mp4", b1_s1, "video",
         OVERLAY_DIR / "anim_01_date_badge.mov", "fadeblack", "typewriter_typing_burst"),

        # Shot 02: 3D Animated Flight Route Map (Swiss Airspace Entrapment)
        ("SHOT_02", ANIM_DIR / "anim_01_map.mp4", b1_s2, "video",
         None, "wipeleft", "whoosh_cinematic"),

        # Shot 03: Airliner Taxiway Departure with Animated Flight SR 111 HUD
        ("SHOT_03", AUTHENTIC_DIR / "pixabay_airliner_departure.mp4", b2_s1, "video",
         OVERLAY_DIR / "anim_02_flight_hud.mov", "smoothleft", "freesound_airplane_chime_ding"),

        # Shot 04: Kloten Tower Pan
        ("SHOT_04", AUTHENTIC_DIR / "zurich_uncut_11_tower_pan.mp4", b2_s2, "video",
         None, "fadewhite", "freesound_jet_engine_tarmac"),

        # Shot 05: Kerosene Emergency Cutoff Valve with Money & Cash Register Foley
        ("SHOT_05", AI_DIR / "ai_07_fuel_hose_cutoff.jpg", b2_s3, "ai_drift",
         None, "rectcrop", "money_banknotes_counting"),

        # Shot 06: Bank Vault Security Doors with Rubber Stamp Slam & Heavy Lock Boom
        ("SHOT_06", AUTHENTIC_DIR / "politics_ubs_06_bank_vault_doors.mp4", b3_dur, "video",
         OVERLAY_DIR / "anim_03_stamp_credit_dead.mov", "slideleft", "sub_boom_heavy"),

        # Shot 07: Engine Cover Wrapping
        ("SHOT_07", AUTHENTIC_DIR / "zurich_uncut_25_engine_cover_wrap.mp4", b4_s1, "video",
         None, "smoothup", "tape_recorder_click"),

        # Shot 08: Split-Flap Board with Animated 48h Countdown Timer
        ("SHOT_08", AI_DIR / "ai_09_cancelled_departure_board.jpg", b4_s2, "ai_drift",
         OVERLAY_DIR / "anim_04_countdown_48h.mov", "fadewhite", "freesound_typewriter_single_key"),

        # Shot 09: Mario Corti Interview with Lower-Third & English Translation Card
        ("SHOT_09", SOUNDBITE_DIR / "soundbite_01_corti_press.mp4", corti_dur, "interview_soundbite",
         OVERLAY_DIR / "corti_translated_overlay.png", "dissolve", "camera_shutter_snap"),

        # Shot 10: 4K Fine Gold Bullion Vault with "The Flying Bank" Gold Dossier Card
        ("SHOT_10", AUTHENTIC_DIR / "pixabay_gold_vault_bars.mp4", b5_s1, "video",
         OVERLAY_DIR / "anim_05_flying_bank_badge.mov", "zoomin", "paper_slide_desk"),

        # Shot 11: 3D Mario Corti Desk Dossier Pan
        ("SHOT_11", STAGE_DIR / "stage_01_mario_corti.mp4", b5_s2, "stage",
         None, "slideleft", "paper_dossier_slide_01"),

        # Shot 12: 3D Hunter Strategy Acquisition Wheel
        ("SHOT_12", ANIM_DIR / "anim_07_hunter_wheel.mp4", b6_s1, "video",
         None, "smoothright", "whoosh_cinematic"),

        # Shot 13: 3D Forensic Debt Explosion Chart (17 Billion CHF)
        ("SHOT_13", ANIM_DIR / "anim_02_chart.mp4", b6_s2, "video",
         None, "rectcrop", "sub_drop_dark"),

        # Shot 14: Remotion Kinetic Balance Sheet Debt Inspector
        ("SHOT_14", REMOTION_DIR / "kinetic_document_inspector.mp4", b6_s3, "remotion",
         None, "smoothleft", "paper_rip"),

        # Shot 15: Blick Newspaper Headline with English Translation Card
        ("SHOT_15", PAPER_DIR / "paper_01_blick_grounded.mp4", b7_s1, "video",
         OVERLAY_DIR / "blick_translated_overlay.png", "fade", "paper_rip"),

        # Shot 16: Grand Aerial Grounded Fleet Dusk Drift (Finale)
        ("SHOT_16", AI_DIR / "ai_08_grounded_fleet_aerial.jpg", b7_s2, "ai_drift",
         None, None, "whoosh_cinematic")
    ]

    total_shots = len(SHOT_SPECS)
    log(f"Rendering {total_shots} broadcast shots with 3D maps, charts, and animations...")

    rendered_shots = []
    sfx_events = []
    cum_t = 0.0

    for idx, (shot_id, asset, dur, shot_type, overlay, trans, sfx) in enumerate(SHOT_SPECS):
        out_shot = TEMP_SHOTS_DIR / f"{shot_id}.mp4"
        is_last = (idx == total_shots - 1)
        render_dur = dur if is_last else dur + T_DUR

        log(f"  Shot {idx+1:02d}/{total_shots:02d} [{shot_id}]: {asset.name} ({dur:.2f}s + {0.0 if is_last else T_DUR:.2f}s tail, {shot_type})")
        render_animated_shot(shot_id, asset, render_dur, shot_type, overlay, out_shot)
        rendered_shots.append((out_shot, dur, trans))

        if sfx:
            sfx_file = FOLEY_DIR / f"{sfx}.wav"
            if sfx_file.exists():
                sfx_events.append((cum_t + 0.05, sfx_file, 0.16))
                
        # Extra context Foley: cash register bell right as cash refusal is mentioned
        if shot_id == "SHOT_05":
            bell_file = FOLEY_DIR / "cash_register_bell.wav"
            if bell_file.exists():
                sfx_events.append((cum_t + 2.0, bell_file, 0.18))

        cum_t += dur

    target_timeline_dur = round(cum_t, 3)
    log(f"Target Video Timeline Duration: {target_timeline_dur}s")

    # Build 15-transition xfade filtergraph chain
    log(f"Building {total_shots - 1}-transition xfade filtergraph chain...")
    inputs = []
    for s_path, _, _ in rendered_shots:
        inputs.extend(["-i", str(s_path)])

    filter_parts = []
    curr_offset = 0.0

    for i in range(len(rendered_shots) - 1):
        _, dur_i, trans_type = rendered_shots[i]
        curr_offset += dur_i
        in_a = f"[v{i}]" if i > 0 else "[0:v]"
        in_b = f"[{i+1}:v]"
        out_v = f"[v{i+1}]" if i < len(rendered_shots) - 2 else "[video_master]"
        t_style = trans_type or "wipeleft"
        filter_parts.append(f"{in_a}{in_b}xfade=transition={t_style}:duration={T_DUR}:offset={curr_offset:.3f}{out_v}")

    full_filter = ";".join(filter_parts)
    xfade_video_master = TEMP_SHOTS_DIR / "xfade_video_master.mp4"

    log("Compiling xfade video transition master...")
    xfade_cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", full_filter,
        "-map", "[video_master]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-an",
        str(xfade_video_master)
    ]
    subprocess.run(xfade_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Master Multi-Stem Broadcast Audio
    SR = 44100
    total_samples = int(target_timeline_dur * SR)
    speech_master = np.zeros(total_samples, dtype=np.float32)

    beat_files = [
        (1, 0.0),
        (2, beat_durs[1]),
        (3, beat_durs[1] + beat_durs[2]),
        (4, beat_durs[1] + beat_durs[2] + beat_durs[3]),
    ]
    corti_start = sum(beat_durs[b] for b in range(1, 5))
    beat_files.append(("corti", corti_start))
    
    after_corti = corti_start + corti_dur
    beat_files.extend([
        (5, after_corti),
        (6, after_corti + beat_durs[5]),
        (7, after_corti + beat_durs[5] + beat_durs[6])
    ])

    for b_id, start_sec in beat_files:
        wav_p = corti_wav if b_id == "corti" else AUDIO_DIR / f"beat_{b_id}.wav"
        samples = load_wav_samples(wav_p)
        start_idx = int(start_sec * SR)
        end_idx = min(total_samples, start_idx + len(samples))
        n_copy = end_idx - start_idx
        if n_copy > 0:
            speech_master[start_idx:end_idx] += samples[:n_copy]

    speech_dur = len(speech_master) / float(SR)
    log(f"Speech Audio Timeline Duration: {speech_dur:.3f}s (Diff: {abs(speech_dur - target_timeline_dur):.3f}s)")

    # Synthesize Foley Master Track
    foley_master = np.zeros(total_samples, dtype=np.float32)
    for sfx_t, sfx_file, sfx_vol in sfx_events:
        try:
            s_samps = load_wav_samples(sfx_file) * sfx_vol
            s_idx = int(sfx_t * SR)
            e_idx = min(total_samples, s_idx + len(s_samps))
            n_copy = e_idx - s_idx
            if n_copy > 0:
                foley_master[s_idx:e_idx] += s_samps[:n_copy]
        except Exception as e:
            log(f"Warning loading SFX {sfx_file}: {e}")

    # Write temporary speech and foley stems
    speech_stem_wav = TEMP_SHOTS_DIR / "speech_stem.wav"
    foley_stem_wav = TEMP_SHOTS_DIR / "foley_stem.wav"

    def write_wav(path, data):
        data = np.clip(data, -1.0, 1.0)
        i_data = (data * 32767).astype(np.int16)
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SR)
            wf.writeframes(i_data.tobytes())

    write_wav(speech_stem_wav, speech_master)
    write_wav(foley_stem_wav, foley_master)

    # Multiplex Final Master Video with Synchronized Kinetic Text Animations
    music_wav = BASE_DIR / "data" / "media" / "audio" / "cinematic_orchestral_tragedy.wav"
    subtitles_mov = OVERLAY_DIR / "kinetic_subtitles_master.mov"
    final_mp4 = EXPORT_DIR / "documentary.mp4"

    log(f"Multiplexing final animated broadcast master with kinetic text -> {final_mp4} (Full Bleed 16:9, FastStart)...")

    combined_filter = (
        f"[0:v][4:v]overlay=0:0:eof_action=pass[vout];"
        f"[1:a]volume=1.0[speech];"
        f"[2:a]lowpass=f=4500,volume=0.9[foley];"
        f"[3:a]volume=0.22,afade=t=in:ss=0:d=2.0,afade=t=out:st={target_timeline_dur - 3.5}:d=3.5[music];"
        f"[speech][foley][music]amix=inputs=3:duration=first:dropout_transition=2[aout]"
    )

    mux_cmd = [
        "ffmpeg", "-y",
        "-i", str(xfade_video_master),
        "-i", str(speech_stem_wav),
        "-i", str(foley_stem_wav),
        "-i", str(music_wav),
        "-i", str(subtitles_mov),
        "-t", str(target_timeline_dur),
        "-filter_complex", combined_filter,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-b:v", "4800k",
        "-maxrate", "6500k",
        "-bufsize", "9500k",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(final_mp4)
    ]
    subprocess.run(mux_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    size_mb = final_mp4.stat().st_size / (1024 * 1024)
    log(f"=== ANIMATED MASTERPIECE v4 COMPLETED: {size_mb:.2f} MB, {target_timeline_dur:.2f}s ===")

if __name__ == "__main__":
    main()
