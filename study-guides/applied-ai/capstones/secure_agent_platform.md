---
layout: page
title: "Capstone: Secure Agent Platform"
guide_type: capstone
---
# Capstone: Secure Agent Platform

Design a platform where teams can build AI agents that use shared models, tools, memory, retrieval, evals, and deployment controls.

---

## 1. Problem Statement

Multiple teams want agents for support, sales, operations, engineering, and internal workflows. The platform should let teams move quickly while enforcing common security, observability, evaluation, and rollout standards.

Clarifying questions:

* Are agents internal-only, customer-facing, or both?
* Who can publish tools, prompts, and agent configs?
* What actions require human approval?
* Is the platform single-tenant, multi-tenant, or workspace-scoped?

---

## 2. Success Criteria

Good means:

* teams can configure agents without rebuilding infrastructure,
* tools have explicit permissions and risk classes,
* tenant and workspace isolation are enforced,
* every agent action is traceable,
* releases are gated by evals,
* incidents can be contained by disabling tools, prompts, models, or agents.

---

## 3. Requirements

Platform requirements:

* agent registry,
* tool registry,
* prompt and model registry,
* memory and retrieval services,
* policy engine,
* approval workflow,
* trace and audit logs,
* eval and rollout infrastructure.

Security requirements:

* least-privilege tool credentials,
* tenant isolation,
* sandboxing for execution tools,
* human approval for high-risk actions,
* prompt-injection and tool-output-injection defenses,
* secrets isolation.

Operational requirements:

* per-agent metrics,
* cost controls,
* rate limits,
* kill switches,
* rollback,
* incident review.

---

## 4. Architecture

```text
agent builder UI
  -> agent registry
  -> policy engine
  -> model gateway
  -> prompt registry
  -> retrieval and memory services
  -> tool registry
  -> approval service
  -> trace and audit pipeline
  -> eval and rollout system
```

Each agent is configuration over shared primitives:

```text
agent = model + prompt + tools + memory scope + retrieval scope + policies + eval suite
```

---

## 5. Request Flow

```text
user invokes agent
  -> authenticate user and tenant
  -> load agent config and policy
  -> retrieve scoped memory and documents
  -> model proposes next step
  -> tool call is authorized by policy engine
  -> high-risk action goes to approval
  -> result returns to agent loop
  -> trace and audit events are written
```

---

## 6. Key Design Decisions

### Central tool registry

Tools should not be hidden inside prompts. The platform should know each tool's schema, owner, credentials, risk class, permissions, rate limits, and approval requirements.

### Policy outside the model

The model chooses candidate actions. The policy engine enforces what is allowed.

### Agent configs are versioned artifacts

Agent behavior depends on model, prompt, tools, memory, retrieval, and policy. Version the whole configuration so releases and incidents are reproducible.

### Shared eval infrastructure

Every agent should have an eval suite for its task plus platform-wide security and regression evals.

---

## 7. Evaluation Plan

Platform evals:

* prompt injection,
* tool-output injection,
* unauthorized tool calls,
* tenant isolation,
* memory scope errors,
* approval workflow bypass,
* action idempotency,
* rollback behavior.

Agent-specific evals:

* task success,
* answer quality,
* tool success,
* escalation correctness,
* latency and cost,
* user satisfaction.

Release gates:

```text
agent config can ship only if:
  task eval passes
  platform security eval passes
  tool permissions are reviewed
  rollback path exists
  monitoring is configured
```

---

## 8. Failure Modes

| Failure | Symptom | Mitigation |
| ------- | ------- | ---------- |
| Hidden permission | prompt references undocumented tool power | central tool registry |
| Cross-agent leakage | one agent sees another team's memory | scoped memory and tenant isolation tests |
| Approval bypass | agent executes high-risk action directly | policy engine and tool enforcement |
| Tool-output injection | tool result tells model to call another tool | untrusted observation labels and policy validation |
| Cost runaway | agent loops or calls expensive tools repeatedly | budgets, stopping rules, rate limits |
| Bad rollout | new prompt breaks behavior | eval gates and config rollback |

---

## 9. Learning Loop

Platform traces can improve:

* tool descriptions,
* prompt templates,
* eval suites,
* routing policies,
* approval thresholds,
* training datasets.

But traces must be filtered by tenant policy, privacy rules, and contamination status before training or broad analysis.

---

## 10. Production Rollout

Roll out at multiple levels:

* tool-level rollout,
* prompt-level rollout,
* model-level rollout,
* agent-level rollout,
* tenant-level rollout.

Kill switches:

* disable one tool,
* force approval for a risk class,
* disable an agent,
* route to safer model,
* turn off memory writes,
* block a retrieval source.

---

## 11. Interview Answer

I would build a secure agent platform around shared registries and policy enforcement. Each agent is a versioned configuration of model, prompt, tools, memory, retrieval, policies, and evals. Tool permissions live in a central registry and are enforced outside the model. Retrieval and memory are scoped by tenant and user. High-risk actions require approval, and every model call, tool call, and approval is traced. Releases are gated by task evals and platform security evals, with rollback and kill switches for tools, prompts, models, and agents.
