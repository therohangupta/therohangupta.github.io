---
layout: page
title: "Chapter 1: LLM Engineering (Prompting, Tools, Control, Reliability, Agents)"
guide_type: chapter
---

This chapter turns the LLM from a probabilistic text model into a usable system component.

Chapter 0 answered: "How does the model work?"

This chapter answers: "How do I make it useful, reliable, debuggable, and cheap enough to run?"

The interview angle here is usually not "can you recite prompt tips." It is:

* can you shape model behavior without changing weights?
* can you build a tool-using system that does not collapse under edge cases?
* can you structure outputs, state, retries, evaluation, and fallbacks?
* can you explain why your system will fail in production before it fails?

---

## Table of Contents

- TOC
{:toc}

---

# 1. The Core Mental Model

Treat an LLM as a conditional distribution:

$$P(y \mid x)$$

LLM engineering is the art of controlling:

* $$x$$, the input context
* the allowed output space
* the sequence of actions over time
* the feedback loop that improves the system

In other words:

Prompting = shape the input
Sampling = shape the randomness
Tools = extend capability
Memory = preserve useful state
Orchestration = control the loop
Evaluation = measure and improve

That is the entire chapter in one sentence.

---

# 2. Prompting as Behavior Control

Prompting is not just writing nicer instructions. It is a method for steering the conditional distribution of outputs without changing model weights.

## 2.1 Prompt as Interface

A prompt usually has four parts:

* instruction
* context
* examples
* output format

These parts are not equivalent.

### Instruction

Tells the model what role it should play.

Example:

* summarize this document
* extract entities
* write a JSON object
* compare two options

### Context

Supplies the data the model should operate on.

Examples:

* a document
* a conversation history
* retrieved passages
* tool outputs

### Examples

Show the model the desired transformation.

This is often the strongest way to shape behavior when a task is ambiguous.

### Output format

Constrain the answer so your software can consume it.

Examples:

* JSON
* YAML
* bullet list
* short answer only
* one line per item

## 2.2 Why Prompting Works

Prompting works because models perform in-context pattern matching.

The prompt gives the model a temporary local task distribution. The model then predicts what an appropriate continuation looks like under that local distribution.

The important idea is:

* the model is not being rewritten
* the prompt changes what the model thinks the task is

## 2.3 Prompting as Soft Programming

A good prompt is like a soft program:

* not deterministic
* not perfect
* but often enough to shape behavior toward a useful region

That is why prompts are powerful but fragile.

## 2.4 Failure Modes of Prompting

Prompting breaks in predictable ways:

* vague instructions lead to vague answers
* conflicting instructions lead to unstable behavior
* too many instructions overwhelm the model
* examples that are too weird distort behavior
* hidden assumptions make the model answer the wrong question

A strong interviewer answer should mention that prompt quality is partly about reducing ambiguity, not just being verbose.

---

# 3. Prompt Taxonomy

There are several distinct prompting patterns. You should know all of them.

## 3.1 Zero-shot Prompting

Ask the task directly without examples.

Use when:

* the task is simple
* the model already knows the transformation
* you want low prompt overhead

Tradeoff:

* lower prompt cost
* more variance

## 3.2 Few-shot Prompting

Provide examples of input-output pairs.

Use when:

* the task is subtle
* the output format matters
* you want the model to infer hidden style or policy

Why it works:

* examples act like in-context demonstrations
* the model infers the latent task from the examples

## 3.3 Instruction Prompting

Give a precise natural-language specification.

Use when:

* task is clearly defined
* you can describe constraints directly

## 3.4 Role Prompting

Assign a role.

Examples:

* you are a careful data extractor
* you are a skeptical reviewer
* you are a senior software engineer

Role prompts are often a shorthand for changing style and priority structure.

## 3.5 Decomposition Prompting

Break a task into substeps.

Example:

* identify entities
* classify them
* then produce final output

Useful when the task is too hard to do in one pass.

## 3.6 Self-consistency / Multi-sample Prompting

Generate multiple candidate answers and choose the most consistent one.

This is a simple but powerful way to reduce randomness.

## 3.7 Critique and Revise

Ask the model to generate, then critique its own answer, then rewrite.

