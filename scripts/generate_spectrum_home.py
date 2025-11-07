"""
Home Page Generator for Spectrum Dashboard System

Created by: Claude Code Agent
Purpose: Generates comprehensive home page showing all drivers across all documents with magnitude distribution
Created at request of user to provide an overview page for the spectrum dashboard system.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict


def sanitize_filename(name):
    """Sanitize driver name for use in filenames"""
    return "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in name).strip().replace(' ', '_').lower()


def load_driver_analysis(analysis_dir):
    """
    Load Claude analysis for all drivers

    Args:
        analysis_dir: Directory containing analysis JSON files

    Returns:
        Dictionary mapping driver names to their analysis data
    """
    print("[OK] Loading Claude analysis files...")

    analysis_data = {}
    analysis_path = Path(analysis_dir)

    if not analysis_path.exists():
        print(f"[WARNING] Analysis directory not found: {analysis_dir}")
        return analysis_data

    analysis_files = list(analysis_path.glob("*_analysis_*.json"))
    print(f"[OK] Found {len(analysis_files)} analysis files")

    for analysis_file in analysis_files:
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            driver_name = data.get('driver_name')
            if driver_name:
                analysis_data[driver_name] = data.get('analysis', {})
        except Exception as e:
            print(f"[ERROR] Failed to load analysis from {analysis_file.name}: {e}")

    print(f"[OK] Loaded analysis for {len(analysis_data)} drivers")
    return analysis_data


def load_driver_summaries(summaries_dir):
    """
    Load Claude summaries for all drivers

    Args:
        summaries_dir: Directory containing summary JSON files

    Returns:
        Dictionary mapping driver names to their summaries
    """
    print("[OK] Loading driver summaries...")

    summaries = {}
    summaries_path = Path(summaries_dir)

    if not summaries_path.exists():
        print(f"[WARNING] Summaries directory not found: {summaries_dir}")
        return summaries

    summary_files = list(summaries_path.glob("*_summary_*.json"))
    print(f"[OK] Found {len(summary_files)} summary files")

    for summary_file in summary_files:
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            driver_name = data.get('driver_name')
            if driver_name:
                summaries[driver_name] = data.get('summary', {})
        except Exception as e:
            print(f"[ERROR] Failed to load summary from {summary_file.name}: {e}")

    print(f"[OK] Loaded summaries for {len(summaries)} drivers")
    return summaries


def extract_all_drivers(input_dir):
    """
    Extract all unique drivers across all documents with their magnitude distributions

    Args:
        input_dir: Directory containing driver JSON files

    Returns:
        Dictionary mapping driver names to their metadata and magnitude counts
    """
    print("[OK] Starting extraction of all drivers across documents")

    # Structure: {driver_name: {category: str, magnitudes: {None: count, Low: count, Medium: count, High: count}, analysis: dict}}
    all_drivers = defaultdict(lambda: {"category": "unspecified", "magnitudes": {"None": 0, "Low": 0, "Medium": 0, "High": 0}, "analysis": None})

    total_documents = 0
    input_path = Path(input_dir)
    json_files = list(input_path.glob("*_drivers_*.json"))

    print(f"[OK] Found {len(json_files)} driver JSON files to process")

    # Track all document titles
    all_document_titles = set()

    # First pass: collect all drivers and their occurrences
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            total_documents += 1
            document_title = data.get('document_title', 'Unknown Document')
            all_document_titles.add(document_title)

            # Search through all driver categories
            for category, drivers in data.get('drivers', {}).items():
                if not isinstance(drivers, list):
                    continue

                for driver in drivers:
                    driver_name = driver.get('driver_name', '').strip()
                    if not driver_name:
                        continue

                    # Get magnitude
                    magnitude = driver.get('magnitude', 'None')
                    if magnitude is None or magnitude == '':
                        magnitude = 'None'

                    # Handle compound magnitudes like "Medium-High"
                    if '-' in str(magnitude):
                        magnitude = str(magnitude).split('-')[-1]

                    # Ensure magnitude is valid
                    if magnitude not in ["None", "Low", "Medium", "High"]:
                        print(f"[WARNING] Unknown magnitude '{magnitude}' in {document_title}, defaulting to 'None'")
                        magnitude = 'None'

                    # Record this driver occurrence
                    if driver_name not in all_drivers:
                        all_drivers[driver_name]["category"] = category

                    all_drivers[driver_name]["magnitudes"][magnitude] += 1

        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse {json_file.name}: {e}")
        except Exception as e:
            print(f"[ERROR] Error processing {json_file.name}: {e}")

    print(f"[OK] Processed {total_documents} documents")
    print(f"[OK] Found {len(all_drivers)} unique drivers")

    # Second pass: count documents that DON'T have each driver (add to "None")
    for driver_name in all_drivers.keys():
        driver_name_lower = driver_name.lower()

        # Count how many documents have this driver (any magnitude)
        docs_with_driver = sum(all_drivers[driver_name]["magnitudes"].values()) - all_drivers[driver_name]["magnitudes"]["None"]

        # Add missing documents to "None" count
        # But we need to recount properly by checking each document
        docs_with_driver_actual = 0

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                found = False
                for category, drivers in data.get('drivers', {}).items():
                    if not isinstance(drivers, list):
                        continue
                    for driver in drivers:
                        if driver.get('driver_name', '').lower() == driver_name_lower:
                            found = True
                            break
                    if found:
                        break

                if found:
                    docs_with_driver_actual += 1

            except Exception:
                pass

        # Set None count to documents missing this driver
        all_drivers[driver_name]["magnitudes"]["None"] = total_documents - docs_with_driver_actual

    # Organize drivers by category
    drivers_by_category = defaultdict(list)
    for driver_name, driver_data in all_drivers.items():
        category = driver_data["category"]
        total_occurrences = (driver_data["magnitudes"]["Low"] +
                            driver_data["magnitudes"]["Medium"] +
                            driver_data["magnitudes"]["High"])
        drivers_by_category[category].append({
            "name": driver_name,
            "magnitudes": driver_data["magnitudes"],
            "total_occurrences": total_occurrences,
            "analysis": driver_data.get("analysis")
        })

    # Sort drivers within each category by total occurrences (descending), then by name
    for category in drivers_by_category:
        drivers_by_category[category].sort(key=lambda x: (-x["total_occurrences"], x["name"]))

    return {
        "total_drivers": len(all_drivers),
        "total_documents": total_documents,
        "drivers_by_category": dict(drivers_by_category)
    }


def format_analysis_for_modal(analysis, magnitude):
    """
    Format Claude's analysis for display in modal

    Args:
        analysis: Dictionary containing analysis data
        magnitude: The magnitude level (none, low, medium, high)

    Returns:
        HTML string with formatted analysis
    """
    if not analysis:
        return "<p class='text-gray-500'>No analysis available for this driver.</p>"

    magnitude_key = magnitude.lower()
    magnitude_data = analysis.get(magnitude_key, {})

    html = "<div class='space-y-4'>"

    if magnitude_key == "none":
        # For "none", show explanation
        explanations = magnitude_data.get('explanation', [])
        if explanations:
            html += "<div class='analysis-section'>"
            html += "<h4 class='font-semibold text-lg mb-2'>Why documents don't include this driver:</h4>"
            html += "<ul class='list-disc list-inside space-y-1 text-sm'>"
            for exp in explanations:
                html += f"<li>{exp}</li>"
            html += "</ul>"
            html += "</div>"
        else:
            html += "<p class='text-gray-500'>No explanation available.</p>"
    else:
        # For low/medium/high, show agreements and divergences
        agreements = magnitude_data.get('agreements', [])
        divergences = magnitude_data.get('divergences', [])

        if agreements:
            html += "<div class='analysis-section'>"
            html += "<h4 class='font-semibold text-lg mb-2 text-green-700'>How documents agree:</h4>"
            html += "<ul class='list-disc list-inside space-y-1 text-sm'>"
            for agreement in agreements:
                html += f"<li>{agreement}</li>"
            html += "</ul>"
            html += "</div>"

        if divergences:
            html += "<div class='analysis-section mt-4'>"
            html += "<h4 class='font-semibold text-lg mb-2 text-orange-700'>How documents diverge:</h4>"
            html += "<ul class='list-disc list-inside space-y-1 text-sm'>"
            for divergence in divergences:
                html += f"<li>{divergence}</li>"
            html += "</ul>"
            html += "</div>"

        if not agreements and not divergences:
            html += "<p class='text-gray-500'>No analysis available for this magnitude level.</p>"

    html += "</div>"
    return html


def generate_home_page(data, template_path, output_path):
    """
    Generate the home page HTML from template and data

    Args:
        data: Dictionary containing drivers organized by category
        template_path: Path to HTML template
        output_path: Path to save generated HTML
    """
    print("[OK] Generating home page HTML")

    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Category display names
    category_names = {
        "technological": "Technological Drivers",
        "organizational": "Organizational Drivers",
        "governance": "Governance Drivers",
        "societal": "Societal Drivers",
        "safety_alignment": "Safety & Alignment Drivers",
        "geopolitical": "Geopolitical Drivers",
        "economic": "Economic Drivers",
        "unspecified": "Unspecified Drivers"
    }

    # Category order for display
    category_order = [
        "technological", "economic", "organizational", "governance",
        "safety_alignment", "geopolitical", "societal", "unspecified"
    ]

    # Build HTML sections for each category
    sections_html = ""
    drivers_analyzed_count = 0
    total_docs = data["total_documents"]

    for category in category_order:
        if category not in data["drivers_by_category"]:
            continue

        drivers = data["drivers_by_category"][category]
        category_title = category_names.get(category, category.replace('_', ' ').title())

        sections_html += f"""
    <section class="category-section">
      <h2 class="category-title">{category_title}</h2>
      <div class="drivers-list">
