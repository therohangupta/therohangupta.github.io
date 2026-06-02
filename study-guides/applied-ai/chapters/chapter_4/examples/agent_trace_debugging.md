# Agent Trace Debugging Artifact

Use this artifact when debugging an agent failure. The goal is to find the first bad transition, not only judge the final answer.

## Trace

| Step | State | Action | Observation | Issue |
| ---- | ----- | ------ | ----------- | ----- |
| 1 | user asks for refund eligibility | retrieve policy | policy v3 returned | ok |
| 2 | policy text in context | call account tool | account shows chargeback | ok |
| 3 | account and policy available | draft refund approval | ignores chargeback exclusion | first failure |
| 4 | draft exists | send response | refund promised incorrectly | downstream symptom |

## Debugging Questions

* Did the planner choose the right next action?
* Did retrieval return the right evidence?
* Did the model use the evidence correctly?
* Did a validator catch the bad action?
* Should this failure become an eval, a policy check, or training data?

## Fix

The first failure is evidence use, not retrieval. Add a deterministic policy validator for chargeback exclusions, add this trace to trajectory evals, and require approval for refund promises above the risk threshold.
