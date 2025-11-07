# File created: 2025-10-12
# Purpose: Async version of batch driver extraction - processes documents in parallel using asyncio
# Created by: AI assistant (Claude Code) at direct user request to improve performance with concurrent API calls

import os
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import json
import re
from typing import Dict, List, Tuple, Optional

# Load environment variables
load_dotenv()

# Configuration
MAX_CONCURRENT_REQUESTS = 5  # Process 5 documents in parallel
MAX_RETRIES = 5  # Maximum number of retries for rate limit errors
INITIAL_RETRY_DELAY = 2  # Initial delay in seconds for exponential backoff
TEST_MODE = False  # Set to True to test with truncated docs (500 chars)
TEST_DOC_LENGTH = 500  # Length to truncate docs in test mode


def extract_json_from_response(response_text: str) -> Optional[Dict]:
    """
    Extract JSON object from the response text (new nested structure).

    Args:
        response_text: The full response text containing JSON

    Returns:
        Parsed JSON object or None if extraction fails
    """
    # Try to find JSON in code blocks first
    json_block_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
    if json_block_match:
        try:
            parsed = json.loads(json_block_match.group(1))
            # Validate it looks like our expected structure (nested object with drivers)
            if isinstance(parsed, dict) and 'drivers' in parsed:
                return parsed
        except json.JSONDecodeError:
            pass

    # Try to find content after "KEY DRIVERS:" marker
    key_drivers_match = re.search(r'KEY DRIVERS:\s*([\s\S]*)', response_text, re.IGNORECASE)
    if key_drivers_match:
        remaining_text = key_drivers_match.group(1)
        # Look for JSON in this section
        json_block = re.search(r'```json\s*([\s\S]*?)\s*```', remaining_text)
        if json_block:
            try:
                parsed = json.loads(json_block.group(1))
                if isinstance(parsed, dict) and 'drivers' in parsed:
                    return parsed
            except json.JSONDecodeError:
                pass

    # Fallback: Try to find raw JSON object using a more sophisticated approach
    # Find all potential JSON objects by counting braces
    for i in range(len(response_text)):
        if response_text[i] == '{':
            brace_count = 0
            in_string = False
            escape = False

            for j in range(i, len(response_text)):
                char = response_text[j]

                if escape:
                    escape = False
                    continue

                if char == '\\':
                    escape = True
                    continue

                if char == '"' and not escape:
                    in_string = not in_string

                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1

                    if brace_count == 0:
                        # Found a complete JSON object
                        potential_json = response_text[i:j+1]
                        if len(potential_json) > 200:  # Must be substantial
                            try:
                                parsed = json.loads(potential_json)
                                if isinstance(parsed, dict) and 'drivers' in parsed:
                                    if isinstance(parsed['drivers'], dict):
                                        return parsed
                            except json.JSONDecodeError:
                                pass
                        break

    return None


def extract_title_and_authors(doc_path: str) -> Tuple[str, str]:
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

        # Look for authors (simple pattern only)
        author_pattern = r'(?:Author|By|Authors?):\s*(.+)'

        for line in lines[:20]:  # Check first 20 lines for authors
            if not authors:
                match = re.search(author_pattern, line, re.IGNORECASE)
                if match:
                    authors = match.group(1).strip()
                    break

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


def get_all_documents() -> List[Tuple[str, str]]:
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


