---
layout: page
title: "Chapter 9: AI System Design"
guide_type: chapter
---

# Chapter 9 — AI System Design

This chapter is where the lower-level pieces become a product or platform.

Earlier chapters explain models, prompting, retrieval, agents, evaluation, learning, and serving. Chapter 7 asks the interview question that usually matters most in senior AI engineering loops:

Can you compose those primitives into a reliable system that real users, teams, and businesses can depend on?

The signal is not whether you can draw boxes. The signal is whether each box has a reason to exist, whether data flows are explicit, whether failures are contained, and whether the system improves over time without becoming unsafe, slow, or unaffordable.

For full scenario practice, use the [Applied AI Capstone Scenarios](../../capstones/overview.html). They combine system design with retrieval, agents, evals, learning loops, production operations, and the security boundaries from [Chapter 10](../chapter_8/guide.html).

---

## Table of Contents

- TOC
{:toc}

---

# 1. The Core Mental Model

A production AI system is not a model wrapped in an API.

It is a control system around a probabilistic component.

The model produces uncertain outputs. The system around it must decide:

* what context the model sees
* what tools it may call
* what state it may read or mutate
* what permissions constrain it
* what validations gate its outputs
* what telemetry records its behavior
* what feedback changes future behavior

The top-layer design question is therefore:

How do I turn uncertain reasoning into bounded, observable, recoverable product behavior?

A useful architecture separates five concerns:

1. User interaction: authentication, product surface, request shaping, streaming.
2. Intelligence: prompts, retrieval, model routing, planning, tool selection.
3. Execution: tool calls, workers, queues, transactions, human approval.
4. Memory: conversation state, user preferences, retrieved knowledge, audit records.
5. Improvement: traces, feedback, evals, experiments, rollouts, rollback.

If those concerns are mixed together, the system becomes hard to debug. A prompt change accidentally changes permissions. A retrieval bug silently changes tool behavior. A latency optimization removes evidence needed for audits. Strong system design keeps these responsibilities separate even when the first prototype is small.

---

# 2. Example System Types

The same primitives appear across many AI products, but the risk profile changes by product.

## 2.1 Enterprise AI Agent Platform

An enterprise agent platform lets multiple teams build agents that can read internal data, call business tools, and automate workflows.

The hard parts are multi-tenancy, permissions, auditability, tool governance, and shared evaluation infrastructure. The platform needs a registry for tools, prompts, models, policies, datasets, and eval suites. It also needs tenant isolation so one team cannot accidentally leak another team's documents, credentials, or traces.

Good design emphasizes:

* central tool registry with permission metadata
* policy engine for action approval
* prompt and workflow versioning
* per-tenant retrieval indexes or access-filtered shared indexes
* tracing across model calls, tool calls, and human approvals
* staged rollout by tenant, user group, workflow, and model

The interview framing is: "I would design the platform so each agent is a configured workflow over shared primitives, not a one-off service with hidden permissions."

## 2.2 Coding Assistant

A coding assistant reads repository context, proposes edits, runs tools, and explains code.

The hard parts are context selection, low-latency interaction, edit safety, sandboxing, and respecting developer intent. The assistant needs repo indexing, symbol search, recent-edit awareness, terminal/tool execution, diff generation, and rollback-friendly state.

Good design emphasizes:

* local or server-side code indexing
* retrieval over files, symbols, commits, diagnostics, and terminal output
* sandboxed command execution
* patch-based edits rather than blind rewrites
* small context windows tailored to the current task
* evals for edit correctness, command safety, and regression avoidance

The interview framing is: "I would treat the assistant as a stateful developer workflow system, not just a chat box over code."

## 2.3 Customer Support Automation

Customer support automation answers questions, drafts replies, triages tickets, and sometimes takes actions such as refunds or account changes.

The hard parts are grounding, policy compliance, escalation, and safe action execution. Retrieval quality matters because one stale policy can produce costly or illegal behavior. Human review queues are central because many tasks are better framed as draft-and-approve than fully autonomous execution.

Good design emphasizes:

* retrieval over help center, policy docs, account metadata, and prior tickets
* confidence and policy checks before answering
* human review for refunds, account changes, and high-risk categories
* audit logs for every source and action
* feedback labels from agent edits, customer satisfaction, and reopen rates

The interview framing is: "I would separate answer generation from action authorization, because fluent text is not the same as permission to mutate customer state."

## 2.4 Research Copilot

