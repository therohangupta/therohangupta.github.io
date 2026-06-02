"""
Rubric scoring example.

Rubrics make subjective evaluation more actionable by decomposing quality into
dimensions. This is the shape of a human-review or judge-model scorecard for a
RAG answer: each dimension has a bounded score, rationale, and confidence.
"""

from __future__ import annotations

from dataclasses import dataclass


MIN_SCORE = 1
MAX_SCORE = 3


@dataclass(frozen=True)
class DimensionScore:
    score: int
    rationale: str
    confidence: float

    def __post_init__(self) -> None:
        if not MIN_SCORE <= self.score <= MAX_SCORE:
            raise ValueError(f"score must be {MIN_SCORE}-{MAX_SCORE}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class RubricScore:
    answers_question: DimensionScore
    grounded_in_sources: DimensionScore
    handles_uncertainty: DimensionScore
    concise: DimensionScore
    failure_category: str | None = None

    @property
    def total(self) -> int:
        return (
            self.answers_question.score
            + self.grounded_in_sources.score
            + self.handles_uncertainty.score
            + self.concise.score
        )

    @property
    def max_score(self) -> int:
        return 12


def score_rag_answer(question: str, answer: str, sources: list[str]) -> RubricScore:
    """
    A production version might use a calibrated judge model or human annotator.
    This deterministic version makes the scorecard data structure visible.
    """
    if not question.strip() or not answer.strip():
        raise ValueError("question and answer are required")
    if not sources:
        return RubricScore(
            answers_question=DimensionScore(1, "Cannot evaluate without source context.", 0.95),
            grounded_in_sources=DimensionScore(1, "No sources provided.", 1.0),
            handles_uncertainty=DimensionScore(1, "Answer should acknowledge missing sources.", 0.9),
            concise=DimensionScore(3, "Short answer.", 0.8),
            failure_category="missing_evidence",
        )

    answer_lower = answer.lower()
    source_text = " ".join(sources).lower()
    question_terms = set(question.lower().strip("?").split())
    overlap = question_terms & set(answer_lower.split())

    grounded = answer_lower.strip(".") in source_text
    uncertainty_text = "not enough information" in answer_lower or "cannot determine" in answer_lower
    too_long = len(answer.split()) > 40
    failure_category = None if grounded else "unsupported_claim"

    return RubricScore(
        answers_question=DimensionScore(
            3 if overlap else 1,
            "Answer overlaps with the user's requested concept." if overlap else "Answer misses the main question.",
            0.75,
        ),
        grounded_in_sources=DimensionScore(
            3 if grounded else 1,
            "Answer is directly supported by a source." if grounded else "Answer is not directly found in sources.",
            0.85,
        ),
        handles_uncertainty=DimensionScore(
            3 if grounded or uncertainty_text else 1,
            "Grounded answer or explicit uncertainty." if grounded or uncertainty_text else "No uncertainty despite weak evidence.",
            0.8,
        ),
        concise=DimensionScore(
            1 if too_long else 3,
            "Too verbose for support context." if too_long else "Concise enough for the channel.",
            0.7,
        ),
        failure_category=failure_category,
    )


if __name__ == "__main__":
    question = "What is the refund limit before human approval is required?"
    sources = [
        "Refund requests over $100 require human approval.",
        "Refunds below $100 can be processed automatically if policy conditions are met.",
    ]
    candidates = [
        "Refund requests over $100 require human approval.",
        "You can always get a refund instantly.",
    ]

    for candidate in candidates:
        score = score_rag_answer(question, candidate, sources)
        print(candidate)
        print(f"score={score.total}/{score.max_score} failure={score.failure_category}")
