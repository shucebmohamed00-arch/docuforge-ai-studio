import sys
import wave
from pathlib import Path

BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
sys.path.insert(0, str(BASE_DIR))
AUDIO_DIR = BASE_DIR / "data" / "media" / "audio" / "swiss-air-grounding-prod"
SRT_PATH = BASE_DIR / "data" / "exports" / "swiss-air-grounding-prod" / "subtitles.srt"

from tools.build_10min_audio_track import BEATS_COMMENTARY

def format_timestamp(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int(round((sec - int(sec)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def get_audio_duration(wav_path: Path) -> float:
    with wave.open(str(wav_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())

def main():
    cum_time = 0.0
    entries = []

    for order in sorted(BEATS_COMMENTARY.keys()):
        wav_path = AUDIO_DIR / f"beat_{order}.wav"
        if not wav_path.exists():
            continue
        dur = get_audio_duration(wav_path)
        start_ts = format_timestamp(cum_time)
        end_ts = format_timestamp(cum_time + dur - 0.05)
        text = BEATS_COMMENTARY[order]

        entries.append((len(entries) + 1, start_ts, end_ts, text))
        cum_time += dur

    with open(SRT_PATH, "w", encoding="utf-8") as f:
        for idx, start_ts, end_ts, text in entries:
            f.write(f"{idx}\n{start_ts} --> {end_ts}\n{text}\n\n")

    print(f"Subtitles written with {len(entries)} cues to {SRT_PATH} (Total: {cum_time:.2f}s)")

if __name__ == "__main__":
    main()
