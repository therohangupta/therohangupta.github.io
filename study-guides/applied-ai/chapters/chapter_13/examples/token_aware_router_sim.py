#!/usr/bin/env python3
"""Compare request-count routing with token-aware routing."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Request:
    request_id: str
    tenant: str
    input_tokens: int
    expected_output_tokens: int

    @property
    def estimated_tokens(self) -> int:
        return self.input_tokens + self.expected_output_tokens


@dataclass
class Worker:
    worker_id: str
    requests: list[Request] = field(default_factory=list)

    @property
    def request_count(self) -> int:
        return len(self.requests)

    @property
    def token_load(self) -> int:
        return sum(request.estimated_tokens for request in self.requests)

    def assign(self, request: Request) -> None:
        self.requests.append(request)


def route_by_request_count(requests: list[Request], worker_count: int) -> list[Worker]:
    workers = [Worker(f"worker-{idx}") for idx in range(worker_count)]
    for request in requests:
        min(workers, key=lambda worker: worker.request_count).assign(request)
    return workers


def route_by_token_load(requests: list[Request], worker_count: int) -> list[Worker]:
    workers = [Worker(f"worker-{idx}") for idx in range(worker_count)]
    for request in requests:
        min(workers, key=lambda worker: worker.token_load).assign(request)
    return workers


def print_workers(title: str, workers: list[Worker]) -> None:
    print(title)
    for worker in workers:
        ids = ", ".join(request.request_id for request in worker.requests)
        print(
            f"  {worker.worker_id}: "
            f"{worker.request_count} requests, {worker.token_load:>6} tokens "
            f"({ids})"
        )
    print()


def main() -> None:
    requests = [
        Request("short-1", "free", 600, 120),
        Request("short-2", "free", 800, 160),
        Request("long-1", "enterprise", 36_000, 2_000),
        Request("short-3", "pro", 700, 140),
        Request("long-2", "enterprise", 52_000, 4_000),
        Request("short-4", "free", 500, 100),
        Request("medium-1", "pro", 4_000, 800),
        Request("short-5", "free", 900, 160),
    ]

    print_workers("Request-count routing", route_by_request_count(requests, 3))
    print_workers("Token-aware routing", route_by_token_load(requests, 3))


if __name__ == "__main__":
    main()
