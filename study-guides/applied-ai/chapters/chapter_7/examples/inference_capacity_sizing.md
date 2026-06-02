# Inference Capacity Sizing Exercise

## Workload

* 20 requests/sec peak interactive traffic
* p95 input length: 6,000 tokens
* p95 output length: 800 tokens
* target p95 time to first token: 1.5 seconds
* target p99 end-to-end latency: 12 seconds
* one long-context tenant can send 40,000-token prompts

## Sizing Steps

1. Estimate prefill token load from input tokens/sec.
2. Estimate decode token load from output tokens/sec.
3. Reserve KV cache memory for active sequences.
4. Add headroom for p99, failover, and model loading.
5. Split long-context traffic into a separate pool if it threatens short interactive traffic.

## Decision

Do not size on QPS alone. Size on token distributions, active sequences, queue time, model load time, and memory pressure.
