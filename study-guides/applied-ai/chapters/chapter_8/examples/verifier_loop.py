"""
Verifier loop example.

The generator proposes multiple answers. Deterministic checks and a simple
verifier score decide which answer is safe enough to return.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    answer: str
    citations: list[str]


@dataclass(frozen=True)
class VerificationResult:
    candidate: Candidate
    score: float
    accepted: bool
    reasons: tuple[str, ...]


def generate_candidates(question: str) -> list[Candidate]:
    """Pretend these came from an LLM sampled at nonzero temperature."""
    return [
        Candidate(
            answer=f"{question} The refund window is 30 days.",
            citations=["policy_refunds"],
        ),
        Candidate(
            answer=f"{question} Refunds are always available with no limit.",
            citations=[],
        ),
        Candidate(
            answer=f"{question} Refunds are available within the policy window.",
            citations=["policy_refunds", "policy_exceptions"],
        ),
    ]


def verify_candidate(candidate: Candidate, evidence: dict[str, str]) -> VerificationResult:
    reasons = []
    if not candidate.citations:
        reasons.append("missing_citations")
    if "always available" in candidate.answer.lower():
        reasons.append("overbroad_claim")
    unsupported = [citation for citation in candidate.citations if citation not in evidence]
    if unsupported:
        reasons.append(f"unsupported_citations={unsupported}")

    score = 0.0 if reasons else verifier_score(candidate)
    return VerificationResult(candidate, score, not reasons and score >= 0.65, tuple(reasons))


def verifier_score(candidate: Candidate) -> float:
    """Toy learned-verifier stand-in: score grounded, cautious answers higher."""
    score = 0.0
    score += 0.4 if "policy" in candidate.answer.lower() else 0.0
    score += 0.3 if len(candidate.citations) >= 2 else 0.1
    score += 0.3 if "always" not in candidate.answer.lower() else -0.4
    return score


def answer_with_verification(question: str, threshold: float = 0.65) -> Candidate | None:
    candidates = generate_candidates(question)
    evidence = {"policy_refunds": "Refund window is 30 days.", "policy_exceptions": "Exceptions require review."}
    verified = [verify_candidate(candidate, evidence) for candidate in candidates]
    for result in verified:
        if not result.accepted:
            print({"rejected": result.candidate.answer, "reasons": result.reasons})

    accepted = [result for result in verified if result.accepted and result.score >= threshold]
    if not accepted:
        return None
    return max(accepted, key=lambda result: result.score).candidate


if __name__ == "__main__":
    result = answer_with_verification("Can I get a refund?")
    if result is None:
        print("Escalate to human or ask a clarifying question.")
    else:
        print(result.answer)
        print("citations:", result.citations)
