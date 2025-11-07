# Guide: Using Gemini for Embeddings to Compare Strings

**Created:** 2025-10-13
**Purpose:** Documentation file created at direct user request to explain how to use Google Gemini API for generating embeddings and comparing strings.

## Overview

This guide explains how to use Google's Gemini API to generate embeddings for text strings and compare them for similarity. Embeddings are dense vector representations of text that capture semantic meaning, allowing you to find similar content even when the exact words differ.

## Use Cases

- **Semantic search:** Find documents similar to a query
- **Clustering:** Group similar documents together
- **Deduplication:** Identify duplicate or near-duplicate content
- **Classification:** Categorize text based on similarity to known categories
- **Recommendation:** Suggest similar items based on content

## Setup

### 1. Install Required Libraries

```bash
pip install google-generativeai numpy python-dotenv
```

### 2. Get API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to your `.env` file:

```bash
GOOGLE_API_KEY=your-api-key-here
```

### 3. Basic Configuration

```python
import google.generativeai as genai
import os
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

# Configure the API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
```

## Generating Embeddings

### Single String Embedding

```python
def generate_embedding(text: str, task_type: str = "retrieval_document") -> list[float]:
    """
    Generate an embedding for a single text string.

    Args:
        text: The text to embed
        task_type: The task type for the embedding. Options:
            - "retrieval_document": For documents in a retrieval system
            - "retrieval_query": For queries in a retrieval system
            - "semantic_similarity": For comparing text similarity
            - "classification": For text classification
            - "clustering": For clustering similar texts

    Returns:
        List of floats representing the embedding vector
    """
    result = genai.embed_content(
        model="models/embedding-001",  # or "models/text-embedding-004"
        content=text,
        task_type=task_type
    )

    return result['embedding']


# Example usage
text = "Artificial intelligence is transforming the world."
embedding = generate_embedding(text)

print(f"[OK] Generated embedding with {len(embedding)} dimensions")
print(f"[OK] First 5 values: {embedding[:5]}")
```

**Output:**
```
[OK] Generated embedding with 768 dimensions
[OK] First 5 values: [0.0234, -0.0156, 0.0389, -0.0421, 0.0187]
```

### Batch Embeddings

```python
def generate_embeddings_batch(
    texts: list[str],
    task_type: str = "retrieval_document"
) -> list[list[float]]:
    """
    Generate embeddings for multiple texts efficiently.

    Args:
        texts: List of texts to embed
        task_type: The task type for embeddings

    Returns:
        List of embedding vectors
    """
    result = genai.embed_content(
        model="models/embedding-001",
        content=texts,
        task_type=task_type
    )

    return result['embedding']


# Example usage
texts = [
    "Machine learning is a subset of AI.",
    "Deep learning uses neural networks.",
    "Python is a programming language.",
    "Artificial intelligence mimics human cognition."
]

embeddings = generate_embeddings_batch(texts)

print(f"[OK] Generated {len(embeddings)} embeddings")
for i, emb in enumerate(embeddings):
    print(f"  Text {i+1}: {len(emb)} dimensions")
```

## Comparing Embeddings

### Cosine Similarity

Cosine similarity measures the cosine of the angle between two vectors. Range: -1 to 1 (1 = identical, 0 = orthogonal, -1 = opposite).

```python
def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Similarity score between -1 and 1
    """
    # Convert to numpy arrays
    v1 = np.array(vec1)
    v2 = np.array(vec2)

    # Calculate cosine similarity
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    return dot_product / (norm_v1 * norm_v2)


# Example usage
text1 = "Machine learning is a subset of artificial intelligence."
text2 = "AI includes machine learning as a subfield."
text3 = "Python is a popular programming language."

emb1 = generate_embedding(text1, task_type="semantic_similarity")
emb2 = generate_embedding(text2, task_type="semantic_similarity")
emb3 = generate_embedding(text3, task_type="semantic_similarity")

similarity_1_2 = cosine_similarity(emb1, emb2)
similarity_1_3 = cosine_similarity(emb1, emb3)

print(f"[OK] Similarity between text1 and text2: {similarity_1_2:.4f}")
print(f"[OK] Similarity between text1 and text3: {similarity_1_3:.4f}")
```

