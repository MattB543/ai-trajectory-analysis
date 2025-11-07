"""
Generate Driver Summaries using Claude 4.5 Sonnet

Created by: Claude Code Agent
Purpose: Analyze all driver data (excluding None) to extract top 3 agreement and disagreement patterns
Created at request of user for driver summary modals on home page
"""

import json
import os
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()


def extract_driver_instances(input_dir, driver_name):
    """
    Extract all instances of a driver across documents (excluding None magnitude)

    Args:
        input_dir: Directory containing driver JSON files
        driver_name: Name of the driver to extract

    Returns:
        List of driver instances with all their data
    """
    instances = []
    input_path = Path(input_dir)
    json_files = list(input_path.glob("*_drivers_*.json"))

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            document_title = data.get('document_title', 'Unknown Document')

            # Search for this driver
            for category, drivers in data.get('drivers', {}).items():
                if not isinstance(drivers, list):
                    continue

                for driver in drivers:
                    if driver.get('driver_name', '').strip() == driver_name:
                        magnitude = driver.get('magnitude', 'None')
                        if magnitude is None or magnitude == '':
                            magnitude = 'None'

                        # Handle compound magnitudes
                        if '-' in str(magnitude):
                            magnitude = str(magnitude).split('-')[-1]

                        # Only include non-None magnitudes
                        if magnitude in ["Low", "Medium", "High"]:
                            instances.append({
                                "magnitude": magnitude,
                                "description": driver.get('description', ''),
                                "direction": driver.get('direction', ''),
                                "certainty": driver.get('certainty', ''),
                                "evidence": driver.get('evidence', ''),
                                "category": category
                            })
                        break
        except Exception as e:
            print(f"    [ERROR] Failed to process {json_file.name}: {e}")

    return instances


def analyze_via_openrouter(instances, driver_name, api_key):
    """Use OpenRouter API to call Claude"""
    import requests

    prompt = f"""You are analyzing driver data from multiple AI trajectory documents.

Driver name: "{driver_name}"

Here is ALL the data about how different documents discuss this driver:

{json.dumps(instances, indent=2)}

TASK:
Analyze this data to identify the most important, interesting, and insightful patterns of agreement and disagreement across these documents.

DO NOT mention specific document names or titles.
Focus on THEMATIC patterns and HIGH-LEVEL insights.

Identify:
1. TOP 3 WAYS DOCUMENTS AGREE: What are the 3 most significant points of convergence or consensus across documents about this driver?
2. TOP 3 WAYS DOCUMENTS DISAGREE: What are the 3 most significant points of divergence or tension across documents about this driver?

Each point should be:
- Concise (1-2 sentences max)
- Insightful (reveal something important about the driver)
- Thematic (describe patterns, not individual instances)
- Impactful (focus on what matters most)

OUTPUT FORMAT:
Return ONLY a valid JSON object with this structure (no markdown, no extra text):

{{
  "agreements": [
    "First major point of agreement...",
    "Second major point of agreement...",
    "Third major point of agreement..."
  ],
  "disagreements": [
    "First major point of disagreement...",
    "Second major point of disagreement...",
    "Third major point of disagreement..."
  ]
}}
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "anthropic/claude-sonnet-4.5",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4000
        }
    )

    if response.status_code != 200:
        print(f"    [ERROR] OpenRouter API error: {response.status_code}")
        print(f"    [ERROR] Response: {response.text}")
        return None

    result = response.json()
    response_text = result['choices'][0]['message']['content']

    # Parse JSON response
    try:
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        analysis = json.loads(response_text)
        return analysis
    except json.JSONDecodeError as e:
        print(f"    [ERROR] Failed to parse JSON response: {e}")
        print(f"    [ERROR] Response was: {response_text[:500]}...")
        return None


def analyze_driver_summary(instances, driver_name):
    """Send driver data to Claude for summary analysis"""

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("    [ERROR] ANTHROPIC_API_KEY not found in environment!")
        return None

    # Check if using OpenRouter
    if api_key.startswith("sk-or-"):
        return analyze_via_openrouter(instances, driver_name, api_key)

    # Use direct Anthropic API
    client = Anthropic(api_key=api_key)

    prompt = f"""You are analyzing driver data from multiple AI trajectory documents.

Driver name: "{driver_name}"

Here is ALL the data about how different documents discuss this driver:

{json.dumps(instances, indent=2)}

