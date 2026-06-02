"""
Reranking pipeline sketch.

First-stage retrieval returns a broad candidate set. A reranker then scores
query-candidate pairs more precisely and keeps only the strongest evidence for
context construction.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    chunk_id: str
    text: str
    first_stage_score: float
    source: str
    tokens: int


def retrieve_candidates(query: str) -> list[Candidate]:
    # In a real system, this would come from dense, sparse, or hybrid retrieval.
    return [
        Candidate("c1", "Billing admins can export enterprise invoices as CSV.", 0.81, "billing.md", 9),
        Candidate("c2", "Admins can reset passwords for managed users.", 0.79, "admin.md", 7),
        Candidate("c3", "Invoice export is disabled unless finance role is enabled.", 0.74, "roles.md", 10),
        Candidate("c4", "Webhook retries are configured from developer settings.", 0.69, "webhooks.md", 8),
    ]


def cheap_cross_encoder_score(query: str, candidate: Candidate) -> float:
    """
    Toy reranker: reward exact query-term matches and preserve a small amount of
    first-stage score. A real cross-encoder would run model inference here.
    """
    query_terms = set(query.lower().split())
    text_terms = set(candidate.text.lower().replace(".", "").split())
    lexical_overlap = len(query_terms & text_terms) / max(len(query_terms), 1)
    return 0.8 * lexical_overlap + 0.2 * candidate.first_stage_score


def build_context(candidates: list[Candidate], token_budget: int = 18) -> str:
    selected = []
    used_tokens = 0
    for candidate in candidates:
        if used_tokens + candidate.tokens > token_budget:
            continue
        selected.append(candidate)
        used_tokens += candidate.tokens

    blocks = []
    for candidate in selected:
        blocks.append(f"[{candidate.chunk_id} from {candidate.source}]\n{candidate.text}")
    return "\n\n".join(blocks)


def has_enough_evidence(candidate: Candidate, query: str, threshold: float = 0.35) -> bool:
    return cheap_cross_encoder_score(query, candidate) >= threshold


def main() -> None:
    query = "Can finance admins export enterprise invoices?"
    candidates = retrieve_candidates(query)

    reranked = sorted(
        candidates,
        key=lambda candidate: cheap_cross_encoder_score(query, candidate),
        reverse=True,
    )
    if not reranked or not has_enough_evidence(reranked[0], query):
        print("No strong evidence found; ask a clarifying question or widen retrieval.")
        return

    print("Reranked candidates:")
    for candidate in reranked:
        score = cheap_cross_encoder_score(query, candidate)
        print(f"{score:.3f} {candidate.chunk_id}: {candidate.text}")

    print("\nContext sent to the model:")
    print(build_context(reranked))


if __name__ == "__main__":
    main()
