"""
Token Counter for AI Trajectory Analysis Documentation

Created by: Claude Code Agent
Purpose: Analysis script to count characters and estimate tokens in markdown files
Request Type: User-requested analysis tool
Created: 2025-10-11

This script scans the docs/ folder recursively, counts characters in each markdown file,
and estimates token counts by dividing by 4 (a rough approximation for English text).
"""

import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def count_chars_in_file(file_path):
    """Count characters in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return len(content)
    except Exception as e:
        print(f"[ERROR] Failed to read {file_path}: {e}")
        return 0


def get_folder_name(file_path, docs_dir):
    """Extract the trajectory folder name from the file path."""
    relative_path = file_path.relative_to(docs_dir)
    if len(relative_path.parts) > 1:
        return relative_path.parts[0]
    else:
        return "Root"


def analyze_docs_folder(docs_path):
    """Analyze all markdown files in the docs folder."""
    docs_dir = Path(docs_path)

    if not docs_dir.exists():
        print(f"[ERROR] Docs directory not found: {docs_path}")
        return None

    # Collect all markdown files
    md_files = list(docs_dir.glob("**/*.md"))

    if not md_files:
        print(f"[ERROR] No markdown files found in {docs_path}")
        return None

    print(f"[OK] Found {len(md_files)} markdown files")

    # Group files by folder
    folder_data = defaultdict(list)

    for md_file in md_files:
        folder_name = get_folder_name(md_file, docs_dir)
        file_name = md_file.name
        char_count = count_chars_in_file(md_file)
        token_estimate = char_count / 4

        folder_data[folder_name].append({
            'file_name': file_name,
            'char_count': char_count,
            'token_estimate': int(token_estimate),
            'full_path': str(md_file)
        })

    return folder_data


def format_output(folder_data):
    """Format the analysis results as a string."""
    lines = []
    lines.append("=" * 80)
    lines.append("AI TRAJECTORY ANALYSIS - TOKEN COUNT REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    lines.append("")

    total_chars = 0
    total_tokens = 0
    total_files = 0

    # Sort folders alphabetically
    for folder_name in sorted(folder_data.keys()):
        files = folder_data[folder_name]
        folder_chars = sum(f['char_count'] for f in files)
        folder_tokens = sum(f['token_estimate'] for f in files)

        lines.append("-" * 80)
        lines.append(f"FOLDER: {folder_name}")
        lines.append("-" * 80)

        # Sort files by name
        for file_info in sorted(files, key=lambda x: x['file_name']):
            lines.append(f"  File: {file_info['file_name']}")
            lines.append(f"    Characters: {file_info['char_count']:,}")
            lines.append(f"    Est. Tokens: {file_info['token_estimate']:,}")
            lines.append("")

            total_chars += file_info['char_count']
            total_tokens += file_info['token_estimate']
            total_files += 1

        lines.append(f"  FOLDER TOTALS:")
        lines.append(f"    Files: {len(files)}")
        lines.append(f"    Characters: {folder_chars:,}")
        lines.append(f"    Est. Tokens: {folder_tokens:,}")
        lines.append("")

    lines.append("=" * 80)
    lines.append("GRAND TOTALS")
    lines.append("=" * 80)
    lines.append(f"Total Files: {total_files}")
    lines.append(f"Total Characters: {total_chars:,}")
    lines.append(f"Total Est. Tokens: {total_tokens:,}")
    lines.append("=" * 80)

    return "\n".join(lines)


def main():
    """Main execution function."""
    print("[OK] Starting token count analysis...")

    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    docs_path = project_root / "docs"

    print(f"[OK] Analyzing docs folder: {docs_path}")

    # Analyze the docs folder
    folder_data = analyze_docs_folder(docs_path)

    if folder_data is None:
        print("[ERROR] Analysis failed")
        return

    # Format the output
    output = format_output(folder_data)

    # Print to console
    print("")
    print(output)

    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = project_root / "outputs" / "count_tokens"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{timestamp}_token_counts.txt"

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print("")
        print(f"[OK] Results saved to: {output_file}")
    except Exception as e:
        print(f"[ERROR] Failed to save output file: {e}")


if __name__ == "__main__":
    main()
