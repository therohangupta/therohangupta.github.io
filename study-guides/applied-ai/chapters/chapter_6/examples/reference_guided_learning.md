# Reference-Guided Learning Taxonomy

Reference-guided learning is not one algorithm. It is a pattern where a fast learner updates against a frozen, delayed, smoothed, privileged, or filtered signal.

The reference is a composition of existing primitives:

| Method | Fast Object | Reference Object | Signal | Update Cadence | Main Failure Mode |
| ------ | ----------- | ---------------- | ------ | -------------- | ----------------- |
| DQN | online Q network | target Q network | bootstrapped value target | periodic copy | target too stale or too unstable |
| SAC | online Q networks / policy | target Q network | value target | soft target update | critic error shapes policy badly |
| PPO | current policy | old policy snapshot | clipped ratio / KL region | per batch | trust region too tight or too loose |
| RLHF | policy model | frozen reference policy and reward model | reward plus KL anchor | reference usually fixed | reward hacking or over-anchoring |
| Knowledge distillation | student model | larger teacher or ensemble | soft labels / logits | teacher fixed | transfers teacher bias |
| BYOL / Mean Teacher | online student encoder | EMA teacher encoder | representation target | EMA every step | representation collapse |
| OPSD | student policy | privileged-context teacher | reverse KL over rollout tokens | teacher fixed or promoted | noisy token-level updates |
| RMSD | student policy | privileged teacher plus judge mask | masked reverse KL | teacher fixed or promoted | judge selects wrong tokens |

## What Changes Across Methods

The table looks uniform, but the reference has a different meaning in each row.

In DQN and SAC, the reference is mostly a **stability device**. The target is bootstrapped from model predictions, so the learner needs a slowly moving copy to avoid chasing its own newest estimate.

In PPO and RLHF, the reference is mostly a **constraint**. The old or frozen policy defines what "nearby behavior" means. The goal is not to copy the reference forever; the goal is to make the update local enough that the reward or preference signal cannot push the policy into strange regions too quickly.

In knowledge distillation, the reference is mostly a **teacher**. The teacher distribution carries information about which alternatives are plausible. The student learns a compressed or cheaper version of that behavior.

In BYOL-style representation learning, the reference is a **smoothed representation target**. The teacher is not providing labels. It is providing stable geometry for the student to match under different views.

In RMSD, the reference is both **privileged teacher** and **credit-assignment filter**. The teacher says how behavior should shift, and the mask says which token positions deserve gradient.

## How To Identify The Pattern

Ask four questions:

1. What is changing quickly?
2. What is changing slowly or not at all?
3. Is the reference acting as an objective, constraint, credit-assignment aid, or information filter?
4. What happens if the reference updates too quickly or too slowly?

Then ask the production question:

```text
What must be versioned to reproduce this update?
```

For DQN, that might be the target update schedule. For RLHF, it is the reference model and reward model. For RMSD, it is the teacher prompt, judge prompt, selected token masks, and rollout policy.

## Interview Framing

Say:

> I would not call the reference a new primitive. It composes objective design, constraints, credit assignment, and update scheduling. The same object can be a teacher in one method, an anchor in another, and a credit-assignment device in a third.
