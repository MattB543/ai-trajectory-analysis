# File created: 2025-10-12
# Purpose: Combine AI & Leviathan Parts I-III into single driver extraction
# Created by: AI assistant at user request to merge the three-part document

from pathlib import Path
import json

print("="*80)
print("COMBINING AI & LEVIATHAN PARTS I-III")
print("="*80)

# Load the three part files
parts = []
for i in range(1, 4):
    files = list(Path('outputs/extract_drivers_v2').glob(f'*_drivers_ai__leviathan_parts_iiii_-_full_doc_{i}.json'))

    if not files:
        print(f"[ERROR] Could not find drivers file for part {i}")
        continue

    print(f"[OK] Loading part {i}: {files[0].name}")
    data = json.load(open(files[0]))
    parts.append(data)

if len(parts) != 3:
    print(f"[ERROR] Expected 3 parts, found {len(parts)}")
    exit(1)

print(f"\n[OK] Loaded all 3 parts")

# Combine the drivers
combined = {
    "document_title": "AI & Leviathan (Parts I-III)",
    "extraction_notes": "Combined extraction from all three parts of the AI & Leviathan series.",
    "drivers": {
        "technological": [],
        "organizational": [],
        "governance": [],
        "societal": [],
        "safety_alignment": [],
        "geopolitical": [],
        "economic": [],
        "custom": []
    }
}

# Merge all drivers from all parts
for part_num, part_data in enumerate(parts, 1):
    print(f"\n[OK] Processing Part {part_num}:")

    for category, drivers in part_data.get('drivers', {}).items():
        if category not in combined['drivers']:
            combined['drivers'][category] = []

        for driver in drivers:
            # Add part number to driver name for tracking
            driver_copy = driver.copy()
            original_name = driver_copy['driver_name']
            driver_copy['driver_name'] = f"{original_name} (Part {part_num})"

            combined['drivers'][category].append(driver_copy)
            print(f"  - Added: {category}/{original_name}")

# Count total drivers
total_drivers = sum(len(drivers) for drivers in combined['drivers'].values())
print(f"\n[OK] Combined total drivers: {total_drivers}")

# Show breakdown by category
print("\n[OK] Driver breakdown:")
for category, drivers in combined['drivers'].items():
    if drivers:
        print(f"  - {category}: {len(drivers)} drivers")

# Save the combined file
from datetime import datetime
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_path = Path('outputs/extract_drivers_v2') / f"{timestamp}_drivers_ai__leviathan_combined.json"

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(combined, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Saved combined drivers to: {output_path.name}")

# Ask if user wants to delete the individual part files
print("\n" + "="*80)
print("[INFO] Individual part files are still present.")
print("[INFO] To delete them, uncomment the deletion code at the end of this script.")
print("="*80)

# Uncomment below to delete individual part files
# print("\n[OK] Deleting individual part files...")
# for i in range(1, 4):
#     files = list(Path('outputs/extract_drivers_v2').glob(f'*ai__leviathan_parts_iiii_-_full_doc_{i}.*'))
#     for f in files:
#         f.unlink()
#         print(f"  - Deleted: {f.name}")
# print("[OK] Individual parts deleted!")
