---
layout: page
title: "Chapter 0: ML Foundations"
guide_type: chapter
---

# Chapter 0 — ML Foundations

This chapter owns the mathematical and conceptual primitives used throughout the guide: probability, optimization, embeddings, information flow, objectives, constraints, and how these primitives compose into AI systems.

---

## Table of Contents

- TOC
{:toc}

---

This chapter provides the **complete mental model** for reasoning about modern AI systems, from abstract primitives to concrete transformer architecture, training pipelines, and inference cost.

---

# Part I: Foundations (Primitives for Applied AI Systems)

This section builds the **minimal mental model** required to reason about modern AI systems (LLMs, agents, RAG, RLHF) without going deep into theory or proofs.

The goal is:

> Reduce complex systems into a few composable primitives you can reason about under interview pressure.

---

## Overview: The 4 Core Primitives

All higher-level AI systems can be reduced to:

1. **Probability → Uncertainty over outputs**
2. **Optimization → Shaping behavior via signals**
3. **Embeddings → Geometry of meaning**
4. **Information flow → What is preserved vs lost**

---

## 1. Probability — Models as Distributions

### Core Idea

A model does **not** output a single answer.

It defines a **probability distribution over possible outputs**.

$$
P(y \mid x)
$$

* (x): input (prompt)
* (y): output (text, action, etc.)

---

### For Language Models

LLMs model sequences token-by-token:

$$
P(y_1, y_2, \ldots, y_n \mid x) = \prod_{t=1}^{n} P(y_t \mid x, y_1, \ldots, y_{t-1})
$$

This means:

* each token depends on previous tokens
* generation is inherently **stochastic**

---

### Intuition

Think of the model as:

> "Given this context, what are plausible next continuations?"

Not:

> "What is the correct answer?"

---

### Why This Matters

This explains:

* hallucinations → high probability ≠ correct
* temperature → reshapes probability distribution
* variability → sampling from distribution

---

### Interview Insight

If asked *"Why does the model hallucinate?"*, a strong answer starts with:

> "Because the model is sampling from a learned probability distribution, not retrieving ground truth."

---

## 2. Optimization — Learning as Signal Shaping

### Core Idea

Training is about **adjusting model parameters to increase probability of desired outputs**.

---

### Objective Function

Typical training minimizes loss:

$$
\mathcal{L} = - \mathbb{E}_{(x,y)} \bigl[\log P(y \mid x)\bigr]
$$

This is **negative log-likelihood**.

---

### Gradient Intuition

Parameters are updated via:

$$
\theta \leftarrow \theta - \eta \nabla_\theta \mathcal{L}
$$

Interpretation:

* increase probability of correct outputs
* decrease probability of incorrect ones

---

### Intuition (Non-Math)

Training = repeatedly telling the model:

> "Do more of this, less of that."

---

### Why This Matters

Explains:

* fine-tuning → shifting behavior distribution
* RLHF → redefining "good" outputs
* overfitting → overly confident in narrow patterns

---

### Key Insight

> The model does not understand correctness — it optimizes **whatever signal you give it**.

---

### Automatic Differentiation and Computation Graphs

Gradient descent needs gradients.

The simplest way to estimate a derivative is a finite difference:

$$
f'(x) \approx \frac{f(x + \epsilon) - f(x - \epsilon)}{2\epsilon}
$$

This is useful conceptually, but it is not how modern ML frameworks train large models. Finite differences are too slow and too noisy when a model has millions or billions of parameters.

Instead, frameworks use **automatic differentiation**.

The mental model:

```text
forward pass:
  compute outputs and remember how each value was produced

backward pass:
  traverse the computation graph backward and apply the chain rule
```

A computation graph records operations:

```text
x -> log(x) -> square(log(x)) -> loss
```

Each node knows:

* what operation produced it,
* which inputs fed that operation,
* how to pass gradients backward through that operation.

Backpropagation is reverse-mode automatic differentiation:

```text
loss
  -> gradient of final operation
  -> gradient of previous operation
  -> ...
  -> gradients of parameters
```

The key idea is not that the framework "magically knows calculus." It records the graph of tensor operations and repeatedly applies the chain rule.

This is why PyTorch's eager autograd model is so intuitive: as tensor operations run, PyTorch builds the graph needed for the backward pass.

Interview framing:

