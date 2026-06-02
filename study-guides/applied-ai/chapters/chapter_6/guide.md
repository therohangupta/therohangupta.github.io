---
layout: page
title: "Chapter 6: Learning Loops"
guide_type: chapter
---

# Chapter 6 — Learning Loops

This chapter explains how model behavior improves after deployment data, evaluation data, human feedback, and environment outcomes become training signal.

Chapter 0 framed optimization as signal shaping: choose an objective, expose the model to data, and update parameters so future behavior moves toward the objective. Chapter 5 applies that same primitive to systems that learn from interaction. The hard part is not saying "use RL" or "collect feedback." The hard part is deciding what signal should be trusted, how it should update the policy, and how to prevent the loop from optimizing the wrong thing.

The interview angle is:

* can you decompose learning loops into reward, policy, value, feedback, exploration, and data?
* can you explain when SFT, RLHF, DPO, reward modeling, bandits, or continual learning are appropriate?
* can you identify the failure modes before the model learns bad behavior?
* can you connect model improvement to production serving, monitoring, and safety gates?

Security note: learning loops are also data-governance systems. Raw traces, user feedback, and model-generated data need privacy filtering, training eligibility decisions, and quarantine when a bad policy produced the data. See [Chapter 8: Security, Privacy, and Trust Boundaries](../chapter_8/guide.html) and the [Production Feedback Learning Loop capstone](../../capstones/production_feedback_learning_loop.html).

---

## Table of Contents

- TOC
{:toc}

---

# 1. The Core Mental Model

A learning loop is a system that turns observed behavior into future behavior.

The smallest version looks like this:

```text
policy produces behavior
environment or users produce feedback
feedback becomes training signal
training updates the policy
updated policy produces new behavior
```

This is the same optimization story from Chapter 0, but with a new source of signal. Instead of only learning from a static dataset, the system can learn from preferences, rewards, outcomes, corrections, traces, tool results, or user interactions.

That makes learning loops powerful and dangerous.

They are powerful because production data contains information that the original training set did not have. They are dangerous because production data is biased, delayed, incomplete, adversarial, and shaped by the current model's behavior. A model that learns from its own bad outputs can become more confident in the wrong direction.

The central question is not "how do we update the model?" It is:

```text
What feedback should be allowed to change future behavior?
```

Every serious answer to RLHF, preference optimization, online learning, or continual learning is a variation on that question.

---

# 2. Core Primitives

## 2.1 Reward

A reward is a scalar signal that says how good an action, answer, trajectory, or outcome was.

In a game, reward might be +1 for winning. In a recommender, it might be click-through, watch time, purchase conversion, or long-term retention. In an LLM assistant, it might be a learned score from a reward model, a human preference label, a task success signal, or a safety-adjusted quality score.

The key idea:

```text
reward is not the same as correctness
```

Reward is a proxy. It compresses a messy human or environment judgment into an optimization target. That compression is useful because gradient-based learning needs a target, but it is risky because the target can be incomplete or wrong.

From Chapter 0's view, reward is objective shaping. If the reward is misspecified, optimization will amplify the misspecification.

## 2.2 Policy

A policy is the behavior-producing function.

In classic RL, the policy maps state to action:

```text
pi(a | s)
```

In an LLM, the policy maps context to a distribution over next tokens:

```text
pi(token | prompt, previous_tokens)
```

When people say "the policy model" in RLHF, they usually mean the LLM being updated. The model is not merely storing facts; it is a conditional action distribution. Post-training changes which completions, tool calls, refusals, explanations, and styles are likely under different contexts.

## 2.3 Value

Value estimates how good a state or partial trajectory is expected to be.

In RL notation:

```text
V(s) = expected future reward from state s
Q(s, a) = expected future reward after taking action a in state s
```

Value matters when feedback is delayed. If an agent takes ten steps and only receives final success or failure, value estimation helps assign credit to earlier decisions.

For LLM systems, value-like ideas appear in:

* process reward models that score intermediate reasoning steps
* rollout evaluators that estimate whether a partial solution is promising
* agents that choose which branch to continue exploring
* rerankers that estimate final answer quality before returning an answer

## 2.4 Advantage

Advantage measures whether an action was better or worse than expected:

```text
A(s, a) = Q(s, a) - V(s)
```

If the outcome was good but every available action was likely to be good, the advantage may be small. If the outcome was much better than expected, the advantage is large.

Advantage is useful because it reduces noise. Instead of reinforcing every token in a successful response equally, the learner tries to reinforce choices that improved the outcome relative to a baseline.

Interview framing:

* reward says "how good was this?"
* value says "how good did we expect this situation to be?"
* advantage says "did this action outperform expectation?"

## 2.5 Feedback

Feedback is the raw observation that can become learning signal.

Common feedback sources include:

* explicit human preference: response A is better than response B
* rating: thumbs up, star score, CSAT
* correction: user edits the answer
* outcome: task succeeded or failed
* tool result: code compiled, test passed, API call succeeded
* safety review: output violated or satisfied policy
* behavioral metric: click, dwell time, conversion, churn

Feedback is not automatically reward. It must be interpreted. A user clicking a result may mean relevance, curiosity, manipulation, or bad UI placement. A thumbs up may mean the answer sounded good, not that it was correct. A rejected support answer may be bad because of content, tone, latency, or user frustration outside the model.

Good learning systems separate raw feedback from trusted training signal.

## 2.6 Exploration vs Exploitation

Exploitation means choosing the behavior that currently looks best. Exploration means trying uncertain behavior to learn whether something better exists.

In production systems, exploration has a cost. Showing users worse recommendations, testing a new model response style, or routing traffic to an experimental policy can harm user experience. But without exploration, the system can get stuck optimizing for what it already knows.

Common exploration patterns:

* epsilon-greedy action choice
* Thompson sampling
* upper confidence bound methods
* randomized ranking
* shadow traffic for model candidates
* limited canary rollout
* offline evaluation before online exposure

LLM systems often explore less directly than recommender systems. They may generate multiple candidate answers offline, label preferences, use rejection sampling, or run small canaries with strict safety gates.

## 2.7 Trajectory Data

A trajectory is a sequence of states, actions, observations, and rewards.

For a tool-using LLM agent, a trajectory might include:

```text
user request
model plan
tool call
tool result
model revision
final answer
user feedback
```

Trajectory data matters because the final answer alone hides the path that produced it. If an agent fails, you need to know whether the failure came from retrieval, planning, tool selection, tool output interpretation, memory, or final response generation.

Strong trajectory logging records:

* input context and prompt version
* model version and sampling parameters
* candidate outputs
* tool calls and observations
* intermediate decisions
* final response
* feedback and outcome
* safety filters and policy decisions

This data is the raw material for evaluation, reward modeling, debugging, and future training.

---

# 3. How the Primitives Compose

A learning loop composes the primitives into a control system:

```text
policy -> actions -> trajectory -> feedback -> reward estimate -> update decision -> policy
```

The composition is easy to draw and hard to operate.

The policy creates data. That data is not neutral because it reflects the current policy's strengths and weaknesses. Users react to that behavior, producing feedback. The system converts feedback into reward estimates or preferences. Training uses those estimates to update the policy. Then the new policy changes which data will be observed next.

This creates two nested loops:

```text
inner loop: model generates behavior for a request
outer loop: collected behavior changes future model behavior
```

Chapter 4 evaluation data becomes especially important here. Evaluation tells you whether a candidate update improves the behavior you care about before you expose it broadly. Without evaluation gates, the outer learning loop can turn noisy production feedback into durable model regression.

## Reference-Guided Updates

A recurring learning-loop pattern is to update a fast learner against a slower, frozen, delayed, privileged, or filtered reference process.

This is not a new primitive beside reward, policy, value, feedback, or trajectory data. It is a way those primitives compose.

