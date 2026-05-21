"""KV-cache decoding sketch.

During decoding, each new token produces one new K/V pair. The model reuses
previous K/V tensors instead of recomputing attention keys and values for the
entire prefix at every step.
"""

from dataclasses import dataclass, field

import numpy as np


@dataclass
class KVCache:
    keys: list[np.ndarray] = field(default_factory=list)
    values: list[np.ndarray] = field(default_factory=list)

    def append(self, key: np.ndarray, value: np.ndarray) -> None:
        self.keys.append(key)
        self.values.append(value)

    @property
    def length(self) -> int:
        return len(self.keys)

    def stacked(self) -> tuple[np.ndarray, np.ndarray]:
        return np.stack(self.keys), np.stack(self.values)


def softmax(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x)
    exp = np.exp(x)
    return exp / exp.sum()


def decode_step(
    token_hidden: np.ndarray,
    cache: KVCache,
    w_q: np.ndarray,
    w_k: np.ndarray,
    w_v: np.ndarray,
) -> np.ndarray:
    query = token_hidden @ w_q
    key = token_hidden @ w_k
    value = token_hidden @ w_v
    cache.append(key, value)

    # Reuse all cached prefix keys/values instead of recomputing them.
    keys, values = cache.stacked()
    scores = (keys @ query) / np.sqrt(query.shape[-1])
    weights = softmax(scores)
    return weights @ values


if __name__ == "__main__":
    rng = np.random.default_rng(3)
    cache = KVCache()
    w_q = rng.normal(size=(8, 4))
    w_k = rng.normal(size=(8, 4))
    w_v = rng.normal(size=(8, 4))

    for step in range(5):
        token_hidden = rng.normal(size=(8,))
        attended = decode_step(token_hidden, cache, w_q, w_k, w_v)
        print(
            f"decoded token {step}, cached prefix length = {cache.length}, "
            f"attended shape = {attended.shape}"
        )
