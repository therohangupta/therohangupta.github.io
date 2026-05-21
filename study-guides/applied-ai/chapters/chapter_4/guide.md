---
layout: page
title: "Chapter 4: Evaluation Systems"
guide_type: chapter
---

Evaluation systems answer a deceptively simple question:

Does the AI system actually work?

For LLM products, that question is harder than it sounds. The output is probabilistic, the task may be subjective, users may care about different failure modes, and a change that improves one cohort can silently hurt another.

This chapter explains how to measure quality, reliability, regressions, and product outcomes in AI systems. The interview signal is not whether you know a list of metrics. It is whether you can design an evaluation system that catches real failures before users do.

---

## Table of Contents

- TOC
{:toc}

---

# 1. The Core Mental Model

An evaluation system is a feedback instrument.

It observes an AI system, compares behavior against some definition of quality, and turns that comparison into a signal engineers can act on.

The simple version is:

```text
inputs -> AI system -> outputs -> scorer -> metrics -> decisions
```

The production version is:

```text
real traffic + curated datasets + adversarial cases
        -> model / prompt / retriever / agent / tool system
        -> traces + outputs + costs + user outcomes
        -> automated checks + model judges + human review
        -> sliced metrics + uncertainty + regression gates
        -> ship / block / rollback / improve
```

The key shift is this:

Evaluation is not a single score. It is a system for producing trustworthy evidence.

For deterministic software, a unit test often has a crisp pass/fail result. For LLM systems, correctness can be graded, contextual, stochastic, or user-dependent. You usually need a layered evaluation stack:

* exact checks for structured outputs
* reference-based checks for known-answer tasks
* rubric grading for qualitative tasks
* human review for ambiguous or high-risk cases
* online metrics for real user impact
* tracing to explain why the score moved

A strong evaluation system does not eliminate uncertainty. It makes uncertainty visible enough to make better engineering decisions.

---

# 2. Core Primitives

## 2.1 Metrics

A metric is a compressed measurement of behavior.

Examples:

* task success rate
* exact match
* hallucination rate
* p95 latency
* cost per successful task
* user thumbs-up rate
* refusal correctness
* tool success rate

Metrics are useful because they make change measurable. They are dangerous because compression hides context.

If a support bot's average satisfaction score rises, that sounds good. But if satisfaction improved for easy billing questions while emergency account-lockout cases got worse, the average metric is hiding the most important regression.

Good metrics should be:

* aligned with user value
* sensitive to meaningful regressions
* hard to game accidentally
* interpretable by engineers
* sliceable by task, user cohort, input type, model version, and failure class

The best interview answer is rarely "use accuracy." It is usually "what does success mean for this product, and what failure would hurt users most?"

## 2.2 Ground Truth

Ground truth is the reference you compare against.

For some tasks, ground truth is objective:

* extracted invoice total
* selected database row
* generated JSON schema validity
* answer to a math problem
* tool call name and arguments

For other tasks, ground truth is partial or subjective:

* "good summary"
* "helpful answer"
* "safe refusal"
* "faithful explanation"
* "high-quality recommendation"

LLM evaluation often operates with imperfect ground truth. That does not mean you give up. It means you choose the strongest available reference:

* exact expected answer where possible
* accepted answer sets for equivalent outputs
* structured validators for machine-readable tasks
* source documents for factuality
* rubrics for qualitative judgment
* preference comparisons for subjective quality
* human adjudication for ambiguous cases

Ground truth is also expensive. Labeling takes time, expert attention, and policy consistency. A small, high-quality golden set is often more valuable than a huge noisy benchmark.

## 2.3 Signal vs Noise

Evaluation is a signal-processing problem.

Signal is the part of the measurement that reflects true system quality. Noise is everything that makes the measurement unstable or misleading.

Common sources of noise:

* stochastic model sampling
* ambiguous prompts
* inconsistent human labels
* flawed judge prompts
* distribution shift between benchmark and production
* small sample sizes
* flaky tools
* transient latency spikes
* hidden changes in retrieved context

If one prompt revision improves the score from 81.0% to 81.4%, that may be a real improvement, or it may be noise. If the evaluation set has 50 examples, the difference is probably not meaningful. If it has 10,000 examples and the improvement is concentrated in a high-value slice, it may matter.

The practical habit is to ask:

* How many examples produced this number?
* How variable is the score across repeated runs?
* Which slices improved or regressed?
* Is the metric correlated with user outcomes?
* Can I inspect traces for examples near the decision boundary?

