---
layout: page
title: "Chapter 9: Software Engineering Fundamentals for AI Systems"
guide_type: chapter
---

# Chapter 9 - Software Engineering Fundamentals for AI Systems

This chapter covers the engineering layer underneath applied AI systems: Python runtime behavior, concurrency, profiling, SQL, data pipelines, and backend service design.

The goal is not to become a database or Python trivia machine. The goal is to explain how production AI systems actually run, fail, scale, and get debugged.

---

## Table of Contents

- TOC
{:toc}

---

# 1. The Core Mental Model

An AI product is not just a model.

It is software wrapped around an expensive, probabilistic component.

That means many "AI failures" are really software engineering failures:

* the API service accepts more work than workers can handle,
* the event loop is blocked by synchronous IO,
* a Python process leaks memory through an unbounded cache,
* a database query scans millions of rows on the hot path,
* a queue hides overload until latency explodes,
* a streaming pipeline silently changes feature distributions,
* a retry loop turns one failure into a traffic storm,
* a cache key forgets tenant or user identity,
* a schema change breaks prompt construction or feature generation.

The model may be the most visible part of the system, but the software around it decides whether the product is fast, reliable, debuggable, safe, and affordable.

A useful runtime mental model is:

```text
user request
  -> API gateway
  -> auth / quota / validation
  -> Python service
  -> database / cache / retrieval
  -> queue / worker / batcher
  -> model gateway or GPU worker
  -> postprocessing / validation
  -> metrics / logs / traces
  -> response
```

Every arrow can fail.

Strong applied AI engineers can reason about each layer:

* what it does,
* what it costs,
* how it fails,
* how to observe it,
* how to recover when it breaks.

The interview signal is not "can you recite the GIL" or "can you define sharding." The signal is whether you can connect fundamentals to production behavior.

For example:

* The GIL matters because CPU-bound Python threads will not parallelize tokenization, parsing, ranking, or feature transforms the way many people expect.
* SQL indexes matter because a retrieval or metadata query can dominate time to first token.
* Async matters because an orchestration service may wait on model APIs, vector databases, and tools at the same time.
* Streaming pipelines matter because stale or skewed features can make a model look broken even when the model artifact did not change.
* Profiling matters because guessing bottlenecks is usually wrong.

---

# 2. Python Runtime Fundamentals

Python is common in AI systems because it is productive and has the best ML ecosystem.

But production Python has sharp edges. You need to understand enough of the runtime to predict performance and failure modes.

## 2.1 CPython, Objects, and References

Most production Python means CPython.

In CPython, almost everything is an object:

* integers,
* strings,
* lists,
* dictionaries,
* functions,
* classes,
* exceptions,
* coroutines,
* modules.

Variables are references to objects, not boxes that directly contain values.

```text
name -> object
```

When you pass a list to a function, you pass a reference to the same list object. When you store a response payload in a cache, that cache holds a reference. When you append a request object to a global debug list, that object cannot be freed while the list still references it.

This matters for AI systems because requests can be large:

* prompts,
* retrieved documents,
* embeddings,
* token arrays,
* image payloads,
* traces,
* tool outputs,
* model responses.

One accidental reference to a large object can keep a lot of memory alive.

## 2.2 Reference Counting

CPython primarily uses reference counting.

Each object tracks how many references point to it. When the count reaches zero, CPython can deallocate the object immediately.

Simple example:

```text
x = large_payload      # refcount increases
y = x                  # refcount increases again
del x                  # refcount decreases
del y                  # refcount reaches zero, object can be freed
```

Reference counting gives CPython predictable cleanup for many objects. But it does not solve every memory problem.

An object will not be freed if something still references it:

* an unbounded cache,
* a global dictionary,
* a closure,
* a running task,
* a callback registry,
* a logger context,
* a trace buffer,
* a pending future,
* a cycle.

Production memory debugging often comes down to asking:

> What is still holding a reference to this object?

## 2.3 Cyclic Garbage Collection

Reference counting alone cannot clean cycles.

Example:

```text
object A -> object B
object B -> object A
```

If nothing else points to A or B, their reference counts are still nonzero because they point to each other.

CPython has a cyclic garbage collector that periodically finds groups of unreachable objects and frees them.

This matters when objects contain:

* parent pointers,
* graph structures,
* closures,
* callbacks,
* exception tracebacks,
* async tasks,
* objects with `__del__` finalizers.

Cycles are not automatically bad, but they make lifetime less obvious.

Interview framing:

> Python mainly uses reference counting, with cyclic GC for unreachable reference cycles. In production, leaks usually mean objects are still reachable through caches, globals, callbacks, tasks, or traces, not that Python forgot how to free memory.

## 2.4 Python Allocators and RSS

A common production confusion:

> "I deleted the object. Why did process memory not go down?"

The answer is that freeing Python objects does not always return memory to the operating system immediately.

CPython uses memory allocators that manage arenas and pools for small objects. Freed memory may stay available for future Python allocations inside the process. Your heap may be healthier even if RSS does not drop.

Important terms:

* **live objects:** objects still reachable and usable,
* **heap growth:** memory Python has allocated for objects,
* **RSS:** resident memory reported by the operating system,
* **fragmentation:** memory is free internally but not easily returned or reused in the pattern you need.

When debugging memory, do not rely on one number.

Use:

* RSS for process-level pressure,
* object counts by type,
* heap snapshots,
* allocation traces,
* cache sizes,
* request-level memory growth,
* worker restart frequency.

## 2.5 Production Memory Leak Patterns

Common leak patterns in AI backends:

### Unbounded Caches

```text
cache[prompt] = response
```

This looks harmless until prompts are unique and the cache grows forever.

Fixes:

* max size,
* TTL,
* tenant-aware keys,
* explicit invalidation,
* cache hit-rate monitoring.

### Trace and Logging Retention

AI traces can be huge. If a service stores full prompts, retrieved chunks, tool outputs, and responses in memory before flushing, memory can spike or leak.

Fixes:

* stream traces out of process,
* redact and truncate large fields,
* sample high-volume traces,
* avoid storing full payloads in exception objects.

### Callback and Task Leaks

Async systems often leak through pending tasks, callbacks, or futures that are never awaited or cancelled.

Fixes:

* timeouts,
* cancellation,
* task groups,
* cleanup handlers,
* monitoring for pending task counts.

### Global Registries

Registries for tools, prompts, metrics, or plugins can accidentally retain per-request objects.

Fixes:

* store configuration, not request state,
* avoid lambdas that close over large objects,
* clear per-request context after use.

### Native Extension Leaks

ML libraries often use native memory outside normal Python object accounting.

Examples:

* NumPy arrays,
* PyTorch tensors,
* tokenizers,
* image libraries,
* GPU memory allocations.

Fixes:

* monitor process RSS and GPU memory,
* release tensors and references,
* use inference mode where appropriate,
* isolate risky workloads in restartable workers.

## 2.6 Memory Debugging Checklist

When memory grows in production:

1. Identify whether growth is per request, per batch, per tenant, or over wall-clock time.
2. Compare RSS, heap snapshots, object counts, cache sizes, and native memory.
3. Reproduce with a representative workload.
4. Check unbounded dictionaries, lists, LRU caches, task registries, and trace buffers.
5. Look for large objects retained by closures, exceptions, callbacks, and globals.
6. Confirm whether memory stabilizes after load stops.
7. Add bounds, cleanup, streaming, or worker recycling.

Good interview answer:

> I would not say "Python has GC, so it cannot leak." Python leaks when objects remain reachable. I would profile object growth, inspect caches and references, check native memory, and add bounds or lifecycle cleanup.

---

# 3. Concurrency in Python

Concurrency is about dealing with multiple things in progress.

Parallelism is about executing multiple things at the same time.

They are related but not identical.

AI systems need both:

* concurrent API requests,
* concurrent retrieval calls,
* concurrent tool calls,
* parallel CPU preprocessing,
* parallel GPU inference,
* background workers,
* streaming responses,
* cancellation and timeouts.

## 3.1 The Three Main Tools

In Python, the main concurrency tools are:

| Tool | Best for | Main tradeoff |
| ---- | -------- | ------------- |
| Threads | IO-bound blocking libraries | Limited CPU parallelism under the GIL |
| Multiprocessing | CPU-bound Python work | More memory and serialization overhead |
| Asyncio | High-concurrency IO with non-blocking libraries | Requires async-compatible code |

The right question is not "which is best?"

The right question is:

> What is the bottleneck?

## 3.2 The GIL

The Global Interpreter Lock is a CPython mutex that allows only one thread to execute Python bytecode at a time within a process.

Why it exists:

* it simplifies CPython internals,
* it protects reference counting,
* it makes many object operations simpler.

What it means:

* CPU-bound Python threads do not run Python bytecode in parallel,
* IO-bound threads can still overlap while waiting,
* native extensions can release the GIL,
* multiprocessing can use multiple CPU cores,
* async can handle many IO waits in one thread.

The GIL does not mean Python can only do one thing at a time. It means pure Python CPU work does not parallelize across threads in a single CPython process.

Interview framing:

> The GIL mostly hurts CPU-bound Python threading. It matters less for IO-bound services, and it can be bypassed with multiprocessing, native extensions, vectorized libraries, or separate services.

## 3.3 Threading

Threads are useful when code blocks on IO:

* database calls,
* HTTP requests,
* file reads,
* model API calls through blocking clients.

Threads let one request wait while another makes progress.

But threads have costs:

* context switching,
* shared-memory bugs,
* locks,
* harder debugging,
* no pure-Python CPU parallelism under the GIL.

Use threads when:

* your libraries are blocking,
* the work is IO-bound,
* concurrency is moderate,
* you need a simple integration.

Avoid threads as the primary solution for:

* CPU-heavy feature transforms,
* large JSON parsing at high volume,
* embedding postprocessing in pure Python,
* workloads requiring strict cancellation semantics.

## 3.4 Multiprocessing

Multiprocessing runs separate Python processes.

