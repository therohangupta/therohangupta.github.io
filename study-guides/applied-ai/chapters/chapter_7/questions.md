---
layout: page
title: "Chapter 7 Questions: Production ML Systems"
guide_type: questions
---

# Chapter 7 — Practice Questions

Explanatory material for this chapter lives in [`guide.md`](guide.html).

---

# Common Interview Questions and Sample Answers

---

## Question 1

**How would you design a production LLM inference service?**

### Sample Answer

I would start by clarifying latency target, request rate, prompt and output length distribution, quality requirements, and cost constraints. Then I would put an API layer in front of a router, use cache where correctness allows it, batch requests through an inference engine such as vLLM or TGI, and instrument the whole path with metrics, logs, and traces. I would add timeouts, bounded retries, fallback models, circuit breakers, and canary deployment so failures degrade predictably.

---

## Question 2

**What is the difference between latency and throughput in LLM serving?**

### Sample Answer

Latency is how long one request waits. Throughput is how much work the system completes per unit time. In LLM serving, throughput should often be measured in tokens per second rather than just requests per second because requests have very different prompt and output lengths. Batching can improve throughput while hurting latency, so the right choice depends on the product's SLO.

---

## Question 3

**Why is time to first token different from time to final token?**

### Sample Answer

Time to first token includes routing, prompt construction, queueing, and prefill before the model can emit anything. Time to final token also includes the full decode loop for all generated output tokens. Streaming improves perceived latency by lowering the time before users see progress, but it does not necessarily reduce total compute.

---

## Question 4

**How does batching improve LLM serving performance?**

### Sample Answer

Batching lets the GPU process multiple requests together, which usually improves utilization and tokens per second. The tradeoff is queueing delay: a request may wait while the batch fills. For interactive systems, the batcher needs to balance hardware efficiency against latency SLOs.

---

## Question 5

**What is continuous batching and why is it useful?**

### Sample Answer

Continuous batching updates the active batch as requests arrive and finish instead of waiting for a fixed batch to complete. This is useful for decoder-only LLMs because output lengths vary. Finished sequences can leave the batch and new sequences can enter, keeping the GPU busier and reducing waste.

---

## Question 6

**Why is KV-cache management important?**

### Sample Answer

The KV cache stores attention state for previous tokens so decode does not recompute the whole sequence every step. It greatly improves inference speed, but it consumes GPU memory proportional to active sequences and sequence length. Poor KV-cache management can cause memory fragmentation, OOMs, reduced concurrency, or admission failures.

---

## Question 7

**When would you use a cache in an ML serving system?**

### Sample Answer

I would use a cache when repeated work is common and the cached result is safe to reuse. Examples include embedding caches, retrieval caches, exact response caches, and prompt-prefix caches. I would be careful about cache keys, user identity, model version, prompt version, and invalidation because a wrong cache hit can leak data or serve stale behavior.

---

## Question 8

**How can retries make an outage worse?**

### Sample Answer

Retries can multiply load during overload. If requests time out and every client retries immediately, the system receives more traffic exactly when it is least able to handle it. Good retry design uses backoff with jitter, caps attempts, avoids retrying non-idempotent operations, and propagates cancellation when the original request is no longer needed.

---

## Question 9

**How would you choose between a small model and a large model in production?**

### Sample Answer

I would treat it as a routing and product tradeoff. A small model is usually faster and cheaper but may have lower quality. A large model may handle harder requests but increases latency and cost. A common design routes easy or low-risk traffic to the small model and escalates complex or high-value traffic to the larger model, with metrics tracking quality, latency, and cost by route.

---

## Question 10

**What metrics would you monitor for an LLM inference service?**

### Sample Answer

I would monitor request rate, error rate, latency percentiles, time to first token, time to final token, queue wait time, prompt tokens, output tokens, tokens per second, GPU utilization, GPU memory utilization, KV-cache usage, cache hit rate, fallback rate, model version, and cost per request. Without token and route dimensions, latency and cost changes are hard to explain.

---

## Question 11

