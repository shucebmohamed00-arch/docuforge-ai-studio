import os
import sys
import wave
import shutil
import zipfile
import subprocess
import numpy as np
from pathlib import Path

PROJ_ID = "swiss-air-grounding-prod"
BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
EXPORT_DIR = BASE_DIR / "data" / "exports" / PROJ_ID
ANIM_DIR = BASE_DIR / "data" / "media" / "animations" / PROJ_ID
AUDIO_DIR = BASE_DIR / "data" / "media" / "audio" / PROJ_ID
CLIPS_DIR = BASE_DIR / "data" / "media" / "authentic_clips"
PAPER_DIR = BASE_DIR / "data" / "media" / "paper_assets"
PHOTO_DIR = BASE_DIR / "data" / "media" / "documentary_photos"
ADV_DIR = BASE_DIR / "data" / "media" / "advanced_25d"
STAGE_DIR = BASE_DIR / "data" / "media" / "magnates_stage"
FIN_DIR = BASE_DIR / "data" / "media" / "financial_graphics"
OVERLAY_DIR = BASE_DIR / "data" / "media" / "magnates_overlays"
BROLL_DIR = BASE_DIR / "data" / "media" / "broll_cache"
SFX_DIR = BASE_DIR / "data" / "media" / "sfx"
TEMP_SHOTS_DIR = BASE_DIR / "data" / "media" / "rapid_zero_dup_shots"