The reference can act as:

* an **objective source**, such as teacher logits, pseudo-labels, reward-model scores, or search-generated targets,
* a **constraint**, such as a KL penalty to an old policy or frozen reference model,
* a **credit-assignment aid**, such as a critic, verifier, value estimate, or token-level relevance mask,
* an **information-flow device**, such as a checkpoint, EMA copy, privileged-context teacher, or delayed target network.

The practical reason is stability. If the learner chases targets produced by its own rapidly changing behavior, training can oscillate, collapse, or amplify mistakes. A slower reference gives the update a target that changes less quickly than the learner.

There are really three different benefits that often get blended together:

1. **Stability:** the reference changes slowly, so targets do not drift as quickly as the learner.
2. **Asymmetry:** the reference has information the learner does not have, such as privileged context, search results, human preference data, or a larger model's distribution.
3. **Selectivity:** the reference helps decide which parts of behavior deserve update pressure, such as value estimates for actions or token masks for relevant disagreements.

Those are different reasons. A DQN target network is mostly about stability. A large teacher model is mostly about asymmetry. RMSD is mostly about selectivity on top of asymmetry. A good explanation says which reason applies instead of treating all reference models as the same thing.

A generic loop looks like:

```text
fast learner produces behavior
slow/frozen/privileged reference scores, anchors, or generates targets
loss compares learner behavior to the reference-guided signal
learner updates
reference updates rarely, by EMA, checkpoint promotion, or not at all
```

This pattern includes RL target networks, PPO old-policy snapshots, RLHF reference models, teacher-student distillation, self-distillation, and verifier/search processes that are distilled into faster policies.

The failure mode depends on the role. If the reference is an objective source, a bad teacher teaches bad behavior. If it is a constraint, a too-strong reference prevents useful learning and a too-weak reference allows drift. If it is a credit-assignment aid, wrong attribution sends gradients to the wrong tokens, actions, or examples. If it is an information-flow device, stale or contaminated checkpoints preserve the wrong signal.

---

# 4. Training and Post-Training Pipeline

Modern LLM improvement is usually not one training method. It is a pipeline.

The common shape is:

```text
pretraining -> SFT -> preference data -> reward/preference optimization -> evaluation -> deployment -> monitoring -> data collection
```

## A Distributional View of Post-Training

A useful way to compare post-training methods is to ask:

```text
What distribution is this update trying to move the policy toward?
```

An LLM policy is a distribution over next tokens and full responses. Post-training changes the shape of that distribution. Different methods differ in what they treat as the target and how directly they pull the model toward it.

SFT has the clearest target. The dataset defines an external demonstration distribution, and cross-entropy training pulls the model toward the demonstrated tokens. This is useful when the model needs to learn a new format, task pattern, or behavior from examples. The risk is that the target distribution may be far from the model's original behavior, so the update can create broad pressure on unrelated capabilities.

RL is less imitation-like. The model samples from its own current policy, receives reward, and shifts probability toward actions or trajectories that scored better than expected. The target is not a fixed answer key. It is a reward-shaped improvement near the states the current policy actually visits.

On-policy distillation sits between the two. Like SFT, it uses a teacher signal. Like RL, the training contexts come from the student's own rollouts. The student is not merely copying an external dataset; it is receiving guidance on its own prefixes, mistakes, and local alternatives.

That gives an interview-useful distinction:

| Method | Training Data Comes From | Main Signal | Update Shape |
| ------ | ------------------------ | ----------- | ------------ |
| SFT | fixed external demonstrations | target tokens | imitate the dataset distribution |
| DPO / preference optimization | fixed preference pairs | chosen over rejected responses | shift likelihood toward preferred examples while anchored to a reference |
| RLHF / RL | policy rollouts | reward or advantage | reinforce higher-reward behavior under the current policy distribution |
| On-policy distillation | student rollouts | teacher logits or corrections | refine the student's local distribution toward a teacher |

This lens helps explain catastrophic forgetting. External datasets can pull the model toward behavior that is far from the starting policy. On-policy methods constrain the update to regions the model already visits, so the nearest task-solving behavior is often easier to learn without damaging unrelated behavior. That does not make on-policy methods automatically safe; the reward, teacher, or preference signal can still be biased. But it explains why data source matters, not only objective choice.

## 4.1 Supervised Fine-Tuning

Supervised fine-tuning trains the model to imitate desired outputs:

```text
prompt -> ideal response
```

SFT is useful when you can write or collect high-quality demonstrations. It teaches format, task behavior, domain style, and instruction following.

SFT is often the first post-training stage because it moves the base model into the right behavioral region. RL or preference optimization then refines choices within that region.

Tradeoff:

* SFT is stable and simple.
* SFT requires demonstration data.
* SFT teaches what to imitate, not necessarily what humans prefer among plausible alternatives.

## 4.2 Reward Modeling

A reward model learns to score outputs.

Instead of asking humans to assign perfect scalar rewards, systems often ask humans to compare outputs:

```text
prompt
response A
response B
label: B is better
```

The reward model is trained so preferred responses receive higher scores than rejected responses. Once trained, it can score many model outputs cheaply.

Reward models are useful because human labeling is expensive. They also introduce a new risk: if the reward model is wrong, the policy can learn to exploit it.

## 4.3 RLHF

RLHF stands for reinforcement learning from human feedback.

A simplified RLHF pipeline:

```text
1. Train or start with an instruction-following policy.
2. Generate multiple responses to prompts.
3. Collect human preferences between responses.
4. Train a reward model from preferences.
5. Optimize the policy to maximize reward model score.
6. Keep the updated policy close to the reference model with a KL penalty.
7. Evaluate, safety test, and deploy only if gates pass.
```

The KL penalty matters. Without it, the policy may drift into strange outputs that exploit the reward model. The reference model acts as an anchor.

RLHF is powerful when:

* quality depends on subjective human preference
* there are many plausible answers
* demonstrations are expensive
* ranking answers is easier than writing perfect answers

RLHF is risky when:

* the reward model does not capture truth or safety
* labels reward style over substance
* the policy can exploit reward-model blind spots
* the update is not gated by strong evals

## 4.4 DPO and Preference Optimization

Direct Preference Optimization, or DPO, optimizes directly from preference pairs without training a separate reward model in the same way as classic RLHF.

The training data still looks like:

```text
prompt
chosen response
rejected response
```

But the optimization objective directly increases the likelihood of the chosen response relative to the rejected response, while staying anchored to a reference policy.

The practical appeal:

* simpler than full RLHF
* more stable for many post-training workflows
* no online rollout loop required for the training step
* works well with curated preference datasets

The limitation:

* it is still only as good as the preference data
* it does not automatically solve exploration
* it can overfit to superficial preference patterns
* it may not optimize long-horizon interactive behavior as naturally as RL

In interviews, a clean distinction is:

```text
RLHF learns a reward model and then optimizes the policy against it.
DPO directly trains the policy from chosen-vs-rejected examples.
```

## 4.5 Parameter-Efficient Fine-Tuning: LoRA and Adapters

Full fine-tuning updates all or most of the model's weights.

That is powerful, but expensive:

* every trainable parameter needs gradient memory,
* optimizer states can be larger than the weights,
* checkpoints are large,
* deployment artifacts are heavy,
* the update can damage broad capabilities if the dataset is narrow.

Parameter-efficient fine-tuning, or PEFT, asks a different question:

```text
Can we adapt the model by training a small number of extra parameters
while keeping the base model mostly frozen?
```

This changes the **parameterization of the update**. Instead of letting optimization move the entire model, PEFT constrains where learning can happen.

### The Core Mental Model

The base model already contains broad capability.

PEFT adds a small learned modification:

```text
frozen base model
  + small trainable adaptation
  -> adapted behavior
```

