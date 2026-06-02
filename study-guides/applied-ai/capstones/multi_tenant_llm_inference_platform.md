---
layout: page
title: "Capstone: Multi-Tenant LLM Inference Platform"
guide_type: capstone
---

# Capstone: Multi-Tenant LLM Inference Platform

## Problem

Design a platform that serves multiple LLMs for many internal and external tenants. The platform must support streaming chat, long-context requests, different model sizes, tenant quotas, security-sensitive routing, cost attribution, and reliable p95/p99 latency.

The goal is not only to call a model. The goal is to operate shared GPU infrastructure where tokens, memory, scheduling, and tenant isolation are first-class concerns.

## Clarifying Questions

* What models must be served, and which ones can be routed to external providers?
* What are the p50, p95, and p99 input and output token distributions?
* What are the latency SLOs for time to first token and full completion?
* Which tenants require isolated infrastructure or private model pools?
* Are requests mostly interactive, batch, agentic, or mixed?
* What is the expected peak load and burst pattern?
* What data classes are allowed in logs, caches, traces, and external providers?
* How should cost be attributed to tenants and teams?

## Requirements

Functional requirements:

* Serve multiple model families through a common API.
* Stream partial responses to clients.
* Route requests by model, data policy, tenant priority, and token budget.
* Enforce tenant quotas for requests, input tokens, output tokens, active sequences, and KV memory.
* Support long-context requests without damaging short interactive traffic.
* Expose observability for latency, tokens, queueing, GPU memory, and cost.

Non-functional requirements:

* Low p95/p99 time to first token for interactive traffic.
* High GPU utilization without letting batching destroy tail latency.
* Strong tenant isolation for sensitive workloads.
* Graceful degradation under overload.
* Safe rollout for new models, runtimes, prompts, and compiled engines.

## Success Criteria

The platform is successful if:

* interactive tenants meet time-to-first-token and p99 latency SLOs,
* high-priority tenants are isolated from noisy neighbors,
* GPU utilization is high without unbounded queue growth,
* long-context traffic has explicit budget and routing,
* every request has cost, route, token, and tenant attribution,
* sensitive data never routes to disallowed model providers,
* overload produces controlled rejections or degradations instead of cascading failure.

## High-Level Architecture

```text
client
  -> API gateway
  -> auth and tenant policy
  -> request classifier
  -> token estimator
  -> admission controller
  -> model and pool router
  -> token-aware queue
  -> GPU worker pool
  -> streaming gateway
  -> logs, traces, metrics, billing
```

## Request Flow

1. The gateway authenticates the caller and attaches tenant metadata.
2. The policy layer classifies data sensitivity and allowed providers.
3. The token estimator computes input tokens and expected output budget.
4. Admission control checks quotas, active sequence limits, KV memory budget, and pool health.
5. The router selects a model and GPU pool that satisfy policy and capacity constraints.
6. The worker streams tokens back through the streaming gateway.
7. Metrics, traces, billing records, and audit fields are written with redaction rules.

## Core Design Decisions

### Token-aware routing before request-count routing

LLM load is token load, not request load. The router estimates input tokens, expected output tokens, context length, priority, and tenant policy before placing work.

This avoids treating a 500-token request and a 60,000-token request as equivalent.

### Separate pools for incompatible traffic

Use distinct pools when traffic has different constraints:

* short interactive chat,
* long-context enterprise requests,
* batch jobs,
* regulated or private tenants,
* experimental models.

Mixing all traffic into one pool can improve average utilization but harm tail latency and isolation.

### Admission control over unbounded queues

The platform should reject, truncate, defer, or downgrade requests before queues become unbounded.

Admission checks:

* tenant token quota,
* active sequence limit,
* KV memory budget,
* max prompt length,
* expected output token cap,
* pool health,
* data routing policy.

### Continuous batching for decode efficiency

Workers should support continuous batching so new requests can enter and completed sequences can leave dynamically. This improves utilization under variable output lengths.

The scheduler still needs fairness: a few long completions should not starve many short interactive responses.

### Scheduling design

The scheduler should separate admission from execution. Admission decides whether the request is allowed to enter the system. Execution scheduling decides when it enters an active batch.

Useful scheduling controls:

* priority queues for interactive and high-value tenants,
* token budgets instead of request-only budgets,
* separate pools for long-context and batch traffic,
* max active sequences per tenant,
* output token caps,
* preemption or deferral for low-priority batch work.

### KV cache management as a first-class resource

KV cache memory grows with active sequences and context length. The platform should track KV cache blocks or an equivalent memory signal and expose it to admission control and autoscaling.

Long-context traffic should have explicit budget and routing rules.

KV cache policy should define:

* per-request maximum context,
* per-tenant KV memory budget,
* eviction or cancellation behavior under pressure,
* prefix-cache key boundaries,
* metrics for allocated blocks, fragmentation, and active sequences.

### Security-aware model routing

Routing should enforce data policy before cost optimization.

Examples:

* restricted tenants use private GPU pools,
* regulated data cannot leave approved providers,
* cross-tenant prefix cache reuse is disabled,
* sensitive traces are redacted or sampled differently,
* model routes are recorded for audit.

## Worker Design

Each worker owns one or more loaded models and exposes:

