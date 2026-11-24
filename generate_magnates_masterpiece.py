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
from PIL import Image, ImageDraw, ImageFont

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

PROJ_ID = "swiss-air-grounding-prod"
BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
EXPORT_DIR = BASE_DIR / "data" / "exports" / PROJ_ID
ANIM_DIR = BASE_DIR / "data" / "media" / "animations" / PROJ_ID
AUDIO_DIR = BASE_DIR / "data" / "media" / "audio" / PROJ_ID
CLIPS_DIR = BASE_DIR / "data" / "media" / "authentic_clips"
OVERLAY_DIR = BASE_DIR / "data" / "media" / "magnates_overlays"
BROLL_DIR = BASE_DIR / "data" / "media" / "broll_cache"
TEMP_SHOTS_DIR = BASE_DIR / "data" / "media" / "rapid_shots"

for d in [EXPORT_DIR, ANIM_DIR, AUDIO_DIR, OVERLAY_DIR, TEMP_SHOTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Curated MagnatesMedia Punch Text Overlays (White text + Red/Gold Accent Keyword)
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
    56: ("450 MILLION CHF ", "TAXPAYER BAILOUT", (212, 175, 55)),
    64: ("NO BRAND IS ", "TOO SACRED TO FALL", (212, 175, 55))
}

def create_magnates_overlay(text_w: str, text_accent: str, accent_color: tuple, out_png: Path):
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 78)
    except:
        font = ImageFont.load_default()

    bbox_w = draw.textbbox((0, 0), text_w, font=font)
    bbox_a = draw.textbbox((0, 0), text_accent, font=font)
    w1 = bbox_w[2] - bbox_w[0]
    w2 = bbox_a[2] - bbox_a[0]
    total_w = w1 + w2
    x = (1920 - total_w) // 2
    y = 485

    # Dark drop shadow with soft offset
    for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 5), (5, 5)]:
        draw.text((x + ox, y + oy), text_w, font=font, fill=(0, 0, 0, 240))
        draw.text((x + w1 + ox, y + oy), text_accent, font=font, fill=(0, 0, 0, 240))

    # Crisp foreground text
    draw.text((x, y), text_w, font=font, fill=(255, 255, 255, 255))
    draw.text((x + w1, y), text_accent, font=font, fill=accent_color + (255,))

    img.save(str(out_png))

