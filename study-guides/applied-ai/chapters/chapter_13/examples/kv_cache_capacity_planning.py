#!/usr/bin/env python3
"""Token-aware KV cache capacity planning sketch."""

from dataclasses import dataclass
from math import floor


GIB = 1024**3


@dataclass(frozen=True)
class Model:
    layers: int
    kv_heads: int
    head_dim: int
    bytes_per_value: int
    weight_memory_gib: float


def kv_bytes_per_sequence(model: Model, sequence_length: int) -> int:
    return sequence_length * model.layers * model.kv_heads * model.head_dim * 2 * model.bytes_per_value


def max_active_sequences(
    model: Model,
    gpu_memory_gib: float,
    sequence_length: int,
    reserved_gib: float = 8.0,
) -> int:
    available = (gpu_memory_gib - model.weight_memory_gib - reserved_gib) * GIB
    if available <= 0:
        return 0
    return floor(available / kv_bytes_per_sequence(model, sequence_length))


def main() -> None:
    model = Model(layers=80, kv_heads=8, head_dim=128, bytes_per_value=2, weight_memory_gib=140)
    for context in [4_000, 16_000, 32_000, 64_000]:
        capacity = max_active_sequences(model, gpu_memory_gib=192, sequence_length=context)
        print(f"context={context:>6} tokens -> approx {capacity:>3} active sequences")


if __name__ == "__main__":
    main()
