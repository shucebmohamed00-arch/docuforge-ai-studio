import os
import shutil
import zipfile
from pathlib import Path

export_dir = Path("data/exports/swiss-air-grounding-prod")
web_mp4 = export_dir / "documentary_web.mp4"
master_mp4 = export_dir / "documentary.mp4"
pkg_zip = export_dir / "docuforge_package.zip"

if web_mp4.exists():
    if master_mp4.exists():
        master_mp4.unlink()
    shutil.move(str(web_mp4), str(master_mp4))
    print(f"Moved {web_mp4.name} to {master_mp4.name} ({master_mp4.stat().st_size / (1024*1024):.2f} MB)")

# Remove intermediate wavs and txt
for f in export_dir.glob("*.wav"):
    f.unlink()
for f in export_dir.glob("v_concat.txt"):
    f.unlink()

# Repackage docuforge_package.zip
if pkg_zip.exists():
    pkg_zip.unlink()

print("Creating docuforge_package.zip (stored mode for zero overhead)...")
with zipfile.ZipFile(str(pkg_zip), "w", compression=zipfile.ZIP_STORED) as zf:
    zf.write(str(master_mp4), arcname="documentary.mp4")
    srt_file = export_dir / "subtitles.srt"
    if srt_file.exists():
        zf.write(str(srt_file), arcname="subtitles.srt")
    for thumb in export_dir.glob("thumbnail*.jpg"):
        zf.write(str(thumb), arcname=thumb.name)

print(f"Package ready: {pkg_zip.name} ({pkg_zip.stat().st_size / (1024*1024):.2f} MB)")
for f in sorted(export_dir.iterdir()):
    print(f"  - {f.name}: {f.stat().st_size / (1024*1024):.2f} MB")
