"""
DPO-style comparison example.

DPO trains from preference pairs:

    prompt, chosen_response, rejected_response

The real DPO objective compares how much the trainable policy prefers the
chosen answer over the rejected answer relative to a frozen reference policy.
This sketch uses log-probability numbers directly so the optimization shape is
visible without implementing a language model.
"""

from dataclasses import dataclass
from math import exp, log


@dataclass(frozen=True)
class Comparison:
    prompt: str
    chosen: str
    rejected: str
    policy_logp_chosen: float
    policy_logp_rejected: float
    reference_logp_chosen: float
    reference_logp_rejected: float


def sigmoid(value: float) -> float:
    if value >= 0:
        z = exp(-value)
        return 1 / (1 + z)
    z = exp(value)
    return z / (1 + z)


def validate_beta(beta: float) -> None:
    if beta <= 0:
        raise ValueError("beta must be positive")


def sigmoid_loss(value: float) -> float:
    probability = sigmoid(value)
    return -log(max(probability, 1e-12))


def dpo_loss(example: Comparison, beta: float = 0.1) -> float:
    validate_beta(beta)
    policy_preference = example.policy_logp_chosen - example.policy_logp_rejected
    reference_preference = example.reference_logp_chosen - example.reference_logp_rejected

    # Positive values mean the policy prefers the chosen response more than the
    # reference model does. The loss rewards that while retaining an anchor.
    relative_preference = beta * (policy_preference - reference_preference)
    return sigmoid_loss(relative_preference)


def average_loss(examples: list[Comparison], beta: float = 0.1) -> float:
    if not examples:
        raise ValueError("examples are required")
    return sum(dpo_loss(example, beta) for example in examples) / len(examples)


def main() -> None:
    examples = [
        Comparison(
            prompt="Summarize the incident.",
            chosen="The outage was caused by a bad cache invalidation rollout.",
            rejected="The outage happened for several complicated reasons.",
            policy_logp_chosen=-8.2,
            policy_logp_rejected=-7.9,
            reference_logp_chosen=-8.5,
            reference_logp_rejected=-8.0,
        ),
        Comparison(
            prompt="Give a safe answer.",
            chosen="I cannot help with that unsafe request.",
            rejected="Sure, here are the steps.",
            policy_logp_chosen=-3.0,
            policy_logp_rejected=-2.5,
            reference_logp_chosen=-2.8,
            reference_logp_rejected=-2.7,
        ),
    ]

    for example in examples:
        loss = dpo_loss(example)
        print(f"prompt={example.prompt!r} dpo_loss={loss:.3f}")
    print(f"average_loss={average_loss(examples):.3f}")


if __name__ == "__main__":
    main()
