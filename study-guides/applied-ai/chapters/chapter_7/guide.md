---
layout: page
title: "Chapter 7: Production ML Systems"
guide_type: chapter
---

# Chapter 7 — Production ML Systems

This chapter turns learned behavior into a reliable product surface.

Chapter 5 answered: "How do learned systems improve?"

This chapter answers: "How do I serve, scale, observe, and operate them without blowing up latency, reliability, or cost?"

The interview angle is usually not "can you name Kubernetes and Redis." It is:

* can you decompose latency, throughput, cost, reliability, and availability?
* can you explain where inference time is actually spent?
* can you design serving paths with batching, queues, caches, routing, and fallbacks?
* can you predict production failure modes before they appear in dashboards?
* can you connect model behavior to infrastructure behavior?
* can you operate model access, rate limits, logging, and rollback without creating security leaks?

Security note: serving infrastructure is part of the trust boundary. Cache keys, logs, model routing, rate limits, abuse monitoring, and rollback all affect security. See [Chapter 8: Security, Privacy, and Trust Boundaries](../chapter_8/guide.html).

---

## Table of Contents

- TOC
{:toc}

---

# 1. The Core Mental Model

A production ML system is not just a model behind an API.

It is a control system around an expensive probabilistic function.

The model is only one part of the runtime path. Around it are routers, queues, batchers, caches, workers, databases, tracing systems, rollout controls, autoscalers, and fallback policies.

The simplest useful mental model is:

```text
request
  -> admission control
  -> routing
  -> cache lookup
  -> batching / queueing
  -> inference
  -> postprocessing
  -> logging / metrics / tracing
  -> response
```

Every step changes the system's behavior.

Routing changes which model sees the request. Batching changes latency and GPU utilization. Caching changes cost and tail latency. Queues absorb bursts but can hide overload. Retries improve transient reliability but can multiply traffic. Observability does not serve the request, but without it the system becomes impossible to operate.

The production question is never just "does the model work?"

It is:

* can the model work under real traffic?
* can the system keep working when dependencies fail?
* can operators see what is happening?
* can the team deploy changes without taking down users?
* can the business afford the resulting token and GPU spend?

---

# 2. Production Primitives

Production ML systems are built from a small number of operational primitives. These primitives are simple individually, but they interact in non-obvious ways.

## 2.1 Latency

Latency is the time a user waits for a result.

For LLM systems, latency has several parts:

* request parsing and authentication
* routing and policy checks
* prompt construction or retrieval
* queueing delay
* prefill time
* decode time
* streaming overhead
* postprocessing and validation
* network time

Two latency numbers matter most:

* **time to first token**, often dominated by routing, queueing, prompt construction, and prefill
* **time to final token**, often dominated by decode length and output token rate

This distinction is important because streaming can make a slow response feel responsive. A user may tolerate eight seconds to complete if the first token arrives in 500 milliseconds. They may abandon a request if nothing appears for four seconds, even if the final completion would have arrived soon after.

Interview framing:

> I would break latency into queueing, prefill, decode, orchestration, dependency calls, and network overhead. Then I would decide whether the target is time to first token, time to final token, or background completion time.

## 2.2 Throughput

Throughput is how much work the system completes per unit time.

For normal web services, throughput is often measured in requests per second. For LLM serving, request count alone is misleading because requests have different token lengths.

Better units include:

* input tokens per second
* output tokens per second
* requests per second by request class
* GPU tokens per second
* successful tasks per dollar

A system can have high request throughput but poor token throughput if every request is tiny. It can also have high token throughput but poor user experience if batching creates unacceptable queueing delay.

Throughput improves when the system uses hardware efficiently. In LLM serving, that usually means better batching, better KV-cache management, less idle GPU time, fewer redundant prefill computations, and more predictable request shapes.

## 2.3 Cost

Cost is the resource bill required to serve the workload.

In production LLM systems, cost comes from:

* GPU time
* CPU orchestration
* memory and storage
* network transfer
* vector database or retrieval infrastructure
* logging and tracing volume
* external model API calls
* engineering and operational complexity

Token cost is often the dominant variable. Long prompts increase prefill work. Long outputs increase decode work. Retries multiply both. Agent loops multiply them again.

Cost should be discussed as a product constraint, not just an infrastructure concern. A feature that requires ten model calls per user action may work technically but fail economically.

## 2.4 Reliability

Reliability is the probability that the system behaves correctly over time.

For ML systems, reliability includes normal distributed-systems reliability and model-specific reliability:

* service returns a response
* response meets latency SLO
* response is generated by the intended model version
* response follows the expected schema or policy
* fallback behavior is acceptable
* metrics and traces are recorded

A reliable ML system does not assume the model is always correct. It wraps inference in validation, timeouts, fallbacks, rollout controls, and measurement.

## 2.5 Availability

Availability is the fraction of time the system can serve requests.

A system can be available but degraded. For example, a product may remain online by routing users from a high-quality large model to a cheaper smaller fallback. Availability remains high, while quality drops.

This is often the right production choice. The system should make degradation explicit:

* full service
* slower but correct service
* cheaper fallback model
* cached response
* partial result
* graceful error

The important design question is not "can we avoid all failures?" It is "when a failure happens, what does the user see, what do operators see, and how quickly can the system recover?"

## 2.6 Failure Modes

A failure mode is a way the system breaks.

Production ML systems fail through interactions:

* a traffic spike increases queueing
* queueing increases latency
* clients retry
* retries increase traffic
* longer queues reduce batching quality
* GPU memory fragments or OOMs
* autoscaling starts too slowly
* dashboards show symptoms but not root cause

Strong system design answers name these cascades. Weak answers list isolated components.

---

# 3. The Serving System

A production inference system has two jobs:

1. turn requests into model executions
2. turn model executions into reliable product behavior

The first job is about serving mechanics. The second is about operational control.

For a small product, serving may look like:

```text
API server -> model API provider -> response
```

For a high-scale or low-latency system, it may look like:

```text
API gateway
  -> request router
  -> Redis cache
  -> priority queue
  -> batcher
  -> GPU inference workers
  -> streaming response channel
  -> metrics/logging/tracing
  -> Postgres audit record
```

The key design principle is separation of concerns.

