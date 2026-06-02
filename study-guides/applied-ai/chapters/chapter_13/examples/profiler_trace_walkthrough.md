# Profiler Trace Walkthrough

## Symptom

p99 latency increased after a retrieval prompt change.

| Stage | Before p99 | After p99 | Diagnosis |
| ----- | ---------- | --------- | --------- |
| tokenization | 80 ms | 120 ms | small increase |
| queue wait | 500 ms | 4.8 s | scheduler pressure |
| prefill | 900 ms | 6.2 s | prompt length growth |
| decode | 2.1 s | 2.4 s | not the main issue |
| tool calls | 300 ms | 310 ms | unchanged |

## Reading

The bottleneck is prefill and queueing, not decode. The fix is prompt/token budget, retrieval compression, chunked prefill, or long-context pool isolation.

## Metrics to Add

* input token distribution,
* queue time by pool,
* prefill time by token bucket,
* active sequences,
* KV memory pressure.