Each process has its own interpreter and its own GIL. That means CPU-bound Python work can run in parallel across cores.

Useful for:

* CPU-heavy preprocessing,
* batch feature transforms,
* image processing,
* parsing large files,
* isolation of risky or leaky work.

Tradeoffs:

* higher memory use,
* process startup cost,
* serialization and IPC overhead,
* harder shared state,
* deployment complexity.

In AI systems, multiprocessing is often used for worker pools and background jobs rather than request-path orchestration.

## 3.5 Asyncio

Asyncio uses an event loop.

Coroutines voluntarily yield control when they hit an `await`.

```text
request A starts DB call -> awaits
request B starts model call -> awaits
request C validates input -> completes
DB result returns -> request A resumes
```

Async is excellent for orchestration services that wait on many network calls:

* model APIs,
* vector databases,
* SQL databases with async drivers,
* object stores,
* tool services,
* streaming clients.

Async fails when you block the event loop:

* synchronous HTTP call,
* synchronous database driver,
* CPU-heavy parsing,
* large JSON serialization,
* `time.sleep`,
* long loop without `await`.

If one coroutine blocks the event loop, all other coroutines wait.

Interview framing:

> Async improves concurrency for IO-bound work. It does not make CPU-bound work faster. In an async service, every dependency on the hot path must be non-blocking or moved to a worker.

## 3.6 Backpressure

Backpressure means the system refuses or slows new work when downstream capacity is saturated.

Without backpressure:

```text
traffic spike -> queue grows -> latency rises -> clients retry -> traffic grows more
```

Backpressure tools:

* bounded queues,
* semaphores,
* admission control,
* rate limits,
* per-tenant quotas,
* load shedding,
* circuit breakers,
* deadlines and cancellation.

AI systems need backpressure because model calls are expensive and slow compared with normal web requests.

If work cannot be served within its deadline, it is often better to reject early than to let it sit in a queue and fail late.

## 3.7 Cancellation and Timeouts

Every external call should have a timeout:

* retrieval,
* database query,
* model call,
* tool call,
* object-store read,
* streaming write.

Cancellation matters because users leave, clients disconnect, and upstream deadlines expire.

If cancellation does not propagate, the system keeps doing useless work:

```text
user disconnects
  -> API task continues
  -> model call continues
  -> worker produces response nobody receives
  -> cost is still paid
```

Good systems propagate deadlines through the request path.

---

# 4. Python Abstractions That Matter

Python lets you build powerful abstractions quickly. That is useful in AI systems, where teams often need rapid iteration over prompts, tools, models, schemas, and workflows.

But dynamic abstractions can hide control flow and make production failures harder to debug.

## 4.1 Decorators

A decorator is a callable that takes a function or class and returns a replacement.

```text
@decorator
def f():
    ...

# roughly means:
f = decorator(f)
```

Common production uses:

* tracing,
* retries,
* auth checks,
* caching,
* timing,
* rate limiting,
* tool registration,
* schema validation.

Example mental model:

```text
function call
  -> wrapper
  -> pre-work
  -> original function
  -> post-work
  -> return
```

Decorators are useful when the behavior is cross-cutting and consistent.

They are dangerous when they hide:

* network calls,
* retries with side effects,
* swallowed exceptions,
* global state mutation,
* performance overhead.

Production rule:

> A decorator should make behavior easier to see at the call site or in traces, not harder.

## 4.2 Metaclasses

Metaclasses control class creation.

Most engineers rarely need them.

They can be useful for:

* frameworks,
* ORMs,
* plugin systems,
* schema registration,
* validation at class definition time.

But they are often overkill. Many use cases can be solved with:

* class decorators,
* base classes,
* registries,
* dataclasses,
* explicit factory functions.

Interview framing:

> A metaclass is the class of a class. It customizes how classes are created. I know what it is, but I would avoid it unless I am building framework-level behavior where class construction itself needs control.

## 4.3 Dynamic Typing and Runtime Validation

Python is dynamically typed. That helps speed, iteration, and expressiveness.

But AI systems often need strict boundaries:

* model output schemas,
* tool arguments,
* API payloads,
* database records,
* event schemas,
* feature rows.

The safest pattern is:

```text
dynamic inside the implementation
strict at boundaries
```

Useful tools:

* type hints,
* dataclasses,
* Pydantic models,
* JSON Schema,
* database constraints,
* runtime validators,
* static type checking where practical.

This matters because LLM outputs are probabilistic. The system should validate before trusting them.

## 4.4 Idempotency as a Software Abstraction

Idempotency means repeating an operation has the same effect as doing it once.

This is essential for:

* retries,
* queues,
* distributed workers,
* agent tool calls,
* payment or email actions,
* data pipeline writes.

A common pattern:

```text
idempotency_key = stable key for the intended action

if action already completed:
    return stored result
else:
    perform action
    store result
```

In AI systems, the model may request the same tool twice, a worker may retry after timeout, or a client may resubmit a request. Idempotency prevents duplicate side effects.

---

# 5. Profiling and Debugging Python Services

Performance work starts with measurement.

Guessing is expensive because AI systems have many possible bottlenecks:

* Python CPU,
* model latency,
* database latency,
* retrieval latency,
* queue wait,
* network time,
* serialization,
* logging,
* tokenization,
* GPU memory,
* downstream tools.

## 5.1 CPU Profiling

Use CPU profiling when the process is actively computing.

Tools and approaches:

* `cProfile` for deterministic profiling,
* sampling profilers such as py-spy,
* flame graphs,
* targeted timers around expensive functions,
* benchmark scripts with realistic inputs.

Common CPU hotspots in AI systems:

* tokenization,
* JSON parsing,
* prompt formatting,
* embedding postprocessing,
* reranking,
* data validation,
* compression,
* encryption,
* pandas transformations,
* large object serialization.

Do not optimize code that is not on the hot path.

## 5.2 Memory Profiling

Use memory profiling when RSS grows, workers OOM, or latency degrades after running for a while.

Look at:

* object counts by type,
* allocation stack traces,
* cache sizes,
* large strings and lists,
* pending tasks,
* exception tracebacks,
* tensor and native memory,
* per-request memory deltas.

Tools and techniques:

* `tracemalloc`,
* heap snapshots,
* object graph inspection,
* process RSS metrics,
* GPU memory metrics,
* controlled load tests.

## 5.3 Latency Profiling

A production request trace should break latency into stages:

```text
ingress
  -> auth
  -> validation
  -> queue wait
  -> database
  -> retrieval
  -> model prefill / API wait
  -> decode / streaming
  -> postprocessing
  -> response write
```

For LLM backends, track at least:

* time to first token,
* time to final token,
* prompt tokens,
* output tokens,
* queue wait,
* model route,
* model version,
* prompt version,
* cache hit/miss,
* retrieval time,
* database time,
* retry count.

Latency without dimensions is hard to debug.

## 5.4 Microbenchmarks vs Production Profiles

Microbenchmarks answer:

> How fast is this function in isolation?

Production profiles answer:

> Where does real user time go?

Both matter.

Microbenchmarks can miss:

* network variance,
* queueing,
* locks,
* GC behavior,
* cold starts,
* large payloads,
* noisy neighbors,
* retries,
* batching effects.

Use microbenchmarks for local code choices. Use traces for system choices.

## 5.5 Debugging Playbook

When a Python AI service is slow:

1. Check whether latency increased for all traffic or only a slice.
2. Split latency by stage.
3. Check request sizes: prompt tokens, retrieved chunks, output tokens, payload bytes.
4. Check queue wait and concurrency.
5. Check database and retrieval timings.
6. Check CPU and memory.
7. Check retries and fallbacks.
8. Compare prompt/model/config versions.
9. Reproduce with a trace from production.

When a Python AI service leaks memory:

1. Confirm whether RSS grows without bound.
2. Compare live object growth and native memory growth.
3. Look for unbounded caches and registries.
4. Inspect pending tasks and futures.
5. Check trace/log buffers.
6. Check large objects retained by exceptions.
7. Add bounds, cleanup, streaming, or worker recycling.

---

# 6. SQL and Relational Systems

AI systems still depend heavily on relational databases.

They store:

* users,
* tenants,
* permissions,
* documents,
* metadata,
* tool state,
* traces,
* feedback,
* eval results,
* feature definitions,
* workflow state.

If the database layer is slow or inconsistent, the AI system will look slow or inconsistent.

## 6.1 Query Plans

To optimize SQL, start with the query plan.

The plan tells you how the database intends to execute the query:

* sequential scan,
* index scan,
* nested loop join,
* hash join,
* sort,
* aggregate,
* filter,
* partition pruning.

Bad signs:

* scanning far more rows than expected,
* joining large tables before filtering,
* sorting huge intermediate results,
* using the wrong index,
* inaccurate row estimates,
* repeated nested loops over large tables.

Strong interview framing:

> I would inspect the query plan first, identify whether the bottleneck is scan, join, sort, aggregation, or cardinality estimation, then change indexes, query shape, partitioning, or materialization based on the plan.

## 6.2 Indexes

An index speeds up lookup by maintaining a separate data structure.

Good for:

* exact lookups,
* range filters,
* joins,
* sorting,
* uniqueness constraints.

Costs:

* extra storage,
* slower writes,
* maintenance overhead,
* planner complexity.

Index design should follow access patterns.

Examples:

```text
tenant_id + document_id
tenant_id + created_at
user_id + status
workflow_id + step_status
source_id + chunk_id
```

For multi-tenant AI systems, forgetting tenant in an index can make queries slow and make access control harder to reason about.

## 6.3 Partitioning

Partitioning splits a table into physical pieces.

Common partition keys:

* time,
* tenant,
* region,
* hash,
* product area.

Partitioning helps when queries can prune partitions.

Example:

```text
WHERE event_date >= '2026-05-01'
```

If the table is partitioned by date, the database can skip older partitions.

Bad partition keys create:

* hot partitions,
* too many tiny partitions,
* cross-partition queries,
* operational complexity.

## 6.4 Materialized Views

