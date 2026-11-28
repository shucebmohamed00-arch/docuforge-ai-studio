import os
import sys
import wave
import shutil
import zipfile
import subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

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
REMOTION_DIR = BASE_DIR / "data" / "media" / "remotion_renders"
FOLEY_DIR = BASE_DIR / "data" / "media" / "master_foley"
FIN_DIR = BASE_DIR / "data" / "media" / "financial_graphics"
OVERLAY_DIR = BASE_DIR / "data" / "media" / "magnates_overlays"
BROLL_DIR = BASE_DIR / "data" / "media" / "broll_cache"
SFX_DIR = BASE_DIR / "data" / "media" / "sfx"
RUNWAY_DIR = BASE_DIR / "data" / "media" / "cinematic_ai_assets"
TEMP_SHOTS_DIR = BASE_DIR / "data" / "media" / "ten_minute_shots"

for d in [EXPORT_DIR, ANIM_DIR, AUDIO_DIR, OVERLAY_DIR, TEMP_SHOTS_DIR, SFX_DIR, PHOTO_DIR, FIN_DIR, RUNWAY_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def log(msg):
    import time
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def get_audio_duration(wav_path: Path) -> float:
    with wave.open(str(wav_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())

# Punch text overlays across all 6 Chapters
PUNCH_TEXTS = {
    1:  ("A SINGLE PHONE CALL ", "FROZE EUROPE", (235, 35, 35)),
    2:  ("SUPPLIERS CUT OFF ", "THE KEROSENE", (235, 35, 35)),
    3:  ("THE CREDIT LINES ", "WERE DEAD", (235, 35, 35)),
    4:  ("EVERY PLANE GROUNDED ", "ON TARMAC", (212, 175, 55)),
    5:  ("NICKNAMED: ", "'THE FLYING BANK'", (212, 175, 55)),
    7:  ("HOW DOES A CARTEL COLLAPSE ", "IN 48 HOURS?", (235, 35, 35)),
    8:  ("AN AGGRESSIVE ", "DEBT SPREE", (235, 35, 35)),
    12: ("ORIGIN: POLITICAL ", "ISOLATION", (235, 35, 35)),
    17: ("THE 1992 HISTORIC ", "EEA REFERENDUM", (212, 175, 55)),
    18: ("VOTED NO: ", "SWITZERLAND ISOLATED", (235, 35, 35)),
    20: ("EUROPE OPEN SKIES: ", "COMPETITORS EXPAND", (212, 175, 55)),
    22: ("SWISSAIR TRAPPED: ", "NO PICKUP IN PARIS", (235, 35, 35)),
    28: ("ENTER: ", "PHILIPPE BRUGGISSER", (212, 175, 55)),
    30: ("THE NOTORIOUS ", "'HUNTER STRATEGY'", (235, 35, 35)),
    33: ("A MULTI-BILLION ", "SHOPPING SPREE", (235, 35, 35)),
    34: ("SABENA BELGIUM: ", "40 YEARS OF LOSSES", (235, 35, 35)),
    37: ("CONFIDENTIAL CLAUSES: ", "OFF-BALANCE DEBT", (235, 35, 35)),
    39: ("BLEEDING 1 MILLION ", "EVERY 24 HOURS", (235, 35, 35)),
    43: ("BRUGGISSER FIRED ", "MARIO CORTI ARRIVES", (212, 175, 55)),
    46: ("FORENSIC AUDIT: ", "ERNST & YOUNG", (212, 175, 55)),
    48: ("OFF-BALANCE DEBT: ", "17.2 BILLION CHF", (235, 35, 35)),
    49: ("SEPTEMBER 11TH: ", "GLOBAL COLLAPSE", (235, 35, 35)),
    54: ("SECRET BANK RESCUE: ", "'PROJECT PHOENIX'", (212, 175, 55)),
    57: ("CARVE OUT CROSSAIR ", "LET MOTHER COMPANY DIE", (235, 35, 35)),
    61: ("OCTOBER 1: ", "UBS WITHHOLDS CASH", (235, 35, 35)),
    64: ("CANCELLATION ORDER: ", "GROUNDED WORLDWIDE", (235, 35, 35)),
    65: ("38,000 PASSENGERS ", "STRANDED GLOBALLY", (235, 35, 35)),
    67: ("PROTESTORS CHANT: ", "'BANKERS: GRAVEDIGGERS'", (235, 35, 35)),
    68: ("FEDERAL BAILOUT: ", "450 MILLION CHF", (212, 175, 55)),
    70: ("CROSSAIR REBRANDS ", "AS 'SWISS'", (212, 175, 55)),
    72: ("LUFTHANSA BUYS ", "THE REMNANTS", (235, 35, 35)),
    73: ("CRIMINAL TRIAL: ", "19 EXECUTIVES CHARGED", (212, 175, 55)),
    75: ("THE VERDICT: ", "FULL ACQUITTAL", (235, 35, 35)),
    76: ("NO BRAND IS TOO SACRED ", "TO FALL", (212, 175, 55))
}

# Key contextual asset mapping integrating Runway AI videos & custom graphics
CONTEXTUAL_ASSETS = {
    # Chapter 1: Grounding Shock (Runway Kling 3.0 Pro + Flash + MapLibre)
    1:  [ANIM_DIR / "anim_01_map.mp4", CLIPS_DIR / "zurich_uncut_38_foggy_morning_kloten.mp4"],
    3:  [RUNWAY_DIR / "ai_07_fuel_hose_cutoff.mp4", CLIPS_DIR / "zurich_uncut_28_md11_wingtip.mp4"],
    4:  [RUNWAY_DIR / "ai_09_cancelled_departure_board.mp4", CLIPS_DIR / "zurich_uncut_37_grounded_lineup.mp4"],
    7:  [STAGE_DIR / "stage_03_ubs_dossier.mp4", CLIPS_DIR / "politics_ubs_06_bank_vault_doors.mp4"],
    8:  [FIN_DIR / "graphic_02_debt_spiral.mp4", CLIPS_DIR / "politics_ubs_20_financial_district_zurich.mp4"],
    11: [FIN_DIR / "graphic_01_stock_crash.mp4", CLIPS_DIR / "politics_ubs_10_stock_chart_screen.mp4"],
    12: [ADV_DIR / "doc_01_nzz_audit_stamp.mp4", FIN_DIR / "graphic_01_stock_crash.mp4"],
    16: [PHOTO_DIR / "photo_07_british_airways.mp4", PHOTO_DIR / "photo_08_lufthansa.mp4", PHOTO_DIR / "photo_09_air_france.mp4"],

    # Chapter 2: The European Trap (Runway Kling 4 Flash Ballot Box + MapLibre)
    17: [RUNWAY_DIR / "ai_14_referendum_ballot_box.mp4", CLIPS_DIR / "politics_ubs_24_parliament_voting_lights.mp4"],
    18: [PAPER_DIR / "paper_01_blick_grounded.mp4", CLIPS_DIR / "politics_ubs_02_politician_speech.mp4"],
    20: [ANIM_DIR / "anim_01_map.mp4", CLIPS_DIR / "zurich_uncut_04_cockpit_view.mp4"],
    22: [PHOTO_DIR / "photo_09_air_france.mp4", CLIPS_DIR / "zurich_uncut_28_md11_wingtip.mp4"],
    28: [REMOTION_DIR / "parallax_bruggisser.mp4", CLIPS_DIR / "politics_ubs_13_investor_meeting.mp4"],

    # Chapter 3: The Hunter Strategy (Runway Kling 4 Flash Contract Signing + D3 Wheel)
    30: [ANIM_DIR / "anim_07_hunter_wheel.mp4", FIN_DIR / "graphic_03_hunter_network.mp4"],
    34: [PAPER_DIR / "paper_06_sabena.mp4", CLIPS_DIR / "zurich_uncut_28_md11_wingtip.mp4"],
    37: [RUNWAY_DIR / "ai_15_confidential_contract_signing.mp4", STAGE_DIR / "stage_03_ubs_dossier.mp4"],
    39: [FIN_DIR / "graphic_02_debt_spiral.mp4", CLIPS_DIR / "politics_ubs_23_bank_teller_counter.mp4"],

    # Chapter 4: The 17 Billion Black Hole (Runway Kling 3.0 Pro Corti Centerpiece + D3 Debt Chart)
    43: [REMOTION_DIR / "parallax_mario_corti.mp4", CLIPS_DIR / "politics_ubs_09_mario_corti_mic.mp4"],
    44: [RUNWAY_DIR / "ai_16_corti_press_conference.mp4", CLIPS_DIR / "politics_ubs_05_press_cameras.mp4"],
    46: [ADV_DIR / "doc_01_nzz_audit_stamp.mp4", FIN_DIR / "graphic_02_debt_spiral.mp4"],
    48: [ANIM_DIR / "anim_02_chart.mp4", FIN_DIR / "graphic_01_stock_crash.mp4"],
    49: [BROLL_DIR / "PASSENGER_TERMINAL.mp4", CLIPS_DIR / "zurich_uncut_37_grounded_lineup.mp4"],

    # Chapter 5: Project Phoenix (Runway Kling 4 Flash Boardroom at Night + Remotion Inspector)
    54: [RUNWAY_DIR / "ai_17_ubs_boardroom_night.mp4", ADV_DIR / "parallax_03_marcel_ospel.mp4"],
    56: [CLIPS_DIR / "politics_ubs_12_crossair_moritz_suter.mp4", CLIPS_DIR / "zurich_uncut_29_a320_nose.mp4"],
    58: [FIN_DIR / "graphic_04_intraday_countdown.mp4", PAPER_DIR / "paper_03_ubs_refusal.mp4"],
    61: [ADV_DIR / "parallax_04_ubs_dossier.mp4", CLIPS_DIR / "politics_ubs_06_bank_vault_doors.mp4"],
    64: [PAPER_DIR / "paper_01_blick_grounded.mp4", CLIPS_DIR / "zurich_uncut_25_engine_cover_wrap.mp4"],

    # Chapter 6: The Fall & Rebirth (Runway Kling 4 Flash Paradeplatz Protests + Courtroom)
    65: [BROLL_DIR / "PASSENGER_TERMINAL.mp4", PAPER_DIR / "paper_04_passengers.mp4"],
    67: [RUNWAY_DIR / "ai_18_paradeplatz_protest.mp4", PHOTO_DIR / "photo_04_protest.mp4"],
    68: [FIN_DIR / "graphic_05_bailout_rescue.mp4", CLIPS_DIR / "politics_ubs_24_parliament_voting_lights.mp4"],
    69: [RUNWAY_DIR / "ai_08_grounded_fleet_aerial.mp4", CLIPS_DIR / "zurich_uncut_37_grounded_lineup.mp4"],
    70: [CLIPS_DIR / "zurich_uncut_09_swissair_cross.mp4", PHOTO_DIR / "photo_07_british_airways.mp4"],
    72: [PHOTO_DIR / "photo_08_lufthansa.mp4", CLIPS_DIR / "politics_ubs_20_financial_district_zurich.mp4"],
    73: [CLIPS_DIR / "politics_ubs_05_press_cameras.mp4", CLIPS_DIR / "politics_ubs_09_mario_corti_mic.mp4"],
    75: [ADV_DIR / "doc_01_nzz_audit_stamp.mp4", CLIPS_DIR / "politics_ubs_18_banker_handshake.mp4"],
    76: [RUNWAY_DIR / "ai_08_grounded_fleet_aerial.mp4", ANIM_DIR / "anim_01_map.mp4", CLIPS_DIR / "zurich_uncut_04_cockpit_view.mp4"]
}

SELECTIVE_SFX_BEATS = {
    1:  ("impact_boom", 0),
    3:  ("hydraulic_hiss", 0),
    4:  ("impact_boom", 0),
    7:  ("impact_boom", 1),
    8:  ("whoosh", 0),
    11: ("impact_boom", 0),
    12: ("paper_rip", 0),
    17: ("camera_shutter", 0),
    18: ("paper_rip", 0),
    20: ("whoosh", 0),
    28: ("whoosh", 0),
    30: ("whoosh", 0),
    34: ("paper_rip", 0),
    37: ("paper_rip", 0),
    43: ("impact_boom", 0),
    44: ("camera_shutter", 0),
    46: ("paper_rip", 0),
    48: ("impact_boom", 0),
    54: ("impact_boom", 0),
    58: ("whoosh", 0),
    61: ("paper_rip", 0),
    64: ("impact_boom", 0),
    67: ("camera_shutter", 0),
    68: ("whoosh", 0),
    69: ("hydraulic_hiss", 0),
    73: ("camera_shutter", 0),
    75: ("paper_rip", 0),
    76: ("impact_boom", 0)
}

def build_punch_overlay(beat_idx: int, l1: str, l2: str, c_rgb: tuple, out_path: Path):
    W, H = 1920, 1080
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 64)
        tag_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 24)
    except Exception:
        font = ImageFont.load_default()
        tag_font = font

    tag_text = "CONFIDENTIAL // FORENSIC DOSSIER"
    bbox_tag = draw.textbbox((0, 0), tag_text, font=tag_font)
    tw, th = bbox_tag[2] - bbox_tag[0], bbox_tag[3] - bbox_tag[1]

    bar_w = 1200
    bar_h = 170
    rx = (W - bar_w) // 2
    ry = H - bar_h - 75

    draw.rounded_rectangle([rx, ry, rx + bar_w, ry + bar_h], radius=16, fill=(10, 14, 22, 230))
    draw.rounded_rectangle([rx, ry, rx + bar_w, ry + bar_h], radius=16, outline=c_rgb, width=3)
    draw.line([rx + 4, ry + 4, rx + bar_w - 4, ry + 4], fill=c_rgb, width=4)

    draw.rectangle([rx + 30, ry - 14, rx + 30 + tw + 20, ry + 14], fill=(12, 16, 24, 255), outline=c_rgb, width=2)
    draw.text((rx + 40, ry - 11), tag_text, fill=(240, 240, 240, 255), font=tag_font)

    bbox1 = draw.textbbox((0, 0), l1, font=font)
    w1 = bbox1[2] - bbox1[0]
    bbox2 = draw.textbbox((0, 0), l2, font=font)
    w2 = bbox2[2] - bbox2[0]

    draw.text((rx + (bar_w - w1) // 2 + 2, ry + 26), l1, fill=(0, 0, 0, 200), font=font)
    draw.text((rx + (bar_w - w1) // 2, ry + 24), l1, fill=(255, 255, 255, 255), font=font)

    draw.text((rx + (bar_w - w2) // 2 + 2, ry + 94), l2, fill=(0, 0, 0, 200), font=font)
    draw.text((rx + (bar_w - w2) // 2, ry + 92), l2, fill=c_rgb + (255,), font=font)

    img.save(out_path, "PNG")

def render_beat_with_xfade(beat_idx: int, assets: list, overlays: list, target_dur: float, out_path: Path):
    N = len(assets)
    T = 0.30

    if N == 1:
        cmd = [
            "ffmpeg", "-y",
            "-ss", "0.0", "-t", str(round(target_dur, 2)),
            "-i", str(assets[0])
        ]
        base_vf = (
            "scale=1280:720:force_original_aspect_ratio=increase,"
            "crop=1280:720:(in_w-1280)/2:(in_h-720)/2,"
            "tpad=stop_mode=clone:stop_duration=3,"
            "settb=AVTB,setpts=PTS-STARTPTS,fps=30,format=yuv420p"
        )
        if overlays[0] and overlays[0].exists():
            cmd.extend(["-i", str(overlays[0])])
            cmd.extend([
                "-filter_complex", f"[0:v]{base_vf}[bg];[1:v]scale=1280:720[ov];[bg][ov]overlay=0:0[outv]",
                "-map", "[outv]"
            ])
        else:
            cmd.extend(["-vf", base_vf])
        cmd.extend([
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
            "-pix_fmt", "yuv420p", "-an", str(out_path)
        ])
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return []

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

    vf_filters = []
    for i in range(N):
        scale_crop = (
            f"[{i}:v]scale=1280:720:force_original_aspect_ratio=increase,"
            f"crop=1280:720:(in_w-1280)/2:(in_h-720)/2,"
            f"tpad=stop_mode=clone:stop_duration=3,"
            f"settb=AVTB,setpts=PTS-STARTPTS,fps=30,format=yuv420p[s{i}]"
        )
        vf_filters.append(scale_crop)

    for i in range(N):
        if i in ov_indices:
            vf_filters.append(f"[{ov_indices[i]}:v]scale=1280:720[sc_ov{i}]")
            vf_filters.append(f"[s{i}][sc_ov{i}]overlay=0:0[v{i}]")
        else:
            vf_filters.append(f"[s{i}]null[v{i}]")

    curr = "v0"
    trans_list = ["smoothleft", "wiperight", "dissolve", "fadewhite", "hblur"]
    for i in range(N - 1):
        trans = trans_list[(beat_idx + i) % len(trans_list)]
        nxt = f"v{i+1}"
        out_v = f"xf{i}" if i < N - 2 else "outv"
        vf_filters.append(f"[{curr}][{nxt}]xfade=transition={trans}:duration={T}:offset={offsets[i]}[{out_v}]")
        curr = out_v

    filter_str = ";".join(vf_filters)
    cmd.extend([
        "-filter_complex", filter_str,
        "-map", "[outv]",
        "-t", str(round(target_dur, 2)),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-an", str(out_path)
    ])
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return offsets

def compose_cinematic_music_score(total_sec: float, out_wav: Path):
    sr = 44100
    n_samples = int(total_sec * sr)
    t = np.linspace(0, total_sec, n_samples, endpoint=False)
    bass = 0.22 * np.sin(2 * np.pi * 55 * t) + 0.12 * np.sin(2 * np.pi * 110 * t)
    pulse_freq = 1.6
    sub_pulse = 0.15 * np.sin(2 * np.pi * 73.4 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * pulse_freq * t))
    drone = 0.10 * np.sin(2 * np.pi * 82.4 * t)
    score = bass + sub_pulse + drone
    fade_len = int(3.0 * sr)
    if n_samples > fade_len:
        score[:fade_len] *= np.linspace(0, 1, fade_len)
        score[-fade_len:] *= np.linspace(1, 0, fade_len)
    score = np.clip(score, -0.85, 0.85)
    score_16 = (score * 32767).astype(np.int16)
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(score_16.tobytes())

def build_transition_sfx_track(total_sec: float, sfx_events: list, out_wav: Path):
    sr = 44100
    n_samples = int((total_sec + 2.0) * sr)
    audio_buf = np.zeros(n_samples, dtype=np.float32)

    def gen_sfx(kind: str, dur_s: float = 1.0) -> np.ndarray:
        s_n = int(dur_s * sr)
        st = np.linspace(0, dur_s, s_n, endpoint=False)
        if kind == "impact_boom":
            f = np.linspace(95, 28, s_n)
            env = np.exp(-4.5 * st)
            return 0.70 * np.sin(2 * np.pi * f * st) * env
        elif kind == "whoosh":
            noise = np.random.uniform(-0.35, 0.35, s_n)
            env = np.sin(np.pi * st / dur_s) ** 2
            return noise * env
        elif kind == "paper_rip":
            clicks = np.random.choice([0, 1], size=s_n, p=[0.985, 0.015]).astype(np.float32)
            env = np.exp(-3.0 * st)
            return clicks * env * 0.50
        elif kind == "camera_shutter":
            t_sh = np.linspace(0, 0.15, int(0.15 * sr), endpoint=False)
            click = 0.6 * np.sin(2 * np.pi * 1200 * t_sh) * np.exp(-35 * t_sh)
            res = np.zeros(s_n, dtype=np.float32)
            res[:len(click)] = click
            return res
        elif kind == "hydraulic_hiss":
            noise = np.random.uniform(-0.25, 0.25, s_n)
            env = np.exp(-2.0 * st)
            return noise * env
        return np.zeros(s_n, dtype=np.float32)

    for time_s, kind in sfx_events:
        idx = int(time_s * sr)
        if idx >= n_samples:
            continue
        clip = gen_sfx(kind, 1.2)
        end_idx = min(idx + len(clip), n_samples)
        audio_buf[idx:end_idx] += clip[:end_idx - idx]

    audio_buf = np.clip(audio_buf, -0.90, 0.90)
    buf_16 = (audio_buf * 32767).astype(np.int16)
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(buf_16.tobytes())

def main():
    log("=====================================================================")
    log("  STARTING DOCUFORGE 10-MINUTE COMPLETE MASTER ASSEMBLY (76 BEATS)  ")
    log("  Full Bleed 16:9, Zero Black Frames, Hybrid Runway AI, Dynamic SFX  ")
    log("=====================================================================")

    # 1. Render all Punch Overlays
    log("Checking punch text kinetic overlays...")
    for beat_idx, (l1, l2, col) in PUNCH_TEXTS.items():
        ov_path = OVERLAY_DIR / f"punch_{beat_idx:02d}.png"
        if not ov_path.exists():
            build_punch_overlay(beat_idx, l1, l2, col, ov_path)

    # 2. Gather authentic pools
    authentic_pool = sorted(list(CLIPS_DIR.glob("*.mp4")))
    broll_pool = sorted(list(BROLL_DIR.glob("*.mp4")))
    log(f"Asset Library loaded: {len(authentic_pool)} authentic archival clips, {len(broll_pool)} stock B-roll clips.")

    # 3. Assemble all 76 Beats
    master_video_clips = []
    master_audio_clips = []
    sfx_events = []
    cumulative_time = 0.0
    total_subshots = 0

    log("Composing 76 Beats across Chapters 1-6...")
    for idx in range(1, 77):
        audio_path = AUDIO_DIR / f"beat_{idx}.wav"
        if not audio_path.exists():
            log(f"WARNING: beat_{idx}.wav missing! Skipping audio.")
            continue

        dur = get_audio_duration(audio_path)
        master_audio_clips.append(str(audio_path))

        # Determine visual assets for beat
        if idx in CONTEXTUAL_ASSETS:
            beat_assets = [a for a in CONTEXTUAL_ASSETS[idx] if a.exists()]
            if not beat_assets:
                beat_assets = [authentic_pool[total_subshots % len(authentic_pool)]]
        else:
            if dur <= 5.0:
                k = 2
            elif dur <= 8.5:
                k = 3
            else:
                k = 4
            beat_assets = []
            for s in range(k):
                cand = authentic_pool[(total_subshots + s) % len(authentic_pool)]
                beat_assets.append(cand)

        total_subshots += len(beat_assets)

        # Overlays
        overlays = [None] * len(beat_assets)
        if idx in PUNCH_TEXTS:
            ov = OVERLAY_DIR / f"punch_{idx:02d}.png"
            if ov.exists():
                overlays[min(1, len(beat_assets) - 1)] = ov

        # Render beat video
        beat_out_mp4 = TEMP_SHOTS_DIR / f"beat_{idx:02d}_master.mp4"
        if not beat_out_mp4.exists():
            render_beat_with_xfade(idx, beat_assets, overlays, dur, beat_out_mp4)

        master_video_clips.append(str(beat_out_mp4))

        # Check SFX cues
        if idx in SELECTIVE_SFX_BEATS:
            kind, sub_i = SELECTIVE_SFX_BEATS[idx]
            sfx_events.append((cumulative_time + 0.1, kind))

        cumulative_time += dur

        if idx % 10 == 0 or idx == 76:
            log(f"Rendered Beat {idx}/76 (Timeline: {cumulative_time:.1f}s / {cumulative_time/60:.2f} mins)...")

    log(f"All 76 Beats successfully composed! Total video cuts: {total_subshots}")

    # 4. Write Video Concat List
    video_concat_txt = EXPORT_DIR / "video_concat.txt"
    with open(video_concat_txt, "w", encoding="utf-8") as f:
        for clip in master_video_clips:
            f.write(f"file '{clip.replace(os.sep, '/')}'\n")

    # 5. Master Voiceover Narration Track
    log("Concatenating master voiceover narration track...")
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

    # 6. Generate Transition SFX Track & Tension Music Score
    sfx_track_wav = EXPORT_DIR / "transition_sfx_track.wav"
    log("Synthesizing dynamic transition SFX track...")
    build_transition_sfx_track(total_timeline_sec, sfx_events, sfx_track_wav)

    tension_wav = EXPORT_DIR / "tension_score.wav"
    log("Synthesizing orchestral tension score...")
    compose_cinematic_music_score(total_timeline_sec, tension_wav)

    # 7. Dynamic Audio Mixing (-14 LUFS broadcast standard)
    log("Mixing Voiceover (-14 LUFS) + Background Score (-20 dB) + SFX accents...")
    master_mix_wav = EXPORT_DIR / "master_audio_mix.wav"
    audio_mix_cmd = [
        "ffmpeg", "-y",
        "-i", str(master_vo_wav),
        "-i", str(tension_wav),
        "-i", str(sfx_track_wav),
        "-filter_complex",
        "[0:a]volume=1.0[vo];"
        "[1:a]volume=0.12[music];"
        "[2:a]volume=0.90[sfx];"
        "[vo][music][sfx]amix=inputs=3:duration=first:weights=1.0 0.20 0.85[mixed];"
        "[mixed]loudnorm=I=-14:TP=-1.5:LRA=11[outa]",
        "-map", "[outa]",
        "-c:a", "pcm_s16le",
        "-ar", "44100",
        str(master_mix_wav)
    ]
    subprocess.run(audio_mix_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 8. Multiplex Final Master Video
    master_out_mp4 = EXPORT_DIR / "documentary.mp4"
    log("Multiplexing complete 10-minute master documentary with Faststart...")
    mux_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(video_concat_txt),
        "-i", str(master_mix_wav),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-vf", "noise=c1s=5:c0f=u+t,eq=contrast=1.05:brightness=-0.02:saturation=1.05",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-s", "1280x720",
        "-b:v", "420k",
        "-maxrate", "600k",
        "-bufsize", "900k",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "96k",
        "-movflags", "+faststart",
        str(master_out_mp4)
    ]
    subprocess.run(mux_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    size_mb = master_out_mp4.stat().st_size / (1024 * 1024)
    log(f"10-Minute Master Documentary rendered successfully! ({size_mb:.2f} MB)")

    # 9. Package Release ZIP
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
    log("=== 10-MINUTE DOCUMENTARY MASTER FULLY COMPLETED WITH ZERO BLACK FRAMES ===")

if __name__ == "__main__":
    main()
