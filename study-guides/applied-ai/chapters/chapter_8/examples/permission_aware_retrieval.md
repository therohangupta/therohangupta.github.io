# Permission-Aware Retrieval

Permission-aware retrieval enforces access control before documents enter ranking, prompts, logs, or model context.

## Unsafe Pattern

```text
query all documents
  -> vector search over global index
  -> send top chunks to model
  -> ask model not to reveal unauthorized content
```

This is unsafe because unauthorized content has already influenced the model and may appear in traces.

## Safer Pattern

```text
request
  -> authenticate user
  -> load tenant, groups, roles
  -> filter candidate documents by ACL
  -> retrieve and rank only allowed chunks
  -> assemble context
  -> generate answer with citations
  -> log source IDs and policy version
```

## Retrieval Record

| Field | Example | Purpose |
| ----- | ------- | ------- |
| `user_id` | `u_123` | ties retrieval to identity |
| `tenant_id` | `acme` | prevents cross-tenant access |
| `groups` | `support_l2`, `billing` | permission filtering |
| `query` | `refund policy for annual plans` | reproducibility |
| `acl_policy_version` | `acl_2026_05_20` | auditability |
| `candidate_doc_count` | `1842` | debugging recall |
| `allowed_doc_count` | `231` | debugging permission filters |
| `returned_chunks` | chunk IDs and source docs | citation and incident review |

## Design Choices

| Design | Good For | Risk |
| ------ | -------- | ---- |
| Per-tenant index | strong isolation, simpler mental model | many indexes, harder global operations |
| Shared index with mandatory ACL filters | scale and operational simplicity | filter bugs can become leaks |
| Hybrid indexes | large enterprise deployments | more complex consistency model |

## Tests

Every permission-aware retriever should have tests for:

* user can retrieve allowed document,
* user cannot retrieve denied document,
* permission change removes document from results,
* deleted document disappears from index,
* tenant A query cannot retrieve tenant B document,
* cached response does not bypass ACLs,
* generated answer only cites allowed sources.
