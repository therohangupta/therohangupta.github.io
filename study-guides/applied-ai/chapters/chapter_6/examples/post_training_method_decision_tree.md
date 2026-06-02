# Post-Training Method Decision Tree

Use this when choosing how to improve model behavior.

```text
Do you have high-quality demonstrations?
  yes -> SFT or PEFT
  no  -> continue

Can humans reliably compare two outputs?
  yes -> DPO / preference optimization
  no  -> continue

Can you define and validate a reward signal?
  yes -> RLHF / RL-style optimization
  no  -> continue

Is the problem online action selection with measurable reward?
  yes -> bandits or online policy experiments
  no  -> continue

Can a stronger teacher label or score the student's own rollouts?
  yes -> distillation / on-policy distillation
  no  -> improve evals, retrieval, prompts, or product design first
```

## Default Rule

Do not update weights when the failure is caused by retrieval, prompt construction, tool policy, stale data, missing validation, or unclear product requirements.
