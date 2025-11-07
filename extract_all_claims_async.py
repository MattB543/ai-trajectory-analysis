"""
Extract claims from all AI trajectory documents using concurrent OpenRouter API calls.

This script processes all markdown documents in the docs/ folder (excluding summaries),
extracts structured claims using Claude Sonnet 4.5 via OpenRouter API, and saves
the results as timestamped JSON files in outputs/claims/.

Usage:
    python extract_all_claims_async.py              # Process all documents
    python extract_all_claims_async.py --test       # Test mode (first 3 documents)
    python extract_all_claims_async.py --skip       # Skip already processed documents
"""

import asyncio
import aiohttp
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from dotenv import load_dotenv
import sys

# Configuration
MAX_CONCURRENT_REQUESTS = 5  # Process 5 documents in parallel
MAX_RETRIES = 5              # Maximum number of retries for errors
INITIAL_RETRY_DELAY = 2      # Initial delay in seconds for exponential backoff
REQUEST_TIMEOUT = 900        # 15 minute timeout for extended thinking

# Directories
DOCS_DIR = "docs"
OUTPUT_DIR = "outputs/claims"
PROMPT_TEMPLATE_PATH = "claude/claims_prompt.md"


def load_prompt_template() -> str:
    """Load the claims extraction prompt template."""
    try:
        with open(PROMPT_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            template = f.read()
        print(f"[OK] Loaded prompt template from {PROMPT_TEMPLATE_PATH}")
        return template
    except FileNotFoundError:
        print(f"[ERROR] Prompt template not found at {PROMPT_TEMPLATE_PATH}")
        sys.exit(1)


def load_documents() -> List[Tuple[str, str, str]]:
    """
    Load all markdown documents from docs/ folder, excluding summaries.

    Returns:
        List of tuples: (file_path, content, base_name)
    """
    documents = []
    docs_path = Path(DOCS_DIR)

    if not docs_path.exists():
        print(f"[ERROR] Documents directory not found: {DOCS_DIR}")
        sys.exit(1)

    # Find all .md files recursively
    for md_file in docs_path.rglob("*.md"):
        # Skip files with "summary" in the name
        if "summary" in md_file.name.lower():
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Get base name without extension
            base_name = md_file.stem

            documents.append((str(md_file), content, base_name))

        except Exception as e:
            print(f"[WARNING] Could not read {md_file}: {str(e)}")

    print(f"[OK] Found {len(documents)} documents to process")
    return documents


def create_prompt(template: str, document: str) -> str:
    """
    Create the full prompt by substituting the document into the template.

    Args:
        template: The prompt template with ${document} placeholder
        document: The document content

    Returns:
        Complete prompt string
    """
    # Replace the ${document} placeholder
    prompt = template.replace("${document}", document)
    return prompt


def generate_output_filename(doc_base_name: str) -> str:
    """
    Generate timestamped output filename.

    Args:
        doc_base_name: Base name of the document

    Returns:
        Filename in format: YYYYMMDD_HHMMSS_docname_claims.json
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{doc_base_name}_claims.json"


def save_claims_json(data: Dict, doc_base_name: str, output_dir: str) -> bool:
    """
    Save claims JSON to output directory.

    Args:
        data: The JSON data to save
        doc_base_name: Base name of the document
        output_dir: Output directory path

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename
        filename = generate_output_filename(doc_base_name)
        filepath = os.path.join(output_dir, filename)

        # Save JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Saved to {filename}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to save {doc_base_name}: {str(e)}")
        return False


async def make_openrouter_call(
    session: aiohttp.ClientSession,
    prompt: str,
    api_key: str,
    semaphore: asyncio.Semaphore,
    doc_info: Tuple[str, str, str],
    doc_index: int,
    total_docs: int
) -> Optional[Dict]:
    """
    Make a single OpenRouter API call with retry logic.

    Args:
        session: Shared aiohttp ClientSession
        prompt: The complete prompt to send
        api_key: OpenRouter API key
        semaphore: Semaphore to limit concurrent requests
        doc_info: Tuple of (file_path, content, base_name)
        doc_index: Index of current document (for logging)
        total_docs: Total number of documents (for logging)

    Returns:
        API response data or None if failed
    """
    file_path, _, base_name = doc_info

    async with semaphore:  # This limits concurrent requests
        print(f"\n[{doc_index}/{total_docs}] Starting: {base_name}")
        print(f"[{doc_index}/{total_docs}] Document: {file_path}")

        # Prepare request headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/ai-trajectory-analysis",
            "X-Title": "AI Trajectory Claims Extraction",
            "Content-Type": "application/json"
        }

        # Prepare request payload
        payload = {
            "model": "anthropic/claude-sonnet-4.5",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0,  # For consistency
            "reasoning": {
                "effort": "high"  # Extended thinking
            },
            "max_tokens": 64000
        }

        # Retry logic with exponential backoff
        retry_count = 0
        retry_delay = INITIAL_RETRY_DELAY

        while retry_count <= MAX_RETRIES:
            try:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
                ) as response:

                    # Handle rate limit errors (429)
                    if response.status == 429:
                        retry_count += 1
                        if retry_count > MAX_RETRIES:
                            print(f"[{doc_index}/{total_docs}] [ERROR] Max retries exceeded for {base_name}")
                            return None

                        print(f"[{doc_index}/{total_docs}] [WARNING] Rate limit, retrying in {retry_delay}s...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue

                    # Raise for other HTTP errors
                    response.raise_for_status()

                    # Parse response
                    data = await response.json()

                    # Extract the content from the response
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"]["content"]

                        # Try to parse the JSON from the content
                        # The response should contain JSON, possibly wrapped in markdown code blocks
                        content = content.strip()

                        # Remove markdown code blocks if present
                        if content.startswith("```json"):
                            content = content[7:]  # Remove ```json
                        elif content.startswith("```"):
                            content = content[3:]  # Remove ```

                        if content.endswith("```"):
                            content = content[:-3]  # Remove closing ```

                        content = content.strip()

                        # Parse as JSON
                        try:
                            claims_data = json.loads(content)
                            print(f"[{doc_index}/{total_docs}] [OK] Response received - {len(claims_data.get('claims', []))} claims extracted")
                            return claims_data
                        except json.JSONDecodeError as e:
                            print(f"[{doc_index}/{total_docs}] [ERROR] Invalid JSON in response: {str(e)}")
                            print(f"[{doc_index}/{total_docs}] [DEBUG] First 500 chars: {content[:500]}")
                            return None
                    else:
                        print(f"[{doc_index}/{total_docs}] [ERROR] Unexpected response format")
                        return None

            except aiohttp.ClientError as e:
                retry_count += 1
                if retry_count > MAX_RETRIES:
                    print(f"[{doc_index}/{total_docs}] [ERROR] Max retries exceeded for {base_name}: {str(e)}")
                    return None

                print(f"[{doc_index}/{total_docs}] [WARNING] Retrying in {retry_delay}s: {str(e)}")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
                continue

            except Exception as e:
                print(f"[{doc_index}/{total_docs}] [ERROR] Unexpected error for {base_name}: {str(e)}")
                return None

        return None


async def process_documents_async(
    documents: List[Tuple[str, str, str]],
    prompt_template: str,
    skip_existing: bool = False
) -> None:
    """
    Process multiple documents concurrently.

    Args:
        documents: List of (file_path, content, base_name) tuples
        prompt_template: The prompt template string
        skip_existing: If True, skip documents that already have output files
    """
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("[ERROR] OPENROUTER_API_KEY not found in environment")
        print("[ERROR] Please set it in your .env file")
        sys.exit(1)

    # Filter out already processed documents if skip_existing is True
    if skip_existing:
        existing_files = set(os.listdir(OUTPUT_DIR)) if os.path.exists(OUTPUT_DIR) else set()
        documents_to_process = []

        for doc in documents:
            file_path, content, base_name = doc
            # Check if any file contains this base_name
            already_exists = any(base_name in f for f in existing_files)

            if already_exists:
                print(f"[SKIP] Already processed: {base_name}")
            else:
                documents_to_process.append(doc)

        documents = documents_to_process

        if not documents:
            print("\n[OK] All documents already processed!")
            return

    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    # Create single aiohttp session for all requests
    async with aiohttp.ClientSession() as session:

        # Create wrapper function with metadata
        async def process_with_metadata(doc, idx):
            file_path, content, base_name = doc

            # Create the full prompt
            prompt = create_prompt(prompt_template, content)

            # Make API call
            result = await make_openrouter_call(
                session=session,
                prompt=prompt,
                api_key=api_key,
                semaphore=semaphore,
                doc_info=doc,
                doc_index=idx,
                total_docs=len(documents)
            )

            return (result, doc, idx)

        # Create tasks for all documents
        tasks = []
        for i, doc in enumerate(documents, 1):
            task = process_with_metadata(doc, i)
            tasks.append(task)

        # Execute all tasks concurrently
        print(f"\n{'='*80}")
        print(f"[OK] Starting parallel processing of {len(tasks)} documents...")
        print(f"[OK] Processing in batches of {MAX_CONCURRENT_REQUESTS}...")
        print(f"[OK] Estimated time: ~{(len(tasks) / MAX_CONCURRENT_REQUESTS * 3):.0f} minutes")
        print(f"{'='*80}\n")

        start_time = datetime.now()

        # Process results as they complete
        completed_count = 0
        successful = 0
        failed = 0

        for coro in asyncio.as_completed(tasks):
            result, doc, idx = await coro
            completed_count += 1

            file_path, content, base_name = doc

            if result:
                # Save result immediately
                if save_claims_json(result, base_name, OUTPUT_DIR):
                    successful += 1
                    print(f"[PROGRESS] {completed_count}/{len(tasks)} completed ({successful} successful, {failed} failed)")
                else:
                    failed += 1
                    print(f"[PROGRESS] {completed_count}/{len(tasks)} completed ({successful} successful, {failed} failed)")
            else:
                failed += 1
                print(f"[{idx}/{len(tasks)}] [ERROR] Failed to process: {base_name}")
                print(f"[PROGRESS] {completed_count}/{len(tasks)} completed ({successful} successful, {failed} failed)")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Print final summary
        print(f"\n{'='*80}")
        print(f"[OK] Processing complete!")
        print(f"[OK] Total time: {duration/60:.1f} minutes")
        print(f"[OK] Successful: {successful}/{len(tasks)}")
        print(f"[OK] Failed: {failed}/{len(tasks)}")
        print(f"[OK] Output directory: {OUTPUT_DIR}")
        print(f"{'='*80}\n")


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Check for command line arguments
    test_mode = "--test" in sys.argv
    skip_existing = "--skip" in sys.argv

    print("\n" + "="*80)
    print("AI Trajectory Claims Extraction")
    print("="*80 + "\n")

    if test_mode:
        print("[TEST MODE] Processing first 3 documents only\n")

    # Load prompt template
    prompt_template = load_prompt_template()

    # Load documents
    documents = load_documents()

    if not documents:
        print("[ERROR] No documents found to process")
        sys.exit(1)

    # Print document list
    print("\nDocuments to process:")
    for i, (path, _, name) in enumerate(documents, 1):
        print(f"  {i}. {name}")
    print()

    # Apply test mode filter
    if test_mode:
        documents = documents[:3]
        print(f"[TEST MODE] Limited to {len(documents)} documents\n")

    # Run async processing
    asyncio.run(process_documents_async(documents, prompt_template, skip_existing))

    print("[OK] All done! Check the outputs/claims/ folder for results.\n")


if __name__ == "__main__":
    main()
