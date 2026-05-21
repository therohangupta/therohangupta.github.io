---
layout: page
title: "Evaluation Systems Practice Questions"
guide_type: questions
---
# Chapter 4 — Practice Questions

Explanatory material for this chapter lives in [`guide.md`](guide.html).

---

# Common Interview Questions and Sample Answers

---

## Question 1

**How would you evaluate an LLM customer-support bot?**

### Sample Answer

I would start with the product goal: resolving user issues safely and accurately. I would measure task success, escalation rate, factuality against policy docs, refusal quality for unsupported requests, latency, cost per resolved ticket, and user satisfaction. I would use an offline golden set for common and high-risk cases, regression tests for past failures, human review for ambiguous cases, and online A/B tests to verify real user impact.

---

## Question 2

**Why is one aggregate eval score usually not enough?**

### Sample Answer

Because LLM failures are unevenly distributed. A system can improve on average while getting worse for long-context inputs, high-risk intents, non-English users, or tool-required workflows. I would report aggregate metrics, but also slice by task type, risk level, input length, user cohort, retrieval quality, and failure class.

---

## Question 3

**What is the difference between offline and online evaluation?**

### Sample Answer

Offline evaluation runs the system on a fixed dataset before deployment. It is repeatable and useful for regression testing, but may not match real user behavior. Online evaluation measures live user outcomes through A/B tests, canaries, satisfaction signals, task completion, and escalation rates. Offline evals catch many failures early; online evals validate real product impact.

---

## Question 4

**When is a metric worse than useless?**

### Sample Answer

A metric is worse than useless when optimizing it pushes the system away from user value. For example, measuring a support bot only by low escalation rate can reward the bot for refusing to hand off cases that need a human. Measuring answer length can reward verbosity instead of correctness. A bad metric does not merely fail to help; it creates the wrong incentives.

---

## Question 5

**How would you design a benchmark for a RAG system?**

### Sample Answer

I would include representative production questions, high-value workflows, known failures, unanswerable questions, ambiguous questions, and adversarial cases with distracting documents. Each case should include source documents, expected answer behavior, metadata tags, and a scoring method. I would measure answer correctness, groundedness, citation quality, refusal behavior, latency, and cost, then slice by retrieval quality and question type.

---

## Question 6

**How do you evaluate factuality or hallucination rate?**

### Sample Answer

For grounded tasks, I would evaluate claims against the provided sources rather than against general world knowledge. A scoring pipeline could extract claims, check whether each claim is supported by retrieved documents, and use human or judge-model review for ambiguous cases. I would report unsupported-claim rate, answer-level hallucination rate, and examples of severe failures.

---

## Question 7

**When would exact match be a good metric, and when would it be bad?**

### Sample Answer

Exact match is good for canonical outputs such as classification labels, extracted fields, selected options, or numeric answers. It is bad for open-ended generation where many phrasings are correct. For summaries or helpful answers, exact match would penalize valid variation and miss deeper quality issues.

---

## Question 8

**How would you evaluate an agent that uses tools?**

### Sample Answer

I would evaluate both final task success and intermediate tool behavior. Metrics should include correct tool selection, valid tool arguments, tool success rate, error handling, unnecessary tool calls, final answer correctness, latency, and cost. Tracing is important because a fluent final answer can hide a wrong tool call or ignored tool failure.

---

## Question 9

**How do you detect regressions after changing a prompt?**

### Sample Answer

I would run the candidate prompt against a baseline on a regression suite containing golden cases, past production failures, edge cases, and safety-sensitive examples. I would compare metrics by slice, inspect failures, and use hard gates for critical correctness and safety. I would also run online canaries if the offline result looks acceptable.

---

## Question 10

**What makes a good golden set?**

### Sample Answer

A good golden set is carefully labeled, representative of important workflows, includes edge cases and high-risk cases, has stable scoring rules, and is protected from overfitting or leakage. It should be small enough to maintain quality but broad enough to catch meaningful regressions.

---

## Question 11

**What is eval leakage?**

### Sample Answer