**What causes latency spikes in production ML systems?**

### Sample Answer

Common causes include traffic bursts, queue buildup, long prompts, long outputs, cold replicas, slow retrieval or database calls, GPU saturation, OOM recovery, bad batching behavior, and retries. I would use tracing to separate queue time, prefill time, decode time, dependency time, and postprocessing time.

---

## Question 12

**How would you deploy a new model version safely?**

### Sample Answer

I would version the model artifact, tokenizer, prompt, serving image, schema, and decoding parameters. Then I would run offline evaluation, shadow traffic if possible, canary a small percentage of production traffic, monitor quality and operational metrics, and keep rollback simple. Metrics should be segmented by model version so regressions are visible.

---

## Question 13

**What is a circuit breaker and how does it apply to model serving?**

### Sample Answer

A circuit breaker stops sending traffic to a dependency or model pool that appears unhealthy. In model serving, it can route away from replicas with high error rates, OOMs, or latency spikes. The fallback might be a different replica, smaller model, cached response, degraded feature, or clear error.

---

## Question 14

**What is batching collapse?**

### Sample Answer

Batching collapse happens when the system stops forming efficient batches, often because traffic is too bursty, request lengths are too heterogeneous, scheduler constraints are too strict, or memory pressure limits active sequences. The result is poor GPU utilization, lower tokens per second, and worse cost per token.

---

## Question 15

**How can cost explode in an LLM product?**

### Sample Answer

Cost can explode through long prompts, long outputs, retries, agent loops, low cache hit rates, routing too much traffic to large models, inefficient batching, abuse, and excessive logging. I would track token usage and cost by route, tenant, feature, and model version, then enforce quotas, context limits, and fallback policies.

---

## Question 16

**How do queues help and hurt production inference systems?**

### Sample Answer

Queues absorb bursts, decouple producers from workers, and allow controlled concurrency and retries. They hurt when they hide overload or add unacceptable waiting time for interactive requests. I would monitor queue length, age of oldest job, retry count, dead-letter rate, and cancellation rate.

---

## Question 17

**What is the role of Kubernetes in production ML serving?**

### Sample Answer

Kubernetes can manage deployments, service discovery, health checks, resource limits, rolling updates, node pools, and autoscaling hooks. It does not automatically solve ML serving. GPU workloads still need careful scheduling, warmup handling, memory planning, model loading, and rollout controls.

---

## Question 18

**When is quantization useful, and what is the risk?**

### Sample Answer

Quantization is useful when memory bandwidth, GPU memory, or cost limits serving. It can allow larger batches, cheaper inference, or deployment on smaller hardware. The risk is quality loss, especially on domain-specific edge cases, so it needs product-specific evaluation rather than only generic benchmarks.

---

## Question 19

**What is speculative decoding?**

### Sample Answer

Speculative decoding uses a smaller or faster draft model to propose tokens and a larger target model to verify them. It can reduce wall-clock decode time when the draft model is fast and its proposals are often accepted. It helps less when prefill dominates, acceptance rate is low, or orchestration overhead outweighs the decode savings.

---

## Question 20

**How would you debug a sudden increase in LLM serving latency?**

### Sample Answer

I would first segment latency into gateway, routing, cache, queue, prefill, decode, dependency, and postprocessing time. Then I would compare prompt length, output length, traffic mix, model version, cache hit rate, queue depth, GPU utilization, KV-cache usage, error rate, and retry rate before and after the spike. The goal is to find whether the system is doing more work, waiting longer, or using hardware less efficiently.

---

## Question 21

**Design exercise: how would you build a model-routing policy for cost and quality?**

### Sample Answer

I would define route classes based on difficulty, user tier, risk, latency target, and required tools or grounding. Easy low-risk requests can use a small model; hard, high-value, or policy-sensitive requests can escalate to a stronger model or verifier path. I would track quality, latency, cost, fallback rate, and user outcomes by route, then add evals specifically for router mistakes because bad routing silently sends hard work to weak models.

---

## Question 22

