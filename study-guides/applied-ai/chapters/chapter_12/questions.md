---
layout: page
title: "Chapter 12 Questions: AI Platform and Infrastructure Stack"
guide_type: questions
---

# Chapter 12 — Practice Questions

Explanatory material for this chapter lives in [`guide.md`](guide.html).

---

# Tech Stack Mental Model Questions

---

## Question 1

**How would you explain PyTorch vs TensorFlow vs JAX?**

### Sample Answer

PyTorch is best understood as eager tensor programming with an autograd tape, which makes it natural for research iteration and debugging. TensorFlow is historically graph-oriented: you define or trace computation so it can be optimized and deployed, which fits production and serving workflows. JAX is NumPy-like functional programming plus transformations such as `grad`, `jit`, `vmap`, and `pmap`, which makes it powerful for compiled high-performance research code. The choice depends on whether the workflow values dynamic debugging, graph deployment, or composable program transformations.

---

## Question 2

**Why is PyTorch dominant in many LLM research workflows?**

### Sample Answer

PyTorch feels close to normal Python, so researchers can inspect tensors, write custom training loops, change model code quickly, and debug failures directly. Its ecosystem also matters: Hugging Face Transformers, DeepSpeed, FSDP, custom Triton kernels, and many open-source LLM projects are PyTorch-first. The tradeoff is that large-scale training still requires careful systems work around distributed execution, memory, data loading, checkpointing, and kernel efficiency.

---

## Question 3

**What does JAX's `jit`, `grad`, and `vmap` mental model buy you?**

### Sample Answer

JAX treats numerical programs as functions that can be transformed. `grad` creates gradient functions, `jit` compiles functions for faster execution, and `vmap` vectorizes functions across batch dimensions. This makes it elegant to express research ideas as composable transformations. The tradeoff is that code needs to be more functional and shape-stable; dynamic Python behavior can cause recompilation or make debugging harder.

---

## Question 4

**When would you use Kubernetes vs Slurm for ML workloads?**

### Sample Answer

Kubernetes is usually better for service-oriented workloads: APIs, inference deployments, workers, retrieval services, and platform components that need health checks, autoscaling, and rolling deploys. Slurm is often better for HPC-style batch training jobs where researchers submit jobs needing a fixed number of nodes or GPUs. Large AI labs may use both: Kubernetes for services and Slurm-like schedulers for research training clusters.

---

## Question 5

**What role does NCCL play in distributed training?**

### Sample Answer

NCCL is the GPU communication library behind operations such as all-reduce, all-gather, reduce-scatter, and broadcast. In distributed training, each GPU computes local work, then workers synchronize gradients, parameters, or activations through communication collectives. If NCCL is misconfigured, slow, or hanging, GPUs can sit idle even when model code is correct. That makes networking, topology, and communication patterns central to training throughput.

---

## Question 6

**How do DeepSpeed ZeRO and PyTorch FSDP reduce memory pressure?**

### Sample Answer

Both reduce memory pressure by sharding model state across GPUs instead of replicating everything everywhere. DeepSpeed ZeRO shards optimizer states, gradients, and parameters depending on stage. PyTorch FSDP similarly shards parameters and gathers them only when needed for computation. The benefit is fitting larger models or batches. The cost is more communication, more complex configuration, and new failure modes around checkpointing and distributed synchronization.

---

## Question 7

**What is the difference between vLLM, TGI, Triton Inference Server, and Ray Serve?**

### Sample Answer

vLLM is specialized for high-throughput LLM serving, especially efficient KV-cache management and continuous batching. TGI is Hugging Face's text-generation server for serving compatible LLMs with production features. Triton Inference Server is a general multi-framework inference server for many model types and backends, not only LLMs. Ray Serve is Python-native distributed serving, useful for custom routing and multi-stage inference pipelines. The right choice depends on whether the bottleneck is LLM token throughput, standard text-generation deployment, heterogeneous model serving, or custom Python orchestration.

---

## Question 8

**How do Spark, Beam, and Dask differ as data-processing systems?**

### Sample Answer

Spark is a distributed batch-processing engine widely used for large joins, aggregations, and ETL. Beam is a programming model for both batch and streaming, where the same pipeline can run on different runners and has strong event-time/windowing concepts. Dask is Python-native distributed computation that feels closer to pandas, NumPy, and custom Python workflows. Spark is often strongest for large enterprise batch ETL, Beam for unified batch/stream semantics, and Dask for Python-centric parallelism.

---

## Question 9

**When would you choose FAISS, pgvector, or a managed vector database?**

### Sample Answer

