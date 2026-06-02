---
layout: page
title: "Capstone: Durable Workflow Automation Agent"
guide_type: capstone
---

# Capstone: Durable Workflow Automation Agent

## Problem

Design an agent that executes long-running business workflows with retries, approvals, idempotency, compensation, and auditability.

## Success Criteria

* workflows resume after failures,
* risky actions require approval,
* retries do not duplicate side effects,
* state is inspectable,
* every external action is auditable.


## Requirements

Functional requirements:

* represent workflow state durably,
* support retries, timers, cancellation, and compensation,
* enforce approvals before high-risk side effects,
* make tool calls idempotent,
* expose workflow history for debugging and audit.

Operational requirements:

* recover after worker crashes,
* avoid duplicate external actions,
* isolate tenant data and credentials,
* provide replay or simulation for failed workflows,
* support versioned workflow definitions.

## Architecture

```text
request -> workflow engine -> state store -> planner -> tool executor -> approval service -> audit log -> completion
```

## Key Design Decisions

### Durable workflow over free-form loop

The model can interpret context and propose next steps, but a workflow engine owns state transitions, retries, timers, and compensation.

### Idempotent tools

Every side-effecting tool call should use idempotency keys and record external action IDs.

## Evaluation Plan

Test happy paths, interrupted workflows, duplicate retry prevention, approval routing, timeout handling, and compensation logic.

## Failure Modes

| Failure | Mitigation |
| ------- | ---------- |
| duplicate external action | idempotency keys |
| workflow lost after crash | durable state store |
| model skips approval | policy gate outside model |
| infinite loop | step and time budgets |

## Learning Loop

Workflow failures become state-machine tests and trajectory evals. High-risk traces are reviewed before they enter training or prompt improvement.


## Rollout Plan

1. Start with internal or low-risk traffic.
2. Run shadow or review-only mode before autonomous behavior.
3. Canary by tenant, workflow, or document type.
4. Monitor quality, latency, cost, safety, and escalation metrics.
5. Keep rollback available for prompts, models, tools, policies, and routing.

## Interview Answer

I would not run the whole process inside one agent prompt. I would use a durable workflow engine with explicit state, checkpoints, retries, idempotency, and approval states, with the model making bounded decisions inside that system.
