---
layout: page
title: "Capstone: Research Copilot with Evidence Synthesis"
guide_type: capstone
---

# Capstone: Research Copilot with Evidence Synthesis

## Problem

Design a research copilot that searches a corpus, synthesizes evidence, cites sources, flags uncertainty, and helps users compare conflicting claims.

## Success Criteria

* answers are grounded in cited evidence,
* unsupported claims are refused or marked uncertain,
* conflicting sources are surfaced instead of hidden,
* retrieval freshness and source authority are visible,
* users can inspect evidence trails.


## Requirements

Functional requirements:

* search across papers, docs, notes, and web-like sources with provenance,
* preserve source metadata: author, date, authority, freshness, and access scope,
* produce claim-level citations,
* surface conflicting evidence instead of collapsing it into one answer,
* support follow-up questions that reuse the evidence table.

Operational requirements:

* cache retrieval safely by corpus/version/user scope,
* log claim, citation, and verifier decisions,
* support human review for high-impact research outputs,
* keep source snapshots or IDs so answers are reproducible.

## Architecture

```text
query -> intent classifier -> search/retrieval -> reranking -> evidence table -> synthesis model -> citation verifier -> response
```

## Key Design Decisions

### Evidence before synthesis

The system should build an evidence object before generation. The model should synthesize from structured evidence, not from an opaque blob of retrieved text.

### Citation verification

A verifier checks whether each generated claim is supported by cited sources. Unsupported claims become warnings, edits, or refusals.

## Evaluation Plan

Evaluate citation support, source precision, freshness, contradiction handling, answer usefulness, and abstention quality.

## Failure Modes

| Failure | Mitigation |
| ------- | ---------- |
| citation does not support claim | citation verifier and regression eval |
| stale source dominates | freshness scoring and source metadata |
| conflicting evidence hidden | contradiction detector and explicit compare mode |
| model over-synthesizes | claim-level grounding checks |

## Learning Loop

Bad citations become eval cases. Source usefulness feedback updates ranking. Unsupported claims do not directly become training data without review.


## Rollout Plan

1. Start with internal or low-risk traffic.
2. Run shadow or review-only mode before autonomous behavior.
3. Canary by tenant, workflow, or document type.
4. Monitor quality, latency, cost, safety, and escalation metrics.
5. Keep rollback available for prompts, models, tools, policies, and routing.

## Interview Answer

I would design around evidence provenance. Retrieval produces source objects with metadata, reranking selects candidate evidence, the model synthesizes with citations, and a verifier checks claim support before the answer ships.
