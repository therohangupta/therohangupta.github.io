---
layout: page
title: "Chapter 3: Retrieval and Memory Systems"
guide_type: chapter
---

# Chapter 3 — Retrieval and Memory Systems

This chapter explains how to ground an LLM in information that is not already in the prompt or model weights.

Chapter 1 answered: "How do I control the model at runtime?"

This chapter answers: "How do I give the model the right external knowledge at the right time, and how do I decide what the system should remember?"

The interview signal is not whether you can say "use RAG." It is whether you can reason about:

* how documents become searchable units
* how queries become retrieval requests
* how dense, sparse, and hybrid retrieval differ
* how retrieved evidence becomes safe context
* how memory is written, read, compressed, and forgotten
* how the system fails when information is stale, noisy, poisoned, or too large
* how permissions, deletion, tenant isolation, and memory scope constrain retrieval

Retrieval is the external knowledge layer. Memory is the persistent state layer. Together they turn an LLM from a stateless text generator into a system that can use private data, cite sources, remember user preferences, and adapt across sessions.

Security note: retrieval and memory are trust-boundary systems. For the full treatment of ACL-aware retrieval, memory deletion, tenant isolation, and prompt injection through retrieved content, see [Chapter 8: Security, Privacy, and Trust Boundaries](../chapter_8/guide.html). For an end-to-end design, see the [Secure Enterprise RAG Support Agent capstone](../../capstones/secure_enterprise_rag_support_agent.html).

---

## Table of Contents

- TOC
{:toc}

---

# 1. The Core Mental Model

An LLM only sees the tokens in its context window.

Retrieval is the process of deciding which external information deserves to become part of that context window.

Memory is the process of deciding which past information should survive beyond the current request.

The simplest retrieval-augmented generation flow is:

1. User asks a question.
2. System rewrites or normalizes the query.
3. Retriever searches documents or memories.
4. Reranker sorts candidates by usefulness.
5. Context builder packs the best evidence into the prompt.
6. Model answers using that evidence.
7. System optionally writes new memory.

The key idea is:

> Retrieval is not "find text that looks similar." Retrieval is controlled information selection under latency, cost, and context constraints.

That is why production RAG is mostly about engineering the information path:

* what gets indexed
* how it gets chunked
* what metadata it carries
* what query is searched
* how candidates are scored
* what evidence is shown to the model
* what the model is allowed to claim

---

# 2. Retrieval Primitives

Retrieval systems are built from a small set of primitives.

## 2.1 Embeddings

An embedding maps text into a vector:

```text
text -> embedding model -> [0.12, -0.04, 0.81, ...]
```

The vector is a learned representation of semantic meaning. Similar texts should land near each other in vector space.

Embeddings exist because keyword overlap is not enough. A user might ask:

> "How do I reset billing access?"

The relevant document might say:

> "To restore invoice permissions, update the user's finance role."

Lexical search may miss this because the words differ. Dense embeddings can match the meaning.

Important embedding choices:

* **model**: general-purpose, domain-specific, multilingual, code-aware
* **dimensionality**: larger vectors may capture more nuance but cost more storage and search time
* **normalization**: cosine similarity is often implemented as dot product over normalized vectors
* **versioning**: changing the embedding model can make old vectors incompatible with new vectors

The production rule is simple:

> Embedding quality sets the ceiling for dense retrieval quality.

## 2.2 Similarity Search

Similarity search finds nearby vectors.

Common scoring functions:

* **cosine similarity**: angle between vectors
* **dot product**: useful when magnitude carries signal or vectors are normalized
* **Euclidean distance**: geometric distance in vector space

In practice:

```text
query embedding -> nearest neighbor search -> top-k candidate chunks
```

Exact nearest neighbor search compares the query against every vector. That is simple but expensive for large indexes.

Approximate nearest neighbor search, or ANN, trades a small amount of recall for much lower latency.

## 2.3 Indexing

An index is a data structure that makes search fast.

For dense retrieval, common index families include:

* **flat index**: exact search, simple, high recall, slower at scale
* **HNSW**: graph-based ANN, fast queries, memory-heavy
* **IVF**: cluster-based ANN, searches a subset of partitions
* **IVF-PQ**: IVF plus compression, lower memory, lower precision

For sparse retrieval, the classic index is an inverted index:

```text
term -> documents containing that term
```

This is the basis for BM25, Elasticsearch, and OpenSearch.

## 2.4 Chunking

Chunking splits large documents into searchable units.

A chunk should be small enough to retrieve precisely and large enough to contain useful context.

Common strategies:

* **fixed-size chunks**: simple token windows with overlap
* **semantic chunks**: split by headings, paragraphs, or topic boundaries
* **hierarchical chunks**: index small chunks but keep links to parent sections
* **sliding windows**: preserve boundary context with overlap

Chunking is one of the highest-leverage parts of RAG. Bad chunking can make a good embedding model look bad.

## 2.5 Metadata Filtering

Metadata filtering constrains retrieval using structured attributes.

Examples:

* tenant ID
* user ID
* document type
* product area
* timestamp
* source system
* access-control labels
* language
* version

Filtering exists because semantic similarity alone does not know whether a document is allowed, fresh, relevant to the right customer, or from the right product.

Strong retrieval systems usually filter before or during search, not after generation.

## 2.6 Retrieval Scoring

Retrieval scoring estimates usefulness.