def get_audio_duration(wav_path: Path) -> float:
    with wave.open(str(wav_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())

def render_subshot(src_video: Path, out_path: Path, dur: float, start_sec: float = 0.0,
                   overlay_png: Path = None, transition: str = "cut",
                   chyron_title: str = None, chyron_sub: str = None):
    vf_chain = []
    
    # 1. Base crop and 1080p scale
    vf_chain.append("scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24")
    
    # 2. MagnatesMedia Cinematic Color Grade
    vf_chain.append("eq=contrast=1.12:brightness=-0.03:saturation=1.08")

    # 3. Dynamic Camera Movement (Ken Burns Zoom or Push-in)
    if transition == "zoom_in":
        vf_chain.append("zoompan=z='min(zoom+0.0018,1.15)':d=60:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080")

    # 4. Lower-third chyron if provided
    if chyron_title and chyron_sub:
        safe_title = chyron_title.replace("'", "").replace(":", " -").replace("Ü", "U").replace("%", " PERCENT")
        safe_sub = chyron_sub.replace("'", "").replace(":", " -").replace("Ü", "U").replace("É", "E").replace("%", " PERCENT")
        font_bold = "C\\:/Windows/Fonts/arialbd.ttf"
        font_reg = "C\\:/Windows/Fonts/arial.ttf"
        draw_box = "drawbox=x=60:y=890:w=880:h=90:color=black@0.75:t=fill"
        draw_bar = "drawbox=x=60:y=890:w=8:h=90:color=0xD4AF37@1.0:t=fill"
        draw_txt1 = f"drawtext=fontfile='{font_bold}':text='{safe_title}':x=85:y=912:fontsize=28:fontcolor=white:box=0"
        draw_txt2 = f"drawtext=fontfile='{font_reg}':text='{safe_sub}':x=85:y=948:fontsize=19:fontcolor=0xD4AF37:box=0"
        vf_chain.append(f"{draw_box},{draw_bar},{draw_txt1},{draw_txt2}")

    # 5. Transition in/out
    if transition == "white_flash":
        vf_chain.append("fade=t=in:st=0:d=0.22:color=white")
    elif transition == "red_flash":
        vf_chain.append("fade=t=in:st=0:d=0.22:color=0x991111")
    elif transition == "crossfade":
        d_out = 0.25
        st_out = max(0.05, dur - d_out)
        vf_chain.append(f"fade=t=in:st=0:d=0.25,fade=t=out:st={st_out}:d={d_out}")
    elif transition == "dip_black":
        d_out = 0.3
        st_out = max(0.05, dur - d_out)
        vf_chain.append(f"fade=t=in:st=0:d=0.3:color=black,fade=t=out:st={st_out}:d={d_out}:color=black")

    vf_str = ",".join(vf_chain)

    cmd = ["ffmpeg", "-y", "-ss", str(start_sec), "-i", str(src_video)]
    if overlay_png and overlay_png.exists():
        cmd.extend(["-i", str(overlay_png)])
        filter_complex = f"[0:v]{vf_str}[bg];[bg][1:v]overlay=0:0[outv]"
        cmd.extend(["-filter_complex", filter_complex, "-map", "[outv]"])
    else:
        cmd.extend(["-vf", vf_str])

    cmd.extend([
        "-t", str(round(dur, 2)),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "21",
        "-pix_fmt", "yuv420p",
        "-an",
        str(out_path)
    ])
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def compose_cinematic_music_score(total_sec: float, out_wav: Path):
    SR = 44100
    total_samples = int(total_sec * SR)
    t = np.linspace(0, total_sec, total_samples, endpoint=False)

    log(f"Composing {total_sec:.1f}s multi-instrument cinematic tension score...")
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.12 * t)
    sub = (0.32 * np.sin(2 * np.pi * 32.7 * t) + 0.20 * np.sin(2 * np.pi * 65.4 * t)) * (0.65 + 0.35 * lfo)

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

    tick_phase = (t * 2.0) % 1.0
    tick_env = np.exp(-tick_phase * 65.0)
    tick = np.sin(2 * np.pi * 2200.0 * t) * tick_env * 0.09

    hb_phase = (t * 1.0) % 1.0
    hb_env = np.exp(-hb_phase * 16.0)
    heartbeat = np.sin(2 * np.pi * 48.0 * t) * hb_env * 0.26

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
    log("=== COMMENCING MAGNATESMEDIA RAPID-PACING CINEMATIC MASTER ASSEMBLY ===")

    # 1. Pre-generate all MagnatesMedia Punch Text Overlays
    log("Pre-rendering MagnatesMedia bold keyword punch text overlays...")
    for beat_num, (tw, ta, col) in PUNCH_TEXTS.items():
        out_p = OVERLAY_DIR / f"punch_{beat_num:02d}.png"
        create_magnates_overlay(tw, ta, col, out_p)

    # 2. Available Asset Pools
    srf_clips = sorted(list(CLIPS_DIR.glob("srf_clip_*.mp4")))
    rsi_clips = sorted(list(CLIPS_DIR.glob("rsi_clip_*.mp4")))
    kloten_clips = sorted(list(CLIPS_DIR.glob("kloten_clip_*.mp4")))
    broll_clips = sorted(list(BROLL_DIR.glob("*.mp4")))
    anim_clips = {
        5:  ANIM_DIR / "anim_02_chart.mp4",
        12: ANIM_DIR / "anim_01_map.mp4",
        23: ANIM_DIR / "anim_07_hunter_wheel.mp4",
        34: ANIM_DIR / "anim_04_document.mp4",
        43: ANIM_DIR / "anim_03_kinetic_type.mp4",
        48: ANIM_DIR / "anim_06_hud.mp4"
    }

    # 3. Assemble Cold Open
    cold_mp4 = ANIM_DIR / "cold_open.mp4"
    cold_wav = AUDIO_DIR / "cold_open.wav"
    master_video_clips = [str(cold_mp4)]
    master_audio_clips = [str(cold_wav)]

    # 4. Generate Rapid-Fire Sub-shots for all 64 Beats
    log("Generating 2.0s - 2.5s rapid sub-shots across all 64 timeline beats...")
    total_subshots = 0

    for idx in range(1, 65):
        audio_path = AUDIO_DIR / f"beat_{idx}.wav"
        dur = get_audio_duration(audio_path)
        master_audio_clips.append(str(audio_path))

        # Determine sub-shot division (2 to 4 cuts per beat)
        if dur <= 5.5:
            splits = [dur * 0.5, dur * 0.5]
        elif dur <= 8.5:
            s1 = 2.4
            s2 = 2.4
            s3 = dur - 4.8
            splits = [s1, s2, s3]
        else:
            s1 = 2.3
            s2 = 2.3
            s3 = 2.3
            s4 = dur - 6.9
            splits = [s1, s2, s3, s4]

        beat_subshot_files = []

        # Primary authentic clip
        primary_clip = srf_clips[(idx - 1) % len(srf_clips)]
        secondary_clip = rsi_clips[(idx - 1) % len(rsi_clips)]
        kloten_clip = kloten_clips[(idx - 1) % len(kloten_clips)]
        macro_broll = broll_clips[(idx - 1) % len(broll_clips)] if broll_clips else kloten_clip

        overlay_file = OVERLAY_DIR / f"punch_{idx:02d}.png"
        has_punch = overlay_file.exists()

        for s_idx, s_dur in enumerate(splits):
            total_subshots += 1
            out_sub = TEMP_SHOTS_DIR / f"shot_{idx:02d}_{s_idx+1}.mp4"

            # Determine visual source and style for each sub-shot
            if s_idx == 0:
                # Shot 1: Authentic Archival Anchor (SRF or Kloten) with Ken Burns zoom
                src = primary_clip
                tr = "white_flash" if idx in [23, 43] else "cut"
                overlay = None
                ch_t = "ZURICH KLOTEN AIRPORT" if idx <= 10 else None
                ch_s = "OCTOBER 2, 2001 - 12:30 PM" if idx <= 10 else None
                render_subshot(src, out_sub, s_dur, start_sec=0.0, overlay_png=overlay,
                               transition=tr, chyron_title=ch_t, chyron_sub=ch_s)

            elif s_idx == 1:
                # Shot 2: MagnatesMedia Punch Text OR Motion Graphic Animation OR Alternate Archive
                if idx in anim_clips:
                    src = anim_clips[idx]
                    tr = "crossfade"
                    overlay = None
                elif has_punch:
                    src = secondary_clip
                    tr = "zoom_in"
                    overlay = overlay_file
                else:
                    src = kloten_clip
                    tr = "cut"
                    overlay = None
                render_subshot(src, out_sub, s_dur, start_sec=2.2, overlay_png=overlay, transition=tr)

            elif s_idx == 2:
                # Shot 3: Macro Stock B-Roll / Action reaction with rapid zoom or fade
                src = macro_broll
                tr = "white_flash" if idx % 8 == 0 else "crossfade"
                render_subshot(src, out_sub, s_dur, start_sec=4.0, transition=tr)

            else:
                # Shot 4: Authentic RSI / SRF concluding glance
                src = secondary_clip
                tr = "cut"
                render_subshot(src, out_sub, s_dur, start_sec=5.5, transition=tr)

            beat_subshot_files.append(out_sub)

        # Concatenate sub-shots for this beat into a single unified beat video
        beat_concat_txt = TEMP_SHOTS_DIR / f"beat_{idx:02d}_concat.txt"
        with open(beat_concat_txt, "w", encoding="utf-8") as f:
            for bf in beat_subshot_files:
                f.write(f"file '{bf.resolve().as_posix()}'\n")

        final_beat_mp4 = ANIM_DIR / f"rapid_beat_{idx:02d}.mp4"
        cmd_cat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(beat_concat_txt),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "21",
            "-pix_fmt", "yuv420p", "-an", str(final_beat_mp4)
        ]
        subprocess.run(cmd_cat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        master_video_clips.append(str(final_beat_mp4))

        if idx % 10 == 0 or idx == 64:
            log(f"Processed {idx}/64 beats ({total_subshots} rapid dynamic cuts completed)...")

    # 5. Build Master Audio Stream
    log("Building 500-second master voiceover narration track...")
    narration_frames = bytearray()
    for af in master_audio_clips:
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

    # 6. Compose Continuous Tension Score & Dynamic Mix
    soundtrack_wav = EXPORT_DIR / "cinematic_soundtrack.wav"
    compose_cinematic_music_score(total_duration, soundtrack_wav)

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

    # 7. Final Master Multiplexing with Faststart
    master_concat_txt = EXPORT_DIR / "master_v_concat.txt"
    with open(master_concat_txt, "w", encoding="utf-8") as f:
        for vf in master_video_clips:
            f.write(f"file '{Path(vf).resolve().as_posix()}'\n")

    master_mp4 = EXPORT_DIR / "documentary.mp4"
    log("Multiplexing ultimate rapid-paced master documentary with Faststart...")
    cmd_final = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(master_concat_txt),
        "-i", str(mixed_audio_wav),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-b:v", "1100k",
        "-maxrate", "1450k",
        "-bufsize", "2200k",
        "-profile:v", "high",
        "-level", "4.0",
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
    log(f"=== MAGNATESMEDIA RAPID MASTER COMPLETE: {total_subshots} TOTAL DYNAMIC SHOTS ===")

if __name__ == "__main__":
    main()
