"""
Synthetic data generation sketch.

This example shows the shape of a targeted synthetic data pipeline:
generate examples for known gaps, validate structure, deduplicate, and keep
the generated set separate from real held-out evaluation data.
"""

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SeedCase:
    category: str
    failure_mode: str
    real_example: str


@dataclass(frozen=True)
class SyntheticExample:
    category: str
    text: str
    expected_label: str
    source_failure_mode: str
    provenance: str
    quality_score: float
    rejection_reason: str | None = None


SEEDS = [
    SeedCase(
        category="refund_policy",
        failure_mode="missing_order_id",
        real_example="I returned my headphones but lost the order email. Can I still get refunded?",
    ),
    SeedCase(
        category="account_transfer",
        failure_mode="ambiguous_authority",
        real_example="Our admin left the company. I need ownership moved to me.",
    ),
]


def generate_with_teacher(seed: SeedCase, variants: int = 3) -> list[SyntheticExample]:
    """Pretend this calls a stronger model with a carefully constrained prompt."""
    examples = []
    for index in range(variants):
        examples.append(
            SyntheticExample(
                category=seed.category,
                text=(
                    f"[variant {index}] User asks about {seed.category} with "
                    f"failure mode {seed.failure_mode}: {seed.real_example}"
                ),
                expected_label=seed.category,
                source_failure_mode=seed.failure_mode,
                provenance=f"teacher_model=example-v1 seed={seed.category}:{seed.failure_mode}",
                quality_score=0.85 - index * 0.05,
            )
        )
    return examples


def is_valid(example: SyntheticExample) -> bool:
    """Cheap structural validation before anything reaches training."""
    if not example.text or not example.expected_label:
        return False
    if example.expected_label != example.category:
        return False
    if len(example.text.split()) < 8:
        return False
    if example.quality_score < 0.7:
        return False
    return True


def deduplicate(examples: Iterable[SyntheticExample]) -> list[SyntheticExample]:
    """Use exact text here; production systems often use embedding similarity too."""
    seen: set[str] = set()
    unique: list[SyntheticExample] = []
    for example in examples:
        key = example.text.lower().strip()
        if key in seen:
            continue
        seen.add(key)
        unique.append(example)
    return unique


def build_synthetic_dataset(seeds: Iterable[SeedCase]) -> list[SyntheticExample]:
    generated: list[SyntheticExample] = []
    for seed in seeds:
        generated.extend(generate_with_teacher(seed))

    valid = [example for example in generated if is_valid(example)]
    return deduplicate(valid)


if __name__ == "__main__":
    dataset = build_synthetic_dataset(SEEDS)
    for row in dataset:
        print(row)