A research copilot helps users search, read, compare, synthesize, and cite sources.

The hard parts are source quality, citation faithfulness, long-context synthesis, and iterative exploration. The system needs search tools, document parsers, citation tracking, note memory, and mechanisms to distinguish evidence from speculation.

Good design emphasizes:

* source ingestion with metadata and provenance
* retrieval over papers, webpages, notes, and user libraries
* citation-aware answer generation
* background workers for document processing
* claims linked to retrieved evidence
* feedback on source usefulness and answer correctness

The interview framing is: "I would optimize for traceable synthesis, where every important claim can be mapped back to a source."

## 2.5 Workflow Automation Agent

A workflow automation agent coordinates multi-step business processes: update a CRM, send an email, schedule a meeting, open a ticket, reconcile records.

The hard parts are durable state, retries, idempotency, authorization, and partial failure recovery. The agent cannot simply "think through" a workflow inside a single model call. It needs explicit state machines or durable workflow orchestration.

Good design emphasizes:

* workflow engine for long-running tasks
* idempotent tool calls
* checkpoints after each step
* human approval for irreversible actions
* event queues for asynchronous execution
* compensation logic when downstream actions fail

The interview framing is: "I would use the model for interpretation and decision support, but use durable workflow machinery for execution."

## 2.6 Internal Knowledge Assistant

An internal knowledge assistant answers employee questions using company docs, chats, tickets, and wikis.

The hard parts are permissions, freshness, conflicting documents, and trust. Employees may ask about compensation, incidents, customer contracts, or unreleased strategy. The assistant must enforce document-level access and show provenance.

Good design emphasizes:

* permission-aware retrieval
* freshness metadata and document ownership
* conflict detection across sources
* source citations in answers
* feedback loops for doc owners
* monitoring unanswered or low-confidence topics

The interview framing is: "I would make access control part of retrieval itself, not a post-processing filter after the model has already seen restricted text."

---

# 3. System Design Primitives

Top-layer system design is easier if you reduce it to primitives.

## 3.1 Interfaces

Interfaces define how users and other systems ask for work.

Examples:

* chat endpoint
* code editor command
* ticket triage webhook
* scheduled workflow
* internal API call

The interface determines latency expectations. A chat response may need to stream within one second. A document ingestion job can take minutes. A refund approval workflow can wait for human review.

## 3.2 Context

Context is the information used to condition model behavior.

Examples:

* user request
* conversation history
* retrieved documents
* account state
* repository files
* tool outputs
* policy rules

The core design problem is signal selection. Too little context produces hallucination. Too much context increases latency, cost, and distraction.

## 3.3 Control Flow

Control flow decides which steps run and in what order.

Examples:

* single prompt
* retrieval then generation
* planner then executor
* tool loop with stopping conditions
* durable workflow
* human-in-the-loop approval

Control flow should be explicit in the application layer. If all control flow lives inside the prompt, debugging and safety become much harder.

## 3.4 State

State is information preserved across steps or requests.

Examples:

* conversation state
* workflow step state
* user preferences
* retrieved evidence
* pending approvals
* tool-call results
* eval labels

State needs ownership. Relational databases usually store durable business state. Caches store temporary speedups. Vector databases store searchable representations. Object stores hold large artifacts. Trace systems store execution history.

## 3.5 Tools

Tools let the system read data or take actions.

Read tools are usually safer: search docs, fetch account status, inspect logs.

Write tools are riskier: issue refund, deploy code, update CRM, send email.

The design should classify tools by risk, permissions, rate limits, idempotency, and approval requirements. Tool descriptions alone are not a permission model.

## 3.6 Evaluation

Evaluation is how the system knows whether it is improving.

Examples:

* golden test sets
* regression suites
* online user feedback
* human review labels
* task completion metrics
* trace audits
* safety incident review

Evals should connect to product outcomes. A support bot is not good because its responses sound polished. It is good if resolution time improves without increasing escalations, wrong answers, or policy violations.

## 3.7 Reference-Guided Improvement

Some system designs add a slower or more expensive reference process to improve the fast production path.

Use this pattern when:

* a verifier, search process, or human review path is too expensive for every request but produces high-quality guidance,
* a policy needs to improve while staying near a safe baseline,
* a specialized enterprise behavior is out of distribution for the base model,
* a large teacher model can produce behavior that a smaller production model should learn,
* a prompt or privileged context works but is too brittle or expensive to keep in every runtime request.