> Training uses a forward pass to compute loss and build the computation graph, then a backward pass to propagate gradients through that graph using the chain rule. Autodiff gives exact gradients for the executed operations, unlike finite differences, which are approximate and too expensive at scale.

---

### Tensors as the Practical Unit of ML Computation

The scalar mental model is useful:

```text
number -> operation -> number -> operation -> loss
```

But real models do not operate one scalar at a time.

They operate on tensors:

| Object | Shape intuition |
| ------ | --------------- |
| Scalar | one number |
| Vector | list of numbers |
| Matrix | table of numbers |
| Tensor | multidimensional array |

For example, an RGB image might be:

```text
(channels, height, width) = (3, 224, 224)
```

A batch of token embeddings might be:

```text
(batch, sequence, hidden_dim)
```

Tensors matter for two reasons:

1. **Memory:** the framework tracks one tensor operation instead of millions of independent scalar objects.
2. **Parallelism:** tensor operations map naturally to CPU vectorization and GPU kernels.

Matrix multiplication is the core operation behind neural networks. Instead of computing every output scalar one at a time in Python, frameworks dispatch large tensor operations to optimized native kernels.

This is the bridge from math to systems:

```text
model equation
  -> tensor operation
  -> optimized kernel
  -> CPU/GPU execution
```

Interview framing:

> Tensors are the practical unit of computation in ML frameworks. They let the framework batch many scalar operations into one graph node and execute them efficiently on optimized hardware.

---

## 3. Embeddings — Meaning as Geometry

### Core Idea

Text is mapped into vectors:

$$
\text{embedding}(x) \in \mathbb{R}^d
$$

These vectors capture **semantic meaning**.

---

### Similarity

Similarity is often measured via cosine similarity:

$$
\text{sim}(a, b) = \frac{a \cdot b}{\lVert a \rVert \, \lVert b \rVert}
$$

---

### Intuition

* similar meaning → vectors close together
* different meaning → far apart

Think:

> Geometry = meaning

---

### Why This Matters

Explains:

* retrieval (RAG)
* clustering
* semantic search
* memory systems

---

### Key Insight

> Retrieval works because "relevant" ≈ "geometrically close"

---

## 4. Information Flow — Signal vs Noise

### Core Idea

Any system has **limited capacity to process information**.

Key constraints:

* context window
* model size
* bandwidth (attention)

---

### Compression View

Models compress input into internal representations.

Not all information survives.

---

### Signal vs Noise

* Signal → useful information
* Noise → irrelevant or distracting information

---

### Intuition

Adding more input does NOT always help.

It can:

* dilute signal
* increase confusion

---

### Why This Matters

Explains:

* why RAG must be selective
* why long prompts degrade performance
* why summarization helps
* why memory needs pruning

---

### Key Insight

> Better systems don't add more data — they improve the **signal-to-noise ratio**.

---

## Composition: How These Primitives Combine

These four ideas combine into everything else:

* Probability → defines behavior space
* Optimization → shapes that behavior
* Embeddings → structure meaning
* Information flow → limits what is usable

---

### Example: RAG System

* embeddings → retrieve relevant docs
* probability → generate answer
* information flow → context selection matters
* optimization → model trained to use context

---

### Example: Agent System

* probability → decides next action
* embeddings → memory retrieval
* optimization → improves behavior over time
* information flow → context management

---

## 5. ML Design Primitives — Understanding How Methods Are Built

The four primitives above help you reason about AI system *behavior*. This section provides a complementary lens: understanding how ML *methods themselves* are designed and improved.

### Core Idea

Most ML progress is not random innovation.

It is systematic movement through a small design space.

A useful split is:

1. **Data / problem space** — what distribution are you learning from?
2. **Learning system / solution space** — given that data, how do you learn from it?

This distinction matters because many "algorithmic" breakthroughs are partly changes to the problem definition itself. RLHF changes the data distribution from likely text to preferred text. AlphaZero changes the data generation process through self-play. Diffusion changes the form of the training data through progressive corruption and denoising.

So when analyzing a new method, ask first:

> Did the problem change, or did the solution method change?

---

### The Compressed Framework

| Primitive | Governs | Recurring Pattern |
|---------|---------|-------------------|
| **Data** | problem definition | static → generated / selected / transformed |
| **Representation** | computational structure | local → global |
| **Parameterization** | what can adapt | fixed → learned |
| **Objective** | the learning signal | direct → surrogate / structured |
| **Constraints** | stability and allowed behavior | unconstrained → constrained |
| **Credit Assignment** | learnability | long, sparse paths → shorter, denser attribution paths |

