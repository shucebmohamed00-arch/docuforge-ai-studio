import re
import collections

with open('tools/assemble_ten_minute_master.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Match lines inside CONTEXTUAL_ASSETS
block_match = re.search(r'CONTEXTUAL_ASSETS\s*=\s*\{(.*?)\n\}', text, re.DOTALL)
if not block_match:
    print("Could not find CONTEXTUAL_ASSETS")
    exit(1)

block = block_match.group(1)
items = re.findall(r'(\w+_DIR)\s*/\s*"([^"]+)"', block)

all_assets = [f"{dir_name}/{asset_name}" for dir_name, asset_name in items]

counts = collections.Counter(all_assets)
duplicates = {k: v for k, v in counts.items() if v > 1}

print(f"Total Asset Usages: {len(all_assets)}")
print(f"Unique Assets: {len(counts)}")
print(f"Duplicates: {len(duplicates)}")

if duplicates:
    print("DUPLICATE ASSETS FOUND:")
    for k, v in sorted(duplicates.items(), key=lambda x: -x[1]):
        print(f"  {v}x: {k}")
    exit(1)
else:
    print("SUCCESS: EXACTLY ZERO DUPLICATES FOUND ACROSS ALL 76 BEATS!")