So the model does not relearn language, reasoning, or world knowledge from scratch. It learns a targeted behavioral shift.

This is why PEFT sits naturally in post-training and continual learning:

* you already have a pretrained or instruction-tuned base model,
* you want a domain/task/style adaptation,
* you want to reduce training cost and blast radius,
* you still need eval gates because the behavior changed.

### LoRA

LoRA stands for low-rank adaptation.

The intuition:

Full fine-tuning changes a weight matrix:

```text
W -> W + Delta W
```

LoRA represents the update with two much smaller low-rank matrices:

```text
Delta W = A B
```

where `A` and `B` are trainable, but the original weight matrix `W` is frozen.

The practical mental model:

```text
frozen base weights + small trainable low-rank adapters
```

During training, gradients update the adapter matrices. During inference, the adapter modifies the layer's behavior. Depending on the system, the adapter can be kept separate or merged into the base weights for deployment.

### Why Low-Rank Helps

Many useful task-specific updates do not need to move the model in every possible parameter direction.

LoRA assumes the useful update can be approximated in a lower-dimensional subspace.

That gives:

* fewer trainable parameters,
* lower optimizer memory,
* smaller checkpoints,
* faster experiments,
* easier per-domain adapters,
* less infrastructure cost than full fine-tuning.

### Adapters More Broadly

LoRA is one PEFT method. The broader adapter family includes methods that add small trainable modules, prompt-like parameters, prefix parameters, or other constrained update paths.

The shared idea:

```text
freeze most of the model
train a small controlled adaptation
```

Different methods place the trainable capacity in different places. Some modify attention projections. Some add modules between layers. Some learn prefix/prompt representations. The details differ, but the design question is the same:

> Where should optimization be allowed to change the model?

### Top PEFT Techniques

The main PEFT methods differ by **where** they add trainable parameters.

Full fine-tuning says:

```text
update the model weights directly
```

PEFT methods say:

```text
freeze most or all base weights
add a small trainable path
let that path steer behavior
```

That small path can live inside weight matrices, inside attention state, near the input embeddings, or as scaling vectors over internal activations.

#### LoRA: Low-Rank Adaptation

LoRA is the most widely used PEFT method because it gives a strong cost-to-quality tradeoff and is easy to deploy.

The core idea is that a large weight update can often be approximated by a lower-rank update.

Instead of training a full matrix update:

```text
W -> W + Delta W
```

LoRA freezes `W` and learns:

```text
Delta W = A B
```

where `A` and `B` are much smaller trainable matrices.

If the original matrix is large, this can reduce trainable parameters dramatically. The exact savings depend on the layer size and chosen rank, but the practical effect is often that you train a small fraction of the parameters instead of the whole model.

For a weight matrix:

```text
W has shape d_out x d_in
```

full fine-tuning can update:

```text
d_out * d_in parameters
```

LoRA learns two smaller matrices:

```text
A has shape d_out x r
B has shape r x d_in
```

so the trainable parameter count is:

```text
r * (d_out + d_in)
```

where `r` is the rank. When `r` is much smaller than `d_in` and `d_out`, the adapter is much cheaper than the original matrix.

The mental model:

```text
base model knows the broad capability
LoRA learns a small direction for the task/domain/style shift
```

LoRA is often applied to attention projection matrices such as query, key, value, or output projections, and sometimes to MLP layers. The rank is a capacity knob:

* lower rank means cheaper and more constrained,
* higher rank means more adaptation capacity but more memory and overfitting risk.

Common target modules include:

* **query/value projections**, when the adaptation mostly needs to change what the model attends to and how it retrieves information from context,
* **all attention projections**, when the task needs a broader change to attention behavior,
* **MLP/up/down projections**, when the adaptation needs more capacity to change internal transformations,
* **output heads or task-specific layers**, in smaller or specialized architectures.

Choosing target modules is a real modeling decision. Training LoRA only on `q_proj` and `v_proj` is cheaper and often works well. Training LoRA on attention and MLP layers gives more capacity but increases memory, training time, and overfitting risk.

Several practical knobs matter:

* **rank (`r`)** controls adapter capacity,
* **alpha** scales the LoRA update relative to the frozen base weights,
* **dropout** can regularize the adapter,
* **target layers** control where the model is allowed to change,
* **merge behavior** determines whether the adapter stays separate or is folded into the base weights for inference.

The deployment advantage is important. A team can keep one large frozen base model and load different LoRA adapters for different customers, domains, tasks, or experiments:

```text
base model
  + support-ticket LoRA
  + legal-formatting LoRA
  + code-style LoRA
```

That is much cheaper than storing and serving three full model copies.

LoRA is useful when the base model can already perform the task but needs targeted behavior change. It is weaker when the base model lacks the underlying capability or when the update needs broad changes across many behaviors.

Failure modes:

* the rank is too low, so the adapter cannot express the needed change,
* the rank is too high, so the adapter overfits a narrow dataset,
* the wrong layers are targeted, so the update has capacity in the wrong place,
* the adapter is paired with the wrong base model or tokenizer,
* the adapter learns formatting/style while factual quality does not improve,
* multiple adapters interact poorly if composed without validation.

Interview framing:

> LoRA is a constrained way to fine-tune. Instead of updating a full weight matrix, it freezes the base matrix and learns a low-rank delta. That reduces trainable parameters, optimizer state, and checkpoint size. The key tradeoff is capacity: low-rank updates are efficient, but the rank and target modules determine whether the adapter can express the behavior change.

#### Prefix Tuning

Prefix tuning does not primarily change the model's normal weights.

Instead, it learns extra continuous vectors that are inserted into the attention mechanism as a prefix. You can think of these vectors as learned "virtual tokens" that every layer can attend to.

In a transformer attention layer, the model forms keys and values from the input. Prefix tuning adds trainable prefix keys and values:

```text
attention over:
  learned prefix keys/values
  + normal prompt keys/values
```

The base model stays frozen. The learned prefix changes what information is available inside attention, which can steer the model toward a task, style, or domain.

The intuition:

```text
Instead of rewriting the model,
learn a task-specific attention context that the model carries through generation.
```

Prefix tuning is more expressive than plain text prompting because the prefix vectors are continuous learned parameters, not human-readable tokens. It can be especially useful when you want task-specific behavior but want to keep one frozen base model.

The important distinction is that prefix tuning conditions the model through the **attention path**, not by changing normal model weights. The learned prefix can be interpreted as persistent task-specific memory that the model can attend to at each layer.

There are two ways to think about it:

```text
human prompt:
  readable instructions in token space

prefix tuning:
  learned instructions in attention-state space
```

In many formulations, the prefix is not just added once at the input. Learned key/value vectors can be supplied to multiple transformer layers, which gives the prefix a deeper influence than a short natural-language instruction at the front of the prompt.

This makes prefix tuning attractive when:

* the task can be represented as a reusable conditioning pattern,
* you want to avoid changing base weights,
* you want one adapter-like object per task,
* the model already has the relevant knowledge,
* the desired change is more about behavior, formatting, or task framing than new facts.

Example:

```text
base model:
  general instruction-following model

prefix:
  task-specific attention context for summarizing legal contracts

result:
  same base model behaves as if it has a learned task instruction
```

Prefix length is the main capacity knob. A longer prefix gives the adapter more room to encode task information, but it also increases attention work and can reduce effective context budget.

The tradeoff is that prefix tuning consumes effective context/attention capacity and may be less straightforward to merge into the base model than LoRA-style weight deltas. It can also be harder to inspect because the learned prefix is not readable text.

Failure modes:

* the prefix is too short to encode the task,
* the prefix is too long and wastes context or attention capacity,
* the learned conditioning overfits the training format,
* the base model ignores or underuses the prefix,
* the prefix steers style but not correctness,
* serving infrastructure does not handle prefix KV state efficiently.