The API layer should not know every GPU detail. The model worker should not own business routing policy. The metrics system should not be an afterthought. The cache should not silently change correctness. Each component should have a clear responsibility and a clear failure policy.

## 3.1 Outside-In Traffic and Resilience Stack

In interviews, many production AI questions are really asking whether you can reason from traffic at the boundary inward toward GPU work.

A strong outside-in flow is:

```text
client request
  -> API gateway
  -> authentication and quota check
  -> token-aware rate limit / admission control
  -> cache lookup
  -> router / load balancer
  -> queue or batcher
  -> model or retrieval dependency
  -> circuit breaker / fallback if dependency fails
  -> response, trace, and metrics
```

The order matters. You want to reject, defer, cache, or route work before spending scarce GPU cycles.

### API Gateway

The gateway is the single controlled entry point. It should handle authentication, request validation, tenant metadata, coarse routing, and policy checks before the request reaches model infrastructure.

For AI systems, the gateway is also a cost boundary. A malformed prompt, unauthorized tenant, or request over token limits should be blocked before it hits an embedding service, vector database, or inference worker.

Interview signal:

> When walking through a request lifecycle, start at the gateway. Do not jump directly to the model.

### Token-Aware Rate Limiting

AI systems should usually rate-limit by more than requests per minute.

Useful limits include:

* requests per minute,
* input tokens per minute,
* output tokens per minute,
* concurrent requests,
* maximum prompt length,
* maximum generated tokens,
* per-tenant daily spend.

This prevents denial-of-wallet failures. A client sending a few huge prompts can be more expensive than a client sending many tiny requests. A good quota system protects both availability and budget.

### Caching Before Expensive Work

Caching belongs early when correctness allows it.

Common cache targets:

* embedding results for repeated queries,
* retrieval results for stable indexes,
* prompt prefixes such as system instructions,
* model responses for deterministic or low-risk requests,
* semantic cache entries for near-duplicate questions.

Semantic caching is powerful but riskier than exact caching. The system needs similarity thresholds, tenant isolation, model/prompt version keys, and freshness rules. A wrong semantic cache hit can be worse than a slow miss because it returns plausible but unrelated content.

### Queues for Work That Does Not Need Synchronous Latency

Not every AI workload should block an HTTP request.

Queue-backed workers are a better fit for:

* document ingestion,
* batch summarization,
* offline evaluation,
* embedding backfills,
* dataset generation,
* report generation,
* long-running agent workflows.

Queues absorb bursts and decouple producers from consumers. They also introduce new obligations: idempotency, retry policy, dead-letter queues, job age monitoring, and cancellation. A queue that silently grows for hours is not resilience; it is delayed failure.

### Circuit Breakers for Dependency Failures

AI pipelines often call several dependencies in sequence: embedding service, vector store, reranker, model provider, tool API, database, and logging pipeline.

If one dependency starts timing out, the system should not keep piling traffic onto it until every caller is stuck. A circuit breaker has three states:

| State | Behavior |
| ----- | -------- |
| Closed | dependency receives normal traffic |
| Open | calls are blocked quickly and fallback behavior runs |
| Half-open | a small number of test calls check whether recovery happened |

For example, if the vector database times out, the system might return a grounded "temporarily unavailable" message, route to a degraded keyword index, or skip retrieval only for low-risk requests. The important point is to fail fast and intentionally instead of letting the backlog cascade.

### Load Balancing and Autoscaling

GPU-backed inference needs load balancing, but round-robin is often too naive. A 50-token response and a 4,000-token response are not equal work.

Better routing signals include:

* active sequence count,
* queue depth,
* KV-cache pressure,
* estimated input and output tokens,
* model loaded on the worker,
* health-check status,
* tenant priority,
* region and latency target.

Autoscaling should also be GPU-aware. CPU utilization can be low while GPU memory, decode slots, or queue depth are saturated. Good autoscaling signals include queue age, pending tokens, GPU memory utilization, tokens per second, p95 latency, and time to first token.

Cold starts matter. Loading a large model can take long enough that reactive autoscaling arrives too late for a traffic spike. For predictable daily patterns, use scheduled or predictive scaling in addition to reactive scaling.

### The Interview Pattern

For a prompt like "how would you handle 10,000 concurrent LLM requests?", answer as a chain:

1. Gateway authenticates, validates, and attaches tenant metadata.
2. Token-aware limits and admission control protect cost and capacity.
3. Exact or semantic caches skip safe repeated work.
4. Router/load balancer sends requests to healthy model pools using token-aware load estimates.
5. Queues and continuous batching smooth bursts and improve GPU utilization.
6. Circuit breakers isolate failing dependencies.
7. Autoscaling adds capacity using GPU-aware metrics and predictive schedules where possible.
8. Observability reports latency, queueing, tokens, cache hit rate, fallback rate, and cost by route and tenant.

---

# 4. System Components

## 4.1 Inference Service

The inference service is the runtime that executes the model.

It is responsible for:

* loading weights
* managing device memory
* tokenizing inputs
* scheduling inference work
* generating outputs
* returning tokens or final completions

For LLMs, the inference service must handle prefill, decode, KV cache, batching, streaming, and cancellation. This is why specialized serving stacks such as vLLM, TensorRT-LLM, and Hugging Face Text Generation Inference exist.

An interview answer should distinguish between a generic web server and an inference server. The web server handles HTTP. The inference server handles GPU scheduling and model execution.

### Prefill vs Decode

LLM inference has two different phases.

**Prefill** is the stage where the model reads the input prompt.

```text
prompt tokens -> forward pass -> initial KV cache
```

Prefill determines much of **time to first token**. It is relatively compute-heavy because the full prompt is available and can be processed in parallel.

**Decode** is the stage where the model generates new tokens one at a time.

```text
previous tokens + KV cache -> next token -> append to KV cache
```

Decode determines much of **time to final token**. It is sequential and often memory-bandwidth-heavy because each step reads model weights and cached attention state.

This distinction matters because the two phases stress hardware differently:

| Phase | Main pressure | User-facing metric |
| ----- | ------------- | ------------------ |
| Prefill | compute over prompt tokens | time to first token |
| Decode | memory bandwidth and KV-cache reads | tokens per second / time to final token |

### KV Cache Mechanics

During autoregressive decoding, future tokens need old keys and values.

They do not need old queries.

Mental model:

