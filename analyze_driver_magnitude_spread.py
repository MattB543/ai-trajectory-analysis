# This script was created by an agent for analysis purposes.
# Purpose: Analyze driver files to identify drivers with the widest magnitude spread (low/medium/high)
# across all documents in the outputs/extract_drivers_v2 folder.
#
# The script:
# 1. Reads all JSON files matching "*_drivers_*.json" pattern
# 2. Extracts all drivers with their magnitude values
# 3. Counts occurrences of each unique driver across all documents
# 4. Filters to drivers appearing 15+ times
# 5. Calculates magnitude spread (low, medium, high counts)
# 6. Identifies top 3 drivers with widest magnitude spread
# 7. Outputs detailed report with analysis results

import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import math

def normalize_magnitude(magnitude):
    """Normalize magnitude values to low, medium, or high."""
    if not magnitude:
        return None
    mag_lower = magnitude.lower().strip()

    # Handle "Medium-High" -> "medium"
    if 'medium' in mag_lower:
        return 'medium'
    elif 'high' in mag_lower:
        return 'high'
    elif 'low' in mag_lower:
        return 'low'
    else:
        return None

def calculate_spread_metric(low_count, medium_count, high_count):
    """
    Calculate spread metric using coefficient of variation.
    Higher values indicate wider spread across magnitude categories.
    """
    counts = [low_count, medium_count, high_count]
    total = sum(counts)

    if total == 0:
        return 0

    # Calculate standard deviation
    mean = total / 3
    variance = sum((x - mean) ** 2 for x in counts) / 3
    std_dev = math.sqrt(variance)

    # Coefficient of variation (normalized by mean)
    if mean > 0:
        cv = std_dev / mean
    else:
        cv = 0

    # Also calculate entropy-based metric (Shannon entropy normalized)
    # This measures how evenly distributed the magnitudes are
    entropy = 0
    for count in counts:
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    # Normalize entropy (max is log2(3) ≈ 1.585)
    normalized_entropy = entropy / 1.585 if entropy > 0 else 0

    # Combined metric: average of CV and normalized entropy
    # This captures both variance and evenness of distribution
    combined_metric = (cv + normalized_entropy) / 2

    return combined_metric

