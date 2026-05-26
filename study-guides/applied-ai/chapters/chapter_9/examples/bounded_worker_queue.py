"""
Bounded worker queue sketch.

The point of this example is backpressure. An unbounded queue can hide overload
until latency is already terrible. A bounded queue makes overload explicit.
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass, field


MAX_QUEUE_SIZE = 100
MAX_ATTEMPTS = 3
WORKER_COUNT = 4


@dataclass
class Job:
    job_id: str
    tenant_id: str
    prompt: str
    idempotency_key: str
    attempts: int = 0
    metadata: dict[str, str] = field(default_factory=dict)


class JobStore:
    """Tiny in-memory stand-in for a durable job table."""

    def __init__(self) -> None:
        self.completed: dict[str, str] = {}

    def already_completed(self, idempotency_key: str) -> bool:
        return idempotency_key in self.completed

    def mark_completed(self, idempotency_key: str, result: str) -> None:
        self.completed[idempotency_key] = result


async def run_inference(job: Job) -> str:
    await asyncio.sleep(0.05)
    if random.random() < 0.2:
        raise TimeoutError("simulated transient model timeout")
    return f"answer for {job.job_id}"


async def worker(name: str, queue: asyncio.Queue[Job], store: JobStore) -> None:
    while True:
        job = await queue.get()
        try:
            if store.already_completed(job.idempotency_key):
                print(f"{name}: skipping duplicate {job.job_id}")
                continue

            job.attempts += 1
            try:
                result = await run_inference(job)
            except TimeoutError:
                if job.attempts < MAX_ATTEMPTS:
                    await queue.put(job)
                    print(f"{name}: retrying {job.job_id}")
                else:
                    print(f"{name}: dead-letter {job.job_id}")
                continue

            store.mark_completed(job.idempotency_key, result)
            print(f"{name}: completed {job.job_id}")
        finally:
            queue.task_done()


async def submit_job(queue: asyncio.Queue[Job], job: Job) -> bool:
    try:
        queue.put_nowait(job)
        return True
    except asyncio.QueueFull:
        return False


async def main() -> None:
    queue: asyncio.Queue[Job] = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
    store = JobStore()

    workers = [
        asyncio.create_task(worker(f"worker-{i}", queue, store))
        for i in range(WORKER_COUNT)
    ]

    for i in range(20):
        accepted = await submit_job(
            queue,
            Job(
                job_id=f"job-{i}",
                tenant_id="tenant-a",
                prompt="Generate account summary.",
                idempotency_key=f"tenant-a:summary:{i}",
            ),
        )
        if not accepted:
            print(f"job-{i}: rejected because queue is full")

    await queue.join()

    for task in workers:
        task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
