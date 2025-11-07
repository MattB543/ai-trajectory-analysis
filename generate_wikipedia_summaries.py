# Created by AI assistant to generate high-level paragraph summaries of markdown documentation files
# Direct request from user to process docs folder markdown files using GPT-5-mini via OpenRouter
# Summary format: A single readable paragraph pulling out key details, decisions, and outcomes

import os
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

def get_openrouter_api_key():
    """Get OpenRouter API key from environment"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("[ERROR] OPENROUTER_API_KEY not found in .env file")
    return api_key

def read_markdown_file(file_path):
    """Read markdown file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"[OK] Read file: {file_path}")
        return content
    except Exception as e:
        print(f"[ERROR] Failed to read {file_path}: {e}")
        return None

def generate_summary(content, api_key, model="openai/gpt-5-mini"):
    """Generate high-level paragraph summary using OpenRouter API"""

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""Please create a high-level summary of the following document in ONE readable paragraph.

The summary should pull out the key details, decisions, and outcomes from the document and present them in a single, cohesive, flowing paragraph that gives the reader a comprehensive understanding of the main points.

Document to summarize:

{content}

Please provide the summary as a single paragraph:"""

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        print(f"[OK] Sending request to OpenRouter API with model {model}...")
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        result = response.json()
        summary = result['choices'][0]['message']['content']
        print(f"[OK] Successfully generated summary")
        return summary

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API request failed: {e}")
        if hasattr(e.response, 'text'):
            print(f"[ERROR] Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to generate summary: {e}")
        return None

def save_summary(summary, original_file_path):
    """Save summary in the same folder as the original markdown file"""
    try:
        original_path = Path(original_file_path)
        folder = original_path.parent
        base_name = original_path.stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create output filename with timestamp
        summary_filename = f"{timestamp}_summary_{base_name}.md"
        summary_path = folder / summary_filename

        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"# High-Level Summary\n\n")
            f.write(f"**Original Document:** {original_path.name}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(summary)

        print(f"[OK] Saved summary to: {summary_path}")
        return str(summary_path)

    except Exception as e:
        print(f"[ERROR] Failed to save summary: {e}")
        return None

def process_markdown_file(file_path, api_key, test_mode=False):
    """Process a single markdown file"""
    print(f"\n{'='*80}")
    print(f"Processing: {file_path}")
    print(f"{'='*80}\n")

    # Read the markdown file
    content = read_markdown_file(file_path)
    if not content:
        return False

    print(f"[OK] File size: {len(content)} characters")

    # Generate summary
    summary = generate_summary(content, api_key)
    if not summary:
        return False

    # Save summary
    output_path = save_summary(summary, file_path)
    if not output_path:
        return False

    print(f"\n[OK] Successfully processed {file_path}")
    return True

def main():
    """Main function"""
    print("\n" + "="*80)
    print("High-Level Paragraph Summary Generator")
    print("Using OpenRouter API with GPT-5-mini")
    print("="*80 + "\n")

    # Get API key
    try:
        api_key = get_openrouter_api_key()
    except ValueError as e:
        print(str(e))
        return

    # Find all markdown files in docs folder
    docs_folder = Path("docs")
    if not docs_folder.exists():
        print(f"[ERROR] docs folder not found")
        return

    # Filter out any existing summary files
    markdown_files = [f for f in docs_folder.rglob("*.md") if "_summary_" not in f.name]
    print(f"[OK] Found {len(markdown_files)} markdown files to process\n")

    if not markdown_files:
        print("[ERROR] No markdown files found in docs folder")
        return

    # Process all files
    successful = 0
    failed = 0

    for i, file_path in enumerate(markdown_files, 1):
        print(f"\n[OK] Processing file {i}/{len(markdown_files)}")

        success = process_markdown_file(str(file_path), api_key)

        if success:
            successful += 1
        else:
            failed += 1

        # Add a small delay between API requests to be respectful
        if i < len(markdown_files):
            time.sleep(2)

    # Print final summary
    print("\n" + "="*80)
    print("PROCESSING COMPLETE")
    print("="*80)
    print(f"[OK] Successfully processed: {successful}/{len(markdown_files)} files")
    if failed > 0:
        print(f"[ERROR] Failed: {failed}/{len(markdown_files)} files")
    print("="*80)

if __name__ == "__main__":
    main()