The design checklist:

* identify the fast object: student model, policy, router, or agent,
* identify the reference object: teacher, old policy, target network, verifier, search process, or judge,
* define the update signal: logits, reward, preference, mask, search target, or selected trajectory,
* define refresh cadence: frozen, checkpoint promotion, EMA, or scheduled retraining,
* gate with evals: target behavior, specificity, regression, safety, latency, and cost,
* keep rollback and lineage: student version, reference version, data version, eval version.

This turns a vague answer like "we will improve the model from feedback" into a concrete system design.

## 3.8 Observability

Observability is the ability to answer: what happened, why, and how often?

For AI systems, logs are not enough. You need traces that connect:

* user request
* selected prompt version
* retrieved documents
* model and parameters
* tool calls
* validations
* final answer
* user or reviewer feedback

Without this chain, silent regressions become normal.

---

# 4. Required Design Dimensions

In interviews, a complete answer should cover the following dimensions.

## 4.1 Architecture

Architecture is the stable decomposition of responsibilities.

A common high-level architecture:

* client or product surface
* API gateway
* auth and permission service
* orchestration service
* retrieval service
* model gateway
* tool execution layer
* workflow workers
* relational database
* vector database
* cache
* event queue
* logging and tracing
* evaluation pipeline
* human review console

The key is not naming every component. The key is explaining why each boundary exists.

For example, separating a model gateway from the orchestrator lets you change model providers, apply routing, centralize rate limits, and log model usage consistently.

## 4.2 Data Flow

Data flow describes how information enters, moves through, and exits the system.

A strong answer traces one request end to end:

1. User submits request.
2. API gateway authenticates and rate-limits.
3. Orchestrator loads user, tenant, conversation, and policy state.
4. Retrieval service fetches relevant context subject to permissions.
5. Context builder compacts and ranks evidence.
6. Model gateway calls selected model with versioned prompt.
7. Tool calls are validated and executed if allowed.
8. Final response is validated, streamed, and stored.
9. Trace, feedback hooks, and eval events are emitted.

This makes hidden assumptions visible.

## 4.3 Memory and Retrieval

Memory and retrieval decide what the system can know at runtime.

Use different storage for different jobs:

* relational database for users, workflows, permissions, and durable state
* vector database for semantic search over documents and prior artifacts
* object store for raw files, transcripts, PDFs, logs, and large payloads
* cache for repeated retrieval results, prompts, feature flags, and hot metadata

Retrieval should be permission-aware, freshness-aware, and observable. The system should log which documents were retrieved and which were actually used in the answer.

## 4.4 Tool Orchestration

Tool orchestration decides how the model interacts with external systems.

For low-risk read tools, direct model-driven tool calls may be acceptable if schema validation and rate limits exist. For high-risk write tools, the application should require explicit authorization, approval, or deterministic business logic.

A good design separates:

* tool discovery: what tools exist
* tool selection: which tool is relevant
* tool authorization: whether this user and workflow may call it
* tool execution: the actual side effect
* tool observation: what result returns to the model

The model may help choose a tool, but it should not be the only authority deciding whether the action is allowed.

## 4.5 State Management

State management determines whether multi-step behavior survives retries, restarts, and partial failures.

Use request-local state for ephemeral context. Use durable state for workflows and actions. Use append-only event logs for audit-sensitive systems. Use caches only for values that can be recomputed.

For long-running agents, a durable workflow engine is often better than a recursive prompt loop. The workflow engine can checkpoint progress, retry failed steps, time out stuck work, and expose state to operators.

## 4.6 Eval Loop

The eval loop converts traces and feedback into improvement.

A practical loop:

1. Log production traces with inputs, prompts, retrieved context, outputs, and outcomes.
2. Sample failures and edge cases for human labeling.
3. Convert labels into offline eval cases.
4. Run evals before prompt, model, retrieval, or tool changes.
5. Release changes behind flags.
6. Monitor online metrics and rollback if regressions appear.

This is how AI systems become engineering systems instead of demo systems.

## 4.7 Safety and Permissions

Safety and permissions are design constraints, not final filters.

A strong design enforces permissions at multiple layers:

* API layer authenticates the user and tenant
* retrieval layer filters documents before model exposure
* tool registry marks risk level and required scopes
* policy engine approves or blocks actions
* human review queue handles ambiguous or high-impact cases
* audit log records sources, decisions, and side effects

For action agents, make unsafe actions impossible by construction whenever possible.