I would choose FAISS when I want a local or custom vector index and am willing to build the service, metadata, persistence, and scaling layers myself. I would choose pgvector when the corpus is small to medium, metadata filtering is important, and the application already uses Postgres. I would choose a managed or dedicated vector database when operational scaling, APIs, namespaces, and vector-specific indexing are worth the added dependency and cost.

---

## Question 10

**How do Prometheus, Grafana, and OpenTelemetry compose?**

### Sample Answer

OpenTelemetry instruments code and emits traces, metrics, and logs in a standard format. Prometheus commonly stores and queries time-series metrics. Grafana visualizes metrics and logs in dashboards. Together, OpenTelemetry can produce telemetry, Prometheus can collect service metrics, and Grafana can show operational views and alerts. In AI systems, the key is to include AI-specific dimensions such as model version, prompt version, token counts, retrieval latency, tool latency, and queue wait.

---

## Question 11

**What should W&B or MLflow track in a research training run?**

### Sample Answer

They should track the full experiment identity: code version, config, hyperparameters, data version, model architecture, checkpoint paths, random seed, metrics, eval results, logs, artifacts, and system utilization. For LLM or RLHF work, I would also track prompt datasets, reward model versions, rollout settings, preference data versions, and evaluation slices. The point is reproducibility: another engineer should be able to understand what changed and why a run improved or regressed.

---

## Question 12

**What is the mental model for Docker and Kubernetes in AI systems?**

### Sample Answer

Docker packages code, dependencies, and runtime assumptions into an image. Kubernetes schedules and manages containers across machines with health checks, restarts, services, and scaling. In AI systems, Docker helps make model services, workers, and data jobs reproducible, while Kubernetes runs and manages those workloads. The hard parts are GPU scheduling, secrets, network access, image size, cold starts, observability, and resource isolation.

---

## Question 13

**Why do AI agents need sandboxing or VM isolation?**

### Sample Answer

Agents may run code, browse websites, manipulate files, call tools, or execute long-horizon tasks. If those actions are untrusted or model-generated, they need isolation from host credentials, files, networks, and other tenants. Sandboxes, containers, VMs, microVMs, network policies, and resource limits reduce blast radius. The mental model is: give the agent a controlled environment where actions are observable, bounded, and disposable.

---

## Question 14

**When should Python be replaced or complemented by C++, Rust, CUDA, or Triton?**

### Sample Answer

Python is excellent for orchestration and research iteration, but lower-level tools are needed when the bottleneck is runtime overhead, memory control, kernel performance, or systems safety. C++ is common for runtimes and high-performance services. Rust is useful for safe systems components and control planes. CUDA gives direct GPU programming control. Triton provides a Python-like way to write custom GPU kernels. The right move is not to rewrite everything; it is to move the hot or safety-critical path to the right layer.

---

## Question 15

**How would you design the stack for an RLHF training pipeline?**

### Sample Answer

I would start with a PyTorch or JAX policy model, a dataset/prompt source, rollout workers, a reward model or preference data pipeline, an optimizer such as PPO or DPO, distributed training infrastructure, checkpoint storage, eval harnesses, and experiment tracking. Ray or custom workers can coordinate rollouts; DeepSpeed or FSDP can reduce memory pressure; Slurm or Kubernetes can schedule jobs; W&B or MLflow can track runs; Prometheus/Grafana/OpenTelemetry can monitor throughput and failures. The main risks are rollout bottlenecks, reward bugs, training instability, checkpoint failures, and irreproducible experiments.

---

## Question 16

**How would you design the stack for a knowledge or RAG system?**

### Sample Answer

I would build ingestion for raw documents, parsing, chunking, metadata extraction, embedding generation, vector and sparse indexes, reranking, context assembly, generation, citation validation, and evals. FAISS, pgvector, or a vector DB can handle dense retrieval; Elasticsearch/OpenSearch can handle sparse retrieval; rerankers improve precision; metadata filters enforce permissions and freshness. The key failure modes are stale indexes, bad chunking, missing access control, poor ranking, unsupported citations, and noisy context.

---

## Question 17

**How would you design the stack for a high-throughput LLM inference service?**

### Sample Answer

I would use an API gateway with auth, quotas, validation, and request IDs; a router for model selection; caches where correctness allows; queues or batchers for admission control; an inference runtime such as vLLM, TGI, Triton, or Ray Serve; streaming responses; output validation; and observability across every stage. The core metrics are time to first token, time to final token, prompt tokens, output tokens, queue wait, GPU utilization, KV-cache pressure, error rate, fallback rate, and cost per successful request.

---

## Question 18

