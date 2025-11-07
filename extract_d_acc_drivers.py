# File created: 2025-10-12
# Purpose: Extract drivers JSON from d_acc full_result file
# Created by: AI assistant to recover drivers from completed API call

import json
import re
from pathlib import Path
from datetime import datetime

# Use the same extraction function from the main script
def extract_json_from_response(response_text):
    """Extract JSON object from the response text."""
    # Try to find JSON in code blocks first
    json_block_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
    if json_block_match:
        try:
            parsed = json.loads(json_block_match.group(1))
            if isinstance(parsed, dict) and 'drivers' in parsed:
                return parsed
        except json.JSONDecodeError:
            pass

    # Try to find content after "KEY DRIVERS:" marker
    key_drivers_match = re.search(r'KEY DRIVERS:\s*([\s\S]*)', response_text, re.IGNORECASE)
    if key_drivers_match:
        remaining_text = key_drivers_match.group(1)
        json_block = re.search(r'```json\s*([\s\S]*?)\s*```', remaining_text)
        if json_block:
            try:
                parsed = json.loads(json_block.group(1))
                if isinstance(parsed, dict) and 'drivers' in parsed:
                    return parsed
            except json.JSONDecodeError:
                pass

    # Fallback: Try to find raw JSON object
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
                        potential_json = response_text[i:j+1]
                        if len(potential_json) > 200:
                            try:
                                parsed = json.loads(potential_json)
                                if isinstance(parsed, dict) and 'drivers' in parsed:
                                    if isinstance(parsed['drivers'], dict):
                                        return parsed
                            except json.JSONDecodeError:
                                pass
                        break

    return None

# Load the full_result file
full_result_path = Path('outputs/extract_drivers_v2/20251012_155509_full_result_d_acc_pathway.json')

print(f"[OK] Loading: {full_result_path.name}")
data = json.load(open(full_result_path, encoding='utf-8'))

print(f"[OK] Response length: {len(data['response'])} chars")

# Extract drivers JSON
print("[OK] Extracting drivers JSON...")

# First try: Look for the LAST occurrence of ```json
response = data['response']
last_json_block = None
for match in re.finditer(r'```json\s*([\s\S]*?)\s*```', response):
    last_json_block = match.group(1)

if last_json_block:
    print("[OK] Found JSON code block at end of response")

    # Fix common quote issues (smart quotes -> regular quotes)
    last_json_block = last_json_block.replace('"', '"').replace('"', '"')
    last_json_block = last_json_block.replace(''', "'").replace(''', "'")
    # Also fix any other unicode quote characters
    last_json_block = last_json_block.replace('�', '"')  # Common corruption
    last_json_block = last_json_block.replace('�', '"')  # Another variant

    print(f"[OK] Applied quote fixes to JSON block")

    try:
        drivers_json = json.loads(last_json_block)
        if not isinstance(drivers_json, dict) or 'drivers' not in drivers_json:
            print("[WARNING] JSON found but missing 'drivers' key, trying standard extraction...")
            drivers_json = extract_json_from_response(response)
    except json.JSONDecodeError as e:
        print(f"[WARNING] JSON parse error after quote fix: {e}")
        print("[OK] Trying standard extraction...")
        drivers_json = extract_json_from_response(response)
else:
    print("[OK] No code block found, using standard extraction...")
    drivers_json = extract_json_from_response(response)

if drivers_json:
    print("[OK] Successfully extracted drivers!")
    print(f"[OK] Document title: {drivers_json.get('document_title', 'N/A')}")

    total_drivers = sum(len(drivers_json['drivers'].get(cat, [])) for cat in drivers_json['drivers'].keys())
    print(f"[OK] Total drivers: {total_drivers}")
    print(f"[OK] Categories: {list(drivers_json['drivers'].keys())}")

    # Save the drivers JSON with same timestamp as full_result
    timestamp = '20251012_155509'  # Match the full_result timestamp
    drivers_path = Path('outputs/extract_drivers_v2') / f"{timestamp}_drivers_d_acc_pathway.json"

    with open(drivers_path, 'w', encoding='utf-8') as f:
        json.dump(drivers_json, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Saved drivers JSON to: {drivers_path.name}")
    print("[OK] d_acc extraction complete!")
else:
    print("[ERROR] Could not extract drivers JSON from response")
    print("[INFO] Response preview:")
    print(data['response'][:1000])
