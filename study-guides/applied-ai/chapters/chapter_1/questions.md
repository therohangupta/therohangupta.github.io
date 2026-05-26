---
layout: page
title: "LLM Engineering Practice Questions"
guide_type: questions
---
# Chapter 1 — Practice Questions

Explanatory material for this chapter lives in [`guide.md`](guide.html).

---

# Common Interview Questions and Sample Answers

---

## Question 1

**Why does few-shot prompting work?**

### Sample Answer

Few-shot prompting works because the model uses the examples to infer the latent task and output style. The examples shift the local conditional distribution and show the model what a correct transformation looks like in context.

---

## Question 2

**How would you make sure an LLM returns valid JSON?**

### Sample Answer

I would not rely on prompt wording alone. I would use schema-constrained generation if available, validate the output strictly, retry on parse failure, and keep the schema as small and specific as possible.

---

## Question 3

**Why do agent systems fail so often?**

### Sample Answer

Agents fail because errors compound across steps. A bad retrieval can cause a bad plan, a bad tool call can cause a bad observation, and then the system keeps building on a wrong state. Loops, retries, and memory also create more failure surface area.

---

## Question 4

**What is the difference between prompting and fine-tuning?**

### Sample Answer

Prompting changes the input context to steer behavior at runtime. Fine-tuning changes the model weights so the behavior becomes internalized. Prompting is faster and more flexible; fine-tuning is more stable but slower and more expensive to change.

---

## Question 5

**When would you choose an agent over a single prompt?**

### Sample Answer

I would choose an agent when the task requires multiple steps, tool use, intermediate observation, or iterative search. If the task is simple and stateless, a single prompt is usually cheaper and more reliable.

---

## Question 6

**How do you reduce hallucinations in a production system?**

### Sample Answer

I would combine retrieval, structured outputs, verification, and constrained actions. I would also make sure the model is only allowed to answer from grounded sources when appropriate, and I would measure hallucination rate offline and online.

---

## Question 7

**Why is structured output so important?**

### Sample Answer

Because downstream software needs reliable typed data, not fluent prose. Structured output reduces ambiguity, makes validation possible, and prevents the model from drifting into unrelated text.

---

## Question 8

**How do you think about latency in an LLM workflow?**

### Sample Answer

I break latency into model time, retrieval time, tool time, and orchestration overhead. Then I ask which steps are actually necessary and which can be parallelized, cached, shortened, or removed.

---

## Question 9

**What is the biggest mistake people make when designing agent systems?**

### Sample Answer

They assume the model will self-correct reliably. In practice, agents need explicit budgets, validation, stopping rules, and safe tool access. Otherwise errors accumulate and the system becomes unstable.

---

## Question 10

**How would you debug a prompt that works in demos but fails in production?**

### Sample Answer

I would inspect the real inputs, compare them to the demo examples, check for distribution shift, look for prompt conflicts, evaluate retrieval quality, inspect tool failures, and measure where the output first diverges from expectations.

---

## Question 11

**Why can adding more context hurt performance?**

### Sample Answer

Because more context can add noise, increase token cost, and make the relevant signal harder to find. The model has limited attention and context budget, so more text is not always better.

---

## Question 12

**What is a good fallback strategy for a critical LLM feature?**

### Sample Answer

I would use a conservative fallback such as a smaller deterministic model, a rules-based path, or a human-in-the-loop approval step. The fallback should fail safely rather than attempting to be clever.

---

# Cross-Section (Foundations ↔ LLM Engineering) Questions

These questions explicitly connect Chapter 1 back to the primitives in Chapter 0.

---

## Question 13

**Why does prompt engineering work even though we are not changing model weights? (Connect to probability + optimization)**

### Sample Answer

Prompting changes the input $x$, which changes the conditional distribution $P(y\mid x)$.  
Even though weights are fixed, the model was trained to condition strongly on context, so modifying the prompt effectively shifts the probability mass toward different outputs.  
This is equivalent to changing the optimization target at inference time without retraining.

---

## Question 14

**Why do structured outputs improve reliability? (Connect to entropy + information flow)**

### Sample Answer

Structured outputs constrain the output space, reducing entropy. By narrowing the possible outputs, we improve the signal-to-noise ratio and make it easier to validate correctness, which leads to more reliable systems.

---

## Question 15

**Why does adding more context sometimes hurt even in a well-designed system? (Connect to information flow)**

### Sample Answer

Because the model has limited capacity to attend to relevant information. Adding more context can dilute signal with noise, making it harder for the model to focus on the important parts, which degrades performance.

---

## Question 16

**Why does few-shot prompting sometimes outperform zero-shot? (Connect to representation)**

### Sample Answer

Few-shot examples provide structured patterns that the model can match in embedding space. They effectively define a local task representation that aligns better with the desired output distribution.

---

## Question 17

**Why are retries and self-consistency effective? (Connect to probability)**

### Sample Answer

Because the model samples from a distribution, multiple runs explore different parts of that distribution. Aggregating results increases the chance of selecting a high-quality outcome and reduces variance.

---

## Question 18

**Why do agent systems become unstable over time? (Connect to optimization + distribution shift)**

