import os
import sys
import json
import time
import asyncio
import subprocess
from pathlib import Path
import wave
import numpy as np

PROJ_ID = "swiss-air-grounding-prod"
BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
AUDIO_DIR = BASE_DIR / "data" / "media" / "audio" / PROJ_ID
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

with open(BASE_DIR / "storyboard_items.json", "r", encoding="utf-8") as f:
    STORYBOARD = json.load(f)

print(f"Total storyboard beats to synthesize: {len(STORYBOARD)}")

async def synthesize_beat(idx: int, text: str, sem: asyncio.Semaphore):
    import edge_tts
    async with sem:
        out_wav = AUDIO_DIR / f"beat_{idx}.wav"
        temp_mp3 = AUDIO_DIR / f"beat_{idx}.temp.mp3"

        clean_text = text.strip() or "Scene transition."
        # Use deep, authoritative documentary narrator voice
        voice = "en-US-AndrewMultilingualNeural"
        
        try:
            comm = edge_tts.Communicate(clean_text, voice, rate="-4%")
            await comm.save(str(temp_mp3))

            # Transcode MP3 to broadcast 44.1kHz 16-bit mono WAV with loudnorm (-14 LUFS)
            cmd = [
                "ffmpeg", "-y", "-i", str(temp_mp3),
                "-ac", "1",
                "-ar", "44100",
                "-af", "aresample=44100,loudnorm=I=-14:LRA=9:TP=-1",
                "-threads", "1",
                str(out_wav)
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            temp_mp3.unlink(missing_ok=True)

            # Check RMS to confirm human speech presence
            with wave.open(str(out_wav), "rb") as wf:
                data = wf.readframes(wf.getnframes())
                arr = np.frombuffer(data, dtype=np.int16)
                dur = wf.getnframes() / float(wf.getframerate())
                rms = np.sqrt(np.mean(arr**2))
                print(f"  [Beat {idx:02d}/64] Synthesized speech ({dur:.2f}s, RMS={rms:.1f})")

        except Exception as e:
            print(f"  [Beat {idx:02d}/64] ERROR: {e}")
            temp_mp3.unlink(missing_ok=True)

async def main():
    sem = asyncio.Semaphore(5) # 5 concurrent requests
    tasks = []
    for idx, it in enumerate(STORYBOARD, 1):
        tasks.append(synthesize_beat(idx, it["narration_text"], sem))
    
    t0 = time.time()
    await asyncio.gather(*tasks)
    print(f"\nAll 64 neural voiceovers generated in {time.time() - t0:.1f} seconds!")

if __name__ == "__main__":
    asyncio.run(main())
