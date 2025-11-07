"""
Generate All Driver Spectrum Pages

Created by: Claude Code Agent
Purpose: Generates spectrum dashboard HTML pages for all drivers with correct naming convention
Created at request of user to ensure navigation from home page works correctly
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def sanitize_filename(name):
    """Sanitize driver name for use in filenames"""
    return "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in name).strip().replace(' ', '_').lower()


def extract_driver_data(input_dir, driver_name):
    """
    Extract data for a specific driver across all documents

    Args:
        input_dir: Directory containing driver JSON files
        driver_name: Name of the driver to extract

    Returns:
        Dictionary with driver data organized by magnitude
    """
    driver_instances = {
        "None": [],
        "Low": [],
        "Medium": [],
        "High": []
    }

    total_documents = 0
    input_path = Path(input_dir)
    json_files = list(input_path.glob("*_drivers_*.json"))

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            total_documents += 1
            document_title = data.get('document_title', 'Unknown Document')
            found_driver = False

            # Search for this driver
            for category, drivers in data.get('drivers', {}).items():
                if not isinstance(drivers, list):
                    continue

                for driver in drivers:
                    if driver.get('driver_name', '').strip() == driver_name:
                        magnitude = driver.get('magnitude', 'None')
                        if magnitude is None or magnitude == '':
                            magnitude = 'None'

                        # Handle compound magnitudes
                        if '-' in str(magnitude):
                            magnitude = str(magnitude).split('-')[-1]

                        if magnitude not in ["None", "Low", "Medium", "High"]:
                            magnitude = 'None'

                        # Extract complete driver information
                        driver_instances[magnitude].append({
                            "document_title": document_title,
                            "description": driver.get('description', 'No description provided'),
                            "magnitude": magnitude,
                            "certainty": driver.get('certainty', 'Unknown'),
                            "category": category,
                            "direction": driver.get('direction', 'Not specified'),
                            "evidence": driver.get('evidence', '')
                        })
                        found_driver = True
                        break

                if found_driver:
                    break

            # If driver not found in this document, add to None
            if not found_driver:
                driver_instances["None"].append({
                    "document_title": document_title,
                    "description": "This document does not mention or discuss this driver",
                    "magnitude": "None",
                    "certainty": "N/A",
                    "category": "None",
                    "direction": "N/A",
                    "evidence": ""
                })

        except Exception as e:
            print(f"[ERROR] Failed to process {json_file.name}: {e}")

    # Calculate statistics
    documents_with_driver = (
        len(driver_instances["Low"]) +
        len(driver_instances["Medium"]) +
        len(driver_instances["High"])
    )

    # Use field names expected by template
    return {
        "driver_name": driver_name,
        "total_documents_processed": total_documents,
        "documents_with_driver": documents_with_driver,
        "documents_without_driver": len(driver_instances["None"]),
        "total_occurrences": documents_with_driver,
        "magnitude_counts": {
            "None": len(driver_instances["None"]),
            "Low": len(driver_instances["Low"]),
            "Medium": len(driver_instances["Medium"]),
            "High": len(driver_instances["High"])
        },
        "magnitude_distribution": driver_instances,
        "generated_at": datetime.now().isoformat()
    }


def generate_driver_page(driver_name, driver_data, template_path, output_path):
    """
    Generate HTML page for a specific driver

    Args:
        driver_name: Name of the driver
        driver_data: Data dictionary for the driver
        template_path: Path to HTML template
        output_path: Path to save generated HTML
    """
    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Embed data into template
    data_js = f"const driverData = {json.dumps(driver_data, ensure_ascii=False, indent=2)};"
    html = template.replace(
        "// DATA_PLACEHOLDER - This will be replaced with actual data\n        const driverData = null;",
        data_js
    )

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


def get_drivers_to_generate(input_dir):
    """
    Get list of drivers that should have pages (those with >= 12 occurrences)

    Args:
        input_dir: Directory containing driver JSON files

    Returns:
        List of driver names
    """
    driver_counts = defaultdict(int)
    input_path = Path(input_dir)
    json_files = list(input_path.glob("*_drivers_*.json"))

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for category, drivers in data.get('drivers', {}).items():
                if not isinstance(drivers, list):
                    continue

                for driver in drivers:
                    driver_name = driver.get('driver_name', '').strip()
                    if driver_name:
                        magnitude = driver.get('magnitude', 'None')
                        # Only count actual occurrences (not None)
                        if magnitude and magnitude != 'None':
                            driver_counts[driver_name] += 1

        except Exception:
            pass

    # Filter to drivers with >= 12 occurrences
    return [name for name, count in driver_counts.items() if count >= 12]


def main():
    print("[OK] Starting generation of all driver spectrum pages...")

    # Get paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    input_dir = project_root / "outputs" / "extract_drivers_v2"
    template_path = project_root / "outputs" / "spectrum_dashboards" / "spectrum_template.html"
    output_dir = project_root / "outputs" / "spectrum_dashboards"

    # Validate paths
    if not input_dir.exists():
        print(f"[ERROR] Input directory not found: {input_dir}")
        return 1

    if not template_path.exists():
        print(f"[ERROR] Template not found: {template_path}")
        return 1

    # Get list of drivers to generate
    print("[OK] Finding drivers to generate...")
    drivers = get_drivers_to_generate(input_dir)
    print(f"[OK] Found {len(drivers)} drivers with >= 12 occurrences")

    if not drivers:
        print("[ERROR] No drivers found!")
        return 1

    # Generate page for each driver
    generated_count = 0
    for i, driver_name in enumerate(sorted(drivers), 1):
        print(f"\n[{i}/{len(drivers)}] Generating page for: {driver_name}")

        try:
            # Extract driver data
            driver_data = extract_driver_data(input_dir, driver_name)
            print(f"    [OK] {driver_data['documents_with_driver']} documents with driver")

            # Generate sanitized filename
            sanitized_name = sanitize_filename(driver_name)
            output_filename = f"{sanitized_name}_spectrum.html"
            output_path = output_dir / output_filename

            # Generate page
            generate_driver_page(driver_name, driver_data, template_path, output_path)
            print(f"    [OK] Generated: {output_filename}")
            generated_count += 1

        except Exception as e:
            print(f"    [ERROR] Failed to generate page: {e}")
            continue

    print(f"\n[OK] ===================================")
    print(f"[OK] Generation complete!")
    print(f"[OK] Successfully generated: {generated_count}/{len(drivers)} pages")
    print(f"[OK] Output directory: {output_dir}")
    print(f"[OK] ===================================")

    return 0


if __name__ == "__main__":
    exit(main())
