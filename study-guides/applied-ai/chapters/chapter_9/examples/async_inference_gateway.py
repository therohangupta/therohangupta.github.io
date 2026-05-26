"""
Async inference gateway sketch.

This example shows the shape of an async Python service that fans out to
retrieval and model calls without blocking the event loop. The model and
retrieval functions are fake, but the concurrency controls are real.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass


MAX_CONCURRENT_REQUESTS = 50
REQUEST_TIMEOUT_SECONDS = 8.0

request_slots = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


@dataclass(frozen=True)
class InferenceRequest:
    request_id: str
    tenant_id: str
    user_id: str
    prompt: str
    max_tokens: int = 256


@dataclass(frozen=True)
class InferenceResponse:
    request_id: str
    text: str
    elapsed_ms: int
    cache_hit: bool


async def retrieve_context(request: InferenceRequest) -> list[str]:
    """Pretend to call a vector DB or document service."""
    await asyncio.sleep(0.08)
    return [
        f"tenant={request.tenant_id}",
        "Only answer from retrieved context when possible.",
    ]


async def call_model_api(prompt: str, *, max_tokens: int) -> str:
    """Pretend to call an external model provider with an async client."""
    await asyncio.sleep(0.18)
    return f"model_response(max_tokens={max_tokens}): {prompt[:80]}..."


def validate_request(request: InferenceRequest) -> None:
    if not request.prompt.strip():
        raise ValueError("prompt must not be empty")
    if request.max_tokens <= 0 or request.max_tokens > 2048:
        raise ValueError("max_tokens is outside allowed range")


def build_prompt(request: InferenceRequest, context: list[str]) -> str:
    context_block = "\n".join(f"- {item}" for item in context)
    return f"Context:\n{context_block}\n\nUser:\n{request.prompt}\n\nAssistant:"


async def handle_request(request: InferenceRequest) -> InferenceResponse:
    """Handle one request with admission control, timeout, and tracing fields."""
    started = time.perf_counter()

    async with request_slots:
        validate_request(request)

        async def run() -> InferenceResponse:
            context = await retrieve_context(request)
            prompt = build_prompt(request, context)
            text = await call_model_api(prompt, max_tokens=request.max_tokens)
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            return InferenceResponse(
                request_id=request.request_id,
                text=text,
                elapsed_ms=elapsed_ms,
                cache_hit=False,
            )

        return await asyncio.wait_for(run(), timeout=REQUEST_TIMEOUT_SECONDS)


async def main() -> None:
    requests = [
        InferenceRequest(
            request_id=f"req-{i}",
            tenant_id="tenant-a",
            user_id=f"user-{i % 3}",
            prompt="Summarize the latest account notes.",
        )
        for i in range(5)
    ]
    responses = await asyncio.gather(*(handle_request(req) for req in requests))
    for response in responses:
        print(response)


if __name__ == "__main__":
    asyncio.run(main())
