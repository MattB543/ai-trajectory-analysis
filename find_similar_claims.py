"""
Find Similar Claim Titles Using Gemini Embeddings

This script:
1. Loads all claim JSON files from outputs/claims/
2. Extracts claim titles (claim_text field)
3. Generates embeddings for each title using Google Gemini API
4. Saves embeddings to a file for future use
5. Finds pairs of claims with similarity > 0.9
6. Outputs a detailed summary of similar claims

Created: 2025-10-13
"""

import google.generativeai as genai
import numpy as np
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Tuple
from datetime import datetime

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Configuration
CLAIMS_DIR = Path("outputs/claims")
EMBEDDINGS_OUTPUT_FILE = "outputs/claim_embeddings.json"
SIMILARITY_THRESHOLD = 0.9
BATCH_SIZE = 100  # Process embeddings in batches to avoid API limits


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Returns:
        Similarity score between -1 and 1 (1 = identical)
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def load_all_claims() -> List[Dict]:
    """
    Load all claim files and extract claim information.

    Returns:
        List of dictionaries with claim metadata and text
    """
    all_claims = []
    claim_files = list(CLAIMS_DIR.glob("*_claims.json"))

    print(f"[OK] Found {len(claim_files)} claim files")

    for claim_file in claim_files:
        try:
            with open(claim_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract document name from filename
            doc_name = claim_file.stem.replace('_claims', '')

            # Process each claim in the file
            for claim in data.get('claims', []):
                all_claims.append({
                    'document': doc_name,
                    'claim_id': claim.get('claim_id'),
                    'claim_text': claim.get('claim_text'),
                    'claim_type': claim.get('claim_type'),
                    'confidence': claim.get('confidence'),
                    'source_file': claim_file.name
                })

        except Exception as e:
            print(f"[ERROR] Failed to load {claim_file.name}: {e}")
            continue

    print(f"[OK] Loaded {len(all_claims)} total claims")
    return all_claims


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts efficiently.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=texts,
            task_type="semantic_similarity"
        )
        return result['embedding']
    except Exception as e:
        print(f"[ERROR] Failed to generate embeddings: {e}")
        return []


def generate_all_embeddings(claims: List[Dict]) -> List[Dict]:
    """
    Generate embeddings for all claims, processing in batches.

    Args:
        claims: List of claim dictionaries

    Returns:
        List of claims with embeddings added
    """
    print(f"\n[OK] Generating embeddings for {len(claims)} claims...")

    # Extract all claim texts
    claim_texts = [claim['claim_text'] for claim in claims]

    # Process in batches
    all_embeddings = []
    for i in range(0, len(claim_texts), BATCH_SIZE):
        batch = claim_texts[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (len(claim_texts) + BATCH_SIZE - 1) // BATCH_SIZE

        print(f"[OK] Processing batch {batch_num}/{total_batches} ({len(batch)} claims)...")

        embeddings = generate_embeddings_batch(batch)
        all_embeddings.extend(embeddings)

    # Add embeddings to claims
    for claim, embedding in zip(claims, all_embeddings):
        claim['embedding'] = embedding

    print(f"[OK] Generated {len(all_embeddings)} embeddings")
    return claims


def save_embeddings(claims: List[Dict], output_file: str):
    """
    Save claims with embeddings to a JSON file.

    Args:
        claims: List of claim dictionaries with embeddings
        output_file: Path to output file
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Prepare data for saving
    save_data = {
        'generated_at': datetime.now().isoformat(),
        'total_claims': len(claims),
        'model': 'models/embedding-001',
        'claims': claims
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2)

    print(f"[OK] Saved embeddings to {output_file}")


def load_embeddings(input_file: str) -> List[Dict]:
    """
    Load previously saved embeddings.

    Args:
        input_file: Path to embeddings file

    Returns:
        List of claims with embeddings
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"[OK] Loaded {data['total_claims']} claims with embeddings")
    print(f"[OK] Generated at: {data['generated_at']}")
    return data['claims']


def find_similar_claims(
    claims: List[Dict],
    threshold: float = 0.9
) -> List[Tuple[Dict, Dict, float]]:
    """
    Find pairs of claims with similarity above threshold.

    Args:
        claims: List of claim dictionaries with embeddings
        threshold: Minimum similarity score (0-1)

    Returns:
        List of (claim1, claim2, similarity) tuples
    """
    print(f"\n[OK] Finding similar claims (threshold: {threshold})...")

    similar_pairs = []
    total_comparisons = len(claims) * (len(claims) - 1) // 2
    comparisons_done = 0

    # Compare each pair of claims
    for i in range(len(claims)):
        for j in range(i + 1, len(claims)):
            similarity = cosine_similarity(
                claims[i]['embedding'],
                claims[j]['embedding']
            )

            if similarity >= threshold:
                similar_pairs.append((claims[i], claims[j], similarity))

            comparisons_done += 1

            # Progress indicator every 10,000 comparisons
            if comparisons_done % 10000 == 0:
                progress = (comparisons_done / total_comparisons) * 100
                print(f"[OK] Progress: {progress:.1f}% ({comparisons_done}/{total_comparisons} comparisons)")

    # Sort by similarity (highest first)
    similar_pairs.sort(key=lambda x: x[2], reverse=True)

    print(f"[OK] Found {len(similar_pairs)} similar pairs above threshold {threshold}")
    return similar_pairs


