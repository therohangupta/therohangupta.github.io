# Scalable AI Backend Design

This example sketches a Python backend for AI inference at production scale.

## Architecture

```text
client
  -> API gateway
  -> auth / quota / validation
  -> request router
  -> cache lookup
  -> retrieval service
  -> bounded queue
  -> inference workers
  -> model provider or GPU runtime
  -> output validation
  -> streaming response
  -> traces / metrics / audit logs
```

## API Layer Responsibilities

- Authenticate user and tenant.
- Validate request size and schema.
- Enforce quotas and rate limits.
- Assign request ID.
- Choose route or model tier.
- Apply deadline.
- Start streaming response if needed.
- Return clear errors when overloaded.

The API layer should not own GPU-specific scheduling logic.

## Worker Responsibilities

- Pull jobs from bounded queues.
- Batch compatible requests.
- Call model provider or local runtime.
- Apply retries only when safe.
- Validate model outputs.
- Emit stage-level metrics.
- Respect cancellation and deadlines.

Workers should be horizontally scalable and restartable.

## Cache Strategy

Possible caches:

- embedding cache,
- retrieval cache,
- prompt-prefix cache,
- response cache,
- metadata cache.

Cache keys must include correctness dimensions:

- tenant,
- permission scope,
- prompt version,
- model version,
- retrieval index version,
- input hash.

Wrong cache keys can leak data or serve stale behavior.

## Queue Strategy

Use bounded queues for backpressure.

Track:

- queue length,
- oldest job age,
- retry count,
- dead-letter count,
- worker utilization,
- per-tenant queue share.

Reject early when deadlines cannot be met.

## Observability

Every request trace should include:

- request ID,
- tenant,
- route,
- prompt version,
- model version,
- retrieval IDs,
- cache hit or miss,
- queue wait,
- model latency,
- token counts,
- cost estimate,
- validation result,
- fallback route.

## Failure Modes

### Provider slowdown

Mitigation:

- circuit breaker,
- fallback model,
- queue limits,
- retry backoff with jitter.

### Slow retrieval

Mitigation:

- metadata indexes,
- retrieval timeout,
- cached results,
- top-k limits,
- degraded no-retrieval path if safe.

### Worker OOM

Mitigation:

- batch size limits,
- request size limits,
- memory profiling,
- worker recycling,
- model route constraints.

### Cache leak

Mitigation:

- TTL,
- max size,
- versioned keys,
- tenant-aware keys,
- cache metrics.

## Interview Framing

> I would separate API orchestration from inference execution. The API layer handles auth, validation, routing, quotas, deadlines, and streaming. Workers handle batching, model calls, validation, and runtime metrics. Bounded queues, caches, circuit breakers, and observability make the system scalable and debuggable.