```text
for each new token:
  compute Q_t, K_t, V_t
  append K_t and V_t to cache
  attend Q_t over cached K/V
```

Without a KV cache, every new token would recompute K and V for all previous tokens. With a KV cache, each token's K/V is computed once and reused.

The cache grows with:

* number of layers,
* sequence length,
* batch size / active requests,
* number of KV heads,
* head dimension,
* precision.

This is why long-context serving becomes a memory problem even when the model weights fit on the GPU.

### Chunked Prefill

Long prompts can monopolize GPU compute during prefill.

Chunked prefill breaks a long prompt into smaller chunks so the serving engine can interleave prefill work with decode work from other requests.

Mental model:

```text
one huge prefill
  -> blocks other requests

chunked prefill
  -> process prompt in pieces
  -> interleave with decode
```

The benefit is better latency fairness. The cost is more scheduling complexity.

### Prefix Caching

Many prompts share prefixes:

* system prompts,
* tool instructions,
* few-shot examples,
* policy text,
* repeated templates.

Prefix caching reuses the KV cache for identical prompt prefixes.

Mental model:

```text
shared prefix -> cached K/V -> skip repeated prefill work
```

This can improve time to first token and reduce compute, but the cache key must include correctness-relevant dimensions:

* model version,
* tokenizer,
* prompt text,
* system/developer instructions,
* tenant or permission scope when relevant.

### PagedAttention / Paged KV Cache

Naive KV cache allocation wants contiguous memory per request.

That is inefficient because requests:

* have different prompt lengths,
* generate different numbers of tokens,
* finish at different times,
* grow dynamically.

PagedAttention treats KV cache memory more like operating-system paging:

```text
logical token sequence
  -> fixed-size physical KV blocks
```

This reduces fragmentation and lets memory from finished requests be reused more flexibly.

### Continuous Batching

Static batching groups a fixed set of requests together.

The problem:

```text
some requests finish early
  -> empty slots remain
  -> GPU utilization drops
```

Continuous batching treats the active batch as a changing pool. As requests finish, new requests enter.

This keeps the GPU busier and is one reason modern LLM serving engines can achieve much higher throughput than naive batching.

### KV Cache Quantization

Quantization stores values in lower precision.

For a real value $x$, a simple quantization mental model is:

```text
real value -> scale and integer code -> approximate real value
```

KV cache quantization reduces VRAM and memory bandwidth pressure during decode.

Tradeoff:

* lower memory use,
* better throughput or concurrency,
* possible quality degradation,
* more implementation complexity.

### Speculative Decoding

Speculative decoding uses a smaller draft model to propose tokens and a larger target model to verify them.

Mental model:

```text
draft model proposes several tokens
  -> target model checks them in parallel
  -> accepted tokens are emitted
  -> rejected tokens are corrected
```

The goal is to reduce the number of slow sequential target-model decode steps.

It works best when:

* the draft model is much faster,
* the draft model's tokens are often accepted,
* decode is the bottleneck,
* orchestration overhead is low.

### Disaggregated Prefill and Decode

Prefill and decode have different resource profiles.

Disaggregated serving runs them on separate pools:

```text
prefill workers: compute-heavy prompt processing
decode workers: memory-bandwidth-heavy token generation
```

Benefits:

* scale prefill and decode independently,
* reduce interference between long prompts and generation,
* tune hardware or scheduling per phase.

Cost:

* KV cache transfer between pools,
* more complex scheduling,
* more failure modes.

Interview framing:

> I would reason about LLM serving by separating prefill and decode. Prefill is prompt processing and initial KV-cache construction; decode is sequential token generation and KV-cache reading. Optimizations like chunked prefill, prefix caching, PagedAttention, continuous batching, KV quantization, speculative decoding, and disaggregated prefill/decode each target a different bottleneck.

### Quantitative Serving Math: Roofline Intuition

A useful first-pass model for one forward pass is:

$$
T = \max(t_{\text{compute}}, t_{\text{mem}})
$$

The system is limited by whichever is slower: math or memory movement.

Ignoring attention compute for a simple estimate:

$$
t_{\text{compute}} = \frac{B \cdot N_{\text{active}}}{\text{FLOPs}}
$$

Where:

* $B$ is batch size,
* $N_{\text{active}}$ is the number of parameters active for a token,
* FLOPs is hardware compute throughput.

Memory time has two main pieces:

$$
t_{\text{mem}} =
\frac{N_{\text{total}} + B \cdot L_{\text{ctx}} \cdot \text{KV}_{\text{bytes/token}}}{\text{mem\_bw}}
$$

Where:

* $N_{\text{total}}$ is the total model weight footprint that must be read,
* $L_{\text{ctx}}$ is context length,
* $\text{KV}_{\text{bytes/token}}$ is KV-cache storage per token,
* $\text{mem\_bw}$ is memory bandwidth.

This simple equation explains several production facts:

* small batches are expensive because weight reads are not amortized,
* larger batches improve cost per token until compute or KV-cache reads dominate,
* decode is often memory-bandwidth-bound,
* long context becomes expensive because KV-cache reads grow with context length,
* output tokens are often more expensive than input tokens because decode cannot parallelize over many positions like prefill.

The key distinction:

```text
weight fetches can be amortized across a batch
KV cache fetches cannot be amortized in the same way because each sequence has its own context
compute cannot be eliminated because each token needs its own matrix multiplies
```

Interview framing:

> I would model an LLM forward pass with a roofline-style max of compute time and memory time. Batching amortizes weight reads, but KV-cache reads still grow with batch and context, which is why cost curves flatten instead of improving forever.

### Batch Size, Latency, and Cost Curves

As batch size increases:

* compute time grows roughly linearly,
* KV-cache memory time grows roughly linearly,
* weight-fetch memory time is mostly fixed for the forward pass.

Latency has a lower bound because the active serving hardware still has to read the model weights. You cannot push latency to zero by making batch size tiny.

Cost per token behaves differently because cost is roughly time divided by tokens served:

```text
cost per token = serving time / batch size
```

When batch size is small, the cost per token is high because each token pays for reading the weights. As batch size grows, the weight read is shared across more tokens. Eventually cost stops improving because compute and KV-cache work are per-token.

This explains "fast mode" and "slow mode" product behavior:

* fast mode may use smaller batches or higher-priority scheduling, improving latency at higher cost,
* slow mode can wait for larger batches, reducing cost up to a point,
* after the weight reads are already amortized, waiting longer does not make decode free.

### Optimal Batch Size Heuristic

A useful heuristic comes from setting compute time equal to weight-fetch memory time and ignoring KV cache:

$$
\frac{B \cdot N_{\text{active}}}{\text{FLOPs}}
=
\frac{N_{\text{total}}}{\text{mem\_bw}}
$$

Solving for batch size:

$$
B =
\frac{\text{FLOPs}}{\text{mem\_bw}}
\cdot
\frac{N_{\text{total}}}{N_{\text{active}}}
$$

Modern accelerators often have a rough ratio on the order of hundreds of low-precision operations per byte of memory bandwidth. If the ratio is approximately 300, then:

```text
optimal batch size is on the order of
300 * (total parameters / active parameters)
```

For a sparse MoE model, total parameters may be much larger than active parameters. That means a very sparse model can require larger batches to fully amortize weight movement.

This is not an exact serving formula. Real systems have attention kernels, routing, network communication, tokenizer overhead, scheduler behavior, and nonideal utilization. But it gives the right shape:

```text
more sparsity -> lower active compute
more sparsity -> more total weights
therefore -> larger batch needed to amortize weight reads
```

### HBM Drain Time and the Train Schedule

Another useful serving mental model is the "train schedule."

An inference engine repeatedly launches batches through the model. A practical cadence is shaped by how long it takes to read a large fraction of high-bandwidth memory:

$$
\text{drain time} \approx \frac{\text{HBM capacity}}{\text{HBM bandwidth}}
$$

For modern accelerator systems, this can land around tens of milliseconds.

Mental model:

```text
every ~t milliseconds:
  a batch "train" departs
  ready sequences board
  the model produces one decode token per sequence
```

If the train leaves too frequently, it cannot read the required memory fast enough. If it leaves too slowly, expensive compute sits idle.

This gives a lower bound on inter-token latency for a given serving configuration. It also explains why extremely low latency is hard: even perfect scheduling cannot bypass memory bandwidth.

### Reading API Prices as Cost Clues

Public API pricing often leaks serving economics.

Useful clues:

* **Output tokens cost more than input tokens:** decode is less efficient than prefill because it generates one token at a time and often waits on memory.
* **Long-context price jumps:** the provider may cross from compute-bound to KV-cache-memory-bound at long context lengths.
* **Cached input tokens are cheaper:** reading or reusing stored prefix state can be cheaper than recomputing the full prefix.
* **Different cache durations have different prices:** the provider may be using different memory or storage tiers.

You should not overfit to exact public prices, but you can infer the qualitative bottleneck:

```text
cheap prefill + expensive decode
  -> decode is memory-bandwidth constrained

price jump above long-context threshold
  -> KV-cache memory bandwidth/capacity is now material

cheap cached tokens
  -> rematerializing KV is more expensive than retrieving stored KV
```

### KV Cache Memory Tiers

There are two ways to recover prefix state:

1. **Rematerialize:** recompute KV cache from token IDs.
2. **Retrieve:** store KV cache somewhere and load it later.

Memory tiers create different tradeoffs:

| Tier | Mental model | Good for | Risk |
| ---- | ------------ | -------- | ---- |
| HBM | fastest device memory | very hot active prefixes | expensive capacity |
| Host DDR | slower but larger memory | warm reusable prefixes | transfer latency |
| Flash/object storage | cheap durable storage | longer-lived cache entries | slow retrieval |
| Rematerialization | recompute from tokens | cold or uncertain reuse | burns GPU compute |

A useful decision rule:

```text
store if expected reuse value > hold cost + retrieval cost
rematerialize if reuse is unlikely or storage would crowd out active work
```

For short-lived active conversations, HBM or host memory may make sense. For long-lived cache entries, slower tiers may be cheaper, but retrieval latency matters. For rarely reused prefixes, recomputation may be cheaper than paying to hold cached state.

This is the same memory/compute tradeoff seen elsewhere:

```text
KV cache:
  spend memory to save compute

activation rematerialization:
  spend compute to save memory
```

## 4.2 Request Router

The router decides where a request goes.

Routing can be based on:

* model version
* tenant
* priority
* region
* request size
* expected latency
* cost tier
* experiment assignment
* fallback policy

Model routing is especially important when a product uses multiple models. A simple request may go to a small fast model. A complex request may go to a larger model. A premium tenant may get a dedicated endpoint. A degraded cluster may route traffic away from an overloaded model pool.

Routing should be observable. If a bad rollout sends 20% of traffic to a broken model, operators need to see that immediately.

## 4.3 Batcher

The batcher groups requests so hardware can process them more efficiently.

Batching improves throughput because GPUs are built for parallel computation. But batching can hurt latency because requests wait for other requests to arrive.

The core tradeoff is:

```text
larger batches -> better GPU utilization, worse queueing latency
smaller batches -> lower queueing latency, worse utilization
```

LLM serving complicates this because requests have different prompt lengths and output lengths. Static batching wastes work when one request is much longer than the others. Continuous batching solves this by adding and removing requests as generation progresses.

## 4.4 Cache

The cache avoids repeated work.

Common caches include:

* response cache for exact repeated prompts
* embedding cache for repeated documents
* retrieval cache for repeated queries
* prompt-prefix cache for shared system prompts or conversation prefixes
* KV cache inside the inference engine

Caching is powerful but dangerous. A cache key that ignores user identity can leak data. A cache key that ignores model version can serve stale behavior. A cache that stores low-quality generated answers can make failures persistent.

In interviews, explain what is cached, why it is safe to cache, how it is invalidated, and what happens on cache miss.

## 4.5 Queue

The queue buffers work between producers and workers.

Queues are useful when:

* traffic is bursty
* work can run asynchronously
* workers need controlled concurrency
* retries need backoff
* priority classes matter

Queues can also hide overload. If requests keep entering faster than workers can process them, the backlog grows. Users see increasing latency long before the service fully fails.

A production queue needs:

* backlog metrics
* age-of-oldest-job metrics
* dead-letter handling
* retry limits
* priority or fairness controls
* cancellation when the result is no longer needed

## 4.6 Worker

