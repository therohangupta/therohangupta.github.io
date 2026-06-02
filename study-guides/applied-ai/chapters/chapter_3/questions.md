---
layout: page
title: "Chapter 3 Questions: Retrieval and Memory Systems"
guide_type: questions
---

# Chapter 3 — Practice Questions

Explanatory material for this chapter lives in [`guide.md`](guide.html).

---

# Common Interview Questions and Sample Answers

---

## Question 1

**What problem does retrieval solve in an LLM system?**

### Sample Answer

Retrieval solves the problem that the model only sees its prompt and may not know private, current, or domain-specific information. A retrieval system selects relevant external evidence and places it into the context window so the model can answer from grounded information instead of relying only on weights.

---

## Question 2

**What is the difference between retrieval and memory?**

### Sample Answer

Retrieval usually means selecting information from an external corpus such as documents, tickets, code, or knowledge base articles. Memory is persistent state created or updated by the system over time, such as user preferences, prior decisions, or summarized session history. Both are read through retrieval-like mechanisms, but memory also needs explicit write, update, compression, and forgetting policies.

---

## Question 3

**Why is chunking so important in RAG?**

### Sample Answer

Chunking defines the unit of retrieval. If chunks are too small, they may omit the surrounding context needed to answer. If chunks are too large, retrieval becomes noisy and wastes prompt tokens. Good chunking preserves semantic boundaries and makes each retrieved unit useful on its own or linkable to a useful parent section.

---

## Question 4

**Implementation tradeoff: how would you choose a chunk size and overlap?**

### Sample Answer

I would start from the document structure and expected questions rather than picking a universal size. For conceptual docs I might split by headings and paragraphs; for logs or transcripts I might use windows with overlap. Larger chunks preserve context but add noise and token cost. Smaller chunks improve precision but risk boundary failures. I would tune using a retrieval evaluation set with realistic queries.

---

## Question 5

**What is dense retrieval good at, and where does it fail?**

### Sample Answer

Dense retrieval is good at semantic matching, paraphrases, and natural language queries. It can find relevant text even when the words differ. It fails on exact identifiers, rare names, error codes, and cases where semantically similar text is not actually the answer. It also depends heavily on embedding model quality.

---

## Question 6

**What is sparse retrieval good at, and where does it fail?**

### Sample Answer

Sparse retrieval, often BM25, is good at exact terms, product names, IDs, stack traces, and domain-specific phrases. It fails when the query and document use different wording for the same concept. It does not understand meaning in the same way embeddings do.

---

## Question 7

**Implementation tradeoff: when would you use hybrid retrieval instead of only vector search?**

### Sample Answer

I would use hybrid retrieval when the corpus contains both natural language concepts and exact terms. Enterprise corpora often have product names, account IDs, error codes, and policy language. Dense search catches meaning; BM25 catches exactness. The cost is more system complexity, score merging, and often reranking, but the quality is usually more robust.

---

## Question 8

**How does a reranker improve retrieval quality?**

### Sample Answer

First-stage retrieval is optimized for speed and recall. A reranker looks more carefully at query-candidate pairs and reorders the candidate set for precision. Cross-encoder rerankers are often stronger because they process the query and document together, but they add latency and inference cost.

---

## Question 9

**Implementation tradeoff: how many candidates should you send to a reranker?**

### Sample Answer

Enough to preserve recall, but not so many that latency and cost explode. A common pattern is to retrieve 50 to 200 first-stage candidates, rerank them, and send the top 5 to 10 chunks to the model. The right number depends on corpus quality, query difficulty, reranker cost, and latency budget.

---

## Question 10

**Why is metadata filtering important?**

### Sample Answer

Metadata filtering enforces scope, permissions, freshness, and product relevance. Similarity alone cannot know whether a document belongs to the right tenant, user, version, or access-control group. Without metadata, the system may retrieve a semantically relevant but unauthorized or outdated document.

---

## Question 11

**Implementation tradeoff: what metadata would you store with each chunk?**

### Sample Answer

I would store stable document ID, chunk ID, parent section ID, source path or URL, title, heading path, timestamps, tenant or user scope, access-control labels, product area, document type, version, language, and embedding model version. More metadata improves filtering and debugging, but it increases ingestion complexity and requires a stable taxonomy.

