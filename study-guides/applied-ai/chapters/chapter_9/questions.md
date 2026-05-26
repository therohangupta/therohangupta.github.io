---
layout: page
title: "Software Engineering Fundamentals Practice Questions"
guide_type: questions
---
# Chapter 9 — Practice Questions

Explanatory material for this chapter lives in [`guide.md`](guide.html).

---

# Common Interview Questions and Sample Answers

---

## Question 1

**How would you optimize a slow SQL query?**

### Sample Answer

I would start by looking at the query plan rather than guessing. I would check whether the database is scanning too many rows, missing a useful index, joining in a bad order, sorting large intermediate results, or returning more columns than needed. Then I would consider adding or changing indexes, rewriting joins or filters, reducing result size, partition pruning, using materialized views, or denormalizing carefully. I would also verify with realistic data because a query that is fast on a small dev database can fail badly in production.

---

## Question 2

**What is the difference between OLTP and OLAP?**

### Sample Answer

OLTP systems are optimized for many small transactional reads and writes, such as user actions, orders, or account updates. They care about low latency, consistency, and concurrency. OLAP systems are optimized for analytical queries over large datasets, such as dashboards, aggregations, and model training data exploration. They care about scan efficiency, columnar storage, compression, and large joins. Mixing the two without care can cause analytical workloads to slow down user-facing transactions.

---

## Question 3

**Explain database sharding.**

### Sample Answer

Sharding splits a dataset across multiple database instances or partitions, usually by a shard key such as tenant ID, user ID, or region. It increases write capacity and storage capacity because no single database owns all data. The tradeoff is complexity: cross-shard queries, transactions, rebalancing, hot shards, and operational debugging become harder. A good shard key spreads load evenly while preserving common access patterns.

---

## Question 4

**What causes deadlocks and how do you prevent them?**

### Sample Answer

Deadlocks happen when two or more transactions hold locks while waiting for locks held by each other, so none can proceed. They often come from inconsistent lock ordering, long transactions, broad updates, or high concurrency on shared rows. Prevention includes keeping transactions short, acquiring locks in a consistent order, indexing filters so fewer rows are locked, lowering isolation when safe, using retries for deadlock errors, and designing workflows to avoid unnecessary shared mutable state.

---

## Question 5

**What are materialized views?**

### Sample Answer

A materialized view stores the result of a query instead of recomputing it every time. It is useful for expensive aggregations, joins, or dashboard queries that are read often and can tolerate some freshness delay. The tradeoff is that the materialized view must be refreshed, which introduces storage cost, refresh complexity, and possible staleness. In ML systems, materialized views can make feature generation or monitoring queries much cheaper if freshness requirements are clear.

---

## Question 6

**Explain CAP theorem.**

### Sample Answer

CAP theorem says that under a network partition, a distributed system must choose between consistency and availability. Consistency means clients see a coherent, up-to-date view of data. Availability means every request receives a non-error response. Partition tolerance is unavoidable in distributed systems because networks fail. The practical lesson is not "pick two forever"; it is to decide what each part of the system should do during partitions, especially for user-visible writes, analytics, queues, and caches.

---

## Question 7

**What is the difference between a star schema and a snowflake schema?**

### Sample Answer

A star schema has a central fact table connected directly to denormalized dimension tables. It is simple and fast for analytics because queries usually need fewer joins. A snowflake schema normalizes dimensions into additional related tables, reducing duplication but increasing join complexity. Star schemas are common in warehouses and BI because they are easier for analysts and query engines. Snowflake schemas can help when dimensions are large, shared, or need stricter consistency.

---

## Question 8

**How would you design a data pipeline for ML systems?**

### Sample Answer

I would define the source data, freshness requirements, schema contracts, feature transformations, labels, validation checks, storage layers, and consumers. A typical pipeline ingests raw events, validates and versions schemas, writes immutable raw data, transforms it into features or training examples, checks quality, and publishes datasets to a feature store, warehouse, or model-training job. I would track lineage, backfills, late-arriving data, privacy filters, and training-serving skew. The pipeline should fail loudly when data quality breaks rather than silently training or serving on corrupted inputs.

