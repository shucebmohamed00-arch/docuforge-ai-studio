"""
DocuForge AI - Real-World Foley Harvester from Freesound API
Downloads authentic, high-quality documentary sound recordings.
"""

import urllib.request
import urllib.parse
import json
import subprocess
from pathlib import Path

API_KEY = "Z7klUv3Q8Cvnh0X8FSAr57g4C6q3UnawhCE5rvya"
OUT_DIR = Path("data/media/master_foley")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_SOUNDS = [
    ("vintage typewriter single key", "freesound_typewriter_single_key"),
    ("mechanical camera shutter click", "freesound_camera_shutter_click"),
    ("airplane seatbelt chime ding", "freesound_airplane_chime_ding"),
    ("office paper document slide", "freesound_paper_document_slide"),
    ("airport terminal announcement chime", "freesound_airport_announcement_chime"),
    ("jet engine taxiing runway", "freesound_jet_engine_tarmac"),
    ("bank vault door heavy slam", "freesound_bank_vault_slam"),
    ("tape recorder cassette button click", "freesound_cassette_button_click"),
    ("whisky glass clink table", "freesound_whisky_glass_clink"),
    ("protest crowd murmuring chanting", "freesound_protest_crowd_distant")
]

def main():
    print("Connecting to Freesound API with active credentials...")
    downloaded = 0
    for query, base_name in TARGET_SOUNDS:
        encoded_q = urllib.parse.quote(query)
        url = f"https://freesound.org/apiv2/search/text/?query={encoded_q}&token={API_KEY}&fields=id,name,previews,duration&page_size=3"
        req = urllib.request.Request(url, headers={"User-Agent": "DocuForge/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
                results = data.get("results", [])
                if results:
                    sound = results[0]
                    preview_url = sound.get("previews", {}).get("preview-hq-mp3")
                    if preview_url:
                        mp3_path = OUT_DIR / f"{base_name}.mp3"
                        wav_path = OUT_DIR / f"{base_name}.wav"
                        urllib.request.urlretrieve(preview_url, str(mp3_path))
                        # Convert to standard 44.1kHz WAV via FFmpeg
                        cmd = [
                            "ffmpeg", "-y",
                            "-i", str(mp3_path),
                            "-ar", "44100",
                            "-ac", "1",
                            str(wav_path)
                        ]
                        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                        if mp3_path.exists():
                            mp3_path.unlink()
                        dur = sound.get("duration", 0)
                        sname = sound.get("name", "")
                        print(f"  [OK] Downloaded '{base_name}.wav' ({dur:.1f}s) — \"{sname}\"")
                        downloaded += 1
        except Exception as e:
            print(f"  [FAIL] Error for '{query}': {e}")

    print(f"\nSuccessfully harvested {downloaded} authentic real-world sound effects from Freesound!")

if __name__ == "__main__":
    main()