This can improve quality when the model is capable of self-correction.

---

# 4. Prompt Design Principles

This is where a lot of practical engineering lives.

## 4.1 Be Explicit About the Goal

Do not assume the model knows what optimization criterion you care about.

Bad:

* make this better

Better:

* make this shorter while preserving all factual details and action items

## 4.2 Put Constraints in Priority Order

If a prompt has multiple constraints, rank them.

Example:

1. output valid JSON
2. do not invent facts
3. keep each field under 30 words

## 4.3 Separate Facts From Instructions

If context and instructions are mixed together, the model can confuse them.

A clean prompt usually makes the boundaries obvious.

## 4.4 Reduce Ambiguity

Ambiguous instructions force the model to guess latent intent.

If the task has multiple plausible interpretations, either specify the preference or give a decision rule.

## 4.5 Use Examples When Rules Are Hard to State

Some tasks are easier to demonstrate than to define.

Examples are especially useful for:

* extraction
* normalization
* formatting
* classification edge cases
* style imitation

---

# 5. Sampling and Decoding Control

Prompting controls what the model sees. Sampling controls how the model chooses among plausible outputs.

## 5.1 Greedy Decoding

Always choose the highest probability next token.

Pros:

* deterministic
* cheap

Cons:

* can be repetitive
* can get stuck in low-quality local choices

## 5.2 Temperature

Temperature changes how peaked the next-token distribution is.

* low temperature: more conservative
* high temperature: more diverse

Conceptually:

* low temperature sharpens the distribution
* high temperature flattens it

## 5.3 Top-k Sampling

Restrict sampling to the k most likely tokens.

Useful when you want diversity without letting the model wander too far.

## 5.4 Top-p Sampling

Restrict sampling to the smallest set of tokens whose probability mass exceeds p.

This adapts to the shape of the distribution.

## 5.5 Beam Search

Search over several candidate continuations.

Useful in some structured generation settings, but often produces bland answers for open-ended text.

## 5.6 Decoding Tradeoff Summary

* deterministic decoding is easier to debug
* stochastic decoding can improve creativity and coverage
* production systems often want a constrained form of stochasticity, not pure randomness

---

# 6. Structured Outputs

This is one of the most important applied engineering topics.

The LLM may be good at language, but your system often needs a machine-readable object.

## 6.1 Why Structured Outputs Matter

Free-form text is hard to consume.

Systems usually need:

* JSON objects
* schema-constrained records
* function arguments
* typed labels
* lists of extracted fields

Structured outputs reduce entropy in the response space and make downstream automation much safer.

## 6.2 Common Structured Output Methods

### A. Prompt-only formatting

You ask for JSON in the prompt.

This is simple but brittle.

### B. Schema-guided generation

The tool/runtime enforces a schema.

This is much more reliable.

### C. Post-processing

You parse and validate after generation.

This is necessary even if you have schema-guided decoding.

## 6.3 Common Output Shapes

* single object
* list of objects
* classification label
* key-value map
* action plan with steps
* tool call arguments

## 6.4 Failure Modes

* invalid JSON
* extra commentary outside the schema
* missing required fields
* hallucinated values
* field type mismatch

## 6.5 Good Interview Framing

If asked how to build reliable structured generation, say:

* constrain the output format as much as possible
* validate the output
* repair or retry when parsing fails
* use smaller, narrower schemas
* never trust raw free-form text when a typed object is needed

## 6.6 Concrete Implementation Stack

In a real application, structured output usually becomes a small pipeline:

```text
prompt template
  -> model call with schema / tool definition
  -> JSON parser
  -> schema validator
  -> business-rule validator
  -> retry / repair / fallback
  -> typed object used by downstream code
```

Common choices:

* **JSON Schema / Pydantic / Zod** for type validation.
* **OpenAI structured outputs or tool calling** when the runtime can constrain generation.
* **Instructor, Guardrails, LangChain output parsers, or custom validators** when the team wants a wrapper around parsing and retries.
* **Strict enums and small schemas** for classification, routing, and extraction.
* **Business-rule validators** for constraints the schema cannot express, such as "refund amount must be less than original payment."