The score may combine:

* vector similarity
* BM25 score
* recency
* authority of the source
* user or tenant match
* reranker score
* diversity penalty
* access-control validity

The important point is that "top-k nearest vectors" is only a starting point. Production scoring is often a ranking function over many signals.

---

# 3. Memory Primitives

Memory is persistent context with lifecycle rules.

The four core operations are:

## Write

Decide whether new information should be stored.

Examples:

* "The user prefers concise answers."
* "The user is working on the Acme onboarding project."
* "This support ticket was resolved by rotating the API key."

Writing memory should be selective. If every interaction becomes memory, the memory store fills with noise.

## Read

Retrieve memory that is relevant to the current request.

Memory read is usually a retrieval problem:

```text
current task -> query memory -> relevant memories -> prompt context
```

Read policy matters. Identity memory should not automatically mix with task memory unless it helps.

## Compress

Condense many memories into a smaller representation.

Examples:

* summarize a long conversation
* merge repeated preferences into one stable preference
* extract durable facts from episodic logs

Compression exists because memory grows faster than context windows and human attention.

## Forget

Delete, expire, hide, or downgrade memory.

Forgetting is not an afterthought. It is required for:

* privacy
* correctness
* freshness
* cost control
* user trust

The strongest memory systems have explicit retention policies instead of accumulating everything forever.

## Slow References vs Retrieval Memory

Retrieval memory and slow-reference learning can both look like "the system remembers something," but they store information in different places.

Retrieval memory stores external information that is read into the prompt at inference time:

```text
memory store -> retrieved context -> current model call
```

A slow reference stores behavioral or optimization memory in artifacts such as checkpoints, teacher policies, EMA copies, target networks, or frozen base models:

```text
teacher / checkpoint / EMA copy -> training signal -> future student behavior
```

The difference matters operationally. Retrieval memory can be edited, expired, permissioned, and cited. A distilled behavior is inside the model or adapter and needs training evals, rollback, and regression coverage.

Self-distillation can compress repeated retrieved or hinted behavior into weights, but that is no longer just memory retrieval. It is a model update.

---

# 4. How Retrieval Pipelines Compose

A production retrieval pipeline usually has more stages than a demo.

```text
user request
  -> query understanding
  -> query rewriting
  -> metadata filter construction
  -> dense retrieval
  -> sparse retrieval
  -> candidate merge
  -> reranking
  -> context construction
  -> generation
  -> citation verification
  -> memory write decision
```

Each stage fixes a different bottleneck.

Query rewriting fixes the mismatch between conversational user text and searchable document language.

Metadata filters fix scope and permission errors.

Dense retrieval fixes semantic mismatch.

Sparse retrieval fixes exact identifiers, rare terms, error codes, names, and abbreviations.

Reranking fixes noisy top-k candidates.

Context construction fixes the problem of giving the model too much, too little, or poorly ordered evidence.

Citation verification fixes the gap between "the model saw evidence" and "the final answer is actually grounded in that evidence."

---

# 5. Dense, Sparse, and Hybrid Retrieval

## Dense Retrieval

Dense retrieval uses embeddings.

Best for:

* semantic similarity
* paraphrases
* natural language questions
* concept matching
* cross-lingual or domain-specific meaning if the embedding model supports it

Weaknesses:

* can miss exact identifiers
* can retrieve plausible but wrong chunks
* depends heavily on embedding model quality
* requires vector index storage and updates

Dense retrieval answers: "What is semantically similar?"

## Sparse Retrieval

Sparse retrieval uses lexical features like term frequency and inverse document frequency. BM25 is the common baseline.

Best for:

* exact terms
* product names
* stack traces
* codes
* legal citations
* names and IDs

Weaknesses:

* misses paraphrases
* depends on tokenization and analyzers
* may overvalue keyword overlap without understanding meaning

Sparse retrieval answers: "What shares important words?"

## Hybrid Retrieval

Hybrid retrieval combines dense and sparse candidates.

A common flow:

1. Run vector search for semantic candidates.
2. Run BM25 for lexical candidates.
3. Merge candidates with score normalization or reciprocal rank fusion.
4. Rerank the merged candidate set.

Hybrid retrieval is often the best default for enterprise RAG because real corpora contain both natural language and exact identifiers.

The interview framing:

> Dense search catches meaning. Sparse search catches exactness. Hybrid search reduces the chance that either failure mode dominates.

---

# 6. Indexing and Vector Search in Practice

## FAISS

FAISS is a library for efficient vector similarity search. It is commonly used when you want local control over indexing, experimentation, or self-hosted retrieval.

Useful FAISS index types:

* `IndexFlatIP` or `IndexFlatL2` for exact baseline search
* IVF indexes for partitioned approximate search
* HNSW-style indexes for graph-based approximate search
* product quantization for memory reduction

FAISS is powerful but you usually need to build surrounding production pieces yourself: metadata storage, access control, ingestion, refresh, serving, and observability.

## HNSW

HNSW stands for Hierarchical Navigable Small World graph.

It builds a graph where nearby vectors are connected. Search navigates the graph from coarse to fine layers.

Best for:

* low-latency ANN
* high recall
* dynamic-ish workloads compared with some cluster indexes

Tradeoff:

* high memory usage
* index build parameters matter

Important knobs:

* `M`: graph connectivity
* `efConstruction`: build-time search breadth
* `efSearch`: query-time search breadth

