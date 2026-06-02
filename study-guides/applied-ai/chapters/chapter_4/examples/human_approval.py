"""
Human approval / escalation sketch.

The agent can prepare a side effect, but execution is blocked until a human
approves the plan and expected impact.
"""

from dataclasses import dataclass
from enum import Enum


class ApprovalStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ProposedAction:
    description: str
    tool: str
    args: dict[str, str]
    risk: str
    approval_status: ApprovalStatus


def propose_action(user_goal: str) -> ProposedAction:
    """Placeholder for an LLM that drafts an action from user intent."""
    return ProposedAction(
        description=f"Send a refund approval email for: {user_goal}",
        tool="send_email",
        args={"recipient": "customer@example.com", "template": "refund_approved"},
        risk="external_side_effect",
        approval_status=ApprovalStatus.PENDING,
    )


def approve(action: ProposedAction, approved: bool) -> ProposedAction:
    action.approval_status = (
        ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
    )
    return action


def execute(action: ProposedAction) -> str:
    if action.risk != "low" and action.approval_status != ApprovalStatus.APPROVED:
        return "Blocked: human approval required"
    return f"Executed {action.tool} with {action.args}"


if __name__ == "__main__":
    proposed = propose_action("refund customer after duplicate charge")
    print(execute(proposed))

    approved = approve(proposed, approved=True)
    print(execute(approved))
