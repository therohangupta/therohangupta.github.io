---
layout: page
title: "Chapter 0: Foundations & LLM Fundamentals"
guide_type: chapter
---

This chapter provides the **complete mental model** for reasoning about modern AI systems, from abstract primitives to concrete transformer architecture, training pipelines, and inference cost.

---

## Table of Contents

- TOC
{:toc}

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

Key pattern:

> long, sparse, opaque attribution paths → shorter, denser, more structured attribution paths

Credit assignment is less a component category and more a cross-cutting property of learnability.

Representation determines what computations are expressible.

Credit assignment determines which of those computations are actually learnable.

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

# Part II: LLM Fundamentals (Architecture, Training, Inference)

This section is the **core engine primer** for transformer-based LLMs.

The goal is not just to know what a transformer is, but to understand:

* how the architecture evolved,
* why modern models use specific design choices,
* how those choices affect quality, latency, memory, and cost,
* and how the pre-training → SFT → RL pipeline changes model behavior.

Use this section as the bridge from basic transformer intuition to real-world LLM systems design.

---

## 6. Big Picture: What a Modern LLM Is

A modern decoder-only LLM is usually a stack of repeated blocks that look roughly like this:

1. Token embedding
2. Positional encoding / rotary position handling
3. Attention sublayer
4. Feedforward / MLP sublayer
5. Residual connection + normalization
6. Repeat many times
7. Final normalization + linear projection to vocab logits

In compact form:

$$
\text{Token IDs} \rightarrow \text{Embeddings} \rightarrow [\text{Attention} + \text{MLP}]^{N} \rightarrow \text{Logits} \rightarrow \text{Sampling}
$$

The important thing is that each architectural choice changes one or more of these axes:

* **Quality**: how well the model predicts / reasons
* **Latency**: how long inference takes
* **Throughput**: how many tokens or requests per second it can serve
* **Memory**: how much GPU RAM it needs
* **Trainability**: how stable and efficient training is
* **Context length**: how far back the model can look effectively

---

## 7. The Transformer Core

### 7.1 Tokenization

Before the model sees text, text is split into tokens.

A token is not necessarily a word. It may be:

* a whole word,
* a subword,
* punctuation,
* part of a word.

This matters because model cost scales with the **number of tokens**, not the number of words.

If the tokenizer splits aggressively, then prompts get longer, which increases attention cost and KV-cache memory.

---

### 7.2 Embeddings

Each token ID maps to a dense vector:

$$
E: \text{token} \rightarrow \mathbb{R}^{d_{model}}
$$

Interpretation:

* tokens are discrete symbols
* embeddings turn them into continuous representations
* similar meanings tend to land near each other in vector space

The embedding matrix is one of the first places where parameter count lives.

---

### 7.3 Positional Information

Attention alone does not know token order.

A model must be told whether token A came before token B.

Classic transformer variants use either:

* learned positional embeddings,
* sinusoidal encodings,
* relative positional encodings,
* rotary positional embeddings (RoPE).

A useful mental model is:

$$
\text{representation}_i = \text{token}_i + \text{position}_i
$$

In many current decoder LLMs, RoPE is preferred because it handles relative position structure well and is efficient for decoder-only generation.

---

### 7.4 Self-Attention

Self-attention lets each token look at other tokens in the context.

For one attention head:

$$
Q = XW_Q, \quad K = XW_K, \quad V = XW_V
$$

$$
\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

Where:

* $Q$ = queries (what this token is looking for)
* $K$ = keys (what each token offers)
* $V$ = values (the information to aggregate)

Intuition:

* query/key similarity decides what to attend to
* values carry the information forward

So attention is not "reasoning" in the human sense. It is **information routing**.

#### Deeper View: Attention as a Computational Object

The formula above can be interpreted more precisely:

* $QK^T$ = similarity kernel (learned)
* softmax = normalization → probability distribution
* multiplication by V = expectation under that distribution

So each output token is:

> a weighted average of value vectors under a learned similarity distribution

**Important consequence:**

Attention is:
* linear in V
* nonlinear in Q, K

This is why:
* value representations are crucial for information content
* query/key control routing, not content

---

### 7.5 Multi-Head Attention (MHA)

Instead of one attention mechanism, transformers use multiple heads.

Each head can specialize in different kinds of relationships:

* syntax,
* coreference,
* local patterns,
* long-range dependencies,
* formatting patterns,
* etc.

If there are $h$ heads, then the model can look at the same sequence in multiple representational subspaces.

This gives expressivity, but it also creates cost, especially in the KV cache during decoding.

---

### 7.6 Feedforward / MLP Block

After attention, each token passes through an MLP:

$$
\text{FFN}(x) = W_2 \sigma(W_1 x + b_1) + b_2
$$

In modern models, this is often not a plain ReLU MLP. It is frequently a gated form such as SwiGLU, which we cover later.

The feedforward block provides non-linearity and parameter capacity. In many architectures, the MLP accounts for a large fraction of the FLOPs per token.

---

### 7.7 Residual Connections + Normalization

Each block is wrapped by residual connections:

$$
x_{l+1} = x_l + f(x_l)
$$

Residual paths help gradients flow and make deep transformers trainable. **Where normalization sits** relative to the sublayer and the residual branch is not cosmetic: it changes gradient behavior, how “clean” the residual stream stays, and how scale drifts across depth.