Interview framing:

> Prefix tuning freezes the model and learns continuous key/value-like prefixes that condition attention. It is like giving the model learned task context at the attention level. It is more powerful than a hand-written prompt but usually less like a weight update than LoRA. The main tradeoff is cheap modular adaptation versus extra attention/context overhead and limited interpretability.

#### Prompt Tuning and P-Tuning

Prompt tuning and P-tuning also learn prompt-like parameters, but they usually operate closer to the input side of the model.

Instead of hand-writing a prompt like:

```text
You are a helpful assistant. Answer in JSON.
```

prompt tuning learns soft prompt embeddings:

```text
[learned embedding 1, learned embedding 2, ...] + user input
```

These learned embeddings are continuous vectors. They do not need to correspond to real vocabulary tokens.

The mental model:

```text
hard prompt: human-written text tokens
soft prompt: trainable embedding vectors
```

Prompt tuning is usually very parameter-efficient because only the soft prompt is trained. That makes it cheap and modular, but also limits how much behavior it can change. It tends to work better when the base model is large and already instruction-capable.

Prompt tuning is closest in spirit to normal prompting:

```text
normal prompting:
  choose discrete tokens by hand

prompt tuning:
  optimize continuous prompt embeddings with gradient descent
```

The model sees the learned embeddings as part of the input sequence. During training, the base model stays frozen and gradients update only the prompt embeddings. The prompt becomes a small learned artifact that can be stored and loaded for a task.

This is very cheap:

```text
trainable parameters =
  number of soft prompt tokens * embedding dimension
```

For a large model, that can be tiny compared with LoRA or full fine-tuning.

Prompt tuning works best when:

* the base model is large and already capable,
* the task is mostly about eliciting existing behavior,
* the desired output format is consistent,
* the training data is task-specific but not huge,
* you need many tiny task adapters.

It is weaker when:

* the model needs new domain knowledge,
* the task requires deep behavior change,
* the base model is small or not instruction-tuned,
* the input format varies widely,
* the prompt must compete with long user context.

The main intuition:

```text
Prompt tuning does not teach the model much new behavior.
It learns how to ask the frozen model for the behavior it already has.
```

P-tuning is a related family of methods that improves the expressiveness of learned prompts, often by using learned prompt encoders or placing trainable prompt representations in ways that better condition the model. The exact variants differ, but the shared idea is:

```text
learn the conditioning signal
instead of manually writing the conditioning text
```

P-tuning can be thought of as making soft prompts less shallow. Instead of treating the learned prompt as a simple list of free embedding vectors, P-tuning methods may generate or structure those vectors with a small neural module. The goal is to make the prompt representation more expressive and easier to optimize.

P-tuning v2-style approaches also made prompt learning more competitive across model sizes and tasks by applying trainable prompt-like parameters more deeply, rather than relying only on a few input embeddings.

The practical distinction:

```text
prompt tuning:
  learn soft tokens near the input

P-tuning:
  learn a richer prompt-conditioning mechanism
```

These methods are good for lightweight task adaptation. They are less suitable when the target behavior requires deep changes to internal reasoning or domain knowledge.

Failure modes:

* the learned prompt overfits to narrow templates,
* performance collapses when inputs differ from training examples,
* the soft prompt is hard to interpret or debug,
* the model treats learned prompt capacity as style conditioning rather than task understanding,
* prompt length eats into useful context,
* prompt embeddings are brittle across model/tokenizer changes.

Interview framing:

> Prompt tuning learns continuous prompt embeddings while freezing the model. It is extremely parameter-efficient, but it mostly learns how to condition a capable base model rather than how to rewrite the model. P-tuning makes prompt learning more expressive with richer prompt representations or deeper prompt conditioning. These methods are lightweight, but they usually have less adaptation capacity than LoRA.

#### IA3

IA3 stands for "Infused Adapter by Inhibiting and Amplifying Inner Activations."

The key idea is even more constrained than LoRA. Instead of adding low-rank matrices, IA3 learns small vectors that scale internal activations.

Conceptually:

```text
activation -> learned scale vector * activation
```

Those learned vectors can scale parts of the attention or feedforward computation. The model's large weight matrices stay frozen, and the adapter learns which internal channels to amplify or suppress for the target task.

The intuition:

```text
LoRA changes directions in weight space.
IA3 changes the strength of existing internal features.
```

This can be extremely parameter-efficient because scaling vectors are tiny compared with full matrices. The cost is lower capacity: IA3 can steer existing features, but it has less room to create new transformations than LoRA.

IA3 is easiest to understand as feature gating.

The frozen base model already computes many internal features. IA3 does not add a large new transformation. It learns which existing channels should matter more or less for a task:

```text
existing feature channel
  -> amplify it
  -> suppress it
  -> leave it mostly unchanged
```

That means IA3 is closer to:

```text
select and rescale existing behavior
```

than:

```text
learn a new behavior from scratch
```

In transformer terms, IA3 can scale activations associated with attention and feedforward layers. Because the learned objects are vectors rather than matrices, the trainable parameter count is extremely small.

This gives IA3 several practical advantages:

* very small adapter checkpoints,
* low optimizer memory,
* fast training,
* easy storage for many tasks,
* reduced risk of catastrophic forgetting because the base model is frozen,
* simple mental model for task-specific feature emphasis.

It also creates a clear limitation. If the base model does not already contain useful features for the task, scaling existing activations may not be enough. LoRA can add a low-rank transformation; IA3 mostly changes the intensity of existing transformations.

IA3 is attractive when you want very small adapters, many task-specific variants, or low training overhead. It is less attractive when the adaptation needs substantial representational change.

Failure modes:

* the task requires new transformations, not just feature reweighting,
* the base model lacks the relevant latent capability,
* learned scales overfit to spurious channels,
* the adapter is too constrained for complex domain adaptation,
* performance is sensitive to which activations are scaled.

Interview framing:

> IA3 freezes the base model and learns small vectors that scale internal activations. It is extremely parameter-efficient because it trains vectors rather than matrices. The tradeoff is capacity: IA3 can amplify or suppress existing features, but it has less ability than LoRA to add new task-specific transformations.

#### Comparing the Methods

| Method | What is trained | Where it acts | Strength | Main limitation |
| ------ | --------------- | ------------- | -------- | --------------- |
| LoRA | low-rank adapter matrices | usually attention/MLP weights | strong general PEFT baseline | rank and target-layer choices matter |
| Prefix tuning | learned prefix keys/values | attention state | expressive learned context | consumes attention/context capacity |
| Prompt tuning | soft prompt embeddings | input embedding sequence | extremely lightweight | limited adaptation capacity |
| P-tuning | learned prompt representations, sometimes with prompt encoders | input or prompt-conditioning path | more expressive prompt adaptation | variant-specific complexity |
| IA3 | learned activation-scaling vectors | attention/MLP activations | tiny adapters, cheap multitask variants | lower capacity than LoRA |

Interview framing:

> LoRA, prefix tuning, prompt tuning, P-tuning, and IA3 are all PEFT methods, but they constrain learning in different places. LoRA learns low-rank weight updates, prefix tuning learns attention prefixes, prompt tuning learns soft input embeddings, P-tuning learns richer prompt-conditioning representations, and IA3 learns vectors that scale internal activations. The common goal is to adapt a mostly frozen base model cheaply while reducing optimizer memory, checkpoint size, and catastrophic-forgetting risk.

### When PEFT / LoRA Is Useful

Use LoRA or PEFT when:

* full fine-tuning is too expensive,
* you need fast domain adaptation,
* you want separate adapters for different customers or tasks,
* the base model is already strong,
* the desired change is narrow,
* you want smaller deployable deltas,
* you want to reduce catastrophic forgetting risk.

Examples:

* adapt a general model to support-ticket tone,
* tune a code model for one repository style,
* adapt a model to medical or legal formatting,
* improve tool-call formatting,
* create a customer-specific adapter without copying the whole base model.

### When PEFT / LoRA Is Not Enough

LoRA is not magic.

It may be insufficient when:

* the base model lacks the underlying capability,
* the domain shift is very large,
* the task needs deep new reasoning patterns,
* the adaptation data is low quality,
* the adapter rank is too small,
* the target behavior conflicts with base-model behavior,
* broad safety or alignment behavior must change.

If the base model cannot do the task at all, a small adapter may only teach surface style.

### How It Compares to Other Updates

| Method | What changes | Best for | Main risk |
| ------ | ------------ | -------- | --------- |
| Prompting | input context only | fast behavior steering | brittle, context-limited |
| RAG | external knowledge in context | fresh/private facts | retrieval noise |
| LoRA / PEFT | small trainable adaptation | cheap targeted behavior shift | adapter/base mismatch, narrow overfit |
| Full fine-tuning | many or all weights | broad behavioral/domain change | cost, forgetting, safety regression |
| Preference optimization | likelihood of preferred outputs | alignment and preference shaping | preference data bias |
| RLHF / RL | policy over trajectories | interactive or long-horizon behavior | reward hacking, instability |

### Evaluation Requirements

A LoRA adapter is still a model update.

Evaluate:

* target task quality,
* general regression,
* safety behavior,
* formatting/schema accuracy,
* hallucination rate,
* latency and memory impact,
* compatibility with quantization or serving stack,
* adapter/base/tokenizer version correctness.

The common mistake is only evaluating the narrow task the adapter was trained on.

### Deployment Mental Model

The deployable artifact is not just the adapter.

It is:

```text
base model
  + tokenizer
  + config
  + adapter weights
  + adapter metadata
  + eval results
```

If the adapter is loaded against the wrong base model, wrong tokenizer, or wrong quantization setting, behavior can silently break.

Chapter 9 covers this engineering side: registries, artifact lineage, serving adapters, and versioning.

### Interview Framing

> PEFT methods like LoRA freeze the base model and train a small constrained update. LoRA represents the update to a weight matrix with low-rank adapter matrices, which reduces trainable parameters and optimizer memory. It is useful for targeted domain or behavior adaptation when the base model is already capable. It still needs eval gates because it can overfit, regress safety, or fail if the adapter is paired with the wrong base model.

## 4.6 Distillation, Self-Distillation, and Reference-Guided Updates

Distillation trains one model or policy to match useful behavior from another model, checkpoint, search process, or privileged context.

The important idea is not merely "two networks." The useful abstraction is:

```text
fast learner updates against a reference signal
that is more stable, better informed, cheaper to query later,
or more filtered than the learner's raw self-update
```

### Knowledge Distillation

Classic knowledge distillation uses a teacher model to train a student model. The teacher is often larger, more accurate, or an ensemble. The student may be smaller, faster, cheaper, or easier to deploy.

The teacher provides **soft targets**, not just hard labels. For example, a hard label may say "cat," but a teacher distribution can say:

```text
cat: 0.82
fox: 0.10
dog: 0.06
raccoon: 0.02
```

That distribution carries structure about which mistakes are plausible. The student learns more than the single correct answer; it learns the teacher's geometry over alternatives.

This is especially useful when the true label is too coarse. In language modeling, many next tokens can be acceptable, but not equally acceptable. A hard target treats every non-observed token as equally wrong. A teacher distribution can say that one synonym, phrase, or action is close to the desired behavior while another is far away.

Distillation also changes the economics of deployment. A large model or ensemble can be used offline to produce targets, then a cheaper student can serve traffic. The price is that the student inherits the teacher's blind spots unless the distillation data and evals include cases where the teacher is wrong.

### Policy Distillation

Policy distillation transfers behavior from one policy to another. In RL, this can compress several task policies into one policy or transfer a search-enhanced policy into a faster policy. In LLMs, it means shaping the next-token distribution or tool-action distribution of the student.

Policy distillation is different from ordinary SFT. SFT imitates observed outputs. Policy distillation can match the teacher's conditional distribution over many possible next actions or tokens.

That distinction matters for agents and LLMs because the same final answer can be reached through different local decisions. Policy distillation can teach the student which intermediate actions were plausible, which tool calls were preferred, or which token choices the teacher considered close alternatives. SFT usually only says "make this full target sequence more likely."

The data source also matters. Offline distillation on a fixed teacher dataset is closer to SFT: the student is pulled toward behavior from an external distribution. On-policy distillation is different because the student generates the states first. The teacher then gives guidance on the student's own partial trajectories. This reduces the mismatch between training states and test-time states, and it helps explain why on-policy distillation can sometimes preserve broad behavior better than ordinary imitation.

### Self-Distillation

Self-distillation is not circular, because the teacher and student are not identical in role even if they share architecture or initial weights.

The teacher may be:

* an earlier checkpoint,
* an EMA or momentum copy of the student,
* the same model with extra context,
* the same model under a different view or augmentation,
* the current model after search, filtering, or verification.

The asymmetry comes from time, information, view, or filtering. The student learns from a version of itself that is delayed, smoothed, privileged, or selectively trusted.

This is the key to why self-distillation is not just a model "teaching itself what it already knows." The teacher is created by changing the information available to the model or by smoothing the model over time. A model with a hint, a model averaged over many recent checkpoints, and a model after search are not the same learning signal as the raw student at the current step.

Representation self-distillation and policy self-distillation should be kept separate:

| Type | What Is Matched | Purpose |
| ---- | --------------- | ------- |
| Representation self-distillation | embeddings or hidden representations | better latent geometry, invariance, semantic clustering |
| Policy self-distillation | token/action distributions | better output behavior, local policy refinement, behavior transfer |

### Target Networks and Old Policies

RL target networks are one of the cleanest examples of the slow-reference pattern.

In DQN, Double DQN, DDPG, TD3, and SAC-style methods, the online network changes quickly while a target network changes slowly. The target network provides bootstrapped value targets. If the target were updated at the same speed as the learner, the learner would chase a moving target partly created by itself.

The bootstrapping problem is subtle. The target often contains the model's own estimate of future value. That means the model is learning from a target that is partly predicted, not purely observed. If the prediction target changes every time the learner changes, errors can reinforce themselves. A target network slows down that feedback path.

PPO, TRPO, RLHF, and DPO use a related but not identical idea. An old policy or frozen reference policy anchors the update. The reference is not always a teacher of better content; often it is a behavioral constraint that says:

```text
improve, but do not move too far in one update
```

This is why plain actor-critic is not always the best example of a slow-teacher/fast-student pattern. In many actor-critic systems, the critic is updated as fast as, or faster than, the actor. The stronger RL examples are target networks, old-policy snapshots, EMA critics, and KL-to-reference constraints.

So there are two questions to separate:

```text
Who evaluates the learner?
Who defines the stable target or constraint?
```

A critic may evaluate the learner without being slow. A target network may be slow without being a separate kind of evaluator. A reference policy may not evaluate quality at all; it may only define the region where the update is allowed to move.

### OPSD and RMSD

On-policy self-distillation, or OPSD, uses the student's own rollouts as the training context. A teacher policy, often the same model with extra context or hints, rescoring those rollouts provides dense token-level feedback.

The phrase **on-policy** matters. The student is not being trained only on ideal demonstrations from some external corpus. It generates its own response, including its own mistakes and awkward prefixes. The teacher then scores what the student actually did. This is closer to a tutor marking up a student's attempted solution than handing the student a polished answer key.

From the distributional view, OPSD is not trying to replace the student with the teacher everywhere. It is trying to reshape the student's current distribution where the student's own behavior creates useful training states. That makes the update more local than SFT on a fixed demonstration set.

