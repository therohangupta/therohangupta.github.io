"""
Memory leak profiling sketch.

Run this locally with a profiler such as tracemalloc or py-spy. The first cache
is intentionally unsafe; the second cache uses an LRU bound.
"""

from __future__ import annotations

import functools
import random
import string
import tracemalloc


unsafe_cache: dict[str, str] = {}


def random_prompt() -> str:
    suffix = "".join(random.choice(string.ascii_letters) for _ in range(32))
    return f"summarize customer account {suffix}"


def expensive_response(prompt: str) -> str:
    # Pretend this string is a large model response plus retrieved context.
    return f"response for {prompt}\n" + ("x" * 10_000)


def unsafe_cached_response(prompt: str) -> str:
    """Leaks memory when prompts are mostly unique."""
    if prompt not in unsafe_cache:
        unsafe_cache[prompt] = expensive_response(prompt)
    return unsafe_cache[prompt]


@functools.lru_cache(maxsize=256)
def bounded_cached_response(prompt: str) -> str:
    """Keeps memory bounded by evicting old entries."""
    return expensive_response(prompt)


def run_workload(use_safe_cache: bool, iterations: int = 2_000) -> None:
    for _ in range(iterations):
        prompt = random_prompt()
        if use_safe_cache:
            bounded_cached_response(prompt)
        else:
            unsafe_cached_response(prompt)


def print_top_allocations(snapshot: tracemalloc.Snapshot, limit: int = 5) -> None:
    for stat in snapshot.statistics("lineno")[:limit]:
        print(stat)


def main() -> None:
    tracemalloc.start()

    run_workload(use_safe_cache=False)
    unsafe_snapshot = tracemalloc.take_snapshot()
    print("Unsafe cache entries:", len(unsafe_cache))
    print_top_allocations(unsafe_snapshot)

    unsafe_cache.clear()
    bounded_cached_response.cache_clear()

    run_workload(use_safe_cache=True)
    safe_snapshot = tracemalloc.take_snapshot()
    print("Bounded cache info:", bounded_cached_response.cache_info())
    print_top_allocations(safe_snapshot)


if __name__ == "__main__":
    main()