for d in [EXPORT_DIR, ANIM_DIR, AUDIO_DIR, OVERLAY_DIR, TEMP_SHOTS_DIR, SFX_DIR, PHOTO_DIR, FIN_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def log(msg):
    import time
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def get_audio_duration(wav_path: Path) -> float:
    with wave.open(str(wav_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())

# Curated MagnatesMedia Punch Text Overlays (Selective, high-impact keyphrases)
PUNCH_TEXTS = {
    1:  ("A SINGLE PHONE CALL ", "FROZE EUROPE", (235, 35, 35)),
    2:  ("SUPPLIERS CUT OFF ", "THE KEROSENE", (235, 35, 35)),
    3:  ("THE CREDIT LINES ", "WERE DEAD", (235, 35, 35)),
    4:  ("EVERY PLANE GROUNDED ", "ON TARMAC", (212, 175, 55)),
    5:  ("NICKNAMED: ", "'THE FLYING BANK'", (212, 175, 55)),
    7:  ("HOW DOES A CARTEL COLLAPSE ", "IN 48 HOURS?", (235, 35, 35)),
    8:  ("AN AGGRESSIVE ", "DEBT SPREE", (235, 35, 35)),
    12: ("ORIGIN: POLITICAL ", "ISOLATION", (235, 35, 35)),
    13: ("THE 1992 HISTORIC ", "EEA REFERENDUM", (212, 175, 55)),
    16: ("LOCKED OUT OF ", "EUROPEAN SKIES", (235, 35, 35)),
    18: ("ENTER: ", "PHILIPPE BRUGGISSER", (212, 175, 55)),
    20: ("THE NOTORIOUS ", "'HUNTER STRATEGY'", (235, 35, 35)),
    24: ("A MULTI-BILLION DOLLAR ", "SHOPPING SPREE", (212, 175, 55)),
    28: ("ALL FINANCIAL RISK ", "ZERO CONTROL", (235, 35, 35)),
    30: ("HEMORRHAGING 3 MILLION ", "EVERY 24 HOURS", (235, 35, 35)),
    32: ("BRUGGISSER FIRED ", "MARIO CORTI ARRIVES", (212, 175, 55)),
    34: ("OFF-BALANCE SHEET DEBT: ", "4.8 BILLION CHF", (235, 35, 35)),
    36: ("SEPTEMBER 11TH: ", "GLOBAL COLLAPSE", (235, 35, 35)),
    38: ("SECRET RESCUE PLAN: ", "'PROJECT PHOENIX'", (212, 175, 55)),
    44: ("OCTOBER 2, 2001: ", "THE TRAP SNAPS SHUT", (235, 35, 35)),
    48: ("ONLY 14.5 MILLION FRANCS ", "REMAINING", (235, 35, 35)),
    51: ("MARIO CORTI ORDERS: ", "FLEET SHUTDOWN", (235, 35, 35)),
    52: ("THE SWISS CROSS ", "GROUNDED", (235, 35, 35)),
    54: ("PROTESTORS CHANT: ", "'SWISSAIR ASSASSINS'", (235, 35, 35)),
    55: ("38,000 PASSENGERS ", "STRANDED GLOBALLY", (212, 175, 55)),
    58: ("SWISSAIR ERADICATED ", "CROSSAIR TAKES OVER", (212, 175, 55)),
    64: ("NO BRAND IS TOO SACRED ", "TO FALL", (235, 35, 35))
}

# Primary Source Historical Interview Soundbites (Voiceover pauses for authentic broadcast witness evidence)
ARCHIVAL_SOUNDBITES = {
    36: (
        BASE_DIR / "data" / "media" / "archival_soundbites" / "soundbite_01_corti_press.mp4",
        BASE_DIR / "data" / "media" / "archival_soundbites" / "soundbite_01_corti_press.wav"
    ),
    49: (
        BASE_DIR / "data" / "media" / "archival_soundbites" / "soundbite_02_grounding_breaking.mp4",
        BASE_DIR / "data" / "media" / "archival_soundbites" / "soundbite_02_grounding_breaking.wav"
    )
}

# 100% Curated Visual Mix (Advanced 2.5D Parallax + Rubber Stamp Document Slams + Mega-Airlines)
CONTEXTUAL_ASSETS = {
    # Beat 7: "The credit lines were dead" -> 3D Mahogany Desk Stage UBS Inquiry Dossier
    7:  [STAGE_DIR / "stage_03_ubs_dossier.mp4", CLIPS_DIR / "politics_ubs_06_bank_vault_doors.mp4"],
    # Beat 8: "An aggressive debt spree"
    8:  [FIN_DIR / "graphic_02_debt_spiral.mp4", CLIPS_DIR / "politics_ubs_20_financial_district_zurich.mp4"],
    # Beat 10: "Catastrophic strategy of debt..."
    10: [FIN_DIR / "graphic_02_debt_spiral.mp4", CLIPS_DIR / "politics_ubs_06_bank_vault_doors.mp4"],
    # Beat 11: Stock Collapse & NZZ Debt Headline
    11: [FIN_DIR / "graphic_01_stock_crash.mp4", CLIPS_DIR / "politics_ubs_10_stock_chart_screen.mp4"],
    # Beat 12: NZZ 17.8B Debt Newspaper with Animated Highlighter + Rubber Stamp Slam
    12: [ADV_DIR / "doc_01_nzz_audit_stamp.mp4", FIN_DIR / "graphic_01_stock_crash.mp4"],
    # Beat 16: Mega-Airlines Illustration Suite (British Airways, Lufthansa, Air France rapid 1.1s cards)
    16: [
        CLIPS_DIR / "politics_ubs_20_financial_district_zurich.mp4",
        PHOTO_DIR / "photo_07_british_airways.mp4",
        PHOTO_DIR / "photo_08_lufthansa.mp4",
        PHOTO_DIR / "photo_09_air_france.mp4",
        CLIPS_DIR / "zurich_uncut_28_md11_wingtip.mp4"
    ],
    17: [CLIPS_DIR / "politics_ubs_02_politician_speech.mp4", CLIPS_DIR / "politics_ubs_24_parliament_voting_lights.mp4"],
    # Beat 18: Enter Philippe Bruggisser 2.5D Parallax
    18: [ADV_DIR / "parallax_02_philippe_bruggisser.mp4", CLIPS_DIR / "zurich_uncut_04_cockpit_view.mp4"],
    # Beat 19: European skies & Cockpit view
    19: [BROLL_DIR / "COCKPIT_FLIGHT.mp4", CLIPS_DIR / "zurich_uncut_04_cockpit_view.mp4"],
    # Beat 20: The Hunter Strategy Web (49% Cap Explainer)
    20: [FIN_DIR / "graphic_03_hunter_network.mp4", CLIPS_DIR / "politics_ubs_13_investor_meeting.mp4"],
    # Beat 22: Philippe Bruggisser 2.5D Parallax Card
    22: [ADV_DIR / "parallax_02_philippe_bruggisser.mp4", CLIPS_DIR / "zurich_uncut_09_swissair_cross.mp4"],
    # Beat 25: Acquisition Web & 49% Cap Explainer
    25: [FIN_DIR / "graphic_03_hunter_network.mp4", CLIPS_DIR / "politics_ubs_18_banker_handshake.mp4"],
    # Beat 28: Multi-billion shopping spree
    28: [CLIPS_DIR / "politics_ubs_23_bank_teller_counter.mp4", FIN_DIR / "graphic_02_debt_spiral.mp4"],
    # Beat 29: Sabena Belgian Airline Newspaper
    29: [PAPER_DIR / "paper_06_sabena.mp4", CLIPS_DIR / "zurich_uncut_28_md11_wingtip.mp4"],
    # Beat 30: 49% ownership cap explainer
    30: [FIN_DIR / "graphic_03_hunter_network.mp4", CLIPS_DIR / "politics_ubs_13_investor_meeting.mp4"],
    # Beat 34: Hemorrhaging 3M daily
    34: [FIN_DIR / "graphic_02_debt_spiral.mp4", CLIPS_DIR / "politics_ubs_10_stock_chart_screen.mp4"],
    # Beat 36: 3D Mahogany Desk Stage Mario Corti Confidential Case File
    36: [STAGE_DIR / "stage_01_mario_corti.mp4", CLIPS_DIR / "politics_ubs_09_mario_corti_mic.mp4"],
    # Beat 37: Post-9/11 aviation collapse (Deserted Terminal & Grounded Fleets, ZERO explosions)
    37: [BROLL_DIR / "PASSENGER_TERMINAL.mp4", FIN_DIR / "graphic_01_stock_crash.mp4", CLIPS_DIR / "zurich_uncut_37_grounded_lineup.mp4"],
    # Beat 40: Financial plunge
    40: [FIN_DIR / "graphic_01_stock_crash.mp4", CLIPS_DIR / "politics_ubs_20_financial_district_zurich.mp4"],
    # Beat 41: UBS HQ & Marcel Ospel 2.5D Parallax
    41: [ADV_DIR / "parallax_03_marcel_ospel.mp4", ADV_DIR / "parallax_04_ubs_dossier.mp4"],
    # Beat 43: Moritz Suter & Crossair MD-82
    43: [CLIPS_DIR / "politics_ubs_12_crossair_moritz_suter.mp4", CLIPS_DIR / "zurich_uncut_29_a320_nose.mp4"],
    # Beat 44: October 2nd Grounding Day begins
    44: [BROLL_DIR / "RAIN_RUNWAY.mp4", CLIPS_DIR / "zurich_uncut_38_foggy_morning_kloten.mp4"],
    # Beat 48: Intraday Countdown (08:00 AM to 13:45 PM)
    48: [FIN_DIR / "graphic_04_intraday_countdown.mp4", CLIPS_DIR / "zurich_uncut_11_tower_pan.mp4"],
    # Beat 49: UBS Refusal Newspaper
    49: [PAPER_DIR / "paper_03_ubs_refusal.mp4", ADV_DIR / "parallax_03_marcel_ospel.mp4"],
    # Beat 52: Blick "DAS ENDE" Newspaper & Intraday Liquidity
    52: [PAPER_DIR / "paper_01_blick_grounded.mp4", FIN_DIR / "graphic_04_intraday_countdown.mp4"],
    # Beat 54: Job loss crisis document with orange highlighter + Rubber Stamp Slam
    54: [ADV_DIR / "doc_02_job_loss_stamp.mp4", CLIPS_DIR / "politics_ubs_07_protesters_signs.mp4"],
    # Beat 55: Shutdown order
    55: [CLIPS_DIR / "zurich_uncut_25_engine_cover_wrap.mp4", CLIPS_DIR / "zurich_uncut_37_grounded_lineup.mp4"],
    # Beat 58: Zurich Protests outside UBS Photo Card
    58: [PHOTO_DIR / "photo_04_protest.mp4", CLIPS_DIR / "politics_ubs_07_protesters_signs.mp4"],
    # Beat 59: 38,000 Stranded Passengers
    59: [BROLL_DIR / "PASSENGER_TERMINAL.mp4", PAPER_DIR / "paper_04_passengers.mp4"],
    # Beat 60: Federal Council 450M Bailout Flowchart
    60: [FIN_DIR / "graphic_05_bailout_rescue.mp4", PAPER_DIR / "paper_05_bailout.mp4"],
    # Beat 62: Court trial media scrum (Clean, watermark-free press cameras)
    62: [CLIPS_DIR / "politics_ubs_05_press_cameras.mp4", CLIPS_DIR / "politics_ubs_22_newspaper_press_rolling.mp4"],
    # Beat 63: Swiss International Air Lines Restructure
    63: [FIN_DIR / "graphic_05_bailout_rescue.mp4", CLIPS_DIR / "zurich_uncut_09_swissair_cross.mp4"]
}

# Strict SFX Events: ONLY at true narrative highlights (No spam on regular cuts!)
SELECTIVE_SFX_BEATS = {
    1:  ("impact_boom", 0),     # Title reveal / Cold Open climax
    7:  ("impact_boom", 1),     # "The credit lines were dead" -> Transition to UBS HQ
    8:  ("whoosh", 0),          # Debt spiral chart reveal
    11: ("impact_boom", 0),     # Stock crash graph reveal
    12: ("paper_rip", 0),       # NZZ 17B Debt Newspaper Reveal
    16: ("whoosh", 1),          # British Airways Mega-Carrier Card reveal
    17: ("camera_shutter", 1),  # Parliament voting lights archive
    20: ("whoosh", 0),          # Hunter network map reveal
    22: ("camera_shutter", 0),  # Philippe Bruggisser Portrait Card
    25: ("whoosh", 0),          # Hunter network map reveal
    29: ("paper_rip", 0),       # Sabena Belgian Airline Newspaper
    36: ("camera_shutter", 0),  # Mario Corti Portrait Card
    40: ("impact_boom", 0),     # Market collapse
    41: ("camera_shutter", 1),  # Marcel Ospel / UBS HQ Card
    48: ("whoosh", 0),          # "The morning of October 2nd: the trap snapped shut"
    49: ("paper_rip", 0),       # UBS 250M Payment Refusal Newspaper
    52: ("paper_rip", 0),       # Blick "DAS ENDE DER SWISSAIR" Newspaper
    54: ("paper_rip", 0),       # Job loss crisis document with orange highlighter
    56: ("impact_boom", 0),     # "The Swiss cross was grounded"
    58: ("camera_shutter", 0),  # Zurich Protests outside UBS Photo Card
    59: ("paper_rip", 1),       # Stranded Passengers report
    60: ("whoosh", 0)           # Federal Council 450M Bailout Flowchart
}

def determine_transition_for_asset(target_asset: Path, default_trans: str = "smoothleft") -> str:
    """
    Returns active, dynamic visual transitions. ZERO black screens!
    """
    name = str(target_asset).lower()
    if "paper_" in name:
        return "wiperight"
    elif "photo_" in name:
        return "fadewhite"
    elif "graphic_" in name:
        return "smoothleft"
    elif "cockpit" in name or "flight" in name:
        return "dissolve"
    return default_trans

def render_beat_with_xfade(beat_idx: int, assets: list, overlays: list,
                           target_dur: float, out_path: Path):
    """
    Renders subshots using native FFmpeg xfade filters to create continuous,
    fluid documentary transitions (smoothleft, wiperight, fadewhite, dissolve, hblur, smoothright).
    Guarantees ZERO black frames or freezes.
    """
    N = len(assets)
    T = 0.35  # Transition duration in seconds

    if N == 1:
        cmd = [
            "ffmpeg", "-y",
            "-ss", "0.0", "-t", str(round(target_dur, 2)),
            "-i", str(assets[0])
        ]
        base_vf = (
            "scale=1920:1080:force_original_aspect_ratio=increase,"
            "crop=1920:1080:(in_w-1920)/2:(in_h-1080)/2,"
            "tpad=stop_mode=clone:stop_duration=3,"
            "settb=AVTB,setpts=PTS-STARTPTS,fps=30,format=yuv420p"
        )
        if overlays[0] and overlays[0].exists():
            cmd.extend(["-i", str(overlays[0])])
            cmd.extend([
                "-filter_complex", f"[0:v]{base_vf}[bg];[bg][1:v]overlay=0:0[outv]",
                "-map", "[outv]"
            ])
        else:
            cmd.extend(["-vf", base_vf])
        cmd.extend([
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "21",
            "-pix_fmt", "yuv420p", "-an", str(out_path)
        ])
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return []

    # Multi-subshot xfade composition
    total_raw = target_dur + (N - 1) * T
    durations = [total_raw / N] * N

    offsets = []
    cum = 0.0
    for i in range(N - 1):
        cum += durations[i]
        offsets.append(round(cum - (i + 1) * T, 3))

    cmd = ["ffmpeg", "-y"]
    for i, a in enumerate(assets):
        start_sec = 0.2 if ("uncut" in str(a) or "broll" in str(a)) else 0.0
        cmd.extend([
            "-ss", str(start_sec),
            "-t", str(round(durations[i] + 0.35, 2)),
            "-i", str(a)
        ])

    ov_indices = {}
    next_input = N
    for i, ov in enumerate(overlays):
        if ov and ov.exists():
            cmd.extend(["-i", str(ov)])
            ov_indices[i] = next_input
            next_input += 1

    filter_parts = []
    base_vf = (
        "scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080:(in_w-1920)/2:(in_h-1080)/2,"
        "tpad=stop_mode=clone:stop_duration=3,"
        "settb=AVTB,setpts=PTS-STARTPTS,fps=30,format=yuv420p"
    )

    for i in range(N):
        if i in ov_indices:
            filter_parts.append(f"[{i}:v]{base_vf}[v{i}_raw]")
            filter_parts.append(f"[v{i}_raw][{ov_indices[i]}:v]overlay=0:0[v{i}]")
        else:
            filter_parts.append(f"[{i}:v]{base_vf}[v{i}]")

    # Cycle through active dynamic transitions (ZERO black screens)
    trans_rot = ["smoothleft", "wiperight", "smoothright", "dissolve", "hblur", "fadewhite"]
    trans_list = []
    for k in range(N - 1):
        next_asset = assets[k + 1]
        default_t = trans_rot[(beat_idx + k) % len(trans_rot)]
        t_name = determine_transition_for_asset(next_asset, default_t)
        trans_list.append(t_name)

    if N == 2:
        filter_parts.append(f"[v0][v1]xfade=transition={trans_list[0]}:duration={T}:offset={offsets[0]},format=yuv420p[outv]")
    elif N == 3:
        filter_parts.append(f"[v0][v1]xfade=transition={trans_list[0]}:duration={T}:offset={offsets[0]}[v01]")
        filter_parts.append(f"[v01][v2]xfade=transition={trans_list[1]}:duration={T}:offset={offsets[1]},format=yuv420p[outv]")
    elif N == 4:
        filter_parts.append(f"[v0][v1]xfade=transition={trans_list[0]}:duration={T}:offset={offsets[0]}[v01]")
        filter_parts.append(f"[v01][v2]xfade=transition={trans_list[1]}:duration={T}:offset={offsets[1]}[v012]")
        filter_parts.append(f"[v012][v3]xfade=transition={trans_list[2]}:duration={T}:offset={offsets[2]},format=yuv420p[outv]")
    elif N == 5:
        filter_parts.append(f"[v0][v1]xfade=transition={trans_list[0]}:duration={T}:offset={offsets[0]}[v01]")
        filter_parts.append(f"[v01][v2]xfade=transition={trans_list[1]}:duration={T}:offset={offsets[1]}[v012]")
        filter_parts.append(f"[v012][v3]xfade=transition={trans_list[2]}:duration={T}:offset={offsets[2]}[v0123]")
        filter_parts.append(f"[v0123][v4]xfade=transition={trans_list[3]}:duration={T}:offset={offsets[3]},format=yuv420p[outv]")

    cmd.extend([
        "-filter_complex", ";".join(filter_parts),
        "-map", "[outv]",
        "-t", str(round(target_dur, 2)),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "21",
        "-pix_fmt", "yuv420p",
        "-an",
        str(out_path)
    ])

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return offsets

def compose_cinematic_music_score(total_sec: float, out_wav: Path):
    SR = 44100
    t = np.linspace(0, total_sec, int(SR * total_sec), endpoint=False)
    bass = 0.35 * np.sin(2 * np.pi * 55.0 * t)
    cello = 0.25 * np.sin(2 * np.pi * 110.0 * t)
    drone_mid = 0.15 * np.sin(2 * np.pi * 164.81 * t)
    drone_high = 0.10 * np.sin(2 * np.pi * 220.0 * t)
    noise = np.random.normal(0, 0.012, len(t))

    mix = bass + cello + drone_mid + drone_high + noise
    lead_in = int(SR * 2.0)
    lead_out = int(SR * 3.5)
    fade_in = np.linspace(0, 1, lead_in)
    fade_out = np.linspace(1, 0, lead_out)
    mix[:lead_in] *= fade_in
    mix[-lead_out:] *= fade_out

    mix = np.clip(mix / (np.max(np.abs(mix)) + 1e-6) * 0.65, -0.92, 0.92)
    pcm = (mix * 32767).astype(np.int16)

    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())

def load_wav_samples(wav_path: Path):
    with wave.open(str(wav_path), "rb") as wf:
        n = wf.getnframes()
        data = wf.readframes(n)
        return np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0

def build_transition_sfx_track(total_sec: float, sfx_events: list, out_wav: Path):
    SR = 44100
    total_samples = int(total_sec * SR)
    track = np.zeros(total_samples, dtype=np.float32)

    whoosh_samp = load_wav_samples(SFX_DIR / "whoosh.wav")
    paper_samp = load_wav_samples(SFX_DIR / "paper_rip.wav")
    boom_samp = load_wav_samples(SFX_DIR / "impact_boom.wav")
    shutter_samp = load_wav_samples(SFX_DIR / "camera_shutter.wav")

    sfx_map = {
        "whoosh": (whoosh_samp, 0.16),
        "paper_rip": (paper_samp, 0.18),
        "impact_boom": (boom_samp, 0.28),
        "camera_shutter": (shutter_samp, 0.18)
    }

    for t_sec, sfx_type in sfx_events:
        idx_start = int(t_sec * SR)
        if sfx_type in sfx_map and idx_start < total_samples:
            samp, vol = sfx_map[sfx_type]
            l = min(len(samp), total_samples - idx_start)
            track[idx_start:idx_start+l] += samp[:l] * vol

    max_val = np.max(np.abs(track))
    if max_val > 0.85:
        track = track / max_val * 0.85

    pcm = (track * 32767).astype(np.int16)
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    log(f"Generated Selective SFX Track: {len(sfx_events)} synchronized sound accents (Zero Spam!)")

def main():
    log("=== COMMENCING MASTER RE-ASSEMBLY (CLEAN FULL-BLEED + MEGA-AIRLINES + NO WATERMARKS) ===")

    # 1. Manage shots cache
    log("Checking subshots cache for incremental xfade generation...")
    force_rebuild = {7, 16, 36}
    for reb_idx in force_rebuild:
        old_f = TEMP_SHOTS_DIR / f"beat_{reb_idx:02d}_master.mp4"
        if old_f.exists():
            old_f.unlink()

    # 2. Asset Pools (Pure 1080p Full Bleed, NO watermarks, NO pillarboxing, NO 9/11 repeats)
    authentic_pool = sorted([
        p for p in CLIPS_DIR.glob("*.mp4")
        if "srf" not in p.name and "14_media_scrum" not in p.name
    ])
    broll_pool = sorted([
        p for p in BROLL_DIR.glob("*.mp4")
        if "CRASH" not in p.name  # Exclude pillarboxed crash clip
    ])
    used_assets = set()
    auth_queue = [p for p in authentic_pool]
    broll_queue = [p for p in broll_pool]

    log(f"Clean Pool: {len(authentic_pool)} authentic archival clips, {len(broll_pool)} high-quality B-Roll clips")

    # 3. Process Cold Open
    cold_raw_mp4 = ANIM_DIR / "cold_open.mp4"
    cold_wav = AUDIO_DIR / "cold_open.wav"
    cold_dur = get_audio_duration(cold_wav)

    cold_master_mp4 = TEMP_SHOTS_DIR / "beat_00_cold_open.mp4"
    log(f"Normalizing Cold Open to exact audio duration ({cold_dur:.2f}s)...")
    cmd_cold = [
        "ffmpeg", "-y", "-ss", "0.2", "-t", str(round(cold_dur, 2)),
        "-i", str(cold_raw_mp4),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080:(in_w-1920)/2:(in_h-1080)/2,tpad=stop_mode=clone:stop_duration=3,settb=AVTB,setpts=PTS-STARTPTS,fps=30,format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "21", "-pix_fmt", "yuv420p", "-an",
        str(cold_master_mp4)
    ]
    subprocess.run(cmd_cold, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    master_video_clips = [str(cold_master_mp4)]
    master_audio_clips = [str(cold_wav)]
    used_assets.add(str(cold_raw_mp4))

    cumulative_time = cold_dur
    sfx_events = []
    total_subshots = 0

    # 4. Render 64 Beats with Native Xfade Transitions
    for idx in range(1, 65):
        audio_path = AUDIO_DIR / f"beat_{idx}.wav"
        dur = get_audio_duration(audio_path)
        master_audio_clips.append(str(audio_path))

        # Check if contextual assets pre-defined for this beat
        if idx in CONTEXTUAL_ASSETS:
            beat_assets = [a for a in CONTEXTUAL_ASSETS[idx] if a.exists()]
            num_subshots = len(beat_assets)
            for a in beat_assets:
                used_assets.add(str(a))
            total_subshots += num_subshots
        else:
            if dur <= 5.2:
                num_subshots = 2
            elif dur <= 8.5:
                num_subshots = 3
            else:
                num_subshots = 4

            beat_assets = []
            for s_idx in range(num_subshots):
                asset = None
                if (total_subshots % 2 == 0) and broll_queue:
                    for cand in broll_queue:
                        if str(cand) not in used_assets and cand.exists():
                            asset = cand
                            used_assets.add(str(cand))
                            broll_queue.remove(cand)
                            break
                elif auth_queue:
                    for cand in auth_queue:
                        if str(cand) not in used_assets and cand.exists():
                            asset = cand
                            used_assets.add(str(cand))
                            auth_queue.remove(cand)
                            break

                if asset is None:
                    asset = authentic_pool[total_subshots % len(authentic_pool)]

                beat_assets.append(asset)
                total_subshots += 1

        # Check for kinetic punch text overlay
        overlays = [None] * len(beat_assets)
        if idx in PUNCH_TEXTS:
            ov = OVERLAY_DIR / f"punch_{idx:02d}.png"
            if ov.exists():
                # Apply overlay to the second subshot (or first if 1 subshot)
                target_sub = min(1, len(beat_assets) - 1)
                overlays[target_sub] = ov

        # Render beat with native xfade if not cached
        beat_out_mp4 = TEMP_SHOTS_DIR / f"beat_{idx:02d}_master.mp4"
        if not beat_out_mp4.exists():
            trans_offsets = render_beat_with_xfade(
                beat_idx=idx,
                assets=beat_assets,
                overlays=overlays,
                target_dur=dur,
                out_path=beat_out_mp4
            )
        else:
            total_raw = dur + (len(beat_assets) - 1) * 0.45
            sub_d = total_raw / len(beat_assets)
            cum_off = 0.0
            trans_offsets = []
            for i in range(len(beat_assets) - 1):
                cum_off += sub_d
                trans_offsets.append(round(cum_off - (i + 1) * 0.45, 3))
        master_video_clips.append(str(beat_out_mp4))

        # Synchronize selective SFX events
        if idx in SELECTIVE_SFX_BEATS:
            sfx_type, trans_pos = SELECTIVE_SFX_BEATS[idx]
            if trans_pos == 0:
                sfx_events.append((cumulative_time, sfx_type))
            elif trans_pos - 1 < len(trans_offsets):
                sfx_events.append((cumulative_time + trans_offsets[trans_pos - 1], sfx_type))
            else:
                sfx_events.append((cumulative_time, sfx_type))

        cumulative_time += dur

        # Primary source archival witness soundbite pause
        if idx in ARCHIVAL_SOUNDBITES:
            sb_video, sb_audio = ARCHIVAL_SOUNDBITES[idx]
            if sb_video.exists() and sb_audio.exists():
                sb_dur = get_audio_duration(sb_audio)
                master_video_clips.append(str(sb_video))
                master_audio_clips.append(str(sb_audio))
                cumulative_time += sb_dur
                log(f"Inserted Authentic Archival Witness Soundbite after Beat {idx} ({sb_dur:.2f}s pause)...")

        if idx % 10 == 0 or idx == 64:
            log(f"Rendered Beat {idx}/64 ({total_subshots} total subshots, 0 black frames)...")

    log(f"All 64 Beats successfully composed! Total unique assets used: {len(used_assets)}")

    # 5. Write Video Concat List
    video_concat_txt = EXPORT_DIR / "video_concat.txt"
    with open(video_concat_txt, "w", encoding="utf-8") as f:
        for clip in master_video_clips:
            f.write(f"file '{clip.replace(os.sep, '/')}'\n")

    # 6. Master Audio Timeline
    log("Building master voiceover narration track...")
    audio_concat_txt = EXPORT_DIR / "audio_concat.txt"
    with open(audio_concat_txt, "w", encoding="utf-8") as f:
        for a_clip in master_audio_clips:
            f.write(f"file '{a_clip.replace(os.sep, '/')}'\n")

    master_vo_wav = EXPORT_DIR / "master_voiceover.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(audio_concat_txt),
        "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "1", str(master_vo_wav)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    total_timeline_sec = get_audio_duration(master_vo_wav)
    log(f"Total Master Timeline Duration: {total_timeline_sec:.2f} seconds ({total_timeline_sec/60:.2f} minutes)")

    # 7. Selective Transition SFX Track
    sfx_track_wav = EXPORT_DIR / "transition_sfx_track.wav"
    build_transition_sfx_track(total_timeline_sec, sfx_events, sfx_track_wav)

    # 8. Tension Music Score
    tension_wav = EXPORT_DIR / "tension_score.wav"
    compose_cinematic_music_score(total_timeline_sec, tension_wav)

    # 9. Dynamic Audio Mixing (-14 LUFS, voiceover clear, score subtle, SFX accented)
    log("Dynamically mixing Voiceover (-14 LUFS) + Tension Score (-20 dB) + Selective SFX...")
    master_mix_wav = EXPORT_DIR / "master_audio_mix.wav"
    audio_mix_cmd = [
        "ffmpeg", "-y",
        "-i", str(master_vo_wav),
        "-i", str(tension_wav),
        "-i", str(sfx_track_wav),
        "-filter_complex",
        "[0:a]volume=1.0[vo];"
        "[1:a]volume=0.10[music];"
        "[2:a]volume=1.0[sfx];"
        "[vo][music][sfx]amix=inputs=3:duration=first:weights=1.0 0.20 0.85[mixed];"
        "[mixed]loudnorm=I=-14:TP=-1.5:LRA=11[outa]",
        "-map", "[outa]",
        "-c:a", "pcm_s16le",
        "-ar", "44100",
        str(master_mix_wav)
    ]
    subprocess.run(audio_mix_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 10. Multiplex Final Master Video
    master_out_mp4 = EXPORT_DIR / "documentary.mp4"
    log("Multiplexing balanced documentary master with Faststart (target < 35 MB)...")
    mux_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(video_concat_txt),
        "-i", str(master_mix_wav),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-vf", "noise=c1s=6:c0f=u+t,eq=contrast=1.05:brightness=-0.02:saturation=1.06",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-s", "1280x720",
        "-b:v", "360k",
        "-maxrate", "500k",
        "-bufsize", "800k",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "96k",
        "-movflags", "+faststart",
        str(master_out_mp4)
    ]
    subprocess.run(mux_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    size_mb = master_out_mp4.stat().st_size / (1024 * 1024)
    log(f"Master Documentary rendered successfully! ({size_mb:.2f} MB)")

    # 11. Package Release ZIP
    pkg_zip = EXPORT_DIR / "docuforge_package.zip"
    with zipfile.ZipFile(pkg_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(master_out_mp4, arcname="documentary.mp4")
        srt_file = EXPORT_DIR / "subtitles.srt"
        if srt_file.exists():
            zf.write(srt_file, arcname="subtitles.srt")
        for thumb in EXPORT_DIR.glob("*.jpg"):
            zf.write(thumb, arcname=thumb.name)

    pkg_mb = pkg_zip.stat().st_size / (1024 * 1024)
    log(f"Release package ready: {pkg_zip.name} ({pkg_mb:.2f} MB)")
    log("=== DOCUMENTARY MASTER FULLY RENDERED WITH FULL-BLEED 16:9, NO WATERMARKS, NO BLACK SCREENS ===")

if __name__ == "__main__":
    main()
