---
layout: page
title: "Capstone: Production Feedback Learning Loop"
guide_type: capstone
---
# Capstone: Production Feedback Learning Loop

Design a system that turns production traces and feedback into safer model or product improvements.

---

## 1. Problem Statement

An AI product receives user feedback, tool outcomes, human edits, and production traces. The team wants to improve the model over time without training on private, noisy, biased, or contaminated data.

Clarifying questions:

* What feedback sources are available, and how trustworthy are they?
* Which data is allowed to be used for training?
* Which failures should become evals instead of training examples?
* How quickly does the product need to learn: daily, weekly, or release-by-release?

---

## 2. Success Criteria

Good means:

* feedback is logged with enough context to explain behavior,
* raw feedback is not treated as reward directly,
* private and contaminated traces are filtered,
* failures become eval cases,
* training datasets are versioned and reproducible,
* candidate updates pass broad regression and safety gates.

---

## 3. Requirements

Data requirements:

* trace IDs across prompts, retrieval, tools, model outputs, and feedback,
* model/prompt/tool/index versions,
* user and tenant policy metadata,
* privacy and retention labels,
* label source and labeler agreement.

Learning requirements:

* classify traces as eval, training, debugging, or excluded,
* support SFT examples, preference pairs, reward labels, and retrieval fixes,
* maintain train/eval split discipline,
* quarantine bad-policy traces.

Operational requirements:

* dataset versioning,
* lineage from trace to dataset to model,
* release gates,
* rollback and monitoring.

---

## 4. Architecture

```text
production system
  -> trace logger
  -> privacy and eligibility filter
  -> failure classifier
  -> labeling workflow
  -> dataset builder
  -> training or retrieval update
  -> eval gate
  -> canary rollout
  -> monitoring and quarantine
```

---

## 5. Data Flow

```text
model interaction
  -> trace with versions and context
  -> user feedback or outcome
  -> privacy filtering
  -> eligibility decision
  -> label or verification
  -> dataset version
  -> candidate update
  -> evals and rollout
```

The trace is not automatically training data. It is a candidate for a decision.

---

## 6. Key Design Decisions

### Feedback is not reward

A thumbs up, click, support edit, or task completion may reflect style, UI placement, user frustration, or missing context. Convert feedback into trusted signal through filtering, labeling, verification, or human review.

### Some failures should become evals, not training examples

If the model exposed private data or violated policy, the first move is a regression test and incident review. Training on the trace may spread the problem.

### Fix the right layer

Not every failure needs post-training:

| Failure | Likely Fix |
| ------- | ---------- |
| missing document | ingestion or retrieval |
| stale policy | source sync |
| bad format | prompt or SFT |
| preference tradeoff | DPO or reward modeling |
| tool misuse | policy engine or agent design |
| narrow customer style | LoRA or prompt |
| unsafe behavior | safety data, policy, eval gate |

---

## 7. Evaluation Plan

Before a candidate update ships, evaluate:

* target task improvement,
* broad regression,
* safety behavior,
* privacy leakage,
* tenant isolation,
* hallucination and grounding,
* style over substance,
* latency and cost,
* slices affected by the training data.

Keep eval sets separate from training data. If an incident creates new eval cases, protect those cases from later training leakage.

---

## 8. Failure Modes

| Failure | Symptom | Mitigation |
| ------- | ------- | ---------- |
| Raw feedback overfit | model optimizes for thumbs up but gets less correct | label calibration and outcome checks |
| Privacy leakage | private text enters dataset | PII filter and training eligibility gate |
| Contaminated traces | bad policy teaches future model | quarantine affected versions |
| Eval contamination | training data includes held-out tests | lineage and split enforcement |
| Narrow improvement | one slice improves, others regress | broad and sliced evals |
| Model-generated data loop | synthetic errors amplify | provenance and external validation |

---

## 9. Learning Loop

Candidate update options:

* retrieval index update,
* prompt or policy change,
* SFT on high-quality demonstrations,
* DPO on preference pairs,
* LoRA for narrow behavior,
* RL or reward optimization when reward is trustworthy,
* no model update if product logic is the right fix.

The loop:

```text
observe
  -> filter
  -> label or verify
  -> choose update type
  -> train candidate
  -> evaluate
  -> canary
  -> monitor
  -> keep or roll back
```

---

## 10. Production Rollout

Roll out model updates like software releases:

* immutable artifact versions,
* release owner,
* offline eval report,
* safety and privacy signoff for risky changes,
* canary metrics,
* rollback path,
* post-launch monitoring.

If a bad update ships, stop further training data ingestion from the affected policy until traces are reviewed.

---

## 11. Interview Answer

I would not train directly on raw production feedback. I would log full trajectories with versions, filter for privacy and eligibility, classify traces as eval or training candidates, label or verify them, and choose the right improvement path: retrieval fix, prompt change, SFT, DPO, LoRA, or RL. Every dataset and candidate model would be versioned, evaluated on target and regression suites, canaried, monitored, and rollback-ready. Contaminated traces from bad policies would be quarantined.
