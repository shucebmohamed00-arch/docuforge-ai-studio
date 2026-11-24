import json

with open("storyboard_items.json", "r", encoding="utf-8") as f:
    items = json.load(f)

print(f"Total Storyboard Beats: {len(items)}")
for i, it in enumerate(items):
    print(f"Beat {i+1:02d} [Scene {it.get('scene_number')}]: {it.get('narration_text')}")