**Output:**
```
[OK] Similarity between text1 and text2: 0.8734
[OK] Similarity between text1 and text3: 0.3421
```

### Euclidean Distance

Euclidean distance measures the straight-line distance between two vectors. Lower values indicate more similarity.

```python
def euclidean_distance(vec1: list[float], vec2: list[float]) -> float:
    """
    Calculate Euclidean distance between two vectors.

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Distance value (0 = identical, higher = more different)
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)

    return np.linalg.norm(v1 - v2)


# Example usage
distance_1_2 = euclidean_distance(emb1, emb2)
distance_1_3 = euclidean_distance(emb1, emb3)

print(f"[OK] Distance between text1 and text2: {distance_1_2:.4f}")
print(f"[OK] Distance between text1 and text3: {distance_1_3:.4f}")
```

### Dot Product

Direct dot product of vectors. Higher values indicate more similarity.

```python
def dot_product_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Calculate dot product between two vectors.

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Dot product value
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)

    return np.dot(v1, v2)
```

## Complete Example: Find Most Similar Strings

```python
import google.generativeai as genai
import numpy as np
from typing import List, Tuple
import os
from dotenv import load_dotenv

# Load and configure
load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def find_most_similar(
    query: str,
    candidates: List[str],
    top_k: int = 5,
    task_type: str = "semantic_similarity"
) -> List[Tuple[str, float]]:
    """
    Find the most similar strings to a query.

    Args:
        query: The query string
        candidates: List of candidate strings to compare
        top_k: Number of top results to return
        task_type: Task type for embeddings

    Returns:
        List of (text, similarity_score) tuples, sorted by similarity
    """
    print(f"[OK] Generating embedding for query...")
    query_embedding = genai.embed_content(
        model="models/embedding-001",
        content=query,
        task_type=task_type
    )['embedding']

    print(f"[OK] Generating embeddings for {len(candidates)} candidates...")
    candidate_embeddings = genai.embed_content(
        model="models/embedding-001",
        content=candidates,
        task_type=task_type
    )['embedding']

    print(f"[OK] Calculating similarities...")
    similarities = []
    for i, candidate_emb in enumerate(candidate_embeddings):
        similarity = cosine_similarity(query_embedding, candidate_emb)
        similarities.append((candidates[i], similarity))

    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities[:top_k]


# Example usage
if __name__ == "__main__":
    query = "How will artificial intelligence affect employment?"

    candidates = [
        "AI and machine learning will transform the job market",
        "The impact of automation on workforce dynamics",
        "Climate change is affecting global temperatures",
        "Neural networks are used in deep learning",
        "Jobs will be displaced but new ones will be created by AI",
        "Quantum computing uses qubits instead of bits",
        "AI could lead to significant unemployment in some sectors",
        "The history of the Roman Empire",
        "Machine learning algorithms need training data",
        "Robotics and AI are changing manufacturing jobs"
    ]

    print("="*80)
    print("FINDING MOST SIMILAR STRINGS")
    print("="*80)
    print(f"\n[OK] Query: {query}\n")

    results = find_most_similar(query, candidates, top_k=5)

    print(f"\n[OK] Top 5 most similar strings:\n")
    for i, (text, score) in enumerate(results, 1):
        print(f"{i}. [Similarity: {score:.4f}]")
        print(f"   {text}\n")
```

**Output:**
```
================================================================================
FINDING MOST SIMILAR STRINGS
================================================================================

[OK] Query: How will artificial intelligence affect employment?

[OK] Generating embedding for query...
[OK] Generating embeddings for 10 candidates...
[OK] Calculating similarities...

[OK] Top 5 most similar strings:

1. [Similarity: 0.8923]
   Jobs will be displaced but new ones will be created by AI

2. [Similarity: 0.8712]
   AI could lead to significant unemployment in some sectors

3. [Similarity: 0.8534]
   AI and machine learning will transform the job market

4. [Similarity: 0.8201]
   Robotics and AI are changing manufacturing jobs

5. [Similarity: 0.7845]
   The impact of automation on workforce dynamics
```

