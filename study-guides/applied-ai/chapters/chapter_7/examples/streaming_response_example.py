"""
Streaming response sketch.

Streaming lowers time to first token and supports cancellation, but it also
means errors can happen after the client has already received partial output.
"""

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass(frozen=True)
class StreamEvent:
    kind: str
    payload: str


async def model_token_stream(prompt: str) -> AsyncIterator[str]:
    # Real serving would stream tokens from vLLM, TGI, or a model API.
    for token in ["Production", " ML", " systems", " need", " backpressure", "."]:
        await asyncio.sleep(0.05)
        yield token


async def stream_response(prompt: str, timeout_seconds: float = 2.0) -> AsyncIterator[StreamEvent]:
    started = asyncio.get_running_loop().time()
    emitted_tokens = 0
    first_token_ms: float | None = None

    try:
        async for token in model_token_stream(prompt):
            now = asyncio.get_running_loop().time()
            if now - started > timeout_seconds:
                yield StreamEvent("error", "stream stopped: timeout")
                return

            if first_token_ms is None:
                first_token_ms = (now - started) * 1000
                print({"metric": "stream.first_token_ms", "value": round(first_token_ms, 1)})

            emitted_tokens += 1
            yield StreamEvent("token", token)
            await asyncio.sleep(0)  # lets cancellation/backpressure propagate
    except asyncio.CancelledError:
        print({"event": "stream.cancelled", "tokens": emitted_tokens})
        raise
    except Exception as exc:
        yield StreamEvent("error", f"upstream stream failed: {exc}")
    finally:
        print({"event": "stream.complete", "tokens": emitted_tokens})


async def main() -> None:
    chunks: list[str] = []
    async for event in stream_response("Explain backpressure."):
        if event.kind == "token":
            chunks.append(event.payload)
        print({"event": event.kind, "payload": event.payload})

    print("".join(chunks))


if __name__ == "__main__":
    asyncio.run(main())
