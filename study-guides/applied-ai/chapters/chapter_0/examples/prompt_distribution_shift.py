"""Toy example: prompt wording shifts the output distribution.

Real LLM logits are learned, but the control idea is the same: changing the
context changes which continuations become likely. In production, this is why
prompt changes need eval suites — a small wording change can shift the entire
output distribution in ways that are hard to predict without measurement.
"""

from collections import Counter
from dataclasses import dataclass
import random


@dataclass(frozen=True)
class PromptEffect:
    """Records how a prompt modifier changes the token distribution."""
    keyword: str
    boosted_token: str
    boost_weight: int


PROMPT_EFFECTS: list[PromptEffect] = [
    PromptEffect(keyword="answer only if cited", boosted_token="unknown", boost_weight=5),
    PromptEffect(keyword="be optimistic", boosted_token="yes", boost_weight=4),
    PromptEffect(keyword="be skeptical", boosted_token="no", boost_weight=4),
]


def toy_next_token_distribution(prompt: str) -> Counter:
    prompt = prompt.lower()
    scores = Counter({"yes": 1, "no": 1, "unknown": 1})

    for effect in PROMPT_EFFECTS:
        if effect.keyword in prompt:
            scores[effect.boosted_token] += effect.boost_weight

    total = sum(scores.values())
    return Counter({token: score / total for token, score in scores.items()})


def sample(distribution: Counter, n: int = 8) -> list[str]:
    tokens = list(distribution)
    weights = [distribution[token] for token in tokens]
    return random.choices(tokens, weights=weights, k=n)


random.seed(7)

for prompt in [
    "Is this claim true?",
    "Be optimistic. Is this claim true?",
    "Be skeptical. Answer only if cited. Is this claim true?",
    "Be optimistic, but answer only if cited. Is this claim true?",
]:
    distribution = toy_next_token_distribution(prompt)
    print(prompt)
    print(dict(distribution))
    print("samples:", sample(distribution))
