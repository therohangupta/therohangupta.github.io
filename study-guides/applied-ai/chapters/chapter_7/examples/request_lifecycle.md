---
layout: page
title: "Request Lifecycle"
guide_type: example
---
# Request Lifecycle Example

This example traces one request through an internal knowledge assistant.

User request:

```text
Can I use Customer A's deployment logs in a public conference talk?
```

This is not a simple knowledge question. It touches customer data, external sharing, policy, and possibly legal review.

---

# 1. Ingress

The client sends:

```json
{
  "request_id": "req_123",
  "user_id": "u_42",
  "tenant_id": "company",
  "message": "Can I use Customer A's deployment logs in a public conference talk?",
  "conversation_id": "conv_77"
}
```

The API gateway:

* authenticates the user
* checks tenant and rate limits
* rejects oversized payloads
* attaches a trace ID
* forwards the request to the orchestrator

The gateway should not call the model. Its job is boundary enforcement and routing.

---

# 2. Classification

The orchestrator runs a small classifier.

Possible output:

```json
{
  "intent": "policy_question",
  "risk": "high",
  "requires_retrieval": true,
  "requires_action": false,
  "candidate_sources": [
    "customer_data_policy",
    "marketing_policy",
    "contract_metadata",
    "security_policy"
  ]
}
```

This classification changes the rest of the lifecycle. A high-risk policy question should use authoritative sources, stricter validation, and possibly escalation.

---

# 3. State Loading

The orchestrator loads structured state:

```json
{
  "user": {
    "id": "u_42",
    "role": "engineering_manager",
    "groups": ["engineering", "conference_speakers"]
  },
  "conversation": {
    "id": "conv_77",
    "summary": "User is preparing a public talk about deployment architecture."
  },
  "flags": {
    "policy_assistant_v3": true,
    "auto_escalate_external_sharing": true
  },
  "versions": {
    "prompt": "policy_answer_v12",
    "retrieval_config": "policy_hybrid_v5",
    "model_route": "risk_sensitive_v2"
  }
}
```

Permissions and flags are structured state. They should not be inferred from chat history.

---

# 4. Permission-Aware Retrieval

The retrieval service searches relevant sources with ACL filters:

```text
query:
  public sharing customer deployment logs conference talk

filters:
  tenant_id = company
  user_groups include engineering or public_policy_readers
  source in customer_data_policy, marketing_policy, contract_metadata, security_policy
```

Candidate documents:

```text
doc_1 customer_data_policy_2026
  "Customer logs may not be shared externally unless anonymized and approved..."

doc_2 marketing_external_talks_policy
  "Public talks require review for customer-identifiable details..."

doc_3 customer_a_contract_summary
  "Customer A contract prohibits disclosure of operational metrics..."

doc_4 old_public_talk_guidance_2022
  "Screenshots may be used if customer name is removed..."
```

The context builder should prefer `doc_1`, `doc_2`, and `doc_3`. It should down-rank or exclude `doc_4` because it is old and potentially superseded.

---

# 5. Context Assembly

The context builder creates a prompt package:

```json
{
  "system_instruction": "Answer as an internal policy assistant. Use only provided sources for policy claims.",
  "task_instruction": "Return a recommendation, citations, uncertainty, and escalation decision.",
  "user_request": "Can I use Customer A's deployment logs in a public conference talk?",
  "conversation_summary": "User is preparing a public talk about deployment architecture.",
  "evidence": [
    {
      "source_id": "doc_1",
      "freshness": "2026-03-10",
      "snippet": "Customer logs may not be shared externally unless anonymized and approved..."
    },
    {
      "source_id": "doc_2",
      "freshness": "2026-01-22",
      "snippet": "Public talks require review for customer-identifiable details..."
    },
    {
      "source_id": "doc_3",
      "freshness": "2025-12-01",
      "snippet": "Customer A contract prohibits disclosure of operational metrics..."
    }
  ],
  "output_schema": {
    "recommendation": "string",
    "reasoning_summary": "string",
    "citations": "array",
    "escalate": "boolean",
    "uncertainty": "low | medium | high"
  }
}
```

The context builder separates instructions from retrieved text so a malicious or stale document cannot override system behavior.

---

# 6. Model Call

The model gateway chooses a stronger model because the request is high risk.

Logged metadata:

```json
{
  "model": "strong_reasoning_model",
  "route": "risk_sensitive_v2",
  "prompt_version": "policy_answer_v12",
  "temperature": 0.1,
  "input_tokens": 1800,
  "output_tokens": 350
}
```

Example model output:

```json
{
  "recommendation": "Do not use Customer A's deployment logs in a public talk without explicit approval. If you need to discuss the architecture, use synthetic or fully anonymized examples and submit the material for review.",
  "reasoning_summary": "The relevant policies require approval for externally shared customer-derived material, and Customer A's contract restricts disclosure of operational metrics.",
  "citations": ["doc_1", "doc_2", "doc_3"],
  "escalate": true,
  "uncertainty": "low"
}
```

---

# 7. Validation

The validation layer checks:

* output is valid JSON
* all citations refer to retrieved documents
* recommendation does not invent policy
* high-risk category includes escalation decision
* answer does not include restricted log contents

If validation fails, the orchestrator can retry with a repair prompt or escalate to human review.

---

# 8. Response

The user receives:

```text
You should not use Customer A's deployment logs in a public conference talk
without explicit approval. If you want to discuss the architecture, use
synthetic or fully anonymized examples and submit the material for review.

Sources: customer data policy, external talks policy, Customer A contract summary.

I recommend sending this to review before including it in your talk.
```

The product may include a button:

```text
Submit talk material for review
```

This turns the answer into a workflow without letting the model directly approve the action.

---

# 9. Persistence and Feedback

The system stores:

```json
{
  "trace_id": "trace_999",
  "request_id": "req_123",
  "user_id": "u_42",
  "intent": "policy_question",
  "risk": "high",
  "prompt_version": "policy_answer_v12",
  "model_route": "risk_sensitive_v2",
  "retrieved_document_ids": ["doc_1", "doc_2", "doc_3"],
  "excluded_document_ids": ["doc_4"],
  "validation_status": "passed",
  "escalated": true,
  "feedback": null
}
```

Later feedback may include:

```json
{
  "trace_id": "trace_999",
  "reviewer_label": "correct",
  "reviewer_notes": "Good escalation. Add a link to speaker review form next time."
}
```

That feedback becomes an eval case or product improvement.

---

# 10. What This Example Tests in Interviews

This lifecycle demonstrates:

* permission-aware retrieval
* risk-based model routing
* context assembly
* structured output
* validation
* escalation
* traceability
* feedback storage

The important move is showing how the system behaves before, during, and after the model call.
