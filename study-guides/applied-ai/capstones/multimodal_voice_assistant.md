---
layout: page
title: "Capstone: Multimodal Voice Assistant"
guide_type: capstone
---

# Capstone: Multimodal Voice Assistant

## Problem

Design a multimodal voice assistant that handles speech, images, text, tools, streaming responses, interruptions, and privacy-sensitive user context.

## Success Criteria

* low latency turn-taking,
* accurate speech recognition and grounding,
* safe tool use,
* graceful interruption handling,
* clear privacy controls for audio/images.


## Requirements

Functional requirements:

* handle audio, text, and image inputs,
* stream partial responses with low time-to-first-audio,
* support user interruption and cancellation,
* confirm risky actions when speech recognition is uncertain,
* ground visual claims in image evidence.

Operational requirements:

* define retention for audio, images, transcripts, and embeddings,
* track latency by ASR, model, tool, and TTS stage,
* redact sensitive media from logs,
* route private media only to approved providers,
* evaluate across accents, noisy environments, and device types.

## Architecture

```text
audio/image/text input -> modality processors -> context builder -> model/router -> tool policy -> streaming response -> trace/eval store
```

## Key Design Decisions

### Streaming and interruption first

Voice UX depends on time-to-first-audio, partial hypotheses, barge-in handling, and cancellation. The system must cancel stale model/tool work when the user interrupts.

### Privacy-aware media handling

Raw audio, images, transcripts, embeddings, and traces have different retention and access policies.

## Evaluation Plan

Measure word error rate, task completion, latency, interruption recovery, hallucinated visual claims, tool safety, and privacy-policy adherence.

## Failure Modes

| Failure | Mitigation |
| ------- | ---------- |
| stale response after interruption | cancellation tokens and turn IDs |
| visual hallucination | image-grounded claim checks |
| accidental media retention | retention policy and redaction |
| tool action from misheard command | confirmation for risky actions |

## Learning Loop

Misrecognitions and interruption failures become eval slices. Sensitive media requires explicit eligibility before training use.


## Rollout Plan

1. Start with internal or low-risk traffic.
2. Run shadow or review-only mode before autonomous behavior.
3. Canary by tenant, workflow, or document type.
4. Monitor quality, latency, cost, safety, and escalation metrics.
5. Keep rollback available for prompts, models, tools, policies, and routing.

## Interview Answer

I would design it as a streaming multimodal system, not just an LLM call. The hard parts are latency, cancellation, modality grounding, privacy, and safe tool execution under uncertain speech input.
