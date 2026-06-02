"""Tiny retrieval evaluation example.

Retrieval quality should be measured before generation. If the right evidence
is missing from top-k, the model may hallucinate even if it is strong.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class EvalCase:
    query_id: str
    relevant_docs: set[str]
    slice: str


CASES = {
    "q1": EvalCase("q1", {"billing-001", "billing-002"}, "billing"),
    "q2": EvalCase("q2", {"auth-001"}, "auth"),
}

RESULTS: dict[str, list[str]] = {
    "q1": ["billing-002", "webhook-001", "billing-001"],
    "q2": ["billing-001", "auth-001", "auth-002"],
}


def recall_at_k(query_id: str, k: int) -> float:
    relevant = CASES[query_id].relevant_docs
    retrieved = set(RESULTS[query_id][:k])
    return len(relevant & retrieved) / len(relevant)


def mrr(query_id: str) -> float:
    relevant = CASES[query_id].relevant_docs
    for rank, doc_id in enumerate(RESULTS[query_id], start=1):
        if doc_id in relevant:
            return 1 / rank
    return 0.0


if __name__ == "__main__":
    recalls = []
    for query_id, case in CASES.items():
        recall = recall_at_k(query_id, 2)
        recalls.append(recall)
        status = "PASS" if recall >= 0.5 else "FAIL"
        print(query_id, case.slice, status, {"recall@2": recall, "mrr": mrr(query_id)})
    print({"aggregate_recall@2": sum(recalls) / len(recalls)})