#### Classic setups (quick refresher)

**Post-norm (original Transformer)**

Each block applies the sublayer, adds the residual, then normalizes:

$$
x \leftarrow \text{LayerNorm}\bigl(x + \text{Sublayer}(x)\bigr)
$$

**Problem:** gradients can become difficult in very deep networks.

**Pre-norm (modern default)**

Move normalization *before* the sublayer:

$$
x \leftarrow x + \text{Sublayer}\bigl(\text{LayerNorm}(x)\bigr)
$$

Intuition: the residual stream carries a relatively “clean” main path; the sublayer sees a normalized input. This is the usual choice in modern stacks (often **RMSNorm** instead of LayerNorm, same placement idea).

#### The pattern behind “extra norm outside the residual”

Pre-norm fixed many training-stability issues, but it introduced another: the residual stream is an **uncontrolled accumulation** of per-block updates. Researchers add **extra normalization** to:

* control how large each update is before it is added back,
* control **global scale** across depth,
* stabilize very deep models and large learning rates.

Below are three recurring patterns (names vary by paper; PaLM-style, LLaMA-family discussions, DeepNet, NormFormer, etc. all play in this space).

#### Variant A: Norm on the sublayer output (NormFormer-style)

Instead of only:

$$
x \leftarrow x + \text{Sublayer}\bigl(\text{LN}_1(x)\bigr)
$$

you effectively **normalize what gets added**:

$$
x \leftarrow x + \text{LN}_2\Bigl(\text{Sublayer}\bigl(\text{LN}_1(x)\bigr)\Bigr)
$$

* $\text{LN}_1$: pre-norm (conditions the sublayer input).
* $\text{LN}_2$: extra normalization on the **update** before it enters the residual stream.

**Intuition:** without $\text{LN}_2$, update magnitudes can grow with depth; with $\text{LN}_2$, each increment is re-scaled (“whitened”) before addition, which often improves stability and sometimes quality.

#### Variant B: Norm after the residual stream (block or periodic output)

Still pre-norm *inside* the usual block, but you also apply normalization to the **running residual state**, e.g. after a block or every $N$ layers:

$$
x \leftarrow x + \text{Sublayer}\bigl(\text{LN}(x)\bigr), \qquad x \leftarrow \text{LN}_{\text{out}}(x)
$$

This is **not** the same as classic post-norm *inside* the block: the inner block stayed pre-norm for training; $\text{LN}_{\text{out}}$ acts more like **re-centering / rescaling the global stream** (common in some scaling-focused designs).

#### Variant C: Final LayerNorm after the full stack

Very standard today (e.g. GPT-2 did not always do this; later GPT-style models typically do):

```text
for each block:
    x ← x + Sublayer(LN(x))
x ← FinalLayerNorm(x)
```

**Why:** even if every block is stable, the **aggregate** representation can drift in scale across depth. A **final** normalization fixes the distribution before the LM head (vocab projection), so logits behave predictably.

#### Mental model: the residual stream as state

Think of depth as a discrete dynamical system on a hidden state:

$$
x_0 \to x_1 \to \cdots \to x_L, \qquad x_{l+1} = x_l + \Delta x_l
$$

The design question is: **how do we control $\Delta x_l$ and the overall scale of $x$?** Different norm placements attack different parts of that problem:

| Norm placement | What it primarily stabilizes |
| -------------- | ---------------------------- |
| Pre-norm | Input to each sublayer |
| Post-norm (classic block) | Whole block output (historical default) |
| Extra norm on sublayer output | **Magnitude of the update** $\Delta x$ before add |
| Norm after blocks / periodic | **Global** residual stream scale mid-stack |
| Final norm | **Global** representation scale before the head |

#### Takeaway

Modern transformers usually **combine pre-norm with one or more extra normalizations** to tame both **per-layer updates** and **global scale**. A “second norm outside the residual” in a diagram usually means one of: **(1)** normalize the branch output before adding (NormFormer-style), **(2)** normalize the stream after some blocks or on a schedule, **(3)** a **final** LayerNorm/RMSNorm at the top of the stack (often all three ideas appear in different combinations across families).

---

## 8. Why the Transformer Became the Dominant Architecture

The original transformer replaced recurrence with attention.

That gave three huge advantages:

1. **Parallel training** — all tokens in a sequence can be processed simultaneously during training.
2. **Long-range dependency handling** — attention can connect distant tokens directly.
3. **Scalable representation learning** — deep stacks of attention + MLP blocks work well at large scale.

The original transformer paper showed that attention-based sequence models can outperform older recurrence-heavy approaches while training much faster on parallel hardware.

---

## 9. The Architecture Progression

A good interview answer often comes from understanding the progression rather than memorizing one model.

Think of the design evolution like this:

### Stage A — Vanilla Transformer

* multi-head attention
* standard FFN
* full quadratic attention
* simple but expensive at long sequence lengths

### Stage B — More Stable / Efficient Core Blocks

* pre-norm
* RMSNorm
* RoPE
* SwiGLU
* better initialization and scaling choices

These changes mostly improved trainability and efficiency without changing the high-level transformer structure.

### Stage C — Faster Decoding Through KV-Cache Reduction

* MQA
* GQA

These reduce the size of the key/value cache and improve decode-time bandwidth usage.

### Stage D — Less Expensive Long-Context Attention

