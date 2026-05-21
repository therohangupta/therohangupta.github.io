---
layout: page
title: "Chapter 3: Agents (Core Product Layer)"
guide_type: chapter
---

Agents are the layer where LLMs become product actors.

Chapter 0 gave the primitives for probability, optimization, information flow, and decision-making. Chapter 1 showed how to control an LLM at runtime. Chapter 2 introduced retrieval and memory as external context. This chapter composes those pieces into systems that can plan, call tools, observe results, update state, and decide what to do next.

The interview signal is not "can you name agent frameworks." It is:

* can you define the control loop?
* can you bound the action space?
* can you explain how errors compound over time?
* can you decide when an autonomous workflow is worse than a guided workflow?
* can you design the operational guardrails that make the system safe to ship?

---

## Table of Contents

- TOC
{:toc}

---

# 1. The Core Mental Model

An agent is a controlled loop:

```text
state -> decide -> act -> observe -> update state -> stop or continue
```

The LLM is usually the decision component, not the entire system. The agent also needs state, tools, policies, budgets, validators, queues, logs, permissions, and stopping rules.

A useful way to describe an agent is:

```text
Agent = policy + state + tools + environment + control loop
```

Where:

* **policy** decides what action to take
* **state** records what the system currently knows
* **tools** let the agent affect the world
* **environment** returns observations
* **control loop** decides whether to continue, retry, escalate, or stop

This makes agents look less like magic and more like a production control system with an LLM inside it.

---

# 2. Purpose: Why Agents Exist

Agents exist because many useful product tasks are not single-turn text transformations.

Examples:

* answering a support ticket may require reading account data, checking logs, drafting a reply, and escalating if confidence is low
* fixing a code issue may require inspecting files, editing code, running tests, and revising based on failures
* booking travel may require searching options, comparing constraints, asking for approval, and executing a purchase
* researching a company may require search, extraction, synthesis, citation checking, and report generation

The common structure is sequential decision-making under uncertainty. The system does not know all required steps in advance. It must choose actions based on intermediate observations.

Agents are useful when:

* the task has multiple dependent steps
* the system needs tools or external state
* the correct path depends on observations
* partial progress can be evaluated
* the action space can be bounded
* failures can be detected and contained

Agents are not automatically better than simple workflows. They add latency, cost, observability burden, safety risk, and failure surface area. In a good product design, "agentic" means "adaptive control loop," not "the model can do anything."

---

# 3. Core Primitives

## 3.1 State

State is the agent's working representation of the task.

It can include:

* user goal
* task constraints
* conversation history
* retrieved documents
* tool outputs
* current plan
* completed steps
* pending approvals
* budget usage
* confidence estimates
* error history

State should be explicit when correctness matters. If all state lives only in the prompt, it becomes hard to validate, resume, debug, or enforce invariants.

Good agent state is typed, inspectable, and small enough to keep signal high. The state object is the product equivalent of the Markov state in a decision process: it should contain enough information to choose the next action without dragging along irrelevant noise.

## 3.2 Actions

An action is something the agent can choose.

Examples:

* call a search tool
* retrieve a document
* query a database
* write a draft
* edit a file
* send an email
* request human approval
* stop with a final answer

The action space should be bounded. A support agent should not have the same tools as a finance agent. A read-only research agent should not have write access. A production agent should not be able to execute arbitrary shell commands unless the sandbox and approval model are designed for it.

The smaller and more typed the action space, the easier the system is to evaluate.

## 3.3 Observations

An observation is the result of an action.

Examples:

* search results
* API response
* database row
* test output
* error message
* user approval or rejection
* timeout

Observations are not automatically truth. Tool outputs can be stale, malformed, partial, or adversarial. A robust agent treats observations as inputs to validate, not facts to blindly absorb.

## 3.4 Transitions

A transition updates state after an action and observation.

```text
next_state = transition(previous_state, action, observation)
```

This is where the system records progress, errors, budget usage, and new constraints. In a free-form loop, the transition may be implicit in the prompt. In a production agent, transitions should often be explicit code so the system can enforce invariants.

Examples:

* after a failed API call, increment retry count
* after a successful draft, mark draft as ready for review
* after human rejection, store feedback and move back to revision
* after spending too many tokens, stop or summarize state

## 3.5 Stopping Rules

A stopping rule decides when the loop ends.

Common stopping rules:

* final answer generated
* plan completed
* confidence threshold reached
* budget exhausted
* max steps reached
* repeated failure detected
* human approval required
* unsafe action requested

Stopping rules are not an implementation detail. They are part of the product contract. Without them, the system can loop forever, spend unbounded money, or take actions after the user expected it to stop.

## 3.6 Budgets

Budgets limit resource use and autonomy.

Useful budgets:

* token budget
* model-call budget
* wall-clock budget
* tool-call budget
* money budget
* retry budget
* side-effect budget
* risk budget

Budgets turn agent design into constrained optimization. The agent is not simply trying to solve the task; it is trying to solve the task within cost, latency, safety, and reliability limits.

## 3.7 Planning

Planning chooses a sequence or partial order of steps.

Plans can be:

* implicit, where the model reasons step by step inside one loop
* explicit, where the system asks for a structured plan before execution
* hierarchical, where a high-level plan decomposes into subplans
* dynamic, where the plan is revised after observations

Plans are useful because they expose intent before side effects happen. They also make it easier to validate whether the agent is about to do something irrelevant, unsafe, or too expensive.

## 3.8 Execution

Execution turns planned steps into tool calls and state transitions.

The execution layer is where production systems need the most ordinary engineering:

* idempotency keys
* retries with backoff
* timeout handling
* concurrency control
* authorization
* observability
* cancellation
* audit logs
* rollback or compensation

An agent with weak execution semantics is just a fluent source of side effects.

---

# 4. Composition: From Primitives to an Agent

A production agent usually has these layers:

```text
User goal
  -> task policy
  -> state representation
  -> planner or next-action selector
  -> tool router
  -> execution layer
  -> observation parser
  -> state transition
  -> validator / guardrail
  -> stopping rule
```

The important design question is where intelligence lives.

Some systems put most intelligence in the LLM prompt. The model reads the full state, decides what to do, calls tools, and repeats. This is flexible but hard to bound.

Other systems put intelligence in explicit workflow code. The model only fills in narrow decisions, such as "classify this ticket" or "draft this reply." This is less flexible but more reliable.

Most useful products sit in the middle: deterministic workflow for product-critical structure, LLM decisions for ambiguous language and judgment-heavy steps, and human approval for high-risk transitions.

---

# 5. Agent Patterns

## 5.1 ReAct

ReAct combines reasoning and acting:

```text
Thought -> Action -> Observation -> Thought -> Action -> Observation -> Final
```

The pattern is useful because the model can choose tools based on intermediate evidence. It is especially natural for search, research, debugging, and tool-using assistants.

The tradeoff is that ReAct loops are easy to over-trust. If the first observation is bad, the model may rationalize around it. If the tool result is noisy, the trajectory can drift. In production, ReAct needs step limits, tool schemas, observation validation, and logging.

## 5.2 Planner / Executor

A planner/executor separates intent from action.

```text
planner: produce structured plan
validator: check plan
executor: run steps
observer: report results
planner: revise if needed
```

This helps when actions are expensive or risky. The plan can be reviewed before execution, and the executor can be more deterministic than the planner.

The tradeoff is plan brittleness. A plan generated before tool observations may be wrong. Good planner/executor systems allow controlled replanning instead of blindly following a stale plan.

## 5.3 Reflect-and-Retry

Reflect-and-retry asks the model or a verifier to critique an output or trajectory, then revise.

This is useful for:

* code generation
* structured extraction
* long-form writing
* reasoning tasks with checkable constraints
* tool-call repair

The key is that reflection should be grounded in evidence. "Think again" is weaker than "compare the output against this schema, these tests, and these source documents."

The tradeoff is cost. Reflection adds more model calls and can create false confidence if the same model critiques its own mistake without new information.

## 5.4 Supervisor / Worker

A supervisor/worker pattern uses one component to route, coordinate, or verify the work of other components.

Examples:

* supervisor routes a support ticket to billing, technical, or account worker
* supervisor decomposes a research task into search, extraction, and synthesis workers
* supervisor checks whether a worker result is sufficient before final response

This pattern is useful when subtasks require different prompts, tools, permissions, or models.

The tradeoff is coordination overhead. Every handoff adds latency, state translation risk, and another place where errors can be hidden.

## 5.5 Hierarchical Agents

Hierarchical agents decompose a large task into levels.

```text
goal
  -> milestones
    -> subtasks
      -> tool actions
```

This is useful for long-horizon work such as software projects, research reports, and operations workflows.

The risk is that high-level mistakes propagate downward. If the top-level decomposition is wrong, lower-level agents may produce impressive but irrelevant work. Hierarchical agents need milestone checks and explicit acceptance criteria.

## 5.6 Multi-Agent Systems

Multi-agent systems use multiple agents that may collaborate, debate, specialize, or check each other.

Common uses:

* specialist agents for different domains
* critic agents for review
* debate-style answer comparison
* parallel search over alternative approaches
* role-based workflow simulation

The benefit is diversity of search. The cost is operational complexity. Multi-agent systems can multiply token spend, make debugging harder, and create the illusion of consensus when agents share the same model biases.

Use multi-agent designs when specialization or parallel exploration clearly pays for the coordination cost.

## 5.7 Event-Driven Agents

Event-driven agents wake up in response to events:

* webhook received
* ticket created
* build failed
* document changed
* customer replied
* scheduled job fired

This pattern fits production systems because it integrates with queues, task runners, retries, and observability. Instead of one long-running loop, the agent advances state across durable events.

The tradeoff is state management. The agent must resume safely, handle duplicate events, and remain idempotent.

---

# 6. Common Technologies and Implementation Patterns

## 6.1 LangGraph

LangGraph is useful when an agent is better represented as a graph of states and transitions than as a single free-form loop. Nodes represent steps, edges represent routing, and state is passed through the graph.

The practical value is control. You can make loops explicit, limit transitions, persist state, and inspect where execution went.

Use it when:

* the workflow has branches or loops
* state needs to be durable
* you want explicit control over agent transitions
* debugging the path matters

## 6.2 MCP

The Model Context Protocol standardizes how models and agents connect to tools and external context. Its importance is not that it makes agents smarter. It makes tool access more uniform and composable.

In agent design, MCP is part of the tool boundary:

* what tools exist?
* what schemas describe them?
* what permissions do they have?
* what context can they expose?
* what side effects can they perform?

The more powerful the MCP server, the more important sandboxing, auth, logging, and approval become.

## 6.3 OpenAI Tools / Function Calling

Tool calling gives the model a structured way to request actions.

This is useful because the system can expose a typed action space instead of asking the model to write arbitrary text commands.

Good function schemas are:

* small
* specific
* typed
* validated
* permission-aware
* designed around product actions, not internal implementation details

Function calling does not guarantee correct tool use. It only gives the system a better interface for constraining and validating actions.

## 6.4 AutoGen and CrewAI

AutoGen and CrewAI are commonly used for multi-agent workflows, role-based collaboration, and agent teams. They are useful for prototyping coordination patterns such as researcher/writer/reviewer or planner/coder/tester.

The production question is whether the framework's abstractions match the reliability boundary you need. For demos, role-based agents can be fast to build. For production, you still need explicit state, permissions, evaluation, retry logic, observability, and cost control.

## 6.5 DSPy

DSPy is relevant when prompt and module behavior should be optimized programmatically instead of hand-tuned. It is less about autonomous tool loops and more about treating LLM calls as optimizable modules in a pipeline.

For agents, DSPy can help optimize subcomponents such as:

* classification prompts
* extraction modules
* rerankers
* plan generators
* verifiers

The connection to Chapter 0 is direct: instead of manually guessing prompts, you define objectives and let examples shape the system.

## 6.6 Queues and Task Runners

Agents that do real work often need durable execution.

Common choices:

* Celery
* Sidekiq
* BullMQ
* Temporal
* Airflow or Dagster for scheduled/data workflows
* cloud queues such as SQS, Pub/Sub, or RabbitMQ