A materialized view stores query results.

Useful when:

* the query is expensive,
* reads are frequent,
* staleness is acceptable,
* refresh rules are clear.

Examples:

* daily feature aggregates,
* dashboard metrics,
* eval summary tables,
* tenant usage reports,
* retrieval quality reports.

Tradeoffs:

* stale data,
* refresh cost,
* storage cost,
* invalidation complexity.

Materialized views are not magic. They move work from read time to refresh time.

## 6.5 Transactions and Deadlocks

Transactions group operations so they succeed or fail together.

Deadlocks happen when transactions wait on each other:

```text
transaction A locks row 1, waits for row 2
transaction B locks row 2, waits for row 1
```

Prevention:

* consistent lock ordering,
* short transactions,
* narrow updates,
* good indexes,
* retry on deadlock,
* avoid user or model calls inside transactions.

AI-specific warning:

Do not hold a database transaction open while waiting for a model call or external tool. Model calls are slow and unreliable compared with database operations.

## 6.6 OLTP vs OLAP

OLTP systems serve transactions:

* user updates,
* workflow state,
* permissions,
* tool execution records,
* request metadata.

They optimize for low-latency reads/writes and consistency.

OLAP systems serve analytics:

* dashboards,
* aggregates,
* model training datasets,
* eval analysis,
* usage reporting.

They optimize for scanning and aggregating large data.

Mixing OLAP queries into OLTP databases can hurt user-facing latency.

Common pattern:

```text
OLTP database
  -> CDC or batch export
  -> warehouse / lake
  -> analytics / training / evals
```

---

# 7. Distributed Data Fundamentals

At scale, one database or one data store may not be enough.

Distributed data systems add capacity, but they also add failure modes.

## 7.1 Sharding

Sharding splits data across multiple database instances.

Example:

```text
tenant_id % number_of_shards -> shard
```

Benefits:

* more storage,
* more write capacity,
* tenant isolation,
* regional placement.

Costs:

* cross-shard queries,
* rebalancing,
* hot shards,
* operational complexity,
* harder transactions.

Good shard keys:

* distribute load,
* match common queries,
* minimize cross-shard operations,
* avoid one huge tenant dominating a shard.

## 7.2 Hot Shards

A hot shard receives too much traffic.

Causes:

* one large tenant,
* time-based writes all hitting the newest partition,
* celebrity users,
* skewed routing,
* batch jobs targeting one key range.

Mitigations:

* split large tenants,
* add sub-sharding,
* spread writes,
* rate limit hot keys,
* route heavy analytics away from OLTP.

## 7.3 CAP Theorem in Practice

CAP says that when a network partition happens, a distributed system must choose between consistency and availability.

Practical translation:

* If the network is healthy, many systems provide both enough consistency and enough availability.
* During partition, you must decide whether to reject requests or risk stale/conflicting data.

AI product examples:

* Permission checks should usually prefer consistency over availability.
* Usage analytics may prefer availability with eventual consistency.
* Feature freshness may tolerate slight staleness.
* Payment or account actions need stronger consistency.
* Caches may serve stale data only when the product can tolerate it.

The interview point:

> CAP is not a slogan. It is a prompt to define behavior under failure for each subsystem.

## 7.4 Star Schema vs Snowflake Schema

Analytics schemas often separate facts and dimensions.

Fact table:

* events,
* requests,
* tool calls,
* model invocations,
* purchases,
* labels.

Dimension tables:

* users,
* tenants,
* models,
* prompts,
* documents,
* products.

Star schema:

```text
dimension tables -> fact table <- dimension tables
```

Dimensions are denormalized and directly connected to the fact table.

Snowflake schema normalizes dimensions into more tables.

Tradeoff:

* star schema is simpler and often faster for analytics,
* snowflake schema reduces duplication but adds joins.

For ML analytics, simplicity often wins unless dimension consistency is a major problem.

---

# 8. Data Pipelines for ML Systems

Models are shaped by data.

If the data pipeline breaks, the model can fail even when the model code is unchanged.

## 8.1 Pipeline Layers

A practical ML data pipeline often has layers:

```text
raw events
  -> validation
  -> cleaned data
  -> features
  -> training datasets
  -> model artifacts
  -> serving features
  -> monitoring and feedback
```

Each layer should have:

* ownership,
* schema,
* freshness expectation,
* quality checks,
* lineage,
* retention policy.

## 8.2 Batch Pipelines

Batch pipelines process data on a schedule:

* hourly,
* daily,
* weekly,
* per training run.

Good for:

* large historical aggregations,
* training datasets,
* offline evals,
* backfills,
* reports.

Risks:

* stale data,
* long recovery time,
* expensive recomputation,
* hidden failures until the next run.

## 8.3 Streaming Pipelines

Streaming pipelines process events continuously.

Good for:

* near-real-time features,
* alerts,
* usage monitoring,
* drift detection,
* personalization,
* online feedback.

Hard parts:

* ordering,
* retries,
* duplicate events,
* late events,
* schema evolution,
* backpressure,
* exactly-once vs at-least-once semantics.

Most systems are effectively at-least-once and rely on idempotent sinks.

## 8.4 Schema Contracts

Schema changes break AI systems quietly.

Examples:

* `user_id` changes from integer to string,
* `timestamp` changes timezone,
* an enum gains a new value,
* a nullable field becomes missing,
* a model output field changes name,
* a document metadata field disappears.

Schema contracts should define:

* field names,
* types,
* nullability,
* allowed values,
* version,
* owner,
* compatibility rules.

Validate data at ingestion and before serving.

## 8.5 Backfills

Backfills recompute historical data.

They are needed when:

* feature logic changes,
* data was missing,
* a bug is fixed,
* a new model needs historical examples,
* a new metric is introduced.

Backfill risks:

* overwhelming databases,
* inconsistent historical definitions,
* duplicate writes,
* changing training data without versioning,
* mixing old and new feature logic.

Use versioned datasets and idempotent writes.

## 8.6 Training-Serving Skew

Training-serving skew happens when the features used in training differ from features used in production.

Causes:

* different code paths,
* different freshness,
* missing real-time data,
* inconsistent defaults,
* time leakage in training,
* schema drift,
* online transformations not matching offline transformations.

Mitigations:

* shared feature definitions,
* feature stores,
* point-in-time correct joins,
* online/offline parity tests,
* monitoring feature distributions.

## 8.7 Data Quality Checks

Data quality checks catch failures before they become model failures.

Common checks:

* row count,
* null rate,
* uniqueness,
* value ranges,
* enum values,
* freshness,
* distribution drift,
* referential integrity,
* duplicate events,
* label availability.

For AI systems, also check:

* prompt version,
* retrieved document source,
* embedding model version,
* model output schema,
* tool result schema,
* citation support.

---

# 9. Scalable Python Backends for AI Inference

A scalable Python AI backend separates user-facing orchestration from expensive inference work.

## 9.1 Basic Architecture

```text
client
  -> API gateway
  -> Python orchestration service
  -> cache / database / retrieval
  -> queue or batcher
  -> inference worker / model gateway
  -> validation
  -> streaming response
  -> traces and metrics
```

The API layer should own:

* auth,
* input validation,
* quotas,
* request IDs,
* routing decisions,
* deadlines,
* streaming connection,
* user-visible errors.

Workers should own:

* model calls,
* batching,
* retries to model providers where safe,
* GPU/runtime management,
* expensive preprocessing,
* output validation,
* worker-level metrics.

Do not make one service own everything forever.

## 9.2 Request Validation

Validate early:

* input size,
* content type,
* tenant/user identity,
* allowed model route,
* max tokens,
* tool permissions,
* schema shape.

Early validation protects downstream systems from bad or abusive requests.

## 9.3 Model Routing

Model routing decides which model or provider handles a request.

Signals:

* task type,
* user tier,
* latency target,
* cost budget,
* risk level,
* input length,
* language,
* required tools,
* retrieval quality.

Routing failure mode:

* easy tasks go to expensive models,
* hard tasks go to weak models,
* fallback model silently reduces quality,
* provider outage routes all traffic to an underprovisioned backup.

Routing must be observable.

## 9.4 Queues and Workers

Queues decouple request intake from work execution.

Benefits:

* absorb bursts,
* control concurrency,
* retry failed work,
* run background jobs,
* isolate slow tasks.

Costs:

* queue wait,
* delayed failures,
* duplicate work,
* harder cancellation,
* hidden overload.

Metrics:

* queue length,
* age of oldest job,
* dequeue rate,
* retry count,
* dead-letter count,
* worker utilization,
* task duration.

## 9.5 Batching

Batching improves throughput by grouping work.

In LLM systems, batching can improve GPU utilization, but it can also increase queueing delay.

Tradeoff:

```text
larger batch -> better throughput -> worse latency
smaller batch -> better latency -> worse utilization
```

Interactive systems often need dynamic batching with strict latency budgets.

## 9.6 Caching

Caches reduce repeated work.

Useful caches:

* response cache,
* prompt-prefix cache,
* embedding cache,
* retrieval result cache,
* document metadata cache,
* tool result cache.

Dangerous cache mistakes:

* missing tenant or permission in cache key,
* stale policy data,
* caching unsafe personalized responses,
* unbounded memory cache,
* no version in key,
* no invalidation strategy.

Cache keys should include correctness-relevant dimensions:

```text
tenant
user or permission scope
model version
prompt version
retrieval index version
input hash
```

## 9.7 Retries and Circuit Breakers

Retries help transient failures.

Retries hurt when:

* the failure is systematic,
* the operation is not idempotent,
* downstream is overloaded,
* clients retry at the same time,
* retry work continues after user cancellation.

Good retry policy:

* bounded attempts,
* exponential backoff,
* jitter,
* deadline-aware,
* idempotency-aware,
* observable.

Circuit breakers stop sending traffic to unhealthy dependencies.

Fallbacks should be explicit:

* smaller model,
* cached response,
* delayed job,
* partial answer,
* human review,
* clear error.