* sliding window attention
* sparse attention
* block-sparse attention
* hybrid local/global patterns

These reduce the cost of attending to very long sequences.

### Stage E — Parameter Efficiency Through Sparsity

* MoE / sparse expert routing

These let models have very large total parameter counts while only activating a small subset per token.

### Stage F — Kernel / Serving Improvements

* FlashAttention
* FlashAttention-2 / 3 style kernel improvements
* PagedAttention / paged KV cache
* speculative decoding
* quantization

These do not fundamentally change the model's learning objective, but they can drastically change real serving costs.

---

## 10. MHA vs MQA vs GQA

This is one of the most important architecture progressions for interview purposes.

### 10.1 Standard Multi-Head Attention (MHA)

In MHA, each head has its own Q, K, and V projections.

If there are $h$ heads, then the KV cache stores keys and values for every head.

#### Pros

* strong quality
* flexible attention patterns
* standard baseline

#### Cons

* large KV cache
* larger memory bandwidth cost during decoding
* higher inference latency for long context

---

### 10.2 Multi-Query Attention (MQA)

MQA shares the key and value heads across all query heads.

So instead of having separate K/V per head, all heads use shared K/V.

#### Why it helps

The KV cache becomes much smaller.
That directly lowers memory bandwidth requirements during autoregressive decoding.

#### Tradeoff

* much faster decode
* smaller KV cache
* but possible quality degradation compared with full MHA

#### Interview framing

MQA is a classic example of trading some expressivity for cheaper inference.

---

### 10.3 Grouped-Query Attention (GQA)

GQA is the middle ground.

Instead of one shared K/V pair for all heads, heads are divided into groups, and each group shares K/V.

#### Why GQA exists

It aims to keep most of the quality of MHA while gaining much of the decode-time efficiency of MQA.

#### Intuition

* MHA: one KV set per head
* MQA: one KV set for all heads
* GQA: a few KV sets shared across groups of heads

#### Why it matters in practice

GQA has become very common in modern decoder LLMs because it is a strong quality/efficiency compromise.

---

### 10.4 Quantifying the KV Cache

Let:

* $h$ = query heads
* $h_{kv}$ = KV heads

KV size $\propto h_{kv}$

| Type | KV Heads |
|------|----------|
| MHA | $h$ |
| GQA | $h / g$ |
| MQA | 1 |

For a model with:

* batch size $B$
* layers $L$
* context length $T$
* KV heads $h_{kv}$
* head dim $d$

**KV Cache Memory:**

$$
\text{Memory} \approx B \cdot L \cdot T \cdot h_{kv} \cdot d \cdot 2
$$

(×2 for K and V)

**What this means:**

* doubling context length → doubles memory
* doubling KV heads → doubles memory
* doubling layers → doubles memory

This is why:
* GQA is huge
* long conversations are expensive
* batching is hard

---

### 10.5 How MQA/GQA Affect Latency and Memory

During decoding, the bottleneck is often loading KV cache, not just doing math.

Even if FLOPs stay similar:

> reducing $h_{kv}$ reduces memory reads per token

So reducing KV heads can materially improve:

* GPU memory usage
* batch size
* throughput
* token latency

This is why MQA/GQA are so important for serving.

A rough mental model:

* MHA = largest KV cache
* GQA = medium KV cache
* MQA = smallest KV cache

---

## 11. Sparse and Sliding-Window Attention

Full attention lets every token look at every other token.
That is powerful, but expensive.

### 11.1 Full Attention Cost

For a sequence of length $n$:

* attention score computation is roughly $O(n^2 d_k)$
* naive attention memory for the score matrix is $O(n^2)$

That quadratic growth is the reason long context becomes expensive.

---

### 11.2 Sliding-Window Attention (SWA)

Sliding-window attention restricts each token to attend only to a local neighborhood of size $w$.

So each token attends to only nearby tokens.

#### Complexity

* roughly $O(nw)$ instead of $O(n^2)$

If $w \ll n$, this is a huge win.

#### Why use it

* long documents
* local coherence matters more than global all-to-all access
* cheaper inference and training for long sequences

#### Tradeoff

* can miss long-range dependencies unless combined with global tokens or other mechanisms

---

### 11.3 Sparse Attention

Sparse attention is the broad category where not all token pairs interact.

Possible sparsity patterns:

* local windows
* strided attention
* block-sparse patterns
* global tokens + local tokens
* task-specific routing

#### Why it helps

Reducing the number of attended pairs lowers compute and memory.

#### Tradeoff

You need to design the sparsity pattern carefully or you lose information that the task needs.

---

### 11.4 When Sparse/Sliding Actually Works

**Full attention assumption:**

> every token may need every other token

**Reality:**

> most dependencies are local

Sliding/sparse attention is basically the model saying:

> "Most of the useful signal is nearby, so I will spend attention budget there."

That is not always true, but it is often a very good approximation for long sequences.

#### Hybrid pattern (modern models)

* local window attention
* periodic global tokens

This preserves:
* efficiency
* long-range signal

---

## 12. SwiGLU and Modern Feedforward Design

The classic transformer feedforward block is often replaced with a gated variant.

### 12.1 Why the FFN Matters

In many transformers, the FFN is a major contributor to model capacity and compute.

A feedforward block processes each token independently but non-linearly, giving the model the ability to transform attention outputs into richer representations.

