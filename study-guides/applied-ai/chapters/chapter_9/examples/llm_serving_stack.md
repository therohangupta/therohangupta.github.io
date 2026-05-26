# High-Throughput LLM Serving Stack

LLM serving is a scheduling, memory, and latency problem.

## Request Path

```text
client
  -> API gateway
  -> auth / quota / validation
  -> router
  -> cache lookup
  -> queue / continuous batcher
  -> model runtime
  -> token streaming
  -> validation
  -> tracing and metrics
```

## API Layer

Responsibilities:

- request validation,
- auth and tenant context,
- quotas and rate limits,
- deadline handling,
- model route selection,
- streaming response.

Common tools:

- FastAPI,
- Starlette,
- gateway/proxy layer,
- Pydantic schemas.

## Serving Runtime

Options:

- vLLM for high-throughput LLM serving and continuous batching,
- TGI for Hugging Face text-generation serving,
- Triton Inference Server for heterogeneous model serving,
- Ray Serve for Python-native distributed serving.

## Core Serving Concepts

### Prefill

Processes the input prompt.

Cost depends on prompt length.

### Decode

Generates tokens one at a time.

Cost depends on output length and KV-cache reads.

### KV Cache

Stores attention keys and values for previous tokens.

Improves speed but consumes memory.

### Continuous Batching

Keeps GPUs busy by adding and removing requests dynamically as sequences progress.

Improves throughput but needs careful latency control.

## Caches

Possible caches:

- response cache,
- prompt-prefix cache,
- embedding cache,
- retrieval cache,
- metadata cache.

Cache keys should include:

- tenant,
- permission scope,
- model version,
- prompt version,
- retrieval index version,
- input hash.

## Metrics

Track:

- time to first token,
- time to final token,
- prompt tokens,
- output tokens,
- tokens per second,
- queue wait,
- GPU utilization,
- GPU memory,
- KV-cache usage,
- cache hit rate,
- fallback rate,
- cost per successful request.

## Failure Modes

- Long prompts dominate prefill.
- Long outputs dominate decode.
- KV cache limits concurrency.
- Queueing hides overload.
- Retries create storms.
- Fallback model silently lowers quality.
- Cache key leaks tenant data.
- Streaming disconnect does not cancel model work.

## Interview Framing

> I would design LLM serving around admission control, batching, KV-cache memory, streaming latency, model routing, fallback behavior, and stage-level observability. Request count alone is not enough; token counts and queue wait usually explain cost and latency.