## 9.8 Observability

A request trace should answer:

* who made the request?
* what route did it take?
* which prompt version was used?
* which model version was used?
* what context was retrieved?
* what tools were called?
* how many tokens were used?
* how long did each stage take?
* did validation pass?
* did fallback happen?
* what was returned?

Metrics should include:

* request rate,
* error rate,
* latency percentiles,
* time to first token,
* time to final token,
* token counts,
* cost,
* cache hit rate,
* queue wait,
* model latency,
* DB latency,
* retrieval latency,
* fallback rate,
* validation failure rate.

Without observability, AI failures become anecdotes.

## 9.9 Common Failure Cascades

### Retry Storm

```text
provider slows down
  -> requests timeout
  -> clients retry
  -> traffic increases
  -> provider slows more
```

Mitigation:

* backoff,
* jitter,
* circuit breaker,
* admission control,
* queue limits.

### Blocked Event Loop

```text
async API service
  -> synchronous DB call
  -> event loop blocks
  -> all requests wait
```

Mitigation:

* async drivers,
* thread pool for blocking calls,
* profiling event loop lag,
* timeouts.

### Slow Metadata Query

```text
prompt construction
  -> permission metadata query
  -> missing index
  -> slow time to first token
```

Mitigation:

* query plan,
* index,
* cache,
* precomputed permissions,
* pagination.

### Memory Leak

```text
trace buffer stores full prompts
  -> memory grows
  -> GC pressure rises
  -> latency rises
  -> worker OOMs
```

Mitigation:

* truncation,
* streaming traces,
* bounded buffers,
* memory profiling,
* worker recycling.

---

# 10. Interview Answer Patterns

The best answers follow a structure:

```text
define the concept
  -> identify the bottleneck or failure mode
  -> explain the tradeoff
  -> give a production debugging or design step
```

## 10.1 "How Would You Optimize a Slow SQL Query?"

Strong answer:

> I would start with the query plan. I want to know whether the bottleneck is scan, join, sort, aggregation, or row estimation. Then I would check indexes, filter selectivity, join order, result size, and whether partition pruning is happening. If the query is repeatedly expensive and can tolerate staleness, I might use a materialized view. I would verify the fix on production-like data and watch write overhead from any new index.

What this answer shows:

* you do not guess,
* you understand plans,
* you understand index tradeoffs,
* you understand freshness and materialization,
* you validate with realistic data.

## 10.2 "Explain Python's GIL"

Strong answer:

> The GIL is a CPython lock that allows only one thread to execute Python bytecode at a time. It simplifies interpreter internals and reference counting. It mainly limits CPU-bound parallelism in Python threads. IO-bound threads can still overlap, and native extensions can release the GIL. For CPU-bound work I would use multiprocessing, vectorized libraries, compiled extensions, or separate workers. For IO-heavy orchestration, async or threads can still be effective.

What this answer shows:

* you know what the GIL is,
* you know what it does not mean,
* you can choose a concurrency model.

## 10.3 "How Would You Debug a Memory Leak?"

Strong answer:

> I would first confirm whether memory grows without bound and whether it is Python heap, native memory, or expected allocator behavior. Then I would reproduce under load, compare heap snapshots, inspect object growth by type, and check unbounded caches, pending tasks, callbacks, traces, and large retained payloads. If native memory is involved, I would inspect tensors or extension libraries. The fix might be bounding caches, releasing references, streaming large data, cancelling tasks, or isolating work in restartable workers.

What this answer shows:

* you know Python can leak through reachability,
* you distinguish RSS from live objects,
* you know native memory exists,
* you propose practical fixes.

## 10.4 "How Would You Build a Scalable Python Backend for AI Inference?"

Strong answer:

> I would separate the API layer from inference workers. The API layer handles auth, validation, quotas, routing, deadlines, and streaming. Workers handle model calls, batching, retries where safe, and runtime-specific metrics. I would add queues for background work, bounded concurrency for backpressure, caches with tenant-aware keys, timeouts, circuit breakers, and fallback routes. Observability needs request IDs, model and prompt versions, token counts, queue delay, DB time, model latency, and cost.

What this answer shows:

* you understand service boundaries,
* you understand backpressure,
* you understand AI-specific observability,
* you understand cost and reliability.

## 10.5 "How Would You Design a Data Pipeline for ML?"

Strong answer:

> I would define sources, schemas, freshness requirements, transformations, labels, validation checks, storage layers, and consumers. I would keep raw immutable data, validate schemas at ingestion, create versioned feature definitions, support backfills, and track lineage. I would monitor freshness, null rates, distribution drift, duplicates, and training-serving skew. The pipeline should fail loudly on data quality issues rather than silently training or serving corrupted features.

What this answer shows:

* you understand data lifecycle,
* you understand correctness,
* you understand ML-specific pipeline risks.

---

# 11. Tech Stack Mental Models for Applied AI Roles

The job descriptions that matter for frontier AI engineering do not ask for tools as trivia.

They ask for tools because the tools reveal the shape of the work:

* training large models,
* scaling reinforcement learning,
* debugging distributed GPU jobs,
* building retrieval and knowledge systems,
* serving LLMs with low latency,
* running evals and experiments reproducibly,
* sandboxing long-horizon agents,
* making research infrastructure reliable enough that scientists can move fast.

The goal of this section is to build mental models for the stack. You do not need to be an expert in every tool. You do need to understand what problem each tool solves, what abstraction it exposes, what it composes with, and what failure modes it creates.

The best mental model is layered:

```text
data and environments
  -> tensors and model code
  -> training / post-training loop
  -> distributed execution
  -> inference serving
  -> product orchestration
  -> evaluation
  -> observability
  -> deployment and operations
```

Different roles emphasize different layers. RL infrastructure roles emphasize rollout workers, reward pipelines, distributed training, cluster scheduling, and reproducibility. Knowledge-system roles emphasize ingestion, indexing, ranking, RAG, query understanding, and evals. Product AI roles emphasize API design, retrieval, tools, safety boundaries, serving, observability, and rollout.

## 11.1 Where Tech Stacks Fit in This Study Guide

The stack is not a separate topic from the earlier chapters. It is the implementation surface of those ideas.

| Chapter | Stack connection |
| ------- | ---------------- |
| Chapter 0 | Tensors, gradients, autograd, Transformer compute, PyTorch, TensorFlow, JAX |
| Chapter 1 | Model APIs, structured outputs, prompt/version tooling, app integration |
| Chapter 2 | FAISS, pgvector, vector databases, Elasticsearch, rerankers, knowledge graphs |
| Chapter 3 | LangGraph, Temporal, MCP, sandboxed tools, workflow engines |
| Chapter 4 | Eval harnesses, judge tooling, tracing, regression datasets |
| Chapter 5 | RLHF, DPO, PPO, reward modeling, W&B, MLflow, distributed training loops |
| Chapter 6 | vLLM, TGI, Triton Inference Server, Ray Serve, Redis, queues, Kubernetes |
| Chapter 7 | Cloud architecture, auth, policy engines, rollout systems, platform composition |
| Chapter 8 | GPUs, TPUs, CUDA, Triton kernels, JAX, high-performance optimization |
| Chapter 9 | The mental-model index tying the concrete technologies together |

## 11.2 How to Learn a Technology

For any tool, ask seven questions:

1. What abstraction does it expose?
2. What bottleneck or complexity does it remove?
3. What does it make harder?
4. What does it compose with?
5. What assumptions does it make?
6. What failure modes does it introduce?
7. What would I monitor or test in production?

Weak answer:

> I know Kubernetes.

Strong answer:

> Kubernetes schedules and manages containerized workloads. In AI systems, it is useful for API services, workers, inference deployments, and some training jobs. But GPU scheduling, gang scheduling, storage locality, startup time, and observability still need careful design. For batch research clusters, Slurm may be a better fit.

That is the level of answer you want.

---

## 11.3 The Framework Layer: PyTorch, TensorFlow, JAX

The framework layer is where mathematical programs become executable tensor programs.

Mental model:

```text
Python code
  -> tensor operations
  -> computation graph or execution trace
  -> gradients
  -> optimizer update
  -> GPU / TPU kernels
```

### PyTorch

PyTorch's core mental model is:

```text
eager tensor program + autograd tape
```

You write Python code that runs immediately. Tensor operations execute eagerly. If tensors require gradients, PyTorch records the operations needed to compute gradients later.

This makes PyTorch feel like normal Python:

* easy to debug,
* easy to inspect intermediate tensors,
* easy to write custom training loops,
* easy to prototype research ideas.

Important concepts:

* `Tensor`: multidimensional array with device and dtype.
* `nn.Module`: composable model component with parameters.
* `autograd`: automatic differentiation engine.
* `optimizer`: parameter update rule.
* `Dataset` / `DataLoader`: data iteration.
* `cuda`: GPU device placement.
* `torch.compile`: compilation path for optimizing eager programs.

Where it sits:

```text
data loader -> PyTorch model -> loss -> autograd -> optimizer -> checkpoint
```

What it composes with:

* Hugging Face Transformers for model definitions and pretrained weights,
* DeepSpeed and FSDP for distributed training,
* W&B or MLflow for experiment tracking,
* Triton kernels for custom GPU operations,
* vLLM or TGI for serving models trained or exported from the PyTorch ecosystem.

Why jobs ask for it:

Frontier AI work often means changing model code, debugging training loops, testing new objectives, or optimizing throughput. PyTorch gives researchers and engineers a flexible surface for that work.

Failure modes:

* silent CPU/GPU device mismatch,
* accidental graph retention causing memory growth,
* inefficient data loading starving GPUs,
* too many small operations causing overhead,
* distributed training hangs,
* checkpoint incompatibility,
* mixed-precision instability.

Interview framing:

> PyTorch is strong for research iteration because it is eager and Pythonic. The mental model is tensors plus autograd plus modules. At scale, the hard parts become data loading, memory, distributed training, kernel efficiency, checkpointing, and observability.

### TensorFlow

TensorFlow's original mental model is:

```text
define computation graph -> optimize graph -> execute graph
```

Modern TensorFlow also supports eager execution, but a key idea remains graph compilation through `tf.function`.

Graph execution can enable:

* optimization,
* portability,
* deployment,
* serving,
* mobile and edge targets,
* static analysis.

Important concepts:

* `Tensor`: array data structure,
* `tf.function`: traces Python into graph form,
* Keras: high-level model API,
* `tf.data`: data pipeline API,
* TensorBoard: visualization and experiment inspection,
* TensorFlow Serving: model serving system,
* TFLite: mobile/edge deployment path.

Where it sits:

```text
data pipeline -> Keras / TensorFlow model -> graph execution -> serving artifact
```

What it composes with:

* TFX-style production ML pipelines,
* TensorFlow Serving,
* TensorBoard,
* mobile/edge deployment stacks,
* data validation and transformation tooling.

Tradeoff:

TensorFlow can be strong when graph optimization and production deployment are central. PyTorch often feels easier for research iteration and debugging. Modern usage has converged somewhat, but the historical mental models still matter in interviews.

Interview framing:

> TensorFlow is graph-oriented at heart. That can make deployment and optimization cleaner, but dynamic research code can feel less direct than PyTorch. The tradeoff is graph optimizability and production paths versus eager debugging flexibility.

### JAX

JAX's mental model is:

```text
NumPy-like functions + program transformations
```

The important transformations are:

* `grad`: take gradients of functions,
* `jit`: compile functions,
* `vmap`: vectorize functions,
* `pmap` / `pjit`: distribute computation across devices.

JAX asks you to think more functionally:

```text
params, batch -> loss
```

Instead of mutating model state inside object-oriented modules, you often pass state explicitly through pure functions.

What it composes with:

* XLA compilation,
* Flax or Haiku model libraries,
* Optax optimizers,
* TPU pods and GPU clusters,
* custom research training loops.

Why jobs ask for it:

JAX is popular in high-performance research environments because transformations make it powerful for vectorization, compilation, and distributed computation.

Failure modes:

* dynamic Python control flow can fight compilation,
* recompilation can destroy performance,
* shape changes can be expensive,
* debugging compiled code can be harder,
* state management requires discipline.

Interview framing:

> JAX is not just another neural network library. It is a system for transforming numerical Python functions. The power comes from `jit`, `grad`, `vmap`, and distributed transformations. The tradeoff is that you need to write code in a more functional and shape-stable way.

### PyTorch vs TensorFlow vs JAX

| Framework | Mental model | Best fit | Main tradeoff |
| --------- | ------------ | -------- | ------------- |
| PyTorch | Eager tensor programs plus autograd | Research iteration, LLM work, flexible training loops | Scaling and optimization require extra systems work |
| TensorFlow | Graph-oriented computation and deployment | Production ML, graph optimization, serving, mobile/edge | Less natural for dynamic research code |
| JAX | Functional numerical programs plus transformations | High-performance research, TPU/GPU scaling, compilation | Requires functional style and shape discipline |

The interview answer should not be "one is better." It should be:

> They optimize for different workflows. PyTorch optimizes for flexible research iteration, TensorFlow for graph/deployment-oriented production paths, and JAX for composable program transformations and high-performance compiled numerical code.

---

## 11.4 Model and Training Library Layer

Above the tensor framework are libraries that package model architectures, tokenizers, training utilities, and distributed training patterns.

Mental model:

```text
raw data
  -> tokenizer
  -> tensors
  -> model
  -> loss
  -> gradients
  -> optimizer
  -> checkpoint
```

### Hugging Face Transformers

Transformers is a standardized interface to model architectures, pretrained checkpoints, tokenizers, and generation utilities.

Mental model:

```text
model name -> config + tokenizer + weights + model class
```

What it is good for:

* loading pretrained models,
* fine-tuning,
* inference prototypes,
* standardizing model APIs,
* comparing architectures,
* accessing community checkpoints.

What it composes with:

* PyTorch, TensorFlow, JAX/Flax backends,
* Datasets,
* Tokenizers,
* Accelerate,
* PEFT/LoRA tooling,
* TRL for post-training,
* model hubs and registries.

Failure modes:

* tokenizer/model mismatch,
* hidden defaults in generation configs,
* memory surprises from model size,
* checkpoint compatibility issues,
* prototype code accidentally becoming production code.

### Datasets and Tokenizers

Datasets manage data loading, streaming, sharding, and preprocessing.

Tokenizers are the boundary between raw text and model tensors.

Mental model:

```text
text -> token ids -> tensors -> model
```

Why tokenizers matter:

* they define vocabulary,
* they affect sequence length,
* they affect cost,
* they affect multilingual behavior,
* they must match the model checkpoint.

In large-scale training, tokenization can become a real throughput bottleneck.

### Accelerate

Accelerate provides a simpler abstraction over multi-device training.

Mental model:

```text
same training loop -> configured device/distributed setup
```

It is useful when you want code to run on CPU, one GPU, multiple GPUs, or distributed environments with fewer changes.

### DeepSpeed

DeepSpeed is a training optimization system for large models.

The key mental model is memory partitioning.

ZeRO reduces memory pressure by sharding:

* optimizer states,
* gradients,
* parameters.

Instead of every GPU storing everything, GPUs store different pieces and communicate when needed.

Tradeoff:

* bigger models and batches fit,
* communication and configuration complexity increase.

### PyTorch FSDP

Fully Sharded Data Parallel is PyTorch's native approach to sharding model states across devices.

Mental model:

```text
each GPU stores shards
  -> gather parameters for computation
  -> compute
  -> reduce/scatter gradients
```

DeepSpeed ZeRO and FSDP solve similar memory-scaling problems, with different APIs and ecosystem integration.

### Fairseq and Megatron-LM Style Stacks

Fairseq and Megatron-style stacks represent research-oriented large-scale sequence modeling systems.

Mental model:

```text
model research code + distributed training patterns + optimized kernels + large-scale configs
```

They matter because many frontier training systems are not just simple library calls. They are large codebases that encode model architecture, data loading, distributed parallelism, checkpointing, and evaluation.

### PEFT and LoRA

Chapter 5 covers the theory of parameter-efficient fine-tuning: why freezing the base model and training a small adaptation can be a useful post-training strategy.

Here, the focus is the engineering side: how PEFT/LoRA shows up in the stack, how it composes with training libraries and serving systems, and what has to be tracked so adapters do not become ambiguous artifacts.

Parameter-efficient fine-tuning changes a small number of trainable parameters instead of updating the full model.

LoRA's mental model is:

```text
frozen base weights + small trainable low-rank adapters
```

Why it matters:

* much lower GPU memory,
* cheaper fine-tuning,
* easier adapter swapping,
* useful domain adaptation,
* faster experimentation.

What it composes with:

* Transformers,
* PEFT libraries,
* quantization,
* Accelerate,
* DeepSpeed/FSDP for larger runs,
* model registries that track base model plus adapter version.

Failure modes:

* adapter/base mismatch,
* overfitting narrow data,
* degraded general capability,
* confusing deployment if the adapter is not loaded with the intended base model,
* evaluation that misses slices where the adapter hurts.

Interview framing:

> The theory of LoRA belongs in post-training: freeze the base model and train a low-rank adaptation. The engineering concern is artifact integrity. I would track the base model, tokenizer, adapter version, training data, and eval results together because the adapter alone is not a complete deployable model.

### Dataset and Checkpoint Formats

Large-scale AI work is also about file formats.

Common dataset/storage formats:

* **Parquet:** columnar analytics format, good for warehouse-style datasets and feature tables.
* **Arrow:** in-memory columnar format, useful for efficient data interchange and Hugging Face Datasets internals.
* **JSONL:** simple line-delimited records, easy for prompts and small/medium corpora but inefficient at huge scale.
* **WebDataset / tar shards:** shard-based format often used for large image or multimodal datasets.
* **TFRecord:** TensorFlow-oriented record format, common in TF pipelines.

Common checkpoint formats:

* PyTorch checkpoints,
* `safetensors`,
* TensorFlow SavedModel,
* sharded checkpoints for large models,
* optimizer-state checkpoints for training resumption.

Mental model:

```text
data format determines how fast and safely bytes become batches
checkpoint format determines how reliably training or serving can resume
```

Why jobs care:

Many large-scale failures are not algorithmic. They are data throughput, checkpoint corruption, slow startup, bad sharding, or unreproducible artifact problems.

Interview framing:

> I would treat datasets and checkpoints as production artifacts. They need versioning, integrity checks, metadata, lineage, and compatibility with the training or serving stack.

---

## 11.5 RL and Post-Training Stack

Post-training turns a pretrained model into a model that follows instructions, uses tools, refuses unsafe requests, or performs well on specific tasks.

Mental model:

```text
policy
  -> rollout / completion
  -> reward or preference signal
  -> optimization update
  -> eval
  -> new policy
```

### Gym and Gymnasium

Gym's mental model is the environment interface:

```text
observation = env.reset()
observation, reward, done, info = env.step(action)
```

This interface matters because RL is about interaction, not just static labels.

For LLM agents, an environment might be:

* a code repository,
* a browser,
* a tool sandbox,
* a game,
* a math problem environment,
* a simulated user,
* a computer-use task.

### TRL and RLHF Libraries

TRL-style libraries package common post-training workflows:

* supervised fine-tuning,
* reward modeling,
* PPO,
* DPO,
* preference optimization.

Mental model:

```text
prompts -> candidate responses -> preference/reward -> policy update
```

They compose with:

* Transformers,
* Datasets,
* Accelerate,
* DeepSpeed/FSDP,
* W&B/MLflow,
* eval harnesses.

### Ray and RLlib

Ray provides distributed Python tasks and actors.

RLlib builds RL abstractions on top of distributed workers.

Mental model:

```text
driver
  -> rollout workers
  -> reward/eval workers
  -> learner workers
  -> checkpoint/eval
```