**How do data, tensor, pipeline, sequence, and expert parallelism differ?**

### Sample Answer

Data parallelism replicates the model and splits examples across workers. Tensor parallelism splits large layer computations across GPUs. Pipeline parallelism splits layers into stages across devices. Sequence parallelism reduces activation memory by splitting sequence-related work. Expert parallelism distributes MoE experts across devices. The right choice depends on what does not fit or what is slow: batch size, parameters, activations, sequence length, or sparse expert capacity. Each strategy trades memory and compute for communication and scheduling complexity.

---

## Question 19

**Why do checkpointing and restore tests matter in large training systems?**

### Sample Answer

Large training jobs fail often enough that checkpointing is part of the system design. A useful checkpoint must capture model weights, optimizer state, scheduler state, RNG state, data-loader position, config, and version metadata. For sharded training, restore logic must correctly map checkpoint shards back to ranks. Restore tests matter because an untested checkpoint may be unusable exactly when a multi-day run fails.

---

## Question 20

**What is LoRA and when would you use it?**

### Sample Answer

LoRA freezes the base model and trains small low-rank adapter matrices. The mental model is "frozen base weights plus small trainable adapters." It is useful when full fine-tuning is too expensive or when you want lightweight domain/task adaptation. The risks are base/adaptor mismatch, overfitting narrow data, and deployment confusion if the adapter is not tracked with the correct base model, tokenizer, and eval results.

---

## Question 21

**Why do dataset and checkpoint formats matter in AI infrastructure?**

### Sample Answer

Formats determine how efficiently and reliably bytes become batches or deployable artifacts. Parquet and Arrow are efficient for columnar data; JSONL is simple but inefficient at huge scale; WebDataset-style shards can work well for large multimodal datasets; `safetensors` can make model weight loading safer. Bad formats or sharding choices can bottleneck GPUs, make backfills painful, corrupt reproducibility, or make serving startup slow.

---

## Question 22

**What problem does a feature store solve?**

### Sample Answer

A feature store centralizes feature definitions and provides consistent offline and online access. It helps reduce training-serving skew, supports point-in-time correct training datasets, and gives serving systems low-latency feature lookup. The tradeoff is operational complexity: feature ownership, freshness, backfills, and online/offline consistency all need explicit management. For small systems, careful warehouse pipelines may be enough.

---

## Question 23

**What should a model registry track before a model is deployed?**

### Sample Answer

A model registry should track more than weights. It should include tokenizer, config, base model, adapters, training data version, code version, eval results, safety review, owner, deployment state, and rollback target. The registry turns an anonymous checkpoint into an auditable deployable artifact. Without this, teams cannot reliably compare, reproduce, approve, or roll back model versions.

---

## Question 24

**What CI checks are useful for ML research infrastructure?**

### Sample Answer

Useful checks include data transform unit tests, schema checks, shape tests, small training-loop smoke tests, checkpoint save/restore tests, deterministic eval harness tests, config validation, and launch tests for distributed jobs. The goal is to catch cheap failures before expensive GPU runs. Research code can stay flexible while still protecting the shared training and evaluation pipeline.

---

## Question 25

**What is the CUDA execution hierarchy, and why does it matter for AI workloads?**

### Sample Answer

CUDA work is organized as a grid of blocks, where blocks contain warps and warps contain threads. Threads execute lanes of work; warps execute in lockstep; blocks can cooperate through shared memory. This matters because GPUs are efficient when many threads run regular operations over large tensors with predictable memory access. Irregular branching, tiny kernels, bad tensor shapes, CPU-GPU transfers, and excessive synchronization can waste the hardware.

---

## Question 26

**Why can many small GPU operations be slower than one fused operation?**

### Sample Answer

Each GPU kernel launch has overhead, and intermediate tensors often require extra memory reads and writes. Many tiny operations can spend more time on launch overhead, synchronization, and memory movement than useful math. A fused operation does more work per launch and can keep intermediate values closer to the compute, which is why optimized kernels and compiler fusion matter for high-throughput ML systems.

---

## Question 27

**Why is one scale-up domain a natural boundary for an MoE layer?**

### Sample Answer

MoE routing creates all-to-all traffic: tokens on many GPUs may need to visit experts on many other GPUs, then return to be combined. Inside a scale-up domain, accelerators usually have much faster and denser interconnect. Across racks or scale-out links, bandwidth is lower and latency is higher. Keeping an expert-parallel MoE layer inside the fast domain avoids making all-to-all routing the bottleneck.

---

## Question 28

**Why does pipeline parallelism not automatically solve KV-cache memory pressure?**

### Sample Answer