---

### 12.2 GLU Family Intuition

A gated linear unit uses one projection to produce values and another to produce gates.

A simplified form:

$$
\text{GLU}(x) = (xW_1) \odot \sigma(xW_2)
$$

The gate decides how much of each component passes through.

---

### 12.3 SwiGLU

SwiGLU is a GLU variant that uses the Swish/Sigmoid-weighted gating form.

A conceptual form looks like:

$$
\text{SwiGLU}(x) = (xW_1) \odot \text{Swish}(xW_2)
$$

#### Why it is popular

* often improves quality over a plain MLP
* strong empirical tradeoff in decoder LLMs
* helps with gradient flow and representational flexibility

#### Cost intuition

SwiGLU usually adds a bit more projection work than a very simple MLP, but the quality gains are often worth it.

---

### 12.4 Why SwiGLU Wins (Deeper View)

Standard FFN:

$$
W_2 \sigma(W_1 x)
$$

SwiGLU:

$$
(xW_1) \odot \text{Swish}(xW_2)
$$

#### Interpretation

Instead of:

> transform everything equally

We get:

> gate each feature dimension

#### Effect

* dynamic feature selection
* smoother gradients
* better conditioning

---

## 13. MoE: Mixture of Experts

MoE is another major modern architecture direction.

### 13.1 Core Idea

Instead of using one dense feedforward block for every token, the model has many expert subnetworks.

A router decides which expert(s) to activate for each token.

So the model has:

* large total parameter count
* smaller active compute per token

This is the key trick.

---

### 13.2 Sparse Activation

If only a few experts are active for each token, then:

* model capacity can be huge
* inference FLOPs stay manageable

That is why MoE is attractive for scaling.

#### Scaling insight

* total params ↑↑
* compute per token ~ constant

---

### 13.3 Pros

* more parameters without proportional compute growth
* can improve quality at fixed FLOPs
* useful for scaling up model capacity

### 13.4 Cons

* routing complexity
* load balancing issues
* communication overhead across devices
* training instability if poorly tuned
* serving complexity

#### Hidden costs

* routing imbalance
* network communication
* latency spikes

---

### 13.5 Interview framing

MoE is a way to say:

> "Not every token needs the whole model; let different submodels specialize."

That's powerful, but only if routing is stable and efficient.

**Why MoE doesn't always reduce latency in practice:**

Because routing introduces communication overhead and imbalance. Even if FLOPs are lower, network and scheduling costs can dominate.

---

## 14. Training Pipeline: Pretraining → SFT → Preference Optimization

A lot of interview candidates understand the model architecture but not the training pipeline.

You should know the standard progression.

---

### 14.1 Pretraining

The model is trained on massive text corpora with next-token prediction.

Objective:

$$
\mathcal{L}_{\text{pretrain}} = -\sum_t \log P(y_t \mid y_{<t})
$$

Or conditionally on some prompt/context:

$$
-\log P(y \mid x)
$$

Equivalent to:

> minimizing KL divergence to true distribution

#### What pretraining gives you

* language fluency
* world knowledge patterns
* syntax and semantics
* some emergent reasoning capacity

#### What pretraining does not give you

* reliable instruction following
* consistent tool use
* user-aligned behavior
* safety constraints

---

### 14.2 Supervised Fine-Tuning (SFT)

SFT trains the model on instruction-response pairs.

This is where the model learns to behave like an assistant.

#### Objective

Same basic cross-entropy idea, but the data now looks like:

* instruction
* conversation
* task demonstration

Changes data distribution:

$$
P_{\text{pretrain}}(x) \rightarrow P_{\text{instruction}}(x)
$$

#### Why it matters

SFT changes the model from a general text predictor into a more controlled task-following system.

---

### 14.3 Post-SFT Preference Optimization

After supervised fine-tuning (SFT), modern LLMs and VLMs often undergo an additional post-training stage focused on:

* alignment
* instruction quality
* safety
* reasoning behavior
* tool usage
* stylistic consistency
* preference optimization

The goal is no longer primarily:

> "learn language structure"

but instead:

> "shape the model's behavior."

Modern post-training usually starts from preference data of the form:

$$
(x, y_w, y_l)
$$

Where:

* $x$ = prompt/context
* $y_w$ = preferred response
* $y_l$ = rejected response

Humans, or increasingly AI systems, compare outputs and indicate which response is better.

The major modern post-SFT approaches are:

1. **PPO-based RLHF**
2. **DPO and related direct preference optimization methods**

These approaches are closely related mathematically but differ substantially in:

* optimization style
* engineering complexity
* stability
* scalability
* applicability to sequential/agentic behavior

---

#### 14.3.a The High-Level Pipeline

Modern training typically looks like:

$$
\text{Pretraining}
\rightarrow
\text{SFT}
\rightarrow
\text{Preference Optimization}
$$

Where:

| Stage | Learns |
|---|---|
| Pretraining | language/world structure |
| SFT | instruction following |
| Preference optimization | desired behavior, typically what humans want |

A useful mental model is:

* Pretraining → "learn the world"
* SFT → "learn to act like an assistant"
* Post-training → "learn what humans prefer"

---

#### PPO-Based RLHF (Classical Pipeline)

The original large-scale alignment pipeline used by systems like early ChatGPT is commonly called:

> RLHF — Reinforcement Learning from Human Feedback.