## 2.4 Distributions of Outcomes

LLM systems do not have one behavior. They have a distribution of behaviors.

The same system may be excellent for short factual questions, mediocre for multi-hop reasoning, fragile for long documents, and unsafe around adversarial inputs. A single aggregate score collapses that distribution into one number.

Evaluation should preserve distributional structure:

* easy vs hard cases
* short vs long inputs
* common vs rare intents
* new users vs power users
* supported vs unsupported languages
* high-confidence vs low-confidence retrieval
* single-step vs multi-step agent tasks
* benign vs adversarial requests

This is why eval slicing matters. A system can improve globally while regressing on the cases that define product trust.

In interviews, this is a strong framing:

> I would not only report an overall score. I would slice by task type, risk level, input length, retrieval quality, and user cohort, because LLM failures are usually unevenly distributed.

## 2.5 Labels and Preferences

Labels say "this is correct" or "this has property X."

Preferences say "output A is better than output B."

Labels are natural for objective tasks:

* expected category
* correct extracted field
* valid or invalid output
* grounded or ungrounded claim

Preferences are natural for subjective tasks:

* answer A is more helpful than answer B
* summary A is more concise while preserving key points
* refusal A is safer and less annoying

Preference data is powerful because users and annotators often find comparison easier than absolute scoring. It is also common in model training and alignment. But preferences still need rubrics. Without rubrics, annotators may optimize for style, verbosity, confidence, or politeness instead of actual task value.

---

# 3. How Evaluation Systems Compose

The primitives combine into an evaluation stack.

At the bottom are test cases:

```text
input
expected behavior
metadata
scoring method
```

A test case might include:

* user prompt
* source documents
* expected JSON fields
* rubric dimensions
* risk category
* tags such as "long_context", "billing", "adversarial", or "tool_required"

The system under test then runs on those cases. For LLM applications, the "system" may include:

* prompt template
* model version
* sampling settings
* retriever
* tool router
* agent loop
* guardrails
* post-processing validators

Scorers convert outputs into measurements. Some scorers are deterministic, such as JSON schema validators. Some are statistical or model-based, such as judge models. Some are human workflows.

Metrics aggregate those scores:

```text
case scores -> slice scores -> aggregate scores -> release decision
```

The release decision should not be a blind threshold. It should be a policy:

* block if critical safety cases regress
* block if structured correctness falls below threshold
* warn if cost rises more than expected
* require human review if factuality improves but refusal quality drops
* allow rollout if only low-risk latency improves and quality is stable

That is the composition:

```text
datasets + runners + scorers + slicing + uncertainty + release policy
```

Evaluation becomes useful when it is wired into decisions.

---

# 4. Evaluation Types

## 4.1 Offline Evaluation

Offline evaluation runs the system against a fixed dataset before deployment.

Use it for:

* prompt changes
* model upgrades
* retriever changes
* tool routing changes
* safety policy updates
* regression gates in CI

Benefits:

* repeatable
* cheap compared to production failure
* can include rare or adversarial cases
* easy to compare versions side by side

Limitations:

* may not match production distribution
* can be overfit
* may miss user behavior changes
* may not capture long-term satisfaction

Offline evals are the first gate, not the final truth.

## 4.2 Online Evaluation

Online evaluation measures live behavior with real users.

Examples:

* A/B tests
* shadow deployments
* canary rollouts
* thumbs-up/down
* task completion
* retention or repeat usage
* escalation rate
* manual review sampling

Online evals answer the question offline evals cannot:

Does this change improve real outcomes?

But they are harder to interpret. User populations shift. Traffic is seasonal. A/B tests need enough volume. Some important failures are rare. User satisfaction can reward confident wrong answers if users do not notice the mistake immediately.

Online metrics should be paired with offline and trace-based analysis.

## 4.3 Regression Evaluation

Regression evaluation asks:

Did this change break something that used to work?

Regression suites are especially important for LLM systems because small changes can have broad effects:

* prompt wording changes
* model version changes
* retrieval chunking changes
* tool schema changes
* safety policy changes
* sampling parameter changes

A good regression suite includes:

* past production failures
* important customer workflows
* edge cases discovered during debugging
* safety-sensitive prompts
* representative golden cases

Every resolved incident should become at least one regression test.

## 4.4 Adversarial Evaluation

