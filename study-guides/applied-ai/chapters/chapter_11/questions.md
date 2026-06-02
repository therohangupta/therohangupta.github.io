---
layout: page
title: "Chapter 11 Questions: Software Engineering Fundamentals for AI Systems"
guide_type: questions
---

# Chapter 11 — Practice Questions

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

## Question 11A

**What changes when a system scales from one machine to many machines?**

### Sample Answer

The bottleneck shifts from local CPU, memory, and IO to coordination, network, partial failure, and skew. One machine fails as a unit; many machines fail partially. Data may need sharding, replicas may be stale, requests may hit different versions, and cross-shard operations become expensive. The design has to decide which operations require strong consistency and which can tolerate eventual consistency. Scaling adds capacity, but it also adds coordination cost, observability needs, and operational complexity.

---

## Question 12B

**How do you choose a shard key for a multi-tenant AI system?**

### Sample Answer

Start from access patterns. If most queries are tenant-scoped, tenant ID is a natural shard key because it keeps common reads, writes, permissions, and debugging local. But large tenants can create hot shards, so the design may need sub-sharding for heavy tenants. Hash sharding spreads load but makes tenant-level operations and debugging harder. Region sharding helps latency and compliance but complicates cross-region queries. A good shard key balances load while preserving the operations the product performs most often.

---

## Question 13C

**When should a system pay coordination cost, and when should it avoid it?**

### Sample Answer

Pay coordination cost when correctness or trust requires it: permissions, payments, irreversible tool actions, idempotency for side effects, and model or policy rollout state. Avoid global coordination on hot paths where stale data is acceptable, such as analytics counters, some ranking signals, cache entries, or non-critical freshness. Coordination improves consistency but adds latency, reduces availability during partitions, and creates operational complexity.

---

## Question 14D

**How do you handle hot shards or hot tenants?**

### Sample Answer

First confirm skew with per-shard metrics: QPS, latency, CPU, memory, queue depth, error rate, and storage growth. Mitigations include splitting large tenants into sub-shards, replicating hot read shards, caching hot keys, rate-limiting abusive tenants, moving heavy analytics off OLTP, load-aware routing, and rebalancing based on traffic rather than storage alone. The important point is that averages hide hot shards.

---

## Question 15

**How does Python memory management work?**

### Sample Answer

Python primarily manages memory through reference counting: objects are freed when their reference count drops to zero. CPython also has a cyclic garbage collector to clean up reference cycles that reference counting alone cannot free. Under the hood, Python uses private memory allocators and arenas for small objects. In production, memory may not immediately return to the operating system even after objects are freed, so engineers need to distinguish live object growth from allocator behavior.

---

## Question 16

**Explain reference counting and garbage collection.**

### Sample Answer

Reference counting tracks how many references point to an object. When the count reaches zero, CPython can deallocate the object immediately. Garbage collection handles cycles, such as two objects that reference each other even though nothing else can reach them. Reference counting gives predictable cleanup for many objects, but cycles require periodic GC work. Finalizers, global references, caches, and closures can make object lifetime less obvious.

---

## Question 17

**What is async programming and when should you use it?**

### Sample Answer

Async programming lets a program handle many concurrent IO-bound tasks without blocking a thread per task. In Python, `asyncio` uses an event loop where coroutines yield control while waiting for network, disk, database, or API responses. It is useful for high-concurrency services that spend much of their time waiting on IO, such as API gateways, retrieval services, or orchestration layers. It is not a magic speedup for CPU-bound work; CPU-heavy tasks need processes, native extensions, or separate workers.

---

## Question 18

**What is the difference between threading, multiprocessing, and asyncio?**

### Sample Answer

Threading runs multiple threads in one process and is useful for IO-bound work, but in CPython only one thread executes Python bytecode at a time because of the GIL. Multiprocessing runs separate processes, bypassing the GIL for CPU-bound work at the cost of more memory and inter-process communication overhead. `asyncio` runs many coroutines on an event loop, which is efficient for IO-bound concurrency but requires non-blocking libraries. The right choice depends on whether the bottleneck is CPU, IO, memory, or external services.

---

## Question 19

**What causes memory leaks in Python?**

### Sample Answer

Python memory leaks usually come from objects that remain reachable longer than intended. Common causes include unbounded caches, global lists or dictionaries, lingering references in closures, reference cycles with finalizers, callbacks that are never deregistered, large objects kept in logs or traces, and native extension leaks. I would debug with memory profiles, heap snapshots, object growth by type, and request-level reproduction. The fix is usually to bound caches, release references, stream large data, or isolate leaking work in restartable workers.

