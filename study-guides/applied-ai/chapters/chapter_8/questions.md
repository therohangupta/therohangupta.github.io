---
layout: page
title: "Chapter 8 Questions: Security, Privacy, and Trust Boundaries"
guide_type: questions
---

# Chapter 8 — Practice Questions

Explanatory material for this chapter lives in [`guide.md`](guide.html).

---

# Common Interview Questions and Sample Answers

---

## Question 1

**What is the core security problem in AI systems?**

### Sample Answer

The core problem is that untrusted text can influence trusted computation. A model may read user messages, retrieved documents, webpages, emails, tool outputs, or memory entries that contain instructions. The system must separate trusted instructions from untrusted evidence and ensure model output does not become authorization.

---

## Question 2

**Why should the model not be the permission boundary?**

### Sample Answer

The model is probabilistic and can be manipulated by prompt injection, misleading context, or tool-output text. It can propose an action, but policy code should decide whether the authenticated user, tenant, role, resource, action, and risk level allow that action.

---

## Question 3

**How do you defend an agent against prompt injection from retrieved documents?**

### Sample Answer

Treat retrieved documents as untrusted evidence, not instructions. Enforce permissions before retrieval, label retrieved content as evidence, minimize context, prevent retrieved text from changing tool permissions or system policy, validate model outputs with policy code, and include adversarial prompt-injection cases in evals.

---

## Question 4

**What is indirect prompt injection?**

### Sample Answer

Indirect prompt injection occurs when adversarial instructions are hidden in content the user did not directly write, such as webpages, emails, tickets, PDFs, code comments, or retrieved documents. The model reads the content and may follow the attacker's instructions unless the system treats that content as untrusted.

---

## Question 5

**How do you design permission-aware retrieval for enterprise users?**

### Sample Answer

Identify the user, tenant, groups, and document permissions before retrieval. Filter candidate documents by ACL before ranking and context assembly. Store permission metadata at document or chunk level, sync deletions and permission changes from the source of truth, and test for cross-tenant leakage.

---

## Question 6

**Why should ACL filtering happen before ranking or generation?**

### Sample Answer

If unauthorized chunks are retrieved and ranked before filtering, private information can influence the model or appear in logs and traces even if the final answer is filtered. Access control must happen before the model sees the content.

---

## Question 7

**What is a confused deputy attack in an LLM agent?**

### Sample Answer

A confused deputy attack happens when an attacker uses untrusted text to trick a more-privileged component into acting with its authority. In an LLM agent, a malicious document might instruct the model to call an internal tool with system credentials. The fix is to authorize tool calls against the real user, tenant, resource, and action, not the model's interpretation.

---

## Question 8

**How do you prevent a model from exfiltrating secrets through tools?**

### Sample Answer

Do not expose secrets unless needed, run tools with least privilege, restrict outbound destinations, validate tool arguments, classify high-risk actions, require approval for sensitive transfers, redact logs, and monitor unusual tool-call patterns. The model should not have direct access to broad credentials.

---

## Question 9

**What should be in an audit log for a tool-using agent?**

### Sample Answer

An audit log should include trace ID, user, tenant, model version, prompt version, retrieved sources, tool name, tool arguments, authorization decision, policy version, human approver if any, result, timestamp, and error or rollback information.

---

## Question 10

**How should human approval work for high-risk agent actions?**

### Sample Answer

The approval should be for a specific proposed action, not a vague plan. The reviewer should see the user request, target resource, action, reason, evidence, risk class, model version, and rollback path. The approval system should be outside the model.

---

## Question 11

**How do you handle memory deletion and user opt-out?**

### Sample Answer

Track where memory-derived data may exist: memory store, vector index, embeddings, traces, logs, eval datasets, training datasets, and backups. Respect opt-out before writing memory, scope memories by user or tenant, and maintain lineage so deletion requests can remove or quarantine derived records.

---

## Question 12

**Why is data governance part of AI security?**

