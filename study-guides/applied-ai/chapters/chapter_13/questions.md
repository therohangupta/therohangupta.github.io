---
layout: page
title: "Chapter 13 Questions: ML Systems and Inference Engineering"
guide_type: questions
---

# Chapter 13 — Practice Questions

These questions are designed for applied AI system design interviews where infrastructure depth matters. Strong answers connect symptoms to bottlenecks, metrics, and tradeoffs.

---

## Question 1

**What is the core mental model for ML systems and inference engineering?**

### Sample Answer

ML systems engineering is bottleneck management. I would trace how model computation becomes hardware execution: request routing, queues, tokenization, batching, runtime execution, kernels, GPU memory, networking, and observability. The main question is which resource is scarce: compute, memory bandwidth, memory capacity, synchronization, network communication, scheduling, or developer complexity.

---

## Question 2

**A team says "GPU utilization is only 25%, so we need a faster model." How would you debug?**

### Sample Answer

Low GPU utilization does not automatically mean the model is too slow. I would split latency into queue time, tokenization, prefill, decode, tool calls, and response streaming. Then I would check batch size, active sequences, tokens/sec, CPU utilization, kernel launch count, memory bandwidth, and synchronization points. The GPU might be idle because requests are too small, the CPU is bottlenecked, batching is weak, or the system is waiting on network or tools.

---

## Question 3

**Why can memory movement dominate ML system performance?**

### Sample Answer

Modern accelerators can perform arithmetic very quickly, but moving data from HBM or CPU memory can be expensive. If each operation repeatedly loads and stores intermediates, arithmetic units may wait on memory. Optimizations like fusion, tiling, caching, quantization, and prefetching are valuable because they reduce bytes moved or increase reuse in fast memory.

---

## Question 4

**Explain kernel fusion in practical terms.**

### Sample Answer

Kernel fusion combines multiple operations into one kernel or compiled region so intermediate tensors do not have to be written to and read from global memory. It can reduce memory traffic, launch overhead, and synchronization. It can hurt if the fused kernel uses too many registers or too much shared memory, lowering occupancy.

---

## Question 5

**What is tiling, and why is it not just "splitting work into chunks"?**

### Sample Answer

Tiling restructures computation around the memory hierarchy. The goal is to load a block of data into fast memory and reuse it many times before evicting it. In matrix multiplication, tiling increases arithmetic intensity because each loaded value contributes to many outputs. It is about locality and reuse, not just dividing work.

---

## Question 6

**A PyTorch benchmark shows a GPU operation took 0.2 ms, but production traces suggest it is much slower. What might be wrong?**

### Sample Answer

CUDA execution is often asynchronous. The benchmark may have timed kernel launch, not completion. I would add `torch.cuda.synchronize()` around timing, warm up the model, avoid measuring one-off compilation or allocation, and benchmark representative shapes and batch sizes. I would also check hidden CPU-GPU sync points such as `.item()` or moving tensors to CPU.

---

## Question 7

**Why do tensor shape, stride, and contiguity matter?**

### Sample Answer

Shape describes the logical tensor. Stride and layout describe how it is stored physically. Non-contiguous tensors can trigger hidden copies or inefficient memory access. Hardware prefers predictable, coalesced access patterns, so a mathematically equivalent tensor layout can have different performance.

---

## Question 8

**What is the difference between prefill and decode in LLM inference?**

### Sample Answer

Prefill processes the input prompt and is parallel over input tokens, so it is often compute-heavy. Decode generates one token at a time and must use prior context, so it is sequential and often memory-bandwidth-bound. Long prompts mainly increase prefill cost, while long outputs mainly increase decode cost and KV cache pressure.

---

## Question 9

**Why is KV cache central to LLM serving?**

### Sample Answer

The KV cache stores attention keys and values from previous tokens so the model does not recompute them for every generated token. It improves decode efficiency but consumes memory proportional to active sequences, context length, layers, KV heads, head dimension, and precision. This makes concurrency and long context expensive.

---

## Question 10

**How does PagedAttention help serving variable-length LLM requests?**

### Sample Answer

