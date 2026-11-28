import sqlite3

conn = sqlite3.connect('data/docuforge.db')
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT order_index, scene_number, duration_sec, narration_text FROM storyboard_items WHERE project_id='swiss-air-grounding-prod' ORDER BY order_index").fetchall()
print(f"Number of beats: {len(rows)}")
total_sec = sum(r['duration_sec'] for r in rows)
print(f"Total planned duration: {total_sec:.1f}s ({total_sec/60:.2f} mins)")
print("\nSample beats across the whole story:")
for r in rows[::7]:
    print(f"Beat {r['order_index']:02d} (Scene {r['scene_number']}): {r['duration_sec']}s - {r['narration_text'][:60]}...")
