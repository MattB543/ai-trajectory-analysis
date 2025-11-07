"""
Data Extraction Script for Spectrum Dashboard System

Created by: Claude Code Agent
Purpose: Extracts driver occurrences across all trajectory documents and organizes them by magnitude
This file was created as part of the spectrum dashboard system for visualizing driver distributions.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict


def sanitize_filename(name):
    """Sanitize driver name for use in filenames"""
    return "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in name).strip().replace(' ', '_').lower()


def extract_driver_data(driver_name, input_dir, output_dir):
    """
    Extract all occurrences of a specific driver across all documents

    Args:
        driver_name: Name of the driver to search for (case-insensitive)
        input_dir: Directory containing driver JSON files
        output_dir: Directory to save output JSON

    Returns:
        Path to the generated JSON file
    """
    print(f"[OK] Starting extraction for driver: {driver_name}")

    # Initialize data structure
    magnitude_distribution = {
        "None": [],
        "Low": [],
        "Medium": [],
        "High": []
    }

    total_occurrences = 0
    files_processed = 0
    files_with_driver = 0

    # Track which documents have been processed with this driver
    documents_with_driver = set()

    # Process all JSON files
    input_path = Path(input_dir)
    json_files = list(input_path.glob("*_drivers_*.json"))

    print(f"[OK] Found {len(json_files)} driver JSON files to process")

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            files_processed += 1
            document_title = data.get('document_title', 'Unknown Document')
            driver_found = False

            # Search through all driver categories
            for category, drivers in data.get('drivers', {}).items():
                if not isinstance(drivers, list):
                    continue

                for driver in drivers:
                    # Case-insensitive comparison
                    if driver.get('driver_name', '').lower() == driver_name.lower():
                        driver_found = True
                        total_occurrences += 1

                        # Get magnitude (default to "None" if not specified)
                        magnitude = driver.get('magnitude', 'None')
                        if magnitude is None or magnitude == '':
                            magnitude = 'None'

                        # Handle compound magnitudes like "Medium-High"
                        if '-' in str(magnitude):
                            magnitude = str(magnitude).split('-')[-1]

                        # Ensure magnitude is valid
                        if magnitude not in magnitude_distribution:
                            print(f"[WARNING] Unknown magnitude '{magnitude}' in {document_title}, defaulting to 'None'")
                            magnitude = 'None'

                        # Create entry
                        entry = {
                            "document_title": document_title,
                            "magnitude": magnitude,
                            "certainty": driver.get('certainty', 'Unknown'),
                            "description": driver.get('description', ''),
                            "direction": driver.get('direction', ''),
                            "evidence": driver.get('evidence', ''),
                            "category": category
                        }

                        magnitude_distribution[magnitude].append(entry)
                        documents_with_driver.add(document_title)

            if driver_found:
                files_with_driver += 1
            else:
                # Document does not contain this driver - add to "None" category
                none_entry = {
                    "document_title": document_title,
                    "magnitude": "None",
                    "certainty": "N/A",
                    "description": "This driver was not identified or analyzed in this document.",
                    "direction": "N/A",
                    "evidence": "",
                    "category": "unspecified"
                }
                magnitude_distribution["None"].append(none_entry)

        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse {json_file.name}: {e}")
        except Exception as e:
            print(f"[ERROR] Error processing {json_file.name}: {e}")

    print(f"[OK] Processed {files_processed} files")
    print(f"[OK] Found driver in {files_with_driver} documents")
    print(f"[OK] Total occurrences: {total_occurrences}")

    # Print distribution
    for mag in ["None", "Low", "Medium", "High"]:
        count = len(magnitude_distribution[mag])
        print(f"[OK]   {mag}: {count} occurrences")

    if total_occurrences == 0:
        print(f"[WARNING] No occurrences found for driver: {driver_name}")
        print(f"[WARNING] This might mean:")
        print(f"[WARNING]   - The driver name doesn't match any in the documents")
        print(f"[WARNING]   - The driver name spelling is different")
        print(f"[WARNING]   - The driver doesn't exist in the current dataset")
        return None

    # Create output structure
    output_data = {
        "driver_name": driver_name,
        "total_occurrences": total_occurrences,
        "documents_with_driver": files_with_driver,
        "total_documents_processed": files_processed,
        "magnitude_distribution": magnitude_distribution,
        "generated_at": datetime.now().isoformat()
    }

    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_name = sanitize_filename(driver_name)
    output_filename = f"{timestamp}_spectrum_data_{sanitized_name}.json"
    output_path = Path(output_dir) / output_filename

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"[OK] Data saved to: {output_path}")

    return output_path


def main():
    if len(sys.argv) < 2:
        print("[ERROR] Usage: python generate_spectrum_data.py <driver_name>")
        print("[ERROR] Example: python generate_spectrum_data.py \"Economic Automation and Labor Market Transformation\"")
        sys.exit(1)

    driver_name = sys.argv[1]

    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    input_dir = project_root / "outputs" / "extract_drivers_v2"
    output_dir = project_root / "outputs" / "spectrum_dashboards" / "data"

    # Validate directories
    if not input_dir.exists():
        print(f"[ERROR] Input directory not found: {input_dir}")
        sys.exit(1)

    if not output_dir.exists():
        print(f"[OK] Creating output directory: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)

    # Extract data
    output_path = extract_driver_data(driver_name, input_dir, output_dir)

    if output_path:
        print(f"[OK] Extraction complete!")
        print(f"[OK] Output file: {output_path}")
    else:
        print(f"[ERROR] Extraction failed - no data found")
        sys.exit(1)


if __name__ == "__main__":
    main()