TASK:
Analyze this data to identify the most important, interesting, and insightful patterns of agreement and disagreement across these documents.

DO NOT mention specific document names or titles.
Focus on THEMATIC patterns and HIGH-LEVEL insights.

Identify:
1. TOP 3 WAYS DOCUMENTS AGREE: What are the 3 most significant points of convergence or consensus across documents about this driver?
2. TOP 3 WAYS DOCUMENTS DISAGREE: What are the 3 most significant points of divergence or tension across documents about this driver?

Each point should be:
- Concise (1-2 sentences max)
- Insightful (reveal something important about the driver)
- Thematic (describe patterns, not individual instances)
- Impactful (focus on what matters most)

OUTPUT FORMAT:
Return ONLY a valid JSON object with this structure (no markdown, no extra text):

{{
  "agreements": [
    "First major point of agreement...",
    "Second major point of agreement...",
    "Third major point of agreement..."
  ],
  "disagreements": [
    "First major point of disagreement...",
    "Second major point of disagreement...",
    "Third major point of disagreement..."
  ]
}}
"""

    print(f"    [OK] Sending to Claude Sonnet 4.5...")

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text

    # Parse JSON response
    try:
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        analysis = json.loads(response_text)
        return analysis
    except json.JSONDecodeError as e:
        print(f"    [ERROR] Failed to parse JSON response: {e}")
        print(f"    [ERROR] Response was: {response_text[:500]}...")
        return None


def get_drivers_to_analyze(input_dir):
    """Get list of drivers with >= 12 occurrences"""
    driver_counts = defaultdict(int)
    input_path = Path(input_dir)
    json_files = list(input_path.glob("*_drivers_*.json"))

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for category, drivers in data.get('drivers', {}).items():
                if not isinstance(drivers, list):
                    continue

                for driver in drivers:
                    driver_name = driver.get('driver_name', '').strip()
                    if driver_name:
                        magnitude = driver.get('magnitude', 'None')
                        if magnitude and magnitude != 'None':
                            driver_counts[driver_name] += 1
        except Exception:
            pass

    return [name for name, count in driver_counts.items() if count >= 12]


def main():
    print("[OK] Starting driver summary generation with Claude Sonnet 4.5...")

    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    input_dir = project_root / "outputs" / "extract_drivers_v2"
    output_dir = project_root / "outputs" / "driver_summaries"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get drivers to analyze
    print("[OK] Finding drivers to analyze...")
    drivers = get_drivers_to_analyze(input_dir)
    print(f"[OK] Found {len(drivers)} drivers with >= 12 occurrences")

    if not drivers:
        print("[ERROR] No drivers found!")
        return 1

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    for i, driver_name in enumerate(sorted(drivers), 1):
        print(f"\n[{i}/{len(drivers)}] Analyzing: {driver_name}")

        try:
            # Extract instances
            instances = extract_driver_instances(input_dir, driver_name)
            print(f"    [OK] Found {len(instances)} instances (excluding None)")

            if len(instances) == 0:
                print(f"    [WARNING] No non-None instances, skipping")
                continue

            # Analyze with Claude
            summary = analyze_driver_summary(instances, driver_name)

            if not summary:
                print(f"    [ERROR] Analysis failed")
                continue

            # Prepare output
            output = {
                "driver_name": driver_name,
                "summary": summary,
                "statistics": {
                    "total_instances": len(instances),
                    "magnitude_breakdown": {
                        "Low": sum(1 for x in instances if x["magnitude"] == "Low"),
                        "Medium": sum(1 for x in instances if x["magnitude"] == "Medium"),
                        "High": sum(1 for x in instances if x["magnitude"] == "High")
                    }
                },
                "metadata": {
                    "analyzed_at": datetime.now().isoformat(),
                    "model": "claude-sonnet-4.5-20250929"
                }
            }

            # Save summary
            sanitized_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in driver_name).strip().replace(' ', '_').lower()
            output_filename = f"{timestamp}_summary_{sanitized_name}.json"
            output_file = output_dir / output_filename

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)

            print(f"    [OK] Summary saved: {output_filename}")

        except Exception as e:
            print(f"    [ERROR] Failed to analyze: {e}")
            continue

    print(f"\n[OK] ===================================")
    print(f"[OK] Summary generation complete!")
    print(f"[OK] Output directory: {output_dir}")
    print(f"[OK] ===================================")

    return 0


if __name__ == "__main__":
    exit(main())