However, this term is slightly misleading.

Humans usually do **not** directly provide rewards during the RL optimization loop itself.

Instead, the pipeline is:

$$
\text{Human Preferences}
\rightarrow
\text{Reward Model}
\rightarrow
\text{RL Optimization}
$$

The reward model acts as a scalable approximation of human judgment.

#### 14.3.b Stage 1 — Reward Model Training

Train a separate reward model:

$$
r_\phi(x,y)
$$

which outputs a scalar score indicating how preferred a response is.

Typically:

* initialize from SFT weights
* attach a scalar reward head
* fine-tune on pairwise preference comparisons

The reward model does **not** generate text.
It only scores responses.

Input:

$$
(x,y_w,y_l)
$$

Loss to minimize:

$$
\mathcal{L}_{RM}
=
-\log \sigma
\left(
r_\phi(x,y_w)-r_\phi(x,y_l)
\right)
$$

This is essentially a Bradley-Terry / pairwise logistic ranking loss.

Interpretation:

> preferred responses should receive higher reward.

At the end of this stage there are now TWO separate models:

| Model | Purpose |
|---|---|
| Policy model $\pi_\theta$ | generates text |
| Reward model $r_\phi$ | scores text |

This distinction is extremely important.

#### 14.3.c Stage 2 — PPO Reinforcement Learning

Now reinforcement learning begins.

The policy samples responses:

$$
y \sim \pi_\theta(\cdot|x)
$$

The reward model scores them:

$$
r_\phi(x,y)
$$

Then PPO updates the policy:

$$
\max_\theta
\;
\mathbb{E}[r_\phi(x,y)]
-
\beta
D_{KL}(\pi_\theta \| \pi_{SFT})
$$

Interpretation:

* maximize preferred behavior
* while preventing the policy from drifting too far from the SFT model

The KL term stabilizes optimization and acts like a trust-region constraint.

---

#### DPO (Direct Preference Optimization)

DPO simplifies the PPO-RLHF pipeline substantially.

Instead of:

$$
\text{Preferences}
\rightarrow
\text{Reward Model}
\rightarrow
\text{PPO}
$$

DPO directly optimizes the policy using preference pairs:

$$
\text{Preferences}
\rightarrow
\text{Policy}
$$

No separate reward model is trained.
No PPO reinforcement learning loop is required.

#### 14.3.d Core Mathematical Insight Behind DPO

The DPO paper showed that the optimal PPO-RLHF policy has a closed-form relationship to reward:

$$
\pi^*(y|x)
\propto
\pi_{ref}(y|x)
\exp\left(
\frac{1}{\beta}r(x,y)
\right)
$$

Rearranging:

$$
r(x,y)
=
\beta
\log
\frac{\pi(y|x)}
{\pi_{ref}(y|x)}
$$

This means:

> policy log-ratios can implicitly represent reward.

So instead of learning:

$$
r_\phi(x,y)
$$

explicitly, DPO optimizes preferences directly in policy space.

#### 14.3.e DPO Objective

The DPO loss to minimize becomes:

$$
\mathcal{L}_{DPO}
=
-\log
\sigma
\left(
\beta
\left[
\log
\frac{\pi_\theta(y_w|x)}
{\pi_{ref}(y_w|x)}
-
\log
\frac{\pi_\theta(y_l|x)}
{\pi_{ref}(y_l|x)}
\right]
\right)
$$

This looks extremely similar to reward-model training because mathematically:

$$
r(x,y)
\leftrightarrow
\beta
\log
\frac{\pi_\theta(y|x)}
{\pi_{ref}(y|x)}
$$

A useful interpretation is:

> DPO is Bradley-Terry preference learning expressed directly in policy space instead of reward space.

#### 14.3.f Supervised Preference Learning vs Reinforcement Learning

This is a subtle but important point:

> DPO is usually trained like supervised learning, while PPO-RLHF is actual reinforcement learning.

DPO uses preference pairs as a fixed dataset and optimizes a differentiable loss with standard backpropagation. There is no environment interaction, no rollout loop, no advantage estimation, and no policy-gradient update. In practice, it feels much closer to supervised fine-tuning with a preference-shaped loss.

PPO-RLHF is different. The current policy generates new samples, a reward model scores those samples, and PPO updates the policy based on reward while constraining drift from the reference/SFT model. That is an actual RL loop: sample actions from the current policy, score outcomes, and improve the policy from those sampled trajectories.

So the clean interview distinction is:

| DPO | PPO-RLHF |
|---|---|
| supervised-style preference learning | reinforcement learning |
| fixed preference dataset | fresh rollouts from current policy |
| backprop through a preference loss | policy-gradient optimization |
| no environment interaction | online sampling loop |
| best viewed as offline alignment | best viewed as RL-based behavior optimization |

---

#### Online RL vs Offline Preference Optimization

Another way to state the distinction is:

| Method | Optimization Style |
|---|---|
| PPO RLHF | online, on-policy reinforcement learning |
| DPO | offline supervised-style preference optimization |

#### 14.3.g What "On-Policy" Means

In on-policy reinforcement learning:

> the model learns from trajectories generated by its current policy.

The policy continuously generates new outputs:

$$
y \sim \pi_\theta(\cdot|x)
$$

and learning happens from those newly sampled rollouts.

This enables:

* exploration
* online adaptation
* trajectory optimization
* long-horizon credit assignment