The worker executes jobs.

Workers may run CPU preprocessing, retrieval, inference calls, postprocessing, or background evaluation. In GPU serving, workers often map to model replicas or inference engine processes.

Important worker controls include:

* concurrency limits
* memory limits
* heartbeat checks
* graceful shutdown
* idempotency
* retry semantics

Workers should be designed so a single bad request cannot poison the whole pool. Large requests, malformed inputs, and pathological outputs need limits.

## 4.7 Metrics, Logging, and Tracing

Observability turns production behavior into evidence.

Metrics answer:

* how many requests are happening?
* how slow are they?
* how many fail?
* how full are queues?
* how utilized are GPUs?
* how much does each request class cost?

Logs answer:

* what happened for this request?
* which model version served it?
* which fallback path was used?
* what validation errors occurred?

Traces answer:

* where did time go?
* which dependency caused the delay?
* which step failed first?

For ML systems, observability should include model-specific dimensions:

* prompt token count
* output token count
* model version
* decoding parameters
* cache hit or miss
* route decision
* fallback reason
* safety or validation outcome

Without these dimensions, a dashboard may show "latency increased" but not whether the cause was longer prompts, queueing, decode speed, retrieval, retries, or a bad model rollout.

---

# 5. Common Technologies

Technology choices are less important than knowing what problem each technology solves.

## 5.1 vLLM

vLLM is an inference serving stack optimized for high-throughput LLM serving.

It is known for:

* continuous batching
* paged attention / paged KV-cache management
* OpenAI-compatible serving APIs
* efficient memory use for concurrent generation

The reason vLLM matters is not the brand name. It matters because naive LLM serving wastes GPU memory and struggles with variable-length generation. vLLM addresses that scheduling and memory-management problem.

## 5.2 TensorRT-LLM

TensorRT-LLM is NVIDIA's stack for optimized LLM inference on NVIDIA GPUs.

It is relevant when teams need:

* highly optimized kernels
* quantization support
* multi-GPU execution
* tight hardware-specific performance tuning

The tradeoff is operational complexity. A team may get better performance, but pay with a more specialized build, deployment, and debugging path.

## 5.3 Text Generation Inference

Hugging Face Text Generation Inference, often called TGI, is another production-oriented LLM serving stack.

It provides:

* model serving APIs
* batching support
* streaming
* metrics
* integration with Hugging Face models

TGI is often attractive when a team wants a practical serving path around Hugging Face model artifacts.

## 5.4 Ray Serve

Ray Serve is useful for scalable Python model serving and orchestration.

It can host deployments, route requests, scale replicas, and compose model pipelines. It is especially useful when inference is not just one model call but a graph of Python steps.

The tradeoff is that Ray adds its own operational model. It can simplify distributed serving, but teams still need to understand resource allocation, backpressure, and failure handling.

## 5.5 Kubernetes

Kubernetes is commonly used to run model-serving infrastructure.

It provides:

* deployment objects
* service discovery
* autoscaling hooks
* resource requests and limits
* rolling updates
* health checks
* node pools

Kubernetes does not automatically solve ML serving. GPU workloads require careful node selection, device plugins, memory planning, startup timing, and rollout controls.

## 5.6 Redis

Redis commonly appears as:

* a low-latency cache
* a rate-limit store
* a session store
* a lightweight queue
* a feature flag or routing metadata store

Redis is useful when millisecond access matters. It is risky when used as the only durable source of truth for important state.

## 5.7 Kafka and Queues

Kafka, SQS, Pub/Sub, RabbitMQ, Celery queues, and similar systems buffer and distribute work.

Use queues when work is asynchronous, bursty, retryable, or fan-out heavy. Avoid queues when the user requires tight synchronous latency and cannot tolerate backlog delay.

Kafka is especially useful for durable event streams, audit trails, analytics pipelines, and high-throughput decoupling between services.

## 5.8 Postgres

Postgres is often the durable control-plane database.

It may store:

* model versions
* deployment metadata
* evaluation results
* job records
* user feedback
* audit logs
* feature flags for small systems

Postgres is not usually in the hot inference path for every token, but it is often the system of record for product and operational state.

## 5.9 GPU Scheduling

GPU scheduling decides which work gets access to scarce accelerator resources.

Important concepts include:

* node pools
* GPU memory capacity
* model placement
* replica sizing
* multi-instance GPU partitioning where available
* priority classes
* preemption
* warm pools

GPU scheduling is harder than CPU scheduling because model weights are large, startup time is high, memory is finite, and workloads have variable sequence lengths.

## 5.10 Autoscaling

Autoscaling changes capacity based on load.

Common signals include:

* request rate
* queue depth
* queue age
* GPU utilization
* tokens per second
* latency percentiles

Autoscaling GPU inference is tricky because adding capacity is slow. A new replica may need to pull weights, allocate GPU memory, warm kernels, and join the router. For bursty traffic, teams often need warm capacity, queue-based scaling, and admission control.

---

# 6. Inference Implementation Details

## 6.1 Batching

Batching combines multiple requests into one model execution step.

For encoder-style models or small classifiers, batching is straightforward: group inputs, run the model, split outputs.

For decoder-only LLMs, batching has two phases:

* **prefill**, where the model processes the input prompt
* **decode**, where the model generates one or more output tokens at a time

The challenge is that requests finish at different times. If static batching waits for every request to complete, short requests are stuck behind long requests.

## 6.2 Continuous Batching

Continuous batching keeps the GPU busy by updating the active batch as requests arrive and finish.

Instead of:

```text
batch A starts
batch A fully finishes
batch B starts
```

the system does:

```text
active batch runs decode step
finished sequences leave
new sequences enter
active batch runs next decode step
```

This improves utilization and reduces wasted time, especially when output lengths vary.

The tradeoff is scheduler complexity. The serving engine must manage active sequences, KV-cache blocks, fairness, cancellation, and memory pressure.

## 6.3 KV-Cache Management

The KV cache stores attention keys and values for previous tokens so the model does not recompute them at every decode step.

Without KV caching, each generated token would require repeatedly processing the whole sequence. With KV caching, decode can reuse prior attention state.

The problem is memory.

KV-cache memory grows with:

* number of active requests
* sequence length
* number of layers
* hidden size
* attention head configuration
* precision

