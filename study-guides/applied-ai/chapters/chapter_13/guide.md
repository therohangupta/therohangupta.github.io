---
layout: page
title: "Chapter 13: ML Systems and Inference Engineering"
guide_type: chapter
---

# Chapter 13 — ML Systems and Inference Engineering

This chapter explains how model computation becomes hardware execution under production constraints.

Earlier chapters explain model behavior, prompting, retrieval, agents, evaluation, learning loops, serving, software fundamentals, and security. Chapter 13 goes one layer lower. It asks what happens inside the runtime, compiler, scheduler, GPU, memory hierarchy, and distributed system when an AI product serves real traffic.

The interview angle is:

* can you connect user-visible symptoms to runtime and hardware causes?
* can you reason about tokens, memory, batching, queues, kernels, and GPUs?
* can you explain what tools like PyTorch, JAX, ONNX, TensorRT, vLLM, Ray, and Kubernetes are actually optimizing?
* can you estimate capacity and debug p95/p99 latency, low utilization, CUDA OOMs, and distributed training failures?

Study loop:

1. Read the guide for the mental model.
2. Use the [questions](questions.html) to practice interview phrasing.
3. Use the [examples](examples.html) as concrete artifacts for debugging, capacity planning, and release discussions.
4. Finish with the [multi-tenant inference capstone](../../capstones/multi_tenant_llm_inference_platform.html) to compose the ideas into one system.

---

## Table of Contents

- TOC
{:toc}

---

# 1. The Core Mental Model

ML systems engineering is the path from model computation to hardware execution under production constraints.

The request path is not just:

```text
request -> model -> response
```

The real path is closer to:

```text
request
  -> tokenizer
  -> scheduler / queue
  -> runtime
  -> kernels
  -> GPU memory
  -> networking / storage / observability
  -> response
```

Training optimizes parameters. Inference optimizes latency, throughput, memory, cost, reliability, and isolation. At scale, raw FLOPs are only one part of the story. Memory movement, synchronization, scheduling, network communication, and idle hardware often dominate.

The core question is:

```text
Which bottleneck is this system actually fighting?
```

A strong interview answer does not stop at "use vLLM" or "use TensorRT." It explains why those systems help.

> I would not debug an ML system only at the API layer. I would break the path into request scheduling, batching, prefill, decode, memory allocation, kernel execution, GPU utilization, and downstream serving behavior.

---

# 2. Bottleneck Map for ML Systems Frameworks

Every major ML systems tool is a strategy for managing one or more bottlenecks:

* memory movement,
* memory capacity,
* synchronization,
* network communication,
* idle hardware,
* compilation overhead,
* developer complexity.

## 2.1 The Main Bottlenecks

| Resource | Typical Problem |
| -------- | --------------- |
| Compute | ALUs or tensor cores are idle |
| Memory bandwidth | too many bytes move between HBM and compute |
| Memory capacity | model weights, activations, or KV cache do not fit |
| Latency | requests wait on queues, tools, network, prefill, or decode |
| Network | distributed workers spend too long communicating |
| Parallelism | synchronization limits useful work |
| Scheduling | available hardware is not matched to the right work |
| Developer complexity | the optimized path is too hard to write by hand |

This framing is useful because it turns tool names into reasons.

## 2.2 Framework Mental Models

| Framework | Mental Model | Main Bottleneck Managed |
| --------- | ------------ | ----------------------- |
| PyTorch | dynamic tensor computation with eager execution | research and development friction |
| TensorFlow | graph-first optimized execution | deployable graph execution |
| JAX | transform pure Python functions into compilable mathematical programs | compiler-driven optimization and parallelization |
| ONNX | portable intermediate representation for ML graphs | framework/runtime portability |
| TensorRT | hardware-optimized NVIDIA execution plan | GPU execution inefficiency |
| vLLM | KV-cache-aware LLM serving engine | memory fragmentation and scheduling inefficiency |
| Kubernetes | declarative distributed operating system for containers | multi-machine orchestration |
| Ray | distributed Python tasks, actors, and objects | distributed execution complexity |

Important distinction:

```text
TensorRT optimizes execution inside the GPU.
vLLM optimizes serving around the GPU.
```

TensorRT focuses on graph optimization, fusion, precision, kernel selection, and memory planning for a model. vLLM focuses on dynamic requests, KV cache management, continuous batching, and throughput under real LLM workloads.

