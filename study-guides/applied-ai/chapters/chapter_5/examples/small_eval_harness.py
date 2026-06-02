"""
Small eval harness sketch.

This example shows the core shape of an offline evaluation system:
dataset -> system under test -> scorers -> aggregate metrics.

It intentionally uses a fake model so the evaluation structure is visible
without requiring external APIs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class EvalCase:
    id: str
    input: str
    expected: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class EvalResult:
    case_id: str
    passed: bool
    score: float
    grounded_score: float
    output: str
    tags: tuple[str, ...]
    failure_category: str | None = None


def system_under_test(user_input: str) -> str:
    """Replace this with a prompt/model/retriever/tool workflow."""
    if "refund" in user_input.lower():
        return "Escalate refund requests over $100 to a human agent."
    if "hours" in user_input.lower():
        return "The store is open from 9am to 5pm."
    return "I do not know."


def exact_match(expected: str, actual: str) -> float:
    return 1.0 if expected.strip().lower() == actual.strip().lower() else 0.0


def groundedness(expected: str, actual: str) -> float:
    expected_terms = set(expected.lower().split())
    actual_terms = set(actual.lower().split())
    return len(expected_terms & actual_terms) / max(len(expected_terms), 1)


def run_eval(
    cases: list[EvalCase],
    runner: Callable[[str], str],
) -> list[EvalResult]:
    if not cases:
        raise ValueError("eval dataset must not be empty")

    results: list[EvalResult] = []

    for case in cases:
        output = runner(case.input)
        score = exact_match(case.expected, output)
        grounded_score = groundedness(case.expected, output)
        failure_category = None if score == 1.0 else "wrong_answer"
        results.append(
            EvalResult(
                case_id=case.id,
                passed=score == 1.0,
                score=score,
                grounded_score=grounded_score,
                output=output,
                tags=case.tags,
                failure_category=failure_category,
            )
        )

    return results


def summarize(results: list[EvalResult]) -> None:
    overall = sum(result.score for result in results) / len(results)
    print(f"overall_exact_match={overall:.2f}")
    print(f"overall_groundedness={sum(result.grounded_score for result in results) / len(results):.2f}")

    tags = sorted({tag for result in results for tag in result.tags})
    for tag in tags:
        tagged = [result for result in results if tag in result.tags]
        score = sum(result.score for result in tagged) / len(tagged)
        print(f"slice.{tag}.exact_match={score:.2f} n={len(tagged)}")

    failures = [result for result in results if not result.passed]
    for failure in failures:
        print(f"FAIL {failure.case_id} category={failure.failure_category}: output={failure.output!r}")


if __name__ == "__main__":
    dataset = [
        EvalCase(
            id="refund_policy",
            input="Can I get a refund for a $200 order?",
            expected="Escalate refund requests over $100 to a human agent.",
            tags=("refund", "policy", "high_risk"),
        ),
        EvalCase(
            id="store_hours",
            input="What are your hours?",
            expected="The store is open from 9am to 5pm.",
            tags=("simple", "faq"),
        ),
        EvalCase(
            id="unknown",
            input="Can you diagnose this medical symptom?",
            expected="I do not know.",
            tags=("unsupported", "safety"),
        ),
    ]

    summarize(run_eval(dataset, system_under_test))
