#!/usr/bin/env python3
"""Toy continuous batching scheduler.

The model is intentionally simple: every active request emits one token per
tick. Finished requests leave the batch, and waiting requests can enter.
"""

from dataclasses import dataclass
from collections import deque


@dataclass
class Request:
    request_id: str
    output_tokens_remaining: int


def run_scheduler(requests: list[Request], max_active: int) -> None:
    waiting = deque(requests)
    active: list[Request] = []
    tick = 0

    while waiting or active:
        while waiting and len(active) < max_active:
            active.append(waiting.popleft())

        active_ids = ", ".join(request.request_id for request in active)
        print(f"tick {tick:>2}: active=[{active_ids}]")

        for request in active:
            request.output_tokens_remaining -= 1

        active = [request for request in active if request.output_tokens_remaining > 0]
        tick += 1


def main() -> None:
    requests = [
        Request("short-a", 2),
        Request("long-a", 7),
        Request("short-b", 1),
        Request("medium-a", 4),
        Request("short-c", 2),
    ]
    run_scheduler(requests, max_active=3)


if __name__ == "__main__":
    main()