But it also introduces:

* instability
* expensive sampling
* reward hacking risks
* engineering complexity

PPO-RLHF is on-policy because the model repeatedly samples fresh outputs from the current policy during RL optimization.

#### 14.3.h What "Offline" Means

DPO is fundamentally an offline preference optimization method, not off-policy RL in the usual reinforcement-learning sense.

It learns from a fixed dataset:

$$
(x,y_w,y_l)
$$

without needing environment rollouts or online exploration.

Advantages:

* simpler optimization
* lower engineering complexity
* stable supervised-style training
* no rollout generation
* no reward model collapse

But it also means:

* no exploration
* no environment interaction
* limited trajectory optimization
* weaker support for delayed rewards

DPO works best when preferences can be expressed as:

> static comparisons between candidate responses.

---

#### PPO RLHF vs DPO Tradeoffs

Neither method universally dominates the other.

They solve somewhat different optimization problems.

| PPO RLHF | DPO |
|---|---|
| explicit reward model | implicit reward via policy |
| online, on-policy RL | offline supervised-style preference optimization |
| rollout generation required | static dataset training |
| supports trajectory optimization | optimized for static comparisons |
| supports exploration | no exploration |
| strong for agents/tool use | strong for conversational alignment |
| more flexible | simpler and more stable |
| higher engineering complexity | easier implementation |
| can optimize delayed rewards | best for local preference ranking |
| vulnerable to reward hacking | vulnerable to dataset limitations |

#### When PPO RLHF Is Useful

RL-style optimization remains important when:

* rewards are delayed
* actions affect future states
* exploration matters
* environment interaction matters
* long-horizon reasoning matters
* trajectory optimization matters

Examples:

* agents
* browser interaction
* robotics
* tool-using systems
* code execution
* autonomous planning systems
* multi-step reasoning systems

These problems naturally involve trajectories:

$$
(s_0,a_0,s_1,a_1,\dots,s_T)
$$

rather than single static responses.

This is fundamentally where reinforcement learning becomes important.

#### When DPO Works Well

DPO is strongest when the optimization problem is mostly:

> preference ranking over static candidate outputs.

Examples:

* conversational quality
* tone alignment
* refusal behavior
* stylistic consistency
* response helpfulness
* instruction-following quality
* harmlessness shaping

In these settings:

* exploration is less important
* trajectory credit assignment is unnecessary
* preference ranking is often sufficient

#### Important Practical Reality

A common misconception is:

> "DPO replaced PPO-RLHF."

That is not the modern frontier reality.

Instead:

* DPO became extremely influential for stable offline preference alignment
* while RL remains important for sequential decision-making and agentic behavior

Modern frontier systems increasingly combine:

* SFT
* rejection sampling
* DPO-style optimization
* reward modeling
* online RL
* verifier-based training
* search/self-play
* synthetic preference generation
* tool-use optimization

The real trend is:

> post-training diversified into multiple specialized optimization regimes.

#### Broader Family of Preference Optimization Methods

DPO is part of a rapidly evolving family of preference optimization methods.

| Method | Core Idea |
|---|---|
| PPO-RLHF | reward-model-based RL optimization |
| DPO | direct preference optimization in policy space |
| IPO | improved stability variants of DPO |
| ORPO | odds-ratio preference optimization |
| SimPO | simplified preference optimization |
| KTO | Kahneman-Tversky-inspired utility shaping |
| RLAIF | AI-generated preference feedback |
| Constitutional AI | rule-guided preference generation |
| Verifier-based RL | optimize correctness via learned verification |
| Rejection sampling | generate many candidates, keep best |

Most of these methods attempt to improve one or more of:

* stability
* sample efficiency
* alignment quality
* reward robustness
* annotation efficiency
* reasoning quality
* long-horizon behavior

#### Modern Practical Reality

Modern LLM and VLM post-training is increasingly hybrid.

Large production systems rarely use only one method.

A realistic modern pipeline may include:

1. SFT
2. rejection sampling
3. DPO-style preference alignment
4. verifier filtering
5. RL optimization for reasoning or agents
6. safety tuning
7. continual synthetic-data improvement

The boundary between:

* supervised learning
* preference optimization
* reinforcement learning
* search
* self-play
* verification

is becoming increasingly blurred.

#### Key Insight

A strong modern mental model is:

| Technique | Best At |
|---|---|
| SFT | imitation and formatting |
| DPO | stable offline preference alignment |
| PPO / RL | trajectory optimization and agent behavior |
| Verifier-based RL | correctness optimization |
| Search/self-play | capability amplification |

The key conceptual distinction is:

| DPO | PPO RLHF |
|---|---|
| optimize preferences over outputs | optimize rewards over trajectories |
| offline preference learning | online policy optimization |
| static comparisons | sequential decision-making |

Modern AI systems increasingly use combinations of all of these.

---

### 14.4 Why Preference Optimization Matters

This stage changes not just knowledge, but behavior.

It can improve:

* instruction following
* tone
* refusal behavior
* robustness to ambiguous prompts

But it can also introduce issues such as:

* reward hacking
* over-optimization for style over substance
* reduced diversity
* brittleness outside the training distribution

---

### 14.5 Common Modern Pipeline Summary

A useful compact model of modern post-training is:

**Pretrain** → learn language and world patterns
**SFT** → learn to respond like an assistant
**Preference optimization** → learn to align with human judgments
**Safety tuning** → reduce harmful or undesired outputs
**Tool / task fine-tuning** → improve operational behavior

#### Key insight

* Pretraining = knowledge
* SFT = format + behavior
* Preference optimization = preferences + alignment

---

## 15. Inference Cost and Systems

This is the part interviewers often care about most in applied roles.

---

### 15.1 Where Inference Cost Comes From

There are two main phases:

#### A. Prefill

The prompt is processed all at once.
This looks much like a training forward pass.

$$
O(L \cdot T^2 \cdot D)
$$

* compute heavy
* GPU-efficient (parallel)

#### B. Decode

The model generates one token at a time autoregressively.
This is where KV cache and memory bandwidth dominate.

$$
O(L \cdot T \cdot D)
$$

* sequential
* memory-bound

#### Total decode (K tokens)

$$
O(L \cdot D \cdot (KT + K^2/2))
$$

---

### 15.2 Attention Runtime Basics

For a sequence of length $n$:

#### Naive full self-attention

* score matrix: $O(n^2)$
* memory: $O(n^2)$ if materialized directly

#### With optimized kernels like FlashAttention

* compute is still fundamentally attention-like and quadratic in token interactions
* but memory is reduced dramatically by avoiding materializing the full attention matrix
* wall-clock time improves because the kernel is IO-aware

#### Key practical idea

Sometimes the model is not compute-bound. It is **memory-bound**.

That means changing memory access patterns can matter as much as changing FLOPs.

---

### 15.3 Why Memory Bandwidth Wins

GPU bottleneck is often:

> bytes/sec, not FLOPs/sec

Each decode step:

* reads KV cache
* reads weights
* writes activations

#### Bottleneck hierarchy (real-world)

1. Memory bandwidth
2. KV cache size
3. Attention compute
4. MLP compute

Even if:
* model is small
* FLOPs are manageable

Memory bandwidth dominates.

---

### 15.4 Decode-Time Complexity with KV Cache

Suppose the prompt length is $p$ and the model generates $L$ new tokens.

At decode step $t$, the model attends to the existing context of length roughly $p + t$.

So per new token, attention cost grows with context length.

Rough intuition:

* one new token at step $t$ costs about $O((p+t)d)$ per layer for attention against the cached keys/values
* generating many tokens gives total decode cost roughly proportional to the area under that growth curve

This is why long chat histories and long generations are expensive.

---

### 15.5 How MQA/GQA Change Cost

Reducing the number of KV heads reduces:

* KV cache size
* memory bandwidth required per decoding step
* pressure on batching

This often improves throughput and reduces latency without changing the overall transformer structure.

**Why reducing KV heads improves latency even if FLOPs are similar:**

Because decode-time cost is dominated by memory bandwidth. Fewer KV heads means less data read per step, which directly reduces latency.

---

### 15.6 How Sliding-Window Attention Changes Cost

If each token attends only to a window of size $w$, then decode-time attention becomes much cheaper.

Instead of growing with total context length, it grows mainly with the window size.

That means:

* lower latency
* lower compute
* lower memory bandwidth usage

But the model may need special design choices to preserve long-range information.

---

### 15.7 How MoE Changes Cost

MoE changes the cost story differently.

#### Dense model

Every token uses all parameters in the block.

#### MoE model

Every token uses only a few experts.

So MoE can increase model capacity a lot without proportional per-token compute.

But it introduces:

* routing overhead
* communication costs
* expert load-balancing problems

That means lower FLOPs does not automatically mean lower wall-clock latency.

---

### 15.8 How SwiGLU Changes Cost

SwiGLU usually improves the quality/efficiency balance of the FFN.

It may slightly increase the projection work compared with a very simple FFN, but it can improve performance enough that the extra cost is worthwhile.

This is a classic architectural tradeoff:

* modest extra compute
* better behavior / accuracy

---

### 15.9 FlashAttention

FlashAttention is not a new model architecture. It is a better attention implementation.

Its key benefit is reducing memory reads/writes by tiling and being IO-aware.

#### Naive attention:

* materializes $n \times n$ matrix
* huge memory traffic

#### FlashAttention:

* tiles computation
* keeps data in SRAM
* avoids HBM writes

#### Result

Same math, much faster runtime.

#### Why this matters

For long sequences, naive attention spends a lot of time moving data around.

FlashAttention reduces that bottleneck, which often translates into real wall-clock speedups.

---

### 15.10 PagedAttention / KV Paging

In serving, variable-length requests create KV cache fragmentation.

PagedAttention stores KV cache in paged blocks, which helps:

* reduce wasted memory
* batch more requests
* serve more efficiently at scale

This is an inference-systems improvement, but it matters a lot in practice because the architecture alone does not determine serving cost.

---

### 15.11 Unifying Cost Mental Model

Everything reduces to:

| Bottleneck | Fix |
|------------|-----|
| KV cache too big | MQA / GQA |
| Attention too expensive | sparse / sliding |
| FFN weak | SwiGLU |
| capacity limit | MoE |
| memory movement | FlashAttention |
| batching inefficiency | paging |

---

### 15.12 One Important Interview Answer

If asked:

> "Why are modern LLMs so expensive to serve?"

A strong answer is:

> Because decode-time generation is sequential, attention requires reading large KV caches, and memory bandwidth becomes the bottleneck. Architectural choices like MQA/GQA reduce KV size, sparse attention reduces attended tokens, and kernels like FlashAttention improve IO efficiency.

That answer connects architecture to actual cost.

#### The Meta-Answer

If they push you hard:

> "The key shift in LLM architecture is that we stopped optimizing just FLOPs and started optimizing memory bandwidth and data movement. That's why KV cache size, attention patterns, and kernel efficiency matter as much as model size."

---

## 16. Modern Design Pattern

A lot of current decoder-only models use a pattern like:

* token embeddings
* RoPE or related positional handling
* RMSNorm / pre-norm
* grouped-query attention
* SwiGLU feedforward blocks
* residual connections
* optionally sliding-window or sparse attention in some layers
* optionally MoE in place of dense FFN blocks
* optimized kernels for attention and KV cache handling

The key is not any single trick.
It is the composition of many small efficiency improvements.

That is why many modern models feel like they are all variants of the same core template.

---

## 17. Architectural Tradeoff Cheat Sheet

### Vanilla MHA

* **Best for:** simplicity, baseline quality
* **Bad for:** decode-time memory and bandwidth

### MQA

* **Best for:** fast decoding
* **Bad for:** possible quality drop

### GQA

* **Best for:** balanced quality and inference efficiency
* **Bad for:** still some KV overhead

### Sliding-Window / Sparse Attention

* **Best for:** long-context efficiency
* **Bad for:** limited global interaction unless augmented

### SwiGLU

* **Best for:** stronger feedforward expressivity
* **Bad for:** slightly more projection complexity

### MoE

* **Best for:** scaling parameters without proportional FLOPs
* **Bad for:** routing, communication, and serving complexity

### FlashAttention / PagedAttention

* **Best for:** serving efficiency and memory reduction
* **Bad for:** implementation complexity

---

## Common LLM Failure Modes

The same architectural choices that make LLMs powerful also create predictable failure modes. In interviews, it is useful to describe these as system behaviors rather than as vague "model mistakes."

### Long-Context Degradation

Longer context does not automatically mean better answers. Additional tokens increase prefill cost and can dilute the evidence the model should attend to. A model may miss a key fact, overweight a nearby distractor, or blend conflicting sources.

This connects directly to Chapter 2 retrieval: the context builder should select compact evidence, not dump every possibly relevant document into the prompt.

### Hallucination Under Weak Evidence

The model samples plausible continuations from its learned distribution. If the prompt lacks grounded evidence, the model may fill gaps with high-probability but false details.

RAG, citations, tool checks, and refusal policies reduce this risk, but they do not eliminate it. The system still needs validation that the answer is supported by the context.

### Distribution Shift

Model behavior changes when prompts, users, domains, tools, or retrieved documents differ from the data distribution the model was trained or tuned on.

Examples include a support bot seeing legal language, a code model reading an unfamiliar framework, or a general assistant receiving tool outputs formatted in a surprising way. Good systems monitor slices, not only aggregate quality.

### Prompt Sensitivity

Small prompt changes can change model behavior because prompts are soft constraints, not compiled programs. Reordering instructions, adding examples, or changing a schema can shift the output distribution.

This is why Chapter 1 treats prompts as versioned runtime interfaces that need tests, rollouts, and rollback.

### Serving Instability

Architecture and serving are coupled. Long prompts, large KV caches, MoE routing imbalance, memory fragmentation, and batching collapse can all make latency or reliability worse even when model quality is unchanged.

Strong answers connect model internals to production symptoms: "Why did latency spike?" may be a KV-cache, batching, routing, or prompt-length problem, not just an infrastructure problem.

---

## What to Say in an Interview

You want to sound like someone who understands the progression, not someone who memorized buzzwords.

A very strong answer might sound like:

> "Modern decoder LLMs are still transformer stacks, but the important progression is that we've optimized different bottlenecks separately. MQA and GQA reduce KV-cache cost at decode time, sliding-window or sparse attention reduces the number of token interactions, SwiGLU improves the feedforward block, and MoE increases capacity without proportionally increasing FLOPs. Then kernel-level systems like FlashAttention and paged KV management improve the actual serving latency and throughput. So the architecture and the serving stack have to be designed together."

That is the right level of answer for an applied AI interview.

---

## LLM Fundamentals Takeaways

If you remember only one thing from this section:

> A transformer is not just "attention." It is a family of design choices around how tokens interact, how much information is cached, how much compute is activated, and how efficiently those operations are executed.

For interviews, the strongest candidates can explain not just what a component is, but **why it exists**, **what bottleneck it addresses**, and **what tradeoff it introduces**.

The progression from vanilla transformer to modern LLM is not a single insight. It is accumulated engineering across attention (MQA/GQA, sparse windows), feedforward (SwiGLU), capacity (MoE), training (SFT + RL), and serving (FlashAttention, PagedAttention, speculative decoding). Each change targets a different cost: KV-cache memory, attention compute, parameter efficiency, or memory bandwidth. Strong answers connect architecture choices to observable production behavior — latency, throughput, memory pressure, and failure modes under load.

---

## What Comes Next

Chapter 1 moves from architecture into **LLM engineering**:

* prompting
* structured outputs
* tool use
* deterministic vs stochastic behavior
* orchestration patterns
* practical ways to make models reliable