Queues matter because agent steps can be slow, flaky, or asynchronous. A model call may time out. A third-party API may rate-limit. A human approval may take hours. Durable orchestration prevents the whole workflow from depending on one in-memory process.

## 6.7 Sandboxed Execution

Sandboxing controls what tool execution can affect.

Examples:

* run code in a container
* mount a temporary filesystem
* restrict network access
* use read-only credentials
* require approval for writes
* isolate browser sessions
* apply per-tool permissions

Sandboxing is especially important when agents can execute code, browse the web, modify files, send messages, or transact money.

---

# 7. Real Implementation Details

## 7.1 State Machines vs Free-Form Loops

A free-form loop gives the model broad control:

```text
while not done:
  ask model what to do
  run tool
  append observation
```

This is easy to build and good for exploration. It is also hard to reason about.

A state machine defines allowed states and transitions:

```text
drafting -> validation -> approval -> execution -> done
```

This is less flexible but easier to test, observe, and secure.

The production default should be: use explicit state machines for product-critical flows, and use free-form loops only inside bounded steps where the blast radius is small.

## 7.2 Async Execution

Agent work often outlives a request/response cycle.

Async execution is needed when:

* tool calls are slow
* tasks can be queued
* humans may approve later
* jobs need retries
* many agents run concurrently
* streaming progress matters

The agent should expose job status, cancellation, partial results, and error states. Otherwise users cannot tell whether the system is working, stuck, or unsafe.

## 7.3 Sandboxing and Permissions

Tools should be permissioned by risk.

Example tiers:

* read-only search
* read-only internal data
* draft-only write actions
* reversible writes
* irreversible writes
* external side effects such as email, purchases, or production deploys

Higher tiers need stronger controls: approvals, audit logs, rate limits, policy checks, and possibly human review.

## 7.4 Idempotency

Agents retry. Networks fail. Users refresh pages. Queues redeliver messages.

Any side-effecting action should have an idempotency strategy:

* idempotency keys
* dedupe tables
* "already completed" checks
* deterministic output paths
* transactional writes
* compensation steps for reversible actions

Without idempotency, an agent can send the same email twice, create duplicate tickets, charge a card twice, or apply the same code change repeatedly.

## 7.5 Cancellation

Cancellation is a product requirement for long-running agents.

The system should define:

* what happens to in-flight model calls
* what happens to queued steps
* what happens to partial side effects
* what state is shown to the user
* whether the workflow can resume later

Cancellation is easiest when execution is divided into steps with clear boundaries. It is hardest when the agent is one unstructured process with hidden state.

## 7.6 Budgets and Rate Limits

Budgets prevent runaway behavior; rate limits protect shared systems.

Useful implementation patterns:

* per-task max steps
* per-user daily spend limits
* per-tool call limits
* per-model token limits
* retry caps
* circuit breakers
* queue concurrency limits
* backpressure when downstream services are unhealthy

The agent should know when a budget is exhausted and respond gracefully: summarize partial progress, ask for permission, or stop with a clear reason.

## 7.7 Parallelization vs Sequential Execution

Parallel execution reduces latency when steps are independent.

Good parallel candidates:

* searching multiple sources
* asking multiple extractors to process separate documents
* generating alternative plans
* running independent checks

Sequential execution is better when each step depends on the previous observation:

* debugging a failing test
* form-filling with validation
* negotiation with a user
* operations workflows with side effects

The interview framing is simple: parallelize independent uncertainty reduction; serialize dependent decisions and side effects.

## 7.8 Plan Validation

Plan validation checks whether the agent's intended trajectory is acceptable before execution.

Validation can check:

* tool permissions
* missing prerequisites
* cost estimate
* unsafe actions
* irrelevant steps
* user constraints
* required approvals
* expected outputs

Plan validation is especially important because early mistakes cascade. A bad first step can send the agent into the wrong part of the state space, where every later step looks locally reasonable but globally wrong.

---

# 8. Tradeoffs

## 8.1 Latency

Agents are slower than single prompts because they make multiple model calls and tool calls. Parallelism can help, but only when steps are independent.

