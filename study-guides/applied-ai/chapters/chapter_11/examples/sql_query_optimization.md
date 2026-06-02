# SQL Query Optimization Walkthrough

This example shows how to reason about a slow query in an AI product.

Scenario: an internal knowledge assistant stores document chunks and retrieves metadata before building a prompt.

## Slow Query

```sql
SELECT
  c.chunk_id,
  c.document_id,
  c.heading,
  c.body,
  d.source_url,
  d.updated_at
FROM document_chunks c
JOIN documents d ON d.document_id = c.document_id
WHERE d.tenant_id = 'tenant-a'
  AND d.visibility = 'internal'
  AND c.embedding_model = 'embed-v3'
ORDER BY d.updated_at DESC
LIMIT 20;
```

## Bad Symptoms

- Sequential scan over `documents`.
- Sequential scan over `document_chunks`.
- Large join before filtering by tenant.
- Sort over too many rows before `LIMIT`.
- Query is on the request path, so it hurts time to first token.

## Questions To Ask

1. Is `tenant_id` selective?
2. Is `visibility` selective?
3. Are chunks filtered by `embedding_model` often?
4. Does the query always order by `updated_at`?
5. Is this OLTP request-path traffic or analytics traffic?

## Better Indexes

```sql
CREATE INDEX idx_documents_tenant_visibility_updated
ON documents (tenant_id, visibility, updated_at DESC, document_id);

CREATE INDEX idx_chunks_document_embedding
ON document_chunks (document_id, embedding_model);
```

These indexes match the access pattern:

- filter documents by tenant and visibility,
- preserve ordering by `updated_at`,
- join chunks by document,
- filter chunks by embedding model.

## Query Shape

Sometimes it is better to identify candidate documents first, then join chunks.

```sql
WITH candidate_documents AS (
  SELECT document_id, source_url, updated_at
  FROM documents
  WHERE tenant_id = 'tenant-a'
    AND visibility = 'internal'
  ORDER BY updated_at DESC
  LIMIT 100
)
SELECT
  c.chunk_id,
  c.document_id,
  c.heading,
  c.body,
  d.source_url,
  d.updated_at
FROM candidate_documents d
JOIN document_chunks c ON c.document_id = d.document_id
WHERE c.embedding_model = 'embed-v3'
LIMIT 20;
```

## Materialized View Option

If the same metadata query is run constantly and slight staleness is acceptable:

```sql
CREATE MATERIALIZED VIEW recent_internal_chunks AS
SELECT
  d.tenant_id,
  d.visibility,
  d.updated_at,
  d.source_url,
  c.chunk_id,
  c.document_id,
  c.heading,
  c.embedding_model
FROM documents d
JOIN document_chunks c ON c.document_id = d.document_id;
```

Tradeoff:

- Faster reads.
- More storage.
- Refresh complexity.
- Staleness risk.

## Interview Framing

Do not say: "I would add an index."

Say:

> I would inspect the query plan to identify whether the bottleneck is scan, join, sort, or cardinality estimation. Then I would add indexes that match the filter, join, and order pattern, consider rewriting the query to reduce intermediate rows, and only use materialization if the read is frequent and staleness is acceptable.
