# Audit Log Schema

Audit logs make AI system behavior reconstructable after a security incident, user complaint, or failed rollout.

## Agent Action Audit Event

```json
{
  "event_type": "agent_tool_call",
  "trace_id": "tr_2026_05_26_001",
  "timestamp": "2026-05-26T16:00:00Z",
  "tenant_id": "acme",
  "user_id": "u_123",
  "session_id": "sess_456",
  "model": {
    "provider": "internal",
    "model_id": "support-agent",
    "model_version": "2026-05-01"
  },
  "prompt": {
    "template_id": "support_agent_v8",
    "template_version": "8.3.1"
  },
  "retrieval": {
    "query": "refund annual plan duplicate charge",
    "acl_policy_version": "acl_42",
    "source_chunk_ids": ["chunk_1", "chunk_2"]
  },
  "tool_call": {
    "tool": "issue_refund",
    "arguments_hash": "sha256:...",
    "resource_id": "invoice_789",
    "risk_class": "financial_write"
  },
  "authorization": {
    "decision": "approved_after_human_review",
    "policy_version": "refund_policy_7",
    "approver_user_id": "manager_55"
  },
  "result": {
    "status": "success",
    "external_operation_id": "refund_abc"
  }
}
```

## Fields Worth Keeping

| Field | Why It Matters |
| ----- | -------------- |
| `trace_id` | joins model call, retrieval, tool call, approval, and response |
| `tenant_id` / `user_id` | investigates scope and access |
| model and prompt version | reproduces behavior |
| source chunk IDs | checks grounding and leakage |
| policy version | explains authorization decision |
| approver ID | proves human approval happened |
| arguments hash | preserves integrity without over-logging sensitive values |
| result status | supports rollback and incident response |

## Logging Rule

Log enough to reconstruct decisions, but do not store unnecessary secrets or raw private content. Auditability and data minimization must both be designed.