---

## Question 9

**What are partitioning and indexing strategies?**

### Sample Answer

Partitioning physically splits data so queries can scan only relevant subsets, often by time, tenant, region, or hash. Indexing creates data structures that make lookups, filters, joins, or sorting faster. Good strategies follow access patterns: time-series analytics often partitions by date, multi-tenant systems may partition or index by tenant, and exact lookups need indexes on identifiers. The tradeoff is write overhead, storage cost, and operational complexity. Too many indexes can slow writes; poor partition keys can create hot partitions.

---

## Question 10

**How would you process streaming data in real time?**

### Sample Answer

I would use an event log or stream such as Kafka, a stream processor, durable checkpoints, schema validation, and idempotent sinks. The system should define event-time versus processing-time semantics, windowing rules, late-event handling, retry behavior, and dead-letter queues. For ML systems, streaming can update features, monitor drift, trigger alerts, or power near-real-time personalization. The hard parts are correctness under retries, backpressure, ordering, schema evolution, and making sure real-time features match training-time definitions.

---

## Question 11

**How does Python memory management work?**

### Sample Answer

Python primarily manages memory through reference counting: objects are freed when their reference count drops to zero. CPython also has a cyclic garbage collector to clean up reference cycles that reference counting alone cannot free. Under the hood, Python uses private memory allocators and arenas for small objects. In production, memory may not immediately return to the operating system even after objects are freed, so engineers need to distinguish live object growth from allocator behavior.

---

## Question 12

**Explain reference counting and garbage collection.**

### Sample Answer

Reference counting tracks how many references point to an object. When the count reaches zero, CPython can deallocate the object immediately. Garbage collection handles cycles, such as two objects that reference each other even though nothing else can reach them. Reference counting gives predictable cleanup for many objects, but cycles require periodic GC work. Finalizers, global references, caches, and closures can make object lifetime less obvious.

---

## Question 13

**What is async programming and when should you use it?**

### Sample Answer

Async programming lets a program handle many concurrent IO-bound tasks without blocking a thread per task. In Python, `asyncio` uses an event loop where coroutines yield control while waiting for network, disk, database, or API responses. It is useful for high-concurrency services that spend much of their time waiting on IO, such as API gateways, retrieval services, or orchestration layers. It is not a magic speedup for CPU-bound work; CPU-heavy tasks need processes, native extensions, or separate workers.

---

## Question 14

**What is the difference between threading, multiprocessing, and asyncio?**

### Sample Answer

Threading runs multiple threads in one process and is useful for IO-bound work, but in CPython only one thread executes Python bytecode at a time because of the GIL. Multiprocessing runs separate processes, bypassing the GIL for CPU-bound work at the cost of more memory and inter-process communication overhead. `asyncio` runs many coroutines on an event loop, which is efficient for IO-bound concurrency but requires non-blocking libraries. The right choice depends on whether the bottleneck is CPU, IO, memory, or external services.

---

## Question 15

**What causes memory leaks in Python?**

### Sample Answer

Python memory leaks usually come from objects that remain reachable longer than intended. Common causes include unbounded caches, global lists or dictionaries, lingering references in closures, reference cycles with finalizers, callbacks that are never deregistered, large objects kept in logs or traces, and native extension leaks. I would debug with memory profiles, heap snapshots, object growth by type, and request-level reproduction. The fix is usually to bound caches, release references, stream large data, or isolate leaking work in restartable workers.

---

## Question 16

**Explain Python's GIL in depth.**

### Sample Answer

The Global Interpreter Lock is a CPython mutex that allows only one thread to execute Python bytecode at a time within a process. It simplifies memory management and protects interpreter internals, especially reference counting. The GIL does not prevent concurrency for IO-bound tasks because threads can release it while waiting on IO, and native extensions may release it during heavy computation. But it limits CPU-bound parallelism in pure Python threads. For CPU-heavy workloads, use multiprocessing, vectorized libraries, compiled extensions, or separate services.

---

## Question 17

