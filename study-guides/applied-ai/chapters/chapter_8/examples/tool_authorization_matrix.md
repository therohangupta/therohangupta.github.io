# Tool Authorization Matrix

An AI agent should not decide tool authority by itself. The tool layer should authorize each action against identity, tenant, resource, action type, and risk.

## Example Matrix

| Tool | Action Type | Required Role | Approval | Notes |
| ---- | ----------- | ------------- | -------- | ----- |
| `search_docs` | read | authenticated user | no | filters by tenant and document ACL |
| `fetch_ticket` | read | support agent | no | ticket must belong to user's assigned queue |
| `draft_reply` | low-risk write | support agent | no | creates draft only, does not send |
| `send_reply` | external write | support agent | yes for regulated categories | reviewer sees final text and citations |
| `issue_refund` | financial write | billing agent | yes above threshold | amount and account must pass policy checks |
| `change_plan` | account mutation | account admin | yes | requires resource owner or delegated admin |
| `delete_user_data` | destructive write | privacy admin | yes | requires deletion workflow and audit entry |
| `run_shell` | code execution | developer role | depends on command | sandboxed, allowlisted, no secrets |

## Authorization Request

```json
{
  "trace_id": "tr_01",
  "user_id": "u_123",
  "tenant_id": "acme",
  "tool": "issue_refund",
  "action": "create_refund",
  "resource_id": "invoice_789",
  "arguments": {
    "amount_usd": 125,
    "reason": "duplicate charge"
  },
  "model_version": "assistant-2026-05-01",
  "policy_version": "refund-policy-7"
}
```

## Policy Decision

```json
{
  "decision": "needs_human_approval",
  "risk": "financial_write",
  "reason": "refund amount exceeds auto-approval threshold",
  "required_approver_role": "billing_manager"
}
```

## Interview Point

The model can propose `issue_refund`, but the authorization service decides whether the action can execute. A valid tool call can still be unauthorized.
