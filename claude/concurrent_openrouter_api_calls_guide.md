# Guide: Making Multiple Concurrent OpenRouter API Calls

**Created:** 2025-10-13
**Purpose:** Documentation file created at direct user request to explain how to make concurrent API calls to OpenRouter as implemented in this repository.

## Overview

This guide explains how to make multiple concurrent API calls to OpenRouter (or any API) efficiently using Python's `asyncio` and `aiohttp` libraries. This pattern is used throughout this repository to process multiple documents in parallel, significantly reducing total processing time.

## Key Concepts

### 1. Asynchronous Programming with `asyncio`

Instead of making API calls one at a time (synchronous), we make multiple calls simultaneously (asynchronous). This allows us to:
- Process multiple documents in parallel
- Maximize throughput and minimize total processing time
- Handle rate limits and retries gracefully

### 2. Rate Limiting with Semaphores

A **semaphore** is a concurrency control mechanism that limits how many operations can run simultaneously. This prevents overwhelming the API with too many requests at once.

## Implementation Pattern

### Configuration

```python
import asyncio
import aiohttp

# Configuration constants
MAX_CONCURRENT_REQUESTS = 5  # Process 5 documents in parallel
MAX_RETRIES = 5              # Maximum number of retries for errors
INITIAL_RETRY_DELAY = 2      # Initial delay in seconds for exponential backoff
```

### Core Components

#### 1. Async Function for Single API Call

```python
async def make_openrouter_call(
    session: aiohttp.ClientSession,
    prompt: str,
    api_key: str,
    semaphore: asyncio.Semaphore,
    doc_index: int,
    total_docs: int
) -> Optional[Dict]:
    """
    Make a single OpenRouter API call with retry logic.

    Args:
        session: Shared aiohttp ClientSession
        prompt: The prompt to send
        api_key: OpenRouter API key
        semaphore: Semaphore to limit concurrent requests
        doc_index: Index of current document (for logging)
        total_docs: Total number of documents (for logging)

    Returns:
        API response data or None if failed
    """
    async with semaphore:  # This limits concurrent requests
        print(f"[{doc_index}/{total_docs}] [OK] Starting API call...")

        # Prepare request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/your-project",
            "X-Title": "Your Project Name",
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
                "effort": "high"  # For extended thinking
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
                    timeout=aiohttp.ClientTimeout(total=900)  # 15 minute timeout
                ) as response:

                    # Handle rate limit errors (429)
                    if response.status == 429:
                        retry_count += 1
                        if retry_count > MAX_RETRIES:
                            print(f"[{doc_index}/{total_docs}] [ERROR] Max retries exceeded")
                            return None

                        print(f"[{doc_index}/{total_docs}] [WARNING] Rate limit, retrying in {retry_delay}s")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue

                    response.raise_for_status()
                    data = await response.json()

                    print(f"[{doc_index}/{total_docs}] [OK] Response received")
                    return data

            except aiohttp.ClientError as e:
                retry_count += 1
                if retry_count > MAX_RETRIES:
                    print(f"[{doc_index}/{total_docs}] [ERROR] Max retries exceeded: {str(e)}")
                    return None

                print(f"[{doc_index}/{total_docs}] [WARNING] Retrying in {retry_delay}s: {str(e)}")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
                continue

        return None
```

#### 2. Main Processing Function

```python
async def process_multiple_documents_async(documents: List[str]) -> None:
    """
    Process multiple documents concurrently.

    Args:
        documents: List of documents to process
    """
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("[ERROR] OPENROUTER_API_KEY not found")
        return

    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    # Create single aiohttp session for all requests
    async with aiohttp.ClientSession() as session:

        # Create wrapper function with metadata
        async def process_with_metadata(doc, idx):
            result = await make_openrouter_call(
                session=session,
                prompt=doc,  # Or build your prompt here
                api_key=api_key,
                semaphore=semaphore,
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
        print(f"[OK] Starting parallel processing of {len(tasks)} documents...")
        print(f"[OK] Processing in batches of {MAX_CONCURRENT_REQUESTS}...\n")

        # Process results as they complete
        completed_count = 0
        successful = 0
        failed = 0

        for coro in asyncio.as_completed(tasks):
            result, doc, idx = await coro
            completed_count += 1

            if result:
                print(f"[OK] [{completed_count}/{len(tasks)}] Completed successfully")
                # Save or process result here
                successful += 1
            else:
                print(f"[ERROR] [{completed_count}/{len(tasks)}] Failed")
                failed += 1

        print(f"\n[OK] Processing complete! Success: {successful}, Failed: {failed}")
```

#### 3. Entry Point

```python
def main():
    """Main entry point."""
    documents = ["doc1", "doc2", "doc3", ...]  # Your documents

    # Run the async processing
    asyncio.run(process_multiple_documents_async(documents))

if __name__ == "__main__":
    main()
```

## How It Works

### Flow Diagram

```
1. Create semaphore (limit = 5)
2. Create aiohttp session
3. Create tasks for all documents
   ├─> Task 1 (waits for semaphore)
   ├─> Task 2 (waits for semaphore)
   ├─> Task 3 (waits for semaphore)
   ├─> Task 4 (waits for semaphore)
   ├─> Task 5 (waits for semaphore)
   ├─> Task 6 (blocked by semaphore)
   └─> Task 7 (blocked by semaphore)
4. First 5 tasks acquire semaphore and start
5. When Task 1 completes, it releases semaphore
6. Task 6 acquires semaphore and starts
7. Process continues until all tasks complete
```

### Semaphore Behavior

```python
# Semaphore with limit of 5
semaphore = asyncio.Semaphore(5)

async with semaphore:  # This blocks if 5 requests already running
    # Make API call
    # When this block exits, semaphore is released
```