Low-latency products should prefer narrow workflows, smaller models for routing, caching, and streaming progress.

Every loop iteration may add model latency, tool latency, retrieval latency, validation latency, and queueing. The painful cases are dependent plans where step N cannot start until step N-1 completes.

Good designs define when to stop early, when to return a partial result, and when to ask a human rather than spending more model calls.

## 8.2 Cost

Agent cost grows with trajectory length:

```text
total cost = sum(model calls + tool calls + retries + verification + human review)
```

Reflection, multi-agent debate, and large context windows can improve quality but quickly multiply spend. Budgets and evaluation are the only honest way to know whether the quality gain is worth it.

## 8.3 Reliability

Every loop iteration is another chance for error. Reliability comes from narrowing the action space, validating observations, using typed state, and measuring trajectories.

The system should not depend on the model being wise at every step. It should make bad steps detectable and recoverable.

## 8.4 Correctness

Agents are strong at ambiguous, language-heavy work and weak at hidden invariants. If correctness is defined by strict rules, encode those rules in code or validation.

Use the model for judgment. Use software for invariants.

An agent can make a locally reasonable decision at each step and still end in the wrong state because errors compound. A bad retrieval result can cause a bad tool call; a bad tool observation can cause a bad plan revision; a bad plan revision can trigger an unsafe action.

Correctness therefore needs checkpoints: tool argument validation, source grounding, state invariants, human approval for irreversible actions, and evaluation of full trajectories rather than only final answers.

## 8.5 Scaling

Scaling agents is harder than scaling stateless calls because long-running work consumes queues, model capacity, tool capacity, and human review bandwidth.

Scaling requires:

* queueing
* concurrency limits
* task prioritization
* load shedding
* model fallback tiers
* observability by step and tool

## 8.6 Operational Complexity

Agents increase the number of things operators must understand:

* why did it choose this action?
* what state did it see?
* what tools did it call?
* what did it ignore?
* what budget did it spend?
* why did it stop?

If you cannot answer those questions from logs, the agent is not production-ready.

---

# 9. Failure Modes

## 9.1 Bad First-Step Cascades

The first action often sets the trajectory. A bad search query, wrong classification, or flawed plan can push the agent into a state where later decisions are built on weak evidence.

Mitigation:

* validate plans before execution
* use retrieval quality checks
* require clarification when the goal is ambiguous
* compare multiple first-step options for high-value tasks

## 9.2 Trajectory Collapse

Trajectory collapse happens when the agent narrows too early and stops exploring alternatives. It may repeatedly reinforce one mistaken interpretation.

Mitigation:

* preserve uncertainty in state
* ask for alternative hypotheses
* use verifier checks
* branch search for high-risk tasks

## 9.3 Tool Feedback Loops

An agent can call a tool, misread the result, call another tool based on that mistake, then continue amplifying the error.

Mitigation:

* parse observations into typed structures
* detect repeated similar tool calls
* cap retries
* summarize evidence separately from conclusions

## 9.4 Runaway Costs

Agents can spend money through long loops, retries, large contexts, or multi-agent expansion.

Mitigation:

* hard budgets
* cost estimates before execution
* stop reasons
* cheaper models for low-risk steps
* user approval before expensive continuation

## 9.5 Duplicated Side Effects

Retries and resumptions can duplicate external actions.

Mitigation:

* idempotency keys
* side-effect logs
* dedupe checks
* approval records
* transactional boundaries

## 9.6 Memory Drift

Memory drift occurs when the agent stores summaries, preferences, or beliefs that become stale or wrong.

Mitigation:

* attach provenance to memories
* expire or revalidate memory
* separate facts from preferences
* avoid writing memory after low-confidence interactions

## 9.7 Infinite Loops

The agent may keep retrying, searching, reflecting, or asking itself to continue.

Mitigation:

* max steps
* repeated-state detection
* retry caps
* progress checks
* explicit "unable to complete" terminal states

## 9.8 Over-Autonomy

Over-autonomy means the agent has more freedom than the product, user, or organization can safely support.

Symptoms:

* broad tools with unclear permissions
* irreversible actions without approval
* vague success criteria
* hidden long-running work
* no audit trail

Mitigation is product design, not just prompt design: bounded action spaces, human-in-the-loop checkpoints, clear user consent, and explicit escalation paths.

---

# 10. Product Framing

## 10.1 Why Agents Are Useful

Agents create leverage when users want outcomes, not individual tool operations.

A user does not want to manually search logs, compare docs, draft a fix, and run checks. They want the issue investigated. The agent is valuable when it can coordinate the steps while keeping the user informed and in control.

## 10.2 When Not to Use Agents

Do not use an agent when:

* a deterministic workflow is sufficient
* the task is single-step
* the action space cannot be bounded
* failures are hard to detect
* side effects are high-risk and irreversible
* latency must be very low
* the user needs predictable behavior more than flexibility

Many "agent" products should start as guided workflows with LLM-assisted steps.

## 10.3 Guided Workflow vs Autonomous Agent

A guided workflow has predefined stages and uses the LLM inside them.

An autonomous agent chooses more of the path itself.

Guided workflows are better when the product has known structure, compliance requirements, or high cost of mistakes. Autonomous agents are better when the task space is open-ended and exploration is valuable.

The most shippable design is often:

```text
guided workflow + bounded agentic substeps + human approval for high-risk actions
```

## 10.4 Human-in-the-Loop

Human-in-the-loop is not a failure of automation. It is a control boundary.

Use human checkpoints when:

* confidence is low
* cost is high
* action is irreversible
* policy requires approval
* user intent is ambiguous
* the system enters an unknown state

The agent should make review easy by presenting the plan, evidence, expected side effects, and alternatives.

---

# 11. What to Say in an Interview

A strong answer frames agents as bounded decision systems:

> I would model the agent as a loop over state, actions, observations, and transitions. The LLM can choose actions, but the product defines the allowed action space, budgets, stopping rules, and approval boundaries.

Then add the implementation detail:

> For production, I would avoid a completely free-form loop for high-risk workflows. I would use an explicit state machine or graph, typed tool schemas, idempotent execution, plan validation, logging, and step-level evaluation.

Then discuss the tradeoff:

> Agents are useful when the path depends on observations, but they are more expensive and less predictable than deterministic workflows. I would choose autonomy only where adaptivity is worth the extra latency, cost, and failure surface.

Finally, connect to safety:

> Safe autonomy comes from bounded action spaces, budgets, validation, sandboxing, and human approval for risky side effects. The goal is not to let the model do anything; it is to let it make useful decisions inside a controlled system.

---

# 12. Chapter Takeaways

* An agent is a controlled loop over state, actions, observations, transitions, and stopping rules.
* The LLM is usually the policy component, not the whole system.
* State should be explicit, typed, inspectable, and small enough to preserve signal.
* Actions should be bounded by product permissions and safety requirements.
* Planning is useful because it exposes intent before execution.
* Execution needs ordinary distributed systems engineering: idempotency, retries, cancellation, queues, logs, and rate limits.
* Most production agents should combine deterministic workflow structure with bounded LLM-driven decisions.
* The main failure pattern is compounding error across steps.
* Safe autonomy is designed through constraints, not hoped for through prompting.

---

# 13. Bridge to Chapter 4

Agents need evaluation more than single-prompt systems because quality is trajectory-level, not just output-level.

It is not enough to ask whether the final answer looked good. You need to know whether the agent chose the right tools, used evidence correctly, respected budgets, stopped for the right reason, avoided unsafe actions, and recovered from failures.

This makes evaluation harder in several ways:

* trajectories are variable-length, so you cannot just compare two strings
* intermediate decisions matter, not only the final output
* cost, latency, and tool-call counts are part of quality
* failure modes are combinatorial across steps
* regression detection must cover new behavior paths, not just old golden answers

Chapter 4 turns this into an evaluation problem: how to measure agent behavior, catch regressions, compare trajectories, and decide whether a system is actually reliable enough to ship. Without strong evaluation, agent improvements are guesses — you cannot tell whether a change to the planner, tool set, or stopping rule actually helped across the distribution of real tasks.
