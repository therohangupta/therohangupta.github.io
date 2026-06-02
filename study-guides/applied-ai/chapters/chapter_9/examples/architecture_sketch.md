---
layout: page
title: "Architecture Sketch"
guide_type: example
---
# Complete Architecture Sketch

This sketch shows the shape of a production AI agent platform. The same architecture can support a knowledge assistant, support automation product, coding assistant, or workflow agent with product-specific changes.

---

# 1. High-Level Architecture

```text
Client / Product UI
        |
        v
API Gateway
  - auth
  - rate limits
  - request IDs
  - tenant routing
        |
        v
Agent Orchestrator
  - loads agent config
  - classifies request
  - builds execution plan
  - manages request-local state
        |
        +--------------------+
        |                    |
        v                    v
Retrieval Service       Tool Registry
  - ACL filters          - schemas
  - hybrid search        - risk levels
  - reranking            - required scopes
  - citations            - owners
        |                    |
        v                    v
Context Builder         Policy Engine
  - token budget         - authorization
  - source ranking       - approval rules
  - prompt assembly      - safety checks
        |                    |
        +----------+---------+
                   |
                   v
              Model Gateway
              - routing
              - retries
              - model logs
              - token cost
                   |
                   v
          Validation / Action Gate
              - schema checks
              - citation checks
              - tool argument checks
              - escalation decisions
                   |
        +----------+----------+
        |                     |
        v                     v
User Response          Workflow Workers
  - streaming            - durable steps
  - citations            - tool execution
  - next actions         - retries
                        - idempotency
                              |
                              v
                      External Systems
                      - CRM
                      - ticketing
                      - docs
                      - email
                      - code host
```

Cross-cutting systems:

```text
Relational DB
  - users
  - tenants
  - permissions
  - workflow state
  - prompt versions
  - feedback

Vector DB / Search Index
  - document chunks
  - embeddings
  - metadata
  - ACL fields

Cache
  - feature flags
  - hot metadata
  - common retrieval results
  - rate limit counters

Event Queue
  - ingestion jobs
  - trace export
  - feedback processing
  - async workflow steps

Observability
  - logs
  - traces
  - metrics
  - dashboards
  - alerting

Evaluation Pipeline
  - golden test sets
  - regression tests
  - reviewer labels
  - rollout gates
```

---

# 2. Why Each Boundary Exists

## API Gateway

The gateway protects expensive downstream services. It handles authentication, rate limiting, tenant routing, request size limits, and request ID assignment.

## Agent Orchestrator

The orchestrator owns the application control flow. It decides whether a request is a simple answer, retrieval question, tool workflow, human-review case, or unsupported request.

This logic should not live only inside a prompt. If it does, you cannot reliably debug or enforce safety.

## Retrieval Service

Retrieval owns document access and evidence selection. It applies permissions before content reaches the model.

## Context Builder

The context builder turns candidates into a prompt. It enforces token budgets, source ordering, citation format, and instruction/data separation.

## Model Gateway

The model gateway centralizes model routing, provider failover, cost tracking, latency tracking, retry policy, and model-specific request formatting.

## Tool Registry and Policy Engine

The tool registry describes what can be called. The policy engine decides what may be called in the current user and workflow context.

Keeping these separate prevents a tool description from becoming an accidental permission model.

## Workflow Workers

Workers execute long-running and side-effecting tasks. They support retries, idempotency, checkpoints, and human approval.

## Evaluation Pipeline

The eval pipeline converts production traces and reviewer labels into release gates. It is the mechanism that stops silent regressions from becoming normal.

---

# 3. Failure Paths and Fallback Modes

## Retrieval Outage

If the retrieval service is down, the orchestrator should not silently answer from priors for grounded workflows.

Fallback options:

* answer only for low-risk general questions,
* tell the user the knowledge source is unavailable,
* route high-risk requests to human review,
* use a cached retrieval result only if freshness and ACL metadata are still valid.

Telemetry:

* `retrieval.error_rate`
* `retrieval.timeout_ms`
* `grounded_answer.fallback_count`

## Model Provider Outage

The model gateway owns provider failover and graceful degradation.

Fallback options:

* route to a smaller backup model,
* use a deterministic template for simple statuses,
* pause side-effecting workflows,
* queue long-running jobs until capacity returns.

Cost/latency tradeoff: keeping a backup route warm costs money, but cold failover increases tail latency during incidents.

## Tool Execution Failure

Workflow workers should use idempotency keys and checkpointed state so retries do not duplicate side effects.

Fallback options:

* retry only idempotent calls,
* require human approval after repeated failures,
* mark workflow state as `needs_attention`,
* expose a clear user-facing status instead of pretending success.

---

# 4. Minimal Data Model

```text
users
  id
  tenant_id
  role
  groups

agents
  id
  owner_team
  active_prompt_version
  active_tool_policy_version
  active_retrieval_config
  active_model_route

documents
  id
  tenant_id
  owner
  source
  freshness_timestamp
  acl
  trust_level

document_chunks
  id
  document_id
  embedding
  text_pointer
  metadata

tools
  id
  name
  schema
  risk_level
  required_scopes
  owner_team

workflow_runs
  id
  user_id
  agent_id
  status
  current_step
  retry_count
  idempotency_key

traces
  id
  request_id
  user_id
  agent_id
  prompt_version
  model_version
  retrieved_document_ids
  tool_call_ids
  validation_status

feedback
  id
  trace_id
  label_type
  label
  reviewer
  notes
```

---

# 4. Example Request Path

User asks:

```text
Can I share this customer roadmap summary with Vendor X?
```

The system:

1. Authenticates the user and resolves tenant permissions.
2. Classifies the request as policy-sensitive.
3. Retrieves customer-sharing policy, vendor contract metadata, and prior approved examples.
4. Filters all documents by ACL before model exposure.
5. Builds context with source snippets, freshness metadata, and citation requirements.
6. Routes to a stronger model because policy risk is high.
7. Produces a structured answer with recommendation, citations, uncertainty, and escalation flag.
8. Validates that citations refer to retrieved documents.
9. Returns the answer or sends it to review if confidence is low.
10. Stores the trace and feedback hook.

---

# 5. Interview Framing

In an interview, do not start by naming vendors. Start with the workflow, then draw boundaries around risk.

A concise framing:

```text
I would design this as an orchestrated AI workflow, not a model endpoint.
The gateway handles auth and rate limits, the orchestrator owns control flow,
retrieval builds permissioned evidence, the model gateway centralizes routing,
the policy engine gates actions, workers execute durable side effects, and the
eval pipeline turns traces into release gates.
```

Then walk through one request end to end.