Increasing `efSearch` improves recall but increases latency.

## IVF and ANN

IVF, or inverted file indexing, partitions vector space into clusters.

At query time, the system searches only the closest clusters instead of every vector.

Important knob:

* `nprobe`: number of clusters searched

Higher `nprobe` means better recall and worse latency.

IVF works well at large scale but needs careful training, partition sizing, and monitoring for recall regressions.

## pgvector

`pgvector` adds vector search to PostgreSQL.

Best for:

* small to medium corpora
* applications already centered on Postgres
* simple metadata joins and transactional workflows
* prototypes that may grow into production

Tradeoff:

* not always the best choice for very large, high-QPS vector workloads
* operational simplicity can matter more than raw benchmark speed

## Pinecone, Weaviate, and Milvus

Managed or dedicated vector databases provide indexing, serving, metadata filtering, replication, and scaling features.

Pinecone is commonly used as a managed vector database.

Weaviate provides vector search plus schema, hybrid search, and object-style storage.

Milvus is a scalable open-source vector database often used for large deployments.

The right choice depends less on marketing labels and more on:

* corpus size
* query volume
* metadata filtering needs
* update rate
* deployment constraints
* operational ownership

## Elasticsearch and OpenSearch

Elasticsearch and OpenSearch are strong lexical search engines and increasingly support vector search and hybrid retrieval.

They are attractive when:

* you already have search infrastructure
* BM25 matters
* filters, analyzers, and faceting matter
* logs, documents, and text search are already indexed there

They are less attractive if your workload is pure vector search at very large scale and you do not need lexical search features.

---

# 7. Scaling Retrieval: 10k Documents to 100M Documents

Retrieval architecture changes qualitatively as the corpus grows.

At small scale, the hard part is usually relevance quality: chunking, embeddings, metadata, and prompt construction. At large scale, the hard part becomes a coupled systems problem:

```text
recall + latency + memory + freshness + permissions + cost + operability
```

You rarely maximize all of these at once. The system chooses where to spend work.

## 7.1 The Scaling Ladder

A useful mental model:

| Corpus Size | Typical Shape | Main Bottleneck | Common Architecture |
| ----------- | ------------- | --------------- | ------------------- |
| 10k documents | one app database or local vector index | relevance quality | pgvector, FAISS flat/HNSW, simple metadata |
| 1M documents | dedicated retrieval service | ANN latency and ingestion | HNSW/IVF, hybrid search, reranking, cache |
| 100M documents | distributed retrieval platform | memory, sharding, freshness, coordination | sharded vector indexes, lexical indexes, routing, async ingestion, replicas |

The same RAG diagram may appear at every scale, but the failure modes change. A 10k-document system can often search broadly and rerank generously. A 100M-document system must route, partition, compress, cache, and limit expensive stages.

## 7.2 Why Naive Vector Search Breaks

Exact vector search compares the query against every vector.

If you have:

```text
100M chunks
768-dimensional embeddings
float32 vectors
```

the raw vector storage alone is roughly:

```text
100M * 768 * 4 bytes ≈ 307 GB
```

That excludes metadata, graph edges, index structures, replicas, caches, and operational overhead. HNSW may add substantial memory for graph links. Replication for availability multiplies storage again.

So the scaling question is not only:

```text
Can I search vectors quickly?
```

It is:

```text
Can I store, update, filter, replicate, route, and debug this index
while preserving enough recall under latency and cost limits?
```

## 7.3 Sharding Strategies

Sharding splits the retrieval corpus across multiple indexes or machines.

Common strategies:

| Strategy | How It Works | Best For | Main Risk |
| -------- | ------------ | -------- | --------- |
| Tenant sharding | route each tenant to its own shard or shard group | B2B / enterprise isolation | hot tenants, uneven shard sizes |
| Hash sharding | distribute chunks by hash of document/chunk ID | uniform load | query must fan out to many shards |
| Semantic sharding | partition by topic, product area, or cluster | fewer shards per query | routing mistakes lose recall |
| Time sharding | split by recency windows | fresh/recent-heavy queries | old but relevant docs may be missed |
| Region sharding | keep data near users or legal region | latency and compliance | cross-region queries become harder |

The shard key should match access patterns. If most queries are scoped to one tenant, tenant sharding is natural. If queries search a global public corpus, tenant sharding does not help. If most answers require recent docs, time sharding can reduce search work, but only if old documents are still reachable when needed.

## 7.4 Fanout vs Routing

A distributed retriever has two basic options:

```text
fanout:
  send query to many shards
  merge top-k results

routing:
  predict which shards matter
  search only those shards
```

Fanout protects recall but increases latency, network traffic, and coordination cost. Routing reduces work but can miss the answer if the router sends the query to the wrong shard.

This is one of the central scaling tradeoffs:

```text
more fanout -> better recall, worse latency/cost
less fanout -> better latency/cost, worse recall risk
```

Strong systems often use a hybrid:

1. Apply hard filters first: tenant, permissions, region, product.
2. Route to likely semantic/time shards.
3. Search a limited number of shards.
4. Merge candidates.
5. Rerank a bounded candidate set.
6. Fall back to broader search when confidence is low.

## 7.5 Scatter-Gather and Distributed Top-K

The distributed-systems name for broad shard search is usually **scatter-gather** or **distributed top-k retrieval**.

The shape is:

```text
query
  -> coordinator
  -> scatter to shard A / shard B / shard C
  -> each shard runs local ANN / BM25 / hybrid search
  -> each shard returns local top-k
  -> coordinator gathers candidates
  -> merge, normalize, dedupe, filter, rerank
  -> final top chunks enter context
```

This is a real and common pattern. Search engines, log search systems, distributed SQL engines, and vector databases often use some version of it.

It is similar in spirit to distributed ML collectives because each worker does local work and the system combines partial results. But it is not usually an **all-reduce** in the training sense. All-reduce combines dense tensors with an operation like sum or mean. Retrieval combines sparse ranked lists with top-k merge, score calibration, deduplication, and reranking.

The interview phrase:

> At large corpus size, retrieval becomes a distributed top-k problem. Each shard returns local candidates; a coordinator merges and reranks them under latency and recall constraints.

### Local Top-K vs Global Top-K

Local top-k can miss the true global top-k if each shard returns too few candidates.

Suppose final context needs 10 chunks. If each shard returns only 10, the coordinator sees a narrow slice from each shard. The true best global candidates may require one shard to return its top 50 because many relevant documents live there.

Common pattern:

```text
each shard returns local top 50
coordinator merges to global top 200
reranker selects final top 5-10
```

Increasing local k improves recall but increases:

* network transfer,
* coordinator merge work,
* reranker cost,
* tail latency.

### Score Calibration Across Shards

Scores from different shards may not be directly comparable.

Reasons:

* shards contain different distributions,
* ANN approximations differ by shard,
* dense and sparse scores use different scales,
* metadata filters change the candidate pool,
* some shards are fresher or larger than others.

A vector score of `0.82` from shard A may not mean exactly the same thing as `0.82` from shard B.

Mitigations:

* normalize scores per shard or per index type,
* use rank-based merging such as reciprocal rank fusion,
* keep separate candidate pools and let the reranker decide,
* calibrate scores against retrieval evals,
* use a cross-encoder reranker after merge when latency allows.

### Tail Latency

Scatter-gather latency is often controlled by the slowest shard:

```text
query latency ≈ slowest shard response + merge/rerank time
```

If a query fans out to 100 shards, one slow shard can dominate p95 or p99 latency.

Mitigations:

* query fewer shards with routing,
* set shard-level timeouts,
* return partial results when safe,
* issue hedged requests to replica shards,
* replicate hot shards,
* use hierarchical merging,
* degrade to cached or lexical-only results under overload.

Partial results are a product decision. They may be acceptable for exploratory search, but not for legal, safety, or permission-sensitive answers.

### Coordinator Bottleneck

The coordinator can become hot even if every shard is healthy.

It must:

* gather local candidates,
* deduplicate chunks from the same document,
* normalize scores,
* enforce final filters,
* merge dense and sparse results,
* call rerankers,
* build final context.

At high QPS, this layer needs its own scaling strategy: stateless coordinator replicas, bounded candidate counts, streaming merge, hierarchical coordinators, batch reranking, and metrics for merge time separately from shard search time.

### Hierarchical Merge

For very large fanout, systems may use multiple merge levels:

```text
leaf shards
  -> regional / shard-group coordinators
  -> global coordinator
  -> reranker / context builder
```

This reduces the amount of data one coordinator handles, but adds another coordination layer. It can improve throughput while increasing complexity and sometimes latency.

### Correctness Constraints

Permission filters should happen before or inside shard search, not only at the final coordinator. Otherwise the coordinator may receive many unauthorized candidates and have too few valid results left after filtering.

The safe order is:

```text
auth / tenant / ACL filters
  -> shard routing
  -> local retrieval over allowed candidates
  -> global merge
  -> rerank / context construction
```

Ranking can be approximate. Permissions should not be approximate.

## 7.6 Metadata Filtering at Scale

Metadata filtering is easy in a demo and hard at scale.

Two bad extremes:

```text
post-filtering:
  vector search globally
  remove unauthorized or wrong-scope results afterward
  -> wastes work and may return too few valid results

over-partitioning:
  create tiny indexes for every metadata combination
  -> operational explosion and poor recall
```

Better systems push high-selectivity, correctness-critical filters into the retrieval path:

* tenant ID,
* ACL / permission scope,
* region,
* document status,
* product/version.

Lower-stakes ranking features can be applied after candidate retrieval:

* recency score,
* authority score,
* popularity,
* source quality,
* diversity.

The rule:

> Filters that protect correctness or permissions should run before the model sees content. Ranking features that improve usefulness can run later.

## 7.7 ANN Index Tradeoffs at Large Scale

At scale, approximate nearest neighbor search is a knob, not a free lunch.

HNSW:

* strong recall and latency,
* high memory usage,
* good for read-heavy low-latency search,
* expensive at very large sizes if memory dominates.

IVF:

* partitions vector space into clusters,
* searches only selected clusters,
* scales better in memory/search work,
* recall depends on cluster quality and `nprobe`.

Product quantization:

* compresses vectors,
* reduces memory and bandwidth,
* can hurt recall because distances are approximate.

The practical shape:

```text
more recall -> search more graph edges / clusters / candidates
more speed -> search fewer candidates
less memory -> compress vectors
more compression -> lower precision
```

No index setting is universally right. Tune against retrieval evals, not only benchmark QPS.

## 7.8 Reranking at Scale

Rerankers improve precision but can become the bottleneck.

