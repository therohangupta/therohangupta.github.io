# Systems Bottleneck Map

Use this map to turn tool names into engineering reasons.

| Symptom | Scarce Resource | Useful Questions | Candidate Tools or Patterns |
| ------- | --------------- | ---------------- | --------------------------- |
| GPU idle while requests wait | scheduling or CPU preprocessing | Is work reaching the GPU in large enough batches? | tokenizer scaling, continuous batching, async queues |
| high memory bandwidth | data movement | Are intermediates written to HBM too often? | fusion, tiling, FlashAttention, quantization |
| CUDA OOM at long context | memory capacity | Is KV cache or activation memory dominating? | PagedAttention, shorter contexts, GQA/MQA, quantization |
| poor distributed training scaling | communication | Are workers waiting on collectives? | overlap comms, tune batch size, topology placement |
| compiled model is slower | shape/profile mismatch | Does benchmark traffic match production shapes? | narrower profiles, representative load tests |
| p99 latency spikes | queueing and tail load | Which stage changed for p99 requests? | token budgets, admission control, pool isolation |

## Interview Move

Do not say only "use a faster runtime." Say:

> I would first identify whether this is compute, memory bandwidth, memory capacity, communication, scheduling, or queueing. Then I would pick the optimization that targets that bottleneck and validate it on representative traffic.