* model health,
* supported context length,
* active sequences,
* queue depth,
* KV cache usage,
* input tokens/sec,
* output tokens/sec,
* GPU memory,
* time to first token,
* error and OOM events.

The worker runtime can be vLLM, TensorRT-LLM, TGI, Triton, or another serving engine. The capstone answer should explain why the runtime fits the workload.

## Routing Algorithm

1. Authenticate the request and identify tenant policy.
2. Classify data sensitivity and allowed model providers.
3. Estimate input tokens and expected output tokens.
4. Check quotas and active sequence limits.
5. Select eligible model pools.
6. Score pools by queue time, token capacity, KV memory, priority, and cost.
7. Assign the request or return a controlled rejection.

## Capacity Planning

Inputs:

* request rate by tenant,
* input token distribution,
* output token distribution,
* concurrency,
* model sizes,
* context lengths,
* measured prefill and decode throughput,
* GPU type,
* failover headroom,
* p95/p99 latency SLO.

Estimate separately:

* prefill capacity for input tokens,
* decode capacity for output tokens,
* KV cache memory for active sequences,
* model weight memory,
* warm spare capacity,
* cost per successful task.

Capacity planning should use token distributions rather than only average QPS.

## Autoscaling and Failover

Scale on token-aware serving signals:

* queue time,
* active sequences,
* input tokens/sec,
* output tokens/sec,
* KV cache pressure,
* GPU memory,
* p95/p99 latency,
* rejection rate.

Failover options:

* route to warm replicas in another pool,
* downgrade to a smaller model,
* defer batch traffic,
* reduce max output tokens,
* return a clear capacity response for low-priority requests.

Model load time matters. If a model takes minutes to load, reactive autoscaling alone will not protect p99 latency; the platform needs warm capacity and predictive scaling for known bursts.

## Observability

Request-level metrics:

* tenant,
* model,
* route,
* input tokens,
* output tokens,
* queue time,
* prefill time,
* decode time,
* time to first token,
* total latency,
* admission decision,
* cache hit or miss.

Worker-level metrics:

* active sequences,
* KV cache usage,
* GPU utilization,
* GPU memory,
* tokens/sec,
* batch size,
* OOM events,
* model load time.

Tenant-level metrics:

* token usage,
* quota usage,
* cost,
* rejection rate,
* p95/p99 latency,
* noisy-neighbor incidents.

## Failure Modes

| Failure | Mitigation |
| ------- | ---------- |
| long-context tenant slows everyone | token-aware quotas and separate long-context pool |
| p99 latency spikes during bursts | queue-based autoscaling and admission control |
| CUDA OOM under variable traffic | KV cache limits, PagedAttention-style block management, active sequence caps |
| cold starts are too slow | warm pools and staged model loading |
| external provider receives restricted data | policy-enforced routing before provider selection |
| prompt prefix cache leaks context | tenant-aware cache keys and disabled cross-tenant reuse |
| batch jobs starve interactive traffic | priority queues and separate pools |
| new runtime causes quality drift | regression evals and staged rollout |

## Evaluation and Load Testing

Test with realistic distributions:

* short chat,
* long-context chat,
* batch summarization,
* high-priority tenant traffic,
* burst traffic,
* model failover,
* OOM and retry scenarios.

Measure:

* time to first token,
* end-to-end latency,
* throughput,
* GPU utilization,
* KV memory,
* rejection rate,
* cost per 1,000 output tokens,
* tenant fairness.

## Learning Loop

The platform should not automatically train on every trace. It should convert incidents and usage into safer system improvements:

* p99 latency incidents become load-test scenarios and release gates,
* OOMs become KV memory regression tests,
* quota violations become admission-control test cases,
* routing mistakes become policy tests,
* tenant complaints become fairness and noisy-neighbor slices,
* high-cost traces become prompt, retrieval, or model-routing optimization candidates.

Only privacy-eligible, policy-compliant traces should enter model improvement pipelines. Many serving failures should become evals, dashboards, routing rules, or capacity plans rather than training data.

## Rollout Plan

1. Start with one model and one internal tenant.
2. Add token-aware metrics before broad rollout.
3. Enable admission control in observe-only mode.
4. Turn on quotas for non-critical tenants.
5. Add long-context and batch pools.
6. Move sensitive tenants only after routing and logging policy are verified.
7. Roll out autoscaling after measuring model load time and warm capacity needs.

## Interview Answer

I would design the platform around token-aware, policy-aware scheduling. The API gateway authenticates requests and passes tenant policy to a router. The router estimates input and output tokens, checks quotas, selects an eligible model pool, and places the request into a token-aware queue. GPU workers use continuous batching and expose active sequences, KV memory, prefill time, decode time, and tokens/sec.

I would separate short interactive traffic from long-context and batch workloads because they stress the serving system differently. I would scale on queue time, active sequences, token throughput, KV memory, and p95/p99 latency, not CPU alone. For security, model routing enforces data classification before cost optimization, and caches, logs, and traces are tenant-aware.

The main tradeoff is utilization versus tail latency. Bigger batches improve throughput, but if the scheduler ignores prompt length, output length, and tenant priority, p99 latency and fairness will degrade. The system needs admission control, quotas, observability, and rollback paths so it fails predictably under load.
