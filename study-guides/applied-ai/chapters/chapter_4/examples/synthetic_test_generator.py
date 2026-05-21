"""
Synthetic test generator sketch.

Synthetic evals are useful for expanding coverage, but generated cases should
be reviewed, deduplicated, validated, and mixed with real examples before they
become release gates.
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class GenerationConfig:
    count: int
    max_per_intent: int
    review_required: bool = True

    def __post_init__(self) -> None:
        if self.count <= 0:
            raise ValueError("count must be positive")
        if self.max_per_intent <= 0:
            raise ValueError("max_per_intent must be positive")


@dataclass(frozen=True)
class SyntheticCase:
    id: str
    input: str
    expected_behavior: str
    tags: tuple[str, ...]
    source_pattern: str
    review_status: str
    rejection_reason: str | None = None


INTENTS = [
    ("refund", "Escalate refund requests over $100 to a human agent."),
    ("account deletion", "Explain account deletion steps and warn about permanence."),
    ("unsupported medical advice", "Refuse diagnosis and suggest contacting a clinician."),
]

STYLES = [
    "polite",
    "angry",
    "short",
    "verbose",
]


def generate_case(index: int) -> SyntheticCase:
    intent, expected = random.choice(INTENTS)
    style = random.choice(STYLES)

    prompts = {
        "polite": f"Hi, could you help me with {intent}?",
        "angry": f"I am furious. Fix this now: {intent}.",
        "short": f"Need help: {intent}",
        "verbose": f"I have a long explanation, but the main thing is that I need help with {intent}. What should I do next?",
    }

    return SyntheticCase(
        id=f"synthetic_{index:03d}",
        input=prompts[style],
        expected_behavior=expected,
        tags=("synthetic", intent.replace(" ", "_"), style),
        source_pattern="intent_style_cross_product",
        review_status="pending_review",
    )


def validate_case(case: SyntheticCase) -> SyntheticCase:
    if len(case.input.split()) < 4:
        return SyntheticCase(**{**asdict(case), "review_status": "rejected", "rejection_reason": "too_short"})
    if case.expected_behavior.lower() in case.input.lower():
        return SyntheticCase(**{**asdict(case), "review_status": "rejected", "rejection_reason": "label_leakage"})
    return SyntheticCase(**{**asdict(case), "review_status": "accepted"})


def generate_suite(config: GenerationConfig) -> list[SyntheticCase]:
    seen_inputs: set[str] = set()
    per_intent: dict[str, int] = {}
    cases: list[SyntheticCase] = []
    attempts = 0

    while len(cases) < config.count and attempts < config.count * 10:
        attempts += 1
        candidate = validate_case(generate_case(attempts))
        intent_tag = candidate.tags[1]

        if candidate.input in seen_inputs:
            continue
        if per_intent.get(intent_tag, 0) >= config.max_per_intent:
            continue

        seen_inputs.add(candidate.input)
        per_intent[intent_tag] = per_intent.get(intent_tag, 0) + 1
        cases.append(candidate)

    if len(cases) < config.count:
        print("WARNING: coverage target not met; generation distribution may be too narrow")

    return cases


if __name__ == "__main__":
    random.seed(7)
    cases = generate_suite(GenerationConfig(count=5, max_per_intent=3))
    print(json.dumps([asdict(case) for case in cases], indent=2))