"""

        for driver in drivers:
            driver_name = driver["name"]
            magnitudes = driver["magnitudes"]
            analysis = driver.get("analysis")
            sanitized_name = sanitize_filename(driver_name)

            # Calculate total occurrences (exclude "None" which represents missing documents)
            total_occurrences = magnitudes["Low"] + magnitudes["Medium"] + magnitudes["High"]

            # Filter out drivers with less than 50% coverage (< 12 occurrences)
            if total_occurrences < 12:
                continue

            # Count drivers with > 3 occurrences for "Drivers Analyzed"
            if total_occurrences > 3:
                drivers_analyzed_count += 1

            # Calculate percentage heights for bar charts
            def calc_height(count):
                return (count / total_docs) * 100

            none_height = calc_height(magnitudes["None"])
            low_height = calc_height(magnitudes["Low"])
            medium_height = calc_height(magnitudes["Medium"])
            high_height = calc_height(magnitudes["High"])

            # Escape driver name for JavaScript string
            escaped_driver_name = driver_name.replace("'", "\\'")

            # Generate analysis HTML for each magnitude level
            import html
            analysis_none = format_analysis_for_modal(analysis, "none") if analysis else ""
            analysis_low = format_analysis_for_modal(analysis, "low") if analysis else ""
            analysis_medium = format_analysis_for_modal(analysis, "medium") if analysis else ""
            analysis_high = format_analysis_for_modal(analysis, "high") if analysis else ""

            # Escape for data attributes (double escape: once for HTML attribute, once for onclick)
            analysis_none_escaped = html.escape(analysis_none, quote=True)
            analysis_low_escaped = html.escape(analysis_low, quote=True)
            analysis_medium_escaped = html.escape(analysis_medium, quote=True)
            analysis_high_escaped = html.escape(analysis_high, quote=True)

            # Get summary data
            summary = driver.get("summary", {})
            summary_json = json.dumps(summary) if summary else "{}"
            summary_json_escaped = html.escape(summary_json, quote=True)

            sections_html += f"""
        <div class="driver-row">
          <div class="driver-header">
            <div class="driver-name">{driver_name} <span class="driver-count">({total_occurrences}/{total_docs})</span></div>
            <div class="driver-buttons">
              <button onclick="openDriverSummary('{escaped_driver_name}', event)" class="open-driver-btn" data-summary="{summary_json_escaped}">
                Driver Summary
              </button>
              <button onclick="navigateToDriver('{sanitized_name}')" class="open-driver-btn">
                Open Driver →
              </button>
            </div>
          </div>
          <div class="magnitude-cards">
            <div class="card magnitude-none" onclick="openDriverBreakdown('{escaped_driver_name}', 'None', event)" data-analysis="{analysis_none_escaped}">
              <div class="card-background" style="height: {none_height}%;"></div>
              <div class="card-content">
                <span class="label">None</span>
                <span class="count">{magnitudes["None"]}</span>
              </div>
            </div>
            <div class="card magnitude-low" onclick="openDriverBreakdown('{escaped_driver_name}', 'Low', event)" data-analysis="{analysis_low_escaped}">
              <div class="card-background" style="height: {low_height}%;"></div>
              <div class="card-content">
                <span class="label">Low</span>
                <span class="count">{magnitudes["Low"]}</span>
              </div>
            </div>
            <div class="card magnitude-medium" onclick="openDriverBreakdown('{escaped_driver_name}', 'Medium', event)" data-analysis="{analysis_medium_escaped}">
              <div class="card-background" style="height: {medium_height}%;"></div>
              <div class="card-content">
                <span class="label">Medium</span>
                <span class="count">{magnitudes["Medium"]}</span>
              </div>
            </div>
            <div class="card magnitude-high" onclick="openDriverBreakdown('{escaped_driver_name}', 'High', event)" data-analysis="{analysis_high_escaped}">
              <div class="card-background" style="height: {high_height}%;"></div>
              <div class="card-content">
                <span class="label">High</span>
                <span class="count">{magnitudes["High"]}</span>
              </div>
            </div>
          </div>
        </div>
