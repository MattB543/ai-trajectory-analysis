# File created by Claude Code on 2025-10-12
# Purpose: FIXED VERSION v3 - Group all drivers from extract_drivers_v2 by magnitude level
# Fixes:
# 1. Better fuzzy matching for summaries with aggressive normalization + manual mappings
# 2. Append scenario/context to document titles for multi-instance docs

import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import re

# Manual mappings for edge cases where fuzzy matching fails
MANUAL_FOLDER_MAPPINGS = {
    "AI and Leviathan: Parts I, II, and III": "AI & Leviathan (Parts I–III)",
    "How Artificial General Intelligence Could Affect the Rise and Fall of Nations": "Artificial General Intelligence and the Rise and Fall of Nations_ Visions for Potential AGI Futures",
}

def normalize_for_matching(text):
    """Aggressive normalization for folder matching"""
    text = text.lower()
    # Remove common punctuation variations
    text = re.sub(r'[:\-_&()\[\],]', ' ', text)
    # Remove "Part X" variations
    text = re.sub(r'\bpart\s+\d+\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bparts?\s+[ivxlcdm]+(?:\s*[,–—-]\s*[ivxlcdm]+)*\b', '', text, flags=re.IGNORECASE)
    # Remove roman numerals standalone
    text = re.sub(r'\b[ivxlcdm]+\b', '', text, flags=re.IGNORECASE)
    # Remove "and" which can appear inconsistently
    text = re.sub(r'\band\b', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_context_from_filename(filename):
    """Extract scenario/context from filename (e.g., '- take-off', '- arms_race')"""
    name_without_ext = filename.replace('.json', '')
    parts = name_without_ext.split('_drivers_', 1)

    if len(parts) < 2:
        return None

    title_part = parts[1]

    # Look for scenario indicators
    match = re.search(r'[-_]\s*((?:take[-_]off|arms[-_]race|diplomacy|plateau|plateuau|big[-_]ai|ending[-_][ab]))\s*$',
                     title_part, re.IGNORECASE)

    if match:
        context = match.group(1).replace('_', '-').replace(' ', '-').title()
        # Fix common typos
        if 'plateuau' in context.lower():
            context = 'Plateau'
        return context

    return None

def get_document_title_with_context(filename, base_title):
    """Get document title with scenario context appended if available"""
    context = extract_context_from_filename(filename)
    if context:
        context = context.replace('-', ' ').title()
        return f"{base_title} - {context}"
    return base_title

def normalize_magnitude(mag):
    """Normalize magnitude values to standard categories"""
    if not mag:
        return "low"
    mag_lower = str(mag).lower().strip()

    if "high" in mag_lower:
        return "high"
    elif "medium" in mag_lower or "med" in mag_lower:
        return "medium"
    elif "low" in mag_lower:
        return "low"
    else:
        return "low"

def find_summary_file(doc_title, docs_base_path):
    """Find the summary file for a given document title with improved matching"""
    docs_path = Path(docs_base_path)

    # Check manual mappings first
    if doc_title in MANUAL_FOLDER_MAPPINGS:
        target_folder = docs_path / MANUAL_FOLDER_MAPPINGS[doc_title]
        if target_folder.exists():
            for summary_file in target_folder.glob('*summary*.md'):
                try:
                    with open(summary_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        summary_lines = []
                        found_separator = False
                        for line in lines:
                            if found_separator and line.strip():
                                summary_lines.append(line)
                            elif line.strip() == '---':
                                found_separator = True
                        return '\n'.join(summary_lines).strip() if summary_lines else content.strip()
                except Exception as e:
                    print(f"[ERROR] Could not read summary file {summary_file}: {e}")
                    return "Summary not available"

    # Normalize the search title
    doc_title_normalized = normalize_for_matching(doc_title)

    # Try to find matching folder
    for folder in docs_path.iterdir():
        if folder.is_dir():
            folder_name_normalized = normalize_for_matching(folder.name)

            # Check if normalized names match (substring or full match)
            if (doc_title_normalized in folder_name_normalized or
                folder_name_normalized in doc_title_normalized):

                # Find summary file in this folder
                for summary_file in folder.glob('*summary*.md'):
                    try:
                        with open(summary_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            lines = content.split('\n')
                            summary_lines = []
                            found_separator = False
                            for line in lines:
                                if found_separator and line.strip():
                                    summary_lines.append(line)
                                elif line.strip() == '---':
                                    found_separator = True
                            return '\n'.join(summary_lines).strip() if summary_lines else content.strip()
                    except Exception as e:
                        print(f"[ERROR] Could not read summary file {summary_file}: {e}")
                        return "Summary not available"

    return "Summary not found"

def main():
    print("[OK] Starting driver grouping by magnitude (v3 - with all fixes)...")

    # Paths
    drivers_path = Path('outputs/extract_drivers_v2')
    docs_path = Path('docs')
    output_path = Path('outputs/grouped_drivers')

    # Clear existing grouped files
    for old_file in output_path.glob('*_grouped_*.json'):
        old_file.unlink()
    print("[OK] Cleared old grouped files")

    output_path.mkdir(parents=True, exist_ok=True)

    # Step 1: Collect all drivers from all documents
    print("[OK] Reading all driver files...")
    all_drivers = defaultdict(lambda: {
        'high': [],
        'medium': [],
        'low': [],
        'documents_processed': set()
    })

    driver_files = list(drivers_path.glob('*_drivers_*.json'))
    print(f"[OK] Found {len(driver_files)} driver files")

    for driver_file in driver_files:
        try:
            with open(driver_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            base_title = data.get('document_title', '')
            doc_title = get_document_title_with_context(driver_file.name, base_title)

            print(f"[OK] Processing: {doc_title}")

            # Process each category of drivers
            drivers = data.get('drivers', {})
            for category, category_drivers in drivers.items():
                if not isinstance(category_drivers, list):
                    continue

                for driver in category_drivers:
                    driver_name = driver.get('driver_name', '').strip()
                    if not driver_name:
                        continue

                    # Track that this document was processed (use base_title for uniqueness)
                    all_drivers[driver_name]['documents_processed'].add(base_title)

                    # Normalize magnitude and add to appropriate list
                    magnitude = normalize_magnitude(driver.get('magnitude', 'low'))

                    driver_entry = {
                        'document_title': doc_title,  # This now includes context
                        'description': driver.get('description', ''),
                        'direction': driver.get('direction', ''),
                        'magnitude': driver.get('magnitude', ''),
                        'certainty': driver.get('certainty', ''),
                        'evidence': driver.get('evidence', ''),
                        'category': category
                    }

                    all_drivers[driver_name][magnitude].append(driver_entry)

        except Exception as e:
            print(f"[ERROR] Error processing {driver_file.name}: {e}")
            continue

    print(f"[OK] Found {len(all_drivers)} unique drivers")

    # Step 2: For each driver, find documents that DON'T have it
    print("[OK] Finding documents without each driver...")
    all_document_titles = set()
    for driver_file in driver_files:
        try:
            with open(driver_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            base_title = data.get('document_title', '')
            all_document_titles.add(base_title)
        except:
            continue

    print(f"[OK] Total unique documents: {len(all_document_titles)}")

    # Step 3: Add "none" entries with summaries
    missing_summaries = []
    for driver_name, driver_data in all_drivers.items():
        documents_without_driver = all_document_titles - driver_data['documents_processed']

        driver_data['none'] = []
        for doc_title in documents_without_driver:
            summary = find_summary_file(doc_title, docs_path)
            if summary == "Summary not found":
                missing_summaries.append(doc_title)
            driver_data['none'].append({
                'document_title': doc_title,
                'summary': summary
            })

    if missing_summaries:
        print(f"\n[WARNING] Still missing summaries for {len(set(missing_summaries))} documents:")
        for doc in set(missing_summaries):
            print(f"    - {doc}")

    print("[OK] Grouping complete, writing output files...")

    # Step 4: Write each driver to its own file (only if <=12 docs in none)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    drivers_written = 0
    drivers_skipped = 0

    for driver_name, driver_data in all_drivers.items():
        # Skip drivers that are too specific (>12 docs without it)
        if len(driver_data['none']) > 12:
            drivers_skipped += 1
            continue

        # Clean filename
        safe_filename = re.sub(r'[^\w\s-]', '', driver_name).strip().replace(' ', '_')
        safe_filename = re.sub(r'[-\s]+', '_', safe_filename)

        output_file = output_path / f"{timestamp}_grouped_{safe_filename}.json"

        # Prepare output structure
        output = {
            'driver_name': driver_name,
            'high': driver_data['high'],
            'medium': driver_data['medium'],
            'low': driver_data['low'],
            'none': driver_data['none'],
            'statistics': {
                'total_documents': len(all_document_titles),
                'documents_with_driver': len(driver_data['documents_processed']),
                'documents_without_driver': len(driver_data['none']),
                'high_count': len(driver_data['high']),
                'medium_count': len(driver_data['medium']),
                'low_count': len(driver_data['low'])
            }
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        drivers_written += 1

    print(f"[OK] Created {drivers_written} grouped driver files in {output_path}")
    print(f"[OK] Skipped {drivers_skipped} drivers (too specific - >12 docs without them)")
    print(f"[OK] Files timestamped with: {timestamp}")

    # Create summary report
    summary_file = output_path / f"{timestamp}_grouping_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"Driver Grouping Summary (v3 - FULLY FIXED)\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"=" * 80 + "\n\n")
        f.write(f"Total unique drivers: {len(all_drivers)}\n")
        f.write(f"Drivers written: {drivers_written}\n")
        f.write(f"Drivers skipped (too specific): {drivers_skipped}\n")
        f.write(f"Total documents: {len(all_document_titles)}\n\n")
        f.write(f"Drivers by frequency:\n")

        # Sort by frequency (only include written drivers)
        sorted_drivers = sorted(
            [(name, data) for name, data in all_drivers.items() if len(data['none']) <= 12],
            key=lambda x: len(x[1]['documents_processed']),
            reverse=True
        )

        for driver_name, driver_data in sorted_drivers:
            f.write(f"\n{driver_name}:\n")
            f.write(f"  Present in {len(driver_data['documents_processed'])} documents\n")
            f.write(f"  High: {len(driver_data['high'])}, Medium: {len(driver_data['medium'])}, Low: {len(driver_data['low'])}\n")

    print(f"[OK] Summary report created: {summary_file}")
    print("[OK] Done!")
    print("\n" + "="*80)
    print("ALL FIXES APPLIED:")
    print("1. Improved fuzzy matching + manual mappings for summaries")
    print("2. Scenario context appended to document titles for multi-instance docs")
    print("="*80)

if __name__ == "__main__":
    main()
