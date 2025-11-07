# File created: 2025-10-12
# Purpose: Collect all custom drivers from extracted data into a single JSON list
# Created by: AI assistant at user request

from pathlib import Path
import json

print("="*80)
print("COLLECTING CUSTOM DRIVERS")
print("="*80)

output_dir = Path('outputs/extract_drivers_v2')

# Load all driver JSON files
driver_files = list(output_dir.glob('*_drivers_*.json'))
print(f"[OK] Found {len(driver_files)} driver files")

# Collect all custom drivers across ALL categories
all_custom_drivers = []

for file in driver_files:
    try:
        data = json.load(open(file, encoding='utf-8'))

        if 'drivers' in data:
            doc_title = data.get('document_title', file.name)

            # Search ALL categories for drivers with "Custom" in the name
            for category, drivers in data['drivers'].items():
                if drivers:
                    for driver in drivers:
                        driver_name = driver.get('driver_name', '')

                        # Check if "Custom" appears in the driver name (case insensitive)
                        if 'custom' in driver_name.lower():
                            print(f"[OK] Found custom driver in {category}: {driver_name}")

                            # Add metadata
                            driver['category'] = category
                            driver['source_document'] = doc_title
                            driver['source_file'] = file.name
                            all_custom_drivers.append(driver)

    except Exception as e:
        print(f"[WARNING] Error processing {file.name}: {e}")

print(f"\n[OK] Total custom drivers collected: {len(all_custom_drivers)}")

# Save to JSON
output_path = Path('outputs/custom_drivers_collection.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_custom_drivers, f, indent=2, ensure_ascii=False)

print(f"[OK] Saved to: {output_path}")

# Print summary
print("\n" + "="*80)
print("CUSTOM DRIVERS SUMMARY")
print("="*80)

for i, driver in enumerate(all_custom_drivers, 1):
    print(f"\n{i}. {driver.get('driver_name', 'Unknown')}")
    print(f"   Category: {driver.get('category', 'Unknown')}")
    print(f"   Source: {driver.get('source_document', 'Unknown')}")

print("\n[OK] Complete!")
