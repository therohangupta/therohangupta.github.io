---
layout: page
title: "Capstone: Eval-to-Rollout Pipeline"
guide_type: capstone
---
# Capstone: Eval-to-Rollout Pipeline

Design the pipeline that decides whether a new model, prompt, retriever, tool policy, or agent workflow should ship.

---

## 1. Problem Statement

The team is changing an AI system. The change improves some internal metric, but production risk is uncertain. The pipeline must produce enough evidence to ship, block, canary, or roll back.

Clarifying questions:

* What artifact changed: model, prompt, retriever, tool policy, or agent workflow?
* What is the highest-cost failure if the candidate is bad?
* Which slices are safety-critical or business-critical?
* Is this a user-facing release, shadow test, or internal-only change?

---

## 2. Success Criteria

Good means:

* release decisions are based on sliced evidence, not one average score,
* regressions are caught before broad rollout,
* human review is used where automated scores are weak,
* uncertainty is visible,
* canaries have rollback criteria,
* incidents become future evals.

---

## 3. Requirements

Functional requirements:

* compare candidate against baseline,
* run offline evals,
* run security and safety evals,
* slice metrics by task, user cohort, risk class, and data source,
* produce a release recommendation,
* monitor canary behavior.

Statistical requirements:

* show confidence intervals or bootstrap ranges where possible,
* avoid overreacting to tiny samples,
* require minimum counts for high-risk slices,
* escalate ambiguous changes to human review.

Operational requirements:

* version models, prompts, datasets, judges, tools, and configs,
* record release decisions,
* support rollback.

---

## 4. Architecture

```text
candidate artifact
  -> offline eval runner
  -> judge and validator layer
  -> human review sampler
  -> slice analyzer
  -> release report
  -> canary controller
  -> production monitors
  -> rollback and incident workflow
```

Artifacts include:

* baseline model/prompt/retriever version,
* candidate version,
* eval dataset version,
* judge prompt/model version,
* scoring code version,
* release decision.

---

## 5. Request/Data Flow

```text
engineer proposes candidate
  -> registry records artifact versions
  -> eval runner executes fixed and fresh evals
  -> metrics are sliced and compared to baseline
  -> uncertain or high-risk cases go to human review
  -> report recommends ship, block, or canary
  -> canary monitors guardrails
  -> rollout expands or rolls back
```

---

## 6. Key Design Decisions

### Slices matter more than averages

An average can improve while a critical slice regresses. Always inspect high-risk categories, rare intents, tenants, languages, document types, and safety cases.

### Judges need calibration

LLM judges can be useful, but they should be checked against human labels. Track where the judge is biased, noisy, or insensitive.

### Confidence is part of the report

For stochastic systems, one measured score is not enough. Report uncertainty ranges, sample counts, and whether the effect is large enough to matter.

### Canary with guardrails

Canaries should monitor both target metrics and guardrails:

* quality,
* latency,
* cost,
* safety,
* escalation,
* tenant leakage,
* tool errors.

---

## 7. Evaluation Plan

Offline report sections:

| Section | Content |
| ------- | ------- |
| Summary | ship/block/canary recommendation |
| Candidate | model, prompt, retriever, policy, config versions |
| Aggregate metrics | baseline vs candidate |
| Slice metrics | high-risk and high-volume breakdowns |
| Uncertainty | confidence intervals, bootstrap ranges, sample counts |
| Representative failures | examples with traces |
| Human review | label counts, disagreements, notes |
| Security checks | injection, leakage, unauthorized tools |
| Cost/latency | p50/p95, token usage, throughput |
| Decision | owner, date, rollback plan |

---

## 8. Failure Modes

| Failure | Symptom | Mitigation |
| ------- | ------- | ---------- |
| Metric gaming | score improves but users suffer | multi-metric scorecard and human review |
| Slice regression | average improves, rare cases fail | required slice gates |
| Judge drift | judge prefers candidate style | judge calibration and fixed anchor set |
| Eval leakage | candidate trained on eval cases | dataset lineage and holdout discipline |
| Canary harm | rollout hurts users | narrow rollout, guardrails, rollback |
| Missing ownership | bad release lingers | explicit owner and incident workflow |

---

## 9. Learning Loop

Every blocked or failed release should improve the eval system:

```text
failed candidate
  -> inspect traces
  -> classify failure
  -> add regression cases
  -> update slices or metrics
  -> fix model/retriever/prompt/tool policy
  -> rerun evals
```

Do not only fix the candidate. Fix the gate that missed or caught the issue.

---

## 10. Production Rollout

Rollout stages:

1. offline eval pass,
2. shadow traffic,
3. internal users,
4. small canary,
5. expanded canary,
6. full rollout.

Rollback triggers:

* critical safety failure,
* tenant leakage,
* unauthorized tool execution,
* statistically meaningful quality regression,
* p95 latency or cost budget breach,
* spike in escalations or user complaints.

---

## 11. Interview Answer

I would treat model release as a production change with evidence. The pipeline compares candidate and baseline on fixed and fresh evals, slices metrics by task and risk, shows uncertainty and sample counts, calibrates model judges against human labels, and gates on safety, security, latency, cost, and quality. If the candidate passes, it goes through shadow or canary rollout with guardrail metrics and rollback criteria. Failed rollouts become regression cases so the eval system improves over time.