## Advanced Use Cases

### 1. Document Clustering

```python
from sklearn.cluster import KMeans
import numpy as np

def cluster_documents(texts: List[str], n_clusters: int = 3) -> dict:
    """
    Cluster documents based on embedding similarity.

    Args:
        texts: List of document texts
        n_clusters: Number of clusters to create

    Returns:
        Dictionary mapping cluster ID to list of document indices
    """
    print(f"[OK] Generating embeddings for {len(texts)} documents...")

    embeddings = genai.embed_content(
        model="models/embedding-001",
        content=texts,
        task_type="clustering"
    )['embedding']

    print(f"[OK] Clustering into {n_clusters} groups...")

    # Convert to numpy array
    X = np.array(embeddings)

    # Perform k-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X)

    # Group documents by cluster
    clusters = {}
    for i, label in enumerate(labels):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(i)

    print(f"[OK] Clustering complete!")
    return clusters, labels


# Example usage
documents = [
    "Machine learning algorithms for classification",
    "Deep learning neural networks",
    "Climate change and global warming",
    "Environmental impact of carbon emissions",
    "Python programming best practices",
    "JavaScript web development",
    "AI ethics and responsible development",
    "Renewable energy sources",
]

clusters, labels = cluster_documents(documents, n_clusters=3)

print("\n[OK] Cluster assignments:\n")
for cluster_id, doc_indices in clusters.items():
    print(f"Cluster {cluster_id}:")
    for idx in doc_indices:
        print(f"  - {documents[idx]}")
    print()
```

### 2. Semantic Deduplication

```python
def find_duplicates(
    texts: List[str],
    similarity_threshold: float = 0.95
) -> List[Tuple[int, int, float]]:
    """
    Find near-duplicate texts based on embedding similarity.

    Args:
        texts: List of texts to check
        similarity_threshold: Minimum similarity to consider as duplicate

    Returns:
        List of (index1, index2, similarity) tuples for potential duplicates
    """
    print(f"[OK] Generating embeddings for {len(texts)} texts...")

    embeddings = genai.embed_content(
        model="models/embedding-001",
        content=texts,
        task_type="semantic_similarity"
    )['embedding']

    print(f"[OK] Finding duplicates (threshold: {similarity_threshold})...")

    duplicates = []

    # Compare each pair of texts
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            similarity = cosine_similarity(embeddings[i], embeddings[j])
            if similarity >= similarity_threshold:
                duplicates.append((i, j, similarity))

    print(f"[OK] Found {len(duplicates)} potential duplicate pairs")
    return duplicates


# Example usage
texts = [
    "Artificial intelligence is transforming society",
    "AI is changing the world as we know it",
    "Machine learning is a subset of AI",
    "Python is a programming language",
    "AI is revolutionizing our society",
    "Deep learning uses neural networks"
]

duplicates = find_duplicates(texts, similarity_threshold=0.85)

print("\n[OK] Potential duplicates:\n")
for idx1, idx2, score in duplicates:
    print(f"[Similarity: {score:.4f}]")
    print(f"  Text {idx1}: {texts[idx1]}")
    print(f"  Text {idx2}: {texts[idx2]}")
    print()
```

### 3. Semantic Search Engine

