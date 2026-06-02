# GPU Serving Incident Debugging

## Incident

After a new prompt template ships, p99 latency for an internal assistant jumps from 4 seconds to 19 seconds. Error rate stays flat.

## Initial Clue

Request count is unchanged, but input tokens increase sharply.

| Metric | Before | After |
| ------ | ------ | ----- |
| p95 input tokens | 6,000 | 31,000 |
| p95 output tokens | 900 | 950 |
| p99 queue time | 600 ms | 8.4 s |
| p99 prefill time | 1.2 s | 7.1 s |
| p99 decode time | 2.1 s | 2.4 s |
| KV memory pressure | 62% | 91% |

## Diagnosis

The issue is not worse decode or model quality. The new template includes too many retrieved snippets, causing prefill and KV memory pressure. Queue time rises because long prompts occupy scheduler capacity.

## Fix

* Cap retrieved context by token budget.
* Add context compression for long documents.
* Route long-context requests to a separate pool.
* Add an eval slice for prompt length.
* Add a release gate on p99 prefill time and KV memory.

## Lesson

Prompt and retrieval changes are infrastructure changes. They can alter prefill, queueing, memory, and cost even when the model artifact is unchanged.
