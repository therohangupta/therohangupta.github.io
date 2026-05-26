# ML Data Pipeline Sketch

This example shows a practical data pipeline for an AI product that learns from support conversations.

## Pipeline

```text
raw support events
  -> schema validation
  -> PII filtering
  -> cleaned event table
  -> feature generation
  -> training dataset
  -> offline evaluation set
  -> model or prompt update
  -> production monitoring
```

## Raw Events

Raw events should be immutable.

Examples:

- user message,
- assistant response,
- retrieved document IDs,
- tool calls,
- human edits,
- escalation outcome,
- satisfaction signal,
- timestamps,
- tenant and permission metadata.

Do not overwrite raw events when feature logic changes. Recompute derived layers instead.

## Schema Validation

Validate at ingestion:

- required fields,
- field types,
- enum values,
- timestamp format,
- tenant ID,
- event version,
- payload size.

Bad data should go to a quarantine or dead-letter path, not silently enter training.

## Feature Generation

Examples:

- request length,
- response length,
- retrieval count,
- citation count,
- tool success rate,
- escalation label,
- human edit distance,
- policy category,
- model route,
- prompt version.

Feature definitions should be versioned. Training and serving should use the same definitions when possible.

## Backfills

Backfills are needed when:

- a feature definition changes,
- a bug is fixed,
- labels arrive late,
- historical data needs reprocessing,
- a new model needs a new dataset.

Rules:

- write idempotently,
- version outputs,
- throttle reads from OLTP sources,
- record lineage,
- keep old datasets for reproducibility.

## Streaming Layer

Streaming can power:

- live drift alerts,
- near-real-time usage dashboards,
- abuse detection,
- online features,
- human-review queues.

Streaming systems should define:

- event-time semantics,
- late event handling,
- deduplication keys,
- retry policy,
- dead-letter queue,
- schema evolution rules.

## Training-Serving Skew Checks

Check that:

- online and offline feature code match,
- timestamps are point-in-time correct,
- default values are consistent,
- null behavior is consistent,
- categorical mappings are versioned,
- feature freshness is monitored.

## Data Quality Dashboard

Monitor:

- row counts,
- null rates,
- duplicate event rate,
- schema failure rate,
- feature distribution drift,
- label delay,
- data freshness,
- failed backfills,
- training-serving skew.

## Interview Framing

> I would design the pipeline with immutable raw data, schema validation, versioned feature definitions, lineage, backfills, and quality checks. The goal is to prevent silent data corruption from becoming a model-quality issue.