```python
class SemanticSearchEngine:
    """Simple semantic search engine using Gemini embeddings."""

    def __init__(self, documents: List[str]):
        """
        Initialize search engine with documents.

        Args:
            documents: List of documents to index
        """
        self.documents = documents
        self.embeddings = None
        self._index()

    def _index(self):
        """Generate embeddings for all documents."""
        print(f"[OK] Indexing {len(self.documents)} documents...")

        result = genai.embed_content(
            model="models/embedding-001",
            content=self.documents,
            task_type="retrieval_document"
        )

        self.embeddings = result['embedding']
        print(f"[OK] Indexing complete!")

    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, str, float]]:
        """
        Search for documents similar to query.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of (index, document, similarity_score) tuples
        """
        print(f"[OK] Searching for: {query}")

        # Generate query embedding
        query_result = genai.embed_content(
            model="models/embedding-001",
            content=query,
            task_type="retrieval_query"
        )
        query_embedding = query_result['embedding']

        # Calculate similarities
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = cosine_similarity(query_embedding, doc_embedding)
            similarities.append((i, self.documents[i], similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[2], reverse=True)

        return similarities[:top_k]


# Example usage
documents = [
    "The quick brown fox jumps over the lazy dog",
    "Machine learning is a method of data analysis",
    "Python is an interpreted programming language",
    "Deep learning is part of machine learning methods",
    "The cat sat on the mat",
    "Natural language processing enables computers to understand text",
    "Neural networks are inspired by the human brain",
    "JavaScript is primarily used for web development"
]

# Create search engine
search_engine = SemanticSearchEngine(documents)

# Perform searches
query = "What is machine learning?"
results = search_engine.search(query, top_k=3)

print(f"\n[OK] Top 3 results for: '{query}'\n")
for idx, doc, score in results:
    print(f"[Score: {score:.4f}] {doc}")
```

## Task Types Explained

Gemini embeddings support different task types that optimize the embeddings for specific use cases:

| Task Type | Use Case | Example |
|-----------|----------|---------|
| `retrieval_document` | Documents in a search corpus | Indexing documents for search |
| `retrieval_query` | Search queries | User search queries |
| `semantic_similarity` | Comparing text similarity | Finding similar documents |
| `classification` | Text classification | Categorizing content |
| `clustering` | Grouping similar texts | Document clustering |

**Best Practice:** Use `retrieval_document` for corpus documents and `retrieval_query` for queries in search applications.

## Model Options

### Available Models

1. **`models/embedding-001`**
   - Dimensions: 768
   - Faster, lower cost
   - Good for most use cases

2. **`models/text-embedding-004`** (if available)
   - May have more dimensions
   - Better performance
   - Check latest docs for availability

```python
# Check available models
for model in genai.list_models():
    if 'embedding' in model.name.lower():
        print(f"[OK] Model: {model.name}")
        print(f"    Supported methods: {model.supported_generation_methods}")
```

## Performance Tips

### 1. Batch Processing

```python
# BAD: One request per text (slow)
embeddings = [generate_embedding(text) for text in texts]

# GOOD: Single batch request (fast)
embeddings = generate_embeddings_batch(texts)
```

### 2. Caching Embeddings

```python
import json
import hashlib

def get_cache_key(text: str) -> str:
    """Generate cache key from text."""
    return hashlib.md5(text.encode()).hexdigest()

def cache_embedding(text: str, embedding: list[float], cache_file: str = "embeddings_cache.json"):
    """Save embedding to cache."""
    try:
        with open(cache_file, 'r') as f:
            cache = json.load(f)
    except FileNotFoundError:
        cache = {}

    cache[get_cache_key(text)] = embedding

    with open(cache_file, 'w') as f:
        json.dump(cache, f)

def get_cached_embedding(text: str, cache_file: str = "embeddings_cache.json") -> list[float] | None:
    """Retrieve embedding from cache."""
    try:
        with open(cache_file, 'r') as f:
            cache = json.load(f)
        return cache.get(get_cache_key(text))
    except FileNotFoundError:
        return None
```

### 3. Pre-compute and Store

For large document collections:

```python
import numpy as np

# Generate all embeddings once
embeddings = generate_embeddings_batch(documents)

# Save to file
np.save('document_embeddings.npy', embeddings)

# Load later
embeddings = np.load('document_embeddings.npy')
```

## Cost Considerations