## 4.8 Rollout Strategy

Rollout strategy controls blast radius.

Common rollout mechanisms:

* feature flags
* tenant allowlists
* shadow mode
* canary release
* A/B tests
* staged model routing
* prompt version pinning
* kill switches

For AI systems, rollout should include eval gates before launch and monitoring after launch. The system should also support rollback of prompts, models, retrieval configs, and tool policies independently.

## 4.9 Monitoring and Debugging

Monitoring asks whether the system is healthy. Debugging asks why it failed.

Useful metrics include:

* request volume
* latency by stage
* token usage
* model cost
* retrieval hit rate
* tool error rate
* validation failure rate
* escalation rate
* human override rate
* task success rate
* safety violation rate

Useful debugging artifacts include:

* full request traces
* prompt versions
* retrieved documents
* model outputs before validation
* tool-call payloads
* policy decisions
* user feedback
* reviewer notes

AI debugging is often comparative. You compare a bad trace with a good trace and identify where the divergence begins.

## 4.10 Cost and Latency Management

Cost and latency are product features.

Common controls:

* model routing by task difficulty
* prompt compression
* retrieval caching
* parallel retrieval and metadata loading
* smaller models for classification and routing
* batch background jobs
* streaming responses
* token budgets per workflow
* circuit breakers on tool loops
* precomputed indexes and summaries

The strongest design answers do not say "use a faster model." They break cost and latency into components and show which component dominates.

---

# 5. Common Technologies and Patterns

The exact stack varies, but the patterns are stable.

## 5.1 API Gateway

An API gateway handles authentication, rate limiting, request size limits, routing, and coarse-grained tenant isolation.

It protects expensive downstream systems from malformed or abusive requests. It is also a natural place to attach request IDs for trace correlation.

## 5.2 Worker Orchestration

Worker orchestration runs asynchronous or long-running work.

Common choices:

* Celery, Sidekiq, BullMQ, Temporal, Dagster, Airflow, Argo Workflows
* Kubernetes jobs for isolated execution
* serverless functions for bursty lightweight tasks

Use workers for ingestion, indexing, batch evals, document parsing, workflow execution, and human-review processing.

## 5.3 Vector DB + Relational DB + Cache

A common storage trio:

* vector DB for semantic retrieval
* relational DB for durable structured state
* cache for low-latency repeated reads

Examples:

* vector DB: Pinecone, Weaviate, Milvus, pgvector, Elasticsearch/OpenSearch vector search
* relational DB: Postgres, MySQL
* cache: Redis, Memcached

The important design point is not the vendor. It is that semantic similarity, transactional state, and fast ephemeral lookup are different problems.

## 5.4 Model Routing

Model routing sends different tasks to different models.

Examples:

* small model for intent classification
* fast model for simple answers
* strong model for complex reasoning
* embedding model for retrieval
* reranker for evidence ordering
* specialized model for code or vision

Routing reduces cost and latency, but adds complexity. You need routing evals because a bad router silently sends hard tasks to weak models.

## 5.5 Event Queues

Event queues decouple producers from consumers.

Common choices:

* Kafka
* SQS
* Pub/Sub
* RabbitMQ
* Redis streams

Queues are useful for ingestion, feedback processing, trace export, notifications, retries, and workflow steps. They also absorb traffic spikes and isolate failures.

## 5.6 Logging and Tracing

AI systems need structured logs and distributed traces.

Trace spans should include:

* request ID
* user and tenant IDs where appropriate
* prompt version
* model version
* retrieval query
* retrieved document IDs
* tool names and statuses
* token counts
* latency
* validation results

For privacy, traces should avoid unnecessary raw sensitive content or apply redaction and retention controls.

## 5.7 Human Review Queues

Human review queues convert uncertain automation into controlled automation.

Use them when:

* an action is high impact
* confidence is low
* policy is ambiguous
* a new workflow is in shadow mode
* users dispute outcomes

Review data should not disappear. It becomes eval data, training data, policy feedback, and product insight.

## 5.8 Feature Flags

Feature flags let you release behavior gradually.

AI systems should flag:

* prompt versions
* retrieval configurations
* model routes
* tool availability
* autonomy level
* safety policies
* UI affordances

Flags are especially important because AI regressions can be qualitative and delayed.

## 5.9 Prompt and Version Management

Prompts are production artifacts.

Treat them like versioned code:

* stable identifiers
* change history
* owners
* eval gates
* rollout status
* rollback support
* compatibility with tool schemas and output schemas

Unversioned prompts make debugging nearly impossible because you cannot reconstruct what the model saw.

---

# 6. Request Lifecycle

A concrete request lifecycle reveals whether the system is actually designed.

Consider an internal knowledge assistant answering: "Can I share this customer roadmap slide with Vendor X?"

## 6.1 Ingress

The client sends the request to the API gateway.

The gateway:

* authenticates the user
* attaches tenant and role metadata
* enforces rate limits
* rejects oversized payloads
* creates a request ID

The request then enters the orchestrator.

## 6.2 Request Classification

The orchestrator classifies the request.

Possible labels:

* knowledge question
* policy question
* action request
* sensitive-data request
* unsupported request

This classification determines retrieval sources, safety checks, model route, and whether human review may be required.

## 6.3 State Loading

The orchestrator loads:

* user profile
* tenant settings
* conversation history
* feature flags
* relevant permissions
* active prompt and policy versions

This state is structured. It should not be reconstructed from free-form chat history if it affects permissions or actions.

## 6.4 Retrieval

The retrieval service searches:

* customer-sharing policy docs
* security policy docs
* contract metadata
* customer account permissions
* prior approved examples

Retrieval filters documents by the user's access rights before returning them.

## 6.5 Context Assembly

The context builder ranks and compresses evidence.

It constructs:

* system instruction
* task instruction
* user request
* relevant policy snippets
* metadata about document freshness
* required citation format
* safety constraints
* output schema

This is where many systems fail. Context assembly is an engineering component, not a string concatenation afterthought.

## 6.6 Model Call

The model gateway selects a model based on task risk and complexity.

It records:

* model name
* prompt version
* temperature
* token counts
* latency
* cost estimate

For policy-sensitive work, the model may be asked to produce structured reasoning fields such as answer, supporting sources, uncertainty, and escalation recommendation.

## 6.7 Validation and Action Gating

The system validates the output.

Checks may include:

* required citations exist
* cited docs were actually retrieved
* answer follows schema
* sensitive action is not being performed directly
* uncertainty threshold is acceptable
* policy category permits direct answer

If validation fails, the system may retry with a repair prompt, fall back to a safer answer, or escalate.

## 6.8 Response and Persistence

The final answer is streamed or returned to the user.

The system stores:

* request and response metadata
* prompt and model versions
* retrieval document IDs
* validation status
* user feedback hook
* trace pointer

Sensitive raw content may require retention limits or redaction.

## 6.9 Feedback and Evaluation

The user may mark the answer helpful, unhelpful, or unsafe. A reviewer may later label whether the answer was policy-correct.

Those labels flow into:

* dashboards
* regression tests
* retrieval quality analysis
* prompt iteration
* policy doc improvement
* model routing changes

The request lifecycle is not complete until production behavior becomes measurable.

---

# 7. Context Building

Context building is the highest-leverage part of many AI products.

A context builder chooses what the model sees. It usually combines:

* instruction context
* user context
* conversation context
* retrieved context
* tool context
* policy context
* output constraints

## 7.1 Retrieval Is Not Enough

Retrieval returns candidates. Context building decides what becomes evidence.

A strong context builder:

* filters by permissions
* ranks by relevance
* considers freshness
* removes duplicates
* compresses long documents
* preserves citations
* separates facts from instructions
* fits within token budget

Bad context building creates retrieval poisoning. A stale document, malicious page, or irrelevant prior ticket can steer the model more than the actual user request.

## 7.2 Context Budgets

Every workflow should have a context budget.

Example budget:

* 500 tokens for system and policy instructions
* 500 tokens for conversation summary
* 2,000 tokens for retrieved evidence
* 500 tokens for tool observations
* 500 tokens reserved for output

Budgets force product decisions. If the system needs more evidence than fits, it may need summarization, reranking, multi-step reading, or a different UX.

## 7.3 Context as an Artifact

For debugging, store the assembled prompt or a redacted representation of it.

You should be able to answer:

* What did the model see?
* Which documents were excluded?
* Which permissions applied?
* Which prompt version was used?
* Which compression strategy ran?

If you cannot reconstruct context, you cannot explain behavior.

---

# 8. Tool Orchestration and State

Tool orchestration is where AI systems become operational systems.

## 8.1 Tool Risk Levels

Classify tools by risk.

Low risk:

* search docs
* fetch read-only account metadata
* run local static analysis
* calculate price estimate

Medium risk:

* draft email
* create ticket
* update non-critical metadata
* schedule meeting

High risk:

* send external email
* issue refund
* change permissions
* deploy code
* delete data

Each level should have different authorization, validation, and review requirements.

## 8.2 Deterministic Guards Around Probabilistic Choices

The model can propose an action. Deterministic code should check whether the action is valid.

Example:

The model proposes `refund_customer(order_id=123, amount=500)`.

The policy engine checks:

* user has refund scope
* order belongs to tenant
* amount is below threshold
* customer is eligible
* no duplicate refund exists
* workflow has required approval

Only then does the tool execute.

## 8.3 Durable Agent State

For multi-step work, state should not live only in the model context.

Durable state includes:

* workflow ID
* current step
* completed steps
* pending approvals
* retry count
* tool-call outputs
* compensation actions
* final status

This lets the system resume after crashes, inspect stuck workflows, and avoid repeating side effects.

## 8.4 Idempotency

Tool calls that mutate external systems should be idempotent.

An idempotency key prevents retries from sending the same email twice, issuing the same refund twice, or creating duplicate tickets.

Without idempotency, retries turn reliability mechanisms into new failure modes.

---

# 9. Failure Containment

AI systems fail in ways that look plausible.

Containment means one bad component does not corrupt the whole system.

## 9.1 Bound Each Loop

Agent loops need:

* maximum iterations
* maximum tool calls
* maximum token budget
* maximum wall-clock time
* stopping conditions
* escalation path

Unbounded loops create latency spikes, cost blowups, and duplicated actions.

## 9.2 Isolate Tools

Tool failures should return structured errors.

The model should not see raw stack traces, secrets, or confusing partial payloads. The orchestrator should decide whether to retry, use fallback data, or escalate.

## 9.3 Use Circuit Breakers

Circuit breakers protect shared dependencies.

Examples:

* disable a flaky tool after error rate spikes
* fall back to cached retrieval during vector DB degradation
* route to a cheaper model when budget is exceeded
* stop autonomous writes during safety incidents

Circuit breakers should be visible to operators and reflected in user-facing behavior.

## 9.4 Separate Drafting From Execution

When risk is high, let the model draft and let deterministic systems or humans execute.

This is the difference between:

* "Here is a suggested refund response for review"
* "The assistant refunded $5,000"

The first can be safely iterated. The second requires strong controls.

---

# 10. Feedback, Evaluation, and Evolution

Production AI systems evolve through feedback loops.

## 10.1 Feedback Storage

Store feedback with enough context to be useful.

Useful fields:

* request ID
* user segment
* prompt version
* model version
* retrieved document IDs
* answer
* user rating
* reviewer label
* failure category
* free-text notes
* downstream outcome

Feedback without trace linkage becomes anecdotal.

## 10.2 Offline Evals

Offline evals catch regressions before rollout.

Build eval sets from:

* production failures
* high-volume tasks
* safety-critical examples
* edge cases
* adversarial inputs
* reviewer-labeled traces

Evals should measure the behavior you care about. For a knowledge assistant, faithfulness and citation accuracy matter. For a workflow agent, task completion and side-effect correctness matter. For a coding assistant, build/test success and edit minimality matter.

## 10.3 Online Monitoring

Online monitoring validates real behavior.

Track:

* task success
* user satisfaction
* human override rate
* escalation rate
* cost per successful task
* latency percentiles
* safety incidents
* retrieval zero-result rate
* tool failure rate

Use online metrics to detect distribution shift that offline evals missed.

## 10.4 System Evolution

The system evolves along several axes:

* better retrieval
* better prompts
* better model routes
* better tools
* better product UX
* better eval coverage
* better policies
* better human review workflows

Mature teams avoid changing everything at once. They version each layer and roll out changes independently so regressions can be attributed.

---

# 11. Tradeoffs

System design is tradeoff selection.

## 11.1 Autonomy vs Control

More autonomy can reduce human workload and handle flexible tasks. It also increases risk because the system may choose unexpected paths.

Use higher autonomy when actions are low risk, reversible, observable, and well evaluated. Use lower autonomy when actions are high impact, irreversible, ambiguous, or legally sensitive.

## 11.2 Latency vs Quality

Better answers often require more retrieval, stronger models, reranking, tool calls, and verification. Each adds latency.

