---
layout: page
title: "Applied AI Study Guide"
guide_type: overview
---
# Study guide overview

This is a compositional map: topics build upward into the kind of systems companies likely care about—not a flat topic list.

## Table of contents

1. [Study guide map (four layers)](#1-study-guide-map-four-layers)
2. [Chapter 0: Foundations and LLM fundamentals](#2-chapter-0-foundations-and-llm-fundamentals)
3. [Chapter 1: LLM engineering (making them useful)](#3-chapter-1-llm-engineering-making-them-useful)
4. [Chapter 2: Retrieval and memory systems](#4-chapter-2-retrieval-and-memory-systems)
5. [Chapter 3: Agents (core product layer)](#5-chapter-3-agents-core-product-layer)
6. [Chapter 4: Evaluation systems](#6-chapter-4-evaluation-systems)
7. [Chapter 5: Learning loops (RL and continual learning)](#7-chapter-5-learning-loops-rl-and-continual-learning)
8. [Chapter 6: Production ML systems](#8-chapter-6-production-ml-systems)
9. [Chapter 7: System design (top layer)](#9-chapter-7-system-design-top-layer)
10. [Chapter 8: Advanced and differentiation topics](#10-chapter-8-advanced-and-differentiation-topics)
11. [How everything connects](#11-how-everything-connects)
12. [Priority order (what to study first)](#12-priority-order-what-to-study-first)

---

## 1. Study guide map (four layers)

Read the guide bottom-up, toward full systems:

| Layer | Focus |
| ----- | ----- |
| **Layer 0** | Foundations (primitives) |
| **Layer 1** | ML + LLM building blocks |
| **Layer 2** | System components (agents, memory, retrieval) |
| **Layer 3** | Full production systems (design, scaling, learning loops) |

---

## 2. Chapter 0: Foundations and LLM fundamentals

[`chapters/chapter_0/guide.md`](chapters/chapter_0/guide.html)

### Part I — Foundations (atomic thinking layer)

Irreducible primitives everything else builds on:

- Probability and distributions (intuitive, not academic)
- Optimization: loss, gradients, convergence intuition
- Representations: embeddings as geometry
- Information flow: compression; signal vs noise
- Composition (RAG and agent examples tying the four primitives together)
- ML design primitives (representation, parameterization, objectives, constraints, credit assignment) and example decompositions (Transformer, PPO, diffusion)
- Practice questions and takeaways for this layer

**Why it matters:** Every LLM, RAG, and RL idea reduces to what is represented, what signal is optimized, and what information is preserved or lost.

### Part II — LLM fundamentals (core engine)

How decoder-style LLMs are built, trained, and served:

- **Core stack:** tokens, embeddings, positional handling, self-attention, FFN blocks, residuals, normalization
- **Why transformers won:** parallelism, long-range dependencies, scalable depth
- **Architecture progression:** stable blocks (pre-norm, RMSNorm, RoPE, SwiGLU), MHA / MQA / GQA, sparse and sliding-window attention, MoE, FlashAttention and paged KV
- **Training pipeline:** pretraining → SFT → preference / RL alignment
- **Inference and cost:** prefill vs decode, KV cache, memory bandwidth, how each design choice hits latency and throughput
- **Interview framing:** tradeoff cheat sheet, “what to say,” practice questions, takeaways

---

## 3. Chapter 1: LLM engineering (making them useful)

### What this chapter covers

**Primitives**

- Prompting; temperature and sampling; context construction; tool calling; structured outputs

**Composition**

- Prompt pipelines; tool-augmented LLMs; mixing deterministic and stochastic control

**Outcomes**

- Real workflows; controlled behavior; more reliable outputs

---

## 4. Chapter 2: Retrieval and memory systems

### What this chapter covers

**Primitives**

- Embeddings as vectors; similarity search; chunking; indexing; metadata filtering

**Composition**

- RAG pipelines; long-term memory; context management systems

**Extensions**

- Episodic vs semantic memory; summarization; memory compression; forgetting strategies

---

## 5. Chapter 3: Agents (core product layer)

Where the stack starts to look like what they build.

### What this chapter covers

**Primitives**

- State; actions (tools); observations; the loop (control / robotics framing)

**Composition**

- Agent loop; planner + executor; reflection and self-correction; multi-agent systems

**Key idea**

Agents = LLM + tools + memory + loop.

---

## 6. Chapter 4: Evaluation systems

Most candidates skip this; startups at this stage usually do not.

### What this chapter covers

**Primitives**

- Metrics; ground truth; signal vs noise; distributions of outcomes

**Composition**

- Offline and online evals; regression testing; adversarial testing; synthetic eval generation

**Key idea**

If you cannot measure it, you cannot improve it.

---

## 7. Chapter 5: Learning loops (RL and continual learning)

### What this chapter covers

**Primitives**

- Reward; policy; feedback; exploration vs exploitation

**Composition**

- SFT (supervised fine-tuning); RLHF; DPO; online learning systems; continual learning pipelines

**Key idea**

Turn real-world usage into model improvement.

---

## 8. Chapter 6: Production ML systems

### What this chapter covers

**Primitives**

- Latency; throughput; cost; failure modes

**Composition**

- Inference services; batching and caching; async pipelines; distributed workers; observability

**Key idea**

Making things work reliably at scale.

---

## 9. Chapter 7: System design (top layer)

Final composition: combine prior chapters into full systems.

### What this chapter covers

**Example systems**

- Enterprise AI agent platform; coding assistant; customer support automation; research copilots; workflow automation agents

**What you will reason about**

- Architecture; tradeoffs; scaling; safety; iteration loops

---

## 10. Chapter 8: Advanced and differentiation topics

Signal boosters for strong candidates.

### What this chapter covers

- Synthetic data generation
- Simulation environments
- Reasoning models (chain-of-thought, verifiers)
- Test-time compute
- Mechanistic interpretability (light touch)
- GPU and system-level optimization intuition

---

## 11. How everything connects

**Compositional chain**

- Embeddings → retrieval → memory
- LLM → reasoning → tool use
- Memory + tools + loop → agent
- Agent + feedback → learning loop (RL)
- Everything + infra → production system

**Compact form**

LLM + retrieval + memory + tools + loop + feedback + infra = applied AI system—the kind of system Applied Compute is building.

---

## 12. Priority order (what to study first)

If you are time-constrained:

| Tier | Priority | Topics |
| ---- | -------- | ------ |
| **1 — Must master** | Highest | Chapter 0; LLM engineering (prompting, tools); retrieval + memory; agents; evaluation |
| **2 — Very important** | High | Learning loops (RLHF, continual learning); production systems |
| **3 — Nice to have** | Lower | Advanced topics (Chapter 8) |
