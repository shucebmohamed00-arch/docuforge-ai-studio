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
BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
EXPORT_DIR = BASE_DIR / "data" / "exports" / PROJ_ID
ANIM_DIR = BASE_DIR / "data" / "media" / "animations" / PROJ_ID
AUDIO_DIR = BASE_DIR / "data" / "media" / "audio" / PROJ_ID
CLIPS_DIR = BASE_DIR / "data" / "media" / "authentic_clips"

EXPORT_DIR.mkdir(parents=True, exist_ok=True)
ANIM_DIR.mkdir(parents=True, exist_ok=True)

# 64 100% Unique Beat Mapping (58 Authentic Archival Clips + 6 Documentary Animations)
BEAT_ASSETS = {
    1:  ("authentic", CLIPS_DIR / "srf_clip_01.mp4", "ZÜRICH KLOTEN AIRPORT", "OCTOBER 2, 2001 - 12:30 PM"),
    2:  ("authentic", CLIPS_DIR / "srf_clip_02.mp4", "AIRBUS A320 TAXIWAY", "KEROSENE REFUSED BY SUPPLIERS"),
    3:  ("authentic", CLIPS_DIR / "srf_clip_03.mp4", "AIRPORT APRON", "CREDIT LINES TERMINATED"),
    4:  ("authentic", CLIPS_DIR / "srf_clip_04.mp4", "ZÜRICH TARMAC", "SWISSAIR FLEET GROUNDED GLOBALLY"),
    5:  ("anim",      ANIM_DIR / "anim_02_chart.mp4", "FINANCIAL DOSSIER", "THE FLYING BANK: 400 CHF TO 14 CHF"),
    6:  ("authentic", CLIPS_DIR / "srf_clip_05.mp4", "SAIRGROUP BOARDROOM", "INSTITUTIONAL BLIND SPOTS"),
    7:  ("authentic", CLIPS_DIR / "srf_clip_06.mp4", "PARADEPLATZ ZÜRICH", "SWISS BANKING CARTEL WITHDRAWAL"),
    8:  ("authentic", CLIPS_DIR / "srf_clip_07.mp4", "NATIONAL CARRIER", "48-HOUR LIQUIDATION"),
    9:  ("authentic", CLIPS_DIR / "kloten_clip_01.mp4", "SWISSAIR MD-11", "HB-IWE: 'THE FLYING BANK' IN FLIGHT"),
    10: ("authentic", CLIPS_DIR / "kloten_clip_02.mp4", "SWISS GLOBAL FLEET", "BALANCED SUBSIDIARY EMPIRE"),
    11: ("authentic", CLIPS_DIR / "kloten_clip_03.mp4", "ORIGINS OF COLLAPSE", "SEVEN YEARS EARLIER: 1994"),
    12: ("anim",      ANIM_DIR / "anim_01_map.mp4", "EUROPEAN AIRSPACE", "1992 REFERENDUM: SWISS ISOLATION"),
    13: ("authentic", CLIPS_DIR / "srf_clip_08.mp4", "DECEMBER 1992", "SWISS CITIZENS REJECT EEA ENTRY"),
    14: ("authentic", CLIPS_DIR / "srf_clip_09.mp4", "SWISSAIR HEADQUARTERS", "STRATEGIC NIGHTMARE"),
    15: ("authentic", CLIPS_DIR / "kloten_clip_04.mp4", "EUROPEAN DEREGULATION", "MEGA-CARRIERS: BA & LUFTHANSA"),
    16: ("authentic", CLIPS_DIR / "kloten_clip_05.mp4", "RESTRICTED AIRSPACE", "DOMESTIC CABOTAGE RIGHTS DENIED"),
    17: ("authentic", CLIPS_DIR / "srf_clip_10.mp4", "STRATEGIC CROSSROADS", "THE FEAR OF SLOW STRANGULATION"),
    18: ("authentic", CLIPS_DIR / "srf_clip_11.mp4", "PHILIPPE BRUGGISSER", "THE NEW ARCHITECT: 1996"),
    19: ("authentic", CLIPS_DIR / "srf_clip_12.mp4", "EXECUTIVE MANDATE", "EXPANSION BY ANY MEANS NECESSARY"),
    20: ("authentic", CLIPS_DIR / "srf_clip_13.mp4", "MCKINSEY & COMPANY", "ARCHITECTS OF THE HUNTER STRATEGY"),
    21: ("authentic", CLIPS_DIR / "srf_clip_14.mp4", "OFFENSIVE EXPANSION", "BUYING FOREIGN AIRLINES"),
    22: ("authentic", CLIPS_DIR / "srf_clip_15.mp4", "BOARD APPROVAL", "TERRIFIED OF IRRELEVANCE"),
    23: ("anim",      ANIM_DIR / "anim_07_hunter_wheel.mp4", "THE HUNTER STRATEGY", "SABENA - AOM - LTU - AIR LIBERTÉ"),
    24: ("authentic", CLIPS_DIR / "srf_clip_16.mp4", "BILLION DOLLAR SPREE", "AGGRESSIVE STAKE ACQUISITIONS"),
    25: ("authentic", CLIPS_DIR / "rsi_clip_01.mp4", "SABENA ACQUISITION", "49.5% STAKE IN LOSS-MAKING CARRIER"),
    26: ("authentic", CLIPS_DIR / "rsi_clip_02.mp4", "EUROPEAN REGULATIONS", "49% FOREIGN OWNERSHIP CEILING"),
    27: ("authentic", CLIPS_DIR / "rsi_clip_03.mp4", "CASH BLEED", "GUARANTEEING DEBTS WITHOUT CONTROL"),
    28: ("authentic", CLIPS_DIR / "rsi_clip_04.mp4", "OPERATIONAL TRAP", "ALL OF THE RISK, NONE OF THE POWER"),
    29: ("authentic", CLIPS_DIR / "srf_clip_17.mp4", "EARLY 2001", "THE CASH INCINERATOR EXPOSED"),
    30: ("authentic", CLIPS_DIR / "srf_clip_18.mp4", "DAILY LOSSES", "3,000,000 CHF LOST EVERY 24 HOURS"),
    31: ("authentic", CLIPS_DIR / "srf_clip_19.mp4", "JANUARY 2001", "BOARDROOM PANIC & EMERGENCY FIRING"),
    32: ("authentic", CLIPS_DIR / "srf_clip_20.mp4", "MARIO CORTI", "CFO OF NESTLÉ TAKES COMMAND"),
    33: ("authentic", CLIPS_DIR / "srf_clip_21.mp4", "CORTI AUDIT", "EXPECTING A DIRE SITUATION"),
    34: ("anim",      ANIM_DIR / "anim_04_document.mp4", "FORENSIC AUDIT", "OFF-BALANCE SHEET DEBT: 4.8B CHF"),
    35: ("authentic", CLIPS_DIR / "rsi_clip_05.mp4", "HIDDEN LIABILITIES", "SAIRGROUP LEGALLY BOUND TO CREDITORS"),
    36: ("authentic", CLIPS_DIR / "rsi_clip_06.mp4", "SEPTEMBER 11, 2001", "GLOBAL AVIATION DEMAND COLLAPSES"),
    37: ("authentic", CLIPS_DIR / "srf_clip_22.mp4", "PARADEPLATZ TOWER", "DESPERATE PLEA TO UBS & CREDIT SUISSE"),
    38: ("authentic", CLIPS_DIR / "srf_clip_23.mp4", "HOTEL DOLDER", "SECRET BAILOUT: PROJECT PHOENIX"),
    39: ("authentic", CLIPS_DIR / "kloten_clip_06.mp4", "CROSSAIR RESTRUCTURING", "REGIONAL SUBSIDIARY SAVED"),
    40: ("authentic", CLIPS_DIR / "kloten_clip_07.mp4", "ASSET TRANSFER", "PARENT DEBT TRAPPED IN SAIRGROUP"),
    41: ("authentic", CLIPS_DIR / "srf_clip_24.mp4", "THE INTERIM PROMISE", "KEEPING PLANES FLYING UNTIL OCT 28"),
    42: ("authentic", CLIPS_DIR / "srf_clip_25.mp4", "THE BANK TRAP", "INTRADAY LIQUIDITY CANCELLED"),
    43: ("anim",      ANIM_DIR / "anim_03_kinetic_type.mp4", "THE FINAL HOURS", "OCTOBER 2, 2001 - ALL FLIGHTS STOP"),
    44: ("authentic", CLIPS_DIR / "rsi_clip_07.mp4", "MORNING OF OCT 2", "THE TRAP SNAPS SHUT"),
    45: ("authentic", CLIPS_DIR / "rsi_clip_08.mp4", "UBS TRANSFER", "EXPECTED 250 MILLION CHF PAYMENT"),
    46: ("authentic", CLIPS_DIR / "rsi_clip_09.mp4", "EMPTY ACCOUNTS", "PAYMENT WITHHELD BY BANK"),
    47: ("authentic", CLIPS_DIR / "rsi_clip_10.mp4", "PARADEPLATZ REFUSAL", "TECHNICAL & LEGAL CONDITIONS CITED"),
    48: ("anim",      ANIM_DIR / "anim_06_hud.mp4", "ZÜRICH KLOTEN HUD", "14.5M CHF LEFT - KEROSENE DENIED"),
    49: ("authentic", CLIPS_DIR / "rsi_clip_11.mp4", "FLIGHT 157", "FUEL HOSE DISCONNECTED AT GATE"),
    50: ("authentic", CLIPS_DIR / "srf_clip_26.mp4", "THE ULTIMATUM", "MARIO CORTI OUT OF CASH"),
    51: ("authentic", CLIPS_DIR / "srf_clip_27.mp4", "THE EXECUTIVE ORDER", "SHUT DOWN ENTIRE GLOBAL FLEET"),
    52: ("authentic", CLIPS_DIR / "rsi_clip_12.mp4", "OCTOBER 2, 2001", "THE SWISS CROSS GROUNDED"),
    53: ("authentic", CLIPS_DIR / "srf_clip_28.mp4", "SWISS NATIONAL GRIEF", "SHOCK ACROSS THE CONFEDERATION"),
    54: ("authentic", CLIPS_DIR / "srf_clip_29.mp4", "PARADEPLATZ PROTESTS", "'SWISSAIR ASSASSINS' OUTSIDE UBS"),
    55: ("authentic", CLIPS_DIR / "rsi_clip_13.mp4", "STRANDED PASSENGERS", "38,000 TRAVELERS STRANDED GLOBALLY"),
    56: ("authentic", CLIPS_DIR / "srf_clip_30.mp4", "FEDERAL PARLIAMENT", "450M CHF EMERGENCY TAXPAYER RESCUE"),
    57: ("authentic", CLIPS_DIR / "rsi_clip_14.mp4", "CRIMINAL INQUIRY", "PROSECUTORS RAID EXECUTIVE SUITES"),
    58: ("authentic", CLIPS_DIR / "rsi_clip_15.mp4", "THE BULACH TRIAL", "19 BOARD MEMBERS IN COURT"),
    59: ("authentic", CLIPS_DIR / "rsi_clip_16.mp4", "REBIRTH INTO SWISS", "LUFTHANSA ACQUIRES CARRIER IN 2005"),
    60: ("authentic", CLIPS_DIR / "kloten_clip_08.mp4", "HISTORICAL VERDICT", "THE PERILS OF EXECUTIVE HUBRIS"),
    61: ("authentic", CLIPS_DIR / "kloten_clip_09.mp4", "ECONOMIC GRAVITY", "FINANCIAL ENGINEERING DEFEATED"),
    62: ("authentic", CLIPS_DIR / "rsi_clip_17.mp4", "INSTITUTIONAL ROT", "BLINDED BY SACRED REPUTATION"),
    63: ("authentic", CLIPS_DIR / "rsi_clip_18.mp4", "COLD CALCULATION", "A LEGACY SACRIFICED"),
    64: ("authentic", CLIPS_DIR / "kloten_clip_10.mp4", "EPILOGUE", "THE LESSON OF THE FLYING BANK")
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

def render_broadcast_beat(src_video: Path, out_path: Path, dur: float, transition_type: str, chyron_title: str, chyron_sub: str):
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
        fade_str = f"fade=t=in:st=0:d={d_in},fade=t=out:st={st_out}:d={d_out}"

    # Sleek lower-third chyron overlay
    safe_title = chyron_title.replace("'", "").replace(":", " -").replace("Ü", "U").replace("%", " PERCENT")
    safe_sub = chyron_sub.replace("'", "").replace(":", " -").replace("Ü", "U").replace("É", "E").replace("%", " PERCENT")

    font_bold = "C\\:/Windows/Fonts/arialbd.ttf"
    font_reg = "C\\:/Windows/Fonts/arial.ttf"

    draw_box = f"drawbox=x=60:y=890:w=900:h=90:color=black@0.75:t=fill"
    draw_bar = f"drawbox=x=60:y=890:w=8:h=90:color=0xD4AF37@1.0:t=fill"
    draw_txt1 = f"drawtext=fontfile='{font_bold}':text='{safe_title}':x=85:y=912:fontsize=28:fontcolor=white:box=0"
    draw_txt2 = f"drawtext=fontfile='{font_reg}':text='{safe_sub}':x=85:y=948:fontsize=19:fontcolor=0xD4AF37:box=0"

    chyron_filter = f"{draw_box},{draw_bar},{draw_txt1},{draw_txt2}"

    vf = (
        f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,"
        f"eq=contrast=1.08:brightness=-0.02:saturation=1.05,"
        f"{chyron_filter},{fade_str}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", str(src_video),
        "-t", str(round(dur, 2)),
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-threads", "4",
        str(out_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def compose_cinematic_music_score(total_sec: float, out_wav: Path):
    SR = 44100
    total_samples = int(total_sec * SR)
    t = np.linspace(0, total_sec, total_samples, endpoint=False)

    log(f"Composing {total_sec:.1f}s multi-instrument cinematic tension score...")

    # 1. Deep Sub-bass & Drone
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.12 * t)
    sub = (0.32 * np.sin(2 * np.pi * 32.7 * t) + 0.20 * np.sin(2 * np.pi * 65.4 * t)) * (0.65 + 0.35 * lfo)

    # 2. String Chord Progression (C min -> Ab maj -> F min -> G sus)
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
    tick_phase = (t * 2.0) % 1.0
    tick_env = np.exp(-tick_phase * 65.0)
    tick = np.sin(2 * np.pi * 2200.0 * t) * tick_env * 0.09

    # 4. Low Heartbeat Sub-kick
    hb_phase = (t * 1.0) % 1.0
    hb_env = np.exp(-hb_phase * 16.0)
    heartbeat = np.sin(2 * np.pi * 48.0 * t) * hb_env * 0.26

    # 5. Tension Riser Sweeps every 32 seconds
    sweep_phase = (t % 32.0) / 32.0
    sweep_freq = 80.0 + 380.0 * (sweep_phase ** 2)
    sweep_env = sweep_phase ** 3
    riser = np.sin(2 * np.pi * sweep_freq * t) * sweep_env * 0.12

    mix = sub + strings + tick + heartbeat + riser
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = (mix / peak) * 0.82

    int_data = (mix * 32767).astype(np.int16)
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(int_data.tobytes())

    log(f"Soundtrack composition ready! ({total_sec:.2f}s)")

def main():
    log("=== COMMENCING ULTIMATE AUTHENTIC MASTER ASSEMBLY ===")

    # 1. Cold Open Hook (13.5s)
    cold_mp4 = ANIM_DIR / "cold_open.mp4"
    cold_wav = AUDIO_DIR / "cold_open.wav"
    video_files = [str(cold_mp4)]
    audio_files = [str(cold_wav)]

    # 2. Render all 64 Beats
    log("Rendering all 64 unique beats with authentic archival footage, 6 animations, and sleek chyrons...")
    for idx in range(1, 65):
        audio_path = AUDIO_DIR / f"beat_{idx}.wav"
        clip_path = ANIM_DIR / f"cinematic_clip_{idx}.mp4"

        dur = get_audio_duration(audio_path)
        tr_type = MAJOR_TRANSITIONS.get(idx, "crossfade")
        asset_type, src_path, chyron_title, chyron_sub = BEAT_ASSETS[idx]

        if not (clip_path.exists() and clip_path.stat().st_size > 100000 and (time.time() - clip_path.stat().st_mtime) < 600):
            render_broadcast_beat(src_path, clip_path, dur, tr_type, chyron_title, chyron_sub)

        video_files.append(str(clip_path))
        audio_files.append(str(audio_path))

        if idx % 10 == 0 or idx == 64:
            log(f"Processed {idx}/64 timeline beats...")

    # 3. Concatenate Full Continuous Audio Stream
    log("Building 500-second voiceover narration bed...")
    total_samples = 0
    narration_frames = bytearray()
    for af in audio_files:
        with wave.open(af, "rb") as wf:
            narration_frames.extend(wf.readframes(wf.getnframes()))

    full_voiceover_wav = EXPORT_DIR / "full_voiceover_master.wav"
    with wave.open(str(full_voiceover_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(bytes(narration_frames))

    total_duration = len(narration_frames) / (44100 * 2)
    log(f"Total Master Timeline Duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")

    # 4. Compose Continuous Cinematic Soundtrack
    soundtrack_wav = EXPORT_DIR / "cinematic_soundtrack.wav"
    compose_cinematic_music_score(total_duration, soundtrack_wav)

    # 5. Dynamically Mix Voiceover & Soundtrack
    log("Dynamically mixing Voiceover (-14 LUFS) and Tension Soundtrack (-18 dB bed)...")
    mixed_audio_wav = EXPORT_DIR / "mixed_final_audio.wav"
    mix_cmd = [
        "ffmpeg", "-y",
        "-i", str(full_voiceover_wav),
        "-i", str(soundtrack_wav),
        "-filter_complex",
        "[0:a]volume=1.0[voice];[1:a]volume=0.22[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-14:LRA=9:TP=-1[outa]",
        "-map", "[outa]",
        "-c:a", "pcm_s16le",
        str(mixed_audio_wav)
    ]
    subprocess.run(mix_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 6. Build Video Concat Manifest
    v_concat_manifest = EXPORT_DIR / "v_concat.txt"
    with open(v_concat_manifest, "w", encoding="utf-8") as f:
        for vf in video_files:
            clean_path = vf.replace("\\", "/")
            f.write(f"file '{clean_path}'\n")

    # 7. Final Master Render with Faststart
    master_mp4 = EXPORT_DIR / "documentary.mp4"
    log("Multiplexing master video with libx264 High Profile and Web Faststart...")
    cmd_final = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(v_concat_manifest),
        "-i", str(mixed_audio_wav),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-profile:v", "high",
        "-level", "4.0",
        "-crf", "21",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(master_mp4)
    ]
    subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    log(f"Master Documentary rendered successfully! ({master_mp4.stat().st_size / (1024*1024):.2f} MB)")

    # 8. Create Distribution ZIP
    pkg_zip = EXPORT_DIR / "docuforge_package.zip"
    log("Packaging docuforge_package.zip...")
    with zipfile.ZipFile(pkg_zip, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.write(master_mp4, arcname="documentary.mp4")
        srt_file = EXPORT_DIR / "subtitles.srt"
        if srt_file.exists():
            zf.write(srt_file, arcname="subtitles.srt")
        for thumb in EXPORT_DIR.glob("thumbnail*.jpg"):
            zf.write(thumb, arcname=thumb.name)

    log(f"Release package ready: {pkg_zip.name} ({pkg_zip.stat().st_size / (1024*1024):.2f} MB)")
    log("=== ULTIMATE DOCUMENTARY PIPELINE COMPLETE ===")

if __name__ == "__main__":
    main()
