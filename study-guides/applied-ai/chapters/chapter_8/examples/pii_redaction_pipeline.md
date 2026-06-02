# PII Redaction Pipeline

Learning loops often start from traces. Those traces may contain private data. A redaction pipeline decides what can be stored, labeled, evaluated, or trained on.

## Pipeline

```text
raw trace
  -> classify sensitivity
  -> detect PII and secrets
  -> redact or tokenize sensitive spans
  -> preserve task-relevant structure
  -> assign retention and training eligibility
  -> write redacted record
  -> store lineage to raw record under restricted access
```

## Example Raw Trace

```text
User: My card 4242 4242 4242 4242 was charged twice. Email me at jane@example.com.
Agent: I can help. Your invoice inv_123 shows...
```

## Redacted Training Candidate

```json
{
  "trace_id": "tr_01",
  "text": "User reports duplicate card charge and asks for email follow-up. Agent inspects invoice.",
  "entities": {
    "payment_card": "[REDACTED_CARD]",
    "email": "[REDACTED_EMAIL]",
    "invoice_id": "[TOKENIZED_INVOICE_ID]"
  },
  "tenant_id": "acme",
  "retention_class": "support_training_candidate",
  "training_eligible": false,
  "needs_review": true,
  "redaction_policy_version": "pii-redaction-2026-05"
}
```

## Eligibility Rules

| Condition | Action |
| --------- | ------ |
| Contains payment card | redact and require review |
| Contains secrets or credentials | exclude from training |
| User opted out | exclude from training |
| Tenant forbids training use | exclude from training |
| Trace from known-bad model version | quarantine |
| Confirmed product failure | prefer eval/regression case |

## Key Lesson

PII redaction is not the same as training approval. A trace can be redacted but still ineligible because of consent, tenant policy, contamination, or safety risk.