Eval leakage happens when test answers or test patterns influence the system being evaluated. Examples include training on eval data, putting golden examples into the prompt, retrieving expected answers from a vector store, or manually special-casing benchmark cases. Leakage makes scores untrustworthy because the eval no longer measures generalization.

---

## Question 12

**How reliable are LLM judge models?**

### Sample Answer

Judge models are useful but imperfect. They can prefer verbose answers, confident style, familiar model outputs, or safe-sounding responses. I would calibrate judges against human labels, use clear rubrics, randomize answer order for pairwise comparisons, track judge versions, inspect disagreements, and prefer deterministic validators when possible.

---

## Question 13

**How would you evaluate refusal quality?**

### Sample Answer

I would measure both under-refusal and over-refusal. Under-refusal means the system answers unsafe or unsupported requests. Over-refusal means it refuses benign requests. A good refusal should identify the boundary, avoid harmful content, and offer safe alternatives when possible. The eval set should include unsafe, borderline, and clearly benign cases.

---

## Question 14

**Why do confidence intervals or uncertainty matter in evals?**

### Sample Answer

Metrics are estimates from samples. If a pass rate moves from 84% to 85% on a small dataset, that may just be noise. Confidence intervals and repeated runs help determine whether a change is meaningful. They are especially important for sliced metrics because each slice may have fewer examples.

---

## Question 15

**How would you use synthetic evals safely?**

### Sample Answer

I would use synthetic evals to expand coverage around known patterns, rare failures, privacy-sensitive cases, or adversarial variants. I would not trust them blindly. I would review samples, mix them with real production cases, track their source, and check whether improvements on synthetic cases correlate with real-world outcomes.

---

## Question 16

**How do you evaluate robustness?**

### Sample Answer

I would perturb inputs and measure whether behavior stays stable. Perturbations could include paraphrases, irrelevant context, different document order, longer inputs, missing fields, tool errors, and repeated stochastic runs. Robustness is about variance, not just average correctness.

---

## Question 17

**How would you choose between human evaluation and automated evaluation?**

### Sample Answer

I would use automated checks for exact outputs, schema validity, known failure patterns, and broad regression coverage. I would use human evaluation for subjective quality, expert factuality, policy interpretation, and judge calibration. The best eval systems combine automation for scale with human review for nuance.

---

## Question 18

**What should be included in an evaluation report before shipping a model change?**

### Sample Answer

It should compare candidate versus baseline, show primary and guardrail metrics, include slice breakdowns, report uncertainty where relevant, list representative failures, show latency and cost changes, identify safety or correctness regressions, and make a clear ship, canary, rollback, or block recommendation.

---

## Question 19

**Why might user satisfaction be a misleading metric?**

### Sample Answer

Users may reward confident, fluent answers even when they are wrong. They may also dislike correct refusals or safe boundaries. Satisfaction is valuable as a product signal, but it should be paired with factuality, task success, safety, and escalation metrics.

---

## Question 20

**How do evaluation systems connect to learning loops?**

### Sample Answer

Evaluation produces the signal used to improve the system. Failed examples become regression tests, labeled examples become training or preference data, online outcomes identify valuable cases, and human review clarifies policy. Without reliable evals, a learning loop may optimize noise or amplify bad incentives.

---

## Question 21

**Design exercise: how would you evaluate an AI support agent before launch?**

### Sample Answer

I would build an eval set from real support intents, historical escalations, policy-sensitive cases, adversarial prompts, and unanswerable requests. I would score task success, factuality, groundedness, citation quality, tool correctness, escalation behavior, latency, and cost. The release gate should compare against a baseline by slice, require no regressions on safety or policy cases, and include human review for representative failures.

---

## Question 22

**Production debugging: an eval dashboard improved, but users report worse answers. What would you investigate?**

### Sample Answer

I would check whether the eval set matches current traffic, whether aggregate gains hide slice regressions, whether synthetic cases overweight easy patterns, whether the judge model rewards style over correctness, and whether online traffic has retrieval, latency, or tool failures not represented offline. I would inspect traces from bad user reports and add those cases to the regression suite.
