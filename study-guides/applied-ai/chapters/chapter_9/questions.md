---
layout: page
title: "Chapter 9 Questions: AI System Design"
guide_type: questions
---

# Chapter 9 — Practice Questions

Explanatory material for this chapter lives in `guide.md`.

---

# Common Interview Questions and Sample Answers

---

## Question 1

**Design an enterprise AI agent platform that lets internal teams build agents over company data and tools.**

### Sample Answer

I would start by separating the shared platform from individual agents. The shared platform would provide an API gateway, authentication, tenant and team isolation, an orchestration service, a model gateway, a retrieval service, a tool registry, a workflow engine, trace storage, eval infrastructure, and a human review console.

Each agent would be a versioned configuration over:

* prompt templates
* allowed tools
* retrieval sources
* permission scopes
* model routes
* safety policies
* eval suites
* rollout flags

The request path would be: client request enters the gateway, auth attaches user and tenant metadata, the orchestrator loads the agent configuration, retrieval fetches permission-filtered context, the model gateway calls the selected model, proposed tool calls are authorized by a policy engine, workers execute approved actions, and traces plus feedback are stored.

The main architectural reasoning is that agent builders should not reimplement auth, tracing, tool permissions, or evals. The platform centralizes these controls while still letting teams customize product behavior.

Important tradeoffs:

* A generic platform improves reuse but can slow product-specific iteration.
* Centralized tool governance improves safety but creates approval overhead.
* Shared retrieval infrastructure reduces operational burden but requires strong tenant and document-level isolation.
* Model routing saves cost but needs evals to prevent hard tasks from going to weak models.

The biggest risks are permission leaks, unsafe tool execution, unclear ownership, and silent regressions across many agents. I would mitigate them with permission-aware retrieval, tool risk levels, prompt/version management, per-agent dashboards, offline eval gates, canary rollout, and kill switches for write tools.

---

## Question 2

**Design a coding assistant that can answer questions about a repository, edit files, and run tests.**

### Sample Answer

I would design it as a stateful developer workflow system rather than a simple chat wrapper. The main components would be an editor client, API gateway or local agent runtime, repository indexer, context builder, model gateway, patch generator, sandboxed command runner, trace store, and eval pipeline.

The repository indexer would build searchable representations of files, symbols, imports, diagnostics, recent edits, git history, and test metadata. The context builder would select relevant files and snippets based on the current cursor, user request, recently viewed files, search results, linter diagnostics, and prior tool output.

For edits, I would prefer patch-based changes with small diffs. For command execution, I would use a sandbox with allowlists, timeouts, and clear user approval for risky commands. The assistant should store the prompt version, selected context, generated diff, commands run, command output, and final status.

The request lifecycle:

1. User asks for a change.
2. System classifies the task as explanation, edit, debug, or command.
3. Context builder retrieves relevant code.
4. Model proposes a plan or patch.
5. Patch is applied and diagnostics are checked.
6. Tests or targeted commands run if appropriate.
7. Trace and outcome are stored.

The main tradeoff is context depth versus latency. Full-repo context is expensive and noisy; narrow context may miss important dependencies. I would use layered retrieval: open files and recent edits first, symbol search second, broader semantic search only when needed.

Evaluation should include compile/test pass rate, task completion, edit minimality, user acceptance, unsafe command rate, and regression cases from previous failures.

---

## Question 3

**Design a customer support automation system that answers tickets and can perform limited account actions.**

### Sample Answer

I would separate answering from acting. The system can draft grounded replies and recommend actions, but deterministic policy checks and human review should gate high-impact mutations.

Architecture:

* ticket ingestion service
* API gateway and auth
* classifier for ticket type, urgency, sentiment, and risk
* retrieval over help center articles, policy docs, account metadata, and prior cases
* context builder with citations and freshness metadata
* model gateway for answer drafting
* policy engine for action authorization
* workflow engine for account actions
* human review queue
* trace, feedback, and eval storage

For a refund request, the system would retrieve order data, refund policy, prior contact history, and account risk signals. The model would produce a recommended answer and action. The policy engine would check amount thresholds, eligibility, user permissions, duplicate refunds, and whether human approval is required. Only approved actions would execute.

Metrics should include resolution rate, time to first response, escalation rate, reopen rate, customer satisfaction, human edit distance, policy violation rate, tool failure rate, and cost per resolved ticket.

The biggest failure modes are stale policy retrieval, hallucinated promises, unsafe refunds, and over-automation of angry or legally sensitive tickets. I would mitigate these with citation validation, policy versioning, confidence thresholds, human review, action audit logs, and sampled QA.