Ray is useful when workloads are Python-native, distributed, and irregular.

### Custom Rollout Workers

Frontier labs often build custom rollout infrastructure because LLM RL workloads are specialized:

* model-generated trajectories can be long,
* tool calls may be slow,
* rewards may require separate models,
* environments may require sandboxes,
* data needs careful logging and replay,
* throughput and reproducibility matter.

Job-role connection:

The roles mention PPO, DPO, RLHF, reward modeling, rollout pipelines, reward pipelines, distributed workloads, throughput, reliability, and reproducibility. This is exactly this layer.

---

## 11.6 Distributed Training and Cluster Orchestration

Large training jobs are distributed systems.

Mental model:

```text
training job
  -> scheduler
  -> nodes
  -> GPUs
  -> communication
  -> checkpoints
  -> metrics
```

### Kubernetes

Kubernetes orchestrates containers.

It handles:

* scheduling,
* service discovery,
* health checks,
* restarts,
* deployments,
* autoscaling,
* resource requests and limits.

AI use cases:

* API services,
* inference workers,
* embedding services,
* retrieval services,
* batch jobs,
* some training jobs.

Tradeoffs:

Kubernetes is excellent for service/platform workloads. GPU training at cluster scale may require extra tooling for gang scheduling, topology awareness, storage, and job lifecycle management.

### Slurm

Slurm is an HPC-style batch scheduler.

Mental model:

```text
submit job -> wait in queue -> allocated nodes -> run script -> release resources
```

It is common in research clusters because training jobs often look like long-running batch jobs that need a specific number of nodes and GPUs.

Kubernetes vs Slurm:

| System | Mental model | Best fit |
| ------ | ------------ | -------- |
| Kubernetes | container orchestration for services and jobs | production services, inference, platform workloads |
| Slurm | batch scheduling for cluster jobs | research training, HPC-style GPU jobs |

### Ray

Ray is a distributed execution framework for Python.

Mental model:

```text
Python function -> remote task
Python class -> remote actor
```

Ray is useful for:

* distributed data processing,
* RL rollouts,
* parallel evaluation,
* model serving,
* task orchestration.

### Docker and Containers

Containers package code, dependencies, and runtime environment.

Mental model:

```text
code + dependencies + OS-level runtime -> image -> container
```

Containers improve reproducibility, but they do not solve everything:

* GPU drivers still matter,
* data paths still matter,
* network and permissions still matter,
* image size and startup time matter.

### NCCL

NCCL is a communication library for GPUs.

It underlies common distributed training operations:

* all-reduce,
* broadcast,
* reduce-scatter,
* all-gather.

Mental model:

```text
GPU workers compute local gradients
  -> NCCL communicates across GPUs
  -> workers synchronize updates
```

Why it matters:

Distributed training performance often depends on communication. If NCCL is slow or hanging, GPUs sit idle even if model code is correct.

### Parallelism Types

Large-model training usually combines several kinds of parallelism.

| Type | Mental model | What it solves | Cost |
| ---- | ------------ | -------------- | ---- |
| Data parallelism | Replicate model, split data | More batch throughput | Gradient synchronization |
| Tensor parallelism | Split matrix operations across GPUs | Layers too large for one GPU | Frequent communication |
| Pipeline parallelism | Split layers across stages | Model depth too large for one GPU | Pipeline bubbles and scheduling |
| Sequence parallelism | Split sequence dimension or related activations | Long sequence activation memory | More complex implementation |
| Expert parallelism | Place MoE experts across devices | Many experts / large sparse models | Routing and load balance |

Mental model:

```text
data parallelism splits examples
tensor parallelism splits math inside layers
pipeline parallelism splits layers
sequence parallelism splits long-token activations
expert parallelism splits sparse expert capacity
```

Why this matters:

When a training run is slow, you need to know whether the bottleneck is compute, memory, communication, pipeline bubbles, data loading, or checkpointing. Parallelism choices change all of those.

Interview framing:

> Distributed training is not one trick. I would choose the parallelism strategy based on what does not fit: batch size, parameters, activations, sequence length, or expert capacity. Then I would monitor GPU utilization, communication time, memory, data loading, and checkpoint overhead.

### Scale-Up, Scale-Out, and MoE Rack Layout

Large sparse models are shaped by physical hardware topology.

Two network domains matter:

| Domain | Mental model | Typical property |
| ------ | ------------ | ---------------- |
| Scale-up | fast local accelerator fabric inside a rack or pod | high bandwidth, low latency, dense connectivity |
| Scale-out | network between racks or pods | slower, more hops, more topology constraints |

MoE layers are especially sensitive to this because expert routing creates all-to-all communication.

Mental model:

```text
tokens on every GPU
  -> router chooses experts
  -> tokens are sent to expert GPUs
  -> expert outputs are sent back and combined
```

If experts live inside one fast scale-up domain, any GPU can send tokens to any expert with high bandwidth. If the expert layer crosses rack boundaries, many routed tokens must use slower scale-out links.

This is why one rack or one scale-up domain becomes a natural boundary for an MoE layer. The model architecture wants:

```text
all-to-all expert traffic
  -> fast dense interconnect
  -> keep experts inside the scale-up domain when possible
```

Interview framing:

> MoE is not just an algorithmic sparsity trick. It creates an all-to-all communication pattern, so the physical interconnect can determine how large an expert-parallel group should be.

### Why Expert Parallelism Fits MoE

Expert parallelism places different experts on different devices.

This matches the structure of an MoE layer:

```text
many experts
  -> split experts across GPUs
  -> route tokens to the selected experts
```

The good part:

* active compute per token can stay low,
* total parameter capacity can grow,
* each GPU only owns a subset of experts.

The hard part:

* token routing can be imbalanced,
* all-to-all communication can dominate,
* expert placement must respect topology,
* larger sparsity may need larger batches to amortize weight movement,
* total parameter memory still has to fit somewhere.

This is the systems reason sparse models often depend on careful co-design between model architecture, router behavior, batch size, and hardware topology.

### Pipeline Parallelism Limits

Pipeline parallelism splits layers across stages:

```text
layers 1-20 -> stage 1
layers 21-40 -> stage 2
layers 41-60 -> stage 3
```

It helps when model weights do not fit in one device or one scale-up domain.

But it introduces pipeline bubbles:

```text
start of batch:
  later stages wait

end of batch:
  earlier stages wait
```

Micro-batches reduce idle time by keeping multiple chunks in flight. This is easier during inference because there is only a forward pass. During training, the backward pass, gradient accumulation, and optimizer step make scheduling much more complicated.

The deeper limitation for LLM inference is KV cache.

Pipeline parallelism divides model weights across stages, but it does not necessarily reduce KV-cache pressure in the way people first expect. To keep $P$ pipeline stages busy, the system often needs roughly $P$ micro-batches in flight. Splitting layers across $P$ stages reduces per-stage KV layers, but increasing in-flight micro-batches pushes active sequence count up. Those effects can cancel.

Mental model:

```text
pipeline parallelism:
  helps weight capacity
  adds scheduling complexity
  creates bubbles
  can add cross-stage latency
  does not magically solve long-context KV pressure
```

This is why pipeline parallelism is often a tradeoff rather than a pure win.

### Pipeline Parallelism and Research Iteration

Pipeline boundaries can also constrain architecture.

If a model has simple sequential layers, splitting layers across stages is natural. But newer architectures may include:

* attention patterns that refer to residuals from many previous layers,
* alternating global and local attention layers,
* nonuniform MoE or routing behavior,
* layer types with very different compute or memory cost.

Those features can create load imbalance or force awkward cross-stage communication.

The engineering risk:

```text
parallelism scheme hard-codes architecture assumptions
  -> model researchers avoid changes that break the system
  -> iteration slows down
```

Strong infrastructure should support the model architecture rather than accidentally dictating it.

### Checkpointing and Fault Tolerance

Large training jobs fail.

They fail because:

* nodes die,
* GPUs error,
* network links degrade,
* jobs are preempted,
* storage stalls,
* code has bugs,
* data shards are corrupt.

Checkpointing is what makes failure recoverable.

A good checkpoint includes:

* model parameters,
* optimizer state,
* scheduler state,
* random number generator state,
* data-loader position or shard state,
* training step,
* config,
* code/data version references.

For very large models, checkpoints are often sharded. That means restore logic must know how shards map back to distributed ranks.

Interview framing:

> I would design checkpointing as part of the training system, not an afterthought. A checkpoint should allow reliable resume with the same optimizer, scheduler, data position, and config. I would test restore regularly because untested checkpoints are just expensive files.

---

## 11.7 Inference and Serving Stack

Serving systems turn trained models into product behavior.

Mental model:

```text
request
  -> gateway
  -> router
  -> queue / batcher
  -> model runtime
  -> stream tokens
  -> trace
```

### vLLM

vLLM is a high-throughput LLM serving system.

Mental model:

```text
continuous batching + efficient KV cache management
```

It is known for PagedAttention, which manages KV cache memory more efficiently.

Good for:

* high-throughput LLM serving,
* many concurrent requests,
* open-weight model deployment.

Interview focus:

* continuous batching,
* KV-cache pressure,
* prefill vs decode,
* throughput vs latency.

### TGI

Text Generation Inference is Hugging Face's LLM serving stack.

Mental model:

```text
standardized server for text generation models
```

Good for:

* serving Hugging Face-compatible models,
* production-ish deployment,
* streaming generation,
* batching and model management.

### Triton Inference Server

Triton Inference Server serves models across multiple frameworks.

Mental model:

```text
model repository + inference server + batching + multiple backends
```

Good for:

* heterogeneous model serving,
* non-LLM inference,
* ensembles,
* GPU inference services.

Do not confuse Triton Inference Server with the Triton language for writing GPU kernels.

### Ray Serve

Ray Serve is Python-native model serving on top of Ray.

Mental model:

```text
Python deployments + distributed routing + autoscaling
```

Good for:

* Python-heavy inference pipelines,
* multi-stage inference graphs,
* custom routing,
* integration with Ray workloads.

