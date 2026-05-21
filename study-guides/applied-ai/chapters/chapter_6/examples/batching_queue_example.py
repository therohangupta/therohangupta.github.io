"""
Batching and queue sketch.

The key idea is that requests wait briefly so the worker can process a batch
instead of one request at a time. Larger batches improve throughput, but the
max wait time bounds user-visible queueing latency.
"""

import queue
import threading
import time
from dataclasses import dataclass, field


BATCH_SIZE = 4
MAX_BATCH_WAIT_SECONDS = 0.025
MAX_QUEUE_SIZE = 8


@dataclass
class Job:
    request_id: str
    prompt: str
    submitted_at: float = field(default_factory=time.monotonic)


@dataclass
class JobResult:
    request_id: str
    ok: bool
    output: str | None = None
    error: str | None = None
    queue_latency_ms: float = 0.0


def run_model_batch(jobs: list[Job]) -> list[str]:
    # Real inference would tokenize the prompts and run one batched model call.
    if any("fail" in job.prompt.lower() for job in jobs):
        raise RuntimeError("simulated batch failure")
    time.sleep(0.05)
    return [f"response for {job.request_id}" for job in jobs]


def collect_batch(work_queue: "queue.Queue[Job]") -> list[Job]:
    first_job = work_queue.get()
    batch = [first_job]
    deadline = time.monotonic() + MAX_BATCH_WAIT_SECONDS

    while len(batch) < BATCH_SIZE:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            batch.append(work_queue.get(timeout=remaining))
        except queue.Empty:
            break

    return batch


def submit(work_queue: "queue.Queue[Job]", job: Job) -> bool:
    try:
        work_queue.put_nowait(job)
        return True
    except queue.Full:
        print({"event": "queue.reject", "request_id": job.request_id, "reason": "backpressure"})
        return False


def worker(work_queue: "queue.Queue[Job]", results: dict[str, JobResult]) -> None:
    while True:
        batch = collect_batch(work_queue)
        try:
            outputs = run_model_batch(batch)
            for job, output in zip(batch, outputs):
                latency_ms = (time.monotonic() - job.submitted_at) * 1000
                results[job.request_id] = JobResult(job.request_id, True, output, queue_latency_ms=latency_ms)
                print({"request_id": job.request_id, "output": output, "queue_latency_ms": round(latency_ms, 1)})
        except Exception as exc:
            # Production systems choose between retrying, dropping, or splitting the batch.
            for job in batch:
                results[job.request_id] = JobResult(job.request_id, False, error=str(exc))
                print({"request_id": job.request_id, "error": str(exc)})
        finally:
            for _ in batch:
                work_queue.task_done()


if __name__ == "__main__":
    work_queue: "queue.Queue[Job]" = queue.Queue(maxsize=MAX_QUEUE_SIZE)
    results: dict[str, JobResult] = {}
    thread = threading.Thread(target=worker, args=(work_queue, results), daemon=True)
    thread.start()

    for i in range(10):
        submit(work_queue, Job(request_id=f"req-{i}", prompt="Explain continuous batching."))

    work_queue.join()
    print({"completed": len(results), "failed": sum(not result.ok for result in results.values())})