async def extract_drivers_async(
    session: aiohttp.ClientSession,
    doc_path: str,
    doc_title: str,
    doc_authors: str,
    api_key: str,
    prompt_template: str,
    semaphore: asyncio.Semaphore,
    doc_index: int,
    total_docs: int
) -> Optional[Dict]:
    """
    Extract key drivers from a document using Claude Sonnet 4.5 with extended thinking (async version).

    Args:
        session: aiohttp ClientSession for making requests
        doc_path: Path to the document to analyze
        doc_title: Title of the document
        doc_authors: Authors of the document
        api_key: OpenRouter API key
        prompt_template: The driver prompt template
        semaphore: asyncio Semaphore to limit concurrent requests
        doc_index: Index of current document
        total_docs: Total number of documents

    Returns:
        Dict containing the analysis results or None if failed
    """
    async with semaphore:  # Limit concurrent requests
        print(f"\n[{doc_index}/{total_docs}] [OK] Starting driver extraction for: {doc_title}")

        try:
            # Read the document to analyze
            print(f"[{doc_index}/{total_docs}] [OK] Loading document: {doc_path}")
            with open(doc_path, 'r', encoding='utf-8') as f:
                document_content = f.read()

            # TEST MODE: Truncate document if enabled
            if TEST_MODE:
                original_length = len(document_content)
                document_content = document_content[:TEST_DOC_LENGTH]
                print(f"[{doc_index}/{total_docs}] [TEST MODE] Truncated doc from {original_length} to {len(document_content)} chars")

            # Fill in the template
            prompt = prompt_template.replace('[TITLE]', doc_title)
            prompt = prompt.replace('[AUTHORS]', doc_authors)
            prompt = prompt.replace('[full_doc_markdown]', document_content)

            print(f"[{doc_index}/{total_docs}] [OK] Sending request to Claude Sonnet 4.5 with extended thinking...")
            print(f"[{doc_index}/{total_docs}] [OK] Document length: {len(document_content)} characters")

            # Prepare request
            headers = {
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/ai-trajectory-analysis",
                "X-Title": "AI Trajectory Analysis Tool",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "anthropic/claude-sonnet-4.5",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "reasoning": {
                    "effort": "high"  # Use high effort for extended thinking
                },
                "max_tokens": 64000  # Max tokens for final response after reasoning
            }

            # Retry logic with exponential backoff for rate limits
            retry_count = 0
            retry_delay = INITIAL_RETRY_DELAY

            while retry_count <= MAX_RETRIES:
                try:
                    async with session.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=900)  # 15 minute timeout
                    ) as response:

                        # Handle rate limit errors (429)
                        if response.status == 429:
                            retry_count += 1
                            if retry_count > MAX_RETRIES:
                                print(f"[{doc_index}/{total_docs}] [ERROR] Max retries exceeded for rate limit")
                                return None

                            # Exponential backoff
                            print(f"[{doc_index}/{total_docs}] [WARNING] Rate limit hit, retrying in {retry_delay}s (attempt {retry_count}/{MAX_RETRIES})")
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                            continue

                        response.raise_for_status()
                        data = await response.json()

                        print(f"[{doc_index}/{total_docs}] [OK] Response received from API")

                        # Extract the response
                        response_content = data['choices'][0]['message']['content']

                        # Try to extract thinking/reasoning if available
                        thinking_content = None
                        if 'reasoning_content' in data['choices'][0]['message']:
                            thinking_content = data['choices'][0]['message']['reasoning_content']
                            print(f"[{doc_index}/{total_docs}] [OK] Extended thinking content captured ({len(thinking_content)} characters)")
                        elif 'reasoning_details' in data['choices'][0]['message']:
                            thinking_content = str(data['choices'][0]['message']['reasoning_details'])
                            print(f"[{doc_index}/{total_docs}] [OK] Reasoning details captured")

                        result = {
                            'document_title': doc_title,
                            'document_authors': doc_authors,
                            'analysis_timestamp': datetime.now().isoformat(),
                            'model': 'anthropic/claude-sonnet-4.5',
                            'response': response_content,
                            'thinking': thinking_content,
                            'usage': data.get('usage', {}),
                            'raw_response': data  # Store full response for debugging
                        }

                        print(f"[{doc_index}/{total_docs}] [OK] Driver extraction completed successfully")
                        return result

                except aiohttp.ClientError as e:
                    # Handle other client errors with retry
                    retry_count += 1
                    if retry_count > MAX_RETRIES:
                        print(f"[{doc_index}/{total_docs}] [ERROR] Max retries exceeded: {str(e)}")
                        return None

                    print(f"[{doc_index}/{total_docs}] [WARNING] Request failed, retrying in {retry_delay}s: {str(e)}")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue

        except Exception as e:
            print(f"[{doc_index}/{total_docs}] [ERROR] Unexpected error: {str(e)}")
            return None

    return None


