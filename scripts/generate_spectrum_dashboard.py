"""
Spectrum Dashboard Generator Script

Created by: Claude Code Agent
Purpose: Generates a complete HTML dashboard for a specific driver by combining the template with extracted data
This file was created as part of the spectrum dashboard system for visualizing driver distributions.
"""

import json
import os
import sys
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path


def sanitize_filename(name):
    """Sanitize driver name for use in filenames"""
    return "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in name).strip().replace(' ', '_').lower()


def generate_dashboard(driver_name, open_browser=True):
    """
    Generate a complete HTML dashboard for a specific driver

    Args:
        driver_name: Name of the driver to generate dashboard for
        open_browser: Whether to open the dashboard in browser after generation

    Returns:
        Path to the generated HTML file
    """
    print(f"[OK] Starting dashboard generation for: {driver_name}")

    # Get paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    template_path = project_root / "outputs" / "spectrum_dashboards" / "spectrum_template.html"
    data_dir = project_root / "outputs" / "spectrum_dashboards" / "data"
    output_dir = project_root / "outputs" / "spectrum_dashboards"

    # Validate template exists
    if not template_path.exists():
        print(f"[ERROR] Template file not found: {template_path}")
        sys.exit(1)

    print(f"[OK] Template found: {template_path}")

    # Step 1: Run data extraction script
    print(f"[OK] Running data extraction...")
    extraction_script = script_dir / "generate_spectrum_data.py"

    try:
        result = subprocess.run(
            [sys.executable, str(extraction_script), driver_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Data extraction failed:")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)

    # Step 2: Find the most recent data file for this driver
    print(f"[OK] Looking for generated data file...")
    sanitized_name = sanitize_filename(driver_name)
    data_files = list(data_dir.glob(f"*_spectrum_data_{sanitized_name}.json"))

    if not data_files:
        print(f"[ERROR] No data file found for driver: {driver_name}")
        sys.exit(1)

    # Sort by modification time and get the most recent
    data_file = max(data_files, key=lambda p: p.stat().st_mtime)
    print(f"[OK] Using data file: {data_file.name}")

    # Step 3: Load the data
    with open(data_file, 'r', encoding='utf-8') as f:
        driver_data = json.load(f)

    print(f"[OK] Loaded data: {driver_data['total_occurrences']} occurrences across {driver_data['documents_with_driver']} documents")

    # Step 4: Load template
    with open(template_path, 'r', encoding='utf-8') as f:
        template_html = f.read()

    # Step 5: Embed data into template
    # Replace the placeholder with actual data
    data_js = f"const driverData = {json.dumps(driver_data, ensure_ascii=False, indent=2)};"
    dashboard_html = template_html.replace(
        "// DATA_PLACEHOLDER - This will be replaced with actual data\n        const driverData = null;",
        data_js
    )

    # Step 6: Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{timestamp}_spectrum_{sanitized_name}.html"
    output_path = output_dir / output_filename

    # Step 7: Write the dashboard file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(dashboard_html)

    print(f"[OK] Dashboard generated: {output_path}")
    print(f"[OK] File size: {output_path.stat().st_size / 1024:.2f} KB")

    # Step 8: Open in browser
    if open_browser:
        print(f"[OK] Opening dashboard in default browser...")
        try:
            webbrowser.open(f'file:///{output_path.as_posix()}')
            print(f"[OK] Dashboard opened successfully!")
        except Exception as e:
            print(f"[WARNING] Could not open browser automatically: {e}")
            print(f"[WARNING] Please open manually: {output_path}")

    return output_path


def main():
    if len(sys.argv) < 2:
        print("[ERROR] Usage: python generate_spectrum_dashboard.py <driver_name> [--no-browser]")
        print("[ERROR] Example: python generate_spectrum_dashboard.py \"Economic Automation and Labor Market Transformation\"")
        print("[ERROR] Options:")
        print("[ERROR]   --no-browser: Don't open the dashboard in browser after generation")
        sys.exit(1)

    driver_name = sys.argv[1]
    open_browser = "--no-browser" not in sys.argv

    print(f"[OK] ===================================")
    print(f"[OK] Spectrum Dashboard Generator")
    print(f"[OK] ===================================")
    print(f"[OK] Driver: {driver_name}")
    print(f"[OK] Open Browser: {open_browser}")
    print(f"[OK] ===================================")

    try:
        output_path = generate_dashboard(driver_name, open_browser)
        print(f"[OK] ===================================")
        print(f"[OK] SUCCESS!")
        print(f"[OK] Dashboard: {output_path}")
        print(f"[OK] ===================================")
    except Exception as e:
        print(f"[ERROR] Dashboard generation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
