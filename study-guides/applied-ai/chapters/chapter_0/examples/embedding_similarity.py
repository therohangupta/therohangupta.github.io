"""Embedding similarity demo.

The point is not that these toy vectors are meaningful. The point is the
retrieval shape: convert items to vectors, compare by cosine similarity, and
rank by geometric closeness rather than exact keywords. Dense retrieval is an
approximation of semantic fit, not proof that a document is correct.
"""

import numpy as np
from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    doc_id: str
    text: str
    vector: np.ndarray
    source: str


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def normalize(v: np.ndarray) -> np.ndarray:
    if np.linalg.norm(v) == 0:
        raise ValueError("cannot normalize a zero vector")
    return v / np.linalg.norm(v)


documents = [
    Document("d1", "refund policy", normalize(np.array([0.9, 0.1, 0.0])), "billing.md"),
    Document("d2", "refund exception", normalize(np.array([0.85, 0.15, 0.0])), "policy.md"),
    Document("d3", "shipping delay", normalize(np.array([0.1, 0.8, 0.1])), "shipping.md"),
    Document("d4", "password reset", normalize(np.array([0.0, 0.1, 0.9])), "auth.md"),
]

query = normalize(np.array([0.8, 0.2, 0.0]))

ranked = sorted(
    ((doc, cosine(query, doc.vector)) for doc in documents),
    key=lambda item: item[1],
    reverse=True,
)

for doc, score in ranked:
    print(f"{doc.doc_id} {score:.3f} {doc.source}: {doc.text}")

print("\nTop matches are candidates for reranking or citation checks, not final truth.")
