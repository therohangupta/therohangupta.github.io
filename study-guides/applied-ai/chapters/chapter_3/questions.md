---
layout: page
title: "Agents Practice Questions"
guide_type: questions
---
# Chapter 3 — Practice Questions

Explanatory material for this chapter lives in [`guide.md`](guide.html).

---

# Common Interview Questions and Sample Answers

---

## Question 1

**What is an agent in an LLM product system?**

### Sample Answer

An agent is a controlled loop that uses state, actions, observations, transitions, and stopping rules to make progress toward a goal. The LLM is usually the policy that chooses or helps choose actions, while the surrounding product system constrains tools, budgets, permissions, and execution.

---

## Question 2

**When would you use an agent instead of a single LLM call?**

### Sample Answer

I would use an agent when the task requires multiple dependent steps, tool use, intermediate observations, or adaptation based on feedback. If the task is a simple text transformation with known inputs and outputs, a single call or deterministic workflow is cheaper, faster, and easier to evaluate.

---

## Question 3

**What are the core primitives of an agent loop?**

### Sample Answer

The core primitives are state, actions, observations, transitions, stopping rules, budgets, planning, and execution. State captures what the agent knows, actions define what it can do, observations report what happened, transitions update state, and stopping rules decide when the loop ends.

---

## Question 4

**Why is explicit state important in production agents?**

### Sample Answer

Explicit state makes the agent inspectable, resumable, testable, and enforceable. If state only exists as prompt text, it is hard to validate whether the system respected constraints, used the right evidence, or should continue. Typed state also helps keep signal high and prevents context from becoming a noisy transcript.

---

## Question 5

**What does "bounded action space" mean, and why does it matter?**

### Sample Answer

A bounded action space means the agent can only choose from a defined set of permitted actions, usually exposed through typed tools or workflow transitions. It matters because unconstrained autonomy is hard to secure, test, and evaluate. The smaller and clearer the action space, the easier it is to reason about safety and correctness.

---

## Question 6

**How would you design safe autonomy for an agent that can take side effects?**

### Sample Answer

I would tier tools by risk, use least-privilege permissions, require human approval for irreversible actions, add idempotency keys for side effects, enforce budgets, log every action, and validate plans before execution. Safe autonomy comes from product and systems constraints, not from asking the model to be careful.

---

## Question 7

**What is the ReAct pattern?**

### Sample Answer

ReAct alternates reasoning, action, and observation. The model thinks about what to do, calls a tool, observes the result, and repeats until it can answer or stop. It is useful for search and debugging tasks, but it needs step limits, tool validation, and observation checks because errors compound across the trajectory.

---

## Question 8

**What is the tradeoff of planner/executor architectures?**

### Sample Answer

Planner/executor architectures expose intent before action, which makes plan validation, human review, and deterministic execution easier. The tradeoff is that plans can become stale or brittle when observations change. Good systems allow controlled replanning instead of blindly executing the original plan.

---

## Question 9

**How do agent loops connect to Chapter 0 optimization and decision ideas?**

### Sample Answer

An agent loop is a decision process under constraints. The model chooses actions based on state, receives observations, and updates its trajectory. Budgets, stopping rules, and validators shape the objective just like optimization constraints shape learning. The system is not maximizing open-ended helpfulness; it is optimizing task success under cost, latency, and safety limits.

---

## Question 10

**Why can a bad first step cause an agent to fail even if later steps look reasonable?**

### Sample Answer

Because agent trajectories compound. A bad first search query, classification, or plan can put the agent in the wrong part of the state space. Later decisions may be locally consistent with bad evidence but globally wrong. This is why plan validation, clarification, and early evidence checks are important.

---

## Question 11

**How would you prevent an agent from looping forever?**

### Sample Answer

I would enforce max steps, retry caps, token and cost budgets, repeated-state detection, and explicit terminal states such as completed, needs human input, budget exhausted, or unable to complete. I would also log stop reasons so failures can be diagnosed.

---

## Question 12

**Why is idempotency important for agents?**

### Sample Answer

Agents retry, resume, and may receive duplicate events from queues. Without idempotency, side effects can be duplicated: sending the same email twice, creating duplicate tickets, or charging a customer twice. Idempotency keys, dedupe records, and transactional checks make retries safe.

---

## Question 13

**When should agent steps be parallelized?**

### Sample Answer