---

## Question 4

**Design a research copilot that searches sources, synthesizes findings, and cites claims.**

### Sample Answer

I would design around provenance. The system should make it easy to inspect which source supports each claim.

The architecture would include source connectors, ingestion workers, document parsers, an object store for raw documents, a metadata store, vector and keyword indexes, reranking, context assembly, a model gateway, citation validation, and feedback capture.

The request lifecycle:

1. User asks a research question.
2. System decomposes the question into search intents.
3. Search retrieves candidate sources.
4. Reranker prioritizes sources by relevance, freshness, authority, and diversity.
5. Context builder extracts evidence snippets with source IDs.
6. Model synthesizes an answer with claim-level citations.
7. Validator checks that cited sources were retrieved and that unsupported claims are reduced or flagged.
8. User feedback on sources and answer quality is stored.

The tradeoff is breadth versus faithfulness. Broad search improves recall but increases noise and latency. Narrow search improves precision but may miss important counterevidence. I would support iterative exploration where the user can inspect sources, ask follow-up questions, and request deeper search.

Evaluation should include citation accuracy, claim support, source relevance, coverage of counterarguments, answer helpfulness, and latency.

---

## Question 5

**Design a workflow automation agent that updates CRM records, sends emails, and creates follow-up tasks.**

### Sample Answer

I would use a durable workflow engine rather than a single autonomous prompt loop. The model can interpret unstructured input and recommend next steps, but the workflow engine should own state transitions, retries, idempotency, and approval gates.

Architecture:

* trigger ingestion from email, webhook, or UI
* classifier for workflow type
* orchestrator
* durable workflow engine
* tool registry for CRM, email, calendar, and task systems
* policy engine
* human approval queue
* relational database for workflow state
* event queue for asynchronous steps
* tracing and eval pipeline

State should include workflow ID, current step, completed steps, pending approvals, retry counts, tool outputs, idempotency keys, and final status.

For sending an email, the model may draft the content. Deterministic code should verify recipient domain, template constraints, user permissions, and whether approval is required. The send action should use an idempotency key so retries do not send duplicates.

The biggest tradeoff is flexibility versus reliability. A free-form agent can handle surprising tasks but is hard to validate. A state-machine workflow is more reliable but less flexible. I would start with explicit workflows for common high-value processes and use the model inside bounded steps.

---

## Question 6

**How would you design memory and retrieval for an internal knowledge assistant with strict permissions?**

### Sample Answer

I would enforce permissions before the model sees content. The retrieval layer should filter documents by user, group, tenant, document ACLs, and possibly purpose of access.

Storage would be split:

* relational DB for users, groups, permissions, document metadata, and feedback
* object store for raw documents
* vector index for semantic chunks with document IDs and ACL metadata
* keyword index for exact matching
* cache for hot metadata and frequent retrieval results

The ingestion pipeline would parse documents, chunk them, compute embeddings, attach source metadata, owner, freshness, and ACLs, then write to indexes. When a user asks a question, retrieval should apply ACL filters before returning chunks. The context builder should preserve citations and document freshness.

For conflicting documents, the system should prefer authoritative and recent sources, flag conflicts, and expose source ownership. For sensitive categories, it should escalate or refuse rather than answer from ambiguous context.

Failure modes include permission leakage, stale docs, contradictory answers, and prompt injection hidden inside retrieved documents. Mitigations include ACL-filtered retrieval, document trust scores, instruction/data separation, freshness metadata, doc-owner feedback, and audit logging.

---

## Question 7

**How would you debug a production incident where an AI assistant suddenly starts giving worse answers, but no service is down?**

### Sample Answer

I would treat it as a silent regression and compare traces.

First I would define the failing behavior: what task, which users, which time window, and which metric changed. Then I would collect bad traces and nearby good traces. For each trace, I would compare request classification, prompt version, model route, retrieval query, retrieved documents, context assembly, model output, validation results, tool calls, and final answer.

I would look for the first divergence:

* new prompt version
* model provider update
* retrieval index refresh
* document ingestion bug
* changed feature flag
* tool schema change
* policy config change
* distribution shift in user requests

Once the likely cause is found, I would create an eval case from the failure before fixing it. Then I would roll back or patch the responsible layer, canary the fix, and monitor online metrics.

The key reasoning is that AI failures often do not throw exceptions. Observability must preserve enough execution context to reconstruct what changed.

---

## Question 8

**How would you prevent cost blowups in a multi-agent system?**

### Sample Answer