PagedAttention stores KV cache in blocks rather than requiring each sequence to have one large contiguous allocation. That reduces fragmentation and makes it easier to manage variable-length sequences under continuous batching. It is a memory-management optimization for serving workloads.

---

## Question 11

**Why is continuous batching important for LLMs?**

### Sample Answer

LLM requests have different output lengths. In fixed batches, some sequences finish early while others continue, wasting capacity. Continuous batching lets requests enter and leave the active batch dynamically, improving throughput while the scheduler manages fairness, token budgets, and latency SLOs.

---

## Question 12

**When can prefix caching be unsafe?**

### Sample Answer

Prefix caching can be unsafe if the cache key ignores tenant, permissions, prompt version, model version, retrieved-document freshness, or safety policy. Reusing a prefix across the wrong boundary can leak context or apply stale instructions. Cache correctness is a security and product issue, not just a performance issue.

---

## Question 13

**What is speculative decoding, and when might it not help?**

### Sample Answer

Speculative decoding uses a cheaper draft model to propose tokens and a larger target model to verify them. It helps when the draft model is fast and the target accepts many proposed tokens. It may not help if acceptance rate is low, workloads are short, memory pressure is high, or the added complexity reduces batching efficiency.

---

## Question 14

**Explain FlashAttention using the memory hierarchy mental model.**

### Sample Answer

FlashAttention avoids materializing the full attention matrix in HBM. It processes attention in tiles that fit in fast memory, fuses parts of the computation, and may recompute cheap values to avoid storing large intermediates. It is fast because it moves less data, not only because it changes arithmetic.

---

## Question 15

**Why does quantization often speed up inference?**

### Sample Answer

Quantization reduces the number of bytes for weights and sometimes activations. That lowers memory bandwidth pressure, improves cache residency, reduces model memory, and may unlock faster hardware kernels. INT8 activation quantization usually needs calibration data to estimate production activation ranges. The quality tradeoff must be measured on relevant slices, because quantization can regress rare or precision-sensitive cases.

---

## Question 16

**What is the difference between PTQ and QAT?**

### Sample Answer

Post-training quantization converts a trained model using calibration data. It is simpler but can lose accuracy. Quantization-aware training simulates or incorporates quantization during training, which costs more but can better preserve quality.

---

## Question 17

**How would you explain ONNX in a deployment pipeline?**

### Sample Answer

ONNX is a portable intermediate representation for model graphs. It lets a model trained in one framework run in another runtime. The main risks are unsupported operators, dynamic shapes, version mismatches, shape inference problems, and numerical differences. I would validate exported outputs against the source model.

---

## Question 18

**What does TensorRT optimize?**

### Sample Answer

TensorRT optimizes model execution on NVIDIA GPUs. It parses a graph, fuses layers, chooses precision, selects kernels, plans memory, and builds an optimized engine. It is mostly about execution efficiency for a model on target hardware, not request scheduling or multi-tenant serving.

---

## Question 19

**Compare TensorRT and vLLM.**

### Sample Answer

TensorRT optimizes execution inside the GPU by compiling the model graph into efficient kernels and memory plans. vLLM optimizes serving around the GPU by managing requests, KV cache, continuous batching, and variable-length generation. They solve different layers of the inference stack.

---

## Question 20

**Why are dynamic shapes hard for compilers?**

### Sample Answer

Compilers optimize best when shapes are known or constrained. Dynamic prompt lengths, batch sizes, and output lengths limit specialization and can cause graph breaks or less efficient kernels. Shape profiles can help, but wide profiles trade performance for flexibility.

---

## Question 21

**A model runs fast in offline benchmarking but has bad p99 latency in production. What would you check?**

### Sample Answer

I would check queue time, prompt and output length distributions, active sequences, KV memory, cold starts, cache misses, tool calls, retries, and noisy tenants. Offline benchmarks may use fixed shapes and clean batches, while production has long-tail traffic and dynamic scheduling.

---

## Question 22

**Why is QPS alone insufficient for LLM capacity planning?**

### Sample Answer

