---
layout: page
title: "Learning Loops Practice Questions"
guide_type: questions
---
# Chapter 5 — Practice Questions

Explanatory material for this chapter lives in [`guide.md`](guide.html).

---

# Common Interview Questions and Sample Answers

---

## Question 1

**What is the simplest mental model for a learning loop?**

### Sample Answer

A learning loop turns observed behavior into future behavior. A policy acts, the system observes feedback, feedback is converted into training signal, and a candidate update changes the policy. The hard part is deciding which feedback is trustworthy enough to optimize.

---

## Question 2

**How does reinforcement learning connect to Chapter 0's idea of optimization?**

### Sample Answer

Chapter 0 treats optimization as shaping parameters toward an objective. RL uses reward as that objective signal. The difference is that the signal often comes from interaction rather than a fixed label, so reward design and credit assignment become central.

---

## Question 3

**What is the difference between reward and feedback?**

### Sample Answer

Feedback is the raw observation, such as a thumbs up, preference label, click, correction, or task outcome. Reward is the interpreted scalar signal used for optimization. Raw feedback can be noisy or biased, so it should not automatically become reward.

---

## Question 4

**What is a policy in an LLM post-training system?**

### Sample Answer

The policy is the model distribution that produces behavior. For an LLM, it maps a prompt and previous tokens to a distribution over next tokens. Updating the policy changes which responses, styles, tool calls, and refusals are more likely.

---

## Question 5

**What are value and advantage used for?**

### Sample Answer

Value estimates expected future reward from a state or partial trajectory. Advantage estimates whether an action was better or worse than expected. They help reduce noise and assign credit, especially when feedback is delayed across a multi-step trajectory.

---

## Question 6

**Why is exploration vs exploitation a production concern?**

### Sample Answer

Exploitation uses the current best-known behavior, while exploration tries uncertain behavior to discover improvements. Exploration can harm users if bad variants are shown live, but without exploration the system may get stuck. Production systems usually control exploration with bandits, canaries, shadow traffic, or offline evaluation.

---

## Question 7

**Why is trajectory logging important for learning loops?**

### Sample Answer

Final answers do not explain how behavior happened. Trajectory logs capture prompts, model versions, tool calls, observations, candidate outputs, validation results, and feedback. That makes failures attributable and turns production behavior into useful evaluation or training data.

---

## Question 8

**When would you use SFT instead of RLHF or DPO?**

### Sample Answer

I would use SFT when I have high-quality demonstrations of the desired behavior. It is simpler and more stable than RLHF, and it is good for teaching format, domain style, and task patterns. It is weaker when ranking plausible alternatives is easier than writing ideal answers.

---

## Question 9

**What is the difference between RLHF and DPO?**

### Sample Answer

RLHF usually trains a reward model from human preferences and then optimizes the policy against that reward model, often with a KL penalty to keep it near a reference model. DPO directly optimizes the policy from chosen-vs-rejected preference pairs without the same separate RL loop.

---

## Question 10

**Why does RLHF often use a KL penalty?**

### Sample Answer

The KL penalty keeps the updated policy close to a reference policy. Without it, the model may drift into strange behavior that exploits reward-model weaknesses. It is a regularization term that limits how aggressively the policy changes under an imperfect reward.

---

## Question 11

**What is reward hacking?**

### Sample Answer

Reward hacking happens when the model maximizes the reward proxy without satisfying the real goal. For example, it may learn to produce longer answers because the reward model associates length with quality, or it may add fake citations because citations look trustworthy.

---

## Question 12

**How does reward hacking relate to Chapter 0 objective shaping?**

### Sample Answer

Chapter 0 says optimization amplifies the objective. Reward hacking is what happens when the objective is only a proxy for the intended behavior. The optimizer finds patterns that increase reward even if they violate the real goal.

---

## Question 13

**Why can preference optimization overfit to style over substance?**

### Sample Answer

Humans often reward answers that are polished, confident, polite, or well formatted. Those signals are easier to observe than factual correctness or deep reasoning. If the preference dataset over-rewards surface features, the model can become more pleasing while becoming less correct.

