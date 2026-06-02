---
layout: page
title: "Applied AI Study Guide"
guide_type: overview
---
# Applied AI Study Guide

This guide is a complete learning path for applied AI and ML systems work. The chapters are ordered to build from primitives, to LLM components, to retrieval and agents, to evaluation and learning, to production/security/system design, and finally to software, platform, and ML systems depth.

Every chapter has a comprehensive `guide.md`, `questions.md`, `examples.md`, and `examples/` directory.

---

## Table of Contents

1. [Study Guide Map](#1-study-guide-map)
2. [Chapter Overview](#2-chapter-overview)
3. [How Everything Connects](#3-how-everything-connects)
4. [Capstone Scenarios](#4-capstone-scenarios)
5. [Learning Paths](#5-learning-paths)
6. [How to Study a Chapter](#6-how-to-study-a-chapter)

---

## 1. Study Guide Map

| Layer | Chapters | Focus |
| ----- | -------- | ----- |
| Foundations | 0-1 | ML primitives and LLM architecture |
| Product Components | 2-4 | LLM engineering, retrieval/memory, agents |
| Measurement and Improvement | 5-6 | Evaluation systems and learning loops |
| Production and Composition | 7-10 | Serving, security, system design, advanced AI techniques |
| Engineering Depth | 11-13 | Software fundamentals, platform stack, ML systems/inference engineering |
| Capstones | Capstone scenarios | Full-system interview practice |

---

## 2. Chapter Overview

### Chapter 0: ML Foundations

[`chapters/chapter_0/guide.md`](chapters/chapter_0/guide.html)  
Owns probability, optimization, embeddings, information flow, objectives, constraints, and the primitives that all later chapters reuse.

### Chapter 1: LLM Architecture and Inference Fundamentals

[`chapters/chapter_1/guide.md`](chapters/chapter_1/guide.html)  
Owns tokens, embeddings, transformer blocks, attention, MHA/MQA/GQA/MLA, MoE, prefill/decode basics, KV cache, and architecture/cost tradeoffs.

### Chapter 2: LLM Engineering

[`chapters/chapter_2/guide.md`](chapters/chapter_2/guide.html)  
Owns prompting, structured outputs, tool calling, context construction, orchestration, retries, fallbacks, and runtime control.

### Chapter 3: Retrieval and Memory Systems

[`chapters/chapter_3/guide.md`](chapters/chapter_3/guide.html)  
Owns RAG, chunking, embeddings, hybrid search, reranking, citations, memory, indexing, sharding, freshness, and retrieval observability.

### Chapter 4: Agents

[`chapters/chapter_4/guide.md`](chapters/chapter_4/guide.html)  
Owns state, actions, observations, loops, planners, executors, workflow graphs, budgets, approval, sandboxing, and agent failure modes.

### Chapter 5: Evaluation Systems

[`chapters/chapter_5/guide.md`](chapters/chapter_5/guide.html)  
Owns metrics, golden sets, judge models, human review, uncertainty, slicing, regression tests, online experiments, canaries, and release gates.

### Chapter 6: Learning Loops

[`chapters/chapter_6/guide.md`](chapters/chapter_6/guide.html)  
Owns SFT, DPO, RLHF, PEFT, distillation, feedback systems, data eligibility, update gates, lineage, quarantine, canaries, and rollback.

### Chapter 7: Production ML Systems

[`chapters/chapter_7/guide.md`](chapters/chapter_7/guide.html)  
Owns serving architecture, queues, caches, routing, deployment, monitoring, incident response, reliability, latency, throughput, and cost.

### Chapter 8: Security, Privacy, and Trust Boundaries

[`chapters/chapter_8/guide.md`](chapters/chapter_8/guide.html)  
Owns prompt injection, trusted/untrusted context, ACL-aware retrieval, tool authorization, audit logs, PII, model-provider boundaries, supply-chain risk, and incident response.

### Chapter 9: AI System Design

[`chapters/chapter_9/guide.md`](chapters/chapter_9/guide.html)  
Owns full-system design templates that compose LLMs, retrieval, agents, evals, learning, production, security, rollout, and failure containment.

### Chapter 10: Advanced AI Techniques

[`chapters/chapter_10/guide.md`](chapters/chapter_10/guide.html)  
Owns synthetic data, simulation, verifiers, reasoning/search, test-time compute, interpretability, advanced distillation, and frontier-style tradeoffs.

### Chapter 11: Software Engineering Fundamentals for AI Systems

[`chapters/chapter_11/guide.md`](chapters/chapter_11/guide.html)  
Owns Python runtime behavior, async, multiprocessing, APIs, queues, SQL, data pipelines, backend service design, reliability, and ordinary software failure modes.

### Chapter 12: AI Platform and Infrastructure Stack

[`chapters/chapter_12/guide.md`](chapters/chapter_12/guide.html)  
Owns PyTorch/JAX/TensorFlow mental models, distributed training libraries, serving stacks, Ray, Kubernetes, data/retrieval/eval stacks, registries, artifact lineage, and observability platforms.

### Chapter 13: ML Systems and Inference Engineering

[`chapters/chapter_13/guide.md`](chapters/chapter_13/guide.html)  
Owns GPU execution, CUDA/PyTorch runtime behavior, compiler/runtime optimization, LLM inference internals, distributed serving/training, capacity planning, and debugging playbooks.

---

## 3. How Everything Connects

```text
ML primitives
  -> LLM architecture
  -> prompting / tools / context control
  -> retrieval + memory
  -> agents
  -> evaluation
  -> learning loops
  -> production serving
  -> security boundaries
  -> full system design
  -> advanced AI levers
  -> software fundamentals
  -> platform stack
  -> ML systems and inference engineering
  -> capstones
```

Compact form:

```text
LLM + retrieval + memory + tools + loop + evals + feedback + security + serving + software + platform + ML systems = applied AI system
```

---

## 4. Capstone Scenarios

[`capstones/overview.md`](capstones/overview.html)

Capstones are full-system drills. They train you to compose the chapters under realistic constraints: security, latency, cost, evals, rollout, learning loops, software systems, and inference capacity.

---

## 5. Learning Paths

[`learning_paths.md`](learning_paths.html)

The learning paths page gives sequencing for AI product engineering, agent platforms, AI infrastructure, post-training systems, security-focused work, and interview sprints. These are study orders, not optional tracks.

---

## 6. How to Study a Chapter

1. Read `guide.md` for the mental model.
2. Answer `questions.md` aloud.
3. Inspect or run the examples from `examples.md`.
4. Connect the chapter to at least one capstone.
5. Revisit earlier chapters when a later chapter reuses their primitives.