The important implementation detail is that schema validity is not the same as correctness. This JSON can be valid and still wrong:

```json
{"priority": "low", "requires_human_review": false}
```

For a medical, financial, legal, or account-access workflow, the system also needs policy checks, grounding checks, and sometimes human review. In interviews, call out this split:

```text
syntax validity != semantic validity != business safety
```

### Example: extraction flow

A robust extraction service might do:

1. build a prompt with clear field definitions,
2. call the model with a schema,
3. validate required fields and types,
4. check extracted values against source spans,
5. retry once with the validation error,
6. route to human review if the second attempt fails.

That is much more realistic than "ask the model for JSON."

---

# 7. Tool Use

Tool use is how LLM systems gain capabilities they do not have intrinsically.

## 7.1 Why Tools Are Needed

LLMs are weak at:

* exact arithmetic
* up-to-date facts
* deterministic side effects
* persistent state changes
* reliable multi-step workflows

Tools solve this by moving certain operations outside the model.

## 7.2 Tool Abstraction

A tool is a function from input to output.

Examples:

* search(query)
* retrieve(doc_id)
* calculate(expression)
* send_email(to, subject, body)
* query_database(sql)

The model decides when to call a tool and what arguments to pass.

## 7.3 Tool Calling Loop

The basic loop is:

1. model proposes an action
2. runtime executes the tool
3. tool result comes back
4. model uses result to continue

This is the basis of most agent systems.

## 7.4 Tool Use Patterns

### Lookup pattern

Ask a tool for missing information.

### Action pattern

Ask a tool to do something in the world.

### Verify pattern

Use a tool to check the model’s own answer.

### Chain pattern

Use multiple tools in sequence.

## 7.5 Tool Use Failure Modes

* hallucinated tool names
* wrong arguments
* wrong ordering of calls
* tool output misread as final answer
* infinite loops
* stale cached tool results

## 7.6 Engineering Principle

Tools should be treated like external dependencies in software engineering:

* validate inputs
* handle failures
* retry carefully
* make calls idempotent when possible
* log everything

## 7.7 Concrete Tool-Calling Architecture

A production tool call is not just a function name emitted by the model. It is usually mediated by a host runtime:

```text
model proposes tool call
  -> tool registry checks name
  -> argument schema validation
  -> authorization / permission check
  -> idempotency key generation
  -> timeout / retry policy
  -> tool execution
  -> result normalization
  -> observation appended to context
```

Common implementation choices:

* **Tool registry:** a map of allowed tool names to callable functions and schemas.
* **Argument validation:** Pydantic, Zod, JSON Schema, protobuf, or typed SDK definitions.
* **Permission layer:** user/session scopes determine which tools are available.
* **Idempotency keys:** prevent repeated writes if an agent retries.
* **Timeouts and circuit breakers:** prevent slow tools from freezing the whole workflow.
* **Result shaping:** tool outputs are summarized or normalized before being put back into the model context.
* **Tracing:** every prompt, tool call, arguments object, result, latency, and error should be logged.

The highest-signal interview move is to say that tools should be exposed as a narrow API, not as arbitrary code execution. For example, prefer:

```text
refund_order(order_id, reason_code)
```

over:

```text
run_sql("UPDATE payments ...")
```

The first gives the system a bounded action space. The second gives the model too much authority and makes validation harder.

---

# 8. Agentic Systems

Once the model can use tools, you can build an agent.

## 8.1 Agent Definition

An agent is:

LLM + state + tools + loop + stopping rule

That last part matters. Without a stopping rule, the agent may not know when to stop acting.

## 8.2 Agent Loop

A generic loop looks like this:

* observe state
* choose action
* execute action
* receive observation
* update memory/state
* decide whether to stop

## 8.3 Main Agent Architectures

### ReAct

The model alternates between reasoning and acting.

Useful when:

* the problem is open-ended
* the agent needs to gather information progressively

### Planner-executor

One component plans, another executes.

Useful when:

* you want separation of concerns
* you want to inspect plans before execution

### Reflect-and-retry

The model critiques its own result and tries again.

Useful when:

* mistakes are common but fixable
* you want self-improvement without external supervision

### Hierarchical agents

A manager agent delegates to sub-agents.

