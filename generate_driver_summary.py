# File created: 2025-10-12
# Purpose: Generate CSV summary of driver counts by category and specific driver
# Created by: AI assistant at user request

from pathlib import Path
import json
import csv
from collections import defaultdict

print("="*80)
print("GENERATING DRIVER SUMMARY CSV")
print("="*80)

output_dir = Path('outputs/extract_drivers_v2')

# Load all driver JSON files
driver_files = list(output_dir.glob('*_drivers_*.json'))
print(f"[OK] Found {len(driver_files)} driver files")

# Count drivers by category and by specific driver name
category_counts = defaultdict(int)
driver_counts = defaultdict(lambda: defaultdict(int))  # category -> {driver_name: count}

for file in driver_files:
    try:
        data = json.load(open(file, encoding='utf-8'))

        if 'drivers' in data:
            for category, drivers in data['drivers'].items():
                if drivers:  # If there are drivers in this category
                    category_counts[category] += len(drivers)

                    # Count each specific driver
                    for driver in drivers:
                        driver_name = driver.get('driver_name', 'Unknown')
                        driver_counts[category][driver_name] += 1

    except Exception as e:
        print(f"[WARNING] Error processing {file.name}: {e}")

print(f"[OK] Processed {len(driver_files)} files")
print(f"[OK] Found {len(category_counts)} categories")

# Generate CSV
csv_path = Path('outputs/driver_summary.csv')

with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)

    # Header
    writer.writerow(['Category', 'Driver Name', 'Count'])

    # Write data sorted by category
    for category in sorted(category_counts.keys()):
        # Write category summary row
        writer.writerow([category, '[CATEGORY TOTAL]', category_counts[category]])

        # Write individual drivers sorted by count (descending)
        drivers_in_category = driver_counts[category]
        sorted_drivers = sorted(drivers_in_category.items(), key=lambda x: x[1], reverse=True)

        for driver_name, count in sorted_drivers:
            writer.writerow([category, driver_name, count])

        # Empty row for readability
        writer.writerow([])

print(f"\n[OK] Saved CSV to: {csv_path}")

# Also print summary to console
print("\n" + "="*80)
print("SUMMARY BY CATEGORY")
print("="*80)

total_drivers = sum(category_counts.values())
print(f"\nTotal drivers across all documents: {total_drivers}\n")

for category in sorted(category_counts.keys()):
    count = category_counts[category]
    print(f"{category:30s} {count:4d} drivers")

print("\n" + "="*80)
print("TOP 10 MOST COMMON DRIVERS")
print("="*80)

# Flatten all drivers and sort by count
all_drivers = []
for category, drivers in driver_counts.items():
    for driver_name, count in drivers.items():
        all_drivers.append((driver_name, category, count))

all_drivers.sort(key=lambda x: x[2], reverse=True)

print(f"\n{'Driver Name':<60} {'Category':<20} {'Count':>5}")
print("-" * 87)
for driver_name, category, count in all_drivers[:10]:
    print(f"{driver_name[:59]:<60} {category:<20} {count:>5}")

print("\n[OK] Complete!")