For interactive products, stream partial responses, parallelize independent work, cache hot context, and use small models for routing. For high-stakes workflows, accept higher latency for verification and review.

## 11.3 Cost vs Reliability

Reliability often costs more: stronger models, retries, evals, tracing, human review, and redundant infrastructure.

The right metric is not cost per request. It is cost per successful task, including human rework, escalations, wrong actions, and churn.

## 11.4 Generality vs Product Fit

A general agent platform can support many workflows, but it may be harder to make any one workflow excellent. A product-specific system can be more reliable and easier to evaluate, but less reusable.

In interviews, avoid overgeneralizing too early. Start with the product workflow, then extract shared platform components where duplication becomes real.

## 11.5 Freshness vs Stability

Fresh data improves relevance, but fresh indexes and prompts can introduce regressions.

Use ingestion pipelines with validation, document ownership, versioned indexes, and rollback. For sensitive domains, know which knowledge snapshot produced each answer.

## 11.6 Observability vs Privacy

Full traces help debugging. They can also store sensitive user data.

Use redaction, scoped access, retention policies, and privacy-aware sampling. Store enough to debug behavior, not every raw token forever.

---

# 12. Failure Modes

## 12.1 Cascade Failures

A retrieval outage causes weak context. Weak context causes the model to call the wrong tool. The wrong tool fails. The agent retries. Retries overload the tool. Latency spikes and costs rise.

Containment:

* health checks
* circuit breakers
* fallback answers
* bounded retries
* per-stage budgets
* graceful degradation

## 12.2 Silent Regressions

A prompt, model, retrieval, or policy change makes answers subtly worse, but no exception is thrown.

Containment:

* prompt and model versioning
* offline regression evals
* canary rollout
* sampled human review
* online quality metrics
* trace comparison

## 12.3 Retrieval Poisoning

Bad or malicious retrieved content steers the model.

Examples:

* stale policy doc
* low-quality wiki page
* user-injected instruction in a document
* irrelevant but semantically similar ticket
* document the user should not access

Containment:

* permission-aware retrieval
* source ranking and trust scores
* freshness metadata
* instruction/data separation
* citation checks
* document owner review

## 12.4 Cost Blowups

The system accidentally sends too many long prompts, retries too often, or enters tool loops.

Containment:

* token budgets
* request budgets
* model routing
* caching
* loop limits
* cost dashboards
* per-tenant quotas

## 12.5 Unsafe Actions

The system takes an action it should only have recommended.

Containment:

* tool risk classification
* policy engine
* approval gates
* idempotency keys
* audit logs
* reversible actions where possible
* kill switch for write tools

## 12.6 Unclear Ownership

Failures fall between teams: model team blames retrieval, retrieval team blames docs, product team blames prompts, platform team blames tool owners.

Containment:

* clear service ownership
* workflow owners
* document owners
* prompt owners
* incident process
* shared traces and dashboards

Ownership is a system design property. If no one owns the behavior, no one can improve it.

---

# 13. What to Say in an Interview

A strong answer is structured, concrete, and operational.

## 13.1 General Design Template

Use this when asked to design any AI product.

1. Clarify the product workflow and success metric.
2. Identify users, permissions, and risk level.
3. Sketch the main architecture.
4. Walk through one request lifecycle.
5. Explain retrieval and memory.
6. Explain tool orchestration and state.
7. Explain safety gates and human review.
8. Explain evals, monitoring, and rollout.
9. Discuss tradeoffs and failure modes.
10. State how the system improves over time.

This template works because it moves from product to architecture to operations.

## 13.2 High-Concurrency Serving Template

Use this when the question is about scaling an LLM API, handling a traffic spike, or keeping a RAG system alive when dependencies fail.

"I would start at the boundary and move inward. Traffic enters through an API gateway that handles auth, request validation, tenant metadata, and coarse routing. Before any GPU work, I would enforce token-aware rate limits and admission control: requests per minute, tokens per minute, max context, max output, concurrency, and spend caps. Then I would cache safe repeated work such as embeddings, retrieval results, prompt prefixes, or deterministic responses. Requests that need inference go through a router/load balancer that understands active sequences, queue depth, KV-cache pressure, model version, and estimated token cost. Synchronous traffic gets strict latency budgets; document processing, batch summarization, evals, and backfills go through queues and worker pools. Circuit breakers isolate failing dependencies like vector stores or model providers, and fallbacks define whether to degrade, retry, or return a clear unavailable response. Autoscaling uses GPU-aware metrics and predictive schedules where traffic is predictable. Observability reports latency, queueing, token volume, cache hit rate, fallback rate, error rate, and cost by route and tenant."

