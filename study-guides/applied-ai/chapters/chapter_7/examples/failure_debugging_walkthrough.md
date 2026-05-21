---
layout: page
title: "Failure Debugging Walkthrough"
guide_type: example
---
# Failure and Debugging Walkthrough

Scenario:

```text
After a retrieval index refresh, an internal knowledge assistant starts giving
incorrect answers about expense reimbursement policy. No service is down.
Latency and error rate look normal.
```

This is a classic silent regression.

---

# 1. Incident Signal

Symptoms:

* employees report wrong reimbursement answers
* support tickets about the assistant increase
* thumbs-down rate rises for expense questions
* no infrastructure alarms fire
* model API latency remains stable

The system is operationally healthy but behaviorally wrong.

This distinction matters in AI systems. A successful HTTP 200 can still be a product failure.

---

# 2. Initial Triage

First define the blast radius.

Questions:

* Which intents are affected?
* Which users or regions are affected?
* When did the regression start?
* Did prompt, model, retrieval, policy, or tool versions change?
* Are wrong answers concentrated around specific documents?

Example finding:

```json
{
  "affected_intent": "expense_policy_question",
  "affected_regions": ["US", "Canada"],
  "start_time": "2026-05-19T14:00:00Z",
  "recent_changes": [
    "retrieval_index_expense_docs_v17 deployed at 13:45",
    "no prompt change",
    "no model route change",
    "no policy engine change"
  ]
}
```

The timing suggests retrieval, but do not assume. Compare traces.

---

# 3. Trace Comparison

Pull one good trace from before the incident and one bad trace after.

## Good Trace

```json
{
  "trace_id": "trace_good_1",
  "prompt_version": "knowledge_answer_v9",
  "model_route": "standard_qa_v4",
  "retrieval_config": "expense_docs_v16",
  "query": "can I expense home office chair",
  "retrieved_documents": [
    "expense_policy_2026",
    "remote_work_equipment_policy_2026",
    "manager_approval_policy_2025"
  ],
  "answer_label": "correct"
}
```

## Bad Trace

```json
{
  "trace_id": "trace_bad_1",
  "prompt_version": "knowledge_answer_v9",
  "model_route": "standard_qa_v4",
  "retrieval_config": "expense_docs_v17",
  "query": "can I expense home office chair",
  "retrieved_documents": [
    "old_remote_work_faq_2022",
    "expense_policy_2026",
    "office_perks_blog_post_2021"
  ],
  "answer_label": "incorrect"
}
```

The first divergence is retrieval. The bad trace retrieved stale and low-authority documents.

---

# 4. Root Cause Investigation

Inspect the retrieval index refresh.

Possible issues:

* old documents were reintroduced
* freshness metadata was dropped
* authority ranking changed
* ACL or source filters failed
* chunking created misleading snippets
* embeddings changed without reranker calibration
* duplicate documents crowded out authoritative policy

Example root cause:

```text
The ingestion job migrated expense documents into a new index but failed to
preserve source_authority and effective_date metadata. The retriever therefore
ranked old FAQ and blog content alongside official policy documents.
```

This is not a model hallucination first. The model answered from bad context.

---

# 5. Immediate Mitigation

Short-term actions:

1. Roll back retrieval config from `expense_docs_v17` to `expense_docs_v16`.
2. Disable the new index behind the feature flag.
3. Add a temporary filter requiring authoritative policy source for expense questions.
4. Notify support and policy owners.
5. Sample recent wrong answers for impact review.

Good rollback design lets you change retrieval config without redeploying the full application.

---

# 6. Permanent Fix

Fix the ingestion and ranking pipeline.

Required changes:

* preserve `source_authority`
* preserve `effective_date`
* mark superseded documents
* add source-type boosts for official policy
* down-rank blog posts and old FAQs
* add ingestion validation checks
* add retrieval eval cases for expense questions

Example validation rule:

```text
For policy intents, top-3 retrieved documents must include at least one
authoritative policy source unless no such source exists.
```

This is not a perfect rule, but it catches the exact class of regression.

---

# 7. Eval Case

Create regression cases before shipping the fix.

Example:

```json
{
  "eval_id": "expense_home_office_chair_policy",
  "input": "Can I expense a home office chair?",
  "expected_retrieval_properties": {
    "must_include_source_type": "official_policy",
    "must_not_include_superseded": true
  },
  "expected_answer_properties": {
    "must_cite_authoritative_policy": true,
    "must_mention_manager_approval_if_required": true,
    "must_not_cite_blog_post": true
  }
}
```

Add similar cases for travel, meals, hardware, international reimbursement, and contractor policy.

---

# 8. Rollout

Roll out the fixed retrieval index gradually:

1. Run offline retrieval evals.
2. Run answer-quality evals using the fixed index.
3. Enable shadow traffic and compare retrieved docs.
4. Canary to internal finance team.
5. Expand to 10 percent of users.
6. Monitor thumbs-down rate, source mix, and policy QA labels.
7. Fully release after metrics stabilize.

Metrics to watch:

* retrieval top-k source authority
* average document freshness
* citation accuracy
* thumbs-down rate
* policy reviewer correctness
* zero-result rate
* latency
* token cost

---

# 9. Post-Incident Review

The postmortem should ask:

* Why did the index refresh drop metadata?
* Why did tests not catch source-authority loss?
* Why did online monitoring not alert on stale source usage?
* Who owns policy retrieval quality?
* Which evals should block future retrieval releases?

Action items:

* make metadata preservation a required ingestion check
* add source mix dashboards
* create policy-intent retrieval evals
* require policy owner signoff for policy index migrations
* document rollback procedure

---

# 10. Interview Framing

When asked to debug this incident, a strong answer is:

```text
I would compare good and bad traces and locate the first behavioral divergence.
Since prompt and model versions were stable but retrieval config changed, I would
inspect retrieved documents, ranking metadata, freshness, and authority signals.
I would roll back the retrieval config immediately, create eval cases from the
bad traces, fix the ingestion metadata bug, and canary the corrected index while
monitoring source authority and answer correctness.
```

The core insight is that production AI debugging is usually trace comparison, not guessing at the prompt.
