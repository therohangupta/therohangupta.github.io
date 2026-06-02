# Candidate Release Eval Report

This is the shape of an eval report for a model, prompt, retriever, or agent change.

## Summary

| Field | Value |
| ----- | ----- |
| Candidate | `support_agent_prompt_v12` |
| Baseline | `support_agent_prompt_v11` |
| Eval dataset | `support_eval_2026_05_20` |
| Decision | Canary, not full rollout |
| Owner | Support AI team |

## Aggregate Metrics

| Metric | Baseline | Candidate | Decision |
| ------ | -------- | --------- | -------- |
| Answer correctness | 84.2% | 86.1% | improved |
| Citation faithfulness | 91.0% | 90.6% | flat |
| Escalation correctness | 88.4% | 84.0% | regressed |
| p95 latency | 2.8s | 3.1s | acceptable |
| Cost per ticket | $0.043 | $0.047 | acceptable |

## Slice Findings

| Slice | Count | Result |
| ----- | ----- | ------ |
| Billing FAQ | 420 | improved |
| Refund policy | 110 | flat |
| Account lockout | 38 | regressed, small sample |
| Enterprise admin | 52 | improved |
| Safety-sensitive | 31 | no known regression, needs more review |

## Uncertainty

The account-lockout slice is small. The candidate appears worse, but the estimate is noisy. Because this slice is high-risk, small sample size is not a reason to ignore the regression. It is a reason to send more cases to human review and limit rollout.

## Representative Failure

```text
User: I am locked out and my backup email is gone.
Candidate: Try resetting your password again.
Expected: Escalate to account recovery workflow.
```

Failure type: under-escalation.

## Release Decision

Canary only for low-risk billing and product FAQ traffic. Block rollout for account-lockout and safety-sensitive routes until the escalation regression is fixed.

## Follow-Up

* add account-lockout regression cases,
* review escalation prompt changes,
* add guardrail metric for under-escalation,
* rerun candidate before full rollout.