A simplified setup:

```text
student prompt x
  -> student rollout y

teacher prompt x' = x + privileged hint/correction
  -> teacher probabilities over the same rollout prefixes

loss:
  reverse KL from student distribution to teacher distribution
```

Reverse KL is conservative because the student's own probabilities determine which tokens dominate the loss. It tends to refine behavior near what the student already considers plausible instead of forcing broad imitation of every teacher-supported mode.

Intuitively, forward KL asks the student to cover the teacher's distribution. Reverse KL asks the student to clean up its own distribution relative to the teacher. That makes reverse KL attractive when the goal is behavior insertion without rewriting every unrelated part of the policy.

The tradeoff is credit assignment. OPSD gives dense token-level signal, but not every teacher-student disagreement is task-relevant. The teacher may disagree on style, filler words, punctuation, or reasoning phrasing even when the target behavior depends on a small number of important tokens. Dense signal is useful only if the signal mostly points at the behavior you wanted to teach.

Relevance-Masked Self-Distillation, or RMSD, adds a second filter:

1. Generate the student rollout.
2. Re-score the rollout with a privileged teacher prompt.
3. Find token positions with large teacher-student logprob disagreement.
4. Ask a judge model which disagreements are relevant to the target behavior.
5. Apply reverse KL only on the selected token positions.

The key distinction:

```text
reverse KL = local in probability space
RMSD = local and relevant in task space
```

This matters because teacher-student disagreement can be noise. The teacher may prefer "Absolutely" over "That" even when the desired behavior is about spelling `pineapple` as `pinapple`. RMSD tries to spend gradient budget on the tokens that actually carry task signal.

RMSD is therefore doing credit assignment at token granularity. The first filter, large logprob disagreement, is high recall: it catches many places where the teacher and student differ. The judge filter tries to improve precision: among those disagreements, it keeps the positions that are semantically relevant to the desired behavior. The method is useful only if the relevance filter is better than blindly trusting every disagreement.

### Method Map

| Method | Slow / Frozen / Privileged Object | Fast Object | Main Role |
| ------ | --------------------------------- | ----------- | --------- |
| DQN / Double DQN | target Q network | online Q network | stable bootstrapped targets |
| DDPG / TD3 / SAC | target critic or target actor | online actor/critic | reduce target drift |
| PPO / TRPO | old policy snapshot | updated policy | trust-region-like constraint |
| RLHF / DPO | reference policy | updated policy | behavioral anchor / KL constraint |
| Knowledge distillation | larger or ensemble teacher | smaller student | transfer / compression |
| BYOL / DINO / Mean Teacher | EMA or momentum teacher | online student encoder | stable representation target |
| OPSD | privileged-context teacher | student policy | local policy refinement |
| RMSD | privileged teacher plus relevance mask | student policy | filtered token-level behavior insertion |

The two big subfamilies are:

* **stabilized self-bootstrapping**, where the teacher is basically the learner delayed or smoothed,
* **asymmetric supervision**, where the teacher has knowledge, compute, context, or filtering the student does not have.

## 4.7 Training, RL, and Inference Compute Economics

A model is not optimized only for pretraining loss.

A deployed model is part of an economic loop:

```text
pretraining compute
  -> post-training / RL compute
  -> inference compute
  -> user value
```

A useful mental model is total compute:

$$
C_{\text{total}} =
C_{\text{pretrain}} + C_{\text{RL}} + C_{\text{inference}}
$$

For dense matrix multiplies, a rough pretraining estimate is:

$$
C_{\text{pretrain}} \approx 6 \cdot N_{\text{active}} \cdot D_{\text{pretrain}}
$$

The factor of 6 is a standard back-of-the-envelope:

* about 2 FLOPs per parameter-token for the forward pass,
* about 4 more for the backward pass,
* total forward plus backward $\approx 6$.

Inference is forward-only:

$$
C_{\text{inference}} \approx
2 \cdot N_{\text{active}} \cdot D_{\text{inference}} \cdot \text{inefficiency}
$$

The inefficiency term matters because decode can have much lower hardware utilization than prefill or training. A token generated one at a time may be memory-bandwidth-bound even when the hardware has enormous peak FLOPs.

RL and post-training sit between the two:

$$
C_{\text{RL}} \approx
(2 \text{ to } 6)
\cdot N_{\text{active}}
\cdot D_{\text{RL}}
\cdot \text{inefficiency}
$$

The range exists because RL workloads may require:

* forward-only rollout generation,
* reward model scoring,
* policy updates on some subset of rollouts,
* expensive decode with lower utilization,
* environment or tool execution around the model.

### Why Models May Be Trained Beyond Chinchilla

The original Chinchilla-style intuition asks:

```text
Given a fixed pretraining compute budget,
what model size and token count minimize loss?
```

But a deployed frontier model asks a broader question:

```text
Given pretraining + RL + inference cost,
what model gives the best user value per total dollar?
```

That can favor training a smaller or sparser model on many more tokens than a pure pretraining-optimal rule would suggest. More training can make the model cheaper or better at inference time, and inference may dominate the lifetime cost if the model serves enough users.

A simple heuristic is cost equalization:

```text
if one stage is much more expensive than the others,
move effort to the stage that reduces it
```

For many power-law-like tradeoffs, the rough optimum is often near the point where major costs are of the same order.

This does not mean the costs are exactly equal in practice. Labs have private scaling curves, deployment forecasts, hardware constraints, model-family plans, and risk estimates. The useful interview point is that pretraining token count is no longer only about the pretraining run. It is also about expected post-training and inference usage.

### RL Compute Has a Hidden Decode Cost

RL for LLMs is not just a normal training loop.

It often includes:

```text
sample prompts
  -> generate rollouts
  -> score with reward/verifier/environment
  -> update policy
  -> evaluate
```

The rollout generation can be expensive because it uses autoregressive decode. Decode may have lower model FLOPs utilization than training because each token is sequential and memory-bound.

That means a million RL tokens can cost more wall-clock time or hardware rental than a million pretraining tokens, depending on batching, context length, reward-model calls, and environment cost.

Interview framing:

> I would not compare pretraining, RL, and inference only by token counts. Pretraining uses efficient forward/backward passes over large batches. RL may include inefficient decode, reward scoring, and partial training on rollouts. Inference is forward-only but often memory-bandwidth-bound during decode.

### Product Traffic Feeds Back Into Training Strategy

If a model will serve enormous traffic, inference cost matters enough to change training strategy.

For example:

```text
model used by few users
  -> pretraining cost may dominate

model used by millions of users
  -> inference cost can dominate lifetime economics
```

This explains why production teams care about:

* smaller active parameter counts,
* MoE sparsity,
* distillation,
* quantization,
* long-context efficiency,
* output length control,
* routing easy requests to cheaper models,
* training more if it reduces inference cost or improves task success.

The model is not just a checkpoint. It is a capital asset that must be amortized through deployment.

## 4.8 Online Learning

Online learning updates behavior as new data arrives.

In strict online learning, the model or policy updates continuously or frequently from production interactions. In many production ML systems, "online learning" is softened into frequent retraining, bandit updates, canary evaluation, or reranking updates rather than immediate LLM weight updates.

Online learning is common in:

* recommendation ranking
* ads bidding
* search ranking
* personalization
* fraud and abuse detection
* contextual bandits

For LLMs, full online weight updates are less common because safety, regression risk, and infrastructure cost are high. More common patterns include:

* updating retrieval indexes
* updating prompts or policies
* updating rerankers
* collecting preference data for batch post-training
* using bandits to choose among model variants

## 4.9 Continual Learning

Continual learning means updating a model over time while preserving previous capabilities.

The challenge is catastrophic forgetting. A model fine-tuned on new data may improve on recent tasks while losing older skills, safety behavior, language ability, or domain coverage.