If first-stage retrieval returns:

```text
200 candidates per query
10,000 queries per minute
```

then the reranker sees:

```text
2,000,000 query-document pairs per minute
```

That can be more expensive than the retriever.

Scaling patterns:

* retrieve fewer candidates for easy queries,
* use cheap lexical/vector scores to prune before reranking,
* batch reranker calls,
* use a small reranker first and a stronger reranker only for hard queries,
* cache reranker scores for repeated query-document pairs,
* apply diversity selection before final context construction.

The tradeoff:

```text
larger candidate set -> better chance answer is included
larger candidate set -> higher reranking latency and cost
```

## 7.9 Freshness and Index Updates

Large indexes cannot always be rebuilt synchronously.

Common update patterns:

| Pattern | Use Case | Tradeoff |
| ------- | -------- | -------- |
| Batch rebuild | stable corpus, simple ops | stale between rebuilds |
| Incremental updates | frequent document changes | more complex consistency |
| Delta index | fresh docs searched separately from main index | merge complexity |
| Blue-green index | build new snapshot, then swap traffic | doubles temporary storage |
| Streaming ingestion | near-real-time updates | backpressure, ordering, and partial failure issues |

Freshness is a product requirement, not a universal good. A legal assistant may prefer a validated daily snapshot over a partially ingested live index. A support bot may need near-real-time policy updates. The architecture should match the freshness SLO.

## 7.10 Replication, Availability, and Consistency

Retrieval systems need replicas for availability and throughput.

Replicas create consistency questions:

* Has every replica loaded the same index snapshot?
* Are metadata and vectors updated atomically?
* Can a query see a new metadata record but an old vector?
* What happens during index rollout?
* Can rollback restore the previous index quickly?

For user-facing RAG, eventual consistency is often acceptable for ordinary document freshness but not for permissions. Access-control changes should propagate more strictly than relevance-ranking updates.

Strong interview framing:

> I would separate freshness requirements by data type. Permissions and deletion need strict handling. Ranking signals and embeddings can often be eventually consistent if the system records the index version used for each answer.

## 7.11 Hot Shards and Skew

Scaling problems often come from skew, not average load.

Examples:

* one large tenant has most documents,
* one product area receives most queries,
* one viral document is retrieved constantly,
* one region gets a traffic spike,
* one shard owns too many high-degree HNSW nodes or popular chunks.

Mitigations:

* split hot tenants across shard groups,
* replicate hot shards,
* cache hot query and retrieval results,
* use load-aware routing,
* isolate heavy tenants,
* rebalance shards based on actual query load, not only storage size.

Average QPS can look fine while one shard is melting. Monitor per-shard latency, QPS, memory, cache hit rate, and recall.

## 7.12 Scaling Checklist

When asked how retrieval changes from 10k to 100M documents, answer in layers:

1. **Data model:** chunking, document IDs, metadata, ACLs, versions.
2. **Index choice:** flat/HNSW/IVF/PQ/hybrid sparse+dense.
3. **Partitioning:** tenant, region, time, semantic, hash.
4. **Query routing:** fanout vs routed search.
5. **Candidate pipeline:** first-stage recall, merge, prune, rerank, diversify.
6. **Freshness:** batch rebuild, delta index, streaming updates, blue-green snapshots.
7. **Reliability:** replicas, circuit breakers, fallbacks, index rollback.
8. **Observability:** per-shard metrics, recall evals, query logs, index versions.
9. **Tradeoffs:** recall vs latency vs memory vs freshness vs coordination.

The strongest answer makes the scaling bottleneck explicit. Do not say "use a vector database" as if that solves the system.

---

# 8. Chunking and Document Modeling

Chunking is where document structure becomes retrieval structure.

## Fixed-Size Chunking

Fixed-size chunking splits text every N tokens or characters.

Benefits:

* simple
* predictable
* easy to implement

Costs:

* can split a definition from its explanation
* can separate a table header from table rows
* can create chunks with no standalone meaning

Overlap helps but increases index size and duplicate retrieval.

## Semantic Chunking

Semantic chunking uses natural boundaries:

* headings
* sections
* paragraphs
* list items
* code blocks
* speaker turns

This usually improves retrieval because each chunk is more coherent.

The cost is implementation complexity. You need parsers for Markdown, HTML, PDFs, docs, support tickets, or code.

## Hierarchical Chunking

Hierarchical chunking stores multiple levels:

```text
document
  -> section
      -> paragraph chunk
```

You can retrieve small chunks for precision, then include the parent section for context.

This is useful when a single paragraph matches the query but the answer requires surrounding definitions, caveats, or examples.

## Chunk Size Tradeoff

Small chunks:

* improve precision
* reduce irrelevant context
* can lose necessary surrounding information

Large chunks:

* preserve context
* reduce boundary failures
* increase noise and token cost

The practical answer is not one magic chunk size. It is to evaluate retrieval quality on realistic questions and tune chunking around the corpus.

---

# 8. Metadata Design

Metadata is the difference between a demo retriever and a production retriever.

Useful metadata often includes:

* stable document ID
* chunk ID
* parent section ID
* source URL or path
* title
* heading path
* created and updated timestamps
* tenant or customer ID
* access-control groups
* language
* product area
* document type
* version
* embedding model version

Good metadata supports:

* authorization
* filtering
* freshness ranking
* deduplication
* citation display
* index rebuilds
* debugging

