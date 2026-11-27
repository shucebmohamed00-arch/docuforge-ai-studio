"""
DocuForge AI - Context-Aware Foley Fetcher
Downloads and cleans context-specific Foley:
1. typewriter_typing_burst.wav: Rapid mechanical typewriter key strikes
2. money_banknotes_counting.wav: Rapid counting of cash / paper money
3. cash_register_bell.wav: Classic mechanical cash register ding
"""

import os
import httpx
from pathlib import Path
import subprocess

FOLEY_DIR = Path("data/media/master_foley")
FOLEY_DIR.mkdir(parents=True, exist_ok=True)
KEY = "Z7klUv3Q8Cvnh0X8FSAr57g4C6q3UnawhCE5rvya"

SOUNDS_TO_GET = [
    {
        "query": "typewriter typing",
        "out_name": "typewriter_typing_burst.wav",
        "filter": "duration:[1.0 TO 4.0]"
    },
    {
        "query": "counting money banknotes",
        "out_name": "money_banknotes_counting.wav",
        "filter": "duration:[1.0 TO 5.0]"
    },
    {
        "query": "cash register bell",
        "out_name": "cash_register_bell.wav",
        "filter": "duration:[0.5 TO 3.0]"
    }
]

with httpx.Client(timeout=15.0) as client:
    for item in SOUNDS_TO_GET:
        target = FOLEY_DIR / item["out_name"]
        if target.exists() and target.stat().st_size > 5000:
            print(f"Already exists: {item['out_name']}")
            continue
            
        print(f"Searching Freesound for: {item['query']}...")
        url = "https://freesound.org/apiv2/search/text/"
        params = {
            "query": item["query"],
            "token": KEY,
            "fields": "id,name,previews",
            "filter": item["filter"],
            "page_size": 3
        }
        resp = client.get(url, params=params)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            if results:
                preview_url = results[0].get("previews", {}).get("preview-hq-mp3")
                if preview_url:
                    print(f"Downloading preview for '{results[0]['name']}'...")
                    mp3_data = client.get(preview_url).content
                    temp_mp3 = FOLEY_DIR / f"temp_{item['out_name']}.mp3"
                    temp_mp3.write_bytes(mp3_data)
                    
                    # Convert to 44.1kHz 16-bit PCM WAV with high-frequency rolloff (gentle lowpass at 5000Hz)
                    cmd = [
                        "ffmpeg", "-y",
                        "-i", str(temp_mp3),
                        "-af", "lowpass=f=5000,volume=1.0",
                        "-ar", "44100",
                        "-ac", "1",
                        str(target)
                    ]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    temp_mp3.unlink(missing_ok=True)
                    print(f"Saved & mastered: {target}")
print("Foley acquisition complete!")
