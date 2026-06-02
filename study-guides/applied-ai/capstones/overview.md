---
layout: page
title: "Applied AI Capstone Scenarios"
guide_type: overview
---
# Applied AI Capstone Scenarios

The chapters teach the pieces. The capstones compose them into realistic systems.

Use these as interview drills. For each scenario, practice explaining the architecture, tradeoffs, failure modes, evaluation plan, security boundaries, learning loop, rollout strategy, software constraints, and inference constraints without reading from the page.

---

## Capstone Template

Every capstone should cover:

1. Problem statement.
2. Success criteria.
3. Requirements and constraints.
4. Architecture and request/data flow.
5. Key design decisions.
6. Evaluation plan.
7. Failure modes.
8. Learning loop.
9. Rollout and operations.
10. Interview answer.

---

## Scenarios

| Capstone | Main Focus | Best After |
| -------- | ---------- | ---------- |
| [Secure Enterprise RAG Support Agent](secure_enterprise_rag_support_agent.html) | RAG, permissions, support tools, evals, learning loops | Chapters 2, 3, 5, 8 |
| [Private Repo Coding Assistant](private_repo_coding_assistant.html) | code retrieval, sandboxed tools, patch safety, tests | Chapters 2, 3, 4, 8, 11 |
| [Eval-to-Rollout Pipeline](eval_to_rollout_pipeline.html) | eval reports, uncertainty, canaries, rollback | Chapters 5, 6, 7 |
| [Production Feedback Learning Loop](production_feedback_learning_loop.html) | traces, labels, data governance, post-training updates | Chapters 5, 6, 8, 12 |
| [Secure Agent Platform](secure_agent_platform.html) | multi-agent platform, tool governance, auditability | Chapters 4, 7, 8, 11 |
| [Multi-Tenant LLM Inference Platform](multi_tenant_llm_inference_platform.html) | GPU serving, token-aware routing, KV cache, tenant isolation | Chapters 7, 8, 12, 13 |
| [Research Copilot with Evidence Synthesis](research_copilot_evidence_synthesis.html) | evidence retrieval, citations, conflicting sources | Chapters 3, 5, 9, 10 |
| [Durable Workflow Automation Agent](durable_workflow_automation_agent.html) | workflow engine, idempotency, approvals, long-running state | Chapters 4, 8, 11 |
| [Multimodal Voice Assistant](multimodal_voice_assistant.html) | voice, images, streaming, interruption, privacy | Chapters 2, 4, 7, 8 |
| [Batch Document Intelligence Pipeline](batch_document_intelligence_pipeline.html) | batch processing, extraction, validation, provenance | Chapters 3, 5, 11, 12, 10 |

---

## Capability Matrix

| Capstone | Retrieval | Agents | Evals | Learning | Security | Serving | Software | Platform | Inference | Advanced |
| -------- | --------- | ------ | ----- | -------- | -------- | ------- | -------- | -------- | --------- | -------- |
| Secure Enterprise RAG Support Agent | high | medium | high | medium | high | medium | medium | medium | low | low |
| Private Repo Coding Assistant | high | high | medium | low | high | medium | high | medium | low | low |
| Eval-to-Rollout Pipeline | low | low | high | medium | medium | high | high | high | medium | low |
| Production Feedback Learning Loop | medium | medium | high | high | high | medium | high | high | medium | high |
| Secure Agent Platform | medium | high | high | medium | high | high | high | high | medium | medium |
| Multi-Tenant LLM Inference Platform | low | low | medium | low | high | high | high | high | high | low |
| Research Copilot with Evidence Synthesis | high | medium | high | medium | medium | medium | medium | medium | low | high |
| Durable Workflow Automation Agent | medium | high | medium | medium | high | medium | high | medium | low | medium |
| Multimodal Voice Assistant | medium | high | high | medium | high | high | high | medium | medium | high |
| Batch Document Intelligence Pipeline | high | low | high | high | medium | low | high | high | low | high |

---

## Drill Prompts

After reading a capstone, answer these without looking:

1. What is the first clarifying question you would ask the interviewer?
2. What is the highest-risk failure mode?
3. Which component enforces permissions?
4. What should be logged for incident response?
5. What metric could improve while the product gets worse?
6. What would you canary first?
7. What rollback lever would you want most?
8. Which failures become evals instead of training data?
9. Is the bottleneck request count, token count, memory, communication, or scheduling?
10. Which chapter concepts are being composed?