**Operational debugging: cost doubled overnight but traffic stayed flat. What do you check?**

### Sample Answer

I would compare token counts, output lengths, retry rates, agent step counts, cache hit rate, route mix, model versions, prompt versions, fallback frequency, and abuse patterns before and after the change. Flat request volume does not mean flat work. A prompt change, bad cache key, router regression, longer retrieved context, or retry storm can all multiply model work without increasing traffic.

---

## Question 23

**How would you debug model drift in production?**

### Sample Answer

I would first separate data drift, concept drift, and system regressions. Then I would compare current traffic to the training and previous production distributions using feature statistics, embedding distributions, input slices, labels or delayed outcomes, and model confidence. I would inspect whether a prompt, model version, retrieval index, upstream schema, or user population changed. The fix might be recalibration, retraining, routing, updated eval coverage, better monitoring by slice, or rollback if the drift came from a bad release.

---

## Question 24

**How would you serve an LLM to millions of users?**

### Sample Answer

I would design it as a routed, observable inference platform rather than one giant model endpoint. The system needs an API gateway, authentication, quotas, prompt construction, model routing, caching where safe, request batching, streaming responses, autoscaled inference workers, and fallbacks for overload or provider failure. I would optimize for tokens per second, time to first token, time to final token, GPU memory, KV-cache pressure, and cost per successful task. At large scale, the key controls are batching, admission control, model tiering, cache strategy, regional capacity, observability, and gradual rollouts.

---

## Question 25

**What is the difference between prefill and decode in LLM serving?**

### Sample Answer

Prefill processes the input prompt and builds the initial KV cache, so it often drives time to first token. Decode generates new tokens one at a time using the KV cache, so it often drives time to final token and tokens per second. Prefill is usually more compute-heavy over prompt tokens, while decode is often memory-bandwidth-heavy because each step reads weights and cached K/V state.

---

## Question 26

**How do chunked prefill, prefix caching, and PagedAttention improve LLM serving?**

### Sample Answer

Chunked prefill splits long prompt processing into smaller pieces so one long prompt does not monopolize the GPU. Prefix caching reuses cached K/V state for repeated prompt prefixes such as system prompts or templates. PagedAttention stores KV cache in fixed-size blocks to reduce memory fragmentation and support variable-length concurrent requests. They target different bottlenecks: scheduling fairness, repeated prefill work, and KV-cache memory management.

---

## Question 27

**When would disaggregated prefill and decode be useful?**

### Sample Answer

It is useful when prefill and decode have different resource needs or interfere with each other under mixed traffic. Prefill workers can be optimized for compute-heavy prompt processing, while decode workers can be optimized for memory-bandwidth-heavy token generation. The benefit is independent scaling and less interference; the cost is more complex scheduling, KV-cache transfer, and new failure modes.

---

## Question 28

**How would you use a roofline-style model to reason about LLM serving cost?**

### Sample Answer

I would compare compute time with memory time and treat latency as roughly the max of the two. Compute time scales with batch size and active parameters, while memory time includes reading model weights and reading KV cache for each active sequence. Batching amortizes weight reads, but compute and KV-cache reads still scale with tokens. This explains why cost per token improves with batching at first and then flattens.

---

## Question 29

**Why is there a lower bound on decode latency even with small batches?**

### Sample Answer

The system still has to read model weights and cached attention state from memory. Memory bandwidth is finite, so a forward pass cannot complete faster than the required memory movement allows. This is why simply reducing batch size cannot make latency arbitrarily small; it may reduce queueing, but it also worsens cost because weight reads are amortized over fewer tokens.

---

## Question 30

**Why are output tokens often more expensive than input tokens?**

### Sample Answer

Input tokens are usually processed in prefill, where many positions can be processed in parallel and weight reads are better amortized. Output tokens are generated during decode, one step at a time, and each step reads model weights and KV cache while producing only one new token per sequence. Decode is often memory-bandwidth-bound and has lower hardware utilization, so output tokens cost more.

---

## Question 31

