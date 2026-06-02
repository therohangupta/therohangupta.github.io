---
layout: page
title: "Capstone: Secure Enterprise RAG Support Agent"
guide_type: capstone
---
# Capstone: Secure Enterprise RAG Support Agent

Design a support agent that answers customer questions using internal knowledge, account data, and support tools while preserving tenant isolation, grounding, auditability, and safe action execution.

---

## 1. Problem Statement

The company wants an AI support agent for enterprise customers. The agent should answer policy and product questions, draft support replies, inspect account state, and propose actions such as refunds or plan changes.

The system must be helpful without leaking data, inventing policy, or taking unauthorized actions.

Clarifying questions:

* Is the agent customer-facing, support-agent-facing, or both?
* Which actions can mutate customer state?
* What data is tenant-restricted or regulated?
* What latency target matters: first draft, final answer, or background resolution?

---

## 2. Success Criteria

Good means:

* answers are grounded in allowed sources,
* support agents resolve tickets faster,
* high-risk actions require approval,
* tenant data never leaks across boundaries,
* stale or deleted documents do not drive answers,
* failures become evals and training candidates,
* operators can trace why an answer or action happened.

---

## 3. Requirements

Functional requirements:

* retrieve support docs, policy docs, and customer-specific account context,
* answer with citations,
* draft replies for human review,
* call read-only tools for account and ticket state,
* propose high-risk actions but require approval before execution.

Latency and cost requirements:

* stream first tokens quickly for normal questions,
* use cheaper models for simple FAQ cases,
* reserve stronger models for complex or high-risk tickets,
* cache stable policy retrieval where safe.

Security and privacy requirements:

* enforce tenant and document ACLs before retrieval,
* treat tickets and retrieved docs as untrusted evidence,
* prevent retrieved text from authorizing tools,
* redact sensitive logs,
* keep audit records for actions and approvals.

Reliability requirements:

* fail closed on permission uncertainty,
* escalate low-confidence or high-risk cases,
* support rollback of prompts, models, retrieval indexes, and tool permissions.

---

## 4. Architecture

```text
support UI
  -> request router
  -> auth and tenant context
  -> policy-aware retriever
  -> context builder
  -> model gateway
  -> answer validator
  -> tool policy engine
  -> support tools / approval queue
  -> trace, metrics, audit logs
```

Key stores:

* document store with source-of-truth permissions,
* vector and keyword indexes with ACL metadata,
* ticket and account databases,
* prompt/model registry,
* eval dataset store,
* trace and audit log store.

---

## 5. Request Flow

```text
agent opens ticket
  -> system authenticates agent and tenant
  -> query is rewritten for retrieval
  -> retriever filters by ACL before ranking
  -> model receives user request plus allowed evidence
  -> model drafts answer with citations
  -> validator checks grounding, policy, and schema
  -> risky proposed action goes to policy engine
  -> approval queue handles refund or plan change
  -> trace and audit log record sources and decisions
```

The model can propose. The policy engine authorizes.

---

## 6. Key Design Decisions

### RAG before fine-tuning for policy knowledge

Policies, pricing, and account rules change. RAG keeps source material fresh and auditable. Fine-tuning may help tone or workflow behavior later, but it should not be the primary store of policy truth.

### ACL filtering before ranking

Do not retrieve globally and ask the model to ignore unauthorized chunks. Unauthorized content should not enter the prompt, ranking features, cache, trace, or answer.

### Draft-and-approve for risky actions

The agent may draft a refund explanation or propose a plan change. Execution requires a policy decision and, above a risk threshold, human approval.

### Separate answer quality from action authorization

An answer can be fluent and grounded while a proposed action is still unauthorized. These are different gates.

---

## 7. Evaluation Plan

Offline evals:

* retrieval recall on known policy questions,
* citation faithfulness,
* answer correctness,
* refusal correctness,
* tenant isolation tests,
* prompt-injection tests inside retrieved docs and tickets,
* tool-call authorization tests,
* regression tests for critical policies.

Human review:

* sample ambiguous answers,
* compare drafts to final human-edited replies,
* label missing evidence, wrong policy, bad tone, and unsafe action proposals.

Online metrics:

* ticket resolution time,
* reopen rate,
* escalation rate,
* customer satisfaction,
* citation failure rate,
* approval rejection rate,
* p95 latency and cost per resolved ticket.

Release gate:

```text
ship only if target quality improves
and tenant isolation has zero known failures
and high-risk tool authorization has zero known bypasses
and latency/cost stay within budget
```

---

## 8. Failure Modes

| Failure | Symptom | Mitigation |
| ------- | ------- | ---------- |
| Cross-tenant retrieval | answer cites another customer's document | ACL-before-ranking tests, tenant-scoped caches |
| Stale policy | agent gives outdated refund rule | source freshness checks, doc lineage, policy evals |
| Prompt injection | malicious ticket text changes behavior | untrusted context labels, tool policy outside model |
| Unsupported answer | citation does not support claim | grounding checker and human review sampling |
| Unsafe action | model triggers refund incorrectly | tool authorization and approval queue |
| Feedback contamination | bad answers become training data | trace quarantine and training eligibility gates |

---

## 9. Learning Loop

Failures become improvement data:

```text
ticket trace
  -> failure label
  -> eval case or training candidate
  -> privacy and eligibility filter
  -> dataset version
  -> candidate update
  -> offline evals
  -> canary
  -> rollout or rollback
```

Use:

* eval cases for policy regressions and tenant isolation,
* SFT examples for stable reply formats,
* DPO/preference pairs for better answer tradeoffs,
* LoRA for narrow support behavior if the base model is already capable,
* retrieval fixes when the problem is missing or stale evidence.

Do not train directly on raw customer feedback or raw ticket text.

---

## 10. Production Rollout

Roll out by risk:

1. shadow mode on historical tickets,
2. draft-only mode for support agents,
3. limited tenant canary,
4. read-only tool access,
5. approved write actions,
6. broader rollout after eval and monitoring gates.

Rollback levers:

* disable tool class,
* revert prompt version,
* route to previous model,
* roll back retrieval index,
* remove bad documents,
* quarantine traces from affected versions.

---

## 11. Interview Answer

I would design the support agent as a RAG and tool system with explicit trust boundaries. The request is authenticated into a tenant and role, retrieval filters by ACL before ranking, and the model sees only allowed evidence. The model drafts grounded answers with citations and may propose actions, but tool authorization happens outside the model using user, tenant, resource, action, and risk level. High-risk actions go to human approval. I would evaluate answer quality, retrieval recall, citation faithfulness, tenant isolation, prompt injection, and tool authorization before rollout. Production traces feed evals and carefully filtered training data, but raw feedback never updates the model directly.