### Sample Answer

Each step feeds the model its own outputs, which may not match the training distribution. Errors accumulate and compound, leading to drift away from the intended behavior.

---

## Question 19

**Why is retrieval helpful but not sufficient to prevent hallucinations? (Connect to probability + signal)**

### Sample Answer

Retrieval adds high-signal context, shifting the distribution toward grounded outputs. However, the model can still assign high probability to incorrect continuations if the retrieved context is incomplete, noisy, or misused.

---

## Question 20

**Why is validation necessary even with a strong model? (Connect to optimization)**

### Sample Answer

Because the model optimizes for likelihood, not correctness. It can produce high-confidence but wrong outputs, so external validation is required to enforce correctness constraints.

---

## Question 21

**Why is decomposition a powerful strategy? (Connect to representation + optimization)**

### Sample Answer

Breaking a task into smaller steps simplifies each subproblem and aligns better with the model's learned patterns. It reduces complexity and improves the quality of intermediate representations.

---

## Question 22

**Why does tool use extend capability beyond the model? (Connect to parameterization)**

### Sample Answer

Tools act as external modules that provide functionality not encoded in the model's parameters. Instead of learning everything internally, the system delegates certain operations to deterministic functions.

---

## Question 23

**Why is memory pruning important? (Connect to information flow)**

### Sample Answer

Because storing everything increases noise and reduces retrieval quality. Pruning ensures that only high-signal information is retained, improving downstream reasoning.

---

## Question 24

**Why is prompt ambiguity dangerous in production systems? (Connect to probability)**

### Sample Answer

Ambiguity widens the output distribution, increasing variance and making outputs less predictable. In production, this leads to inconsistent behavior and harder debugging.

---

## Question 25

**A prompt works well offline but fails after retrieval is added. Why might that happen?**

### Sample Answer

Retrieval changes the input distribution. The model is no longer conditioning only on the clean prompt; it is also conditioning on retrieved snippets that may be noisy, contradictory, stale, or instruction-like. This can dilute the original task, introduce context poisoning, or make the model over-trust irrelevant evidence. I would debug retrieval quality, source ranking, prompt boundaries, citation support, and whether retrieved text is being treated as data rather than instructions.

---

## Question 26

**Why can retries make an LLM workflow less reliable instead of more reliable?**

### Sample Answer

Retries help when failures are transient or validation-driven. They hurt when the underlying issue is systematic, such as a bad prompt, broken tool, invalid schema, or missing context. Blind retries can increase cost, duplicate side effects, amplify outages, and produce inconsistent state. Good retries are bounded, idempotent, logged, and conditioned on the failure type.

---

## Question 27

**How would you safely expose tools to an LLM?**

### Sample Answer

I would expose tools through a narrow registry of typed, permissioned actions. Each tool should have a schema, input validation, output validation, timeout, audit log, and risk level. Read-only tools can be broadly available; write or irreversible tools need scopes, idempotency keys, approval gates, and rollback or compensation paths. The model should never receive arbitrary code or raw database write access.

---

## Question 28

**What should happen if a tool partially fails after making an external change?**

### Sample Answer

The system should treat this as a state-management problem, not just a prompt problem. The tool call should have an idempotency key, durable status, and enough logging to determine whether the side effect happened. The agent should not blindly retry. It should check the external state, continue only from the confirmed state, or escalate to human review if the result is ambiguous.

---

## Question 29

**Why can structured outputs still fail even with JSON mode or schema-constrained generation?**

### Sample Answer

JSON mode can improve syntax, but it does not guarantee semantic correctness. The model can still put the wrong value in a valid field, omit contextually required information, hallucinate IDs, choose the wrong enum, or satisfy the schema while violating business rules. Production systems still need validators, grounding checks, policy checks, and fallback behavior.

---

## Question 30

**When should you avoid building an agent and use a simpler workflow instead?**

### Sample Answer

Avoid an agent when the task is simple, deterministic, high-risk, cheap to solve with a fixed workflow, or does not require iterative observation. A linear pipeline with classification, retrieval, validation, and one model call is often easier to debug, cheaper, and safer. Agents are useful when the task genuinely needs multi-step search, tool use, and adaptation under uncertainty.

---

## Question 31

**How would you debug an LLM workflow that only fails in production traffic?**

### Sample Answer

I would inspect traces rather than only the final answer: prompt version, retrieved context, tool calls, validation failures, model parameters, latency, user segment, and route. Then I would compare production failures to offline eval cases to identify distribution shift. Common causes are noisy retrieval, prompt accumulation, hidden user intents, tool errors, schema drift, and missing eval coverage.

---

## Question 32

**How would you detect hallucinations automatically?**

### Sample Answer

I would treat hallucination detection as claim verification, not vibes. For grounded tasks, extract factual claims from the answer and check whether each claim is supported by retrieved sources, citations, tool outputs, or a trusted database. Deterministic checks are best when possible, such as verifying IDs, dates, calculations, and citation spans. For open-ended claims, I would use calibrated judge models or human review on sampled traffic, track unsupported-claim rate, and slice failures by retrieval quality, prompt version, and task type.

---
