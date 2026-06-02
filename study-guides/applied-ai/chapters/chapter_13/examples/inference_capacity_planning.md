# Inference Capacity Planning

Capacity planning for LLMs must be token-aware.

## Inputs

* QPS by route and tenant,
* input token distribution,
* output token distribution,
* latency SLOs,
* model size and precision,
* context length,
* measured prefill throughput,
* measured decode throughput,
* GPU memory,
* model load time,
* failover headroom.

## Separate Estimates

Prefill:

```text
input_tokens/sec needed vs measured prefill throughput
```

Decode:

```text
output_tokens/sec needed vs measured decode throughput
```

KV memory:

```text
active_sequences * sequence_length * layers * kv_heads * head_dim * 2 * bytes
```

## Common Mistake

Sizing only from average QPS hides the workload. A few long-context requests can dominate prefill time and KV memory even when request count is low.

## Output

A useful capacity plan states:

* how many GPUs are needed for normal load,
* how much headroom is kept for p99 and failover,
* which traffic is isolated into separate pools,
* what admission control does under overload,
* which metric triggers scale-out.