LLM cost depends heavily on tokens, not just requests. A low-QPS workload with long prompts and long outputs can be more expensive than a high-QPS short-response workload. Capacity planning needs input token distribution, output token distribution, concurrency, context length, model size, GPU type, and latency SLO.

---

## Question 23

**How would you estimate KV cache pressure for a serving system?**

### Sample Answer

I would start with `batch * sequence_length * layers * kv_heads * head_dim * 2 * bytes`, then adjust for model architecture, precision, fragmentation, reserved memory, and batching behavior. The estimate helps explain why long context and concurrency can quickly become memory bottlenecks.

---

## Question 24

**How would you design autoscaling for an LLM serving platform?**

### Sample Answer

I would scale on token-aware signals: queue time, active sequences, input tokens/sec, output tokens/sec, GPU memory, p95/p99 latency, and rejection rate. CPU utilization alone is not enough. I would also account for model load time and keep warm capacity for failover and bursty tenants.

---

## Question 25

**A single tenant sends a few very long-context requests and everyone else slows down. What should the platform do?**

### Sample Answer

The platform needs token-aware admission control and tenant isolation. I would add per-tenant quotas for input tokens, output tokens, active sequences, and KV memory. Long-context traffic may go to a separate pool or lower-priority queue so it does not block short interactive requests.

---

## Question 26

**What is the difference between replication and model parallelism?**

### Sample Answer

Replication copies the whole model onto multiple workers to serve more independent requests. Model parallelism splits one model across devices so it can fit or run faster. Replication scales request throughput; parallelism changes how one model execution is distributed and adds communication overhead.

---

## Question 27

**What is DDP, and where can it bottleneck?**

### Sample Answer

Distributed data parallel training replicates the model across GPUs, gives each GPU different data, and synchronizes gradients after backward pass. The common synchronization primitive is all-reduce: it combines gradient values from workers and returns the averaged result to each worker. DDP can bottleneck on all-reduce communication, network topology, dataloader speed, or stragglers.

---

## Question 28

**Why do FSDP and ZeRO help train larger models?**

### Sample Answer

They shard parameters, gradients, and optimizer states across devices so each GPU stores less. The tradeoff is more communication and coordination. They are memory-saving strategies, not free speedups.

---

## Question 29

**A distributed training job scales poorly from 8 GPUs to 64 GPUs. What would you investigate?**

### Sample Answer

I would inspect compute/communication overlap, all-reduce time, network topology, batch size per GPU, dataloader throughput, stragglers, checkpointing, NCCL configuration, and GPU utilization. Poor scaling usually means the extra GPUs spend too much time waiting.

---

## Question 30

**What is NCCL, and why does it matter?**

### Sample Answer

NCCL is a communication library for GPU collectives like all-reduce, all-gather, reduce-scatter, and broadcast. It matters because distributed training and model parallel inference depend on fast GPU-to-GPU communication. NCCL hangs or topology problems can stall an entire job.

---

## Question 31

**A production LLM service starts throwing CUDA OOM errors after hours of stable operation. What are likely causes?**

### Sample Answer

I would check KV cache growth, long-context requests, memory fragmentation, leaks, too many active sequences, allocator behavior, and whether failed requests release memory. The system may have enough total memory but not enough contiguous usable memory for the next allocation.

---

## Question 32

**How would you debug slow decode specifically?**

### Sample Answer

I would check output token length, active sequences, KV cache reads, memory bandwidth, batch efficiency, quantization/kernel support, and GPU memory pressure. Decode is often memory-bound, so improving arithmetic alone may not help.

---

## Question 33

**How would you debug slow prefill specifically?**

### Sample Answer

I would inspect prompt length distribution, retrieval stuffing, chunked prefill behavior, attention implementation, batching, tokenizer cost, and whether long prompts are monopolizing the queue. Prefill is more parallel than decode but long prompts can still dominate latency.

---

## Question 34

**What metrics should every serious LLM serving platform expose?**

### Sample Answer

At minimum: request count, error rate, queue time, time to first token, end-to-end latency, input tokens/sec, output tokens/sec, prefill time, decode time, active sequences, KV memory, GPU utilization, GPU memory, batch size, model route, tenant, and rejection/admission-control events.

