"""
ReAct-style loop sketch.

This example shows the shape of a support/research agent runtime: a bounded
reasoning/action/observation loop with tool boundaries and failure containment.
Production systems replace choose_next_action with a model/tool-selection call
and execute tools through permissioned, observable adapters.
"""

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class AgentState:
    goal: str
    scratchpad: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    steps: int = 0


@dataclass(frozen=True)
class ToolCall:
    name: str
    args: dict[str, Any]


@dataclass(frozen=True)
class Decision:
    thought: str
    tool_call: ToolCall


TOOLS: dict[str, Callable[[dict[str, Any]], str]] = {
    "search_docs": lambda args: f"Search results for {args['query']}",
    "lookup_ticket": lambda args: f"Ticket {args['ticket_id']} is open",
}


def choose_next_action(state: AgentState) -> Decision:
    """Placeholder for an LLM tool-selection call."""
    if not state.observations:
        return Decision("I need evidence before answering.", ToolCall("search_docs", {"query": state.goal}))
    return Decision("I have enough evidence to answer.", ToolCall("finish", {"answer": f"Answer based on: {state.observations[-1]}"}))


def run_agent(goal: str, max_steps: int = 4) -> str:
    state = AgentState(goal=goal)

    while state.steps < max_steps:
        decision = choose_next_action(state)
        state.scratchpad.append(decision.thought)
        state.steps += 1

        if decision.tool_call.name == "finish":
            return str(decision.tool_call.args["answer"])

        if decision.tool_call.name not in TOOLS:
            return f"Stopped: unknown tool {decision.tool_call.name}"

        try:
            observation = TOOLS[decision.tool_call.name](decision.tool_call.args)
        except Exception as exc:
            return f"Stopped: tool failed {decision.tool_call.name}: {exc}"
        state.observations.append(observation)

    return "Stopped: step budget exhausted"


if __name__ == "__main__":
    print(run_agent("How should we handle a billing support ticket?"))
