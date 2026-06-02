"""
BM25 + dense hybrid retrieval.

This small example shows why production systems often combine lexical and
semantic retrieval. BM25 catches exact terms such as "ERR-42"; dense-style
similarity catches related meaning. Reciprocal rank fusion merges the rankings
without assuming their raw scores are comparable.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict


DOCUMENTS = {
    "doc1": "ERR-42 means the webhook signature is invalid.",
    "doc2": "Rotate the webhook secret when signature validation fails.",
    "doc3": "Enterprise invoices are exported from the billing dashboard.",
    "doc4": "Finance admins can grant invoice export permissions.",
}

SYNONYMS = {
    "permission": "grant",
    "permissions": "grant",
    "access": "grant",
    "invoice": "invoices",
    "webhooks": "webhook",
    "invalid": "fails",
}


def tokenize(text: str) -> list[str]:
    return [token.strip(".,:;!?").lower() for token in text.split()]


def bm25(query: str) -> list[str]:
    query_terms = tokenize(query)
    doc_terms = {doc_id: tokenize(text) for doc_id, text in DOCUMENTS.items()}
    doc_freq = defaultdict(int)
    for terms in doc_terms.values():
        for term in set(terms):
            doc_freq[term] += 1

    avg_len = sum(len(terms) for terms in doc_terms.values()) / len(doc_terms)
    k1 = 1.5
    b = 0.75
    scores = {}

    for doc_id, terms in doc_terms.items():
        counts = Counter(terms)
        score = 0.0
        for term in query_terms:
            if counts[term] == 0:
                continue
            idf = math.log(1 + (len(DOCUMENTS) - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5))
            numerator = counts[term] * (k1 + 1)
            denominator = counts[term] + k1 * (1 - b + b * len(terms) / avg_len)
            score += idf * numerator / denominator
        scores[doc_id] = score

    return sorted(scores, key=scores.get, reverse=True)


def denseish(query: str) -> list[str]:
    """Toy semantic retrieval using synonym expansion and token overlap."""
    expanded_query = [SYNONYMS.get(token, token) for token in tokenize(query)]
    query_counts = Counter(expanded_query)
    scores = {}

    for doc_id, text in DOCUMENTS.items():
        expanded_doc = [SYNONYMS.get(token, token) for token in tokenize(text)]
        doc_counts = Counter(expanded_doc)
        scores[doc_id] = sum(query_counts[token] * doc_counts[token] for token in query_counts)

    return sorted(scores, key=scores.get, reverse=True)


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    scores = defaultdict(float)
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] += 1 / (k + rank)
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def main() -> None:
    query = "Who can access invoice exports?"
    lexical = bm25(query)
    semantic = denseish(query)
    fused = reciprocal_rank_fusion([lexical, semantic])

    print("BM25:", lexical)
    print("Dense-ish:", semantic)
    print("Hybrid:")
    for doc_id, score in fused:
        print(f"{score:.4f} {doc_id}: {DOCUMENTS[doc_id]}")


if __name__ == "__main__":
    main()
