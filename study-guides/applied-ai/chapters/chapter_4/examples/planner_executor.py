"""
Planner/executor sketch.

The planner proposes structured steps. The validator blocks unsafe or irrelevant
steps before the executor performs any side effects.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Step:
    name: str
    tool: str
    args: dict[str, str]
    requires_approval: bool = False


@dataclass
class ExecutionState:
    completed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    paused_for_approval: str | None = None


@dataclass(frozen=True)
class StepResult:
    step_name: str
    status: str
    message: str


def plan(goal: str) -> list[Step]:
    """Placeholder for a structured LLM planning call."""
    return [
        Step("gather_context", "search_docs", {"query": goal}),
        Step("draft_response", "draft_message", {"tone": "concise"}),
        Step("send_response", "send_email", {"recipient": "user"}, True),
    ]


def validate_plan(steps: list[Step], allowed_tools: set[str]) -> None:
    for step in steps:
        if step.tool not in allowed_tools:
            raise ValueError(f"Tool is not allowed: {step.tool}")

    side_effects = [step for step in steps if step.tool.startswith("send_")]
    if side_effects and not all(step.requires_approval for step in side_effects):
        raise ValueError("Side-effecting steps require approval")


def execute_step(step: Step) -> StepResult:
    if step.requires_approval:
        return StepResult(step.name, "paused", f"Paused for human approval before {step.name}")
    if step.tool == "draft_message" and not step.args.get("tone"):
        return StepResult(step.name, "failed", "Missing tone argument")
    return StepResult(step.name, "completed", f"Executed {step.tool} with {step.args}")


def run(goal: str) -> ExecutionState:
    steps = plan(goal)
    validate_plan(steps, allowed_tools={"search_docs", "draft_message", "send_email"})

    state = ExecutionState()
    for step in steps:
        result = execute_step(step)
        if result.status == "completed":
            state.completed.append(result.step_name)
        elif result.status == "paused":
            state.paused_for_approval = result.step_name
            break
        else:
            state.failed.append(result.step_name)
            break

    return state


if __name__ == "__main__":
    print(run("Resolve a customer refund request"))
