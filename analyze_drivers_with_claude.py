# File created by Claude Code on 2025-10-12
# Purpose: Analyze each grouped driver file using Claude 4.5 Sonnet
# User wants structured JSON analysis of agreement/divergence patterns at each magnitude level
# Created by assistant decision to fulfill user's analysis request

import json
import os
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def analyze_via_openrouter(driver_data, driver_name, api_key):
    """Use OpenRouter API to call Claude"""
    import requests

    prompt = f"""You are analyzing AI trajectory driver data across multiple documents.

The driver is: "{driver_name}"

Here is the complete driver data organized by magnitude levels:

HIGH MAGNITUDE INSTANCES:
{json.dumps(driver_data.get('high', []), indent=2)}

MEDIUM MAGNITUDE INSTANCES:
{json.dumps(driver_data.get('medium', []), indent=2)}

LOW MAGNITUDE INSTANCES:
{json.dumps(driver_data.get('low', []), indent=2)}

DOCUMENTS WITHOUT THIS DRIVER:
{json.dumps(driver_data.get('none', []), indent=2)}

TASK:
Analyze this driver data and provide a structured analysis for each magnitude level.

For the "none" level:
- Explain in bullet points WHY these documents don't include this driver (if clear from their summaries)
- Look for patterns (e.g., all focus on X instead, none discuss Y, etc.)

For each magnitude level (low/medium/high) that has entries:
- Create TWO lists:
  1. AGREEMENTS: How the documents at this level agree or converge on understanding this driver
  2. DIVERGENCES: How the documents at this level differ or diverge in their treatment of this driver

Be specific and reference document titles when relevant.

OUTPUT FORMAT:
Return ONLY a valid JSON object with this exact structure (no markdown, no extra text):

{{
  "none": {{
    "explanation": ["bullet point 1", "bullet point 2", ...]
  }},
  "low": {{
    "agreements": ["bullet point 1", "bullet point 2", ...],
    "divergences": ["bullet point 1", "bullet point 2", ...]
  }},
  "medium": {{
    "agreements": ["bullet point 1", "bullet point 2", ...],
    "divergences": ["bullet point 1", "bullet point 2", ...]
  }},
  "high": {{
    "agreements": ["bullet point 1", "bullet point 2", ...],
    "divergences": ["bullet point 1", "bullet point 2", ...]
  }}
}}

If a magnitude level has no entries, you can use empty arrays [] or provide brief explanatory notes.
Be thorough but concise. Focus on meaningful patterns, not just restating individual entries."""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "anthropic/claude-sonnet-4.5",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 8000
        }
    )

    if response.status_code != 200:
        print(f"    [ERROR] OpenRouter API error: {response.status_code}")
        print(f"    [ERROR] Response: {response.text}")
        return None

    result = response.json()
    response_text = result['choices'][0]['message']['content']

    # Parse the JSON response
    try:
        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        analysis = json.loads(response_text)
        return analysis
    except json.JSONDecodeError as e:
        print(f"    [ERROR] Failed to parse JSON response: {e}")
        print(f"    [ERROR] Response was: {response_text[:500]}...")
        return {
            "error": "Failed to parse response",
            "raw_response": response_text
        }

