#!/usr/bin/env python3
"""
Load Full Documents into Database
Created: 2025-10-11
Purpose: Read all markdown files from docs/ and load them into the trajectories table
         Handles single documents, multi-part documents, and multi-scenario documents
This file was created as a direct request from the user
"""

import os
import csv
import psycopg2
from pathlib import Path
from datetime import datetime
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection - use DATABASE_URL from .env
DATABASE_URL = os.getenv('DATABASE_URL')

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
CSV_PATH = PROJECT_ROOT / 'input' / 'Top_AI_Trajectory_Sources.csv'
DOCS_PATH = PROJECT_ROOT / 'docs'

def sanitize_folder_name(title):
    """
    Sanitize title to match folder name (same logic used when creating folders)
    """
    # Replace invalid Windows characters with underscores
    invalid_chars = r'[:<>?/\\*"|]'
    sanitized = re.sub(invalid_chars, '_', title)
    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores and dots
    sanitized = sanitized.strip('_. ')
    return sanitized

def parse_csv():
    """
    Parse the CSV file and return a list of trajectory metadata dictionaries
    """
    trajectories = []

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert multi-scenario to boolean
            multi_scenario = row['Multi-scen?'].strip().lower() not in ['no', 'n', '']

            # Parse rating (handle non-numeric ratings)
            rating_str = row['Rating'].strip()
            try:
                rating = int(rating_str)
            except ValueError:
                # If rating contains text, try to extract the number
                rating_match = re.search(r'\d+', rating_str)
                rating = int(rating_match.group()) if rating_match else None

            # Parse year (handle year ranges like "2022–25")
            year_str = row['Year'].strip()
            year = None
            if year_str:
                try:
                    year = int(year_str)
                except ValueError:
                    # Try to extract first year from range (e.g., "2022–25" -> 2022)
                    year_match = re.search(r'\d{4}', year_str)
                    year = int(year_match.group()) if year_match else None

            trajectory = {
                'title': row['Title'].strip(),
                'authors': row['Author(s)/Org'].strip(),
                'year': year,
                'scenario_lane': row['Scenario lane'].strip(),
                'multi_scenario': multi_scenario,
                'rating': rating,
                'why_it_matters': row['Why it matters (one-liner)'].strip(),
                'links': row['Link(s)'].strip()
            }
            trajectories.append(trajectory)

    print(f"[OK] Parsed {len(trajectories)} trajectories from CSV")
    return trajectories

def find_markdown_files(trajectory):
    """
    Find all markdown files for a given trajectory
    Returns list of tuples: (file_path, part_number, part_name)
    """
    folder_name = sanitize_folder_name(trajectory['title'])
    folder_path = DOCS_PATH / folder_name

    if not folder_path.exists():
        print(f"[ERROR] Folder not found: {folder_path}")
        return []

    md_files = list(folder_path.glob('*.md'))

    if not md_files:
        print(f"[ERROR] No markdown files found in: {folder_path}")
        return []

    # Process files and determine part info
    file_info = []

    for md_file in md_files:
        filename = md_file.name

        # Determine part number and name based on filename
        if filename == 'full_doc.md':
            part_number = 1
            part_name = None
        elif filename.startswith('full_doc_'):
            # Multi-part document (e.g., full_doc_1.md, full_doc_2.md)
            part_match = re.search(r'full_doc_(\d+)\.md', filename)
            if part_match:
                part_number = int(part_match.group(1))
                part_name = f'Part {part_number}'
            else:
                part_number = 1
                part_name = None
        else:
            # Scenario file (e.g., arms_race.md, plateau.md)
            scenario_name = filename.replace('.md', '').replace('_', ' ').title()
            # Find the scenario number by sorting alphabetically
            scenario_files = sorted([f.name for f in md_files if f.name != 'full_doc.md'])
            part_number = scenario_files.index(filename) + 1 if filename in scenario_files else 1
            part_name = scenario_name

        file_info.append((md_file, part_number, part_name))

    return sorted(file_info, key=lambda x: x[1])  # Sort by part number

def insert_trajectory(cursor, trajectory, file_path, part_number, part_name, full_content):
    """
    Insert a trajectory record into the database
    """
    sql = """
        INSERT INTO trajectories
        (title, authors, year, scenario_lane, multi_scenario, rating,
         why_it_matters, links, part_number, part_name, file_name, full_content)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """

    cursor.execute(sql, (
        trajectory['title'],
        trajectory['authors'],
        trajectory['year'],
        trajectory['scenario_lane'],
        trajectory['multi_scenario'],
        trajectory['rating'],
        trajectory['why_it_matters'],
        trajectory['links'],
        part_number,
        part_name,
        file_path.name,
        full_content
    ))

    trajectory_id = cursor.fetchone()[0]
    return trajectory_id

def main():
    """
    Main function to load all documents into the database
    """
    print("[OK] Starting document loading process...")
    print(f"[OK] Project root: {PROJECT_ROOT}")
    print(f"[OK] CSV path: {CSV_PATH}")
    print(f"[OK] Docs path: {DOCS_PATH}")

    # Parse CSV
    trajectories = parse_csv()

    # Connect to database
    try:
        if not DATABASE_URL:
            print("[ERROR] DATABASE_URL not found in .env file")
            return

        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("[OK] Connected to database")
    except Exception as e:
        print(f"[ERROR] Failed to connect to database: {e}")
        return

    # Process each trajectory
    total_inserted = 0
    total_errors = 0

    for trajectory in trajectories:
        print(f"\n[OK] Processing: {trajectory['title']}")

        # Find markdown files
        file_info = find_markdown_files(trajectory)

        if not file_info:
            print(f"[ERROR] No files found for: {trajectory['title']}")
            total_errors += 1
            continue

        print(f"[OK] Found {len(file_info)} file(s)")

        # Insert each file
        for file_path, part_number, part_name in file_info:
            try:
                # Read content
                with open(file_path, 'r', encoding='utf-8') as f:
                    full_content = f.read()

                # Insert into database
                trajectory_id = insert_trajectory(
                    cursor, trajectory, file_path,
                    part_number, part_name, full_content
                )

                part_info = f" ({part_name})" if part_name else ""
                print(f"[OK] Inserted ID {trajectory_id}: {file_path.name}{part_info} - {len(full_content)} chars")
                total_inserted += 1

            except Exception as e:
                print(f"[ERROR] Failed to insert {file_path.name}: {e}")
                total_errors += 1

    # Commit and close
    try:
        conn.commit()
        print(f"\n[OK] Transaction committed")
    except Exception as e:
        print(f"[ERROR] Failed to commit: {e}")
        conn.rollback()

    cursor.close()
    conn.close()

    # Summary
    print("\n" + "="*60)
    print(f"[OK] Load complete!")
    print(f"[OK] Total records inserted: {total_inserted}")
    print(f"[ERROR] Total errors: {total_errors}")
    print("="*60)

if __name__ == '__main__':
    main()
