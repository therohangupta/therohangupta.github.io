# LLM Latency Incident Walkthrough

Scenario: p95 time to first token doubled after a release.

## Symptom

| Metric | Before | After |
| ------ | ------ | ----- |
| p50 time to first token | 420 ms | 610 ms |
| p95 time to first token | 1.2 s | 2.7 s |
| p95 time to final token | 5.8 s | 7.1 s |
| Input tokens p95 | 3.2k | 8.9k |
| Queue time p95 | 180 ms | 920 ms |

## Recent Change

The release added more retrieved context and a second reranker call for complex tickets.

## Debug Breakdown

```text
request
  -> routing
  -> retrieval
  -> reranking
  -> prompt construction
  -> queueing
  -> prefill
  -> decode
  -> streaming
```

## Findings

| Component | Finding |
| --------- | ------- |
| Retrieval | returns 20 chunks instead of 8 |
| Reranker | adds 300 ms on complex tickets |
| Prefill | longer prompts increase GPU work |
| Queueing | long-context requests reduce batch efficiency |
| Decode | mostly unchanged |

## Likely Fixes

* cap context by evidence value,
* route long-context requests to separate pool,
* reduce retrieved chunks after reranking,
* cache stable retrieval for repeated policy questions,
* stream earlier after prefill,
* add token-budget regression tests to release gate.

## Interview Framing

Do not debug LLM latency as one number. Split it into orchestration, retrieval, queueing, prefill, decode, and streaming. A long-context change often shows up as prefill and queueing pressure before it shows up as decode slowdown.
