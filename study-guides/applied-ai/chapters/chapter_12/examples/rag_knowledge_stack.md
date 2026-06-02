# RAG / Knowledge System Stack

Knowledge systems organize external information so models can use it.

## Pipeline

```text
source documents
  -> ingestion
  -> parsing
  -> chunking
  -> metadata extraction
  -> embeddings
  -> dense and sparse indexes
  -> retrieval
  -> reranking
  -> context builder
  -> model answer
  -> citation validation
  -> evals and feedback
```

## Ingestion

Sources:

- docs,
- PDFs,
- tickets,
- wikis,
- code,
- Slack/chat,
- databases,
- web pages.

Important metadata:

- source ID,
- tenant,
- permissions,
- owner,
- timestamp,
- version,
- document type,
- heading path.

## Indexing

Dense retrieval:

- FAISS,
- pgvector,
- Pinecone,
- Weaviate,
- Milvus.

Sparse retrieval:

- Elasticsearch,
- OpenSearch,
- BM25-style systems.

Hybrid retrieval often works better than either alone.

## Reranking

First-stage retrieval optimizes recall.

Reranking improves precision:

```text
top 100 candidates -> reranker -> top 5 context chunks
```

Tradeoff:

- better relevance,
- higher latency and cost.

## Context Building

The context builder decides what the model sees.

It should handle:

- permissions,
- freshness,
- deduplication,
- source diversity,
- citation IDs,
- token budget,
- instruction/data separation.

## Evaluation

Measure:

- recall at k,
- precision at k,
- answer groundedness,
- citation support,
- unsupported claim rate,
- latency,
- cost,
- failure by query type.

## Failure Modes

- Bad chunking loses context.
- Embedding model changes without reindexing.
- Metadata filters leak permissions.
- Sparse search misses paraphrases.
- Dense search misses exact IDs.
- Reranker adds too much latency.
- Retrieved context is stale.
- Model cites sources that do not support the claim.

## Interview Framing

> I would design a knowledge system as ingestion, indexing, retrieval, reranking, context construction, generation, and evaluation. The hard parts are permissions, freshness, chunking, ranking, citation support, and measuring retrieval separately from generation.