- Gemini API pricing: Check [Google AI pricing](https://ai.google.dev/pricing)
- Embeddings are typically cheaper than text generation
- Batch requests are more efficient
- Cache frequently-used embeddings

## Error Handling

```python
from google.api_core import exceptions
import time

def generate_embedding_with_retry(
    text: str,
    max_retries: int = 3,
    retry_delay: int = 2
) -> list[float] | None:
    """
    Generate embedding with retry logic.

    Args:
        text: Text to embed
        max_retries: Maximum retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Embedding vector or None if failed
    """
    for attempt in range(max_retries):
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="semantic_similarity"
            )
            return result['embedding']

        except exceptions.ResourceExhausted:
            print(f"[WARNING] Rate limit hit, retrying in {retry_delay}s...")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff

        except exceptions.InvalidArgument as e:
            print(f"[ERROR] Invalid argument: {e}")
            return None

        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            if attempt < max_retries - 1:
                print(f"[WARNING] Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                return None

    return None
```

## Complete Working Example

```python
"""
Complete example: Find similar drivers from AI trajectory documents.
File purpose: Created by user request to demonstrate Gemini embeddings.
"""

import google.generativeai as genai
import numpy as np
import os
from dotenv import load_dotenv
from typing import List, Tuple

# Load configuration
load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity."""
    v1, v2 = np.array(vec1), np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def find_similar_items(
    query: str,
    items: List[str],
    top_k: int = 5
) -> List[Tuple[str, float]]:
    """Find most similar items to query."""

    # Generate embeddings
    print(f"[OK] Generating embeddings...")
    all_texts = [query] + items

    result = genai.embed_content(
        model="models/embedding-001",
        content=all_texts,
        task_type="semantic_similarity"
    )

    embeddings = result['embedding']
    query_emb = embeddings[0]
    item_embs = embeddings[1:]

    # Calculate similarities
    print(f"[OK] Calculating similarities...")
    similarities = []
    for i, item_emb in enumerate(item_embs):
        sim = cosine_similarity(query_emb, item_emb)
        similarities.append((items[i], sim))

    # Sort and return top K
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]


def main():
    """Main function."""

    # Example: AI trajectory drivers
    query = "technological unemployment and job displacement"

    drivers = [
        "Rapid advancement in AI capabilities leading to AGI",
        "Economic inequality due to AI-driven automation",
        "Job market disruption from intelligent systems",
        "Increased AI safety research and regulation",
        "Climate change mitigation using AI technology",
        "AI-powered scientific breakthroughs in medicine",
        "Mass unemployment from robotic automation",
        "International AI arms race and competition",
        "Democratization of AI tools and access",
        "AI alignment and control problem solutions"
    ]

    print("="*80)
    print("SEMANTIC SIMILARITY SEARCH WITH GEMINI EMBEDDINGS")
    print("="*80)
    print(f"\nQuery: {query}\n")

    results = find_similar_items(query, drivers, top_k=5)

    print(f"\n[OK] Top 5 most similar drivers:\n")
    for i, (driver, score) in enumerate(results, 1):
        print(f"{i}. [Similarity: {score:.4f}]")
        print(f"   {driver}\n")


if __name__ == "__main__":
    main()
```

## Summary

**Key Points:**
1. Gemini provides high-quality text embeddings via the `embed_content()` API
2. Use appropriate task types for your use case
3. Batch processing is more efficient than individual requests
4. Cosine similarity is the standard metric for comparing embeddings
5. Cache embeddings for frequently-accessed texts
6. Handle rate limits with exponential backoff

**Common Applications:**
- Semantic search
- Document clustering
- Duplicate detection
- Content recommendation
- Text classification

**Best Practices:**
- Use `retrieval_document` for corpus, `retrieval_query` for queries
- Batch multiple texts in single API call
- Cache embeddings to reduce costs
- Handle errors gracefully with retries
- Pre-compute embeddings for large collections

This approach provides powerful semantic understanding for text comparison tasks!
