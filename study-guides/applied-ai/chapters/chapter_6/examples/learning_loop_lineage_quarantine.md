# Learning Loop Data Lineage and Quarantine

This artifact shows how a production trace becomes an eval case, training candidate, or excluded record.

## Trace Record

```json
{
  "trace_id": "tr_001",
  "model_version": "support_model_2026_05",
  "prompt_version": "support_prompt_v12",
  "retrieval_index": "support_docs_2026_05_20",
  "tenant_id": "acme",
  "feedback": "thumbs_down",
  "outcome": "ticket_reopened",
  "contains_pii": true,
  "policy_incident": false
}
```

## Eligibility Decision

| Check | Result | Action |
| ----- | ------ | ------ |
| Tenant allows training use | yes | continue |
| User opted out | no | continue |
| Contains PII | yes | redact before labeling |
| From known-bad policy | no | continue |
| Confirmed failure | yes | add to eval candidate set |

## Dataset Routing

```text
raw trace
  -> redaction pipeline
  -> failure classifier
  -> eval candidate: yes
  -> training candidate: maybe after review
```

The same trace should not automatically enter both training and eval. If it becomes a held-out regression case, protect it from future training leakage.

## Quarantine Case

If the trace came from a bad prompt version:

```json
{
  "trace_id": "tr_002",
  "prompt_version": "support_prompt_v13_bad",
  "quarantine_reason": "prompt caused unsafe refund advice",
  "training_eligible": false,
  "eval_candidate": true
}
```

## Rule of Thumb

Bad production behavior should first become evidence. Only after privacy review, labeling, and split decisions should it become training data.
