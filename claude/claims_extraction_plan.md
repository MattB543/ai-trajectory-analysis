# Claims Extraction Implementation Plan

**Created:** 2025-10-13
**Purpose:** Extract structured claims from 23 AI trajectory documents using concurrent OpenRouter API calls

## Project Overview

**Objective:** Build an async Python script that processes all documents in the `docs/` folder, extracting structured claims using Claude Sonnet 4.5 via OpenRouter API, with concurrent processing following established patterns in this repository.

## Current State Analysis

### Documents to Process
- **Total documents:** 23 markdown files
- **Location:** `docs/` folder and subfolders
- **Format:** Markdown (.md)
- **Size range:** 330 to 4500+ lines
- **Filter:** Skip files with "summary" in the filename

### Documents List
```
1. docs/Advanced AI_ Possible Futures (five scenarios)/advanced_ai_possible_futures_arms_race.md
2. docs/Advanced AI_ Possible Futures (five scenarios)/advanced_ai_possible_futures_big_ai.md
3. docs/Advanced AI_ Possible Futures (five scenarios)/advanced_ai_possible_futures_diplomacy.md
4. docs/Advanced AI_ Possible Futures (five scenarios)/advanced_ai_possible_futures_plateau.md
5. docs/Advanced AI_ Possible Futures (five scenarios)/advanced_ai_possible_futures_take_off.md
6. docs/AGI and Lock-In/agi_and_lock_in.md
7. docs/AGI Ruin_ A List of Lethalities/agi_ruin_a_list_of_lethalities.md
8. docs/AGI, Governments, and Free Societies/agi_governments_and_free_societies.md
9. docs/AI & Leviathan (Parts I–III)/ai_and_leviathan_parts_i_to_iii.md
10. docs/AI 2027/ai_2027.md
11. docs/AI as Normal Technology/ai_as_normal_technology.md
12. docs/AI-Enabled Coups/ai_enabled_coups.md
13. docs/Artificial General Intelligence and the Rise and Fall of Nations_ Visions for Potential AGI Futures/artificial_general_intelligence_and_the_rise_and_fall_of_nations.md
14. docs/Could Advanced AI Drive Explosive Economic Growth/could_advanced_ai_drive_explosive_economic_growth.md
15. docs/d_acc Pathway/d_acc_pathway.md
16. docs/Gradual Disempowerment/gradual_disempowerment.md
17. docs/Machines of Loving Grace/machines_of_loving_grace.md
18. docs/Situational Awareness_ The Decade Ahead/situational_awareness_the_decade_ahead.md
19. docs/Soft Nationalization_ How the US Government Will Control AI Labs/soft_nationalization_how_the_us_government_will_control_ai_labs.md
20. docs/The AI Revolution - Wait but Why/the_ai_revolution_wait_but_why.md
21. docs/The Intelligence Curse (series)/the_intelligence_curse_series.md
22. docs/Tool AI Pathway/tool_ai_pathway.md
23. docs/What Failure Looks Like/what_failure_looks_like.md
```

### Existing Infrastructure
- ✅ `outputs/claims/` directory exists (empty)
- ✅ `claude/claims_prompt.md` exists (template with ${document} placeholder)
- ✅ `claude/concurrent_openrouter_api_calls_guide.md` exists (implementation guide)
- ❌ No `.env` file (needs to be created)
- ❌ No `requirements.txt` (needs to be created)
- ❌ No existing async processing scripts

## Technical Requirements

