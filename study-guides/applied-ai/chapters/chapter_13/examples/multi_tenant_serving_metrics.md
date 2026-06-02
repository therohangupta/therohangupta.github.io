# Multi-Tenant Serving Metrics

A multi-tenant inference platform needs token-aware observability. Request counts alone hide the real workload.

## Request-Level Fields

```json
{
  "request_id": "req_7f2",
  "tenant_id": "acme",
  "model": "llama-3.1-70b",
  "priority": "interactive",
  "input_tokens": 18420,
  "output_tokens": 720,
  "time_to_first_token_ms": 1650,
  "end_to_end_latency_ms": 9400,
  "queue_ms": 410,
  "prefill_ms": 890,
  "decode_ms": 7900,
  "route": "gpu-pool-long-context",
  "cache_hit": false,
  "admission_decision": "allowed"
}
```

## Worker-Level Metrics

* active sequences,
* batch size,
* input tokens/sec,
* output tokens/sec,
* GPU utilization,
* GPU memory used,
* KV cache blocks used,
* queue depth,
* model load time,
* cold starts,
* OOM events.

## Tenant-Level Metrics

* request count,
* input tokens,
* output tokens,
* rejected tokens,
* average and p99 queue time,
* quota usage,
* cost attribution,
* noisy-neighbor events.

## Why These Metrics Matter

One tenant with a few long-context requests can consume more GPU memory and scheduler time than hundreds of short requests. A serious platform must measure tokens, active sequences, and KV memory, not only QPS.

## Alerts

Good alerts:

* p99 queue time exceeds SLO for interactive traffic,
* KV cache memory above 85% for five minutes,
* output tokens/sec drops while request count stays flat,
* one tenant exceeds 40% of active sequence memory,
* cold starts exceed configured budget.

Weak alerts:

* CPU utilization only,
* request count only,
* average latency only.
