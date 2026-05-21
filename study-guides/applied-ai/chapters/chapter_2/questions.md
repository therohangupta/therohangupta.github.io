---
layout: page
title: "Retrieval and Memory Systems Practice Questions"
guide_type: questions
---
# Chapter 2 — Practice Questions

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
