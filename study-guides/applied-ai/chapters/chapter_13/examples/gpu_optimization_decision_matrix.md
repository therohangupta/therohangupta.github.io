# GPU Optimization Decision Matrix

Use this matrix when an interviewer asks how to make inference faster or cheaper. The key is to connect an optimization to the bottleneck it addresses.

| Symptom | Likely Bottleneck | Candidate Fixes | Tradeoff |
| ------- | ----------------- | --------------- | -------- |
| many small kernels | launch overhead | fusion, graph capture, compilation | less flexibility, possible graph breaks |
| high HBM bandwidth | memory movement | fusion, tiling, quantization, FlashAttention | precision or implementation complexity |
| model barely fits | memory capacity | quantization, tensor parallelism, offload, smaller model | quality, communication, latency |
| low GPU utilization | scheduling or CPU bottleneck | larger batches, continuous batching, tokenizer scaling, fewer sync points | p99 latency can worsen |
| long prompts cause p99 spikes | prefill pressure | token budgets, chunked prefill, prompt compression, separate pools | possible quality loss |
| long outputs slow everyone | decode pressure | token limits, scheduling policy, faster kernels, speculative decoding | fairness and complexity |
| distributed training scales poorly | communication | overlap comms, tune batch size, topology-aware placement, FSDP/ZeRO tuning | memory and convergence tradeoffs |
| compiled engine underperforms | poor shape/profile match | narrower profiles, representative benchmarking, operator review | more engines to manage |

## How to Use It

1. Identify the bottleneck from traces and profiles.
2. Pick the least invasive optimization that targets that bottleneck.
3. Benchmark on representative traffic, not only synthetic fixed shapes.
4. Check quality, safety, and cost regressions.

## Example Answer

If decode is slow because the workload is memory-bandwidth-bound, I would not start by adding a bigger GPU blindly. I would inspect KV cache pressure, active sequences, output length distribution, batching efficiency, and kernel support. Quantization or better serving scheduling may help more than pure compute.