When concurrency rises, KV cache can become the limiting resource before raw compute does. Poor KV-cache management causes OOMs, evictions, cache fragmentation, or admission failures.

Paged KV-cache approaches treat cache memory more like virtual memory: allocate blocks as needed, reuse freed blocks, and reduce fragmentation.

For the model-architecture side of this tradeoff, see Chapter 0's discussion of MHA, MQA, GQA, and MLA. Those choices determine how much K/V state exists before the serving system has to manage it.

## 6.4 Streaming

Streaming sends partial output as it is generated.

Streaming helps because it improves perceived latency. It does not necessarily reduce total model work.

A streaming service must handle:

* client disconnects
* cancellation propagation
* partial output logging
* timeout policy
* backpressure when clients read slowly
* errors after some tokens have already been sent

The last point matters. Once a system has streamed partial output, it cannot pretend the request never happened. Error handling must be designed around partial completion.

## 6.5 Async Handling

Inference services often need asynchronous request handling because model calls are slow relative to normal HTTP operations.

Async handling allows the server to:

* accept many connections
* wait on queues or model workers without blocking threads
* stream tokens
* cancel work when clients disconnect
* enforce timeouts

Async is not magic throughput. The GPU still has finite capacity. Async improves orchestration efficiency, not model capacity.

## 6.6 Retries and Timeouts

Timeouts bound waiting. Retries recover from transient failures.

Together, they can also cause overload.

If a service times out after ten seconds and every client retries immediately, the system may double its load exactly when it is least able to handle it. Retrying long inference requests is especially expensive because repeated work consumes tokens and GPU time.

Good retry design includes:

* retry only idempotent operations
* use exponential backoff with jitter
* cap retry attempts
* avoid retrying requests that are still running
* propagate request IDs
* distinguish queue timeout, model timeout, and downstream timeout

For LLMs, cancellation matters. If the client gives up, the server should stop generation when possible.

## 6.7 Model Routing

Model routing maps requests to models.

Common routing patterns:

* small model for easy requests, large model for hard requests
* specialized model for a domain
* region-local model for latency
* cheaper model for free tier
* fallback model during outage
* canary model for experiments

Routing can optimize quality, cost, latency, or availability. It rarely optimizes all four at once.

A strong answer explains the routing objective and the failure policy. If the router misclassifies request difficulty, quality may fall. If the router routes too much traffic to the large model, cost explodes. If fallback routing hides failures, teams may not notice quality degradation.

## 6.8 Quantization

Quantization reduces numerical precision to reduce memory use and improve throughput.

Examples include int8, int4, FP8, and mixed-precision approaches.

Quantization can help by:

* fitting larger models on available GPUs
* increasing batch size
* reducing memory bandwidth pressure
* lowering cost per token

The cost is possible quality loss, hardware-specific behavior, and extra validation burden. A model that looks fine on generic benchmarks may degrade on the product's important edge cases.

## 6.9 Speculative Decoding

Speculative decoding uses a smaller or faster draft model to propose tokens, then a larger target model verifies them.

The goal is to reduce wall-clock decode time while preserving the target model's output distribution when implemented correctly.

It works best when:

* the draft model is much faster
* the draft model predicts tokens the target model often accepts
* decode time is the bottleneck

It helps less when prompts are short and prefill dominates, when the draft model has low acceptance, or when orchestration overhead cancels the gain.

## 6.10 Fallbacks and Circuit Breakers

Fallbacks define what happens when the preferred path fails.

Circuit breakers stop sending traffic to a failing dependency or model pool.

Fallback options include:

* retry a different replica
* route to a smaller model
* return a cached response
* provide a partial answer
* degrade a feature
* return a clear error

Fallbacks should be explicit product decisions. A fallback that silently returns lower-quality output may preserve uptime but damage trust.

## 6.11 Version Compatibility

Model deployments need version control just like software deployments.

Track:

* model artifact version
* tokenizer version
* prompt version
* serving image version
* decoding parameters
* schema version
* evaluation suite version
* rollout percentage
* adapter version, when PEFT or LoRA is used
* teacher or reference checkpoint, when the model came from distillation or reference-guided training
* reward model, verifier, or judge version, when those systems shaped the update
* teacher prompt or privileged context template, when self-distillation used extra context

A surprising number of production bugs come from mismatched versions. A new model with an old tokenizer, a new prompt with an old parser, or a new schema with an old client can break the system even if each component works alone.

Reference-guided updates make this more important. A distilled student is not only "model v17." Its behavior depends on the teacher checkpoint, rollout data, reference policy, judge prompt, relevance mask settings, eval suite, and promotion gate that produced it. If those artifacts are not tracked together, regressions become hard to reproduce.

---

# 7. Deployment and Versioning

Deployment is the process of changing production behavior safely.

A good deployment path answers:

* what changed?
* who receives it?
* how do we measure it?
* how do we roll it back?
* what happens to in-flight requests?

Common rollout patterns include:

* **blue-green deployment**, where traffic switches between two environments
* **rolling deployment**, where replicas update gradually
* **canary deployment**, where a small percentage receives the new version first
* **shadow deployment**, where the new model receives copied traffic but does not affect users
* **A/B testing**, where versions are compared under controlled assignment

For ML systems, deployment also includes quality validation. A new model may be faster and still worse. A new quantization setting may lower cost and subtly break important tasks. A new prompt may improve average quality while increasing refusal rate.

The rollout metric set should include:

* error rate
* latency percentiles
* queue depth
* token usage
* cost per request
* cache hit rate
* validation failure rate
* user-visible quality metrics
* fallback rate

Rollback should be boring. If rollback requires rebuilding images, manually editing routes, or guessing which model artifact was deployed, the system is not production-ready.

For teacher-student or reference-guided systems, rollback may also require quarantining bad training data. If a bad canary generated logs that later entered a distillation run, simply rolling back the served model is not enough. The training dataset, teacher choice, and affected trajectories should be marked so future updates do not learn from contaminated behavior.

---

# 8. Performance Analysis

Performance analysis starts by asking where time and money go.

## 8.1 Where Time Is Spent

For an LLM request, wall-clock latency often looks like:

```text
total latency =
  gateway overhead
  + prompt construction
  + retrieval or tool calls
  + queueing delay
  + prefill time
  + decode time
  + postprocessing
  + network streaming overhead
```