### FastAPI and Starlette

FastAPI and Starlette sit at the API layer.

Mental model:

```text
HTTP request -> validation -> async handler -> response
```

They compose with:

* Pydantic schemas,
* async model clients,
* Redis,
* queues,
* tracing middleware,
* auth systems.

They should not become the whole inference platform. Keep API concerns separate from GPU/runtime concerns.

### Redis and Queues

Redis is often used for:

* caching,
* rate limiting,
* coordination,
* lightweight queues,
* session state.

Celery, Dramatiq, and RQ provide background task queues.

Mental model:

```text
API accepts work -> queue stores work -> workers process work
```

Failure modes:

* unbounded queue growth,
* duplicate jobs,
* stuck jobs,
* missing idempotency,
* overloaded workers,
* stale cache values.

---

## 11.8 Data Engineering and ETL Stack

Data systems feed training, retrieval, evals, monitoring, and learning loops.

Mental model:

```text
raw events
  -> durable storage
  -> transformation
  -> features / evals / training data
  -> monitoring
```

### Spark

Spark is distributed batch processing.

Mental model:

```text
large dataset -> partitioned transformations -> distributed execution
```

Good for:

* large historical datasets,
* joins,
* aggregations,
* feature generation,
* ETL.

Failure modes:

* shuffles dominate runtime,
* skewed partitions,
* memory pressure,
* expensive joins,
* poor file layout.

### Beam

Beam provides a unified batch and streaming programming model.

Mental model:

```text
pipeline definition -> runner executes it
```

The same logical pipeline can run on different runners.

Good for:

* systems that need both batch and streaming semantics,
* windowing,
* event-time processing,
* portability across execution engines.

### Dask

Dask is Python-native distributed computation.

Mental model:

```text
familiar Python dataframe/array tasks -> distributed scheduler
```

Good for:

* Python teams,
* parallel dataframes,
* custom workflows,
* workloads that do not fit neatly into Spark.

### Kafka

Kafka is a durable event log.

Mental model:

```text
producers -> append events to topics -> consumers read offsets
```

Good for:

* streaming events,
* decoupling services,
* replay,
* near-real-time features,
* monitoring pipelines.

Failure modes:

* consumer lag,
* bad partition keys,
* duplicate processing,
* schema evolution,
* poison messages.

### Airflow, Dagster, Prefect

These orchestrate workflows.

Mental model:

```text
task graph -> scheduler -> retries -> lineage/metadata
```

Airflow is widely used for scheduled DAGs. Dagster emphasizes software-defined assets and lineage. Prefect emphasizes Pythonic workflows and operational ergonomics.

### dbt

dbt is a SQL transformation and analytics engineering tool.

Mental model:

```text
raw warehouse tables -> versioned SQL models -> tested analytical datasets
```

It is useful when the transformation layer is mostly SQL and teams need tests, lineage, documentation, and repeatability.

### Object Stores and Warehouses

S3 and GCS are common storage backbones.

Mental model:

```text
cheap durable object storage for datasets, checkpoints, logs, artifacts
```

Warehouses like BigQuery, Snowflake, and Redshift support analytical querying.

They are not usually low-latency request-path databases. They are for analytics, training data, eval analysis, and reporting.

### Feature Stores

A feature store manages reusable ML features across training and serving.

Mental model:

```text
feature definition
  -> offline historical values
  -> online low-latency values
  -> consistent training and serving access
```

Examples include Feast-style systems and custom internal feature platforms.

Why they matter:

* reduce training-serving skew,
* centralize feature definitions,
* support point-in-time correct training data,
* provide online low-latency feature lookup,
* improve reuse across models.

Tradeoffs:

* operational complexity,
* feature ownership,
* freshness guarantees,
* backfill complexity,
* online/offline consistency.

Interview framing:

> I would use a feature store when multiple models need shared, versioned, point-in-time-correct features with online serving. For simpler systems, a warehouse plus careful pipeline contracts may be enough.

---

## 11.9 Retrieval, Search, and Knowledge Systems Stack

Knowledge systems are central to applied AI.

Mental model:

```text
documents
  -> parsing
  -> chunking
  -> embeddings / sparse index
  -> retrieval
  -> reranking
  -> context assembly
  -> model
```

### FAISS

FAISS is a library for vector search.

Mental model:

```text
local vector index inside your own service or batch job
```

Good for:

* experiments,
* local indexes,
* custom retrieval systems,
* high-performance vector search when you own the service layer.

Tradeoff:

You manage persistence, metadata, filtering, scaling, and service APIs yourself.

### pgvector

pgvector adds vector search to Postgres.

Mental model:

```text
relational metadata + vector similarity in one database
```

Good for:

* small to medium corpora,
* apps already using Postgres,
* strong metadata filtering,
* simpler operations.

Tradeoff:

It may not match dedicated vector systems at very large scale or specialized latency targets.

### Managed Vector Databases

Examples include Pinecone, Weaviate, and Milvus-style systems.

Mental model:

```text
dedicated vector retrieval service
```

Good for:

* larger corpora,
* operational offload,
* vector-specific indexing and scaling,
* APIs around metadata and namespaces.

Tradeoff:

You add a specialized dependency, cost, and possible vendor/platform constraints.

### Elasticsearch and OpenSearch

These are sparse search systems.

Mental model:

```text
inverted index over terms + filtering + ranking
```

Good for:

* BM25,
* exact term matching,
* logs,
* document search,
* filters and facets.

They compose well with dense retrieval in hybrid search.

### Rerankers

Rerankers improve precision after first-stage retrieval.

Mental model:

```text
retrieve many candidates cheaply -> score fewer candidates carefully
```

Cross-encoder rerankers look at query and document together, which is often better but slower.

### Knowledge Graphs

Knowledge graphs organize entities and relationships.

Mental model:

```text
entities + relations + attributes -> graph queries and reasoning
```

Good for:

* structured relationships,
* provenance,
* entity-centric retrieval,
* multi-hop queries.

Tradeoff:

They require schema design, entity resolution, maintenance, and often still need text retrieval alongside them.

---

## 11.10 Evaluation and Experimentation Stack

Evals are the bridge between change and confidence.

Mental model:

```text
candidate change
  -> fixed eval set
  -> metrics and slices
  -> trace inspection
  -> ship / canary / rollback
```

### pytest

pytest is deterministic software testing.

Use it for:

* schema validators,
* prompt rendering,
* tool argument validation,
* retrieval filters,
* deterministic business rules,
* regression tests around known failures.

### Eval Harnesses

OpenAI Evals-style or custom harnesses run model/system behavior against datasets.

They should track:

* input,
* expected behavior,
* model output,
* scoring rubric,
* model version,
* prompt version,
* retrieval context,
* tool traces.

### LangSmith, Braintrust, Ragas-Style Tools

These tools help with traces, datasets, model comparison, and RAG evaluation.

Mental model:

```text
production/eval traces -> labeled datasets -> comparison runs -> failure analysis
```

Do not treat any eval platform as magic. The quality comes from good datasets, clear rubrics, and careful slice analysis.

### W&B and MLflow

W&B and MLflow track experiments, metrics, artifacts, and models.

Mental model:

```text
run config + code version + data version + metrics + artifacts
```

Track:

* hyperparameters,
* model config,
* dataset version,
* checkpoint path,
* metrics,
* eval results,
* logs,
* system utilization,
* random seed,
* code commit.

### Hydra and Config Systems

Config systems make experiments reproducible.

Mental model:

```text
experiment = code + data + config + seed + environment
```

Without configuration discipline, research results become hard to reproduce.

### Model Registries and Artifact Stores

Model registries track deployable model artifacts and their metadata.

Mental model:

```text
model artifact + metadata + lineage + approval state -> deployable version
```

A good registry tracks:

* model weights,
* tokenizer,
* base model and adapter,
* training data version,
* eval results,
* safety review status,
* owner,
* deployment status,
* rollback target.

Artifact stores hold the underlying files:

* checkpoints,
* datasets,
* eval outputs,
* logs,
* generated samples,
* model cards.

Why this matters:

A model is not just a `.pt` file. It is a bundle of weights, tokenizer, config, data lineage, eval evidence, and deployment policy.

Interview framing:

> I would not ship an anonymous checkpoint. I would promote a model through a registry with versioned artifacts, eval results, owner metadata, and rollback information.

### CI for Research and ML Infrastructure

Research code still needs tests.

Useful checks:

* unit tests for data transforms,
* small overfit tests for training loops,
* shape tests for model changes,
* deterministic smoke tests,
* checkpoint save/restore tests,
* eval harness regression tests,
* lint/type checks for production code,
* launch tests for distributed job configs.

The job-role signal is clear: teams want infrastructure that lets researchers move quickly without breaking the pipeline.

Interview framing:

> I would build CI that catches cheap failures before expensive GPU runs: import errors, config mistakes, data schema breaks, shape mismatches, checkpoint restore failures, and small training-loop regressions.

---

## 11.11 Observability and Reliability Stack

Observability answers:

> What happened, where, and why?

Mental model:

```text
request id
  -> spans
  -> metrics
  -> logs
  -> dashboard
  -> alert
  -> incident response
```

### OpenTelemetry

OpenTelemetry standardizes instrumentation for traces, metrics, and logs.

Mental model:

```text
instrument code once -> export telemetry to different backends
```

In AI systems, spans should cover:

* prompt construction,
* retrieval,
* reranking,
* model call,
* tool call,
* validation,
* streaming,
* database queries.

### Prometheus

Prometheus collects and queries time-series metrics.

Good for:

* counters,
* gauges,
* histograms,
* latency percentiles,
* service health,
* queue depth,
* GPU utilization if exported.

### Grafana

Grafana visualizes metrics and logs from multiple sources.

Mental model:

```text
metrics source -> dashboard -> operational picture
```

Good dashboards answer a debugging question. They are not just charts.

### Datadog-Style Platforms

Hosted observability platforms combine metrics, traces, logs, dashboards, and alerts.