Useful when:

* the task is large
* tasks can be decomposed cleanly

## 8.4 Agent Strengths

Agents can handle:

* long workflows
* multi-step problem solving
* tool coordination
* iterative search
* stateful tasks

## 8.5 Agent Weaknesses

Agents are fragile because errors compound.

Common failure modes:

* wrong first step poisons the rest
* one bad retrieval leads to a bad plan
* memory drift accumulates over time
* loops can over-run cost and latency budgets
* the system can be overconfident in a bad trajectory

## 8.6 Practical Design Rule

Do not make an agent autonomous unless the task has:

* a clear success condition
* bounded action space
* observable intermediate results
* acceptable failure cost

If those are missing, use a guided workflow instead of a free-running agent.

---

# 9. State and Memory

State is everything the system remembers between steps.

## 9.1 Short-Term Memory

This is the current context window.

Pros:

* simple
* fast
* directly available to the model

Cons:

* limited size
* expensive to grow
* noisy if overloaded

## 9.2 Long-Term Memory

Stored outside the context window.

Examples:

* vector database
* SQL store
* event log
* profile store
* summary store

## 9.3 Memory Operations

* write: store something useful
* read: retrieve relevant prior state
* summarize: compress history
* prune: discard stale or low-value memory
* update: revise memory after new evidence

## 9.4 Memory Design Questions

Ask:

* what should be stored?
* how is it retrieved?
* when does it expire?
* how do we prevent memory from becoming clutter?
* how do we stop retrieval from adding noise?

## 9.5 Common Memory Failure Modes

* over-recall of irrelevant facts
* stale memory causing wrong behavior
* summary lossiness
* identity drift across sessions
* retrieval bias toward similar but wrong items

## 9.6 Good Memory Principle

Memory should be useful, not merely large.

More memory can reduce quality if it is not curated.

---

# 10. Retrieval-Augmented Workflows

This section overlaps with retrieval architecture, but here the focus is engineering control.

## 10.1 Why Retrieval Is Used

Retrieval helps when the model needs:

* private knowledge
* fresh knowledge
* user-specific knowledge
* long documents
* sources that should be cited or grounded

## 10.2 Retrieval Workflow

A common pipeline:

1. preprocess and chunk data
2. embed chunks
3. retrieve candidates
4. rerank candidates
5. construct context
6. generate answer
7. optionally cite or verify

## 10.3 Retrieval Failure Modes

* bad chunking
* wrong embedding model
* poor top-k selection
* missing metadata filters
* context window overload
* irrelevant retrieved text that distracts the model

## 10.4 Retrieval Is Not Magic

Retrieval only helps if the right information is inserted into context in a usable form.

If retrieval is wrong, the model can become more confused than if you had retrieved nothing.

See also: Chapter 2's retrieval chapter for chunking, metadata, reranking, and memory lifecycle; Chapter 4 for measuring retrieval quality; and Chapter 6 for the latency and cost impact of retrieval services.

---

# 11. Reliability Patterns

This is a core Applied AI interview area.

## 11.1 Decompose the Task

Instead of asking for a final answer immediately, break the problem into stages.

Examples:

* extract facts
* validate facts
* produce answer
* check answer

## 11.2 Retry

If the model fails, try again.

But retrying blindly is not enough. You need a changed condition:

* different prompt
* different temperature
* different tool result
* different subtask ordering

## 11.3 Self-consistency

Generate multiple answers and choose the most consistent or best-scoring one.

Good for tasks where one pass is noisy.

## 11.4 Verification

Use a checker.

Checker can be:

* another model
* a rules engine
* a schema validator
* a database lookup
* a unit test

## 11.5 Guardrails

Guardrails are constraints that limit failure impact.

Examples:

* allowlisted tools only
* blocked actions require approval
* schemas enforced before execution
* rate limits on repeated tool calls
* content filters for safety

## 11.6 Fallbacks

When the primary model or flow fails, fall back to something safer.

Examples:

* simpler model
* rule-based response
* no action taken
* ask for clarification

## 11.7 Why Reliability Is So Hard

Because failures can come from many layers:

* prompt ambiguity
* model hallucination
* tool errors
* retrieval noise
* stale memory
* orchestration bugs
* user behavior mismatch