**How would you profile Python code performance?**

### Sample Answer

I would first define the performance problem: CPU time, memory growth, IO latency, database time, or end-to-end request latency. For CPU, I would use profilers such as `cProfile`, sampling profilers, or py-spy. For memory, I would use tracemalloc, heap snapshots, and object growth analysis. For services, I would add tracing around request stages, database calls, model calls, queue wait, and serialization. Profiling should use realistic inputs because microbenchmarks can miss production bottlenecks like network waits, batching, and lock contention.

---

## Question 18

**What are metaclasses?**

### Sample Answer

Metaclasses are the classes of classes. In Python, a class definition creates a class object, and the metaclass controls how that class object is created. They can customize class construction, registration, validation, or dynamic method creation. They are powerful but often unnecessary; decorators, base classes, or simple registries are usually easier to understand. In interviews, the key is to know the mechanism and also know when not to use it.

---

## Question 19

**How do decorators work internally?**

### Sample Answer

A decorator is a callable that takes a function or class and returns a replacement. The `@decorator` syntax is shorthand for assigning `func = decorator(func)`. Function decorators often wrap the original function in another function that adds behavior before or after the call. Good decorators preserve metadata with `functools.wraps`, handle arguments carefully, and avoid hiding side effects. In production systems, decorators are commonly used for retries, tracing, auth checks, caching, and registration.

---

## Question 20

**How would you build a scalable Python backend for AI inference?**

### Sample Answer

I would separate the API layer from the inference workers. The API layer should authenticate requests, validate inputs, enforce quotas, route work, and return streaming responses when useful. Inference workers should batch requests, manage model clients or GPU runtimes, apply timeouts, and emit metrics for tokens, latency, errors, and cost. I would use queues for asynchronous work, autoscaling based on queue depth and GPU utilization, caches where safe, and backpressure when capacity is exhausted. The design should make model, prompt, and route versions observable so regressions can be rolled back quickly.

---

# Tech Stack Mental Model Questions

---

## Question 21

**How would you explain PyTorch vs TensorFlow vs JAX?**

### Sample Answer

PyTorch is best understood as eager tensor programming with an autograd tape, which makes it natural for research iteration and debugging. TensorFlow is historically graph-oriented: you define or trace computation so it can be optimized and deployed, which fits production and serving workflows. JAX is NumPy-like functional programming plus transformations such as `grad`, `jit`, `vmap`, and `pmap`, which makes it powerful for compiled high-performance research code. The choice depends on whether the workflow values dynamic debugging, graph deployment, or composable program transformations.

---

## Question 22

**Why is PyTorch dominant in many LLM research workflows?**

### Sample Answer

PyTorch feels close to normal Python, so researchers can inspect tensors, write custom training loops, change model code quickly, and debug failures directly. Its ecosystem also matters: Hugging Face Transformers, DeepSpeed, FSDP, custom Triton kernels, and many open-source LLM projects are PyTorch-first. The tradeoff is that large-scale training still requires careful systems work around distributed execution, memory, data loading, checkpointing, and kernel efficiency.

---

## Question 23

**What does JAX's `jit`, `grad`, and `vmap` mental model buy you?**

### Sample Answer

JAX treats numerical programs as functions that can be transformed. `grad` creates gradient functions, `jit` compiles functions for faster execution, and `vmap` vectorizes functions across batch dimensions. This makes it elegant to express research ideas as composable transformations. The tradeoff is that code needs to be more functional and shape-stable; dynamic Python behavior can cause recompilation or make debugging harder.

---

## Question 24

**When would you use Kubernetes vs Slurm for ML workloads?**

### Sample Answer

Kubernetes is usually better for service-oriented workloads: APIs, inference deployments, workers, retrieval services, and platform components that need health checks, autoscaling, and rolling deploys. Slurm is often better for HPC-style batch training jobs where researchers submit jobs needing a fixed number of nodes or GPUs. Large AI labs may use both: Kubernetes for services and Slurm-like schedulers for research training clusters.

---

## Question 25

**What role does NCCL play in distributed training?**

### Sample Answer

