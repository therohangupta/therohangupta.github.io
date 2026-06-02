#!/usr/bin/env python3
"""Small bootstrap interval and minimum-detectable-effect sketch."""

from random import Random
from statistics import mean

baseline = [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1]
candidate = [1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1]


def bootstrap_delta(xs, ys, rounds=2000, seed=7):
    rng = Random(seed)
    deltas = []
    for _ in range(rounds):
        bx = [rng.choice(xs) for _ in xs]
        by = [rng.choice(ys) for _ in ys]
        deltas.append(mean(by) - mean(bx))
    deltas.sort()
    return deltas[int(0.025 * rounds)], mean(deltas), deltas[int(0.975 * rounds)]


lo, mid, hi = bootstrap_delta(baseline, candidate)
print(f"baseline={mean(baseline):.3f}")
print(f"candidate={mean(candidate):.3f}")
print(f"delta interval=[{lo:.3f}, {hi:.3f}], center={mid:.3f}")
print("If the interval overlaps zero, treat the result as evidence, not proof.")