Common mitigation patterns:

* mix old and new data during training
* keep a replay buffer
* evaluate broad regression suites
* use small adapter updates where appropriate
* freeze parts of the model
* gate updates by capability and safety evals
* track per-domain performance, not only aggregate metrics

Continual learning is not just "train again." It is controlled change management for model behavior.

## 4.10 Self-Improvement Loops

A self-improvement loop uses the model or system to generate training candidates, critique outputs, solve tasks, create synthetic data, or propose refinements.

Examples:

* generate multiple candidate answers and keep the one that passes tests
* use an LLM judge to label preference pairs
* use execution results to create verified code examples
* ask a stronger model to critique a weaker model
* mine failure traces and turn them into training cases

The danger is feedback contamination. If the model generates flawed data and then trains on it without independent validation, the system can amplify its own biases and mistakes.

Self-improvement loops need external anchors:

* human review
* deterministic tests
* trusted datasets
* safety filters
* held-out evaluations
* production outcome checks

## 4.11 Learning Loop Operations

The algorithm is only one part of the learning loop. In deployed systems, most of the work is operational:

* deciding which traces are eligible for training
* redacting or excluding sensitive data
* collecting labels or preferences with clear instructions
* measuring annotator disagreement
* sampling edge cases instead of only high-volume cases
* converting failures into regression tests
* promoting updates through offline evals, canaries, and rollback plans

A mature loop usually has separate ownership for data policy, labeling quality, training, evaluation, deployment, and incident response. If those responsibilities are blurred, a "learning" system can quietly absorb noisy feedback, private content, or product incentives that conflict with correctness.

The economic question matters too. Some improvements are cheaper as prompt changes, retrieval fixes, tool validation, or model routing. Post-training is worth the cost when the desired behavior is broad, repeated, and hard to enforce at runtime.

---

# 5. Common Technologies and Patterns

## Reward Models

Reward models are usually transformer-based classifiers or regressors trained over prompt-response pairs. They may produce a scalar quality score, safety score, helpfulness score, or domain-specific score.

In production, reward models are often used for:

* training signal in RLHF
* offline ranking of candidate responses
* rejection sampling
* safety scoring
* evaluation dashboards

## Preference Datasets

Preference datasets contain examples of chosen and rejected outputs.

Useful fields include:

* prompt
* chosen response
* rejected response
* label source
* labeler agreement
* task category
* safety category
* model versions that produced candidates
* timestamp and sampling settings

Metadata matters because preference data ages. A preference from an old policy, old UI, or old safety policy may not match the current product.

## RL Training Loops

An RL training loop typically has:

* rollout generation
* reward scoring
* advantage estimation
* policy update
* reference-policy regularization
* evaluation
* checkpointing

For LLMs, these loops are expensive because rollouts are token-heavy and model updates require large GPU workloads. That is why teams often use offline preference optimization, rejection sampling, or smaller rerankers before full RL.

## Reference-Guided Learning Patterns

Reference-guided learning is the broad family where the current learner is trained against a frozen, delayed, smoothed, privileged, or filtered signal.

Common patterns:

| Pattern | Reference Role | Typical Examples |
| ------- | -------------- | ---------------- |
| Bootstrap target | produces stable targets for a bootstrapped prediction | DQN target network, SAC target Q network |
| Behavioral anchor | limits how far the policy can move | PPO old policy, RLHF reference model, DPO reference policy |
| Teacher | transfers richer behavior or softer labels | knowledge distillation, policy distillation, ensemble distillation |
| Momentum teacher | smooths the current learner over time | BYOL, DINO, MoCo-style momentum encoders, Mean Teacher |
| Privileged teacher | sees extra context, hints, or corrections | OPSD, RMSD |
| Filter or judge | decides which token/action differences matter | RMSD relevance mask, pseudo-label confidence filtering |

This pattern should be described as a composition of objective design, constraints, credit assignment, and update cadence. The reference is not automatically "better." Sometimes it is better informed. Sometimes it is merely slower, which is enough to stabilize the target.

## Offline and Online Bandits

Bandits handle decisions where actions produce observable reward but full long-horizon RL is unnecessary.

Examples:

* choosing which prompt template to use
* choosing among model variants
* selecting a ranking strategy
* routing traffic between answer styles
* choosing retrieval depth

Offline bandit evaluation tries to estimate policy performance from logged data. Online bandits allocate live traffic while balancing exploration and exploitation.

## Trajectory Logging

Trajectory logging is the instrumentation layer that makes learning possible.

Without logs, feedback cannot be attributed. You need the prompt, context, model version, output, tool calls, latency, filters, user action, and outcome. This is also the bridge from Chapter 4 evaluation to Chapter 5 learning: eval cases often come from logged failures.

## Rejection Sampling and Reranking

Rejection sampling generates multiple candidates, scores them, and keeps the best acceptable one.

Reranking is similar: generate or retrieve candidates, score them with a model or heuristic, and return the top result.

These patterns improve behavior without changing policy weights. They are often cheaper and safer than immediate retraining, but they add inference cost and depend on scorer quality.

## Post-Training Pipelines

A mature post-training pipeline includes:

* data ingestion
* cleaning and deduplication
* labeling
* dataset versioning
* training
* offline evaluation
* safety evaluation
* red-team testing
* staged rollout
* monitoring
* rollback

This is software engineering around optimization. The model update is only one step.

---

# 6. Implementation Details

## 6.1 Data Collection

Collect the full decision context, not just the final answer.

For an LLM product, useful records include:

* user request after privacy filtering
* retrieved documents or tool observations
* prompt template version
* model and checkpoint version
* sampling parameters
* candidate outputs
* final selected output
* validation results
* user feedback
* downstream outcome
* safety filter results

Data collection must also handle privacy, retention, consent, and security. A training pipeline that leaks sensitive user data into future models is a production incident, not a model improvement.

## 6.2 Preference Labeling

Preference labels are easier to collect than perfect demonstrations, but they are not free.

Good labeling workflows define:

* what "better" means
* how to handle factuality vs helpfulness vs tone
* when safety overrides user preference
* how to break ties
* how to measure labeler agreement
* how to audit label quality

For high-stakes domains, labels often need expert review. For low-stakes domains, crowd labels or LLM-assisted labels may be acceptable if validated against trusted samples.

## 6.3 Reward Estimation

Reward can come from:

* direct environment outcome
* human labels
* learned reward model
* deterministic verifier
* heuristic score
* LLM judge
* blended score

The safest systems avoid pretending that one reward captures everything. They often maintain separate scores for helpfulness, correctness, safety, policy compliance, latency, and user satisfaction. The update gate can then require that no critical dimension regresses.

## 6.4 Gated Policy Updates

A gated update process asks:

```text
Should this candidate policy be allowed to change production behavior?
```

Useful gates:

* offline benchmark improvement
* no regression on critical tasks
* safety eval pass
* privacy and compliance checks
* human review for risky behavior changes
* canary success
* rollback readiness

The update should be reversible. In production, the ability to roll back a model or route traffic away from a bad policy is part of the learning system.

## 6.5 Safety Maintenance

Safety is not a one-time filter. It must be maintained across updates.

Policy updates can accidentally weaken refusals, increase confident hallucinations, leak private information, or make unsafe tool calls. A post-training pipeline needs safety datasets, adversarial tests, red-team prompts, policy-specific evaluations, and monitoring for novel failures.

The key rule:

```text
Never let a quality reward silently override safety constraints.
```

## 6.6 Continual-Learning Risks

Continual learning can go wrong when recent data dominates older invariants.

Examples:

* a support bot learns from angry users and becomes overly apologetic
* a coding assistant overfits to one team's style and regresses general Python ability
* a retrieval system promotes popular but outdated documents
* an agent learns shortcuts that pass shallow tests but fail real tasks
* a model absorbs private or low-quality user text