## 2.3 The Systems Lens

When you see a new ML systems tool, ask:

1. What resource is scarce?
2. What data is moving?
3. What synchronization is happening?
4. What hardware is idle?
5. What can be fused, tiled, cached, batched, pipelined, quantized, sharded, prefetched, or scheduled differently?

That checklist works for GPU kernels, vector databases, distributed training, inference gateways, and production agents.

---

# 3. Data Movement Patterns

A surprising amount of systems optimization reduces to:

```text
avoid moving data more than necessary
```

Modern hardware can do enormous arithmetic. Feeding the arithmetic units is often the harder problem.

## 3.1 Kernel Fusion

Kernel fusion combines multiple operations into one kernel or compiled region.

Naive path:

```text
HBM -> compute -> HBM -> compute -> HBM
```

Fused path:

```text
HBM -> compute -> compute -> compute -> HBM
```

The goal is to avoid writing intermediate tensors to slow global GPU memory and reading them back. Intermediates may stay in registers, shared memory, or cache instead.

Fusion helps by:

* reducing HBM/global memory traffic,
* reducing kernel launches,
* reducing synchronization barriers,
* giving compilers more room to reorder and optimize.

Fusion can hurt if it increases register pressure or shared-memory use so much that occupancy drops. The tradeoff is:

```text
less memory traffic and fewer launches
vs
more complex kernels and lower parallelism
```

## 3.2 Tiling, Blocking, and Chunking

Tiling is not merely splitting work into chunks. It is restructuring computation around the memory hierarchy.

The mental model:

```text
load once, reuse many times
```

In matrix multiplication, the same elements of `A` and `B` are reused across many output cells. A tiled implementation loads blocks into fast memory, reuses them many times, then moves to the next tile.

This increases arithmetic intensity:

```text
more FLOPs per byte moved
```

On GPUs, tiling tries to maximize reuse in registers and shared memory before touching HBM again.

## 3.3 Caching and Prefetching

Caching keeps frequently used data physically closer to compute. Prefetching moves data before compute stalls waiting for it.

Examples:

* CPU caches,
* GPU L2 cache,
* prefix caches in LLM serving,
* Redis and CDN edge caches,
* database page caches.

Caching helps only when the cache key respects correctness boundaries. In AI systems, cache keys may need tenant, permissions, prompt version, model version, source freshness, and safety policy.

## 3.4 Quantization as Data Movement Reduction

Quantization reduces representation size so memory bandwidth and memory capacity stop dominating.

Lower precision can mean:

* smaller weights,
* smaller activations,
* lower bandwidth pressure,
* better cache residency,
* more efficient hardware kernels.

Quantization is not magic integer math. Its biggest practical benefit is often moving fewer bytes.

## 3.5 Batching, Pipelining, Vectorization, and Sharding

Common systems patterns:

| Pattern | Core Goal |
| ------- | --------- |
| Batching | amortize overhead across many items |
| Pipelining | overlap stages so hardware waits less |
| Vectorization | apply one instruction to many values |
| Sharding | reduce per-node memory or communication pressure |
| Prefetching | hide latency before compute stalls |
| Fusion | avoid writing intermediates |
| Tiling | maximize reuse before eviction |

Most are memory, communication, or scheduling optimizations more than pure compute optimizations.

---

# 4. Hardware and GPU Foundations

## 4.1 CPU vs GPU

A CPU is optimized for low-latency execution of complex control flow. It has fewer powerful cores, large caches, branch prediction, and strong single-thread performance.

A GPU is optimized for throughput. It has many simpler execution lanes and is designed to run huge numbers of similar operations in parallel.

This is why tensor workloads map well to GPUs: large matrix operations expose lots of parallel work.

## 4.2 GPU Execution Model

Useful vocabulary:

* **thread:** one execution lane,
* **warp:** a group of threads executing together, often 32 on NVIDIA GPUs,
* **block:** a group of threads that can share fast shared memory,
* **SM:** streaming multiprocessor that schedules and executes warps,
* **tensor core:** specialized matrix-multiply hardware,
* **kernel:** a GPU function launched over many threads.

You do not need to write CUDA in every applied AI job, but you should know what these terms explain: occupancy, memory access, launch overhead, and utilization.

## 4.3 GPU Memory Hierarchy

From fastest and smallest to slowest and largest:

```text
registers
  -> shared memory / SRAM
  -> L1 / L2 cache
  -> HBM / global memory / VRAM
  -> CPU RAM
  -> disk / network storage
```

Kernel fusion tries to keep intermediates in registers or shared memory. Tiling tries to reuse data in shared memory before fetching more from HBM. Quantization reduces how many bytes need to move through the hierarchy.

## 4.4 Bottleneck Types

| Bottleneck | Symptom |
| ---------- | ------- |
| Compute-bound | arithmetic units saturated |
| Memory-bound | waiting on HBM/global memory |
| Launch-bound | many small kernels and high overhead |
| Communication-bound | distributed workers wait on network |
| Scheduling-bound | hardware idle despite queued work |

LLM decode is often memory-bound because each token needs model weights and KV cache reads while generating only one next token per sequence.

## 4.5 Occupancy, Warp Divergence, and Memory Coalescing

**Occupancy** measures how many warps can be active on an SM. Higher occupancy can hide memory latency, but it is not always the final goal. A kernel can have high occupancy and still be memory-bound.

**Warp divergence** happens when threads in a warp take different branches. The hardware may serialize paths, reducing effective parallelism.

**Memory coalescing** means neighboring threads access neighboring memory, allowing efficient memory transactions. Poor access patterns waste bandwidth.

## 4.6 Profiling Mental Model

When profiling GPU workloads, inspect:

* GPU utilization,
* memory bandwidth,
* tensor core utilization,
* kernel launch count,
* kernel duration,
* CPU-GPU synchronization,
* HBM usage,
* active sequences and tokens/sec for LLM serving.

Do not trust one number. Low utilization can come from CPU bottlenecks, tiny batches, sync points, memory stalls, or scheduling issues.

---

# 5. PyTorch Runtime and CUDA Execution

## 5.1 Tensor Storage, Shape, Stride, Dtype, and Device

A tensor is not only values. It also has:

* storage,
* shape,
* stride,
* dtype,
* device,
* layout.

Two tensors can share storage but view it differently. This matters for performance and memory use.

## 5.2 Contiguous vs Non-Contiguous Tensors

A contiguous tensor is laid out in memory in the order operations usually expect. A non-contiguous tensor may be a view with unusual strides.

Some operations can handle non-contiguous tensors. Others trigger hidden copies. Hidden copies can increase memory use and latency.

Interview framing:

> Tensor layout matters because hardware wants predictable, coalesced memory access. A shape that looks fine mathematically may be inefficient physically.

## 5.3 CUDA Asynchronous Execution

Many PyTorch CUDA operations are asynchronous. Python may enqueue work and continue before the GPU has finished.

This means naive timing can lie:

```text
start timer
launch GPU op
stop timer
```

That may measure launch time, not execution time. Use synchronization when benchmarking.

Synchronization points include:

* `torch.cuda.synchronize()`,
* `.item()`,
* moving tensors from GPU to CPU,
* some logging or printing paths.

## 5.4 Streams and Overlap

CUDA streams allow independent sequences of GPU work. They can help overlap:

* compute,
* memory transfers,
* preprocessing,
* communication.

Streams are powerful but easy to misuse. The main mental model is pipelining: keep hardware doing useful work instead of waiting.

## 5.5 Memory Allocation and Fragmentation

GPU allocation is expensive, so frameworks use caching allocators. PyTorch may keep GPU memory reserved even after tensors are freed so future allocations are faster.

Long-running inference servers can suffer from fragmentation:

* many sequence lengths,
* changing KV cache sizes,
* dynamic batching,
* varying model routes,
* temporary buffers.

Fragmentation can cause OOM even when total free memory looks large.

## 5.6 Mixed Precision and Checkpointing

Mixed precision uses lower-precision formats such as FP16 or BF16 to reduce memory and improve hardware throughput.

Gradient checkpointing trades compute for memory. Instead of storing every activation during training, the system recomputes some activations during backward pass.

The recurring pattern:

```text
spend extra compute to reduce memory pressure
```

---

# 6. LLM Inference Internals

## 6.1 Why LLM Inference Is Different

Traditional inference often performs one forward pass and returns one result.

LLM generation is autoregressive:

```text
token -> token -> token
```

Each generated token depends on previous tokens. This makes output length, KV cache, batching, and scheduling central to serving.

## 6.2 Prefill vs Decode

**Prefill** processes the input prompt. It is parallel over input tokens and often compute-heavy.

