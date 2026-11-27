import json
import wave
from pathlib import Path

with open('storyboard_items.json', 'r', encoding='utf-8') as f:
    sb = json.load(f)

audio_dir = Path('data/media/audio/swiss-air-grounding-prod')
print(f"Total storyboard beats: {len(sb)}")

total_dur = 0
for idx, b in enumerate(sb[:15], 1):
    txt = b.get('voiceover_text') or b.get('narration_text') or b.get('text') or ''
    wav_path = audio_dir / f"beat_{idx}.wav"
    dur = 0.0
    if wav_path.exists():
        with wave.open(str(wav_path), 'rb') as wf:
            dur = wf.getnframes() / wf.getframerate()
    vis = b.get('visual_summary') or b.get('visual_prompt') or ''
    print(f"Beat {idx:02d} | WAV Dur: {dur:.2f}s | Audio File: beat_{idx}.wav")
    print(f"   VO: {txt}")
    print(f"   Visual intent: {vis}")
    total_dur += dur
    if total_dur >= 60:
        print(f"Reached {total_dur:.2f}s at Beat {idx}")
        break
