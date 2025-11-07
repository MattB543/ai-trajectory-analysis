"""
Cluster Similar Claims for Deduplication

This script:
1. Loads claim embeddings from previous analysis
2. Filters out exact duplicates (similarity = 1.0)
3. Finds clusters of similar claims (0.9 < similarity < 1.0)
4. Identifies groups of claims that should potentially be rephrased/merged
5. Outputs detailed cluster analysis for review

Created: 2025-10-13
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict
from datetime import datetime

# Configuration
EMBEDDINGS_FILE = "outputs/claim_embeddings.json"
SIMILARITY_THRESHOLD = 0.9
EXCLUDE_PERFECT_MATCHES = True
OUTPUT_FILE = "outputs/claim_clusters.json"
REPORT_FILE = "outputs/claim_clusters_report.txt"


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def load_embeddings(input_file: str) -> List[Dict]:
    """Load previously saved embeddings."""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"[OK] Loaded {data['total_claims']} claims with embeddings")
    return data['claims']


def is_exact_duplicate(claim1: Dict, claim2: Dict) -> bool:
    """Check if two claims are exact duplicates (same text)."""
    return claim1['claim_text'].strip() == claim2['claim_text'].strip()


def build_similarity_graph(
    claims: List[Dict],
    threshold: float,
    exclude_perfect: bool = True
) -> Dict[int, Set[int]]:
    """
    Build a graph where nodes are claims and edges connect similar claims.

    Returns:
        Dictionary mapping claim index to set of similar claim indices
    """
    print(f"\n[OK] Building similarity graph (threshold: {threshold})...")

    graph = defaultdict(set)
    total_comparisons = len(claims) * (len(claims) - 1) // 2
    comparisons_done = 0
    edges_added = 0
    perfect_matches_skipped = 0

    for i in range(len(claims)):
        for j in range(i + 1, len(claims)):
            similarity = cosine_similarity(
                claims[i]['embedding'],
                claims[j]['embedding']
            )

            comparisons_done += 1

            # Skip exact duplicates if requested
            if exclude_perfect and similarity >= 0.9999:
                if is_exact_duplicate(claims[i], claims[j]):
                    perfect_matches_skipped += 1
                    continue

            if similarity >= threshold:
                graph[i].add(j)
                graph[j].add(i)
                edges_added += 1

            # Progress indicator
            if comparisons_done % 100000 == 0:
                progress = (comparisons_done / total_comparisons) * 100
                print(f"[OK] Progress: {progress:.1f}% ({comparisons_done}/{total_comparisons})")

    print(f"[OK] Graph built: {edges_added} edges, {perfect_matches_skipped} perfect matches skipped")
    return graph


def find_connected_components(graph: Dict[int, Set[int]]) -> List[Set[int]]:
    """
    Find connected components in the similarity graph.
    Each component is a cluster of similar claims.
    """
    print(f"\n[OK] Finding connected components (clusters)...")

    visited = set()
    components = []

    def dfs(node: int, component: Set[int]):
        """Depth-first search to find connected nodes."""
        visited.add(node)
        component.add(node)

        for neighbor in graph.get(node, set()):
            if neighbor not in visited:
                dfs(neighbor, component)

    # Find all connected components
    for node in graph.keys():
        if node not in visited:
            component = set()
            dfs(node, component)
            if len(component) > 1:  # Only include clusters with 2+ claims
                components.append(component)

    # Sort by cluster size (largest first)
    components.sort(key=len, reverse=True)

    print(f"[OK] Found {len(components)} clusters")
    return components


def analyze_cluster(claims: List[Dict], cluster_indices: Set[int]) -> Dict:
    """
    Analyze a cluster of similar claims.

    Returns:
        Dictionary with cluster analysis
    """
    cluster_claims = [claims[i] for i in cluster_indices]

    # Get unique documents in cluster
    documents = list(set(c['document'] for c in cluster_claims))

    # Get claim types distribution
    claim_types = {}
    for claim in cluster_claims:
        claim_type = claim['claim_type']
        claim_types[claim_type] = claim_types.get(claim_type, 0) + 1

    # Calculate pairwise similarities within cluster
    indices = list(cluster_indices)
    similarities = []
    for i in range(len(indices)):
        for j in range(i + 1, len(indices)):
            sim = cosine_similarity(
                claims[indices[i]]['embedding'],
                claims[indices[j]]['embedding']
            )
            similarities.append(sim)

    return {
        'size': len(cluster_claims),
        'documents': documents,
        'claim_types': claim_types,
        'min_similarity': min(similarities) if similarities else 0,
        'max_similarity': max(similarities) if similarities else 0,
        'avg_similarity': sum(similarities) / len(similarities) if similarities else 0,
        'claims': [
            {
                'document': c['document'],
                'claim_id': c['claim_id'],
                'claim_type': c['claim_type'],
                'confidence': c['confidence'],
                'claim_text': c['claim_text']
            }
            for c in cluster_claims
        ]
    }


def save_cluster_report(clusters_data: List[Dict], output_file: str):
    """Save detailed text report of clusters."""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*100 + "\n")
        f.write("CLAIM CLUSTERS ANALYSIS - POTENTIAL DUPLICATES FOR REVIEW\n")
        f.write("="*100 + "\n")
        f.write(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Clusters Found: {len(clusters_data)}\n")
        f.write(f"\nClusters contain claims that are semantically similar and may need to be:\n")
        f.write(f"  - Merged into a single canonical claim\n")
        f.write(f"  - Rephrased for consistency\n")
        f.write(f"  - Reviewed to determine if they express the same underlying idea\n")

        for cluster_idx, cluster in enumerate(clusters_data, 1):
            f.write(f"\n\n{'='*100}\n")
            f.write(f"CLUSTER #{cluster_idx}\n")
            f.write(f"{'='*100}\n")
            f.write(f"Size: {cluster['size']} claims\n")
            f.write(f"Documents: {', '.join(cluster['documents'][:5])}")
            if len(cluster['documents']) > 5:
                f.write(f" ... and {len(cluster['documents']) - 5} more")
            f.write(f"\nClaim Types: {', '.join(f'{k}({v})' for k, v in cluster['claim_types'].items())}\n")
            f.write(f"Similarity Range: {cluster['min_similarity']:.4f} - {cluster['max_similarity']:.4f} ")
            f.write(f"(avg: {cluster['avg_similarity']:.4f})\n")

            f.write(f"\n{'-'*100}\n")
            f.write("CLAIMS IN THIS CLUSTER:\n")
            f.write(f"{'-'*100}\n")

            for i, claim in enumerate(cluster['claims'], 1):
                f.write(f"\n{i}. [{claim['claim_type']}] ({claim['confidence']}) - {claim['document'][:50]}\n")
                f.write(f"   Claim ID: {claim['claim_id']}\n")

                # Wrap long text
                text = claim['claim_text']
                words = text.split()
                lines = []
                current_line = "   "

                for word in words:
                    if len(current_line) + len(word) + 1 <= 97:
                        current_line += word + " "
                    else:
                        lines.append(current_line.rstrip())
                        current_line = "   " + word + " "

                if current_line.strip():
                    lines.append(current_line.rstrip())

                f.write("\n".join(lines) + "\n")

    print(f"[OK] Saved detailed report to {output_file}")


def print_summary(clusters_data: List[Dict]):
    """Print summary to console."""

    print("\n" + "="*100)
    print("CLAIM CLUSTERS SUMMARY")
    print("="*100)

    total_claims_in_clusters = sum(c['size'] for c in clusters_data)

    print(f"\nTotal Clusters: {len(clusters_data)}")
    print(f"Total Claims in Clusters: {total_claims_in_clusters}")
    print(f"Average Cluster Size: {total_claims_in_clusters / len(clusters_data):.1f}")

    # Show size distribution
    size_dist = {}
    for cluster in clusters_data:
        size = cluster['size']
        size_dist[size] = size_dist.get(size, 0) + 1

    print(f"\nCluster Size Distribution:")
    for size in sorted(size_dist.keys(), reverse=True):
        print(f"  Size {size}: {size_dist[size]} clusters")

    # Show top 10 largest clusters
    print(f"\n{'-'*100}")
    print("TOP 10 LARGEST CLUSTERS:")
    print(f"{'-'*100}")

    for i, cluster in enumerate(clusters_data[:10], 1):
        print(f"\nCluster #{i}: {cluster['size']} claims")
        print(f"  Documents: {len(cluster['documents'])} unique documents")
        print(f"  Similarity: {cluster['avg_similarity']:.4f} (avg)")
        print(f"  Types: {', '.join(f'{k}({v})' for k, v in sorted(cluster['claim_types'].items()))}")

        # Show first claim as example
        if cluster['claims']:
            first_claim = cluster['claims'][0]
            text = first_claim['claim_text']
            if len(text) > 120:
                text = text[:117] + "..."
            print(f"  Example: \"{text}\"")

    print("\n" + "="*100)


def main():
    """Main execution function."""

    print("="*100)
    print("CLUSTERING SIMILAR CLAIMS FOR DEDUPLICATION REVIEW")
    print("="*100)

    # Load embeddings
    claims = load_embeddings(EMBEDDINGS_FILE)

    # Build similarity graph
    graph = build_similarity_graph(
        claims,
        threshold=SIMILARITY_THRESHOLD,
        exclude_perfect=EXCLUDE_PERFECT_MATCHES
    )

    # Find clusters
    clusters = find_connected_components(graph)

    # Analyze each cluster
    print(f"\n[OK] Analyzing {len(clusters)} clusters...")
    clusters_data = []

    for cluster_indices in clusters:
        cluster_analysis = analyze_cluster(claims, cluster_indices)
        clusters_data.append(cluster_analysis)

    # Print summary
    print_summary(clusters_data)

    # Save JSON output
    output_data = {
        'generated_at': datetime.now().isoformat(),
        'similarity_threshold': SIMILARITY_THRESHOLD,
        'exclude_perfect_matches': EXCLUDE_PERFECT_MATCHES,
        'total_clusters': len(clusters_data),
        'total_claims_in_clusters': sum(c['size'] for c in clusters_data),
        'clusters': clusters_data
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n[OK] Saved JSON data to {OUTPUT_FILE}")

    # Save detailed report
    save_cluster_report(clusters_data, REPORT_FILE)

    print("\n" + "="*100)
    print("ANALYSIS COMPLETE")
    print("="*100)
    print(f"\nReview the clusters in {REPORT_FILE}")
    print("Each cluster contains claims that should potentially be:")
    print("  - Merged into a single canonical claim")
    print("  - Rephrased for consistency across documents")
    print("  - Reviewed to determine if they express the same idea")


if __name__ == "__main__":
    main()