def analyze_driver_with_claude(driver_data, driver_name):
    """Send driver data to Claude for analysis and return structured JSON"""

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("    [ERROR] ANTHROPIC_API_KEY not found in environment!")
        return None

    # Check if using OpenRouter
    if api_key.startswith("sk-or-"):
        return analyze_via_openrouter(driver_data, driver_name, api_key)

    client = Anthropic(api_key=api_key)

    # Prepare the analysis prompt
    prompt = f"""You are analyzing AI trajectory driver data across multiple documents.

The driver is: "{driver_name}"

Here is the complete driver data organized by magnitude levels:

HIGH MAGNITUDE INSTANCES:
{json.dumps(driver_data.get('high', []), indent=2)}

MEDIUM MAGNITUDE INSTANCES:
{json.dumps(driver_data.get('medium', []), indent=2)}

LOW MAGNITUDE INSTANCES:
{json.dumps(driver_data.get('low', []), indent=2)}

DOCUMENTS WITHOUT THIS DRIVER:
{json.dumps(driver_data.get('none', []), indent=2)}

TASK:
Analyze this driver data and provide a structured analysis for each magnitude level.

For the "none" level:
- Explain in bullet points WHY these documents don't include this driver (if clear from their summaries)
- Look for patterns (e.g., all focus on X instead, none discuss Y, etc.)

For each magnitude level (low/medium/high) that has entries:
- Create TWO lists:
  1. AGREEMENTS: How the documents at this level agree or converge on understanding this driver
  2. DIVERGENCES: How the documents at this level differ or diverge in their treatment of this driver

Be specific and reference document titles when relevant.

OUTPUT FORMAT:
Return ONLY a valid JSON object with this exact structure (no markdown, no extra text):

{{
  "none": {{
    "explanation": ["bullet point 1", "bullet point 2", ...]
  }},
  "low": {{
    "agreements": ["bullet point 1", "bullet point 2", ...],
    "divergences": ["bullet point 1", "bullet point 2", ...]
  }},
  "medium": {{
    "agreements": ["bullet point 1", "bullet point 2", ...],
    "divergences": ["bullet point 1", "bullet point 2", ...]
  }},
  "high": {{
    "agreements": ["bullet point 1", "bullet point 2", ...],
    "divergences": ["bullet point 1", "bullet point 2", ...]
  }}
}}

If a magnitude level has no entries, you can use empty arrays [] or provide brief explanatory notes.
Be thorough but concise. Focus on meaningful patterns, not just restating individual entries."""

    print(f"    [OK] Sending to Claude Sonnet 4.5...")

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=8000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text

    # Parse the JSON response
    try:
        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        analysis = json.loads(response_text)
        return analysis
    except json.JSONDecodeError as e:
        print(f"    [ERROR] Failed to parse JSON response: {e}")
        print(f"    [ERROR] Response was: {response_text[:500]}...")
        return {
            "error": "Failed to parse response",
            "raw_response": response_text
        }

def main():
    print("[OK] Starting driver analysis with Claude Sonnet 4.5...")

    # Paths
    grouped_drivers_path = Path('outputs/grouped_drivers')
    output_path = Path('outputs/driver_analysis')
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all grouped driver JSON files (latest timestamp)
    driver_files = sorted(grouped_drivers_path.glob('*_grouped_*.json'), reverse=True)

    # Filter to only get files from the latest run
    if driver_files:
        latest_timestamp = driver_files[0].name.split('_')[0]
        driver_files = [f for f in driver_files if f.name.startswith(latest_timestamp)]

    print(f"[OK] Found {len(driver_files)} driver files to analyze")

    if not driver_files:
        print("[ERROR] No driver files found!")
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    for i, driver_file in enumerate(driver_files, 1):
        print(f"\n[{i}/{len(driver_files)}] Analyzing: {driver_file.name}")

        try:
            # Load driver data
            with open(driver_file, 'r', encoding='utf-8') as f:
                driver_data = json.load(f)

            driver_name = driver_data.get('driver_name', 'Unknown')
            print(f"    [OK] Driver: {driver_name}")

            # Analyze with Claude
            analysis = analyze_driver_with_claude(driver_data, driver_name)

            # Prepare output
            output = {
                "driver_name": driver_name,
                "analysis": analysis,
                "statistics": driver_data.get('statistics', {}),
                "metadata": {
                    "analyzed_at": datetime.now().isoformat(),
                    "model": "claude-sonnet-4.5-20250929",
                    "source_file": driver_file.name
                }
            }

            # Save analysis
            output_filename = f"{timestamp}_analysis_{driver_file.name.replace('grouped_', '')}"
            output_file = output_path / output_filename

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)

            print(f"    [OK] Analysis saved to: {output_filename}")

        except Exception as e:
            print(f"    [ERROR] Failed to analyze {driver_file.name}: {e}")
            continue

    # Create summary
    summary_file = output_path / f"{timestamp}_analysis_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"Driver Analysis Summary\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Model: claude-sonnet-4.5-20250929\n")
        f.write(f"=" * 80 + "\n\n")
        f.write(f"Total drivers analyzed: {len(driver_files)}\n")
        f.write(f"Output location: {output_path}\n")
        f.write(f"Timestamp: {timestamp}\n")

    print(f"\n[OK] Analysis complete!")
    print(f"[OK] {len(driver_files)} drivers analyzed")
    print(f"[OK] Results saved to: {output_path}")
    print(f"[OK] Summary: {summary_file}")

if __name__ == "__main__":
    main()