### API Configuration
- **Provider:** OpenRouter (https://openrouter.ai/api/v1/chat/completions)
- **Model:** `anthropic/claude-sonnet-4.5`
- **Temperature:** 0 (for consistency)
- **Max tokens:** 64000 (claims extraction can produce lengthy JSON)
- **Extended thinking:** High effort mode (for complex claim identification)
- **API Key:** From environment variable `OPENROUTER_API_KEY`

### Concurrency Settings
- **MAX_CONCURRENT_REQUESTS:** 5 (balanced approach)
- **MAX_RETRIES:** 5
- **INITIAL_RETRY_DELAY:** 2 seconds
- **Timeout:** 900 seconds (15 minutes - these are long documents)

### Output Format
- **Location:** `outputs/claims/`
- **Naming:** `YYYYMMDD_HHMMSS_<doc_name>_claims.json`
- **Example:** `20251013_210530_ai_2027_claims.json`
- **Content:** Raw JSON response from API (validated structure)

## Implementation Components

### 1. Script Structure: `extract_all_claims_async.py`

#### Core Functions

**`load_prompt_template()`**
- Read `claude/claims_prompt.md`
- Return template string

**`load_documents()`**
- Recursively find all `.md` files in `docs/` folder
- Filter out files containing "summary" in filename
- Read file contents
- Return list of tuples: `(file_path, content, base_name)`

**`create_prompt(template: str, document: str) -> str`**
- Replace `${document}` placeholder with actual document content
- Return complete prompt

**`make_openrouter_call(session, prompt, api_key, semaphore, doc_info, doc_index, total_docs)`**
- Async function for single API call
- Parameters:
  - `session`: Shared aiohttp ClientSession
  - `prompt`: Complete prompt with document
  - `api_key`: OpenRouter API key
  - `semaphore`: Concurrency limiter
  - `doc_info`: Tuple of (file_path, content, base_name)
  - `doc_index`: Current document number (for logging)
  - `total_docs`: Total document count
- Returns: API response data or None on failure
- Features:
  - Semaphore-based rate limiting
  - Exponential backoff for 429 errors
  - Detailed logging with document index
  - 15-minute timeout

**`save_claims_json(data, doc_base_name, output_dir)`**
- Generate timestamped filename
- Validate JSON structure (basic check)
- Save to `outputs/claims/` folder
- Return success/failure status

**`process_documents_async(documents, prompt_template)`**
- Main async orchestration function
- Create semaphore and aiohttp session
- Create tasks for all documents
- Use `asyncio.as_completed()` for immediate result processing
- Save results immediately as they complete
- Track success/failure counts
- Display progress and statistics

**`main()`**
- Entry point
- Load environment variables
- Validate API key exists
- Load prompt template
- Load documents
- Run async processing
- Print summary statistics

### 2. Dependencies: `requirements.txt`
```
aiohttp>=3.9.0
python-dotenv>=1.0.0
```

### 3. Configuration: `.env.example`
```
OPENROUTER_API_KEY=your_api_key_here
```

### 4. Helper Scripts

**`validate_claims_json.py`** (optional but recommended)
- Read all JSON files in `outputs/claims/`
- Validate structure matches expected schema
- Report any malformed outputs
- Display statistics (claims per doc, claim types, etc.)

## Implementation Steps

### Phase 1: Setup (5 minutes)
1. Create `requirements.txt`
2. Create `.env.example` template
3. Prompt user to create `.env` with their API key
4. Install dependencies: `pip install -r requirements.txt`

### Phase 2: Core Script Development (20 minutes)
1. Import statements and configuration constants
2. Implement `load_prompt_template()`
3. Implement `load_documents()`
4. Implement `create_prompt()`
5. Implement `make_openrouter_call()` with full error handling
6. Implement `save_claims_json()`
7. Implement `process_documents_async()`
8. Implement `main()` entry point

### Phase 3: Testing & Validation (10 minutes)
1. Test with single document first (modify to process only 1 doc)
2. Validate JSON output structure
3. Test error handling (simulate 429 errors)
4. Run full batch on all 23 documents
5. Verify all outputs saved correctly

### Phase 4: Optional Enhancements (5 minutes)
1. Create validation script for JSON outputs
2. Add support for `--test` mode (limit to 3 documents)
3. Add support for `--skip-existing` (don't reprocess existing outputs)
4. Add `--resume` functionality

## Expected Runtime

**Sequential Processing:** 23 documents × ~3 minutes/doc = ~69 minutes

**Concurrent Processing (5 parallel):** 23 documents ÷ 5 × ~3 minutes = ~14 minutes

**Note:** Times may vary based on:
- Document length
- API response time
- Rate limiting
- Extended thinking time

## Error Handling Strategy

### Recoverable Errors
- **429 (Rate Limit):** Exponential backoff, retry up to 5 times
- **Network errors:** Same retry logic
- **Timeout:** Log and continue to next document

### Non-Recoverable Errors
- **Missing API key:** Exit with error message
- **Invalid template:** Exit with error message
- **No documents found:** Exit with warning

### Output Handling
- Save successful results immediately (don't wait for all)
- Log failed documents to console
- Continue processing even if some documents fail
- Final summary shows success/failure counts

## File Structure After Implementation

```
ai-trajectory-analysis-v2/
├── claude/
│   ├── claims_prompt.md (existing)
│   ├── concurrent_openrouter_api_calls_guide.md (existing)
│   └── claims_extraction_plan.md (this file)
├── docs/
│   └── [23 document files in subfolders]
├── outputs/
│   └── claims/
│       ├── 20251013_210530_ai_2027_claims.json
│       ├── 20251013_210645_agi_and_lock_in_claims.json
│       └── [... 21 more JSON files]
├── .env (user creates this)
├── .env.example (we create this)
├── requirements.txt (we create this)
├── extract_all_claims_async.py (we create this)
└── validate_claims_json.py (optional, we can create this)
```

## Success Criteria

1. ✅ All 23 documents processed successfully
2. ✅ All JSON outputs saved with correct naming convention
3. ✅ JSON outputs follow the schema defined in claims_prompt.md
4. ✅ No more than 5 concurrent API requests at a time
5. ✅ Proper error handling with retries
6. ✅ Progress logging during execution
7. ✅ Summary statistics at completion
8. ✅ Processing completes in ~15 minutes or less

## Validation Checks

### Per-Document Validation
- JSON is valid (parseable)
- Has `document_metadata` object
- Has `claims` array
- Each claim has required fields: `claim_id`, `claim_type`, `claim_text`, `confidence`, `quote`
- Claim types are from allowed list

### Batch Validation
- All 23 output files exist
- No duplicate timestamps (unlikely but check)
- File sizes are reasonable (>1KB, suggesting actual content)
- Can parse all files as valid JSON

## Potential Issues & Solutions

### Issue: Rate Limiting
**Solution:**
- Already using semaphore with limit of 5
- Exponential backoff implemented
- Can reduce MAX_CONCURRENT_REQUESTS if needed

### Issue: Large Documents Causing Timeouts
**Solution:**
- 15-minute timeout should be sufficient
- Extended thinking mode may take longer
- Can increase timeout if needed

### Issue: Malformed JSON Responses
**Solution:**
- Log raw response before attempting to parse
- Save even if JSON is malformed (for debugging)
- Add try/except around JSON parsing

### Issue: API Key Not Set
**Solution:**
- Check at startup, fail fast with clear message
- Provide example of how to set it

### Issue: Documents Not Found
**Solution:**
- Verify path resolution (handle Windows paths)
- Print document list before processing
- User can verify documents will be processed

## Next Steps

1. User reviews and approves this plan
2. Implement Phase 1 (Setup)
3. Implement Phase 2 (Core Script)
4. Test with single document
5. Run full batch
6. Validate outputs
7. Celebrate! 🎉

## Notes

- This is a production-ready implementation following the concurrent API patterns documented in the guide
- The script will be reusable for future document batches
- The async pattern can handle hundreds of documents efficiently
- Consider adding `--test` mode for rapid iteration during development
- JSON validation script will be valuable for ensuring data quality
- All outputs are immediately saved, so partial failures don't lose all progress

---

**Ready to implement!** This plan provides a clear roadmap for building a robust, concurrent claims extraction pipeline.
