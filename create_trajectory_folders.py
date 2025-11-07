# Created to process the CSV file and create folders for each AI trajectory title
# Direct request from user to create folders in docs directory based on CSV data

import csv
import os
import re
from pathlib import Path

def sanitize_folder_name(title):
    """
    Sanitize a title string to create a valid Windows folder name.
    Removes or replaces invalid characters: : ? / \ * " < > |
    """
    # Replace invalid characters with underscores or remove them
    sanitized = title.strip()

    # Replace problematic characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', sanitized)

    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)

    # Remove leading/trailing underscores and dots (Windows doesn't like trailing dots)
    sanitized = sanitized.strip('_. ')

    # Truncate if too long (Windows has a 255 character limit for folder names)
    if len(sanitized) > 200:
        sanitized = sanitized[:200].strip('_. ')

    return sanitized

def main():
    # Define paths
    csv_path = r'C:\Users\matth\projects\ai-trajectory-analysis\input\Top_AI_Trajectory_Sources.csv'
    docs_dir = r'C:\Users\matth\projects\ai-trajectory-analysis\docs'

    # Ensure docs directory exists
    os.makedirs(docs_dir, exist_ok=True)

    print('[OK] Starting folder creation process...')
    print(f'[OK] Reading CSV from: {csv_path}')
    print(f'[OK] Creating folders in: {docs_dir}')
    print()

    folders_created = []
    errors = []

    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header
                title = row.get('Title', '').strip()

                if not title:
                    print(f'[WARNING] Row {row_num}: Empty title, skipping...')
                    continue

                # Sanitize the title for use as a folder name
                folder_name = sanitize_folder_name(title)

                if not folder_name:
                    print(f'[ERROR] Row {row_num}: Could not create valid folder name from title: {title}')
                    errors.append((row_num, title))
                    continue

                # Create the full folder path
                folder_path = os.path.join(docs_dir, folder_name)

                try:
                    os.makedirs(folder_path, exist_ok=True)
                    folders_created.append(folder_name)
                    print(f'[OK] Created: {folder_name}')
                except Exception as e:
                    print(f'[ERROR] Row {row_num}: Failed to create folder "{folder_name}": {str(e)}')
                    errors.append((row_num, title))

        print()
        print('=' * 80)
        print('[OK] Folder creation complete!')
        print(f'[OK] Total folders created: {len(folders_created)}')

        if errors:
            print(f'[WARNING] Errors encountered: {len(errors)}')
            for row_num, title in errors:
                print(f'  - Row {row_num}: {title}')

        print()
        print('[OK] Listing all folders in docs directory:')
        print('=' * 80)

        # List all folders in docs directory
        if os.path.exists(docs_dir):
            all_items = sorted(os.listdir(docs_dir))
            folders = [item for item in all_items if os.path.isdir(os.path.join(docs_dir, item))]

            for idx, folder in enumerate(folders, start=1):
                print(f'{idx:2d}. {folder}')

            print('=' * 80)
            print(f'[OK] Total folders in docs directory: {len(folders)}')

    except FileNotFoundError:
        print(f'[ERROR] CSV file not found: {csv_path}')
        return 1
    except Exception as e:
        print(f'[ERROR] Unexpected error: {str(e)}')
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
