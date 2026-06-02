# OpenTelemetry AI Trace Schema

This sketch shows the fields that make an AI request debuggable across model calls, retrieval, tools, evals, and incidents.

## Trace Shape

```json
{
  "trace_id": "tr_001",
  "span_id": "span_model_001",
  "parent_span_id": "span_request_001",
  "service.name": "support-agent",
  "tenant_id": "acme",
  "user_id_hash": "sha256:...",
  "request.route": "/support/answer",
  "ai.model.provider": "internal",
  "ai.model.name": "support-model",
  "ai.model.version": "2026-05-01",
  "ai.prompt.template": "support_rag_v9",
  "ai.prompt.version": "9.2.0",
  "ai.input_tokens": 4820,
  "ai.output_tokens": 318,
  "ai.retrieval.index_version": "support_docs_2026_05_20",
  "ai.retrieval.source_ids": ["doc_123", "doc_456"],
  "ai.tool.name": "fetch_ticket",
  "ai.tool.risk_class": "read_only",
  "ai.policy.version": "tool_policy_7",
  "ai.eval.case_id": null,
  "latency.ms": 1820,
  "error.type": null
}
```

## Why These Fields Matter

| Field Group | Debugs |
| ----------- | ------ |
| model and prompt version | behavior changes after release |
| token counts | latency and cost spikes |
| retrieval source IDs | grounding, stale docs, leakage |
| tenant and user scope | access-control incidents |
| tool and policy version | unsafe or unauthorized actions |
| eval case ID | offline reproduction |
| latency and error fields | production reliability |

## Design Notes

Do not log raw prompts or private documents by default. Store source IDs, hashes, redacted snippets, and policy metadata unless raw content is explicitly needed and access-controlled.

The goal is to reconstruct decisions without turning observability into a data leak.