This template works because it shows that production AI scaling is not just "add more GPUs." The system must control admission, avoid duplicate work, isolate failures, route variable-cost requests, and scale on the right metrics.

## 13.3 Enterprise Agent Platform Template

"I would build a shared platform with an API gateway, auth layer, orchestration service, model gateway, tool registry, retrieval service, workflow engine, and observability/eval pipeline. Each agent would be a versioned configuration over prompts, tools, policies, model routes, and eval suites. I would enforce permissions at retrieval and tool execution, not just in the prompt. For rollout, I would use tenant flags, shadow mode, canaries, and rollback of prompts, models, and tool policies independently."

## 13.4 Coding Assistant Template

"I would start with a context engine over the repository: symbols, files, recent edits, diagnostics, terminal output, and user intent. The assistant would produce patch-style edits, run tools in a sandbox, and keep traces of context, commands, and diffs. I would evaluate it using task completion, test pass rate, edit minimality, and unsafe command rate. The main tradeoff is context depth versus latency."

## 13.5 Customer Support Automation Template

"I would separate grounded answer generation from action execution. Retrieval would pull policy docs, account data, and prior cases with provenance. The model would draft answers and recommend actions, while deterministic policy checks and human review gate refunds or account mutations. I would monitor resolution rate, reopen rate, escalation rate, policy violations, and cost per resolved ticket."

## 13.6 Research Copilot Template

"I would design around evidence provenance. Search and ingestion produce source objects with metadata. Retrieval and reranking select evidence. The model synthesizes with citations, and validation checks that claims are supported by retrieved sources. Feedback on source usefulness and claim correctness feeds evals and ranking improvements."

## 13.7 Workflow Automation Template

"I would not run the whole workflow inside one agent loop. I would use a durable workflow engine with explicit steps, checkpoints, retries, idempotency keys, and approval states. The model helps interpret unstructured inputs and choose next steps, but deterministic code owns state transitions and high-risk action authorization."

## 13.8 Debugging Template

When asked how to debug a production failure:

1. Identify the failing user-visible behavior.
2. Pull traces for bad and good examples.
3. Compare request classification, retrieval, context assembly, model output, validation, tool calls, and final response.
4. Locate the first divergence.
5. Check whether it is a data, prompt, model, tool, policy, or orchestration issue.
6. Add an eval case before changing the system.
7. Roll out the fix behind a flag and monitor.

This is much stronger than saying "I would inspect logs."

---

# 14. Takeaways

Top-layer AI system design is composition under uncertainty.

The model is one component. The product behavior comes from context construction, retrieval, tool orchestration, state management, safety gates, eval loops, rollout controls, and observability.

The best design answers are operational. They explain who can do what, what data the model sees, how actions are approved, how failures are contained, how regressions are detected, and how the system improves.

The examples directory includes both architecture walkthroughs and a small runnable request-pipeline sketch:

* [`examples/architecture_sketch.md`](examples/architecture_sketch.html)
* [`examples/request_lifecycle.md`](examples/request_lifecycle.html)
* [`examples/failure_debugging_walkthrough.md`](examples/failure_debugging_walkthrough.html)
* [`examples/product_specific_design.md`](examples/product_specific_design.html)
* [`examples/request_pipeline.py`](examples/request_pipeline.py)

If you remember one sentence:

Design AI systems so uncertain reasoning is bounded by deterministic interfaces, permissioned data access, observable execution, and continuous evaluation.

---

# 15. Bridge to Advanced Topics

Chapter 7 composes the previous layers into complete systems. The next layer asks how strong candidates differentiate beyond standard production design.

Advanced topics include synthetic data, simulation, verifier models, reasoning-time search, test-time compute, interpretability, and systems optimization. These techniques can improve quality, but they also change cost, evaluation, and operational risk.

The bridge is:

System design tells you where the bottleneck is. Advanced techniques give you additional levers once the ordinary architecture is already clear.

[Chapter 13](../chapter_13/guide.html) adds the infrastructure depth behind system-design answers. For high-concurrency LLM APIs and agent platforms, do not stop at "scale horizontally." Explain token-aware routing, queueing, prefill/decode split, KV-cache pressure, long-context isolation, GPU pool placement, and autoscaling signals.