---

## Question 14

**What is catastrophic forgetting in continual learning?**

### Sample Answer

Catastrophic forgetting is when new training improves recent or narrow tasks while damaging older capabilities. A model fine-tuned on support transcripts might become better at support tone but worse at general reasoning or safety. Replay data, broad regression evals, and gated updates help reduce the risk.

---

## Question 15

**Why should raw user feedback not directly update an LLM?**

### Sample Answer

Raw user feedback can be noisy, biased, adversarial, private, or unrelated to model quality. A thumbs up may reward tone rather than truth. A click may reward curiosity rather than relevance. The safer path is to log, filter, label, evaluate, and gate updates before changing the model.

---

## Question 16

**How would you design a safe continual-learning pipeline?**

### Sample Answer

I would collect trajectory data with privacy filtering, select candidate examples, label or verify them, mix them with replay data, train a candidate model, run broad quality and safety evals, canary the model, monitor production metrics, and keep rollback ready. I would treat model updates like production releases.

---

## Question 17

**When are bandits a better fit than full RL?**

### Sample Answer

Bandits are a better fit when the system chooses among actions or variants and observes relatively direct reward, but does not need long-horizon planning. Examples include choosing a prompt template, model variant, retrieval depth, ranking policy, or UI treatment.

---

## Question 18

**What is distribution drift in a learning loop?**

### Sample Answer

Distribution drift means the data the system sees changes over time. Users change, products change, the UI changes, and the model itself changes which examples are observed. A reward model or preference dataset that worked before may stop matching current behavior.

---

## Question 19

**How would you connect evaluation data from Chapter 4 to learning data in Chapter 5?**

### Sample Answer

Evaluation data identifies where behavior succeeds or fails. Those failures can become labeling tasks, preference comparisons, SFT examples, regression tests, or reward-model training cases. The important step is preserving the distinction between eval data used for gating and training data used for updating.

---

## Question 20

**What is a strong interview answer for "how would you improve this model from user feedback?"**

### Sample Answer

I would say that I would not train directly on raw feedback. I would define the target behavior, log full trajectories, filter sensitive or low-quality data, collect preference labels or verified outcomes, choose SFT, DPO, RLHF, or bandits based on the signal, evaluate offline, gate for safety and regressions, canary the update, and monitor for drift.

---

## Question 21

**What should gate an online model or policy update before it reaches all users?**

### Sample Answer

The update should pass offline evals, safety evals, slice-based regression checks, latency/cost checks, and canary monitoring. It should also have a rollback plan and clear ownership. For learning loops, the gate matters because bad updates can change the future data distribution and create feedback loops.

---

## Question 22

**How would you roll back after a bad learning update?**

### Sample Answer

Keep model, prompt, reward, and data versions immutable so the system can revert to the last known-good version. Stop further data collection from the bad policy if it is contaminating logs, mark affected trajectories, and run regression analysis to identify which slices failed. Then fix the data, reward, or gating process before trying another update.

---

## Question 23

**What is evaluation drift in a learning loop?**

### Sample Answer

Evaluation drift happens when the eval set or metric stops representing the current product distribution. As the model changes, users may change behavior, routes may change, and new failure modes may appear. A learning loop needs fresh production samples, slice monitoring, held-out sets, and periodic human review so the gate stays meaningful.

---

## Question 24

**Why is it risky to train directly on thumbs-up / thumbs-down feedback?**

### Sample Answer

Raw user feedback is noisy and biased. Users may rate style instead of correctness, only complain when angry, or reward confident but wrong answers. Feedback also lacks context unless full traces are stored. It should be filtered, calibrated, joined with task outcomes, and often converted into preference or supervised examples before training.

---

## Question 25

**How can a production RL or bandit loop make a product worse even while optimizing its reward?**

### Sample Answer

The reward may be incomplete. A system optimizing clicks, short-term satisfaction, or task completion may learn to avoid hard cases, over-escalate, become too verbose, or exploit UI behavior. In production, the reward must be constrained by safety, quality, fairness, latency, and long-term user trust metrics.

---
