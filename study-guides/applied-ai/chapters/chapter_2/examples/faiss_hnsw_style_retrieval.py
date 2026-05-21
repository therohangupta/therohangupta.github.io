"""
FAISS/HNSW-style retrieval sketch.

This example uses only numpy so it can run without FAISS. It demonstrates the
shape of vector retrieval: embed documents, normalize vectors, search nearest
neighbors, and return source metadata.

In production, the exact_search function would be replaced by FAISS, pgvector,
Pinecone, Weaviate, Milvus, or another vector index. HNSW would avoid scanning
every vector by navigating an approximate nearest-neighbor graph. The tradeoff:
exact search is simple and high-recall; ANN search is faster at scale but can
miss candidates unless you tune parameters like ef_search / probes / top_k.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np


DIM = 32


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    metadata: dict[str, str]


def toy_embed(text: str) -> np.ndarray:
    """Deterministic toy embedding based on hashed tokens."""
    vector = np.zeros(DIM, dtype=np.float32)
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = digest[0] % DIM
        sign = 1.0 if digest[1] % 2 == 0 else -1.0
        vector[index] += sign

    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def exact_search(
    query: str,
    chunks: list[Chunk],
    top_k: int = 3,
    metadata_filter: dict[str, str] | None = None,
) -> list[tuple[float, Chunk]]:
    """Exact cosine search. FAISS IndexFlatIP is conceptually similar."""
    if metadata_filter:
        chunks = [
            chunk
            for chunk in chunks
            if all(chunk.metadata.get(key) == value for key, value in metadata_filter.items())
        ]

    query_vector = toy_embed(query)
    matrix = np.stack([toy_embed(chunk.text) for chunk in chunks])
    scores = matrix @ query_vector
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [(float(scores[i]), chunks[i]) for i in top_indices]


def main() -> None:
    chunks = [
        Chunk(
            "billing-001",
            "Enterprise invoices can be exported from the billing dashboard.",
            {"product": "billing", "source": "billing_guide.md"},
        ),
        Chunk(
            "auth-001",
            "Users can reset multi-factor authentication from security settings.",
            {"product": "auth", "source": "security_guide.md"},
        ),
        Chunk(
            "billing-002",
            "Invoice permissions are controlled by the finance admin role.",
            {"product": "billing", "source": "roles.md"},
        ),
    ]

    for score, chunk in exact_search(
        "How do finance users access invoices?",
        chunks,
        metadata_filter={"product": "billing"},
    ):
        print(f"{score:.3f} {chunk.chunk_id} {chunk.metadata['source']}: {chunk.text}")


if __name__ == "__main__":
    main()