"""

        sections_html += """
      </div>
    </section>
"""

    # Replace placeholders in template
    html = template.replace("{{DRIVERS_ANALYZED}}", str(drivers_analyzed_count))
    html = html.replace("{{TOTAL_DOCUMENTS}}", str(data["total_documents"]))
    html = html.replace("{{GENERATION_DATE}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    html = html.replace("{{CATEGORY_SECTIONS}}", sections_html)

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[OK] Home page generated: {output_path}")


def main():
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    input_dir = project_root / "outputs" / "extract_drivers_v2"
    analysis_dir = project_root / "outputs" / "driver_analysis"
    summaries_dir = project_root / "outputs" / "driver_summaries"
    template_path = project_root / "outputs" / "spectrum_dashboards" / "home_template.html"
    output_path = project_root / "outputs" / "spectrum_dashboards" / "index.html"

    # Validate directories
    if not input_dir.exists():
        print(f"[ERROR] Input directory not found: {input_dir}")
        return 1

    if not template_path.exists():
        print(f"[ERROR] Template not found: {template_path}")
        print(f"[ERROR] Please create the home_template.html first")
        return 1

    # Load Claude analysis and summaries
    analysis_data = load_driver_analysis(analysis_dir)
    summaries_data = load_driver_summaries(summaries_dir)

    # Extract all drivers
    data = extract_all_drivers(input_dir)

    # Merge analysis and summaries into driver data
    for category_drivers in data["drivers_by_category"].values():
        for driver in category_drivers:
            driver_name = driver["name"]
            if driver_name in analysis_data:
                driver["analysis"] = analysis_data[driver_name]
            if driver_name in summaries_data:
                driver["summary"] = summaries_data[driver_name]

    # Generate home page
    generate_home_page(data, template_path, output_path)

    print("[OK] Home page generation complete!")
    print(f"[OK] Total drivers: {data['total_drivers']}")
    print(f"[OK] Total documents: {data['total_documents']}")

    # Print summary by category
    for category, drivers in sorted(data["drivers_by_category"].items()):
        print(f"[OK]   {category}: {len(drivers)} drivers")

    return 0


if __name__ == "__main__":
    exit(main())
