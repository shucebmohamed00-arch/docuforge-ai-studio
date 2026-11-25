import os
import wave
import zipfile
import subprocess
import numpy as np
from pathlib import Path

PROJ_ID = "swiss-air-grounding-prod"
BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
EXPORT_DIR = BASE_DIR / "data" / "exports" / PROJ_ID
AUDIO_DIR = BASE_DIR / "data" / "media" / "audio" / PROJ_ID
SFX_DIR = BASE_DIR / "data" / "media" / "sfx"
TEMP_SHOTS_DIR = BASE_DIR / "data" / "media" / "rapid_zero_dup_shots"

def get_audio_duration(wav_path: Path) -> float:
    with wave.open(str(wav_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())

SELECTIVE_SFX_BEATS = {
    1:  ("impact_boom", 0),
    7:  ("impact_boom", 1),
    8:  ("whoosh", 0),
    11: ("impact_boom", 0),
    12: ("paper_rip", 0),
    16: ("whoosh", 1),
    17: ("camera_shutter", 1),
    20: ("whoosh", 0),
    22: ("camera_shutter", 0),
    25: ("whoosh", 0),
    29: ("paper_rip", 0),
    36: ("camera_shutter", 0),
    40: ("impact_boom", 0),
    41: ("camera_shutter", 1),
    48: ("whoosh", 0),
    49: ("paper_rip", 0),
    52: ("paper_rip", 0),
    54: ("paper_rip", 0),
    56: ("impact_boom", 0),
    58: ("camera_shutter", 0),
    59: ("paper_rip", 1),
    60: ("whoosh", 0)
}

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

def finish():
    print("Gathering all 64 rendered beats...")
    cold_master = TEMP_SHOTS_DIR / "beat_00_cold_open.mp4"
    cold_wav = AUDIO_DIR / "cold_open.wav"
    cold_dur = get_audio_duration(cold_wav)

    master_video_clips = [str(cold_master)]
    master_audio_clips = [str(cold_wav)]

    cumulative_time = cold_dur
    sfx_events = []

    for idx in range(1, 65):
        beat_mp4 = TEMP_SHOTS_DIR / f"beat_{idx:02d}_master.mp4"
        audio_wav = AUDIO_DIR / f"beat_{idx}.wav"
        dur = get_audio_duration(audio_wav)

        master_video_clips.append(str(beat_mp4))
        master_audio_clips.append(str(audio_wav))

        if idx in SELECTIVE_SFX_BEATS:
            sfx_type, trans_pos = SELECTIVE_SFX_BEATS[idx]
            sfx_events.append((cumulative_time + (0.0 if trans_pos == 0 else 1.2), sfx_type))

        cumulative_time += dur

    # 1. Write video concat
    video_concat_txt = EXPORT_DIR / "video_concat.txt"
    with open(video_concat_txt, "w", encoding="utf-8") as f:
        for clip in master_video_clips:
            f.write(f"file '{clip.replace(os.sep, '/')}'\n")

    # 2. Audio Timeline
    print("Building master audio timeline...")
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
    print(f"Timeline duration: {total_timeline_sec:.2f}s ({total_timeline_sec/60:.2f} mins)")

    # 3. SFX Track
    sfx_track_wav = EXPORT_DIR / "transition_sfx_track.wav"
    build_transition_sfx_track(total_timeline_sec, sfx_events, sfx_track_wav)

    # 4. Tension Score
    tension_wav = EXPORT_DIR / "tension_score.wav"
    compose_cinematic_music_score(total_timeline_sec, tension_wav)

    # 5. Audio Mix
    print("Mixing audio...")
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

    # 6. Multiplex Master Video
    master_out_mp4 = EXPORT_DIR / "documentary.mp4"
    print("Multiplexing master documentary...")
    mux_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(video_concat_txt),
        "-i", str(master_mix_wav),
        "-map", "0:v:0",
        "-map", "1:a:0",
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
    print(f"Master Documentary rendered! ({size_mb:.2f} MB)")

    # 7. Package ZIP
    pkg_zip = EXPORT_DIR / "docuforge_package.zip"
    with zipfile.ZipFile(pkg_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(master_out_mp4, arcname="documentary.mp4")
        srt_file = EXPORT_DIR / "subtitles.srt"
        if srt_file.exists():
            zf.write(srt_file, arcname="subtitles.srt")
        for thumb in EXPORT_DIR.glob("*.jpg"):
            zf.write(thumb, arcname=thumb.name)

    pkg_mb = pkg_zip.stat().st_size / (1024 * 1024)
    print(f"Release package ready: {pkg_zip.name} ({pkg_mb:.2f} MB)")
    print("=== FINISHED COMPLETE RE-ASSEMBLY ===")

if __name__ == "__main__":
    finish()