**Decode** generates one token at a time. It is sequential and often memory-bandwidth-bound.

This distinction explains many production symptoms:

* long prompts increase prefill time,
* long outputs increase decode time,
* many active sequences increase KV cache pressure,
* streaming improves perceived latency but not total compute.

## 6.3 KV Cache

The KV cache stores attention keys and values from previous tokens so decode does not recompute the full history each step.

Rough shape intuition:

```text
batch * sequence_length * layers * kv_heads * head_dim * 2 * bytes
```

The factor of `2` is for keys and values.

MHA, MQA, GQA, and MLA can be understood partly as strategies for reducing KV memory without losing too much quality.

The serving problem:

```text
KV cache grows with users, context length, output length, layers, and precision.
```

## 6.4 PagedAttention

PagedAttention applies virtual-memory-style ideas to KV cache management.

Instead of requiring large contiguous KV regions for every sequence, the system stores KV cache in blocks and maps sequences to blocks.

This helps:

* reduce fragmentation,
* support variable-length sequences,
* enable continuous batching,
* improve memory utilization.

## 6.5 Continuous Batching

Fixed batching wastes work because LLM requests have different output lengths. Some finish early while others continue decoding.

Continuous batching lets requests enter and leave the active batch dynamically.

The scheduler must manage:

* prefill work,
* decode work,
* active sequences,
* token budgets,
* fairness,
* KV memory,
* latency SLOs.

## 6.6 Prefix Caching and Chunked Prefill

Prefix caching reuses computation for shared prompt prefixes. It helps when many requests share system prompts, templates, or retrieved context.

Chunked prefill splits long prompts into smaller pieces so huge prefill requests do not monopolize the system.

Both are scheduling and memory-locality tools. They are not automatically safe: cache keys must respect tenant, permissions, prompt version, and model version.

## 6.7 Speculative Decoding

Speculative decoding uses a smaller draft model to propose tokens and a larger target model to verify them.

It helps when:

* the draft model is much cheaper,
* acceptance rate is high,
* verification can be batched efficiently.

It can hurt when acceptance rate is low or memory/runtime complexity overwhelms the benefit.

## 6.8 FlashAttention as Tiling, Fusion, and Recomputation

Classic attention can materialize a large attention matrix. That is expensive because the matrix may be too large to keep in fast memory.

FlashAttention uses the mental model:

```text
recompute cheap things to avoid storing gigantic intermediates
```

It processes attention in tiles, streams blocks through fast memory, and avoids writing the full attention matrix to HBM.

FlashAttention combines:

* tiling: process blocks that fit in fast memory,
* fusion: avoid intermediate writes,
* recomputation: spend extra compute to reduce memory traffic.

This is the broader lesson: the fastest algorithm is often the one that moves less data, not the one with the fewest mathematical operations.

---

# 7. Quantization and Precision

## 7.1 Precision Types

Common formats:

| Format | Notes |
| ------ | ----- |
| FP32 | high precision, expensive |
| TF32 | NVIDIA format for faster matmul with FP32-like range |
| FP16 | fast on tensor cores, smaller range |
| BF16 | wider range than FP16, common for training |
| FP8 | emerging for high-performance training/inference |
| INT8 | common inference quantization target |
| INT4 | aggressive weight compression |

## 7.2 Why Quantization Helps

Quantization helps because it reduces bytes moved and stored.

Benefits:

* smaller model weights,
* lower memory bandwidth pressure,
* larger effective cache capacity,
* faster kernels when hardware supports them,
* lower serving cost.

## 7.3 PTQ vs QAT

**Post-training quantization** converts a trained model using calibration data. It is simpler but can hurt accuracy.

**Quantization-aware training** trains with quantization effects included. It is more expensive but can preserve quality better.

## 7.4 Weight-Only vs Activation Quantization

Weight-only quantization compresses model weights but may keep activations higher precision. It is often easier to deploy.

Activation quantization can reduce more bandwidth but requires more careful calibration because activation distributions depend on inputs.

## 7.5 Failure Modes

Quantization can fail because of:

* outlier channels,
* bad calibration data,
* unsupported kernels,
* hardware mismatch,
* accuracy regressions on rare slices,
* small batches where overhead dominates,
* precision-sensitive tasks.

The right question is not "is quantization faster?" It is "does this quantization improve cost/latency at acceptable quality loss on the target workload?"

---