Parallelize steps when they are independent, such as searching multiple sources, processing separate documents, or generating alternative plans. Keep steps sequential when each decision depends on the previous observation or when actions have side effects. A good rule is: parallelize independent uncertainty reduction; serialize dependent decisions and writes.

---

## Question 14

**What is human-in-the-loop, and when should it be used?**

### Sample Answer

Human-in-the-loop means the system pauses for human judgment, approval, or clarification. It should be used when confidence is low, intent is ambiguous, cost is high, policy requires review, or the next action is irreversible. It is a control boundary, not a failure of automation.

---

## Question 15

**How would you choose between a guided workflow and an autonomous agent?**

### Sample Answer

I would use a guided workflow when the product path is known, correctness matters, or compliance and predictability are important. I would use more autonomy when the task is open-ended and the correct path depends on observations. In many products, the best design is a guided workflow with bounded agentic substeps.

---

## Question 16

**What are common failure modes of production agents?**

### Sample Answer

Common failure modes include bad first-step cascades, trajectory collapse, tool feedback loops, runaway costs, duplicated side effects, memory drift, infinite loops, and over-autonomy. Most of these come from compounding errors across steps, so containment and observability are central to the design.

---

## Question 17

**How would you evaluate whether an agent is working well?**

### Sample Answer

I would evaluate both the final output and the trajectory. That means measuring task success, tool choice quality, evidence use, budget adherence, stop reasons, safety policy compliance, and recovery from failures. For agents, a fluent final answer is not enough if the path was unsafe or expensive.

---

## Question 18

**What role do frameworks like LangGraph, AutoGen, CrewAI, MCP, and DSPy play?**

### Sample Answer

They provide different abstractions around orchestration, tools, multi-agent coordination, and optimization. LangGraph helps model workflows as graphs of state transitions. MCP standardizes tool and context access. AutoGen and CrewAI help prototype multi-agent patterns. DSPy helps optimize LLM modules. None of them removes the need for state design, permissions, evaluation, and operational controls.

---

## Question 19

**How would you explain safe tool use in an interview?**

### Sample Answer

I would say tools should be exposed as typed, permissioned actions with validation around inputs and outputs. Read-only tools can be broadly available, while write or irreversible tools need approval, audit logs, idempotency, and stricter limits. The goal is to give the model useful capabilities without giving it unbounded authority.

---

## Question 20

**What is the relationship between agent memory and memory drift?**

### Sample Answer

Agent memory can improve continuity by preserving useful facts, preferences, and prior observations. But memory drift happens when stale, wrong, or low-confidence information gets reused as if it were true. To reduce drift, memory should have provenance, confidence, expiration, and clear separation between facts, preferences, and summaries.

---

## Question 21

**How do you prevent one failing agent run from consuming all system resources?**

### Sample Answer

Give every run explicit budgets: max tool calls, max tokens, max wall-clock time, max retries, and max parallel branches. Use queue limits, cancellation, rate limits, and circuit breakers around external tools. The orchestrator should mark the run as failed or escalated when budgets are exhausted rather than allowing open-ended loops.

---

## Question 22

**What changes when agents run asynchronously or in distributed workers?**

### Sample Answer

State must become durable and resumable. A single in-memory loop is not enough because workers can crash, retries can duplicate actions, and tool calls may finish out of order. Distributed agents need workflow IDs, checkpoints, idempotency keys, leases or locks, cancellation, and clear ownership of each step.

---

## Question 23

**Why is scheduling important for production agent systems?**

### Sample Answer

Agent runs can vary wildly in cost. Some finish after one tool call; others trigger long retrieval, multiple model calls, and slow external APIs. Scheduling prevents expensive runs from starving short ones. A good system separates queues by priority, risk, customer tier, expected cost, or tool type and enforces fairness and resource limits.

---

## Question 24

**How would you handle a tool call that takes longer than expected inside an agent loop?**

### Sample Answer

The tool call should have a timeout and cancellation policy. If it times out, the agent should record the failure as an observation, decide whether a retry is safe, and avoid repeating non-idempotent actions. For high-value workflows, the system may continue with partial results or escalate. The important point is that the model should not wait forever or invent the missing tool result.

---

## Question 25

**Why are partial results useful in distributed agent execution?**

### Sample Answer

Partial results let the system recover from failures and avoid losing work. If retrieval succeeded but a downstream tool failed, the system can resume from the last checkpoint instead of restarting the whole trajectory. Partial results also support human review, debugging, and cost control because engineers can see which step failed and why.

---