NCCL is the GPU communication library behind operations such as all-reduce, all-gather, reduce-scatter, and broadcast. In distributed training, each GPU computes local work, then workers synchronize gradients, parameters, or activations through communication collectives. If NCCL is misconfigured, slow, or hanging, GPUs can sit idle even when model code is correct. That makes networking, topology, and communication patterns central to training throughput.

---

## Question 26

**How do DeepSpeed ZeRO and PyTorch FSDP reduce memory pressure?**

### Sample Answer

Both reduce memory pressure by sharding model state across GPUs instead of replicating everything everywhere. DeepSpeed ZeRO shards optimizer states, gradients, and parameters depending on stage. PyTorch FSDP similarly shards parameters and gathers them only when needed for computation. The benefit is fitting larger models or batches. The cost is more communication, more complex configuration, and new failure modes around checkpointing and distributed synchronization.

---

## Question 27

**What is the difference between vLLM, TGI, Triton Inference Server, and Ray Serve?**

### Sample Answer

vLLM is specialized for high-throughput LLM serving, especially efficient KV-cache management and continuous batching. TGI is Hugging Face's text-generation server for serving compatible LLMs with production features. Triton Inference Server is a general multi-framework inference server for many model types and backends, not only LLMs. Ray Serve is Python-native distributed serving, useful for custom routing and multi-stage inference pipelines. The right choice depends on whether the bottleneck is LLM token throughput, standard text-generation deployment, heterogeneous model serving, or custom Python orchestration.

---

## Question 28

**How do Spark, Beam, and Dask differ as data-processing systems?**

### Sample Answer

Spark is a distributed batch-processing engine widely used for large joins, aggregations, and ETL. Beam is a programming model for both batch and streaming, where the same pipeline can run on different runners and has strong event-time/windowing concepts. Dask is Python-native distributed computation that feels closer to pandas, NumPy, and custom Python workflows. Spark is often strongest for large enterprise batch ETL, Beam for unified batch/stream semantics, and Dask for Python-centric parallelism.

---

## Question 29

**When would you choose FAISS, pgvector, or a managed vector database?**

### Sample Answer

I would choose FAISS when I want a local or custom vector index and am willing to build the service, metadata, persistence, and scaling layers myself. I would choose pgvector when the corpus is small to medium, metadata filtering is important, and the application already uses Postgres. I would choose a managed or dedicated vector database when operational scaling, APIs, namespaces, and vector-specific indexing are worth the added dependency and cost.

---

## Question 30

**How do Prometheus, Grafana, and OpenTelemetry compose?**

### Sample Answer

OpenTelemetry instruments code and emits traces, metrics, and logs in a standard format. Prometheus commonly stores and queries time-series metrics. Grafana visualizes metrics and logs in dashboards. Together, OpenTelemetry can produce telemetry, Prometheus can collect service metrics, and Grafana can show operational views and alerts. In AI systems, the key is to include AI-specific dimensions such as model version, prompt version, token counts, retrieval latency, tool latency, and queue wait.

---

## Question 31

**What should W&B or MLflow track in a research training run?**

### Sample Answer

They should track the full experiment identity: code version, config, hyperparameters, data version, model architecture, checkpoint paths, random seed, metrics, eval results, logs, artifacts, and system utilization. For LLM or RLHF work, I would also track prompt datasets, reward model versions, rollout settings, preference data versions, and evaluation slices. The point is reproducibility: another engineer should be able to understand what changed and why a run improved or regressed.

---

## Question 32

**What is the mental model for Docker and Kubernetes in AI systems?**

### Sample Answer

Docker packages code, dependencies, and runtime assumptions into an image. Kubernetes schedules and manages containers across machines with health checks, restarts, services, and scaling. In AI systems, Docker helps make model services, workers, and data jobs reproducible, while Kubernetes runs and manages those workloads. The hard parts are GPU scheduling, secrets, network access, image size, cold starts, observability, and resource isolation.

---

## Question 33

**Why do AI agents need sandboxing or VM isolation?**

### Sample Answer

