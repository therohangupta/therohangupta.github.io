"""
Explicit state-machine agent sketch.

This models a support workflow automation agent. It is less flexible than a
free-form loop, but allowed transitions are easy to inspect, test, and secure.
"""

from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    NEW = "new"
    NEEDS_CONTEXT = "needs_context"
    DRAFTING = "drafting"
    NEEDS_APPROVAL = "needs_approval"
    DONE = "done"
    FAILED = "failed"


@dataclass(frozen=True)
class AgentTask:
    task_id: str
    customer_tier: str
    status: Status = Status.NEW


class Event(str, Enum):
    START = "start"
    CONTEXT_FOUND = "context_found"
    DRAFT_READY = "draft_ready"
    APPROVED = "approved"
    ERROR = "error"


ALLOWED_TRANSITIONS = {
    Status.NEW: {Status.NEEDS_CONTEXT},
    Status.NEEDS_CONTEXT: {Status.DRAFTING, Status.FAILED},
    Status.DRAFTING: {Status.NEEDS_APPROVAL, Status.FAILED},
    Status.NEEDS_APPROVAL: {Status.DONE, Status.DRAFTING},
    Status.DONE: set(),
    Status.FAILED: set(),
}


def transition(current: Status, next_status: Status) -> Status:
    if next_status not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"Invalid transition: {current} -> {next_status}")
    return next_status


def classify_next_state(status: Status, event: Event) -> Status:
    """A real system might use rules plus an LLM classifier here."""
    if status == Status.NEW:
        return Status.NEEDS_CONTEXT
    if status == Status.NEEDS_CONTEXT and event == Event.CONTEXT_FOUND:
        return Status.DRAFTING
    if status == Status.DRAFTING and event == Event.DRAFT_READY:
        return Status.NEEDS_APPROVAL
    if status == Status.NEEDS_APPROVAL and event == Event.APPROVED:
        return Status.DONE
    if event == Event.ERROR:
        return Status.FAILED
    return status


def run(task: AgentTask, events: list[Event]) -> AgentTask:
    status = task.status
    for event in events:
        next_status = classify_next_state(status, event)
        if next_status != status:
            status = transition(status, next_status)
    return AgentTask(task.task_id, task.customer_tier, status)


if __name__ == "__main__":
    print(run(AgentTask("ticket-123", "enterprise"), [Event.START, Event.CONTEXT_FOUND, Event.DRAFT_READY, Event.APPROVED]))
