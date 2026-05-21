---
layout: page
title: "Product Specific Design"
guide_type: example
---
# Product-Specific Design Example

This example designs a customer support automation product.

Product goal:

```text
Help support agents resolve common tickets faster while preventing incorrect
policy answers and unsafe account actions.
```

The system should start as agent-assist and gradually automate low-risk workflows.

---

# 1. Product Requirements

## Users

* support agents
* support managers
* trust and safety reviewers
* customers receiving replies

## Core Workflows

* summarize incoming tickets
* classify issue type and urgency
* retrieve relevant policies and account context
* draft customer replies
* recommend actions such as refund, replacement, or escalation
* execute approved low-risk actions
* route high-risk cases to humans

## Success Metrics

* reduced time to first response
* reduced average handle time
* improved first-contact resolution
* stable or improved customer satisfaction
* lower reopen rate
* low policy violation rate
* low unsafe action rate

The key metric is not "the model sounds helpful." The product wins only if it resolves tickets correctly and safely.

---

# 2. Architecture

```text
Support UI
   |
   v
Ticket Assist API
   |
   v
Support Orchestrator
   |
   +--> Ticket Classifier
   |
   +--> Retrieval Service
   |      - help center
   |      - policy docs
   |      - prior tickets
   |      - account metadata
   |
   +--> Context Builder
   |
   +--> Model Gateway
   |
   +--> Validation Layer
   |
   +--> Policy Engine
   |
   +--> Human Review Queue
   |
   +--> Action Workers
          - refund tool
          - replacement tool
          - CRM update tool
          - email send tool
```

Storage:

```text
Postgres
  - tickets
  - accounts
  - policy versions
  - action approvals
  - feedback labels

Vector / Search Index
  - help articles
  - policy chunks
  - prior resolved tickets

Redis
  - hot account metadata
  - feature flags
  - rate limits

Object Store
  - raw ticket attachments
  - transcripts
  - audit exports

Trace Store
  - model calls
  - retrieved docs
  - tool calls
  - reviewer decisions
```

---

# 3. Ticket Flow

Incoming ticket:

```text
My subscription renewed even though I cancelled last week. I want a refund.
```

## Step 1: Classification

```json
{
  "issue_type": "billing_refund",
  "urgency": "normal",
  "sentiment": "negative",
  "risk": "medium",
  "requires_account_lookup": true,
  "possible_actions": ["draft_reply", "check_subscription", "recommend_refund"]
}
```

## Step 2: Retrieval

The system retrieves:

* refund policy
* cancellation policy
* subscription status
* payment history
* prior customer contacts
* similar resolved tickets

Retrieval must distinguish between policy documents and prior cases. Prior cases are examples, not authority.

## Step 3: Drafting

The model drafts:

```json
{
  "customer_reply": "I can help with that. I checked your account and see...",
  "recommended_action": {
    "type": "refund",
    "amount": 29.00,
    "reason": "Cancellation before renewal window"
  },
  "citations": ["refund_policy_v8", "account_subscription_state"],
  "confidence": "medium",
  "needs_review": true
}
```

## Step 4: Policy Gate

The policy engine checks:

* support agent has refund permission
* refund amount below automatic threshold
* payment exists and has not already been refunded
* cancellation timestamp qualifies
* no fraud or abuse flag exists
* customer region allows this policy

If checks pass and the amount is low, the action may be approved. If not, route to review.

## Step 5: Human Review

The support agent sees:

* draft reply
* evidence snippets
* recommended action
* policy checks
* editable final response

The agent can approve, edit, reject, or escalate.

## Step 6: Action Execution

A worker executes the refund using:

```json
{
  "tool": "issue_refund",
  "ticket_id": "ticket_123",
  "payment_id": "pay_456",
  "amount": 29.00,
  "idempotency_key": "ticket_123_refund_pay_456_2900"
}
```

The idempotency key prevents duplicate refunds if the worker retries.

---

# 4. Rollout Plan

## Phase 1: Draft Only

The model summarizes tickets and drafts replies. Humans perform all actions.

Measure:

* agent acceptance rate
* edit distance
* policy correctness
* handle time

## Phase 2: Recommendations

The model recommends actions, but humans approve every action.

Measure:

* recommendation precision
* human rejection reasons
* policy gate failures

## Phase 3: Low-Risk Automation

The system executes narrow, low-risk actions automatically.

Examples:

* resend receipt
* update ticket category
* issue small refund under strict policy
* send password reset guidance

Measure:

* unsafe action rate
* reopen rate
* escalation after automation
* customer satisfaction

## Phase 4: Continuous Improvement

Use reviewer labels and customer outcomes to improve retrieval, prompts, policies, and evals.

---

# 5. Failure Modes and Mitigations

## Stale Policy

The assistant retrieves an old refund policy.

Mitigation:

* policy versioning
* freshness ranking
* authoritative source tags
* policy owner review
* evals covering changed policies

## Hallucinated Promise

The assistant promises a refund that policy does not allow.

Mitigation:

* structured outputs
* citation checks
* policy gate
* human review for medium or high risk

## Duplicate Refund

A retry executes the same refund twice.

Mitigation:

* idempotency keys
* transaction logs
* duplicate-action checks

## Over-Automation

The system handles angry or legally sensitive tickets without escalation.

Mitigation:

* risk classifier
* sentiment and legal keyword detection
* escalation thresholds
* sampled QA

## Silent Regression

A prompt change reduces answer quality but does not break schemas.

Mitigation:

* regression evals
* canary rollout
* human override monitoring
* reopen rate monitoring

---

# 6. Interview Answer Summary

A concise interview version:

```text
I would start with agent-assist, not full automation. The system classifies
tickets, retrieves policy and account context, drafts a response, and recommends
actions. A deterministic policy engine and human review gate account mutations.
Low-risk actions can later be automated with idempotency, audit logs, and feature
flags. I would evaluate using resolution rate, reopen rate, human edit distance,
policy violations, unsafe actions, latency, and cost per resolved ticket.
```
