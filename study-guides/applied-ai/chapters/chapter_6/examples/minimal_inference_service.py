"""
Minimal inference service sketch.

This is not a production server. It shows the shape of a synchronous API layer
around a model client: validate input, enforce limits, call inference, record
basic metrics, and return a structured response.
"""

import time
from dataclasses import dataclass


MAX_PROMPT_CHARS = 8_000
MAX_OUTPUT_TOKENS = 512


@dataclass
class InferenceRequest:
    request_id: str
    tenant_id: str
    prompt: str
    max_tokens: int = 256


@dataclass(frozen=True)
class InferenceResponse:
    request_id: str
    model: str
    text: str
    fallback_used: bool = False


class ModelClient:
    def generate(self, prompt: str, max_tokens: int) -> str:
        # In a real system this might call vLLM, TGI, TensorRT-LLM, or a vendor API.
        return f"generated response for: {prompt[:40]}"


class Metrics:
    def record(self, name: str, value: float, **tags: str) -> None:
        print({"metric": name, "value": value, "tags": tags})


def validate_request(request: InferenceRequest) -> None:
    if not request.prompt.strip():
        raise ValueError("prompt is required")
    if len(request.prompt) > MAX_PROMPT_CHARS:
        raise ValueError("prompt is too large")
    if request.max_tokens > MAX_OUTPUT_TOKENS:
        raise ValueError("max_tokens exceeds service limit")


def handle_inference(request: InferenceRequest, model: ModelClient, metrics: Metrics) -> dict:
    started = time.monotonic()
    validate_request(request)

    try:
        output = model.generate(request.prompt, request.max_tokens)
        metrics.record("inference.success", 1, tenant=request.tenant_id)
        return InferenceResponse(request.request_id, "example-model-v1", output).__dict__
    except TimeoutError:
        metrics.record("inference.timeout", 1, tenant=request.tenant_id)
        return InferenceResponse(
            request_id=request.request_id,
            model="fallback-template",
            text="The model is temporarily unavailable. Please try again shortly.",
            fallback_used=True,
        ).__dict__
    except Exception:
        metrics.record("inference.error", 1, tenant=request.tenant_id)
        raise
    finally:
        elapsed_ms = (time.monotonic() - started) * 1000
        metrics.record("inference.latency_ms", elapsed_ms, tenant=request.tenant_id)


if __name__ == "__main__":
    response = handle_inference(
        InferenceRequest(
            request_id="req-123",
            tenant_id="tenant-a",
            prompt="Summarize the production ML serving path.",
        ),
        model=ModelClient(),
        metrics=Metrics(),
    )
    print(response)
