#!/usr/bin/env python3
"""Pure-Python KV-cache decoding sketch."""

from dataclasses import dataclass, field
from math import exp


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def softmax(values):
    m = max(values)
    exps = [exp(v - m) for v in values]
    total = sum(exps)
    return [v / total for v in exps]


@dataclass
class KVCache:
    keys: list[list[float]] = field(default_factory=list)
    values: list[list[float]] = field(default_factory=list)

    def append(self, key, value):
        self.keys.append(key)
        self.values.append(value)


def decode_step(hidden, cache):
    # Toy projection: query/key/value are the hidden vector itself.
    query = hidden
    cache.append(hidden, hidden)
    scores = [dot(query, key) for key in cache.keys]
    weights = softmax(scores)
    return [sum(weights[i] * cache.values[i][d] for i in range(len(cache.values))) for d in range(len(hidden))]


def main():
    cache = KVCache()
    for token, hidden in enumerate([[1.0, 0.0], [0.5, 0.5], [0.0, 1.0]]):
        output = decode_step(hidden, cache)
        print(f"step={token}, cache_length={len(cache.keys)}, output={[round(v, 3) for v in output]}")


if __name__ == "__main__":
    main()