If time to first token is bad, investigate:

* routing overhead
* cache lookup
* prompt construction
* retrieval latency
* queueing delay
* prefill length
* cold model replicas

If time to final token is bad, investigate:

* output length
* decode tokens per second
* batching behavior
* GPU memory pressure
* slow client streaming
* postprocessing and validation

## 8.2 What Costs Tokens

Token cost is not just the user's visible prompt.

It includes:

* system prompts
* developer instructions
* conversation history
* retrieved documents
* tool outputs
* few-shot examples
* hidden reasoning or intermediate steps when used
* retries
* fallback attempts
* generated output

Cost control often starts with context control. Shorter prompts, better retrieval, summarization, prompt-prefix caching, and smaller model routing can reduce cost without changing the product surface.

## 8.3 Wall-Clock Latency vs Compute Work

Wall-clock latency and compute work are related but not identical.

Batching can increase per-request waiting time while improving total tokens per second. Streaming can improve perceived responsiveness without reducing total compute. Caching can reduce both latency and compute if hit rates are high. Retries increase compute and often worsen latency.

This is why production systems must optimize against the correct objective. A background summarization job can maximize throughput. An interactive chat product may sacrifice throughput for low time to first token.

## 8.4 GPU Utilization Bottlenecks

Low GPU utilization can come from:

* small batches
* CPU preprocessing bottlenecks
* tokenizer bottlenecks
* slow networking
* poor request scheduling
* memory-bound decode
* frequent model loading
* waiting on retrieval or tools

High GPU utilization can also be bad if latency SLOs are missed. A saturated GPU may look efficient while users experience long queues.

Useful serving metrics include:

* GPU utilization
* GPU memory utilization
* tokens per second
* prefill tokens per second
* decode tokens per second
* active sequences
* pending queue length
* KV-cache usage
* batch size distribution
* time to first token
* time to final token

---

# 9. Reliability Patterns

## 9.1 Admission Control

Admission control rejects or delays work before the system collapses.

It can enforce:

* maximum prompt length
* maximum output length
* tenant quotas
* concurrency limits
* queue length limits
* priority classes

Rejecting a request early is often better than accepting it into a queue that will time out anyway.

## 9.2 Backpressure

Backpressure tells upstream callers to slow down.

Without backpressure, overload propagates until everything fails. With backpressure, the system can preserve capacity for high-priority or already-admitted work.

Backpressure can be implemented through rate limits, queue limits, HTTP 429 responses, retry-after headers, or internal flow-control signals.

## 9.3 Idempotency

Idempotency means repeated execution of the same logical operation does not create duplicate side effects.

This matters when clients retry. A request to generate a draft may be safe to retry. A request that charges a customer, sends an email, or writes a final answer to a database needs an idempotency key.

## 9.4 Health Checks

Health checks should test real readiness.

For model serving, "process is alive" is not enough. A useful readiness check may need to verify:

* model weights are loaded
* GPU memory is allocated
* tokenizer is available
* inference engine can run a small request
* the replica is registered with the router

Readiness and liveness should be different. A slow warmup should not be killed repeatedly because the liveness probe is too aggressive.

## 9.5 Observability as a Feature

Observability is not optional instrumentation added after launch.

For production ML systems, observability is part of the feature because operators must understand quality, cost, and reliability at the same time.

A good trace for an LLM request includes:

* request ID
* tenant or traffic class
* model route
* model version
* prompt version
* input and output token counts
* cache events
* queue wait time
* prefill and decode timing
* fallback events
* validation result

Sensitive data must be handled carefully. Logging prompts can be useful for debugging, but it may create privacy, compliance, and retention risk.

---

# 10. Tradeoffs

Production ML systems are built out of competing constraints. A strong design makes the constraint explicit instead of pretending one architecture optimizes everything.

## 10.1 Latency vs Throughput

Batching improves hardware utilization, but waiting to form a batch increases queue time. Streaming improves perceived latency, but the backend still pays the full decode cost. Low-latency products often need smaller batches, stricter admission control, and fewer retries than offline workloads.

## 10.2 Quality vs Cost

Large models, rerankers, tool calls, and verification steps can improve quality, but they increase cost per request. The common pattern is route-based quality: cheap paths for easy requests, expensive paths for hard or high-value requests, and explicit escalation when confidence is low.

## 10.3 Simplicity vs Resilience

A single-model service is easier to operate. A service with fallback models, circuit breakers, shadow traffic, regional failover, and versioned prompts is harder to build but safer under production failures. The right complexity depends on user risk, traffic volume, and recovery expectations.

## 10.4 Cache Efficiency vs Correctness

Caching can reduce latency and cost dramatically, but wrong cache keys can leak data, serve stale policy, or ignore prompt/model version changes. Cache decisions should include tenant, permission, prompt version, model version, and freshness requirements when those affect correctness.

## 10.5 Model Routing vs Debuggability

Routing lets the system match request difficulty to model cost and capability. It also makes incidents harder to understand because the same user-facing feature may be served by many models, prompts, or inference pools. Every route needs segmented metrics, evals, and fallback behavior.

## 10.6 Utilization vs Tail Reliability

Driving GPUs near full utilization lowers cost per token, but leaves less slack for bursts, long-context requests, and retries. Interactive products usually reserve capacity or shed load earlier than offline systems because p95 and p99 latency matter more than average utilization.

---

# 11. Failure Modes in Production

## 11.1 Latency Spikes

Latency spikes can come from traffic bursts, long prompts, slow dependencies, cold replicas, GPU saturation, or queue buildup.

The fix depends on the cause. More replicas help if capacity is low. They do not help if every request waits on the same slow database query or if clients are sending huge prompts.

## 11.2 Batching Collapse

Batching collapse happens when the serving engine stops forming efficient batches.

Causes include:

* traffic too low or too bursty
* request lengths too heterogeneous
* scheduler settings too strict
* too many priority classes
* excessive cancellations
* memory pressure limiting active sequences

The symptom is poor GPU utilization and worse cost per token. Sometimes latency also worsens because the system loses throughput.

## 11.3 Cache Thrash

Cache thrash happens when the working set is larger than the cache or keys are too unstable to hit.

Symptoms include low hit rate, high eviction rate, and unpredictable latency. In LLM systems, cache thrash may affect response caches, retrieval caches, embedding caches, or prefix caches.

