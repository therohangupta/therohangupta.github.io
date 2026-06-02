"""End-to-end AI request pipeline sketch.

This example represents the runtime skeleton behind a production AI feature:
route the request, build context, call a model, validate the response, and
record operational metadata. It is intentionally small, but shaped like a real
service boundary with typed state, budgets, fallbacks, and observability hooks.
"""

from dataclasses import dataclass, field
from enum import Enum
from time import perf_counter


class Route(str, Enum):
    GENERAL = "general"
    GROUNDED_QA = "grounded_qa"
    HUMAN_REVIEW = "human_review"


@dataclass(frozen=True)
class Request:
    request_id: str
    user_text: str
    tenant_id: str
    max_context_tokens: int = 120


@dataclass
class PipelineState:
    request: Request
    route: Route = Route.GENERAL
    context: list[str] = field(default_factory=list)
    answer: str | None = None
    fallback_reason: str | None = None
    metrics: dict[str, float] = field(default_factory=dict)


def classify_route(request: Request) -> Route:
    if len(request.user_text.strip()) < 5:
        return Route.HUMAN_REVIEW
    if any(term in request.user_text.lower() for term in ("policy", "refund", "contract")):
        return Route.GROUNDED_QA
    return Route.GENERAL


def retrieve_context(request: Request, route: Route) -> list[str]:
    if route != Route.GROUNDED_QA:
        return []

    # Production: call retrieval with ACL filters, source IDs, freshness, and
    # reranking. This toy keeps the interface visible without a vector DB.
    candidates = [
        "Refund policy: refunds after 30 days require manager approval.",
        "Contract policy: customer-specific terms override default policy.",
    ]
    budget = request.max_context_tokens
    selected: list[str] = []
    used_tokens = 0
    for chunk in candidates:
        chunk_tokens = len(chunk.split())
        if used_tokens + chunk_tokens > budget:
            break
        selected.append(chunk)
        used_tokens += chunk_tokens
    return selected


def generate_response(request: Request, context: list[str]) -> str:
    if context:
        return f"Based on policy context: {context[0]} Answer: {request.user_text}"
    return f"General answer: {request.user_text}"


def validate_response(state: PipelineState) -> str | None:
    if not state.answer:
        return "empty_answer"
    if state.route == Route.GROUNDED_QA and not state.context:
        return "missing_grounding"
    if state.route == Route.GROUNDED_QA and "Based on policy context" not in state.answer:
        return "ungrounded_answer"
    return None


def handle_request(request: Request) -> PipelineState:
    started = perf_counter()
    state = PipelineState(request=request)

    state.route = classify_route(request)
    if state.route == Route.HUMAN_REVIEW:
        state.fallback_reason = "ambiguous_or_too_short"
        state.answer = "I need a bit more detail before I can safely help."
        state.metrics["latency_ms"] = (perf_counter() - started) * 1000
        return state

    state.context = retrieve_context(request, state.route)
    state.answer = generate_response(request, state.context)

    validation_error = validate_response(state)
    if validation_error:
        state.fallback_reason = validation_error
        state.answer = "I need to route this to a human reviewer."

    state.metrics["latency_ms"] = (perf_counter() - started) * 1000
    state.metrics["context_chunks"] = float(len(state.context))
    return state


if __name__ == "__main__":
    result = handle_request(
        Request(
            request_id="req_123",
            user_text="Can this customer get a refund after 45 days?",
            tenant_id="tenant_a",
        )
    )
    print(result)