---

## Question 12

**What is embedding drift?**

### Sample Answer

Embedding drift happens when vectors in the same index are produced by different embedding models or incompatible versions. Similarity scores become less meaningful, and retrieval quality can silently degrade. The fix is to version embeddings and re-embed the corpus when changing embedding models.

---

## Question 13

**How would you evaluate retrieval separately from generation?**

### Sample Answer

I would create realistic queries with known relevant documents or answer-containing chunks. Then I would measure recall at k, precision at k, mean reciprocal rank, and whether the final context contains enough evidence to answer. This isolates whether failures come from retrieval or from the model's generation.

---

## Question 14

**What is lost-in-the-middle, and how do you mitigate it?**

### Sample Answer

Lost-in-the-middle is the tendency for models to underuse information buried in the middle of long contexts. Mitigations include shortening context, placing the strongest evidence first or near the instruction, grouping related evidence, summarizing low-priority material, and avoiding unnecessary chunks.

---

## Question 15

**Implementation tradeoff: FAISS, pgvector, or a managed vector database?**

### Sample Answer

FAISS is strong for local control, experimentation, and custom indexes, but you build the service layer yourself. pgvector is attractive if the app already uses Postgres and the corpus is small to medium with useful relational metadata. Managed vector databases like Pinecone, Weaviate, or hosted Milvus reduce operational burden and scale better for dedicated vector workloads, but add vendor or platform complexity.

---

## Question 16

**What is the difference between HNSW and IVF-style indexes?**

### Sample Answer

HNSW is graph-based. It searches by navigating a graph of nearby vectors and often gives strong recall at low latency, but uses more memory. IVF partitions vectors into clusters and searches only selected partitions. IVF can scale well and reduce search work, but recall depends on partition quality and how many clusters are probed.

---

## Question 17

**How should citations be designed in a RAG system?**

### Sample Answer

Citations should use stable source metadata such as document ID, URL, section, page, or timestamp. The prompt should require citations for factual claims, and the system should preferably verify that cited sources actually support the claim. A citation is not automatically proof; the cited span must contain the evidence.

---

## Question 18

**What is retrieval poisoning?**

### Sample Answer

Retrieval poisoning occurs when malicious or low-quality content enters the retrievable corpus and influences generation. For example, a retrieved page might contain instructions telling the model to ignore system rules. The fix is to treat retrieved content as data, separate it from instructions, sanitize untrusted sources, and rank by source authority.

---

## Question 19

**How would you design long-term memory for a user-facing assistant?**

### Sample Answer

I would separate raw logs from memory. Memory writes would be selective and classified by type, such as preference, project fact, episode, or identity. Each memory would have scope, source, timestamp, confidence, and retention policy. Reads would use retrieval with metadata filters, and users should be able to inspect, correct, and delete memory.

---

## Question 20

**Implementation tradeoff: when should a memory be summarized instead of stored as raw episodes?**

### Sample Answer

Summarization is useful when many episodes repeat the same durable pattern or when raw history is too large for efficient retrieval. It reduces cost and noise, but it can introduce summary drift or erase important details. I would keep links to source episodes for auditability and update summaries conservatively.

---

## Question 21

**What is the difference between episodic and semantic memory?**

### Sample Answer

Episodic memory stores events, such as what happened in a session or ticket. Semantic memory stores generalized facts, such as user preferences or stable project knowledge. Episodic memory is useful for chronology and auditability; semantic memory is useful for personalization and reusable context.

---

## Question 22

**Why can adding more retrieved chunks hurt answer quality?**

### Sample Answer

More chunks can add irrelevant or conflicting information, increase prompt cost, and bury the key evidence. Retrieval should select high-value context, not maximize context size. A smaller, better-ranked context often produces more grounded answers than a large noisy context.

---

## Question 23

**How does retrieval change model behavior in terms of information flow?**

### Sample Answer

Retrieval changes the input signal. Instead of asking the model to answer from parameters alone, the system injects external evidence into the prompt. That shifts the conditional distribution toward answers supported by the retrieved context. If retrieval injects noisy or wrong context, the model's output will often follow that bad signal.

---

## Question 24