**How should a serving system decide whether to store or rematerialize KV cache?**

### Sample Answer

It should compare expected reuse value against storage and retrieval cost. Hot prefixes may be worth keeping in HBM or host memory; warm prefixes may fit slower memory tiers; cold prefixes are often cheaper to recompute from token IDs. Rematerialization spends compute to save memory, while KV caching spends memory to save compute. The right choice depends on reuse probability, cache duration, memory tier bandwidth, and whether stored KV crowds out active serving work.

---

## Question 32

**How would you handle 10,000 concurrent requests to an LLM API?**

### Sample Answer

I would start outside-in. The API gateway authenticates requests, validates payloads, attaches tenant metadata, and rejects requests that violate policy before they spend GPU. Then token-aware rate limits and admission control enforce requests per minute, tokens per minute, concurrent requests, prompt length, output length, and spend quotas. I would use exact or semantic caching where correctness allows it, route requests to healthy model pools with token-aware load estimates, queue and continuously batch inference work, and autoscale on GPU-aware metrics such as queue age, active sequences, KV-cache pressure, tokens per second, and p95 latency. Circuit breakers should isolate failing dependencies, and dashboards should segment latency, cost, fallback rate, and cache hit rate by route and tenant.

---

## Question 33

**How would you prevent a denial-of-wallet attack on an inference API?**

### Sample Answer

Use token-aware quotas, not only request counts. A few huge prompts or long generations can cost more than many small requests. I would enforce per-tenant request limits, input-token limits, output-token limits, concurrency limits, maximum context length, maximum generation length, and daily spend caps. I would also add authentication, abuse detection, request validation, queue limits, and alerts on cost per tenant. The key is to reject expensive bad traffic before it reaches model workers.

---

## Question 34

**What should happen when the vector database goes down mid-query?**

### Sample Answer

The system should fail intentionally rather than letting requests pile up. A circuit breaker should detect timeouts or high error rates and move from closed to open, blocking further calls temporarily. The fallback depends on risk: return a temporary unavailable message, route to a degraded keyword index, use cached retrieval results, or answer only if the task is low risk and can be handled without retrieval. In half-open state, the system sends a small number of test requests to check recovery before restoring traffic.

---

## Question 35

**Why is round-robin load balancing often insufficient for LLM serving?**

### Sample Answer

LLM requests have highly variable cost. A short prompt with a 50-token answer is not equivalent to a long-context request generating 4,000 tokens. Round-robin ignores prompt length, expected output length, active sequences, KV-cache pressure, model loaded on each worker, queue depth, and tenant priority. Better load balancing uses inference-aware signals so long or expensive requests do not overload one worker while others appear healthy.

---

## Question 36

**p95 latency doubled after adding longer retrieved context. How would you debug it?**

### Sample Answer

I would split latency into retrieval, reranking, prompt construction, queueing, prefill, decode, and streaming. Longer context usually increases prefill cost and KV-cache pressure, which can also increase queueing by reducing concurrency. I would compare input-token distributions, queue time, prefill time, active sequence count, GPU memory, and batch efficiency before and after the release. Fixes might include context budgeting, reranking fewer chunks, separate pools for long-context requests, caching stable retrieval, or routing complex requests differently.

---

## Question 37

**How can caching create a security or correctness bug in an AI system?**

### Sample Answer

If cache keys omit tenant, user permissions, prompt version, model version, source freshness, or policy version, the system can serve another user's answer, stale policy, or output generated under old safety rules. Caching should be used only when correctness boundaries are represented in the key or the cached object is safe to share.

---

## Question 38

**What is the difference between data drift, concept drift, and label drift?**

### Sample Answer

Data drift means the input distribution P(X) changes. Concept drift means the relationship P(Y | X) changes, so the same inputs no longer imply the same outputs. Label drift means the base rate P(Y) changes. These require different responses: data drift may need monitoring and recalibration, concept drift may need new labels or retraining, and label drift may require threshold or prior adjustment. In production, diagnose drift by slices and by upstream changes, not just aggregate metrics.