def safe_print(text: str):
    """
    Print text with encoding error handling for Windows console.

    Args:
        text: Text to print
    """
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace problematic characters with ASCII equivalents
        print(text.encode('ascii', errors='replace').decode('ascii'))


def print_summary(similar_pairs: List[Tuple[Dict, Dict, float]]):
    """
    Print a detailed summary of similar claims.

    Args:
        similar_pairs: List of (claim1, claim2, similarity) tuples
    """
    print("\n" + "="*80)
    print("SIMILAR CLAIMS SUMMARY")
    print("="*80)

    if not similar_pairs:
        print("\n[OK] No similar claims found above the threshold.")
        return

    print(f"\nFound {len(similar_pairs)} pairs of similar claims:\n")

    for idx, (claim1, claim2, similarity) in enumerate(similar_pairs, 1):
        print(f"\n{'-'*80}")
        print(f"Pair #{idx} | Similarity: {similarity:.4f}")
        print(f"{'-'*80}")

        safe_print(f"\nClaim 1:")
        safe_print(f"   Document: {claim1['document']}")
        safe_print(f"   Claim ID: {claim1['claim_id']}")
        safe_print(f"   Type: {claim1['claim_type']}")
        safe_print(f"   Confidence: {claim1['confidence']}")
        safe_print(f"   Text: {claim1['claim_text']}")

        safe_print(f"\nClaim 2:")
        safe_print(f"   Document: {claim2['document']}")
        safe_print(f"   Claim ID: {claim2['claim_id']}")
        safe_print(f"   Type: {claim2['claim_type']}")
        safe_print(f"   Confidence: {claim2['confidence']}")
        safe_print(f"   Text: {claim2['claim_text']}")

    print("\n" + "="*80)


def save_summary_report(similar_pairs: List[Tuple[Dict, Dict, float]], output_file: str):
    """
    Save a detailed summary report to a text file.

    Args:
        similar_pairs: List of (claim1, claim2, similarity) tuples
        output_file: Path to output file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("SIMILAR CLAIMS ANALYSIS REPORT\n")
        f.write("="*80 + "\n")
        f.write(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Similarity Threshold: {SIMILARITY_THRESHOLD}\n")
        f.write(f"Total Similar Pairs Found: {len(similar_pairs)}\n")

        if not similar_pairs:
            f.write("\nNo similar claims found above the threshold.\n")
            return

        f.write("\n\n" + "="*80 + "\n")
        f.write("DETAILED RESULTS\n")
        f.write("="*80 + "\n")

        for idx, (claim1, claim2, similarity) in enumerate(similar_pairs, 1):
            f.write(f"\n\n{'─'*80}\n")
            f.write(f"Pair #{idx} | Similarity: {similarity:.4f}\n")
            f.write(f"{'─'*80}\n")

            f.write(f"\nClaim 1:\n")
            f.write(f"  Document: {claim1['document']}\n")
            f.write(f"  Claim ID: {claim1['claim_id']}\n")
            f.write(f"  Type: {claim1['claim_type']}\n")
            f.write(f"  Confidence: {claim1['confidence']}\n")
            f.write(f"  Text: {claim1['claim_text']}\n")

            f.write(f"\nClaim 2:\n")
            f.write(f"  Document: {claim2['document']}\n")
            f.write(f"  Claim ID: {claim2['claim_id']}\n")
            f.write(f"  Type: {claim2['claim_type']}\n")
            f.write(f"  Confidence: {claim2['confidence']}\n")
            f.write(f"  Text: {claim2['claim_text']}\n")

    print(f"\n[OK] Saved detailed report to {output_file}")


def main():
    """Main execution function."""

    print("="*80)
    print("FINDING SIMILAR CLAIM TITLES USING GEMINI EMBEDDINGS")
    print("="*80)

    # Check if embeddings already exist
    if os.path.exists(EMBEDDINGS_OUTPUT_FILE):
        print(f"\n[OK] Found existing embeddings file: {EMBEDDINGS_OUTPUT_FILE}")
        print("[OK] Loading embeddings from file...")
        claims = load_embeddings(EMBEDDINGS_OUTPUT_FILE)
    else:
        print(f"\n[OK] No existing embeddings found. Generating new embeddings...")

        # Load all claims
        claims = load_all_claims()

        if not claims:
            print("[ERROR] No claims found. Exiting.")
            return

        # Generate embeddings
        claims = generate_all_embeddings(claims)

        # Save embeddings for future use
        save_embeddings(claims, EMBEDDINGS_OUTPUT_FILE)

    # Find similar claims
    similar_pairs = find_similar_claims(claims, threshold=SIMILARITY_THRESHOLD)

    # Print summary to console
    print_summary(similar_pairs)

    # Save detailed report
    report_file = "outputs/similar_claims_report.txt"
    save_summary_report(similar_pairs, report_file)

    # Also save as JSON for programmatic access
    json_report_file = "outputs/similar_claims_pairs.json"
    json_data = {
        'generated_at': datetime.now().isoformat(),
        'threshold': SIMILARITY_THRESHOLD,
        'total_pairs': len(similar_pairs),
        'pairs': [
            {
                'similarity': float(similarity),
                'claim1': {k: v for k, v in claim1.items() if k != 'embedding'},
                'claim2': {k: v for k, v in claim2.items() if k != 'embedding'}
            }
            for claim1, claim2, similarity in similar_pairs
        ]
    }

    with open(json_report_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)

    print(f"[OK] Saved JSON report to {json_report_file}")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
