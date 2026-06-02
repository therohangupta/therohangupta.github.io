#!/usr/bin/env python3
"""Estimate KV cache memory for LLM serving scenarios.

This is intentionally approximate. The goal is to build intuition about how
context length, concurrency, architecture, and precision drive memory pressure.
"""

from dataclasses import dataclass


BYTES_PER_GIB = 1024**3


@dataclass(frozen=True)
class ModelKVConfig:
    name: str
    layers: int
    kv_heads: int
    head_dim: int
    bytes_per_value: int


@dataclass(frozen=True)
class ServingScenario:
    active_sequences: int
    average_sequence_length: int
    reserved_fraction: float = 0.15


def estimate_kv_cache_gib(model: ModelKVConfig, scenario: ServingScenario) -> float:
    raw_bytes = (
        scenario.active_sequences
        * scenario.average_sequence_length
        * model.layers
        * model.kv_heads
        * model.head_dim
        * 2
        * model.bytes_per_value
    )
    with_reserved = raw_bytes * (1 + scenario.reserved_fraction)
    return with_reserved / BYTES_PER_GIB


def main() -> None:
    models = [
        ModelKVConfig("small-7b-gqa", layers=32, kv_heads=8, head_dim=128, bytes_per_value=2),
        ModelKVConfig("large-70b-gqa", layers=80, kv_heads=8, head_dim=128, bytes_per_value=2),
    ]
    scenarios = [
        ServingScenario(active_sequences=32, average_sequence_length=4_000),
        ServingScenario(active_sequences=64, average_sequence_length=16_000),
        ServingScenario(active_sequences=128, average_sequence_length=32_000),
    ]

    print("Approximate KV cache memory, including allocator headroom:\n")
    for model in models:
        print(model.name)
        for scenario in scenarios:
            memory_gib = estimate_kv_cache_gib(model, scenario)
            print(
                f"  {scenario.active_sequences:>3} seq x "
                f"{scenario.average_sequence_length:>6} tokens -> "
                f"{memory_gib:6.2f} GiB"
            )
        print()


if __name__ == "__main__":
    main()
