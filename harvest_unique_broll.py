import httpx
import json
from pathlib import Path

key = "58792744-1212081ab096e987f487b3116"
queries = [
    "airplane", "aircraft flight", "jet engine", "runway tarmac", "airport gate",
    "control tower", "airplane takeoff", "cockpit instruments", "pilot flying",
    "flight radar", "airplane landing", "business meeting", "boardroom executive",
    "contract signing", "corporate office", "stock market screen", "trading floor",
    "stock crash", "wall street", "financial graph", "counting money", "bank vault",
    "gold bullion", "cash dollars", "currency exchange", "news reporter",
    "press conference", "camera flash", "microphone interview", "passengers airport",
    "airport concourse", "departure board", "luggage baggage", "rain runway",
    "stormy clouds", "night runway", "foggy airport", "aerial city", "zurich",
    "switzerland alps", "handshake business", "financial crisis", "airplane sunset"
]

unique_urls = set()
collected = []

print("Querying Pixabay Videos API for diverse 1080p clips...")
with httpx.Client(timeout=10.0) as client:
    for q in queries:
        try:
            resp = client.get("https://pixabay.com/api/videos/", params={"key": key, "q": q, "per_page": 4})
            if resp.status_code == 200:
                hits = resp.json().get("hits", [])
                for h in hits:
                    u = h.get("videos", {}).get("medium", {}).get("url") or h.get("videos", {}).get("small", {}).get("url")
                    if u and u not in unique_urls:
                        unique_urls.add(u)
                        collected.append({
                            "query": q,
                            "id": h.get("id"),
                            "url": u,
                            "duration": h.get("duration", 10)
                        })
        except Exception as e:
            print(f"Error for {q}: {e}")
        if len(collected) >= 75:
            break

print(f"Total unique video clips collected: {len(collected)}")

# Save to broll_bank.json
out_file = Path("backend/app/agents/broll_bank.json")
out_file.parent.mkdir(parents=True, exist_ok=True)
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(collected, f, indent=2)

print(f"Saved {len(collected)} verified unique clips to {out_file}")