Agents may run code, browse websites, manipulate files, call tools, or execute long-horizon tasks. If those actions are untrusted or model-generated, they need isolation from host credentials, files, networks, and other tenants. Sandboxes, containers, VMs, microVMs, network policies, and resource limits reduce blast radius. The mental model is: give the agent a controlled environment where actions are observable, bounded, and disposable.

---

## Question 34

**When should Python be replaced or complemented by C++, Rust, CUDA, or Triton?**

### Sample Answer

Python is excellent for orchestration and research iteration, but lower-level tools are needed when the bottleneck is runtime overhead, memory control, kernel performance, or systems safety. C++ is common for runtimes and high-performance services. Rust is useful for safe systems components and control planes. CUDA gives direct GPU programming control. Triton provides a Python-like way to write custom GPU kernels. The right move is not to rewrite everything; it is to move the hot or safety-critical path to the right layer.

---

## Question 35

**How would you design the stack for an RLHF training pipeline?**

### Sample Answer

I would start with a PyTorch or JAX policy model, a dataset/prompt source, rollout workers, a reward model or preference data pipeline, an optimizer such as PPO or DPO, distributed training infrastructure, checkpoint storage, eval harnesses, and experiment tracking. Ray or custom workers can coordinate rollouts; DeepSpeed or FSDP can reduce memory pressure; Slurm or Kubernetes can schedule jobs; W&B or MLflow can track runs; Prometheus/Grafana/OpenTelemetry can monitor throughput and failures. The main risks are rollout bottlenecks, reward bugs, training instability, checkpoint failures, and irreproducible experiments.

---

## Question 36

**How would you design the stack for a knowledge or RAG system?**

### Sample Answer

I would build ingestion for raw documents, parsing, chunking, metadata extraction, embedding generation, vector and sparse indexes, reranking, context assembly, generation, citation validation, and evals. FAISS, pgvector, or a vector DB can handle dense retrieval; Elasticsearch/OpenSearch can handle sparse retrieval; rerankers improve precision; metadata filters enforce permissions and freshness. The key failure modes are stale indexes, bad chunking, missing access control, poor ranking, unsupported citations, and noisy context.

---

## Question 37

**How would you design the stack for a high-throughput LLM inference service?**

### Sample Answer

I would use an API gateway with auth, quotas, validation, and request IDs; a router for model selection; caches where correctness allows; queues or batchers for admission control; an inference runtime such as vLLM, TGI, Triton, or Ray Serve; streaming responses; output validation; and observability across every stage. The core metrics are time to first token, time to final token, prompt tokens, output tokens, queue wait, GPU utilization, KV-cache pressure, error rate, fallback rate, and cost per successful request.

---

## Question 38

**How do data, tensor, pipeline, sequence, and expert parallelism differ?**

### Sample Answer

Data parallelism replicates the model and splits examples across workers. Tensor parallelism splits large layer computations across GPUs. Pipeline parallelism splits layers into stages across devices. Sequence parallelism reduces activation memory by splitting sequence-related work. Expert parallelism distributes MoE experts across devices. The right choice depends on what does not fit or what is slow: batch size, parameters, activations, sequence length, or sparse expert capacity. Each strategy trades memory and compute for communication and scheduling complexity.

---

## Question 39

**Why do checkpointing and restore tests matter in large training systems?**

### Sample Answer

Large training jobs fail often enough that checkpointing is part of the system design. A useful checkpoint must capture model weights, optimizer state, scheduler state, RNG state, data-loader position, config, and version metadata. For sharded training, restore logic must correctly map checkpoint shards back to ranks. Restore tests matter because an untested checkpoint may be unusable exactly when a multi-day run fails.

---

## Question 40

**What is LoRA and when would you use it?**

### Sample Answer

LoRA freezes the base model and trains small low-rank adapter matrices. The mental model is "frozen base weights plus small trainable adapters." It is useful when full fine-tuning is too expensive or when you want lightweight domain/task adaptation. The risks are base/adaptor mismatch, overfitting narrow data, and deployment confusion if the adapter is not tracked with the correct base model, tokenizer, and eval results.