Adversarial evaluation probes how the system behaves under hostile, confusing, or boundary-case inputs.

Examples:

* prompt injection
* jailbreak attempts
* malicious tool requests
* misleading source documents
* impossible user requests
* contradictory instructions
* privacy-sensitive prompts
* long-context distraction

Adversarial tests are not only for safety. They also reveal whether the system has crisp boundaries. A customer-support bot should know when not to answer. A coding agent should avoid destructive operations without approval. A medical assistant should avoid making diagnoses beyond its scope.

## 4.5 Synthetic Evaluation

Synthetic evaluation uses generated test cases.

Use it when:

* real data is scarce
* rare failures need coverage
* privacy prevents using production examples
* you want broad combinatorial coverage
* you need to stress a known weakness

Synthetic tests are useful but dangerous. A generator model may produce cases that are too clean, too repetitive, or biased toward what another model can answer. Synthetic data should usually be sampled, reviewed, and mixed with real cases.

The best pattern is:

```text
real failures -> characterize pattern -> generate variants -> review subset -> add to eval suite
```

## 4.6 Human Evaluation

Human evaluation uses annotators, domain experts, internal reviewers, or end users to judge outputs.

It is useful when:

* correctness is subjective
* policy interpretation matters
* factuality requires expertise
* failure cost is high
* automated judges are untrusted

Human evals need operational discipline:

* clear rubrics
* calibration examples
* inter-annotator agreement checks
* adjudication rules
* label audits
* reviewer fatigue management

Human review is not automatically ground truth. Humans can be inconsistent, biased, rushed, or fooled by fluent wrong answers. But for many tasks, human evaluation remains the highest-quality signal when designed carefully.

---

# 5. Common Patterns and Technologies

## 5.1 Eval Harnesses

An eval harness is a runner that executes test cases against a system and records scores.

Common harness capabilities:

* load datasets
* run model or application versions
* call scorers
* aggregate metrics
* compare versions
* export reports
* fail CI on regressions

Examples of tools and patterns:

* custom Python runners
* pytest-based eval suites
* OpenAI Evals-style datasets and graders
* promptfoo for prompt regression tests
* LangSmith or Langfuse datasets and traces
* Braintrust-style experiment tracking
* internal CI jobs that compare candidate vs baseline

The harness matters because evals should be repeatable. If evaluation is a spreadsheet and a manual prompt, it will not reliably protect production.

## 5.2 Prompt Test Suites

Prompt test suites treat prompts as versioned behavior.

They check:

* output format
* refusal behavior
* tool call selection
* groundedness
* tone
* policy compliance
* task completion

Prompt tests are not only for prompt engineers. In LLM systems, a prompt is production code. It deserves regression tests.

## 5.3 A/B Tests

A/B tests compare variants on live traffic.

Typical variants:

* old prompt vs new prompt
* model A vs model B
* retrieval strategy A vs B
* different agent tool policies
* different refusal messages

Good A/B tests define:

* primary metric
* guardrail metrics
* target population
* sample size expectations
* rollout and rollback rules
* how to handle novelty effects and delayed outcomes

The primary metric says what you are trying to improve. Guardrail metrics prevent "improvements" that create hidden damage. For example, a system might increase click-through rate by becoming more sensational, while factuality and user trust decline.

## 5.4 Tracing Dashboards

Tracing dashboards show what happened inside the system.

For an LLM workflow, traces may include:

* prompt template version
* retrieved documents
* model calls
* token usage
* tool calls
* intermediate agent steps
* validation failures
* retries
* final output
* latency breakdown
* costs
* scores

Tools and patterns:

* OpenTelemetry spans
* LangSmith traces
* Langfuse traces
* Honeycomb or Datadog dashboards
* custom request logs
* model gateway logs

Metrics tell you that quality changed. Traces help you understand why.

## 5.5 Scoring Pipelines

Scoring pipelines turn raw outputs into structured evaluation results.

They may include:

* deterministic validators
* regex or parser checks
* schema validation
* retrieval-grounding checks
* judge model calls
* human review queues
* aggregation jobs
* dashboards

In production, scoring is often asynchronous. You may not want to block the user response while a judge model grades factuality. Instead, log the interaction, score it later, and feed the result into monitoring, training data, or review workflows.

## 5.6 Judge Models

Judge models are LLMs used to grade other LLM outputs.

They are useful for:

* factuality checks
* helpfulness ratings
* rubric scoring
* pairwise preferences
* style compliance
* refusal quality

They are risky because they can inherit bias, be fooled by fluency, prefer verbosity, miss domain errors, and drift when the judge model changes.

Judge models should be treated as imperfect measurement instruments. Calibrate them against human labels. Track judge version. Use structured rubrics. Inspect disagreements. Avoid using the same model family as both generator and judge when correlation bias matters.

### Practical judge-model caveats

A judge model is useful when it is cheaper, faster, or more scalable than human review. It is dangerous when it becomes an unquestioned source of truth.

Common failure patterns:

* **verbosity bias:** longer answers look more thoughtful even when they are less precise.
* **style bias:** polished prose gets higher scores than terse correct answers.
* **authority bias:** confident hallucinations pass because they sound plausible.
* **shared blind spots:** generator and judge from the same model family make similar mistakes.
* **rubric drift:** small prompt changes alter score distributions.
* **position bias:** in pairwise comparison, first or second answer is preferred independent of quality.

A mature setup calibrates the judge:

```text
human-labeled calibration set
  -> judge prompt / rubric
  -> judge scores
  -> disagreement analysis
  -> rubric or prompt revision
  -> locked judge version for release comparisons
```

Track judge agreement with humans by slice. A judge that is 90% aligned on easy support answers but 55% aligned on safety refusals should not gate safety releases.

## 5.7 Rubric-Based Grading

A rubric decomposes quality into dimensions.

Example dimensions for a RAG answer:

* answers the user's question
* cites relevant sources
* avoids unsupported claims
* handles uncertainty
* uses concise language

Rubrics make qualitative judgment more consistent. They also make scores more actionable. "The answer got 3/5" is vague. "The answer was helpful but ungrounded" tells the engineer where to look.

## 5.8 Data Labeling Workflows

Labeling workflows turn raw examples into evaluation data.

Important pieces:

* sampling policy
* annotation guidelines
* reviewer training
* calibration examples
* multi-reviewer agreement
* adjudication
* label versioning
* privacy controls

Labeling is an engineering system, not just a data task. If labels are inconsistent, every metric built on top of them becomes questionable.

## 5.9 Scorecards and Review Loops

Teams often turn eval results into a scorecard rather than one scalar score.

Example scorecard for a RAG support assistant:

| Dimension | Scorer | Gate |
| --------- | ------ | ---- |
| JSON validity | deterministic parser | must be 100% |
| Citation support | source-span checker + human spot check | no critical unsupported claims |
| Helpfulness | judge model calibrated to human labels | no regression by more than 2% |
| Safety/refusal | curated golden set | zero known critical failures |
| Latency | tracing metric | p95 under target |
| Cost | token + tool accounting | cost per successful case under budget |

The scorecard matters because release decisions are multi-objective. A model can improve helpfulness while getting worse at citations, or reduce latency while increasing hallucinations.

A review loop usually looks like:

```text
production trace sampled
  -> automated scorers run
  -> high-risk / low-confidence cases enter human review
  -> labels and failure tags are stored
  -> eval dataset is updated
  -> product or prompt changes are tested against the updated suite
```

The practical rule: failures should not just be counted; they should become future test cases.

---

# 6. Metrics That Matter

## 6.1 Task Success Rate

Task success rate measures whether the system completed the user's intended task.

It is often the most important product metric, but it can be hard to define.

For a coding agent, success might mean:

* tests pass
* requested files changed
* no unrelated edits
* user accepts the result

For customer support, success might mean:

* user problem resolved
* no escalation needed
* answer followed policy
* user did not reopen the ticket

Task success should be grounded in real user value, not just model output quality.

## 6.2 Exact Match and Structured Correctness

Exact match is useful when there is a canonical answer.

Examples:

* classification label
* extracted date
* final numeric answer
* selected option

Structured correctness expands this idea to typed outputs:

* valid JSON
* schema compliance
* required fields present
* values in allowed ranges
* tool arguments valid

Exact match is brittle for free-form language. It is excellent for places where downstream software needs precise structure.

## 6.3 Factuality and Hallucination Rate

Factuality asks whether claims are true and supported.

Hallucination rate measures unsupported or false claims.

For RAG systems, factuality should often be measured against provided sources, not general world knowledge. A model may say something true but unsupported by the retrieved context. Depending on the product, that may still be a failure.

Common scoring approaches:

* claim extraction plus source support checks
* human factuality review
* judge model rubric
* citation precision and recall
* answerability checks

Factuality metrics are hard but essential in trust-sensitive products.

## 6.4 Tool Success Rate

Tool success rate measures whether tool calls were correct and completed.

Break it down:

* chose the right tool
* formed valid arguments
* handled tool errors
* interpreted tool results correctly
* avoided unnecessary tool calls

An agent can produce a fluent final answer while using the wrong tool or ignoring a failed tool call. Tool success metrics catch failures hidden by natural language.

## 6.5 Latency

Latency measures user wait time.

Useful views:

* p50 latency
* p95 latency
* p99 latency
* time to first token
* end-to-end completion time
* per-step breakdown

For LLM systems, latency comes from:

* prompt length
* output length
* model size
* retrieval
* tool calls
* retries
* judge calls
* orchestration

Latency is a quality metric. A technically correct answer that arrives too late may fail the product.

## 6.6 Cost

Cost should usually be measured per useful outcome, not just per request.

Examples:

* cost per successful resolution
* cost per accepted code change
* cost per grounded answer
* cost per human escalation avoided

A more expensive model may be cheaper overall if it reduces retries, escalations, or manual review. A cheaper model may be more expensive if it fails more often.

## 6.7 User Satisfaction

User satisfaction captures subjective value.

Signals:

* thumbs up/down
* rating
* re-query rate
* abandonment
* retention
* support escalation
* qualitative feedback

Satisfaction is important but easy to misread. Users may like answers that are confident and wrong. Users may dislike safe refusals that are correct. Satisfaction should be a product signal, not the only truth metric.

## 6.8 Refusal Quality

Refusal quality measures whether the system refuses when it should and helps when it can.

Two failure classes matter:

* under-refusal: answers unsafe or unsupported requests
* over-refusal: refuses benign requests

A good refusal:

* identifies the boundary
* avoids providing harmful content
* offers safe alternatives where possible
* is concise and respectful

Refusal metrics should include both safety and usefulness. A system that refuses everything is safe but useless.

## 6.9 Robustness and Variance

Robustness measures stability under perturbation.

Examples:

* paraphrased inputs
* different input order
* longer context
* irrelevant distractors
* repeated stochastic runs
* model version changes
* tool latency or failure

Variance matters because a system that succeeds 90% of the time on repeated runs can still be unacceptable for high-stakes tasks. For stochastic systems, evaluate multiple runs or run deterministically when possible.

---

# 7. Implementation Details

## 7.1 Dataset Construction

A good eval dataset is intentionally built.

Sources:

* production logs
* user-reported failures
* support escalations
* manually written edge cases
* synthetic variants
* adversarial red-team prompts
* domain expert examples

Each example should include metadata:

* task type
* risk level
* source
* expected behavior
* scoring method
* relevant documents or tool fixtures
* known failure category

Do not treat the dataset as static. It should evolve with product usage and incidents.

## 7.2 Golden Set Design

A golden set is a high-quality, trusted benchmark used for release decisions.

Properties:

* carefully labeled
* representative of critical workflows
* includes edge cases
* stable enough for version comparison
* protected from prompt or model overfitting
* reviewed when product policy changes

Golden sets should not be the only eval data. If engineers repeatedly tune against the same golden set, it becomes less meaningful. Keep some holdout data and add fresh production samples.

## 7.3 Test Case Generation

Test generation expands coverage.

Patterns:

* paraphrase existing cases
* generate boundary cases
* vary entities, formats, and lengths
* generate adversarial distractors
* mutate tool responses
* combine intents

Generated tests should be filtered. A synthetic test with wrong expected behavior is worse than no test because it teaches the system and the team the wrong lesson.

## 7.4 Eval Slicing

Slicing means reporting metrics by subgroup.

Useful slices:

* task type
* input length
* language
* customer tier
* data source
* retrieval confidence
* model version
* tool path
* risk category
* failure type

Slicing turns one vague number into a map of system behavior. It also reveals fairness and reliability issues that aggregate scores hide.

## 7.5 Confidence Intervals and Uncertainty Intuition

Every metric estimated from samples has uncertainty.

If 87 out of 100 examples pass, the observed pass rate is 87%. But the true pass rate over the whole production distribution is not exactly known. With only 100 examples, a few examples can move the score noticeably.

The intuition:

* larger sample sizes reduce uncertainty
* metrics near 50% have more variance than metrics near 0% or 100%
* small score deltas may be noise
* sliced metrics need enough examples per slice
* repeated stochastic runs reveal model variance

You do not always need to compute formal statistics in an interview, but you should mention uncertainty. A mature answer says:

> I would avoid overreacting to tiny changes unless the sample size is large enough and the slice is important.

## 7.6 Score Aggregation

Aggregation combines many measurements into a decision.

Simple averaging is often wrong because not all failures have equal cost.

Better aggregation patterns:

* separate quality, safety, latency, and cost metrics
* use weighted scores only when weights reflect product risk
* require hard gates for critical failures
* report slices next to aggregate scores
* track confidence intervals
* compare candidate vs baseline, not candidate alone

For example:

```text
Ship only if:
- task success does not regress more than 1%
- hallucination rate improves or stays flat
- critical safety cases have zero known failures
- p95 latency stays under 3 seconds
- cost per successful task stays within budget
```

This is better than a single "eval score" because release decisions are multi-objective.

## 7.7 Concrete Eval Harness Shape

A real eval harness needs more than a loop over examples. It needs stable inputs, reproducible system configuration, scorers, traces, and comparison logic.

```text
eval_cases.jsonl
  -> load case + metadata
  -> run candidate system
  -> run baseline system (optional)
  -> collect trace
  -> run deterministic scorers
  -> run judge scorers
  -> aggregate by slice
  -> compare candidate to baseline
  -> emit report and release gate
```

A useful case record contains:

```json
{
  "id": "refund_042",
  "task_type": "refund_policy",
  "input": "Can I get a refund after 45 days?",
  "expected_behavior": "Explain policy exception rules and ask for order date.",
  "risk_level": "medium",
  "fixtures": {"retrieved_docs": ["refund_policy_v3"]},
  "scorers": ["groundedness", "helpfulness", "policy_compliance"]
}
```

The harness should record:

* model and prompt version,
* retrieval index version,
* tool fixture version,
* sampling parameters,
* full trace or trace pointer,
* raw output,
* scorer outputs,
* final pass/fail or score.

Without versioning, you cannot explain why yesterday's eval result differs from today's. Without traces, you cannot debug which stage caused the regression.

## 7.8 Human Review Operations

Human review is most valuable when it is targeted.

Do not send random outputs to reviewers forever. Sample intentionally:

* high-risk categories,
* low-confidence judge scores,
* large model-vs-baseline disagreements,
* user-reported failures,
* new product flows,
* slices with high variance,
* cases near release thresholds.

Reviewers need:

* a written rubric,
* examples of good and bad labels,
* a way to mark ambiguity,
* an escalation path for unclear policy,
* periodic calibration sessions,
* disagreement adjudication.

The output of review should be structured:

```text
label + severity + failure category + free-text note + source evidence
```

That structure lets failures become dashboards, eval slices, and training data.

---

# 8. Tradeoffs

## 8.1 Correctness vs Cost

More evaluation costs more money and time. Judge models, human labels, repeated stochastic runs, and large test suites can be expensive.

The right question is not "how do we evaluate everything?" It is:

What failures are expensive enough to justify stronger evaluation?

High-risk flows need deeper evals. Low-risk copy suggestions may only need lightweight regression tests and online monitoring.

## 8.2 Speed vs Confidence

Fast evals are useful in development and CI. Slow evals are useful before launches.

A practical stack often has layers:

* quick smoke tests on every prompt change
* medium regression suite in CI
* larger offline benchmark before release
* online canary after release
* periodic human review

This gives developers fast feedback without pretending a small test suite proves production readiness.

## 8.3 Automation vs Judgment

Automated evals scale. Human judgment catches nuance.

Use automation for:

* schema checks
* exact correctness
* known failure patterns
* broad regression coverage
* continuous monitoring

Use humans for:

* ambiguous quality
* policy interpretation
* expert factuality
* new failure discovery
* judge calibration

The best systems combine both.

## 8.4 Stability vs Adaptation

A stable benchmark enables version comparison. An adaptive benchmark catches new failures.

You need both:

* stable golden set for longitudinal tracking
* fresh sampled data for distribution shift
* incident-derived tests for known regressions
* holdout sets to reduce overfitting

## 8.5 Aggregate Metrics vs Debuggability

Executives want a single number. Engineers need failure examples.

A good evaluation report gives both:

* headline metrics
* slice breakdowns
* representative failures
* trace links
* changes from baseline
* release recommendation

The score should point engineers toward the next debugging action.

---

# 9. Failure Modes

## 9.1 Misleading Metrics

A metric is misleading when it improves while user value worsens.

Examples:

* measuring answer length instead of helpfulness
* measuring thumbs-up without factuality
* measuring exact match for a task with many valid phrasings
* measuring average success while high-risk cases regress
* measuring tool call count and accidentally rewarding unnecessary tools

A metric is worse than useless when it actively drives the team toward bad behavior. For example, optimizing a support bot for fewer escalations can make it avoid escalation even when a human is needed.

## 9.2 Benchmark Overfit

Benchmark overfit happens when the system improves on the eval set without improving real behavior.

Causes:

* repeated tuning against the same examples
* prompt examples copied from test cases
* model trained on benchmark data
* synthetic tests too similar to generator patterns
* engineers learning benchmark quirks

Mitigations:

* holdout sets
* fresh production samples
* private evals
* rotate some tests
* inspect real failures
* measure online outcomes

## 9.3 Eval Leakage

Eval leakage occurs when test answers or patterns leak into the system being evaluated.

Examples:

* putting golden examples into the prompt
* training on eval data
* retrieving eval answers from a vector store
* judge prompt revealing expected answers
* developers manually special-casing known cases

Leakage makes the score untrustworthy because the evaluation no longer measures generalization.

## 9.4 Judge Bias

Judge models have biases.

They may prefer:

* longer answers
* confident tone
* familiar model style
* their own model family's outputs
* safe-sounding but unhelpful responses
* plausible explanations over correct reasoning

Mitigations:

* calibrate against human labels
* use pairwise judging with randomized order
* use clear rubrics
* track judge versions
* inspect judge disagreements
* use deterministic validators where possible

## 9.5 Synthetic Mismatch

Synthetic tests may not match real users.

They can be:

* too clean
* too verbose
* too balanced
* too easy
* biased toward the generating model
* missing messy production context

Synthetic evals are best used for coverage expansion, not as the sole source of truth.

## 9.6 Blind Spots

Every eval suite has blind spots.

Common blind spots:

* rare but catastrophic failures
* long-tail user intents
* multilingual users
* accessibility needs
* tool outages
* adversarial behavior
* delayed user dissatisfaction
* data freshness issues

The goal is not perfect coverage. The goal is to continuously shrink the unknown failure surface.

---

# 10. What to Say in an Interview

When asked how you would evaluate an LLM system, start from the product objective.

A strong answer:

1. Defines the task and failure costs.
2. Separates objective correctness from subjective quality.
3. Builds a golden set from representative and high-risk cases.
4. Uses deterministic checks where possible.
5. Uses judge models or humans for qualitative dimensions.
6. Slices metrics by task, cohort, risk, and input shape.
7. Compares candidate vs baseline with uncertainty.
8. Adds regression tests for production failures.
9. Uses online A/B tests or canaries to validate real impact.
10. Monitors traces, cost, latency, and safety after launch.

For example:

> I would not rely on one aggregate score. I would build a layered eval: exact validators for structured outputs, source-grounded factuality checks for RAG answers, rubric-based judge or human scoring for helpfulness, regression tests for known failures, and online metrics like task completion and escalation rate. I would slice results by intent, risk level, input length, and retrieval quality, then use hard gates for safety and correctness.

That answer shows production judgment.

---

# 11. Takeaways

Evaluation is not just measuring model accuracy. It is building a trustworthy feedback system around a probabilistic product.

The core primitives are:

* metrics compress behavior
* ground truth defines comparison
* signal vs noise determines trust
* distributions reveal hidden regressions
* labels and preferences encode quality

The core engineering pattern is:

```text
datasets + runners + scorers + slices + uncertainty + release policy
```

Strong evaluation systems are layered. They combine offline tests, online experiments, regression suites, adversarial probes, synthetic cases, and human judgment.

The most common mistake is treating an eval score as truth. A score is evidence. Good engineers ask where it came from, what it misses, how uncertain it is, and whether it maps to user value.

---

# 12. What Comes Next

Evaluation produces the signal that learning systems consume.

Once you can measure quality, you can decide which examples matter, which failures should become training data, which preferences should update a policy, and which feedback loops are safe to automate.

Chapter 5 builds on this by asking:

How does usage data become better behavior over time?