Bad metadata causes production failures that look like model failures.

For example, if a user asks about version 2 of an API but the retriever returns version 1 docs, the model may answer fluently and incorrectly. The root cause is not generation. It is metadata and ranking.

---

# 9. Retrieval Scoring and Reranking

First-stage retrieval should prioritize recall. Reranking should prioritize precision.

## First-Stage Retrieval

First-stage retrieval collects candidates quickly.

Examples:

* top 50 dense candidates
* top 50 BM25 candidates
* recent memories from the current user
* exact matches on IDs

This stage should avoid missing the answer.

## Score Merging

Dense and sparse scores are not naturally comparable.

Common merge techniques:

* normalize scores into a common range
* use weighted sums
* use reciprocal rank fusion
* keep separate candidate pools and let reranking decide

Reciprocal rank fusion is popular because it uses ranks instead of raw scores:

```text
score(doc) = sum(1 / (k + rank_in_list))
```

It is simple and robust when score scales differ.

## Rerankers and Cross-Encoders

A reranker scores a query-document pair more carefully than first-stage retrieval.

Cross-encoders read the query and candidate chunk together:

```text
reranker(query, candidate_text) -> relevance score
```

They are usually more accurate than embedding similarity but slower because each query-candidate pair requires model inference.

Use rerankers when:

* top-k quality matters
* documents are noisy
* first-stage retrieval returns many plausible candidates
* the answer depends on exact relevance, not just semantic neighborhood

Tradeoff:

* better precision
* higher latency and cost

---

# 10. Query Rewriting

User questions are often bad search queries.

Examples:

* "What about the thing from yesterday?"
* "Can I do this for enterprise accounts?"
* "Why did it fail?"

Query rewriting turns conversational input into searchable text.

Common rewrite operations:

* resolve pronouns using conversation history
* expand abbreviations
* add product or tenant context
* generate multiple query variants
* extract filters from natural language
* separate semantic query text from structured constraints

Example:

```text
User: "Can I do this for enterprise accounts?"
Rewrite: "Does the bulk invoice export feature support enterprise accounts?"
Filters: product_area=billing, account_type=enterprise
```

Query rewriting improves recall, but it can also inject wrong assumptions. A good system logs both the original and rewritten query so failures can be debugged.

---

# 11. Context Construction

Context construction decides what the model actually sees.

This is not the same as retrieval. Retrieval returns candidates. Context construction builds the prompt.

Important choices:

* how many chunks to include
* whether to include summaries or raw text
* whether to group chunks by source
* how to order evidence
* how to include metadata and citations
* how much conversation history to keep
* where to place the strongest evidence

## Lost-in-the-Middle Mitigation

Models often use information at the beginning and end of long contexts more reliably than information buried in the middle.

Mitigations:

* put the most relevant evidence first
* repeat critical constraints near the answer instruction
* group related chunks together
* keep context shorter when possible
* use summaries to compress low-priority evidence
* place source IDs close to quoted evidence

More context is not automatically better. More irrelevant context can make the answer worse.

---

# 12. Citations and Grounding

Grounding means the answer is supported by evidence.

Citations are the user-visible trace from answer claims to evidence.

A good citation system needs:

* stable source IDs
* chunk-to-document mapping
* page, section, URL, or timestamp metadata
* answer instructions that require source attribution
* post-generation checks for unsupported claims

There is a subtle failure mode:

> The model can cite a document it saw without the claim actually being supported by that document.

So citations should not be treated as proof by themselves. Stronger systems verify that cited spans contain the claimed information.

Practical grounding pattern:

1. Ask the model to answer only from supplied evidence.
2. Require citations for factual claims.
3. Reject or flag claims without citation.
4. Optionally run a verifier over answer-citation pairs.

---

# 13. Memory Systems

Memory is retrieval over a special corpus: the system's past interactions and learned state.

## 13.1 Short-Term Context Memory

Short-term memory is the working context of the current session.

Examples:

* recent messages
* current task state
* active tool results
* temporary goals

It is usually kept in the prompt, a session store, or a conversation buffer.

Tradeoff:

* easy to use
* quickly hits context limits
* can carry stale assumptions forward

## 13.2 Long-Term Vector Memory

Long-term vector memory stores durable facts or episodes in a searchable index.

Examples:

* user preferences
* past decisions
* resolved issues
* project facts

Read path:

```text
current request -> embed query -> retrieve relevant memories -> inject selected memories
```

Write path:

```text
interaction -> memory extraction -> validation -> storage with metadata
```

Long-term memory should be scoped by user, workspace, tenant, and sensitivity.

## 13.3 Episodic vs Semantic Memory

Episodic memory stores events:

* "On May 3, the user asked to migrate billing jobs to a queue."
* "Ticket 1842 was fixed by updating the webhook secret."

Semantic memory stores generalized facts:

* "The user prefers Python examples."
* "The billing service uses Stripe webhooks."

Episodic memory is useful for auditability and temporal context. Semantic memory is useful for personalization and durable knowledge.

Strong systems often derive semantic memory from repeated episodic evidence.

## 13.4 Summarization Memory

Summarization memory compresses long histories.

Useful patterns:

* rolling session summary
* project summary
* decision log
* user preference summary
* unresolved tasks summary

The risk is summary drift. If a summary is wrong, every later answer may inherit that wrong state.

Mitigation:

* preserve links to source episodes
* update summaries conservatively
* allow memory inspection and correction

## 13.5 Identity and Personalization Memory

Identity memory stores stable user-specific preferences or facts.

Examples:

* preferred language
* preferred answer length
* timezone
* project role
* recurring constraints

This memory can improve product experience, but it has privacy and trust implications.

Rules of thumb:

* do not infer sensitive attributes casually
* keep identity memory scoped and inspectable
* distinguish user-stated facts from model-inferred guesses
* let users delete or correct memory

## 13.6 Forgetting Policies

Forgetting policies decide when memory should be removed or downgraded.

Common policies:

* time-to-live expiration
* max memory count per user or project
* sensitivity-based retention
* recency decay in ranking
* explicit user deletion
* confidence-based pruning
* merge duplicates into summaries

Forgetting improves quality because stale facts are often worse than missing facts.

---

# 14. Real Implementation Patterns

## 14.1 Ingestion Pipeline

A practical ingestion pipeline:

1. Load documents from source systems.
2. Parse into structured text.
3. Split into chunks.
4. Attach metadata.
5. Compute embeddings.
6. Upsert vectors and metadata into an index.
7. Store raw source text in durable storage.
8. Record index and embedding versions.

Important operational details:

* make ingestion idempotent
* track deleted documents
* support partial reindexing
* keep source-of-truth IDs stable
* log chunk counts and embedding failures

## 14.2 Retrieval Cache

Retrieval caches store results for repeated queries or repeated embeddings.

Cache layers:

* query rewrite cache
* embedding cache
* retrieval result cache
* reranking cache
* final answer cache for deterministic FAQ-style systems

Cache keys should include:

* normalized query
* filters
* index version
* embedding model version
* user or tenant scope

If the cache key ignores permissions or index version, it can return unsafe or stale results.

## 14.3 Hybrid Search Flow

A robust hybrid flow:

1. Build structured filters from user, tenant, permissions, and query.
2. Run BM25 for exact lexical candidates.
3. Run dense vector search for semantic candidates.
4. Merge candidates with reciprocal rank fusion.
5. Remove duplicates using stable document and chunk IDs.
6. Rerank the top candidates.
7. Build context with source metadata.

This flow is common because it handles both "what does this mean?" and "find this exact thing."

## 14.4 Reranking Pipeline

Reranking usually runs after candidate generation:

```text
top 100 candidates -> cross-encoder reranker -> top 5 to 10 context chunks
```

Production considerations:

* cap candidate count to control latency
* batch reranker calls
* cache repeated query-candidate scores
* use a cheaper reranker for low-risk queries
* skip reranking when first-stage score confidence is high

## 14.5 Memory Write Pipeline

Memory writes should be treated like state mutations, not casual logging.

A safer write pipeline:

1. Extract candidate memory from the interaction.
2. Classify memory type: preference, fact, episode, task, identity.
3. Check sensitivity and policy.
4. Check whether similar memory already exists.
5. Update, merge, or insert.
6. Attach source, timestamp, scope, and confidence.

The important distinction:

* logs record what happened
* memory stores what should influence future behavior

---

# 15. Tradeoffs and Performance

## 15.1 Latency

Retrieval adds latency before generation.

Latency sources:

* query rewriting model call
* embedding call
* vector search
* BM25 search
* metadata filtering
* reranking model call
* context construction

Common optimizations:

* cache embeddings
* parallelize dense and sparse retrieval
* cap candidate counts
* use approximate indexes
* batch reranker requests
* skip expensive stages for easy queries

## 15.2 Cache Hit Rate

Caching can make retrieval cheap, but only for repeated or normalized queries.

High cache hit rate is more likely when:

* queries are FAQ-like
* filters are stable
* documents change slowly
* query rewriting normalizes variations

Low cache hit rate is common in open-ended conversational systems.

## 15.3 Index Update Cost

Indexes are not free to update.

Update costs include:

* embedding new or changed chunks
* deleting stale chunks
* rebuilding ANN structures
* warming caches
* maintaining consistency between metadata and vectors

High-write systems need different design than mostly static documentation systems.

## 15.4 Memory Growth

Memory grows with usage.

If unchecked, memory growth causes:

* higher storage cost
* slower retrieval
* more irrelevant recalls
* privacy risk
* worse personalization due to stale facts

Compression and forgetting are performance features, not just product features.

## 15.5 Precision and Recall

Retrieval precision means the returned chunks are relevant.

Retrieval recall means the system finds the chunks that contain the answer.

Tradeoff:

* high recall first-stage retrieval returns more candidates and costs more downstream
* high precision context reduces model confusion but risks missing useful evidence

RAG systems often optimize for recall early and precision late:

```text
retrieve broadly -> rerank carefully -> include selectively
```

## 15.6 Cost

Cost comes from:

* embedding generation
* vector database storage
* query volume
* reranker inference
* longer prompts
* observability and evaluation

Long context can hide retrieval quality problems but increase model cost. Better retrieval often reduces generation cost by shrinking prompts.

---

# 16. Failure Modes

## 16.1 Bad Chunking

Symptoms:

* retrieved chunks look related but do not contain the answer
* answers miss important caveats
* citations point to vague passages

Cause:

* chunks are too small, too large, or split across semantic boundaries

Fix:

* evaluate chunking on real questions
* use semantic or hierarchical chunking
* preserve headings and parent context