These primitives are conceptually separable, but operationally entangled.

Changing one often forces changes elsewhere:

* changing representation can affect gradient flow
* making more computation learnable can require stronger constraints
* changing the objective can reshape the representations that emerge
* changing data can make the same architecture behave completely differently

---

### Layer 1: Data — The Problem Space

Data defines the distribution the model is trying to learn.

This includes more than a static dataset on disk:

* **dataset composition** — what examples are included or missing?
* **data generation** — humans, environments, self-play, synthetic data, reward models
* **data transformation** — augmentation, tokenization, corruption, chunking, prompting
* **data selection / weighting** — curriculum learning, replay buffers, preference weighting

Key idea:

> Data defines the problem. The learning system defines how you solve it.

This explains why:

* RLHF can dramatically change behavior without changing the base architecture much
* self-play can create a moving learning problem
* prompting can change behavior by changing the local conditioning distribution
* synthetic data can improve capabilities by changing what regions of the distribution are emphasized

---

### Layer 2: The Learning System — The Solution Space

Once the data defines the problem, the next question is:

> How do we design a system that can learn from that distribution?

The learning system has five useful primitives.

---

#### 1. Representation — Computational Structure

Representation asks:

> What kinds of structure does the model naturally express?

A useful way to think about representation is not just:

> What architecture is this?

but:

> What computational structure does this architecture make natural?

Examples:

* CNN → local spatial structure
* RNN → sequential dependence
* Transformer → global relational interaction
* MoE → sparse conditional routing through experts

The key representational pattern is often:

> local interactions → global interactions

Attention was powerful because it changed the interaction topology: distant tokens could communicate directly instead of passing information step-by-step through a recurrent chain.

---

#### 2. Parameterization — Fixed vs Learned

Parameterization asks:

> What parts of the computation are fixed, and what parts are learned?

Key pattern:

> fixed computation → learned computation

Examples:

* fixed image features → learned features
* fixed alignment heuristics → learned attention
* fixed routing → learned routing
* fixed loss weights → learned task weights
* full fine-tuning → constrained low-rank adaptation (LoRA)

This primitive asks:

> What should optimization be allowed to decide?

Parameterization is not just implementation detail. Two systems can represent similar function classes in theory but behave differently in practice because their parameterization changes optimization geometry, gradient flow, and generalization.

---

#### 3. Objective — The Learning Signal

Objective asks:

> What signal is the system optimizing?

Direct objectives are often hard:

* sparse
* noisy
* unstable
* non-differentiable
* high variance

So ML often reshapes difficult problems into objectives that are easier to optimize.

Examples:

* next-token prediction → cross-entropy
* generative modeling → denoising objective
* image generation → diffusion noise prediction
* distribution transport → flow matching velocity prediction
* reward maximization → PPO clipped surrogate objective
* representation learning → contrastive objective

Diffusion and flow matching are useful examples.

Both still try to learn a data distribution, but they choose different local learning targets:

* diffusion commonly predicts noise or a denoising direction at a timestep
* flow matching predicts a velocity field along a path between distributions

The defining design move is objective design: replacing a hard global generation problem with many structured local prediction problems.

Reference-guided methods are another objective-design pattern, but they should not be treated as a new primitive. A teacher, target network, old policy, reward model, or search process usually provides a more usable learning signal:

* teacher logits become a soft objective for distillation,
* a target Q network creates a bootstrapped value target,
* a reward model creates a scalar objective for policy optimization,
* a search process creates policy/value targets that a network can learn,
* a privileged-context teacher creates token-level targets for self-distillation.

The design question is:

> What reference signal makes the desired behavior easier to optimize?

---

#### 4. Constraints — Stability and Allowed Behavior

Constraints ask:

> What should the system avoid doing?

The boundary between objectives and constraints can be blurry.

A rough distinction:

* **Objectives** define what behavior the system is trying to produce.
* **Constraints** shape which optimization paths or solutions are allowed, discouraged, or stabilized.

In practice, many mechanisms do both.

Examples:

* weight decay
* gradient clipping
* KL penalties
* entropy regularization
* trust regions
* normalization layers
* attention scaling

Key pattern:

> unconstrained optimization → constrained optimization