I would budget the system at multiple levels: per request, per user, per tenant, per workflow, and per tool loop.

Controls:

* model routing based on task complexity
* small models for classification and routing
* prompt and context token budgets
* maximum agent iterations
* maximum tool calls
* retrieval result limits
* retry budgets
* cache for repeated context and retrieval
* async batch jobs where latency is not critical
* per-tenant quotas and alerts
* circuit breakers when spend spikes

I would measure cost per successful task, not just cost per request. A cheap answer that causes human rework may be more expensive than a stronger model call.

The architecture should expose token usage, model cost, tool cost, retry counts, and latency by stage. Without stage-level metrics, cost optimization becomes guesswork.

The tradeoff is that aggressive cost controls can reduce quality. I would protect high-risk workflows with stronger models and verification while optimizing low-risk high-volume paths.

---

## Question 9

**How would you design rollout and rollback for prompt, model, retrieval, and tool changes?**

### Sample Answer

I would version each layer independently.

Prompts should have stable IDs, owners, changelogs, eval results, and rollout status. Models should be routed through a model gateway so traffic can shift by percentage, tenant, user group, task type, or feature flag. Retrieval configs should be versioned, including embedding model, chunking strategy, index snapshot, reranker, and filters. Tool schemas and policies should also be versioned because prompt behavior depends on tool interfaces.

Rollout process:

1. Run offline evals against relevant regression suites.
2. Run shadow mode if possible.
3. Canary to internal users or a small tenant slice.
4. Monitor quality, safety, latency, and cost metrics.
5. Expand gradually.
6. Roll back the changed layer if regressions appear.

Rollback should not require redeploying the whole application. For example, a bad prompt should be rolled back through prompt config, not a code revert. A bad model route should be changed at the gateway. A bad retrieval index should fall back to the previous snapshot.

The risk is interaction effects: a new prompt may work with one tool schema but fail with another. That is why evals need to test realistic full workflows, not isolated prompts only.

---

## Question 10

**How would you design safety and permissions for an agent that can use internal tools and external APIs?**

### Sample Answer

I would not rely on prompt instructions as the permission boundary. Safety should be enforced by the application, policy engine, retrieval layer, and tool execution layer.

Design:

* authenticate user and tenant at ingress
* map user to scopes and roles
* filter retrieval by ACL before model exposure
* register tools with risk levels and required scopes
* validate tool arguments against schema and business rules
* require human approval for high-impact or irreversible actions
* use idempotency keys for side effects
* log every decision and action
* provide kill switches for write tools

Tool risk should determine execution mode:

* read-only tools can often execute directly with rate limits
* draft tools can produce artifacts for review
* write tools need policy checks
* high-risk write tools need approval or deterministic execution only

The core principle is least privilege. The agent should only see data and tools needed for the current task, and only for the current user context.

---

## Question 11

**Design monitoring and observability for a production AI platform.**

### Sample Answer

I would combine standard service observability with AI-specific traces.

Standard metrics:

* request volume
* error rate
* latency percentiles
* dependency health
* queue depth
* worker failures

AI-specific metrics:

* token usage
* model cost
* prompt version distribution
* model route distribution
* retrieval hit rate
* reranker score distribution
* tool-call success rate
* validation failure rate
* human override rate
* escalation rate
* task success
* safety incidents

A trace should connect the user request, classification, prompt version, model version, retrieved document IDs, assembled context or redacted context, tool calls, validation results, final answer, and feedback.

For debugging, I would support trace comparison between good and bad examples. For privacy, I would redact sensitive values, restrict trace access, and set retention policies.

The main tradeoff is debuggability versus privacy. The system needs enough information to explain behavior without storing unnecessary sensitive content forever.

---

## Question 12

**You are designing an AI system for a high-stakes domain where wrong answers are costly. How does your architecture change?**

### Sample Answer

I would reduce autonomy, increase verification, and make uncertainty visible.

Changes:

* stronger identity and permission checks
* authoritative retrieval sources only
* stricter context construction
* lower tolerance for unsupported claims
* structured outputs with uncertainty and citations
* deterministic validation
* human review for ambiguous or high-impact cases
* conservative fallback behavior
* stronger audit logging
* slower rollout
* larger offline eval suites
* incident review process

The model should often draft or recommend rather than execute. If actions are allowed, they should be reversible where possible and gated by policy.

The tradeoff is slower user experience and higher cost. That is acceptable when the cost of wrong automation is high. In interviews, I would explicitly tie autonomy level to reversibility, impact, and observability.

---

## Question 13

