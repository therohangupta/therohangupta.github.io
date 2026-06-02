# RAG Trace Debugging Artifact

This artifact shows what to inspect when a RAG answer is wrong.

## Trace Summary

```json
{
  "trace_id": "rag_001",
  "user_id": "u_123",
  "tenant_id": "acme",
  "query": "Can annual plans be refunded after renewal?",
  "rewritten_query": "annual plan renewal refund policy",
  "retriever_version": "hybrid_v4",
  "index_version": "support_docs_2026_05_20",
  "prompt_version": "rag_answer_v9",
  "model_version": "answer_model_2026_05"
}
```

## Retrieved Chunks

| Rank | Chunk | Source | Freshness | Allowed | Note |
| ---- | ----- | ------ | --------- | ------- | ---- |
| 1 | `refund_policy_old_12` | legacy policy PDF | stale | yes | says refunds allowed within 60 days |
| 2 | `billing_faq_44` | help center | fresh | yes | says contact support |
| 3 | `refund_policy_new_03` | current policy | fresh | yes | says refunds allowed within 30 days |

## Generated Answer

```text
Annual plans can be refunded within 60 days of renewal.
```

## Failure Classification

The model answered from the top-ranked stale chunk even though the current policy was retrieved lower.

This is a retrieval/ranking/freshness failure, not primarily a generation failure.

## Debug Questions

* Did the source-of-truth mark the old document as deprecated?
* Did ingestion preserve effective dates?
* Does ranking include freshness or policy version metadata?
* Did the prompt tell the model to prefer current policy over legacy documents?
* Does the eval set include policy-version conflicts?

## Likely Fixes

* add effective-date metadata,
* downrank deprecated sources,
* remove stale chunks from the active index,
* add a regression case for conflicting policies,
* require citations to current policy for refund answers.