## 16.2 Stale Memory

Symptoms:

* the assistant remembers old preferences
* outdated project facts override current instructions
* users lose trust

Fix:

* timestamps
* recency decay
* explicit updates
* user-visible memory controls
* expiration policies

## 16.3 Retrieval Poisoning

Retrieval poisoning happens when malicious or low-quality content enters the retrievable corpus.

Examples:

* a document says "ignore all previous instructions"
* a support ticket contains untrusted user text
* a web page injects prompt instructions

Fix:

* treat retrieved text as data, not instructions
* separate system instructions from evidence
* sanitize untrusted sources
* rank by source authority
* use allowlisted corpora for high-risk workflows

## 16.4 Embedding Drift

Embedding drift happens when embeddings are produced by different models or versions.

Symptoms:

* retrieval quality changes after model upgrade
* new documents behave differently from old documents
* similarity scores become less meaningful

Fix:

* version embeddings
* re-embed full indexes when changing models
* compare recall before and after migration

## 16.5 Noisy Top-K Results

Dense search often returns semantically adjacent but answer-irrelevant chunks.

Fix:

* hybrid search
* reranking
* better chunking
* metadata filters
* query rewriting
* diversity controls

## 16.6 Context Overload

Too much retrieved context can make the model worse.

Symptoms:

* answer cites irrelevant sources
* model misses the key fact
* answer blends conflicting documents

Fix:

* reduce top-k
* rerank
* group evidence
* summarize low-priority context
* resolve conflicting sources before generation

## 16.7 Metadata Mismatch

Metadata mismatch happens when filters do not match how documents are labeled.

Examples:

* product names changed
* tenant IDs are missing
* access labels are stale
* document version is not tracked

Fix:

* validate metadata during ingestion
* monitor empty-result rates
* log filters used at query time
* maintain stable taxonomies

---

# 17. What to Say in an Interview

If asked:

> "How would you build retrieval for an LLM product?"

A strong answer is:

> "I would start by modeling the corpus, because retrieval quality depends heavily on chunking and metadata. I would create semantically coherent chunks, store stable source IDs and access-control metadata, embed the chunks, and index them in a vector store. At query time I would build filters, run dense and probably sparse retrieval in parallel, merge candidates, rerank the top set, then construct a short grounded context with citations. I would evaluate retrieval separately from generation using realistic questions, and I would monitor recall, precision, latency, stale results, and unsupported claims."

If asked:

> "Why not just put all documents in the prompt?"

A strong answer is:

> "Because context is expensive, limited, and noisy. Retrieval is an information selection problem. The system should choose the smallest set of high-value evidence that answers the current question while respecting permissions and freshness."

If asked:

> "How would you design memory?"

A strong answer is:

> "I would separate logs from memory. Logs record everything; memory stores only durable facts that should influence future behavior. I would define write policies, scopes, confidence, timestamps, and forgetting rules. Reads would use retrieval plus metadata filters so that only relevant and allowed memories enter the prompt."

The meta-answer:

> Retrieval and memory are not model tricks. They are data systems around the model. The hard parts are representation, indexing, ranking, context selection, lifecycle management, and evaluation.

---

# 18. When Retrieval Makes Things Worse

Retrieval is not automatically a quality improvement. It improves a system only when retrieved evidence is relevant, fresh, permitted, and compact enough for the model to use.

Retrieval can make answers worse when:

* the top result is semantically similar but factually irrelevant
* stale documents outrank current policy
* metadata filters silently exclude the correct source
* poisoned or user-authored content enters the evidence set
* too many chunks crowd out the key passage
* latency from search and reranking exceeds the product budget
* citations create false confidence even though the cited text does not support the answer

The practical test is not "did retrieval run?" It is:

```text
Did the retrieved context increase the probability of a correct, grounded, policy-compliant answer enough to justify the latency and cost?
```

If the answer is no, the right fix may be better chunking, stronger filters, reranking, source authority, query rewriting, smaller top-k, or no retrieval for that class of request.

See also: Chapter 1's retrieval-augmented workflow section for runtime control, Chapter 4's evaluation chapter for measuring retrieval quality, and Chapter 6's production chapter for the latency and cost impact of retrieval services.

---

# 19. Retrieval and Memory Takeaways

If you remember only one thing:

> RAG quality is mostly determined before the model answers.

The most important levers are:

* chunking
* metadata
* embedding quality
* dense/sparse/hybrid retrieval choice
* reranking
* context construction
* citation verification
* memory write and forgetting policy

For interviews, do not stop at "use a vector database." Explain the pipeline:

```text
ingest -> chunk -> embed -> index -> retrieve -> rerank -> construct context -> generate -> verify -> remember or forget
```

That is the full system.

---

# 20. What Comes Next

Chapter 3 moves from retrieval and memory into agents.

Retrieval gives an LLM access to knowledge.
Memory gives it continuity.

Agents add:

* state
* actions
* observations
* planning
* execution loops
* stopping rules
* budgets

That is where an LLM system stops being only a question-answering workflow and starts becoming a product layer that can act over time.

[Chapter 13](../chapter_13/guide.html) adds the systems view underneath retrieval-augmented generation. Retrieved context is not free: larger top-k, longer chunks, and memory summaries increase prompt tokens, prefill time, KV-cache memory, and queue pressure. Good RAG design balances answer quality against token load and latency, not retrieval recall alone.