**How would you choose between building a general AI agent platform and building one product-specific agent?**

### Sample Answer

I would start from the workflows and ask how much is genuinely shared.

A general platform is justified when multiple teams need the same primitives: auth, tool registry, retrieval, model gateway, tracing, evals, prompt management, human review, and rollout controls. It reduces duplication and improves governance.

A product-specific agent is better when the workflow has unique UX, domain logic, latency requirements, or safety constraints. It can be optimized more aggressively and evaluated more directly.

The risk of a platform is premature abstraction. Teams may spend months building generic agent infrastructure before proving any workflow creates value. The risk of product-specific agents is fragmentation: inconsistent permissions, poor observability, duplicated tool integrations, and no shared eval standards.

My approach would be to build the first high-value workflow product-specifically, but factor out only the platform capabilities that become obviously repeated: model gateway, tracing, tool registry, retrieval connectors, and eval harness.

---

## Question 14

**How would you design an eval loop for a top-layer AI product after launch?**

### Sample Answer

I would build a loop that connects production traces to offline and online evaluation.

Production logging captures request metadata, prompt version, model version, retrieval IDs, tool calls, validations, output, and user outcomes. A sampling job selects traces for human review based on failures, high-risk categories, low confidence, user dissatisfaction, and random sampling. Reviewers label correctness, faithfulness, safety, and task completion.

Those labels become:

* regression test cases
* prompt improvement data
* retrieval ranking feedback
* model routing data
* policy updates
* product UX insights

Before each change, the system runs offline evals. During rollout, canaries monitor online metrics. After rollout, failures are added back into the eval set.

The key reasoning is that evals should evolve with production. A static benchmark quickly becomes less useful as user behavior, documents, tools, and models change.

---

## Question 15

**How would your architecture change when an AI product scales from 10,000 users to 100 million users?**

### Sample Answer

At 10,000 users, the main challenge is proving product quality and making the request path observable. A straightforward architecture with an API gateway, model gateway, retrieval service, database, cache, queue, and eval loop may be enough.

At 100 million users, the main challenge becomes controlling blast radius and variable load. I would add regional routing, tenant or user segmentation, stricter admission control, token-aware quotas, multi-region model capacity, global traffic management, per-route autoscaling, hot-key and hot-tenant mitigation, more aggressive caching, async queues for non-interactive work, and circuit breakers around retrieval, model providers, and tools.

The system also needs stronger operational controls:

* per-region and per-tenant metrics,
* progressive rollout by cohort,
* model and prompt versioning,
* regional fallbacks,
* cost dashboards,
* abuse detection,
* incident playbooks,
* data residency controls.

The key tradeoff is that global scale improves reach but increases coordination cost. You cannot treat the product as one homogeneous service anymore. You need slices: by region, tenant, route, model, risk level, and workload type.

---

## Question 16

**How would you scale a RAG product from 10,000 documents to 100 million documents?**

### Sample Answer

I would stop thinking of retrieval as one index and start treating it as a retrieval platform. At 10,000 documents, a simple vector index with metadata and reranking may work. At 100 million documents, I need sharded indexes, hybrid sparse+dense retrieval, query routing, strict permission filtering, bounded fanout, approximate search, compression, replicas, async ingestion, freshness policies, and per-shard observability.

The request path would be:

1. classify the query and construct filters,
2. route to tenant, region, time, or semantic shards,
3. run dense and sparse retrieval with bounded fanout,
4. merge candidates,
5. rerank only a manageable candidate set,
6. construct context with citations,
7. record index and shard versions for debugging.

The main tradeoffs are recall versus latency, memory versus precision, freshness versus stability, and fanout versus coordination cost. I would tune the system against retrieval evals, not only QPS benchmarks.

---

## Question 17

**When a system gets slower as it scales, how do you decide what to fix first?**

### Sample Answer

I would identify which assumption broke. Did data stop fitting on one machine? Did one database become write-bound? Did queue age grow? Did one shard get hot? Did cross-service coordination dominate latency? Did the reranker or model become the bottleneck?

Then I would use traces and per-stage metrics to locate the bottleneck:

* ingress and auth,
* database queries,
* retrieval latency,
* shard fanout,
* queue wait,
* model prefill and decode,
* tool calls,
* retries,
* postprocessing.

The fix depends on the bottleneck. Add indexes or partitioning for slow scans, shard or replicate for capacity, cache repeated work, move background tasks to queues, reduce fanout, batch model work, route easy requests to cheaper paths, or add circuit breakers if failures cascade. The important thing is not to add infrastructure blindly. Scale problems are specific.