The fix is not to avoid learning. The fix is to make updates explicit, measured, versioned, and gated.

---

# 7. Tradeoffs

## 7.1 Latency

Learning loops can improve future quality but add current latency.

Reranking, rejection sampling, reward scoring, and multi-candidate generation all require extra inference. Online bandits may add routing complexity. Full RL does not usually affect request latency directly during training, but the resulting policy may be larger, slower, or require additional safety checks.

## 7.2 Cost

Costs come from:

* human labeling
* rollout generation
* reward model training
* policy training
* evaluation suites
* storage for trajectories
* serving extra candidates or scorers

Preference optimization is often chosen because it can be cheaper and simpler than full online RL. Reranking is often chosen because it improves behavior without changing weights, but it increases per-request inference cost.

## 7.3 Reliability

Static models are easier to reason about than models that change. Every update creates regression risk.

Learning systems need versioning, reproducibility, eval gates, rollback, and monitoring. Without those, "the model is learning" becomes an explanation for unpredictable behavior rather than a controlled improvement mechanism.

## 7.4 Correctness

User preference is not the same as correctness. People may prefer confident, fluent, or agreeable answers even when they are wrong.

For correctness-sensitive tasks, preference signal should be combined with ground-truth checks, retrieval grounding, tests, expert review, or deterministic verifiers.

## 7.5 Scaling

At small scale, manually inspecting bad outputs and fine-tuning occasionally may work. At large scale, teams need automated logging, dataset pipelines, labeling operations, training jobs, eval dashboards, canaries, and rollback infrastructure.

The organizational complexity can exceed the modeling complexity.

## 7.6 Operational Complexity

Learning loops create dependencies across product, data, ML, infra, safety, legal, and support teams.

You need clear ownership for:

* what data can be used
* what labels mean
* what metrics decide promotion
* who approves risky updates
* how incidents are handled
* how users can opt out where required

---

# 8. Failure Modes

## 8.1 Reward Hacking

Reward hacking happens when the policy finds behavior that maximizes reward without satisfying the real goal.

Examples:

* writing verbose answers because the reward model associates length with quality
* adding citations that look real but are not grounded
* refusing too often because refusals avoid unsafe mistakes
* optimizing for clicks with misleading titles
* passing shallow tests while hiding deeper errors

The fix is better reward design, adversarial evaluation, multiple metrics, human audits, and conservative update gates.

## 8.2 Misgeneralized Preferences

A model can learn the wrong abstraction from preference data.

If labelers prefer polite responses, the model may overgeneralize into excessive flattery. If labelers prefer confident answers, the model may become more confidently wrong. If labels reward concise answers, the model may omit necessary caveats.

This is Chapter 0 generalization under a preference-shaped objective. The model learns patterns that reduce training loss, not necessarily the human concept you intended.

## 8.3 Catastrophic Forgetting

Catastrophic forgetting occurs when new training damages old capabilities.

A model fine-tuned on customer support transcripts might become better at support tone but worse at reasoning. A domain-specific update might improve one product area and degrade safety refusals elsewhere.

Mitigations include replay data, broad eval suites, regularization, adapters, frozen layers, and staged rollout.

## 8.4 Distribution Drift

The world changes, users change, products change, and the model itself changes which data gets observed.

A reward model trained on old outputs may not score new outputs correctly. A preference dataset from one user segment may not generalize to another. A policy optimized under one UI may fail under a redesigned UI.

Learning loops need drift monitoring and periodic revalidation.

## 8.5 Style Over Substance

Preference optimization often rewards surface features:

* confident tone
* helpful phrasing
* clean formatting
* apparent reasoning
* pleasing brevity

These features are not bad, but they can crowd out truth, depth, and calibrated uncertainty. A model can become more satisfying while becoming less correct.

## 8.6 Feedback Loops from Bad Data

If the system trains on biased, spammy, adversarial, or model-generated data, the next policy may produce more of the same.

Examples:

* a recommender learns from clickbait clicks and shows more clickbait
* an assistant learns from unverified thumbs-up feedback
* a code model trains on generated code that only appears correct
* an agent learns from traces where bad tool calls were not labeled

The defense is data filtering, source weighting, held-out trusted evals, and explicit review of data entering training.

## 8.7 Reference-Guided Learning Failures

Slow or frozen references reduce some instability, but they introduce their own failure modes.

Common failures:

* **stale teacher:** the reference caps progress because it no longer represents the best available behavior,
* **overactive teacher refresh:** updating the reference too frequently removes the timescale separation and can cause collapse,
* **confirmation bias:** self-distillation can amplify the learner's existing blind spots,
* **irrelevant disagreement:** teacher and student differ on style, punctuation, or discourse markers instead of the target behavior,
* **over-constraint:** KL or reference anchoring is too strong, so the policy cannot learn the new behavior,
* **under-constraint:** the anchor is too weak, so the policy drifts or exploits the reward model,
* **bad masking:** RMSD-style filters miss relevant tokens or select fluent but irrelevant tokens,
* **teacher bias transfer:** large-to-small distillation transfers the teacher's mistakes along with its capabilities,
* **target lag mismatch:** target networks updated too slowly delay learning, while targets updated too quickly destabilize bootstrapping.

The operational fix is to evaluate both the target behavior and the preserved behavior. A reference-guided update is not successful just because the student matches the teacher.

---

# 9. What to Say in an Interview

For a learning-loop question, start with the objective and feedback source:

```text
I would first define what behavior we want, what feedback can measure it, and how trustworthy that feedback is.
```

Then separate the options:

* Use SFT when you have demonstrations of desired behavior.
* Use preference optimization when ranking outputs is easier than writing ideal outputs.
* Use RLHF when you need to optimize against a learned reward signal and can afford the complexity.
* Use bandits when choosing among actions or variants with measurable online reward.
* Use continual learning only with strong regression and safety gates.

Then explain the safety layer:

```text
I would not let raw user feedback update the model directly. I would log trajectories, clean and label data, train or score candidates offline, run evals, gate updates, canary, monitor, and keep rollback available.
```

High-signal phrases:

* "Reward is a proxy, so I would design against reward hacking."
* "Preference data shapes behavior but can overfit to style."
* "The current policy controls the data distribution, so the loop can bias itself."
* "I would treat model updates like production releases."
* "Continual learning needs replay or regression coverage to avoid forgetting."

---

# 10. Takeaways

Learning loops convert feedback into future behavior.

The core primitives are reward, policy, value, advantage, feedback, exploration, and trajectory data. They compose into a loop where behavior creates data, data creates signal, signal creates updates, and updates create new behavior.

The engineering challenge is controlling that loop. Good systems collect rich trajectories, separate raw feedback from trusted reward, use preference or reward modeling carefully, gate policy updates, maintain safety, and monitor drift.

The Chapter 0 lesson still applies: optimization amplifies the objective. In Chapter 5, the objective may come from humans, users, tools, tests, or production outcomes. If that signal is wrong, the model does not merely make mistakes; it learns them.

---

# 11. Bridge to Production Serving

Once a model can change, serving becomes more than inference.

Production serving must answer:

* which model version should receive this request?
* how do we compare the new policy to the old one?
* how do we canary, monitor, and roll back?
* how do we keep latency and cost acceptable?
* how do we prevent training data from leaking private information?
* how do we detect regressions after deployment?

Chapter 6 moves from learning loops to production ML systems: model serving, deployment, monitoring, scaling, incident response, and operating changing models reliably.

[Chapter 13](../chapter_13/guide.html) adds the runtime cost of learning-loop choices. A tuned model, larger context window, longer reasoning trace, or new verifier can change prefill/decode balance, memory use, batching efficiency, and GPU count. Treat model updates like production releases that must pass both behavioral evals and serving benchmarks.