### Sample Answer

AI systems often turn logs, feedback, and traces into future training data. If private, low-quality, or contaminated traces enter training, a temporary exposure can become durable behavior. Training eligibility, PII redaction, consent, retention, and provenance are security controls.

---

## Question 13

**How do you quarantine contaminated traces from a bad policy or model release?**

### Sample Answer

Mark affected model and prompt versions, isolate traces from training pipelines, inspect whether labels are reliable, convert confirmed failures into eval cases, and only reintroduce examples after review. Quarantine prevents bad behavior from becoming training signal.

---

## Question 14

**What security evals should gate an AI system release?**

### Sample Answer

Run evals for direct and indirect prompt injection, unauthorized tool calls, tenant isolation, sensitive-data leakage, refusal correctness, dangerous action approval, jailbreak robustness, and memory deletion behavior. Security evals should gate release alongside quality, latency, and cost.

---

## Question 15

**How would you explain trusted vs untrusted context in an interview?**

### Sample Answer

Trusted context defines policy and authority, such as system instructions and tool contracts. Untrusted context is evidence, such as user text, retrieved documents, webpages, or tool outputs. The model can use untrusted context to answer questions, but it should not let untrusted context override policy or grant permissions.

---

## Question 16

**A tenant reports seeing another tenant's document in an AI answer. What do you do first?**

### Sample Answer

Treat it as a security incident. Identify the trace, model version, prompt version, retrieval query, retrieved chunks, cache keys, user and tenant IDs, and source document permissions. Disable or narrow affected retrieval paths if needed, check whether unauthorized content entered logs or training pipelines, notify according to policy, and add a regression eval for the leak.

---

## Question 17

**An agent executed a tool based on malicious retrieved text. What boundaries failed?**

### Sample Answer

Retrieved content was treated as authority instead of evidence, and tool authorization likely depended too much on model output. The fix is to label retrieved text as untrusted, prevent it from changing tool policy, validate actions outside the model, require approval for risky actions, and add prompt-injection evals.

---

## Question 18

**What is the difference between safety filtering and security design?**

### Sample Answer

Safety filtering catches some bad outputs, but security design controls authority and data flow before the output exists. A secure system enforces ACLs, least-privilege tools, context minimization, validation, audit logs, and release gates. Filtering is one layer, not the boundary.

---

## Question 19

**How can logs become a security risk in AI systems?**

### Sample Answer

AI logs often contain prompts, retrieved documents, tool outputs, model responses, user data, and traces. If raw logs are widely accessible or retained too long, they can leak sensitive data. Logs should be minimized, redacted, access-controlled, retained intentionally, and excluded from training unless eligible.

---

## Question 20

**What is a strong interview answer for securing an AI agent?**

### Sample Answer

I would separate trusted instructions, untrusted context, model outputs, privileged tools, and durable state. Retrieval would enforce ACLs before ranking. Tools would run with least privilege and validate action, resource, user, tenant, and risk outside the model. High-risk actions would require human approval. I would log actions with trace IDs, run adversarial security evals, monitor abuse, and keep rollback and trace quarantine ready.

---

## Question 21

**When is model routing a security decision, not only a cost or quality decision?**

### Sample Answer

Model routing is a security decision when prompts may contain private documents, regulated data, secrets, customer traces, or tenant-restricted context. Some data may be allowed only on self-hosted models or providers with specific retention and logging guarantees. The router should consider data classification, tenant policy, provider retention, model capability, and audit requirements, not only latency or price.

---

## Question 22

**How can supply chain risk show up in an AI system?**

### Sample Answer

Supply chain risk can come from poisoned retrieval documents, unreviewed prompt changes, tool descriptions that request broader authority, wrong model or adapter artifacts, package updates that affect sanitization, or embedding-model changes that alter retrieval. I would version and review models, prompts, tools, datasets, indexes, and dependencies; track provenance; run evals after upgrades; and keep rollback paths.

---