A strong candidate can talk about all of these, not just the model.

---

# 12. Orchestration and Control Flow

Once the system gets beyond a single prompt, you need orchestration.

## 12.1 Common Orchestration Units

* request router
* prompt builder
* retriever
* tool executor
* validator
* state manager
* logger
* evaluator

## 12.2 Common Control Flow Patterns

### Linear flow

One step after another.

Best for simple tasks.

### Branching flow

Different paths depending on model or tool output.

Best for mixed task types.

### Looping flow

Repeat until success or budget exhaustion.

Best for search and agents.

### Parallel flow

Run multiple checks or subtasks at once.

Best for speed and robustness.

## 12.3 Important Engineering Concepts

### Idempotency

If an action is retried, it should not accidentally duplicate side effects.

### Timeouts

A tool or model call should fail fast when it hangs.

### Cancellation

If one branch succeeds, stop wasting compute on the others.

### Budgets

Cap token count, tool count, and wall-clock time.

## 12.4 Why This Matters

Without orchestration, LLM systems become expensive, hard to debug, and hard to trust.

## 12.5 Reference Implementation Pattern

A practical LLM workflow often looks like a typed service pipeline:

```text
HTTP request
  -> auth and rate limit
  -> intent classifier
  -> context builder / retriever
  -> prompt renderer
  -> model router
  -> model call
  -> validator
  -> tool executor if needed
  -> response formatter
  -> tracing + eval logging
```

Different teams implement this with different stacks:

* **Simple product workflow:** FastAPI or Node service, prompt templates in code, JSON Schema validation, OpenAI/Anthropic SDK, Postgres logs.
* **Retrieval-heavy workflow:** vector DB, reranker, prompt builder, grounded answer validator, citation checker.
* **Agent workflow:** LangGraph-style state machine, typed state object, tool registry, budget counter, human escalation node.
* **Enterprise workflow:** API gateway, queue, worker pool, audit logs, permission checks, feature flags, tracing dashboard.

The architecture should make the non-model pieces explicit. A good production answer names the components that constrain the model:

* schema,
* validator,
* tool permissions,
* retry budget,
* timeout,
* fallback,
* trace,
* eval signal.

If those are absent, the model is the whole system, and the system is hard to trust.

---

# 13. Evaluation and Measurement

You cannot improve what you cannot measure.

## 13.1 Offline Evaluation

Run the system on a fixed dataset.

Useful for:

* regressions
* comparisons
* controlled testing

## 13.2 Online Evaluation

Measure behavior in production.

Useful for:

* true user impact
* real failure rates
* latency and cost
* feedback loops

## 13.3 Evaluation Dimensions

You should evaluate at least:

* correctness
* completeness
* latency
* cost
* refusal behavior
* user satisfaction
* tool success rate
* hallucination rate

## 13.4 Synthetic Evaluation

Generate test cases automatically.

This is especially important for agents and long workflows, where manual labels are too expensive.

## 13.5 Adversarial Testing

Try to break the system on purpose.

Examples:

* malformed input
* conflicting instructions
* retrieval noise
* long context overload
* tool failure
* partial outages

## 13.6 Regression Testing

When the prompt, model, retriever, or tool changes, run the same eval suite again.

That is how you prevent accidental quality loss.

---

# 14. Latency and Cost in LLM Engineering

This matters a lot in interviews, especially for startup systems.

## 14.1 What Costs Tokens

* long prompts
* long retrieved context
* long chain-of-thought style intermediate text
* long tool traces
* long agent trajectories

## 14.2 What Costs Time

* model size
* context length
* number of tool calls
* number of agent loop iterations
* retry count
* reranking and validation

## 14.3 What Costs Money

Usually a combination of:

* model inference
* vector retrieval
* external tool calls
* human review
* logging and storage

## 14.4 Simple Rule

Every extra step should earn its keep.

If a new prompt stage, retry, or tool call does not improve success rate enough to justify the added cost, it should be removed.

---

# 15. Production Failure Modes and Operational Patterns

This is one of the most important sections for applied AI interviews.

Most candidates can describe:

* the happy path,
* the architecture diagram,
* the ideal workflow.