Mental model:

```text
one operational surface for service behavior
```

Useful when teams need integrated incident debugging and do not want to run every observability component themselves.

### Sentry

Sentry focuses on application errors and exceptions.

Good for:

* stack traces,
* error grouping,
* release tracking,
* user/session context.

For AI systems, make sure sensitive prompts and retrieved content are redacted.

---

## 11.12 Cloud, Containers, and Sandboxing Stack

AI systems run inside infrastructure.

Mental model:

```text
code + dependencies
  -> image
  -> isolated runtime
  -> scheduled workload
  -> monitored execution
```

### Docker

Docker packages code and dependencies into images.

Good for:

* reproducible services,
* consistent worker environments,
* deployment pipelines,
* local/prod parity.

Failure modes:

* huge images,
* dependency drift,
* missing GPU runtime configuration,
* secrets baked into images,
* slow cold starts.

### Kubernetes

Kubernetes schedules and manages containers.

It composes with:

* Docker/container images,
* service meshes,
* ingress controllers,
* autoscalers,
* GPU node pools,
* observability agents,
* config/secrets systems.

For AI, Kubernetes is common for services and inference fleets, but research training may still use Slurm or specialized schedulers.

### AWS and GCP

Cloud platforms provide:

* compute,
* GPUs/TPUs,
* object storage,
* managed databases,
* networking,
* IAM,
* logging,
* managed Kubernetes,
* warehouses.

Mental model:

```text
managed building blocks + operational contracts + cost model
```

Interview focus:

Do not list services. Explain how compute, storage, networking, identity, and observability compose.

### VMs and Sandboxing

Agents that run code or use computers need isolation.

Mental model:

```text
untrusted action -> isolated environment -> controlled outputs
```

Sandboxing protects:

* host filesystem,
* network,
* credentials,
* other tenants,
* production systems.

Technologies and concepts:

* VMs,
* containers,
* gVisor-style syscall isolation,
* Firecracker-style microVMs,
* seccomp,
* network policies,
* resource limits.

The point is not the brand name. The point is the boundary.

---

## 11.13 Performance and Systems Languages

Python is the orchestration language for much of AI, but performance often comes from lower layers.

Mental model:

```text
Python orchestration
  -> native runtimes
  -> kernels
  -> hardware execution
```

### CUDA

CUDA is NVIDIA's programming model for GPUs.

Mental model:

```text
many lightweight threads execute the same kernel over data in parallel
```

The execution hierarchy is:

```text
grid
  -> blocks
  -> warps
  -> threads
```

* A **thread** executes one lane of work.
* A **warp** is a group of threads that execute in lockstep on NVIDIA GPUs.
* A **block** is a group of threads that can cooperate through shared memory.
* A **grid** is the full set of blocks launched for a kernel.

This is why GPU code works best when the same operation is applied across many data elements with regular memory access. Branch-heavy or irregular workloads can underuse the hardware because different threads in the same warp want to do different things.

You do not need to write CUDA for every role, but you should understand why GPU performance depends on:

* memory bandwidth,
* kernel fusion,
* occupancy,
* communication,
* data movement,
* tensor shapes.

Key performance intuition:

```text
slow path:
  CPU loop calls many tiny GPU operations

better path:
  one larger fused kernel does more work per launch
```

Kernel launches have overhead. CPU-GPU transfers have overhead. Moving data repeatedly between host memory and device memory can dominate runtime even when each individual operation is fast.

For AI workloads, many optimizations come from:

* keeping tensors on the GPU,
* fusing operations to reduce intermediate reads/writes,
* choosing tensor shapes that hit efficient kernels,
* increasing arithmetic intensity,
* reducing synchronization points,
* overlapping compute and communication when possible.

Interview framing:

> I do not need to hand-write CUDA to reason about GPU performance. I would look for CPU-GPU transfers, many small kernel launches, poor tensor shapes, memory-bandwidth limits, and synchronization. The high-level fix is usually to batch, fuse, keep data resident, and use optimized kernels.

### Triton Language

Triton is a Python-like language for writing GPU kernels.

Mental model:

```text
write custom tensor kernel -> compile to efficient GPU code
```

It is often used when framework operations are not efficient enough or when a new attention/MLP/kernel pattern needs optimization.

Do not confuse Triton language with Triton Inference Server.

### C++

C++ is used for:

* runtimes,
* inference engines,
* high-performance services,
* native extensions,
* kernels,
* systems where latency and memory control matter.

Mental model:

```text
manual control and performance at the cost of complexity
```

### Rust

Rust is used when teams want systems-level performance with stronger memory safety.

Good fits:

* control-plane services,
* sandboxes,
* CLIs,
* high-reliability infrastructure,
* agents/tools that need safety boundaries.

### OS Internals

OS fundamentals matter for:

* processes,
* threads,
* memory,
* files,
* sockets,
* scheduling,
* signals,
* containers,
* cgroups.

Many AI infra bugs are OS bugs wearing ML clothing: file descriptor leaks, process zombies, memory pressure, slow disks, network timeouts, or bad scheduling.

---

## 11.14 Agent and Tooling Stack

Agent systems compose models with state, tools, and control flow.

Mental model:

```text
state
  -> policy / model
  -> tool or action
  -> observation
  -> state update
  -> stop condition
```

### LangGraph

LangGraph models agent workflows as graphs of state transitions.

Good for:

* explicit state,
* multi-step workflows,
* branching,
* controlled loops,
* tool use.

Mental model:

```text
stateful graph, not free-form chat
```

### Temporal

Temporal is durable workflow orchestration.

Good for:

* long-running workflows,
* retries,
* durable state,
* human approvals,
* compensation logic,
* exactly-once-ish business processes.

Mental model:

```text
workflow state persists outside the worker process
```

Temporal solves reliability problems that prompts cannot solve.

### MCP

MCP standardizes how models and agents access tools and context.

Mental model:

```text
agent client -> standardized server -> tools/resources/prompts
```

It matters because tool integration becomes more reusable when context and actions have a standard interface.

### Sandboxed Code Execution

Code agents need to run untrusted or model-generated code safely.

Components:

* isolated filesystem,
* restricted network,
* timeouts,
* CPU/memory limits,
* process cleanup,
* audit logs,
* artifact capture.

This composes with containers, VMs, workflow engines, and evaluation environments.

---

## 11.15 Stack Patterns by Role Type

Different roles emphasize different combinations.

### RL Infrastructure / Post-Training Engineer

Core stack:

```text
PyTorch or JAX
  -> Transformers / custom model code
  -> rollout workers
  -> reward model
  -> PPO / DPO / RLHF trainer
  -> distributed scheduler
  -> checkpoint store
  -> eval harness
  -> W&B / MLflow
  -> Prometheus / Grafana / OpenTelemetry
```

What to know:

* distributed training,
* rollout throughput,
* reward pipeline reliability,
* checkpointing,
* reproducibility,
* GPU utilization,
* debugging slowdowns after many steps.

### Knowledge / Retrieval Engineer

Core stack:

```text
document ingestion
  -> parsing / chunking
  -> embedding model
  -> FAISS / pgvector / vector DB
  -> Elasticsearch / OpenSearch
  -> reranker
  -> context builder
  -> model API
  -> RAG evals
```

What to know:

* dense vs sparse retrieval,
* metadata filtering,
* access control,
* ranking,
* query understanding,
* index freshness,
* citation support,
* knowledge graph tradeoffs.

### Inference / Serving Engineer

Core stack:

```text
FastAPI / gateway
  -> auth / quota
  -> router
  -> Redis cache
  -> queue / batcher
  -> vLLM / TGI / Triton / Ray Serve
  -> GPU workers
  -> OpenTelemetry / Prometheus / Grafana
```

What to know:

* prefill vs decode,
* batching,
* KV cache,
* GPU memory,
* streaming,
* admission control,
* cost per token,
* fallback behavior.

### Research Infrastructure Engineer

Core stack:

```text
PyTorch / JAX
  -> distributed training framework
  -> Slurm / Kubernetes / Ray
  -> object storage checkpoints
  -> data pipeline
  -> experiment tracker
  -> observability
```

What to know:

* researcher ergonomics,
* reproducibility,
* cluster utilization,
* debugging distributed jobs,
* data throughput,
* checkpoint reliability,
* performance profiling.

### Agent Platform Engineer

Core stack:

```text
model API
  -> LangGraph / custom orchestrator
  -> Temporal / durable workflow
  -> MCP / tool registry
  -> sandboxed execution
  -> retrieval
  -> eval harness
  -> observability
```

What to know:

* explicit state,
* tool permissions,
* idempotency,
* durable workflows,
* human approvals,
* sandboxing,
* trace-based debugging.

---

# 12. Chapter Takeaways

Software engineering fundamentals are not separate from applied AI. They are what make applied AI usable.

Key ideas:

* Python runtime behavior matters because AI payloads are large and services are long-running.
* The GIL matters when choosing between threads, processes, async, and native code.
* Async is powerful for IO-bound orchestration, but blocking the event loop can break the whole service.
* Memory leaks usually come from reachable objects, unbounded caches, traces, tasks, or native allocations.
* SQL performance depends on query plans, indexes, partitioning, materialization, and realistic data.
* Distributed data systems trade simplicity for capacity and availability.
* ML data pipelines need schema contracts, lineage, validation, backfills, and skew monitoring.
* Scalable AI backends need separation between API orchestration and inference execution.
* Tech stacks should be learned as abstractions and failure modes, not as brand-name checklists.
* PyTorch, TensorFlow, and JAX differ mainly in execution and transformation mental models.
* Distributed training, serving, retrieval, evals, and observability each have distinct stack layers that must compose cleanly.
* Observability is not optional; it is how you debug probabilistic systems.

Compact interview framing:

> A production AI system is a normal distributed system with an unusually expensive, probabilistic core. I need to reason about Python runtime behavior, data systems, queues, caches, model calls, framework execution, distributed training, serving stacks, and observability together, because failures usually appear at the boundaries.