---

## Question 20

**Explain Python's GIL in depth.**

### Sample Answer

The Global Interpreter Lock is a CPython mutex that allows only one thread to execute Python bytecode at a time within a process. It simplifies memory management and protects interpreter internals, especially reference counting. The GIL does not prevent concurrency for IO-bound tasks because threads can release it while waiting on IO, and native extensions may release it during heavy computation. But it limits CPU-bound parallelism in pure Python threads. For CPU-heavy workloads, use multiprocessing, vectorized libraries, compiled extensions, or separate services.

---

## Question 21

**How would you profile Python code performance?**

### Sample Answer

I would first define the performance problem: CPU time, memory growth, IO latency, database time, or end-to-end request latency. For CPU, I would use profilers such as `cProfile`, sampling profilers, or py-spy. For memory, I would use tracemalloc, heap snapshots, and object growth analysis. For services, I would add tracing around request stages, database calls, model calls, queue wait, and serialization. Profiling should use realistic inputs because microbenchmarks can miss production bottlenecks like network waits, batching, and lock contention.

---

## Question 22

**What are metaclasses?**

### Sample Answer

Metaclasses are the classes of classes. In Python, a class definition creates a class object, and the metaclass controls how that class object is created. They can customize class construction, registration, validation, or dynamic method creation. They are powerful but often unnecessary; decorators, base classes, or simple registries are usually easier to understand. In interviews, the key is to know the mechanism and also know when not to use it.

---

## Question 23

**How do decorators work internally?**

### Sample Answer

A decorator is a callable that takes a function or class and returns a replacement. The `@decorator` syntax is shorthand for assigning `func = decorator(func)`. Function decorators often wrap the original function in another function that adds behavior before or after the call. Good decorators preserve metadata with `functools.wraps`, handle arguments carefully, and avoid hiding side effects. In production systems, decorators are commonly used for retries, tracing, auth checks, caching, and registration.

---

## Question 24

**How would you build a scalable Python backend for AI inference?**

### Sample Answer

I would separate the API layer from the inference workers. The API layer should authenticate requests, validate inputs, enforce quotas, route work, and return streaming responses when useful. Inference workers should batch requests, manage model clients or GPU runtimes, apply timeouts, and emit metrics for tokens, latency, errors, and cost. I would use queues for asynchronous work, autoscaling based on queue depth and GPU utilization, caches where safe, and backpressure when capacity is exhausted. The design should make model, prompt, and route versions observable so regressions can be rolled back quickly.

---

## Question 25

**What does Pipeline in scikit-learn do and why is it important?**

### Sample Answer

An sklearn Pipeline chains preprocessing and model steps into one fit/predict object. It matters because preprocessing is fit only on training folds during cross-validation, which prevents leakage. It also makes hyperparameter search, deployment packaging, and reproducibility easier because the transformation and model are treated as one artifact. In ML systems, the same principle applies beyond sklearn: keep feature transformations versioned with the model that expects them.

---

## Question 26

**What is the difference between fit(), transform(), and fit_transform()?**

### Sample Answer

`fit()` learns parameters from data, such as a scaler mean, vocabulary, or imputation value. `transform()` applies already learned parameters to data. `fit_transform()` does both, usually on training data for convenience. The important rule is to never fit preprocessing on test or production data when evaluating, because that leaks information and inflates metrics.

---

## Question 27

**What is the difference between a clustered and non-clustered index?**

### Sample Answer

A clustered index determines the physical or primary storage order of table rows, so a table generally has only one. A non-clustered index is a separate lookup structure that points back to rows and can exist on many columns or column combinations. Clustered indexes are useful for range scans and primary access patterns; non-clustered indexes speed selective filters and joins. The tradeoff is write overhead, storage cost, and choosing indexes that match real query patterns.

---

## Question 28

**How would you write a SQL query to find the top N users by transaction volume per month?**

### Sample Answer

I would aggregate transactions by user and month, then rank users within each month using a window function. For example: compute `SUM(amount)` grouped by `user_id` and month, then use `ROW_NUMBER() OVER (PARTITION BY month ORDER BY total_amount DESC)` and filter where the row number is less than or equal to N. The key concept is partitioned ranking after aggregation.

---

## Question 29

**What is a medallion architecture in data engineering?**

### Sample Answer

A medallion architecture organizes data into quality tiers. Bronze is raw ingested data kept close to source form. Silver is cleaned, validated, deduplicated, and joined data. Gold is business-ready or ML-ready data such as aggregates, features, or product tables. The pattern helps separate ingestion, cleaning, serving, backfills, lineage, and data quality ownership.