PPO is a clean example:

* vanilla policy gradient: unconstrained updates
* TRPO: explicit trust-region constraint
* PPO: softer approximate constraint via clipping / KL penalties

Many "new algorithms" are really changes in how learning dynamics are constrained.

Frozen or slow references often appear here as constraints. In RLHF and DPO, a reference policy is not necessarily a better teacher. It is an anchor that keeps the updated policy from moving too far under an imperfect preference or reward signal. In PPO, the old policy snapshot defines the local region where the update is trusted. In PEFT, frozen base weights constrain which parts of the model can change.

So the reference process is often best understood as:

```text
objective says: move toward this signal
constraint says: but do not move too far from this reference
```

---

#### 5. Credit Assignment — Learnability

Credit assignment asks:

> Does useful information reliably reach the parts of the system that need updating?

This is different from optimization.

Optimization asks:

> How are parameters updated?

Credit assignment asks:

> Can the system tell which parameters, actions, or intermediate states caused success or failure?

Backpropagation sits at the intersection:

* it propagates learning signals backward through computation graphs
* optimizers like SGD or Adam use those signals to update parameters

Examples:

* residual connections shorten gradient paths
* attention shortens long-range attribution paths
* replay buffers stabilize temporal credit assignment
* GAE reduces variance in RL
* diffusion and flow matching create intermediate local prediction targets
* actor-critic loops iteratively improve behavior through evaluation and update
* critics, verifiers, and relevance masks decide which actions or tokens deserve update pressure

Key pattern:

> long, sparse, opaque attribution paths → shorter, denser, more structured attribution paths

Credit assignment is less a component category and more a cross-cutting property of learnability.

Representation determines what computations are expressible.

Credit assignment determines which of those computations are actually learnable.

Reference-guided methods can also be credit-assignment devices. A critic estimates which states or actions matter. A verifier identifies which candidate passed. RMSD-style token masks identify which teacher-student disagreements are task-relevant rather than style noise. These mechanisms do not add a new primitive; they make the existing credit-assignment problem denser, more local, or less noisy.

---

### Recurring Meta-Patterns

These transformations appear repeatedly across ML advances:

| Pattern | Description |
|---------|-------------|
| Static → Generated / Selected / Transformed | Data becomes part of the method, not just background |
| Local → Global | Expand interaction radius or communication topology |
| Fixed → Learned | Push heuristics into parameters |
| Direct → Surrogate / Structured | Replace hard goals with optimizable learning signals |
| Unconstrained → Constrained | Stabilize learning by limiting updates or behaviors |
| Long-path → Short-path | Improve credit assignment by shortening attribution paths |
| Single-pass → Iterative | Solve via refinement across learning, inference, or both |
| Fast learner → Slow reference composition | Combine objective, constraint, credit assignment, and update scheduling so a fast learner trains against a more stable or better-filtered signal |

The last row is intentionally a composition pattern, not a new primitive. A slow or frozen reference can be an objective source, a constraint, a credit-assignment aid, or an information-flow mechanism depending on the method.

---

### The Unifying Mental Model

$$
\text{Data} = \text{problem definition}
$$

$$
\text{Learning system} = \text{solution method}
$$

Within the learning system:

  * **Representation + Parameterization** define what functions are expressible,

  * **Objective + Constraints** define what behavior is incentivized and stabilized,

  * **Credit Assignment** determines whether useful learning signals can propagate through the system.

Most important methods do not move along only one axis.

They usually change several parts of the design space at once.

---

### Why ML Abstractions Feel "Leakier"

In normal software: abstractions are exact and composable.

In ML: abstractions are statistical and interacting.

* Changing normalization affects optimization
* Changing architecture affects gradient flow
* Changing loss affects representation
* Changing data changes the problem itself

Everything is coupled.

That is why the framework is useful: not because it forces every method into exactly one box, but because it helps you see which parts of the system moved.

---

### Example Decompositions

#### RLHF

| Primitive | Design Choice |
|-----------|---------------|
| Data | preference comparisons; model-generated responses scored by humans or AI systems |
| Representation | usually same base language model architecture |
| Parameterization | policy model, reward model, sometimes frozen reference model |
| Objective | produce preferred outputs, not merely likely text |
| Constraints | KL penalty / reference-model proximity |
| Credit Assignment | policy-gradient or preference-loss signal tells the model which outputs should become more likely |