**What would you monitor in a production retrieval system?**

### Sample Answer

I would monitor retrieval latency, empty-result rate, recall and precision on evaluation sets, reranker latency, cache hit rate, index freshness, embedding failures, permission-filter behavior, citation support rate, memory growth, and user feedback on answer quality. I would also log query rewrites, filters, retrieved chunk IDs, and index versions for debugging.

---

## Question 25

**What are the tradeoffs between fine-tuning and RAG?**

### Sample Answer

Fine-tuning changes model weights, so it is useful for teaching durable behavior, domain style, formats, and task patterns. It is less ideal for fast-changing facts because updating weights is slower, riskier, and harder to audit. RAG keeps knowledge outside the model and retrieves it at runtime, which makes updates, citations, permissions, and freshness easier. The tradeoff is that RAG adds retrieval latency and can fail if chunking, ranking, or context construction is poor. In production, fine-tuning often shapes behavior while RAG supplies current or private knowledge.

---

## Question 26

**How does a RAG system change when scaling from 10k documents to 100M documents?**

### Sample Answer

At 10k documents, the main problems are chunking, embedding quality, metadata, and prompt construction. A simple pgvector or FAISS index may be enough. At 100M documents, retrieval becomes a distributed systems problem: vector memory, ANN indexing, sharding, metadata filtering, index freshness, replication, reranking cost, and per-shard observability all matter. I would move from a single broad index to a routed and sharded retrieval platform with hybrid sparse+dense retrieval, strict pre-filtering for permissions, approximate search, bounded reranking, async ingestion, index versioning, and rollback.

---

## Question 27

**How would you shard a large vector retrieval system?**

### Sample Answer

I would choose the shard key based on access patterns. For enterprise RAG, tenant or region sharding is natural because most queries are scoped by customer and permissions. For global corpora, semantic, time, or hash sharding may be better. The tradeoff is fanout versus recall: searching many shards improves recall but increases latency and coordination cost; routing to fewer shards is faster but can miss answers. I would monitor per-shard latency, QPS, memory, recall, and hot-shard skew.

---

## Question 28

**What is the tradeoff between fanout search and routed search?**

### Sample Answer

Fanout sends the query to many shards and merges results. It protects recall but increases network traffic, tail latency, and coordination cost. Routed search predicts which shards are relevant and searches fewer of them. It is cheaper and faster, but recall depends on the router. A strong system often combines hard filters, such as tenant and ACL, with semantic or time-based routing and falls back to broader search when confidence is low.

---

## Question 29

**Is distributed retrieval basically an all-reduce over sharded vector stores?**

### Sample Answer

The intuition is close, but the exact pattern is usually scatter-gather or distributed top-k, not all-reduce. A coordinator sends the query to multiple shards, each shard runs local retrieval and returns local top-k candidates, and the coordinator merges, normalizes, deduplicates, filters, and reranks the combined candidate set. All-reduce combines dense tensors with an operation like sum or mean; retrieval combines sparse ranked lists. The main tradeoffs are recall versus fanout latency, local top-k size, score calibration across shards, coordinator bottlenecks, and tail latency from slow shards.

---

## Question 30

**Why can local top-k from each shard miss the global best results?**

### Sample Answer

If each shard returns too few candidates, the coordinator may never see some documents that should be in the global top results. For example, if one shard contains many highly relevant documents but only returns top 10, the true global top 10 might require that shard's top 50. Increasing local k improves recall but increases network transfer, merge work, reranker cost, and latency. Large systems often over-retrieve locally, merge to a larger global candidate set, and then rerank down to the final context.

---

## Question 31

**Why are scores hard to compare across retrieval shards?**

### Sample Answer

Different shards can have different data distributions, index approximations, freshness, sizes, or metadata filters. A similarity score from one shard may not mean the same thing as the same score from another shard. Hybrid retrieval adds another mismatch because dense and sparse scores use different scales. Mitigations include score normalization, rank fusion, calibration on retrieval evals, keeping separate candidate pools, and using a cross-encoder reranker after the merge.

---

## Question 32

**How does scatter-gather retrieval affect tail latency?**

### Sample Answer

