"""Minimal tool-calling loop.

The model proposes a tool call, the host application executes it, and the
result becomes new context for the next model step. Production systems add
permission checks, argument sanitization, timeout enforcement, idempotency
keys, and structured tracing around this loop.
"""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ToolSpec:
    fn: Callable[..., Any]
    required_args: frozenset[str]
    side_effect: bool = False


def lookup_order(order_id: str) -> dict:
    fake_db = {"A123": {"status": "shipped", "eta": "Friday"}}
    return fake_db.get(order_id, {"status": "unknown", "eta": None})


def format_user_message(status: str, eta: str | None) -> dict:
    if status == "unknown":
        return {"message": "I could not find that order. Please check the order ID."}
    return {"message": f"Your order is {status}. Estimated arrival: {eta}."}


TOOLS: dict[str, ToolSpec] = {
    "lookup_order": ToolSpec(fn=lookup_order, required_args=frozenset({"order_id"})),
    "format_user_message": ToolSpec(fn=format_user_message, required_args=frozenset({"status", "eta"})),
}


def execute_tool_call(call: dict) -> dict:
    name = call["name"]
    args = call.get("arguments", {})
    if name not in TOOLS:
        return {"error": f"unknown tool: {name}"}

    spec = TOOLS[name]
    missing = spec.required_args - set(args)
    if missing:
        return {"error": f"missing arguments for {name}: {sorted(missing)}"}

    # Production: check permissions, enforce timeout, log trace span.
    return {"result": spec.fn(**args)}


def next_model_call(observation: dict) -> dict | None:
    """Tiny stand-in for the next model step after observing tool output."""
    result = observation.get("result")
    if not isinstance(result, dict) or "status" not in result:
        return None
    return {
        "name": "format_user_message",
        "arguments": {"status": result["status"], "eta": result["eta"]},
    }


if __name__ == "__main__":
    calls = [{"name": "lookup_order", "arguments": {"order_id": "A123"}}]

    while calls:
        call = calls.pop(0)
        observation = execute_tool_call(call)
        print({"tool": call["name"], "observation": observation})
        followup = next_model_call(observation)
        if followup:
            calls.append(followup)