What RLHF really changed: the problem definition moved from "predict likely text" toward "produce text humans prefer."

---

#### Reference-Guided Learning Pattern

This is not a separate primitive. It is a common composition of several primitives.

| Primitive | Design Choice |
|-----------|---------------|
| Data | student rollouts, replay buffers, teacher-generated examples, search traces, or preference comparisons |
| Representation | student policy, teacher model, critic, verifier, target network, or search process |
| Parameterization | fast learner plus frozen, delayed, EMA, larger, or privileged reference |
| Objective | match teacher logits, value targets, reward scores, pseudo-labels, or selected token distributions |
| Constraints | KL-to-reference, old-policy trust region, frozen base model, target update cadence |
| Credit Assignment | critic estimates, verifier results, token-level masks, advantage estimates, teacher-student disagreement |

What the pattern really does: it makes a hard or unstable update easier by composing an objective source, a stabilizing constraint, and a credit-assignment mechanism around a slower or better-filtered signal.

Examples:

* DQN uses a target network to stabilize bootstrapped value targets.
* PPO uses an old policy snapshot to constrain policy movement.
* RLHF uses a reference model to anchor reward optimization.
* Distillation uses teacher distributions as richer objectives than hard labels.
* RMSD uses a privileged teacher plus relevance mask to focus token-level updates.

---

#### Transformer

| Primitive | Design Choice |
|-----------|---------------|
| Data | tokenized sequences |
| Representation | tokens → embeddings, self-attention, residual blocks |
| Parameterization | learned Q/K/V projections, learned MLP weights, sometimes learned positional encodings |
| Objective | cross-entropy, masked prediction, or post-training rewards/preferences |
| Constraints | LayerNorm / RMSNorm, dropout, weight decay |
| Credit Assignment | backprop through residual stack; attention enables shorter long-range paths |

What made Transformers work: global representation + learned routing + residual/normalization support for trainability.

---

#### PPO

| Primitive | Design Choice |
|-----------|---------------|
| Data | on-policy rollouts from the current policy |
| Representation | policy network and value network |
| Parameterization | policy $\pi_\theta(a\|s)$, value $V_\phi(s)$ |
| Objective | advantage-weighted probability ratio |
| Constraints | clipping and optional KL penalty approximate a trust region |
| Credit Assignment | GAE, baselines, actor-critic loop, multiple epochs per batch |

What PPO really is: policy gradient + temporal credit assignment machinery + approximate trust-region constraint.

---

#### Diffusion Models

| Primitive | Design Choice |
|-----------|---------------|
| Data | progressively corrupted samples across timesteps |
| Representation | U-Net or Transformer, iterative refinement over timesteps |
| Parameterization | predict noise, clean signal, or velocity |
| Objective | local denoising / noise-prediction objective |
| Constraints | fixed noise schedule shapes the solution path |
| Credit Assignment | timesteps provide structured intermediate supervision |

What made diffusion work: data transformation + iterative refinement + objective transformation.

---

#### Flow Matching

| Primitive | Design Choice |
|-----------|---------------|
| Data | source distribution paired with target data distribution along a path |
| Representation | trajectory / vector-field view of generation |
| Parameterization | neural network predicts a velocity field |
| Objective | predict how a sample should move at a point along the path |
| Constraints | path choice and solver choices shape the transformation |
| Credit Assignment | intermediate points provide structured local prediction targets |

What flow matching really is: a change along the objective axis, turning generation into velocity prediction along a distribution path.

---

### The Checklist

When encountering a new ML method, ask:

1. Did the data distribution change?
2. Did the representation or interaction topology change?
3. What was made learnable that was previously fixed?
4. How was the objective reshaped?
5. What constraints were added, relaxed, or approximated?
6. Did credit assignment become easier?

Most papers become easier to parse once you can say:

> "This method moved these parts of the design space."

---

## Foundations Takeaways

If you remember only a few things:

1. Models = probability distributions, not truth engines
2. Training = shaping behavior via signals
3. Meaning = geometry (embeddings)
4. Performance = signal-to-noise ratio under constraints

These four ideas will let you reason about nearly every system you'll see in interviews.

---

---

## Bridge to Chapter 1

Chapter 1 builds on these primitives by explaining how modern decoder LLMs implement them through tokens, embeddings, attention, transformer blocks, training pipelines, and inference-time memory.
