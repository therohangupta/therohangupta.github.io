---
layout: page
title: "Capstone: Private Repo Coding Assistant"
guide_type: capstone
---
# Capstone: Private Repo Coding Assistant

Design an AI coding assistant that can answer questions about a private repository, propose patches, run safe tools, and preserve developer control.

---

## 1. Problem Statement

Developers want help understanding code, making small edits, debugging failures, and running tests. The assistant can read repository context and use tools, but it must not leak secrets, run dangerous commands, or rewrite code without review.

Clarifying questions:

* Does the assistant run locally, remotely, or in a hybrid setup?
* Can repository content be sent to external model providers?
* Which commands are allowed without approval?
* Is the assistant allowed to edit files directly or only propose diffs?

---

## 2. Success Criteria

Good means:

* retrieves the right files, symbols, tests, and terminal context,
* proposes small reviewable patches,
* runs only approved commands in a sandbox,
* avoids leaking private code or secrets,
* explains failures with traceable evidence,
* improves developer throughput without hiding risk.

---

## 3. Requirements

Functional requirements:

* code search by symbol, path, and semantic similarity,
* recent edit and diagnostic awareness,
* patch generation,
* test/lint execution,
* terminal output interpretation,
* rollback-friendly edit history.

Security and privacy requirements:

* repository access scoped to authenticated user,
* no cross-workspace context leakage,
* secret scanning before prompt construction and tool output logging,
* sandboxed command execution,
* allowlist or policy review for commands that mutate files or contact networks.

Latency and cost requirements:

* fast local context retrieval,
* incremental indexing,
* model routing by task complexity,
* streaming for explanations.

---

## 4. Architecture

```text
IDE UI
  -> task router
  -> repo indexer
  -> context selector
  -> model gateway
  -> patch planner
  -> tool runner sandbox
  -> diff viewer
  -> trace and eval logger
```

The system should separate context selection, reasoning, file edits, and command execution. A model response should not directly mutate the repository without going through an edit tool or patch application layer.

---

## 5. Request Flow

```text
developer asks for a bug fix
  -> gather open file, cursor, diagnostics, recent edits
  -> retrieve related symbols and tests
  -> model proposes plan and patch
  -> patch tool applies bounded diff
  -> sandbox runs targeted tests
  -> model summarizes result
  -> trace records files, commands, outputs, and model versions
```

---

## 6. Key Design Decisions

### Retrieval should be hybrid

Code search needs exact symbol/path search and semantic retrieval. Embeddings help with conceptual questions, but exact references matter for correctness.

### Patches beat blind rewrites

Patch-based edits are reviewable and reversible. They also reduce accidental deletion of user changes.

### Tool execution needs policy

Commands should be categorized:

| Command Type | Example | Control |
| ------------ | ------- | ------- |
| read-only | `ls`, test discovery | usually allowed |
| local validation | `pytest path/test.py` | sandboxed |
| file mutation | formatter, codegen | approval or explicit user request |
| network | package install, external API | approval and restrictions |
| destructive | delete, reset, force push | block unless explicitly approved |

### Secrets are context hazards

Private repo context can contain tokens, keys, customer data, or credentials. Secret scanning should happen before sending context to model providers or logs.

---

## 7. Evaluation Plan

Offline evals:

* issue-to-patch benchmark tasks,
* unit test pass rate,
* patch minimality,
* no unrelated file changes,
* command safety,
* retrieval hit rate for relevant files,
* secret leakage tests.

Human review:

* code correctness,
* maintainability,
* whether the patch follows repo style,
* whether the explanation matches the change.

Online metrics:

* accepted patch rate,
* revert rate,
* test pass rate after assistant edits,
* time to task completion,
* dangerous command block rate,
* user interruption rate.

---

## 8. Failure Modes

| Failure | Symptom | Mitigation |
| ------- | ------- | ---------- |
| Wrong context | edits unrelated code | hybrid retrieval, recent-file weighting, trace review |
| Over-editing | broad rewrite for small bug | patch-size limits, minimality evals |
| Unsafe command | runs destructive shell command | command policy and sandbox |
| Secret leakage | key appears in prompt or log | secret scanning and redaction |
| Test tunnel vision | passes narrow test but breaks behavior | broader regression selection |
| User change overwrite | assistant reverts manual edits | read latest file before patching, diff conflict checks |

---

## 9. Learning Loop

Useful feedback signals:

* patch accepted or rejected,
* user edits after assistant patch,
* tests passed or failed,
* command blocked or approved,
* reviewer comments,
* reverted commits.

Potential updates:

* retrieval tuning from missed relevant files,
* SFT examples for repo-specific style,
* preference pairs from accepted vs rejected patches,
* eval cases from regressions,
* tool policy updates for unsafe command attempts.

Raw private code should not automatically become training data. Training eligibility depends on repo policy, user consent, and redaction.

---

## 10. Production Rollout

Start with read-only Q&A, then patch suggestions, then user-approved patch application, then sandboxed validation. Expand command access gradually.

Rollback levers:

* disable command execution,
* disable patch application,
* route to safer model,
* restrict context sources,
* revert prompt or retrieval index version.

---

## 11. Interview Answer

I would build the coding assistant as a repo-aware workflow system. It would use hybrid retrieval over files, symbols, diagnostics, and tests, then produce bounded patches rather than blind rewrites. Tool execution would run in a sandbox with command policies, and dangerous or networked commands would require approval. I would evaluate patch correctness, test pass rate, minimality, retrieval quality, secret leakage, and command safety. Accepted patches, failed tests, and reviewer edits would feed evals and carefully governed training data.
