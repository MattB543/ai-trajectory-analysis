# File created: 2025-10-11
# Purpose: Batch extract key drivers from all AI trajectory documents
# Created by: AI assistant (Claude Code) at user's request to process all trajectory documents

import os
from pathlib import Path
from extract_drivers import extract_drivers, save_output
import re

def extract_title_and_authors(doc_path):
    """
    Extract title and authors from the first few lines of the markdown document.

    Args:
        doc_path: Path to the full_doc.md file

    Returns:
        tuple: (title, authors) or (folder_name, "Unknown Authors") if not found
    """
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            # Read first 50 lines to find title and authors
            lines = [f.readline() for _ in range(50)]

        title = None
        authors = None

        # Look for title (usually first line starting with #)
        for line in lines:
            if line.startswith('# ') and not title:
                title = line.replace('#', '').strip()
                # Remove trailing colons
                title = title.rstrip(':')
                break

        # Look for authors (various patterns)
        author_patterns = [
            r'(?:Author|By|Authors?):\s*(.+)',
            r'(?:^|\n)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+(?:,?\s+(?:and\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)*)\s*$',
        ]

        for line in lines[:20]:  # Check first 20 lines for authors
            for pattern in author_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match and not authors:
                    authors = match.group(1).strip()
                    break

            # Also check for lines with multiple capital names separated by commas
            if not authors and re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+(?:,\s+[A-Z][a-z]+\s+[A-Z][a-z]+)+', line.strip()):
                authors = line.strip()

        # Get folder name as fallback
        folder_name = Path(doc_path).parent.name

        if not title:
            title = folder_name

        if not authors:
            authors = "Unknown Authors"

        return title, authors

    except Exception as e:
        # Fallback to folder name
        folder_name = Path(doc_path).parent.name
        return folder_name, "Unknown Authors"


def get_all_documents():
    """
    Get all trajectory documents in the docs folder.

    Returns:
        list: List of tuples (display_name, full_doc_path)
    """
    docs_dir = Path('docs')
    documents = []

    for folder in sorted(docs_dir.iterdir()):
        if folder.is_dir():
            # Find all .md files in this folder
            md_files = sorted(folder.glob('*.md'))

            for md_file in md_files:
                # Create display name combining folder and file
                file_stem = md_file.stem

                # If it's just "full_doc", use folder name
                if file_stem == 'full_doc':
                    display_name = folder.name
                else:
                    # For numbered parts or specific scenarios, include both
                    display_name = f"{folder.name} - {file_stem}"

                documents.append((display_name, str(md_file)))

    return documents


def process_all_documents(skip_existing=True):
    """
    Process all trajectory documents and extract drivers.

    Args:
        skip_existing: If True, skip documents that already have output files
    """
    documents = get_all_documents()

    print("=" * 80)
    print("BATCH DRIVER EXTRACTION FOR ALL TRAJECTORY DOCUMENTS")
    print("=" * 80)
    print(f"\n[OK] Found {len(documents)} documents to process\n")

    output_dir = Path('outputs/extract_drivers')

    for i, (display_name, doc_path) in enumerate(documents, 1):
        print(f"\n{'=' * 80}")
        print(f"[{i}/{len(documents)}] Processing: {display_name}")
        print(f"{'=' * 80}")

        # Create safe filename from display name
        safe_name = re.sub(r'[^\w\s-]', '', display_name).strip().replace(' ', '_').lower()
        # Limit length for very long names
        if len(safe_name) > 80:
            safe_name = safe_name[:80]

        # Check if already processed
        if skip_existing:
            existing_files = list(output_dir.glob(f"*_drivers_{safe_name}.json"))
            if existing_files:
                print(f"[SKIP] Already processed - found {existing_files[0].name}")
                continue

        # Extract title and authors
        print(f"[OK] Extracting metadata from document...")
        title, authors = extract_title_and_authors(doc_path)
        print(f"[OK] Title: {title}")
        print(f"[OK] Authors: {authors}")

        # Extract drivers
        try:
            result = extract_drivers(doc_path, title, authors)

            if result:
                save_output(result, safe_name)
                print(f"[OK] Successfully processed: {display_name}")
            else:
                print(f"[ERROR] Failed to extract drivers from: {display_name}")

        except Exception as e:
            print(f"[ERROR] Exception processing {display_name}: {str(e)}")
            continue

    print(f"\n{'=' * 80}")
    print("[OK] Batch processing complete!")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    # Process all documents, skipping ones that already have output
    process_all_documents(skip_existing=True)

    # To reprocess all documents (overwrite existing), use:
    # process_all_documents(skip_existing=False)