Fanout latency is often dominated by the slowest shard plus merge and rerank time. Querying many shards increases the chance that one shard is slow. Mitigations include routing to fewer shards, shard-level timeouts, partial results when safe, hedged requests to replicas, hot-shard replication, hierarchical merging, and degraded fallback modes. Partial results are fine for some exploratory search, but not for permission-sensitive or high-stakes answers.

---

## Question 33

**Why is metadata filtering hard at retrieval scale?**

### Sample Answer

Post-filtering wastes work and can return too few valid results if most retrieved chunks are unauthorized or wrong-scope. But creating separate indexes for every metadata combination creates operational explosion. Correctness-critical filters such as tenant, ACL, region, document status, and product version should be pushed into the retrieval path. Softer ranking signals such as recency, authority, and popularity can often be applied after candidate retrieval.

---

## Question 34

**How do HNSW, IVF, and product quantization trade recall, latency, and memory?**

### Sample Answer

HNSW often gives strong recall and low latency but uses more memory because it stores graph links. IVF partitions the vector space and searches selected clusters, reducing search work but making recall depend on partition quality and the number of clusters probed. Product quantization compresses vectors to reduce memory and bandwidth, but distance estimates become less precise. At large scale, index choice is a recall-latency-memory tradeoff, not a pure performance win.

---

## Question 35

**How does reranking become a scaling bottleneck?**

### Sample Answer

Rerankers score query-document pairs, often with a cross-encoder. If first-stage retrieval returns 200 candidates for 10,000 queries per minute, the reranker must score two million pairs per minute. That can dominate latency and cost. Scaling patterns include pruning before reranking, batching reranker calls, using small rerankers for easy cases, escalating to stronger rerankers only for hard queries, caching repeated scores, and limiting candidate counts by query difficulty.

---

## Question 36

**How would you keep a 100M-document retrieval index fresh?**

### Sample Answer

I would separate freshness requirements by data type. Permissions and deletions need strict handling; ranking signals and embeddings can often be eventually consistent. Architecturally, I might use batch rebuilds for stable corpora, incremental updates for normal document changes, a delta index for fresh documents, blue-green index swaps for safe rollout, or streaming ingestion for near-real-time systems. Every answer should record the index version so regressions and stale answers can be debugged.

---

## Question 37

**What are hot shards, and how do you handle them?**

### Sample Answer

Hot shards happen when load is uneven: one tenant, region, topic, or document receives much more traffic than others. Average QPS can look fine while one shard melts. Mitigations include splitting large tenants, replicating hot shards, caching hot query results, load-aware routing, isolating heavy tenants, and rebalancing based on query load rather than storage size alone.

---

## Question 38

**What should you monitor in a retrieval system at very large scale?**

### Sample Answer

Monitor aggregate and per-shard query latency, recall on eval queries, empty-result rate, candidate counts, reranker latency, cache hit rate, index freshness, ingestion lag, permission-filter behavior, hot shard load, memory usage, replica health, index version, and citation support. Per-shard metrics matter because distributed retrieval failures often hide behind healthy averages.

---

## Question 39

**How would you retrieve relevant resumes from 2 million inconsistently structured resumes?**

### Sample Answer

I would not assume resumes have reliable structure. I would store each raw resume and parsed text as a parent document, then create many searchable evidence chunks linked by `resume_id`. If section structure is semi-reliable, I would create section-aware chunks for skills, experience, projects, education, and certifications. If structure is unreliable, I would use overlapping token windows and maybe multiple granularities, preserving source offsets and parser quality flags.

At query time, I would use the job description to run hybrid retrieval over chunks: dense retrieval for semantic fit and sparse retrieval for exact skills, tools, companies, credentials, and acronyms. Then I would group chunk hits by `resume_id`, aggregate evidence across chunks, pull neighboring context where useful, and rerank candidate resumes using the job description plus supporting snippets. The system should return resumes or candidates, not isolated chunks.

Structured fields such as years of experience, seniority, skills, and education should be treated as soft signals unless extraction confidence is high. Hard filters should be reserved for reliable metadata such as permissions, tenant, or trusted availability/location fields. The main tradeoff is recall versus precision: relying too much on structure can miss good candidates, while broad chunk retrieval needs aggregation and reranking to avoid noisy matches.
