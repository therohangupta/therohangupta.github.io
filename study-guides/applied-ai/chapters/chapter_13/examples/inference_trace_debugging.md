# Inference Trace Debugging

This example shows how to debug p99 latency by splitting a request into stages instead of treating "the model is slow" as one bucket.

## Incident

An enterprise support chatbot usually returns the first token in under 900 ms. After enabling long-context retrieval, p99 time to first token rises to 6.8 seconds.

## Trace Snapshot

| Stage | p50 | p95 | p99 | Notes |
| ----- | --- | --- | --- | ----- |
| auth and tenant policy | 18 ms | 42 ms | 55 ms | normal |
| query rewrite | 90 ms | 170 ms | 240 ms | normal |
| retrieval | 140 ms | 480 ms | 850 ms | elevated but not dominant |
| context assembly | 35 ms | 80 ms | 130 ms | normal |
| queue wait | 120 ms | 1.9 s | 3.2 s | high |
| prefill | 260 ms | 1.4 s | 2.9 s | high |
| first decode step | 45 ms | 120 ms | 210 ms | normal |

## Token Distribution

| Slice | p50 Input Tokens | p95 Input Tokens | p99 Input Tokens |
| ----- | ---------------- | ---------------- | ---------------- |
| before launch | 2,400 | 7,800 | 12,600 |
| after launch | 5,900 | 28,000 | 61,000 |

The system is not mainly decode-bound. It is queue-bound and prefill-bound because retrieval stuffed too much context into prompts.

## Diagnosis

The new retriever returned more documents than the serving pool was sized for. A few long-context requests held scheduler capacity and increased queue time for everyone.

## Fixes

* Add prompt-token budgets by tenant and request class.
* Add retrieval compression before model prefill.
* Use chunked prefill so very long prompts do not monopolize the batch.
* Route long-context requests to a separate pool.
* Add an admission-control event when a request is truncated or rejected.

## Metrics to Add

* input tokens by tenant,
* output tokens by tenant,
* queue time by model pool,
* prefill time by token bucket,
* active sequences,
* KV cache memory,
* rejected or truncated requests.

## Interview Framing

Do not say only "add more GPUs." First show which stage changed, which tokens changed, and which resource became scarce. Then decide whether the fix is more capacity, better scheduling, better retrieval, context compression, or policy limits.