# 8. Model Compilation and Runtime Optimization

## 8.1 Eager Execution vs Graph Execution

Eager execution runs operations as the program reaches them. It is flexible and easy to debug.

Graph execution captures computation as a graph, then optimizes the graph before running it. It can be faster but less flexible.

## 8.2 Computation Graphs and IRs

A graph represents:

* operators,
* tensors,
* shapes,
* dtypes,
* dependencies,
* constants.

An intermediate representation, or IR, gives compilers a standard form to optimize.

## 8.3 ONNX

ONNX is a portable intermediate representation for ML computation graphs.

The goal:

```text
train in one framework
deploy in another runtime
```

Common problems:

* unsupported operators,
* dynamic control flow,
* shape inference failures,
* version mismatch,
* numerical differences.

## 8.4 TensorRT

TensorRT aggressively rewrites neural networks into hardware-optimal NVIDIA GPU execution plans.

Pipeline:

```text
ONNX / framework graph
  -> graph parsing
  -> layer fusion
  -> precision lowering
  -> kernel selection
  -> memory planning
  -> serialized engine
```

TensorRT is about making one model run efficiently on NVIDIA hardware.

## 8.5 Torch Compile, XLA, MLIR, and TVM

These systems use compiler techniques:

* graph capture,
* lowering,
* fusion,
* memory planning,
* backend-specific code generation.

Mental models:

* `torch.compile`: make PyTorch programs more compiler-friendly.
* XLA: compile tensor programs for accelerators.
* MLIR: infrastructure for multi-level compiler IRs.
* TVM: generate optimized kernels across hardware targets.

## 8.6 Dynamic Shapes

Dynamic shapes make optimization harder because the compiler cannot specialize as aggressively.

For inference systems, dynamic shapes come from:

* variable prompt lengths,
* variable image sizes,
* variable batch sizes,
* variable output lengths.

TensorRT uses optimization profiles to specialize for shape ranges. Wide ranges are flexible but less optimized.

## 8.7 Compiler Failure Modes

Compiler/runtime paths can fail through:

* graph breaks,
* unsupported ops,
* poor shape profiles,
* numerical drift,
* precision mismatch,
* engine rebuild cost,
* custom operator incompatibility.

Always benchmark the compiled path against the real workload.

---

# 9. Distributed LLM Serving

## 9.1 Single-GPU vs Multi-GPU Serving

A small model may fit on one GPU with replicas for scale. A large model may need to be split across GPUs.

The distinction:

```text
replication scales requests
parallelism makes one model fit or run faster
```

## 9.2 Model Parallelism for Inference

Common forms:

* tensor parallelism: split tensor operations across GPUs,
* pipeline parallelism: split layers across stages,
* expert parallelism: route MoE experts across devices.

These reduce per-device memory or increase throughput, but add communication.

## 9.3 Request Routing and Token-Aware Load Balancing

Round-robin is weak for LLMs because requests vary wildly.

One request may have:

```text
500 input tokens + 50 output tokens
```

Another may have:

```text
80,000 input tokens + 4,000 output tokens
```

The router should consider prompt length, expected output length, active sequences, KV memory, model pool, and tenant priority.

## 9.4 GPU Worker Pools

Serving systems manage:

* model loading,
* warm pools,
* cold starts,
* replica placement,
* heterogeneous GPUs,
* queue assignment,
* health checks.

Cold starts matter because loading a large model can take much longer than a normal request.

## 9.5 Multi-Tenant Serving

Multi-tenant serving needs:

* per-tenant quotas,
* token-aware limits,
* priority queues,
* noisy-neighbor controls,
* long-context isolation,
* cost attribution,
* data/security policy routing.

Tenant isolation is both a systems and security problem.

## 9.6 Autoscaling and Failover

Useful autoscaling signals:

* queue time,
* active sequences,
* input tokens/sec,
* output tokens/sec,
* GPU memory usage,
* p95/p99 latency,
* request rejection rate,
* model load time.

Scaling on CPU utilization alone is usually wrong for LLM serving.

## 9.7 Serving Stacks

Common serving components:

* **vLLM:** LLM serving engine with PagedAttention and continuous batching.
* **TGI:** text-generation serving stack.
* **Triton:** general inference server for many model types.
* **TensorRT-LLM:** optimized NVIDIA LLM inference stack.
* **Ray Serve:** distributed Python serving framework.
* **Kubernetes:** container orchestration and resource placement.