Strong candidates can describe:

* how the system fails,
* how those failures compound,
* how to detect them,
* and how to contain them.

This section is about the operational reality of long-running AI systems.

---

## 15.1 Prompt Drift

Prompt drift occurs when a prompt that worked initially degrades over time.

Causes include:

* changing user behavior,
* longer conversation histories,
* new retrieval data,
* conflicting instructions,
* prompt accumulation,
* hidden assumptions.

### Example

A customer-support prompt originally assumed:

* short contexts,
* one issue per conversation,
* well-formatted retrieved docs.

Months later:

* conversations become multi-topic,
* retrieval injects noisy snippets,
* users ask chained questions.

The original prompt now behaves unpredictably.

### Important Insight

Prompts are not static artifacts.

They interact with:

* the retrieval distribution,
* the user distribution,
* orchestration logic,
* memory state.

This is a form of distribution shift.

---

## 15.2 Context Poisoning

Retrieved context can overpower instructions.

The model may:

* anchor on irrelevant documents,
* absorb false assumptions,
* follow malicious injected instructions,
* over-trust retrieved content.

### Example

Suppose retrieval returns:

* one highly relevant document,
* several noisy but strongly worded documents.

The model may follow the noisy documents because:

* they dominate attention,
* they appear authoritative,
* they contain imperative phrasing.

### Mitigations

* reranking,
* metadata filtering,
* retrieval scoring,
* instruction separation,
* trusted-source weighting,
* retrieval validation.

---

## 15.3 Agent Trajectory Collapse

Agents often fail gradually, not instantly.

A common pattern:

1. slightly bad retrieval
2. slightly wrong plan
3. slightly wrong tool call
4. corrupted state
5. compounding downstream errors

This is trajectory collapse.

### Why It Happens

Each step conditions future steps.

Errors become part of the context distribution.

The model then reasons from corrupted state.

---

## 15.4 Tool Feedback Loops

A dangerous operational pattern:

1. tool call partially fails
2. agent retries blindly
3. duplicate side effects occur
4. system state diverges

Examples:

* duplicate purchases,
* repeated emails,
* repeated API writes,
* conflicting updates.

### Why This Matters

LLM systems interact with the external world.

Unlike pure text generation, actions are not reversible.

### Important Engineering Concept: Idempotency

A retried action should ideally produce the same final state rather than duplicate side effects.

---

## 15.5 Specification Gaming

This directly connects back to Chapter 0.

The model optimizes:

* what you specified,
  not:
* what you intended.

Exactly like reward hacking in RL.

### Example

Suppose you optimize:

* short customer support responses.

The model may:

* become unhelpfully terse,
* omit caveats,
* refuse complex requests.

The optimization target was incomplete.

### Important Insight

LLM systems are optimization systems.

Misaligned objectives produce pathological behavior.

---

## 15.6 Orchestration Architecture Patterns

Real systems rarely use one giant free-running agent.

They usually use explicit orchestration structures.

---

### A. DAG / Workflow Architecture

Tasks are arranged as explicit graph stages.

Example:

classifier → retriever → planner → executor → verifier

### Pros

* deterministic,
* debuggable,
* bounded cost,
* easier evaluation.

### Cons

* less flexible,
* harder to generalize.

---

### B. Autonomous Agent Loop

The model chooses actions dynamically.

### Pros

* flexible,
* adaptive,
* handles open-ended tasks.

### Cons

* harder to debug,
* unstable,
* potentially unbounded cost.

---

### C. Human-in-the-Loop Systems

Humans intervene:

* before execution,
* after planning,
* only under uncertainty,
* or only for dangerous actions.

### Why These Exist

Autonomous systems are often too risky for production.

Human review reduces catastrophic failure probability.

---

### D. Multi-Model Routing

Different models handle different tasks.

Example:

* small model → classification,
* medium model → retrieval rewrite,
* large model → reasoning-heavy tasks.

### Why This Matters

This is often the biggest practical cost optimization.

Not every request needs the largest model.

---

## 15.7 Operational Observability

Without observability, debugging production AI systems becomes nearly impossible.

---

### Tracing

Record:

* prompts,
* retrieved docs,
* tool calls,
* outputs,
* latency,
* retries,
* intermediate reasoning.

This lets engineers reconstruct failures.

---

### Prompt Versioning

Prompts are effectively code.

You need:

* version control,
* rollback,
* evaluation before deployment,
* reproducibility.

---

### Drift Monitoring

The environment changes over time:

* user behavior,
* retrieval corpus,
* tool APIs,
* latency distributions,
* model updates.

Systems must detect when quality degrades.

---

### Cost Monitoring

Track:

* tokens/request,
* retrieval cost,
* tool calls,
* retries,
* agent loop depth.

A small orchestration bug can increase cost by 10x.

---

## 15.8 Cascading Failure Example

A realistic production failure chain:

1. retrieval index partially corrupted
2. irrelevant docs retrieved
3. planner produces wrong strategy
4. executor retries invalid tool calls
5. retries increase latency
6. timeout handler triggers fallback
7. fallback bypasses verification
8. incorrect action reaches user

Strong candidates can reason through chains like this.

---

## 15.9 Important Meta-Insight

The biggest failures in production LLM systems often do NOT come from:

* the transformer architecture,
* the base model,
* or token prediction itself.

They come from:

* orchestration,
* retrieval,
* memory,
* retries,
* distributed state,
* evaluation gaps,
* and misaligned incentives.

That is why applied AI engineering increasingly looks like systems engineering.

---

# 16. Safety and Trust

If the system can act, then safety matters.

## 16.1 Types of Risk

* bad information
* harmful actions
* unauthorized tool use
* privacy leaks
* overconfident wrong answers
* irreversible side effects

## 16.2 Safety Design Patterns

* human approval for high-impact actions
* least-privilege tool access
* action logs
* audit trails
* content filters
* scoped memory
* data redaction

## 16.3 Trust Principle

The more the system can do, the more tightly it needs to be constrained.

---

# 17. How to Think About a Production LLM System

A production system is usually a stack of these parts:

* user interface
* request router
* prompt builder
* retrieval layer
* model inference
* tool executor
* state store
* evaluator
* monitoring and logging

When an interviewer asks you to design an LLM application, they are often asking how you connect these pieces.

The best answers usually discuss:

* where context comes from
* how the model is constrained
* how failures are detected
* how the system recovers
* how quality is measured over time

---

# 18. Summary Mental Model

LLM engineering is about turning a probabilistic generator into a controlled system.

The main levers are:

* prompt design
* decoding strategy
* structured outputs
* tools
* memory
* orchestration
* retries and validation
* evaluation and safety

The deeper lesson is this:

> A good LLM product is not just a good model. It is a good control system around a model.

---

# 19. Key Tradeoffs

Every LLM engineering decision lives in tension with at least one other goal:

* **Control vs Flexibility** — Strict schemas and validation reduce hallucination risk, but they also reduce the model's ability to handle unexpected inputs gracefully. Over-constraining the output space can make the system brittle in novel situations.

* **Reliability vs Latency** — Retries, validation loops, multi-step orchestration, and verification all improve output quality, but they add time. For interactive products, the budget for these steps is tight.

* **Determinism vs Expressiveness** — Low temperature and constrained decoding produce predictable outputs, but they limit the model's creative and reasoning range. High-stakes factual tasks want determinism; open-ended generation wants expressiveness.

* **Cost vs Quality** — Longer contexts, larger models, more tool calls, and additional verification steps all improve quality but increase per-request spend. The design question is not "which is better" but "where is the marginal gain no longer worth the marginal cost for this product?"

* **Simplicity vs Completeness** — A single-prompt system is easy to debug and fast to ship. A multi-stage pipeline with retrieval, tools, validation, and orchestration handles more cases but is harder to reason about, test, and maintain.

These tensions are not solvable — they are navigable. Strong engineering means making the tradeoff explicit, measuring both sides, and revisiting the balance as the product and traffic evolve.

---

# 20. What Comes Next

Chapter 2 will go deep on retrieval and memory systems:

* chunking
* embeddings
* reranking
* hybrid search
* long-term memory
* context management
* retrieval evaluation

That is where the system starts to feel truly agentic and enterprise-ready.