Pipeline parallelism splits layers across stages, so it helps with model weight capacity. But to keep multiple stages busy, the system needs multiple micro-batches in flight. Splitting layers reduces the KV stored per stage, while more in-flight micro-batches increase the active sequence count. These effects can cancel, so pipeline parallelism is not a magic fix for long-context KV pressure. It also adds bubbles, scheduling complexity, and cross-stage latency.

---

## Question 29

**How can a distributed parallelism scheme slow research iteration?**

### Sample Answer

If the parallelism scheme assumes a specific architecture, model changes can become expensive. Pipeline boundaries may make cross-layer residual attention, alternating attention patterns, or uneven layer costs hard to implement. Expert placement may assume a fixed topology. When researchers avoid useful architecture changes because the infrastructure cannot support them, the system is constraining research instead of enabling it.

---

## Question 30

**What artifacts must be versioned in a distillation or self-distillation run?**

### Sample Answer

Version the student checkpoint, teacher or reference checkpoint, tokenizer, training code, rollout data, teacher prompt or privileged context, reward/verifier/judge version, mask parameters, eval suite, and promotion decision. For EMA or target-network methods, also track the decay or update interval. The student checkpoint alone is not enough to reproduce the behavior.

---

## Question 31

**What fields would you log for an OPSD or RMSD training example?**

### Sample Answer

Log the student prompt, teacher prompt or privileged context, student rollout, student top-K logprobs at each prefix, teacher logprobs on the same prefixes, candidate high-disagreement token positions, judge-selected relevant positions, masked loss metadata, student checkpoint, teacher checkpoint, and eval tags. This makes the token-level training signal auditable.

---

## Question 32

**Why are teacher forward passes and rollout generation major cost drivers?**

### Sample Answer

Rollout generation uses autoregressive decode, which can be slower and less hardware-efficient than large-batch training. Teacher rescoring adds additional forward passes over the same prefixes, and RMSD-style methods may also store top-K logprobs and call a judge model. The training cost is not just the backward pass; it includes data generation, scoring, filtering, storage, and eval.

---

## Question 33

**How would you debug a regression after a teacher checkpoint promotion?**

### Sample Answer

I would compare runs before and after the promotion by teacher checkpoint, student checkpoint, rollout data, mask selection, eval slices, and update cadence. I would check whether the new teacher changed target distributions, selected different tokens, introduced behavior outside the intended slice, or came from contaminated data. Then I would roll back or quarantine the affected teacher/data artifacts before retraining.

---

## Question 34

**What is the difference between torch.no_grad() and model.eval()?**

### Sample Answer

`model.eval()` switches modules such as dropout and batch normalization into inference behavior. `torch.no_grad()` tells PyTorch not to build the autograd graph, which reduces memory use and overhead during inference. They solve different problems and are often used together: `model.eval()` for correct layer behavior, `torch.no_grad()` for efficient execution.

---

## Question 35

**How does PyTorch autograd work?**

### Sample Answer

PyTorch autograd records tensor operations into a dynamic computation graph when tensors require gradients. Calling `backward()` traverses that graph in reverse and applies the chain rule to populate `.grad` fields. Gradients accumulate by default, so training loops usually call `optimizer.zero_grad()` before the backward pass. This eager define-by-run model is why PyTorch feels natural for research debugging.

---

## Question 36

**What is the difference between DataLoader num_workers and pin_memory?**

### Sample Answer

`num_workers` controls how many worker processes load and preprocess batches in parallel. Increasing it can help when the GPU is waiting on CPU data loading, but too many workers can add overhead or memory pressure. `pin_memory=True` allocates page-locked host memory so CPU-to-GPU copies can be faster and asynchronous. Use these when profiling shows the input pipeline is starving accelerator compute.

---

## Question 37

**What is the difference between Hugging Face pipeline() and direct model inference?**

### Sample Answer

`pipeline()` is a high-level wrapper that bundles tokenization, model execution, decoding, and task-specific postprocessing. It is useful for prototypes and common tasks. Direct model inference gives more control over batching, padding, truncation, generation parameters, streaming, device placement, and output parsing. In production, teams often start with pipelines but move lower-level when they need performance, reliability, or custom behavior.

---

## Question 38

**What is LangChain and what problems does it solve?**

### Sample Answer

LangChain is an application framework for composing LLM calls with prompts, tools, retrievers, memory, and agent-like workflows. It reduces boilerplate for common patterns such as RAG, tool calling, and chains. The tradeoff is abstraction complexity: production systems still need clear state, typed interfaces, evals, tracing, permission checks, and escape hatches when framework abstractions hide important behavior.