---

## Question 41

**Why do dataset and checkpoint formats matter in AI infrastructure?**

### Sample Answer

Formats determine how efficiently and reliably bytes become batches or deployable artifacts. Parquet and Arrow are efficient for columnar data; JSONL is simple but inefficient at huge scale; WebDataset-style shards can work well for large multimodal datasets; `safetensors` can make model weight loading safer. Bad formats or sharding choices can bottleneck GPUs, make backfills painful, corrupt reproducibility, or make serving startup slow.

---

## Question 42

**What problem does a feature store solve?**

### Sample Answer

A feature store centralizes feature definitions and provides consistent offline and online access. It helps reduce training-serving skew, supports point-in-time correct training datasets, and gives serving systems low-latency feature lookup. The tradeoff is operational complexity: feature ownership, freshness, backfills, and online/offline consistency all need explicit management. For small systems, careful warehouse pipelines may be enough.

---

## Question 43

**What should a model registry track before a model is deployed?**

### Sample Answer

A model registry should track more than weights. It should include tokenizer, config, base model, adapters, training data version, code version, eval results, safety review, owner, deployment state, and rollback target. The registry turns an anonymous checkpoint into an auditable deployable artifact. Without this, teams cannot reliably compare, reproduce, approve, or roll back model versions.

---

## Question 44

**What CI checks are useful for ML research infrastructure?**

### Sample Answer

Useful checks include data transform unit tests, schema checks, shape tests, small training-loop smoke tests, checkpoint save/restore tests, deterministic eval harness tests, config validation, and launch tests for distributed jobs. The goal is to catch cheap failures before expensive GPU runs. Research code can stay flexible while still protecting the shared training and evaluation pipeline.

---

## Question 45

**What is the CUDA execution hierarchy, and why does it matter for AI workloads?**

### Sample Answer

CUDA work is organized as a grid of blocks, where blocks contain warps and warps contain threads. Threads execute lanes of work; warps execute in lockstep; blocks can cooperate through shared memory. This matters because GPUs are efficient when many threads run regular operations over large tensors with predictable memory access. Irregular branching, tiny kernels, bad tensor shapes, CPU-GPU transfers, and excessive synchronization can waste the hardware.

---

## Question 46

**Why can many small GPU operations be slower than one fused operation?**

### Sample Answer

Each GPU kernel launch has overhead, and intermediate tensors often require extra memory reads and writes. Many tiny operations can spend more time on launch overhead, synchronization, and memory movement than useful math. A fused operation does more work per launch and can keep intermediate values closer to the compute, which is why optimized kernels and compiler fusion matter for high-throughput ML systems.

---

## Question 47

**Why is one scale-up domain a natural boundary for an MoE layer?**

### Sample Answer

MoE routing creates all-to-all traffic: tokens on many GPUs may need to visit experts on many other GPUs, then return to be combined. Inside a scale-up domain, accelerators usually have much faster and denser interconnect. Across racks or scale-out links, bandwidth is lower and latency is higher. Keeping an expert-parallel MoE layer inside the fast domain avoids making all-to-all routing the bottleneck.

---

## Question 48

**Why does pipeline parallelism not automatically solve KV-cache memory pressure?**

### Sample Answer

Pipeline parallelism splits layers across stages, so it helps with model weight capacity. But to keep multiple stages busy, the system needs multiple micro-batches in flight. Splitting layers reduces the KV stored per stage, while more in-flight micro-batches increase the active sequence count. These effects can cancel, so pipeline parallelism is not a magic fix for long-context KV pressure. It also adds bubbles, scheduling complexity, and cross-stage latency.

---

## Question 49

**How can a distributed parallelism scheme slow research iteration?**

### Sample Answer

If the parallelism scheme assumes a specific architecture, model changes can become expensive. Pipeline boundaries may make cross-layer residual attention, alternating attention patterns, or uneven layer costs hard to implement. Expert placement may assume a fixed topology. When researchers avoid useful architecture changes because the infrastructure cannot support them, the system is constraining research instead of enabling it.

---