Each solves a different layer of the system.

---

# 10. Distributed Training Systems

## 10.1 Training Memory Breakdown

Training memory includes:

```text
parameters + gradients + optimizer states + activations + temporary buffers
```

Optimizer states can be larger than the model weights. Activations can dominate for long sequences and large batches.

## 10.2 Data Parallelism and DDP

Data parallelism replicates the model on each GPU and gives each replica different data.

After backward pass, workers synchronize gradients, often with all-reduce.

This is simple but can become communication-bound.

## 10.3 FSDP and ZeRO

FSDP and ZeRO reduce memory by sharding parameters, gradients, and optimizer states across devices.

The tradeoff:

```text
less memory per GPU
vs
more communication and coordination
```

## 10.4 Tensor, Pipeline, and Expert Parallelism

Tensor parallelism splits operations inside layers.

Pipeline parallelism splits layers into stages.

Expert parallelism distributes MoE experts and routes tokens to them.

Large training runs often combine several parallelism strategies.

## 10.5 Communication and NCCL

NCCL provides GPU communication collectives such as all-reduce, broadcast, reduce-scatter, and all-gather.

Distributed training often bottlenecks on communication rather than compute. Systems try to overlap communication with computation.

## 10.6 Checkpointing and Fault Tolerance

Long-running jobs need:

* checkpoint storage,
* recovery from preemption,
* reproducible configs,
* optimizer state checkpoints,
* data-loader state,
* failure detection.

Checkpointing too frequently can stall training. Checkpointing too rarely risks losing expensive work.

## 10.7 Distributed Training Failure Modes

Common failures:

* non-linear scaling,
* stragglers,
* NCCL hangs,
* OOM,
* dataloader bottlenecks,
* checkpoint stalls,
* network topology mismatch,
* rank mismatch.

---

# 11. Capacity Planning for LLM Systems

## 11.1 Inputs to Capacity Planning

You need:

* QPS,
* prompt length distribution,
* output length distribution,
* concurrency,
* model size,
* context length,
* latency SLO,
* GPU type,
* measured tokens/sec,
* batching efficiency,
* routing mix.

Average request size is not enough. Long-tail prompts and outputs often determine p95/p99 behavior.

## 11.2 Prefill and Decode Capacity

Input tokens and output tokens stress the system differently.

Prefill scales with prompt length and is more parallel. Decode scales with output length and active sequences, and is often memory-bound.

Capacity planning should estimate both.

## 11.3 KV Cache Memory Estimate

Rough intuition:

```text
KV memory ≈ batch * sequence_length * layers * kv_heads * head_dim * 2 * bytes
```

This is not a substitute for benchmarking. It is a way to reason about why context length and concurrency are expensive.

## 11.4 GPU Count and Cost Estimate

Estimate:

* peak tokens/sec,
* headroom,
* redundancy,
* p95/p99 target,
* expected batching efficiency,
* failover capacity,
* cost per successful task.

Do not size only for average load. Interactive AI products need tail-latency headroom.

## 11.5 Autoscaling Policy

Good autoscaling signals include:

* queue time,
* tokens/sec,
* active sequences,
* KV memory,
* GPU memory pressure,
* p95/p99 latency.

Bad signals include CPU utilization alone or request count alone.

## 11.6 Capacity Planning Failure Modes

Common mistakes:

* average tokens/request hides long-tail load,
* one tenant dominates KV memory,
* model load time makes scale-out too slow,
* scaling on CPU while GPU is bottleneck,
* ignoring output length variance,
* mixing long-context and short-context traffic in one pool.

---

# 12. Debugging Playbook

## 12.1 Low GPU Utilization

Possible causes:

* small batches,
* CPU/tokenization bottleneck,
* network overhead,
* synchronization points,
* inefficient kernels,
* too many tiny requests,
* poor request scheduling.

## 12.2 CUDA OOM

Possible causes:

* KV cache growth,
* fragmentation,
* long contexts,
* memory leak,
* too many active sequences,
* model too large,
* allocator behavior.

## 12.3 p99 Latency Spikes

Possible causes:

* long-tail prompts,
* queue buildup,
* cold starts,
* noisy neighbors,
* retries,
* slow tools,
* cache misses,
* GC or event loop stalls.

## 12.4 Slow Prefill

Possible causes:

* long prompts,
* retrieval stuffing,
* weak batching,
* attention implementation,
* model too large.

## 12.5 Slow Decode

Possible causes:

* memory bandwidth,
* KV cache reads,
* low batch efficiency,
* poor quantization or kernel support,
* too many active sequences.

## 12.6 NCCL Hangs

Possible causes:

* network failure,
* rank mismatch,
* timeout,
* GPU failure,
* version mismatch,
* topology issue.

## 12.7 Debugging Checklist

```text
split latency
check token distributions
check queue time
check prefill/decode time
check active sequences
check KV memory
check GPU utilization
check memory bandwidth
check error/retry rates
compare candidate vs baseline
```

---

# 13. System Design Patterns

## 13.1 Single-Model Inference Service

```text
API gateway
  -> router
  -> queue
  -> inference workers
  -> streaming response
  -> observability
```

Use when one model family serves most traffic and isolation requirements are simple.

## 13.2 Multi-Tenant LLM Serving Platform

```text
API gateway
  -> auth / tenant policy
  -> request classifier
  -> model router
  -> token-aware queue
  -> GPU worker pools
  -> streaming gateway
  -> metrics / tracing / billing
```

Use when many tenants, models, contexts, and priorities share infrastructure.

## 13.3 Batch Inference Platform

Offline workloads prioritize throughput and cost over interactivity.

Design around:

* large batches,
* checkpointable jobs,
* queue scheduling,
* object storage,
* retryable workers,
* cost-aware GPU allocation.

## 13.4 Training Platform

```text
data loader
  -> distributed workers
  -> checkpoint store
  -> metrics tracker
  -> model registry
```

Training platforms need data versioning, fault tolerance, distributed communication, and reproducibility.

## 13.5 Model Compilation Pipeline

```text
PyTorch model
  -> export / graph capture
  -> optimize
  -> compile engine
  -> benchmark
  -> deploy
```

Compilation should be treated like a release artifact, not an invisible build step.

---

# 14. How to Use the Examples

The examples are meant to be operational artifacts, not extra reading:

* use the bottleneck map when choosing an optimization,
* use the GPU memory hierarchy and fusion/tiling examples to explain why moving less data matters,
* use the PyTorch/CUDA example when debugging suspicious benchmarks,
* use the capacity-planning scripts when reasoning about long context and active sequences,
* use the continuous batching scheduler to explain why fixed batches waste capacity,
* use the compiled model checklist when discussing ONNX, TensorRT, or `torch.compile` releases,
* use the incident examples when practicing p99 latency and GPU serving debugging.

In an interview, cite the artifact shape even if you do not remember every detail:

```text
I would build a stage-level trace, split prefill and decode, check token distributions, inspect KV memory, and compare candidate vs baseline under realistic load.
```

---

# 15. What to Say in an Interview

A strong infrastructure answer follows this structure:

1. Clarify workload: QPS, prompt length, output length, latency SLO, model size, traffic shape.
2. Identify bottleneck: CPU, queue, prefill, decode, memory, network, tool dependency.
3. Choose architecture: batching, routing, caching, GPU pools, autoscaling, fallback.
4. Discuss tradeoffs: latency vs throughput, cost vs quality, utilization vs p99, flexibility vs optimized runtime.
5. Add observability: tokens/sec, queue time, prefill time, decode time, KV memory, GPU utilization, error rates.
6. Add failure handling: rate limits, admission control, rollback, failover, degraded mode.

High-signal phrases:

* "Memory movement often dominates arithmetic."
* "Request load balancing is not token load balancing."
* "Decode is often memory-bandwidth-bound."
* "Continuous batching fights output-length variance."
* "TensorRT optimizes execution inside the GPU; vLLM optimizes serving around the GPU."
* "Capacity planning needs token distributions, not just QPS."

---

# 16. Takeaways

ML systems engineering is bottleneck management.

The recurring patterns are fusion, tiling, caching, quantization, batching, pipelining, sharding, prefetching, and scheduling. They all ask how to keep expensive hardware doing useful work while moving less data and waiting less often.

LLM serving is dominated by autoregressive decode, KV cache memory, scheduling, and tail latency. Distributed training is dominated by memory, communication, checkpointing, and fault tolerance.

The best engineers can connect a production symptom to the layer that caused it: prompt length, queueing, prefill, decode, KV memory, kernel efficiency, GPU utilization, network communication, or deployment architecture.