def save_output(result: Dict, doc_name: str, doc_index: int, total_docs: int) -> None:
    """
    Save the extraction results to the outputs folder with timestamped filename.

    Args:
        result: Dictionary containing the analysis results
        doc_name: Short name for the document (for filename)
        doc_index: Index of current document
        total_docs: Total number of documents
    """
    # Create outputs directory if it doesn't exist
    output_dir = Path('outputs/extract_drivers_v2')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamped filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Extract the clean JSON drivers array from the response
    print(f"[{doc_index}/{total_docs}] [OK] Extracting structured drivers JSON from response...")
    drivers_json = extract_json_from_response(result['response'])

    if drivers_json:
        # Save the clean drivers-only JSON
        drivers_filename = f"{timestamp}_drivers_{doc_name}.json"
        drivers_filepath = output_dir / drivers_filename

        print(f"[{doc_index}/{total_docs}] [OK] Saving clean drivers JSON to: {drivers_filepath}")
        with open(drivers_filepath, 'w', encoding='utf-8') as f:
            json.dump(drivers_json, f, indent=2, ensure_ascii=False)

        # Add extracted drivers to result for full output
        result['extracted_drivers'] = drivers_json

        # Count total drivers across all categories
        total_drivers = sum(len(drivers_json['drivers'].get(cat, []))
                          for cat in drivers_json['drivers'].keys())
        print(f"[{doc_index}/{total_docs}] [OK] Successfully extracted {total_drivers} drivers across {len(drivers_json['drivers'])} categories")
    else:
        print(f"[{doc_index}/{total_docs}] [WARNING] Could not extract JSON from response - saving full response only")

    # Save full result with metadata
    full_filename = f"{timestamp}_full_result_{doc_name}.json"
    full_filepath = output_dir / full_filename

    print(f"[{doc_index}/{total_docs}] [OK] Saving full result with metadata to: {full_filepath}")
    with open(full_filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Save human-readable text version
    text_filename = f"{timestamp}_analysis_{doc_name}.txt"
    text_filepath = output_dir / text_filename

    with open(text_filepath, 'w', encoding='utf-8') as f:
        f.write(f"Document: {result['document_title']}\n")
        f.write(f"Authors: {result['document_authors']}\n")
        f.write(f"Analysis Date: {result['analysis_timestamp']}\n")
        f.write(f"Model: {result['model']}\n")
        f.write("=" * 80 + "\n\n")

        if result.get('thinking'):
            f.write("EXTENDED THINKING:\n")
            f.write("=" * 80 + "\n")
            f.write(result['thinking'])
            f.write("\n\n" + "=" * 80 + "\n\n")

        f.write("RESPONSE:\n")
        f.write("=" * 80 + "\n")
        f.write(result['response'])

    print(f"[{doc_index}/{total_docs}] [OK] Text version saved to: {text_filepath}")
    print(f"[{doc_index}/{total_docs}] [OK] Extraction complete!")
    print(f"\n[{doc_index}/{total_docs}] [OK] Output files:")
    if drivers_json:
        print(f"  - Clean drivers JSON: {drivers_filename}")
    print(f"  - Full result with metadata: {full_filename}")
    print(f"  - Human-readable analysis: {text_filename}")


async def process_all_documents_async(skip_existing: bool = True) -> None:
    """
    Process all trajectory documents and extract drivers asynchronously.

    Args:
        skip_existing: If True, skip documents that already have output files
    """
    # Check for API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("[ERROR] OPENROUTER_API_KEY not found in .env file")
        return

    # Read the driver prompt template once
    print("[OK] Loading driver prompt template...")
    with open('claude/driver_prompt.md', 'r', encoding='utf-8') as f:
        prompt_template = f.read()

    # Get all documents
    documents = get_all_documents()

    print("=" * 80)
    print("ASYNC BATCH DRIVER EXTRACTION FOR ALL TRAJECTORY DOCUMENTS")
    print("=" * 80)
    print(f"\n[OK] Found {len(documents)} documents to process")
    print(f"[OK] Max concurrent requests: {MAX_CONCURRENT_REQUESTS}")
    print(f"[OK] Max retries per document: {MAX_RETRIES}")
    if TEST_MODE:
        print(f"[TEST MODE] Enabled - truncating documents to {TEST_DOC_LENGTH} characters")
    print()

    output_dir = Path('outputs/extract_drivers_v2')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Filter documents to process
    documents_to_process = []
    print("[OK] Filtering documents to process...")
    for i, (display_name, doc_path) in enumerate(documents, 1):
        print(f"[OK] Checking document {i}/{len(documents)}: {display_name[:50]}...")

        # Create safe filename from display name
        safe_name = re.sub(r'[^\w\s-]', '', display_name).strip().replace(' ', '_').lower()
        # Limit length for very long names
        if len(safe_name) > 80:
            safe_name = safe_name[:80]

        # Check if already processed
        if skip_existing:
            existing_files = list(output_dir.glob(f"*_drivers_{safe_name}.json"))
            if existing_files:
                print(f"[SKIP] Already processed - {display_name} (found {existing_files[0].name})")
                continue

        # Extract title and authors
        print(f"[OK] Extracting metadata for: {display_name[:50]}...")
        title, authors = extract_title_and_authors(doc_path)
        documents_to_process.append((display_name, doc_path, title, authors, safe_name))
        print(f"[OK] Added to queue: {title[:50]}...")

    if not documents_to_process:
        print("\n[OK] All documents already processed!")
        return

    # TEST MODE: Limit to first 5 documents
    if TEST_MODE and len(documents_to_process) > 5:
        print(f"[TEST MODE] Limiting to first 5 documents (out of {len(documents_to_process)} available)")
        documents_to_process = documents_to_process[:5]

    print(f"\n[OK] Processing {len(documents_to_process)} documents...\n")

    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    # Create aiohttp session
    async with aiohttp.ClientSession() as session:
        # Create async wrapper to track completion with metadata
        async def process_with_metadata(display_name, doc_path, title, authors, safe_name, idx):
            result = await extract_drivers_async(
                session=session,
                doc_path=doc_path,
                doc_title=title,
                doc_authors=authors,
                api_key=api_key,
                prompt_template=prompt_template,
                semaphore=semaphore,
                doc_index=idx,
                total_docs=len(documents_to_process)
            )
            return (result, display_name, safe_name, idx, len(documents_to_process))

        # Create tasks for all documents
        tasks = []
        for i, (display_name, doc_path, title, authors, safe_name) in enumerate(documents_to_process, 1):
            task = process_with_metadata(display_name, doc_path, title, authors, safe_name, i)
            tasks.append(task)

        # Execute all tasks concurrently
        print(f"[OK] Starting parallel processing of {len(tasks)} documents...")
        print(f"[OK] Processing in batches of {MAX_CONCURRENT_REQUESTS}...\n")

        # Process results as they complete and SAVE IMMEDIATELY
        completed_count = 0
        successful = 0
        failed = 0
        batch_start_time = datetime.now()

        for coro in asyncio.as_completed(tasks):
            task_result = await coro
            completed_count += 1

            result, display_name, safe_name, idx, total = task_result

            # Show progress
            elapsed = (datetime.now() - batch_start_time).total_seconds()
            status = "[OK]" if result else "[ERROR]"
            print(f"\n{status} [{completed_count}/{len(tasks)}] Completed: {display_name}")
            print(f"[PROGRESS] {completed_count}/{len(tasks)} documents ({completed_count/len(tasks)*100:.1f}%) - Elapsed: {elapsed:.1f}s")

            # SAVE IMMEDIATELY after each completion
            if result:
                try:
                    print(f"\n[{completed_count}/{len(tasks)}] [OK] Saving output files immediately...")
                    save_output(result, safe_name, idx, total)
                    successful += 1
                    print(f"[{completed_count}/{len(tasks)}] [OK] Files saved successfully!\n")
                except Exception as e:
                    print(f"[{completed_count}/{len(tasks)}] [ERROR] Failed to save {display_name}: {str(e)}\n")
                    failed += 1
            else:
                print(f"[{completed_count}/{len(tasks)}] [ERROR] Failed to extract drivers from: {display_name}\n")
                failed += 1

            # Show batch completion summary
            if completed_count % MAX_CONCURRENT_REQUESTS == 0:
                avg_time = elapsed / completed_count
                remaining = len(tasks) - completed_count
                estimated_remaining = avg_time * remaining
                print(f"\n{'='*60}")
                print(f"[BATCH COMPLETE] Completed batch of {MAX_CONCURRENT_REQUESTS}!")
                print(f"[STATS] Avg time per doc: {avg_time:.1f}s")
                print(f"[STATS] Success: {successful} | Failed: {failed}")
                print(f"[ESTIMATE] Remaining: {remaining} docs, ~{estimated_remaining:.1f}s ({estimated_remaining/60:.1f} minutes)")
                print(f"{'='*60}\n")

    print(f"\n{'=' * 80}")
    print("[OK] Async batch processing complete!")
    print(f"{'=' * 80}")
    print(f"[OK] Successful: {successful}")
    print(f"[ERROR] Failed: {failed}")
    print(f"[OK] Total: {successful + failed}\n")


def main():
    """Main entry point for the async driver extraction script."""
    # Run the async processing
    asyncio.run(process_all_documents_async(skip_existing=True))


async def test_mode():
    """Test mode: Process only first 5 docs with truncated content."""
    global TEST_MODE
    TEST_MODE = True

    print("\n" + "="*80)
    print("RUNNING IN TEST MODE - FIRST 5 DOCS ONLY, TRUNCATED TO 500 CHARS")
    print("="*80 + "\n")

    await process_all_documents_async(skip_existing=False)


if __name__ == "__main__":
    import sys

    # Check for test mode flag
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("[OK] Starting in TEST MODE...")
        asyncio.run(test_mode())
    else:
        main()

    # To reprocess all documents (overwrite existing), use:
    # asyncio.run(process_all_documents_async(skip_existing=False))

    # To run test mode: python extract_all_drivers_async.py --test
