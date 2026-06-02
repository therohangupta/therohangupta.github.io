"""
Reward modeling sketch.

This example shows the shape of preference-based reward modeling:

1. Start with prompt, chosen response, rejected response triples.
2. Score each prompt-response pair.
3. Train the scorer so chosen responses receive higher reward.

The model here is intentionally tiny. A production system would use a
transformer encoder/decoder backbone, dataset versioning, held-out evals,
label-quality checks, and safety-specific reward dimensions.
"""

from dataclasses import dataclass
from math import exp, log


@dataclass(frozen=True)
class PreferenceExample:
    prompt: str
    chosen: str
    rejected: str


class ToyRewardModel:
    def __init__(self) -> None:
        self.weights = {
            "specific": 0.5,
            "grounded": 0.5,
            "concise": 0.1,
            "unsafe": -1.0,
        }

    def score(self, prompt: str, response: str) -> float:
        text = f"{prompt} {response}".lower()
        return sum(weight for feature, weight in self.weights.items() if feature in text)

    def update(self, example: PreferenceExample, learning_rate: float = 0.1) -> float:
        chosen_score = self.score(example.prompt, example.chosen)
        rejected_score = self.score(example.prompt, example.rejected)

        # Pairwise logistic loss: prefer chosen_score > rejected_score.
        margin = chosen_score - rejected_score
        loss = -log(sigmoid(margin))

        # A real model would backpropagate through neural features. This toy
        # update nudges word features found in chosen/rejected responses.
        chosen_words = set(example.chosen.lower().split())
        rejected_words = set(example.rejected.lower().split())
        for feature in self.weights:
            if feature in chosen_words:
                self.weights[feature] += learning_rate * (1 - sigmoid(margin))
            if feature in rejected_words:
                self.weights[feature] -= learning_rate * (1 - sigmoid(margin))

        return loss


def sigmoid(value: float) -> float:
    return 1 / (1 + exp(-value))


def main() -> None:
    data = [
        PreferenceExample(
            prompt="Explain why a cache improves latency.",
            chosen="A specific grounded answer: caching avoids repeated work on hot reads.",
            rejected="Caching is nice and usually good.",
        ),
        PreferenceExample(
            prompt="Answer a medical question.",
            chosen="I cannot provide unsafe instructions; consult a clinician.",
            rejected="Here are unsafe steps you can try.",
        ),
    ]

    reward_model = ToyRewardModel()

    for epoch in range(3):
        total_loss = 0.0
        for example in data:
            total_loss += reward_model.update(example)
        print(f"epoch={epoch} loss={total_loss:.3f} weights={reward_model.weights}")

    candidate = "A concise grounded answer with specific tradeoffs."
    print("candidate reward:", reward_model.score("Explain caching.", candidate))


if __name__ == "__main__":
    main()
