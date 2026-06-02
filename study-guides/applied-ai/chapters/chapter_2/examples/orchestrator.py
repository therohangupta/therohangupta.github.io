"""Small orchestrator sketch.

An LLM workflow is usually a controlled sequence of deterministic and
probabilistic steps: classify, retrieve, generate, validate, and fallback.
Production systems replace the toy functions here with model calls, retrieval
services, structured-output parsers, tracing, and rollout-controlled policies.
"""

from dataclasses import dataclass, field


@dataclass
class WorkflowState:
    user_text: str
    route: str = "general"
    route_confidence: float = 0.0
    context: str | None = None
    answer: str | None = None
    fallbacks: list[str] = field(default_factory=list)


def classify_request(user_text: str) -> tuple[str, float]:
    if "order" in user_text.lower():
        return "order_status", 0.92
    if "refund" in user_text.lower():
        return "refund_policy", 0.63
    return "general", 0.76


def retrieve_context(route: str, confidence: float) -> str | None:
    if confidence < 0.7:
        return None

    contexts = {
        "order_status": "Order status requires an order_id and a lookup_order tool call.",
        "refund_policy": "Refunds after 30 days require human review.",
        "general": "General support answer should be concise.",
    }
    return contexts[route]


def generate_answer(user_text: str, context: str) -> str:
    # Production: call the model through a gateway with prompt/model versions,
    # request IDs, token budgets, and structured output validation.
    return f"Using context: {context} Answer request: {user_text}"


def validate_answer(answer: str, state: WorkflowState) -> str | None:
    if len(answer) > 500:
        return "answer too long"
    if state.route == "refund_policy" and "human review" not in answer:
        return "refund answer missing escalation language"
    return None


def handle_request(user_text: str) -> WorkflowState:
    state = WorkflowState(user_text=user_text)
    state.route, state.route_confidence = classify_request(user_text)

    state.context = retrieve_context(state.route, state.route_confidence)
    if state.context is None:
        state.fallbacks.append("low route confidence: ask clarifying question")
        state.answer = "Can you clarify whether this is about an order, refund, or something else?"
        return state

    state.answer = generate_answer(user_text, state.context)
    validation_error = validate_answer(state.answer, state)
    if validation_error:
        state.fallbacks.append(validation_error)
        state.answer = "I need to route this to a human for review."
    return state


if __name__ == "__main__":
    print(handle_request("Where is my order A123?"))
    print(handle_request("Can I get a refund after 45 days?"))