Bad cache keys can be worse than no cache. They can serve stale, cross-user, or cross-version responses.

## 11.4 OOMs

Out-of-memory failures often come from long sequences, too many active requests, oversized batches, model weight size, KV-cache growth, or fragmentation.

Mitigations include:

* prompt length limits
* output length limits
* smaller batches
* quantization
* better KV-cache paging
* admission control
* model sharding
* more memory per replica

OOMs should not be treated as random. They are usually a sign that memory capacity was not modeled against worst-case request shape.

## 11.5 Queue Backlogs

Queue backlogs mean arrival rate exceeds service rate.

A backlog may be acceptable for offline jobs. It is dangerous for interactive requests. Watch age of oldest job, not just queue length. A queue of 1,000 tiny jobs may be fine. A queue with one 30-minute-old interactive request is not.

Retries can make backlogs worse. So can autoscaling delays.

## 11.6 Bad Rollouts

Bad rollouts happen when a new model, prompt, parser, image, or routing policy breaks production.

Common causes:

* insufficient canarying
* missing rollback path
* version mismatch
* metrics not segmented by version
* shadow tests that did not cover real traffic
* quality regressions hidden by aggregate metrics

The solution is not "never deploy." The solution is controlled deployment with fast detection and easy rollback.

For distilled or reference-guided models, bad rollouts can also come from mismatched training lineage:

* student served with the wrong adapter,
* student distilled from a stale or low-quality teacher,
* reference policy changed but the KL assumptions were not revalidated,
* judge prompt changed and selected different token masks,
* teacher-generated data came from a failed canary or shifted product distribution.

Segment metrics by student version, teacher/reference version, adapter version, and traffic slice. Otherwise a regression may look like random model drift when it is actually an artifact mismatch.

## 11.7 Observability Gaps

An observability gap means the system fails but the team cannot explain why.

Examples:

* latency dashboard lacks queue time
* error dashboard lacks model version
* cost dashboard lacks token counts
* quality dashboard lacks route decisions
* traces omit fallback events

Observability gaps are production risks because they increase time to recovery.

## 11.8 Cost Explosions

Cost explosions happen when a system does much more model work than expected.

Causes include:

* longer prompts
* longer outputs
* retries
* agent loops
* low cache hit rates
* routing too much traffic to large models
* inefficient batching
* traffic abuse
* logging too much high-volume data

Cost needs alerts just like latency and errors. A system can be technically healthy and financially unhealthy.

---

# 12. What to Say in an Interview

When asked to design a production ML serving system, start with the workload.

Say:

> I would first clarify whether this is synchronous or asynchronous, the latency target, expected request rate, prompt and output length distribution, quality requirements, cost constraints, and failure policy.

Then decompose the serving path:

> I would put an API layer in front of a router, use cache where correctness allows it, queue or batch requests depending on latency tolerance, serve the model through an inference engine such as vLLM or TGI, and instrument the path with metrics, logs, and traces.

Then explain the key tradeoff:

> The main tension is latency versus throughput versus cost. Larger batches improve GPU utilization but increase queueing. Smaller models reduce latency and cost but may reduce quality. Caches reduce cost and latency but introduce invalidation and correctness risks.

Then cover reliability:

> I would use timeouts, bounded retries, circuit breakers, admission control, fallback models, canary rollouts, and clear rollback. I would track model version, prompt version, token counts, queue time, cache hit rate, fallback rate, and latency percentiles.

Then name failure modes:

> I would watch for latency spikes, queue backlogs, KV-cache memory pressure, OOMs, batching collapse, bad rollouts, observability gaps, and cost explosions.

This structure signals that you can reason across model behavior, infrastructure, and product constraints.

---

# 13. Takeaways

Production ML systems are controlled serving systems around expensive learned functions.

The model is important, but production behavior comes from the whole path:

* routing decides which model handles work
* queues and batchers decide how efficiently hardware is used
* caches decide what work can be skipped
* workers execute bounded units of computation
* timeouts, retries, and circuit breakers decide how failures propagate
* observability decides whether humans can debug the system
* deployment controls decide whether change is safe

The central tradeoff is:

```text
latency, throughput, cost, quality, and reliability cannot all be maximized at once
```

Strong engineers make the tradeoff explicit, measure it, and design failure behavior before production traffic finds the weak point.

---

# 14. What Comes Next

Chapter 6 focused on serving learned systems reliably.

Chapter 7 moves one level up: full system design.

Once you understand inference services, queues, routers, caches, fallbacks, observability, and rollout controls, you can compose them into larger product architectures: search assistants, agent platforms, recommendation systems, document intelligence systems, copilots, and enterprise AI workflows.

The bridge is:

```text
deployment becomes full system design
```

[Chapter 13](../chapter_13/guide.html) goes one layer deeper beneath this serving chapter. When Chapter 6 says batching, caching, routing, latency, cost, or scaling, Chapter 11 explains the mechanics: prefill vs decode, KV cache, PagedAttention, continuous batching, memory bandwidth, model compilation, quantization, and GPU-aware autoscaling.

Use this ownership split:

| Question | Chapter 6 Answer | Chapter 11 Answer |
| -------- | ---------------- | ----------------- |
| How should the service be operated? | routers, queues, caches, fallbacks, rollouts, observability | GPU workers, KV cache, kernels, memory bandwidth, compiler/runtime behavior |
| How should traffic be balanced? | load balancers, queues, rate limits, tenant controls | token-aware routing, active sequences, prefill/decode split, KV memory |
| How should latency be debugged? | traces, service dependencies, retries, cache hit rate | queue time, prefill, decode, CUDA sync, batching efficiency, GPU utilization |
| How should capacity be planned? | QPS, cost, reliability, autoscaling policy | input/output token distributions, tokens/sec, model load time, GPU memory, p99 headroom |

High-signal Chapter 11 mental models to reuse in production serving answers:

* request load balancing is not token load balancing,
* decode is often memory-bandwidth-bound,
* continuous batching fights output-length variance,
* long context is a KV-cache and prefill problem,
* capacity planning needs token distributions, not only QPS.

For a full scenario, see the [multi-tenant LLM inference platform capstone](../../capstones/multi_tenant_llm_inference_platform.html).