**Key Points:**
- Maximum 5 requests run simultaneously
- When one completes, the next one starts
- This prevents overwhelming the API
- Reduces risk of rate limiting

### Exponential Backoff for Rate Limits

When a 429 (rate limit) error occurs:

```
Attempt 1: Wait 2 seconds
Attempt 2: Wait 4 seconds  (2 × 2)
Attempt 3: Wait 8 seconds  (4 × 2)
Attempt 4: Wait 16 seconds (8 × 2)
Attempt 5: Wait 32 seconds (16 × 2)
```

This gives the API time to recover while automatically retrying.

## Real-World Example from This Repo

See these files for complete implementations:
- `extract_all_drivers_async.py:189-336` - Driver extraction with concurrent API calls
- `extract_all_predictions_async.py:190-337` - Prediction extraction with concurrent API calls

### Key Features in These Implementations

1. **Immediate Saving**: Results are saved as soon as they complete (line 522-546)
2. **Progress Tracking**: Shows completion percentage and time estimates
3. **Error Handling**: Comprehensive error handling with retries
4. **Skip Existing**: Can skip already-processed documents
5. **Test Mode**: Supports testing with truncated documents
6. **Extended Thinking**: Uses Claude's extended thinking mode

### Performance Example

**Without Concurrency (Sequential):**
- 50 documents × 120 seconds each = 6000 seconds (100 minutes)

**With Concurrency (5 parallel):**
- 50 documents ÷ 5 concurrent × 120 seconds = 1200 seconds (20 minutes)

**Result:** 5× faster processing!

## Common Patterns

### Pattern 1: Process as Results Complete

```python
# Results are processed immediately as they finish
for coro in asyncio.as_completed(tasks):
    result = await coro
    # Save or process result immediately
    save_result(result)
```

**Benefit:** No need to wait for all tasks to complete before saving results.

### Pattern 2: Wait for All Results

```python
# Wait for all tasks to complete
results = await asyncio.gather(*tasks, return_exceptions=True)

# Then process all results
for result in results:
    if isinstance(result, Exception):
        print(f"[ERROR] Task failed: {result}")
    else:
        save_result(result)
```

**Benefit:** Simpler code when you need all results before proceeding.

### Pattern 3: Shared Session

```python
# Create one session for all requests
async with aiohttp.ClientSession() as session:
    # All API calls use this session
    tasks = [make_call(session, ...) for item in items]
    results = await asyncio.gather(*tasks)
```

**Benefit:** More efficient connection pooling and resource usage.

## Configuration Tips

### Adjusting Concurrency

```python
# Conservative (slower, safer)
MAX_CONCURRENT_REQUESTS = 3

# Moderate (balanced)
MAX_CONCURRENT_REQUESTS = 5

# Aggressive (faster, more likely to hit rate limits)
MAX_CONCURRENT_REQUESTS = 10
```

**Recommendation:** Start with 5 and adjust based on:
- API rate limits
- Your budget
- Error rate
- Processing time needs

### Timeout Configuration

```python
# Short timeout for quick responses
timeout=aiohttp.ClientTimeout(total=60)  # 1 minute

# Medium timeout for typical requests
timeout=aiohttp.ClientTimeout(total=300)  # 5 minutes

# Long timeout for extended thinking
timeout=aiohttp.ClientTimeout(total=900)  # 15 minutes
```

## Error Handling Best Practices

1. **Always use try-except** around API calls
2. **Implement exponential backoff** for rate limits
3. **Set reasonable timeouts** to prevent hanging
4. **Log all errors** with context (document index, etc.)
5. **Return None or sentinel value** on failure (don't raise)
6. **Save successful results immediately** (don't wait for all)

## Testing

### Test Mode Pattern

```python
TEST_MODE = False  # Set to True for testing

if TEST_MODE:
    # Truncate long inputs
    document_content = document_content[:500]

    # Limit number of documents
    documents = documents[:5]

    print("[TEST MODE] Running with limited data")
```

### Running Test Mode

```bash
# Run normally
python extract_all_drivers_async.py

# Run in test mode
python extract_all_drivers_async.py --test
```

## Common Issues and Solutions

### Issue 1: Rate Limiting (429 Errors)

**Solution:**
- Reduce `MAX_CONCURRENT_REQUESTS`
- Increase `INITIAL_RETRY_DELAY`
- Increase `MAX_RETRIES`

### Issue 2: Timeout Errors

**Solution:**
- Increase timeout value
- Check internet connection
- Reduce prompt/document size

### Issue 3: Memory Issues

**Solution:**
- Don't load all results in memory at once
- Save results as they complete
- Process in smaller batches

### Issue 4: Inconsistent Results

**Solution:**
- Check for proper error handling
- Verify all exceptions are caught
- Add more detailed logging

## Additional Resources

- **asyncio documentation:** https://docs.python.org/3/library/asyncio.html
- **aiohttp documentation:** https://docs.aiohttp.org/
- **OpenRouter API docs:** https://openrouter.ai/docs

## Summary

**Key Takeaways:**
1. Use `asyncio` + `aiohttp` for concurrent API calls
2. Use `Semaphore` to limit concurrent requests
3. Implement exponential backoff for rate limits
4. Use `asyncio.as_completed()` to process results as they finish
5. Share a single `ClientSession` across all requests
6. Handle errors gracefully with retries
7. Start with 5 concurrent requests and adjust based on performance

**Benefits:**
- 5-10× faster processing time
- Better resource utilization
- Graceful handling of rate limits
- Immediate result saving
- Progress tracking

This pattern is production-ready and used throughout this repository for efficient large-scale document processing.
