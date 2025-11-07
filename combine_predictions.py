import json
import os
from pathlib import Path

def extract_doc_title(filename):
    """Extract document title from filename.
    Example: 20251013_211400_advanced_ai_possible_futures_arms_race_predictions.json
    Returns: advanced_ai_possible_futures_arms_race
    """
    # Remove timestamp prefix (YYYYMMDD_HHMMSS_)
    name = filename.split('_', 2)[-1]
    # Remove _predictions.json suffix
    name = name.replace('_predictions.json', '')
    return name

def combine_predictions():
    predictions_dir = Path('outputs/predictions')
    combined_predictions = []

    # Get all JSON files
    json_files = sorted(predictions_dir.glob('*.json'))

    print(f"Found {len(json_files)} prediction files")

    for json_file in json_files:
        print(f"Processing: {json_file.name}")

        # Extract doc title
        doc_title = extract_doc_title(json_file.name)

        # Read JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Add doc_title at the top level
        combined_entry = {
            "doc_title": doc_title,
            "predictions": data.get("predictions", [])
        }

        combined_predictions.append(combined_entry)

    # Write combined file
    output_file = Path('outputs/all_predictions_combined.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_predictions, f, indent=2, ensure_ascii=False)

    print(f"\nCombined {len(combined_predictions)} documents into {output_file}")
    print(f"Total size: {output_file.stat().st_size:,} bytes")

if __name__ == "__main__":
    combine_predictions()