def main():
    print("[OK] Starting driver magnitude spread analysis...")

    # Set up paths
    base_dir = Path(r"C:\Users\matth\projects\ai-trajectory-analysis")
    input_dir = base_dir / "outputs" / "extract_drivers_v2"
    output_dir = base_dir / "outputs" / "analyze_driver_magnitude_spread"

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Output directory created/verified: {output_dir}")

    # Find all driver JSON files
    driver_files = list(input_dir.glob("*_drivers_*.json"))
    print(f"[OK] Found {len(driver_files)} driver files to analyze")

    if not driver_files:
        print("[ERROR] No driver files found!")
        return

    # Data structures to track drivers
    driver_occurrences = defaultdict(int)  # Total count per driver
    driver_magnitudes = defaultdict(lambda: {'low': 0, 'medium': 0, 'high': 0, 'none': 0})

    # Process each file
    processed_files = 0
    skipped_files = 0

    for file_path in driver_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract all drivers from all categories
            drivers_dict = data.get('drivers', {})

            for category, drivers_list in drivers_dict.items():
                if not isinstance(drivers_list, list):
                    continue

                for driver in drivers_list:
                    driver_name = driver.get('driver_name', '').strip()
                    magnitude = driver.get('magnitude', '')

                    if not driver_name:
                        continue

                    # Count occurrence
                    driver_occurrences[driver_name] += 1

                    # Track magnitude
                    normalized_mag = normalize_magnitude(magnitude)
                    if normalized_mag:
                        driver_magnitudes[driver_name][normalized_mag] += 1
                    else:
                        driver_magnitudes[driver_name]['none'] += 1

            processed_files += 1

        except Exception as e:
            print(f"[ERROR] Failed to process {file_path.name}: {e}")
            skipped_files += 1

    print(f"[OK] Processed {processed_files} files successfully")
    if skipped_files > 0:
        print(f"[ERROR] Skipped {skipped_files} files due to errors")

    # Filter to drivers appearing 15+ times
    frequent_drivers = {
        name: count for name, count in driver_occurrences.items()
        if count >= 15
    }

    print(f"[OK] Found {len(frequent_drivers)} drivers appearing 15+ times")

    if not frequent_drivers:
        print("[ERROR] No drivers found with 15+ occurrences!")
        return

    # Calculate spread metrics for frequent drivers
    driver_spread_analysis = []

    for driver_name in frequent_drivers:
        mags = driver_magnitudes[driver_name]
        low_count = mags['low']
        medium_count = mags['medium']
        high_count = mags['high']
        none_count = mags['none']
        total_count = driver_occurrences[driver_name]

        # Calculate spread metric
        spread_metric = calculate_spread_metric(low_count, medium_count, high_count)

        driver_spread_analysis.append({
            'driver_name': driver_name,
            'total_occurrences': total_count,
            'low': low_count,
            'medium': medium_count,
            'high': high_count,
            'none': none_count,
            'spread_metric': spread_metric
        })

    # Sort by spread metric (descending)
    driver_spread_analysis.sort(key=lambda x: x['spread_metric'], reverse=True)

    # Get top 3
    top_3 = driver_spread_analysis[:3]

    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{timestamp}_driver_magnitude_spread_analysis_top3_widest_distribution_min15occurrences.txt"
    output_path = output_dir / output_filename

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("DRIVER MAGNITUDE SPREAD ANALYSIS\n")
        f.write("="*80 + "\n\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Files Analyzed: {processed_files}\n")
        f.write(f"Total Unique Drivers: {len(driver_occurrences)}\n")
        f.write(f"Drivers with 15+ Occurrences: {len(frequent_drivers)}\n\n")

        f.write("="*80 + "\n")
        f.write("SPREAD METRIC EXPLANATION\n")
        f.write("="*80 + "\n\n")
        f.write("The spread metric combines two statistical measures:\n\n")
        f.write("1. Coefficient of Variation (CV): Measures the relative variability\n")
        f.write("   of magnitude counts. Higher values indicate greater spread.\n\n")
        f.write("2. Normalized Shannon Entropy: Measures how evenly distributed\n")
        f.write("   the magnitudes are across low/medium/high categories.\n")
        f.write("   Maximum entropy (1.0) = perfectly even distribution.\n\n")
        f.write("Combined Metric = (CV + Normalized Entropy) / 2\n\n")
        f.write("Higher values indicate wider magnitude spread with more varied\n")
        f.write("distribution across low, medium, and high categories.\n\n")

        f.write("="*80 + "\n")
        f.write("TOP 3 DRIVERS WITH WIDEST MAGNITUDE SPREAD\n")
        f.write("="*80 + "\n\n")

        for i, driver in enumerate(top_3, 1):
            f.write(f"RANK #{i}\n")
            f.write("-"*80 + "\n")
            f.write(f"Driver Name: {driver['driver_name']}\n\n")
            f.write(f"Total Occurrences: {driver['total_occurrences']}\n")
            f.write(f"Spread Metric: {driver['spread_metric']:.4f}\n\n")
            f.write("Magnitude Distribution:\n")
            f.write(f"  Low:    {driver['low']:3d} occurrences ({driver['low']/driver['total_occurrences']*100:5.1f}%)\n")
            f.write(f"  Medium: {driver['medium']:3d} occurrences ({driver['medium']/driver['total_occurrences']*100:5.1f}%)\n")
            f.write(f"  High:   {driver['high']:3d} occurrences ({driver['high']/driver['total_occurrences']*100:5.1f}%)\n")
            if driver['none'] > 0:
                f.write(f"  None:   {driver['none']:3d} occurrences ({driver['none']/driver['total_occurrences']*100:5.1f}%)\n")
            f.write("\n")

            # Visual representation
            total_with_mag = driver['low'] + driver['medium'] + driver['high']
            if total_with_mag > 0:
                f.write("Visual Distribution (only low/medium/high):\n")
                low_bar = "█" * int(driver['low'] / total_with_mag * 40)
                med_bar = "█" * int(driver['medium'] / total_with_mag * 40)
                high_bar = "█" * int(driver['high'] / total_with_mag * 40)
                f.write(f"  Low:    [{low_bar:<40}]\n")
                f.write(f"  Medium: [{med_bar:<40}]\n")
                f.write(f"  High:   [{high_bar:<40}]\n")
            f.write("\n")

        # Summary statistics
        f.write("="*80 + "\n")
        f.write("SUMMARY STATISTICS FOR ALL DRIVERS (15+ OCCURRENCES)\n")
        f.write("="*80 + "\n\n")

        # Calculate overall statistics
        spread_metrics = [d['spread_metric'] for d in driver_spread_analysis]
        avg_spread = sum(spread_metrics) / len(spread_metrics)

        f.write(f"Average Spread Metric: {avg_spread:.4f}\n")
        f.write(f"Highest Spread Metric: {max(spread_metrics):.4f}\n")
        f.write(f"Lowest Spread Metric: {min(spread_metrics):.4f}\n\n")

        f.write("="*80 + "\n")
        f.write("COMPLETE LIST OF DRIVERS (15+ OCCURRENCES) BY SPREAD METRIC\n")
        f.write("="*80 + "\n\n")
        f.write(f"{'Rank':<6} {'Spread':<8} {'Total':<7} {'Low':<5} {'Med':<5} {'High':<5} {'Driver Name'}\n")
        f.write("-"*80 + "\n")

        for i, driver in enumerate(driver_spread_analysis, 1):
            f.write(f"{i:<6} {driver['spread_metric']:>6.4f}  {driver['total_occurrences']:>5}  "
                   f"{driver['low']:>4}  {driver['medium']:>4}  {driver['high']:>4}  "
                   f"{driver['driver_name']}\n")

    print(f"[OK] Analysis complete!")
    print(f"[OK] Report saved to: {output_path}")
    print(f"\n[OK] TOP 3 DRIVERS WITH WIDEST MAGNITUDE SPREAD:")
    print("="*80)

    for i, driver in enumerate(top_3, 1):
        print(f"\n#{i}: {driver['driver_name']}")
        print(f"    Total Occurrences: {driver['total_occurrences']}")
        print(f"    Spread Metric: {driver['spread_metric']:.4f}")
        print(f"    Low: {driver['low']} ({driver['low']/driver['total_occurrences']*100:.1f}%)")
        print(f"    Medium: {driver['medium']} ({driver['medium']/driver['total_occurrences']*100:.1f}%)")
        print(f"    High: {driver['high']} ({driver['high']/driver['total_occurrences']*100:.1f}%)")

if __name__ == "__main__":
    main()