---

## Question 35

**How would you handle a model compilation release?**

### Sample Answer

I would treat the compiled engine as a release artifact. I would compare numerical outputs against the source model, benchmark representative shapes, test dynamic shape profiles, run regression evals, verify memory and latency, and roll it out behind staged traffic with rollback.

---

## Question 36

**What is the practical difference between online serving and batch inference?**

### Sample Answer

Online serving optimizes p95/p99 latency, streaming, fairness, admission control, and interactive reliability. Batch inference optimizes throughput, cost, checkpointability, and retryable jobs. The same model may need different batching, scheduling, and autoscaling strategies in each mode.

---

## Question 37

**How can observability help distinguish product problems from infrastructure problems?**

### Sample Answer

If traces include prompt length, output length, queue time, prefill, decode, retrieval/tool time, model route, tenant, and error type, we can tell whether users are waiting because of model behavior, external tools, routing, GPU pressure, or long prompts. Without token-level and stage-level metrics, everything looks like "the model is slow."

---

## Question 38

**How should security influence inference routing?**

### Sample Answer

Routing is not only a cost or latency decision. Sensitive tenants or regulated data may need private model pools, restricted providers, stricter logging, no cross-tenant cache reuse, or isolated workers. The router should enforce data classification and tenant policy before optimizing cost.

---

## Question 39

**What is a good first answer to "design a multi-tenant LLM inference platform"?**

### Sample Answer

I would start by clarifying QPS, token distributions, model mix, latency SLOs, tenancy, data sensitivity, and cost targets. Then I would design an API gateway, auth and tenant policy layer, token-aware router, queues, GPU worker pools, streaming gateway, observability, admission control, autoscaling, and rollback/fallback paths.

---

## Question 40

**What is the most important habit when discussing ML systems tools in interviews?**

### Sample Answer

Explain the bottleneck the tool addresses. Do not only name tools. For example, vLLM helps with KV cache management and continuous batching; TensorRT helps with graph optimization and GPU execution; FSDP helps with training memory; FlashAttention reduces attention memory traffic. Before choosing vLLM, TensorRT-LLM, Triton, or an external provider, ask about model size, latency SLO, token distributions, tenant isolation, hardware target, and data policy. Tie every tool to the resource it saves.

---

## Question 41

**What is arithmetic intensity, and why does it matter?**

### Sample Answer

Arithmetic intensity is the amount of computation performed per byte of data moved. High arithmetic intensity means hardware can spend more time doing useful math after loading data. Low arithmetic intensity means performance may be limited by memory bandwidth. Tiling, fusion, and caching often improve performance by increasing reuse and reducing bytes moved.

---

## Question 42

**How do you distinguish compute-bound and memory-bound workloads?**

### Sample Answer

A compute-bound workload is limited by arithmetic throughput, so tensor cores or ALUs are saturated. A memory-bound workload is limited by moving data, so compute units wait on HBM, cache, CPU memory, or network. I would use profiling metrics such as tensor core utilization, memory bandwidth, kernel duration, and stalls rather than guessing from model size.

---

## Question 43

**What are SMs, warps, and tensor cores?**

### Sample Answer

An SM, or streaming multiprocessor, schedules and executes groups of GPU threads. A warp is a group of threads that execute together. Tensor cores are specialized hardware units for matrix operations. These concepts matter because GPU performance depends on how well work is mapped to parallel execution and specialized matrix hardware.

---

## Question 44

**What is occupancy, and why is it not the only performance goal?**

### Sample Answer

Occupancy describes how many warps are active on an SM relative to what the hardware can support. Higher occupancy can hide memory latency, but a high-occupancy kernel can still be memory-bound or inefficient. Sometimes a lower-occupancy kernel with better data reuse or tensor core use is faster.

---

## Question 45

**Why does memory coalescing matter?**

### Sample Answer

Memory coalescing means nearby GPU threads access nearby memory locations, allowing efficient memory transactions. Poor access patterns waste bandwidth because the hardware may need more transactions to fetch the same useful data. Tensor layout, strides, and access patterns can therefore change performance even when the mathematical operation is the same.
