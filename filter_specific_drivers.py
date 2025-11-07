# File created by Claude Code on 2025-10-12
# Purpose: Remove driver files that are too specific (>12 docs in "none" category)
# Direct request from user to filter out rare/specific drivers

import json
import os
from pathlib import Path

def main():
    print("[OK] Identifying drivers with >12 docs in 'none' category...")

    grouped_drivers_path = Path('outputs/grouped_drivers')

    # Find all grouped driver JSON files
    driver_files = list(grouped_drivers_path.glob('*_grouped_*.json'))
    print(f"[OK] Found {len(driver_files)} driver files")

    files_to_remove = []
    files_to_keep = []

    for driver_file in driver_files:
        # Skip summary files
        if 'summary' in driver_file.name:
            continue

        try:
            with open(driver_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            none_count = len(data.get('none', []))
            driver_name = data.get('driver_name', 'Unknown')
            total_docs = data.get('statistics', {}).get('total_documents', 21)
            docs_with_driver = total_docs - none_count

            if none_count > 12:
                files_to_remove.append({
                    'file': driver_file,
                    'name': driver_name,
                    'none_count': none_count,
                    'with_driver': docs_with_driver
                })
            else:
                files_to_keep.append({
                    'name': driver_name,
                    'none_count': none_count,
                    'with_driver': docs_with_driver
                })

        except Exception as e:
            print(f"[ERROR] Error processing {driver_file.name}: {e}")

    print(f"\n[OK] Analysis complete:")
    print(f"    Files to KEEP: {len(files_to_keep)}")
    print(f"    Files to REMOVE: {len(files_to_remove)}")

    if files_to_remove:
        print(f"\n[OK] Drivers to remove (too specific - present in <9 documents):")
        for item in sorted(files_to_remove, key=lambda x: x['with_driver']):
            print(f"    - {item['name']}: {item['with_driver']} docs have it, {item['none_count']} don't")

        # Remove the files
        print(f"\n[OK] Removing {len(files_to_remove)} files...")
        for item in files_to_remove:
            item['file'].unlink()
            print(f"    [OK] Removed: {item['file'].name}")
    else:
        print("[OK] No files to remove - all drivers are sufficiently common")

    print(f"\n[OK] Remaining drivers: {len(files_to_keep)}")
    print(f"[OK] Done!")

if __name__ == "__main__":
    main()
