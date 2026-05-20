---
layout: post
title: "Navigating the Machine Learning Design Space: Understanding the Primitives Behind the Progress"
date: 2026-05-15 10:00:00 -0800
categories: general
---

My first year as an ML Engineer is almost complete, and one of the biggest shifts in how I understand the field has been learning to see machine learning less as a stream of disconnected methods and more as a <span class="term" tabindex="0" data-tooltip="A way of seeing ML methods as choices along a few recurring axes, instead of as disconnected tricks."><strong>design space</strong></span>.

When I first started studying ML in college, and even when I started working in industry, the field often felt like a pile of separate words being yelled at you without reason: transformers, diffusion, VLA, PPO, <span class="term" tabindex="0" data-tooltip="Reinforcement Learning from Human Feedback: training signal from human preferences, not just next-token prediction.">RLHF</span>, <span class="term" tabindex="0" data-tooltip="Low-Rank Adaptation: a cheaper way to fine-tune by learning small update matrices instead of changing every weight.">LoRA</span>, AlphaZero, contrastive learning, <span class="term" tabindex="0" data-tooltip="A system improves by generating its own training experience, usually by competing against versions of itself.">self-play</span>, actor-critic, etc. 

Each method seems to come with its own vocabulary, equations, architectures, implementation details, and mental model.

It is easy to get lost in the sauce.

But something interesting happens when you zoom out and see the field with a bird's eye view.

Across architectures, objectives, optimization strategies, and training methods, the same kinds of changes show up again and again. What looks like constant reinvention is often just **recombining a surprisingly small set of underlying ideas**.

Over time, I started noticing that many ideas in ML were not isolated inventions. They were different answers to recurring design questions:

* What distribution are we learning from?
* What structure should the model impose?
* What should be learned, and what should stay fixed?
* What signal should the system optimize?
* How should learning signals propagate?

This post is my attempt at describing that structure.

The goal isn't to explain every method in detail. There are much better resources for that at the moment. My goal is to provide a lens — a compact mental model that helps you:

* understand new papers faster
* see connections between seemingly unrelated methods
* reason about ML design decisions more clearly
* recognize recurring patterns across the field

And just to be clear: this is not the only way to think about ML. It's simply a framework that has helped me organize the field in my own head, and I think it may be useful to others too, especially those starting out learning about it.

## Table of Contents

- Table of Contents
{:toc}

---

## The Two-Layer View

At a high level, I think most machine learning systems can be decomposed into two layers:

**Layer 1: The Data (the problem)**

What distribution are you learning from?

**Layer 2: The Learning System (the solution)**

  Given that data, how do you learn from it?

Most discussions of ML focus almost entirely on Layer 2:

* architectures
* losses
* optimizers
* training algorithms

But a large fraction of actual progress in the field comes from changes to Layer 1 instead.

Sometimes the biggest breakthroughs aren't new models at all — they're **changes to the problem definition itself**.

So we'll start there.

---

## Layer 1: Data — The Problem Space

Before thinking about architectures or loss functions, it’s worth stepping back and asking a simpler question:

> What problem is the model actually solving?
{: .callout .callout-question}

In machine learning, that problem is ultimately defined by **data**.

More precisely:

> The data defines the <span class="term" tabindex="0" data-tooltip="The pattern of examples the model is exposed to. In practice, this often defines the actual problem more than the model architecture does."><strong>distribution</strong></span> the model is trying to learn.
{: .callout .callout-key}

Everything else — the model, the loss, the training algorithm — is just a way of learning a high-dimensional function that fits to that distribution.

This sounds obvious at first, but it's surprisingly easy to overlook. A lot of ML discourse implicitly treats the dataset as static background context while focusing on the learning algorithm itself. In practice, changing the <span class="term" tabindex="0" data-tooltip="The inputs, labels, contexts, and sampling process the model is trained or conditioned on. Change this, and you often change the task itself.">data distribution</span> often changes the problem **more fundamentally than changing the model**.

---

### Data is not just a dataset

It’s tempting to think of data as a static object:

* a dataset on disk
* a collection of labels
* a giant matrix of examples

But in modern ML, data is much richer than that.

It includes:

#### 1. Dataset composition

What examples are included?

* Are edge cases represented?
* Is the data balanced or heavily skewed?
* What regions of the real world are absent?
* What assumptions are implicitly encoded in the sampling process?

Two models with identical architectures can behave very differently simply because they were trained on different distributions.

A model trained mostly on internet text learns a different world model than one trained on scientific literature or code. The architecture may stay fixed while the learned behavior changes dramatically.

---

#### 2. Data generation process

Where does the data come from?

In classical supervised learning, the answer is simple: **humans collect and label examples.**

Modern ML systems are often much stranger than that.

Data may instead come from:

* interaction with an environment (reinforcement learning)
* self-play dynamics (AlphaZero)
* preference comparisons (RLHF)
* generation from other models
* systems or external memory

In many systems, the model is no longer just consuming data — it is participating in generating the distribution it learns from.

This creates feedback loops:

* the model changes the data
* the new data changes the model
* which changes future data again

Self-play systems are a particularly clean example of this dynamic.

---

#### 3. Data transformation

How is the data modified before learning?

Examples include:

* augmentation
* tokenization
* filtering
* corruption processes
* chunking and context construction

These transformations often redefine the learning problem itself.

<span class="term" tabindex="0" data-tooltip="Generative models that learn by corrupting data with noise and then learning how to reverse that process.">Image diffusion models</span> are a particularly interesting example.

The core generative modeling problem remains:

> learn a distribution over images.
{: .callout .callout-example}

But diffusion changes the form of the data the model sees during training:
* images are progressively corrupted with noise
* the model learns to reverse that corruption process


The breakthrough was not just architectural. It was partly a redesign of the data distribution itself.

One thing to note: foundation models made this aspect of ML unusually visible through prompting and in-context learning.

Few-shot examples, retrieved documents, chain-of-thought prompting, and system instructions all modify the conditioning context the model operates over. Even without changing parameters, these transformations can substantially alter model behavior.

In that sense, prompting is best understood not as changing the learning system itself, but as changing the local distribution the model conditions on at inference time.

---

#### 4. Data selection and weighting

Not all data points matter equally.

ML systems frequently decide:

* which examples to prioritize
* which to replay more often
* which to ignore
* and when certain examples should appear during training

Examples include:

* curriculum learning
* replay buffers
* importance sampling
* preference weighting in RLHF

These choices shape what the model ultimately learns.

Two systems trained on the same raw dataset can still learn very different behaviors depending on how the data is sampled and weighted over time.

---

### Many "Algorithmic" Breakthroughs Are Actually Data Changes

A useful shift in perspective is this:
> Many advances in ML are really changes to the data distribution disguised as algorithmic advances.
{: .callout .callout-key}

Many breakthroughs in ML are described as algorithmic:

* "This optimizer is better"
* "This architecture is more powerful"
* "This loss function works better"

But often, the real change is simpler:

> The data distribution changed.
{: .callout .callout-key}

Some examples:

#### RLHF

RLHF introduces human preference data and changes the problem from:

"predict likely text"

to:

"produce text humans prefer."

The underlying language model architecture may barely change at all.

#### AlphaZero

AlphaZero continuously generates stronger self-play trajectories as the policy improves.

The learning problem evolves dynamically during training because the data distribution itself evolves.

#### Diffusion Models

Diffusion models redefine generative modeling as denoising over progressively corrupted samples.

The architecture matters, but the corruption process is equally central to the method.

---

### Why this matters

Separating the problem space from the solution space turns out to be extremely useful.

It clarifies why:

* scaling data can outperform architectural innovation
* RLHF changed LLM behavior so dramatically
* synthetic data and self-play are so powerful
* prompting and in-context learning feel qualitatively different from fine-tuning

If you only look at Layer 2 (models and algorithms), you miss a large part of what’s actually driving progress.

A more complete view is:

> Data defines the problem.
> The learning system defines how you solve it.
{: .callout .callout-key}

Keeping this separation in mind makes it much easier to reason about:

* why certain methods work
* why others fail
* and what kinds of changes are likely to matter

With the problem defined by data, we can now look at the other half:

> Given a data distribution, how do we design a system that can learn from it?
{: .callout .callout-question}

That’s where the core primitives of machine learning come in.

---
## Layer 2: The Learning System — The Solution Space

Once the data defines the problem, the next question becomes:

> How do we design a system that can learn from that distribution effectively?
{: .callout .callout-question}

This is where most of machine learning research lives.

New architectures, new optimizers, new RL algorithms, new training tricks — they all operate within what I’ll call the **learning system**.

At first glance, the space feels enormous. Every year introduces:

* new architectures
* new training recipes
* new scaling strategies
* new RL methods
* new adaptation techniques

But once you zoom out, most of these methods can be decomposed into changes along a surprisingly small number of recurring axes.

I’ve found it useful to think of the learning system as composed of five core primitives:

1. **Representation**:
What structure/function bias should the model impose on the data?
2. **Parameterization**:
What model components are fixed vs learned?
3. **Objective**:
What signal is the system optimizing for?
4. **Constraints**:
What behaviors are encouraged or discouraged? (closely related to Objective)
5. **Credit Assignment**:
How does signal propagate in learning?

A compressed version of the framework looks like this:

| Primitive | Governs | Recurring Pattern |
|---|---|---|
| **Data** | problem definition | static → generated / selected / transformed |
| **Representation** | computational structure | local → global |
| **Parameterization** | what can adapt | fixed → learned |
| **Objective** | the learning signal | direct → surrogate / structured |
| **Constraints** | stability and allowed behavior | unconstrained → constrained |
| **Credit Assignment** | learnability | long, sparse paths → shorter, denser attribution paths |

These primitives are conceptually distinct, but in practice they are deeply coupled.

That coupling is one of the defining properties of ML systems.

A change in representation often changes optimization behavior.
A change in parameterization alters what constraints become necessary.
A change in objective reshapes what kinds of representations emerge.

Unlike traditional software systems, the components do not remain neatly isolated.

Still, even with that coupling, this decomposition turns out to be surprisingly useful.

The key shift is this:

> Most ML progress is not random innovation.  
> It is **systematic exploration of this design space**.
{: .callout .callout-key}

---

## 1. Representation

The first primitive is representation.

Representation answers the question:

> What kinds of structure does the model naturally express?
{: .callout .callout-question}

A useful way to think about representation is not just:

> What architecture is this?
{: .callout .callout-question}

but:

> What computational structure does this architecture make natural?
{: .callout .callout-question}

This is the part of ML most people think about first:
- MLPs
- CNNs
- RNNs
- Transformers
- Graph neural networks

Different architectures fundamentally compose to different mathematical functions that each impose a different bias on how it fits to the actual data.

For example:

- CNNs assume **local spatial structure**
- RNNs assume **sequential dependence**
- Transformers assume **relational interactions between arbitrary elements**

These assumptions are not just implementation details — they fundamentally shape what kinds of functions are easy or difficult for the model to learn.

In many cases, representation changes are changes in <span class="term" tabindex="0" data-tooltip="Who can talk to whom inside the computation. For example, attention makes distant tokens directly interact instead of passing information step by step."><strong>interaction topology</strong></span>: which parts of the input can communicate, **how directly they communicate**, and what patterns are cheap for the model to express.

---

### Representation as inductive bias

A useful way to think about representation is:

> Representation defines the model’s <span class="term" tabindex="0" data-tooltip="The kinds of patterns a model naturally prefers or finds easy to represent before seeing any particular dataset.">inductive bias</span>.
{: .callout .callout-key}

Or more concretely:

> What kinds of patterns are "cheap" for the model to represent?
{: .callout .callout-question}

CNNs make translation-invariant image features cheap.

Transformers make long-range interactions cheap.

RNNs make recursive temporal updates cheap.

This is why architecture changes can produce dramatic improvements even when everything else stays fixed.

---

### The Shift from Local to Global

One recurring pattern in ML representation is:

> Local interactions → global interactions
{: .callout .callout-pattern}

You can see this progression clearly:

- MLPs: weak structural assumptions
- CNNs: local receptive fields
- RNNs: temporal recurrence
- Transformers: fully connected relational reasoning

Attention was powerful not just because it was "more expressive," but because it changed the interaction topology of the model.

Instead of forcing information to propagate step-by-step through space or time, attention allows direct interaction between distant elements.

This dramatically improves:
- representation flexibility
- long-range reasoning
- optimization stability 
- long-range credit assignment

Notice something important here:

> A representation change often affects optimization implicitly.
{: .callout .callout-note}

This coupling shows up constantly in ML.

---

### Representation is not just architecture

It’s tempting to reduce representation to "what neural network are you using," but the concept is broader.

Representation also includes:
- positional encodings
- tokenization schemes
- latent spaces
- feature embeddings
- memory layouts
- iterative refinement structures

Even diffusion models can be partially understood as a representational shift:
> generation becomes a trajectory through noise space rather than a direct mapping.
{: .callout .callout-example}

Mixture-of-Experts models are another example:
> instead of representing computation as a single dense pathway, they represent it as sparse conditional routing through specialized subnetworks.
{: .callout .callout-example}


---

### Representation changes often require other changes

This is one reason ML abstractions feel "leaky" compared to traditional software abstractions.

Representation determines:

* what structure is easy to express
* what generalizations emerge naturally
* what optimization paths are available

And importantly:

> representation choices often force changes elsewhere in the system.
{: .callout .callout-key}

You often cannot change representation in isolation.

Transformers are a good example:
- Attention enabled global interactions
- But training deep attention stacks required:
  - residual connections
  - normalization
  - stable optimization techniques

Without those supporting changes, the representation would not scale effectively.

This is a recurring theme throughout the design space:

> Primitives are conceptually distinct, but operationally coupled.
{: .callout .callout-key}

---

## 2. Parameterization

If representation defines the structure of computation, <span class="term" tabindex="0" data-tooltip="The choice of what parts of the system are fixed and what parts are allowed to be learned from data.">parameterization</span> defines:

> What parts of that computation are fixed, and what parts are learned?
{: .callout .callout-question}

This is one of the deepest recurring patterns in modern ML.

A huge amount of progress can be summarized as:

> Replace **fixed computation** with **learned computation**.
{: .callout .callout-pattern}

---

### Fixed → learned

This pattern appears everywhere once you start looking for it.

Examples:
- fixed image features → learned features
- fixed alignment heuristics → learned attention
- fixed routing → learned routing (Mixture-of-Experts)
- fixed loss weighting → learned task weighting
- fixed normalization behavior → adaptive normalization

Many innovations that initially appear mathematically sophisticated are, at a high level, versions of the same move:

> Delegate more decisions to **optimization**.
{: .callout .callout-pattern}

If a useful heuristic can be expressed as parameters, ML systems tend to push it into the learned portion of the system.

---

### Attention as learned interaction

Self-attention is a particularly clean example.

Earlier sequence models often relied on:
- fixed receptive fields
- fixed recurrence structures
- manually constrained interaction patterns

Attention changes this into:
> learned interaction strengths between elements.
{: .callout .callout-key}

Instead of specifying which tokens should influence each other, the model learns relational structure dynamically from data.

That’s as much a parameterization shift as it is a representational one.

---

### LoRA and Constrained Adaptation

LoRA (Low-Rank Adaptation) provides another useful example.

LoRA does not fundamentally change the model architecture. Instead, it changes:
> **where learning is allowed to occur.**
{: .callout .callout-key}

Rather than updating the full weight matrices during fine-tuning, LoRA constrains updates to a low-rank subspace.

The representation stays mostly fixed.

The parameterization changes.

This single decision dramatically reduces:

* memory usage
* compute requirements
* adaptation cost

while preserving much of the model’s ability to specialize.

The insight was not primarily architectural — it was about rethinking what needed to be learned versus what could remain fixed.

---

### Learned normalization and adaptive computation

Normalization layers illustrate another interesting progression.

Originally, normalization was mostly a stabilization trick:
- BatchNorm
- LayerNorm

But over time, people started making parts of normalization adaptive or learnable:
- affine scaling parameters
- RMSNorm variants
- gating mechanisms
- adaptive residual scaling

This reflects a broader pattern:

> Replace static heuristics with dynamically learned parameters.
{: .callout .callout-pattern}

The system increasingly learns not just the solution, but aspects of the optimization process itself.

---

### Parameterization changes alter the function space

A subtle but important point:

Parameterization does not just change implementation details.

It changes:
- optimization geometry
- expressivity
- generalization behavior

Two systems may represent the same mathematical function class in theory, but behave very differently in practice because of parameterization.

This is one reason ML often feels different from classical software engineering:
> the way you parameterize a solution strongly affects whether gradient-based learning can actually find it.
{: .callout .callout-key}

---

### Why Parameterization Matters

Parameterization does not just affect implementation details.

It changes:

* optimization geometry
* gradient flow
* expressivity
* generalization behavior

Two systems can represent similar function classes in theory while behaving very differently in practice because of how they are parameterized.

This is one of the biggest differences between ML systems and classical software systems:

> the way you express a computation strongly affects whether gradient-based learning can actually discover it.
{: .callout .callout-key}

And more importantly, parameterization is deeply coupled to other primitives.

Parameterization interacts tightly with:

* representation
* constraints
* credit assignment

Opening more of a system to learning often increases flexibility, but also increases instability.

As more computation becomes learnable:

* constraints become more important
* optimization becomes harder
* regularization becomes necessary

Again:
> the primitives often move together.
{: .callout .callout-note}

---

## 3. Objective

Once you define a representation and parameterization, the next question is:

> What exactly is the model trying to optimize?
{: .callout .callout-question}

This is the objective.

Examples:
- cross-entropy
- reward maximization
- reconstruction loss
- contrastive learning
- denoising losses
- flow matching
- preferences 

At first glance, objectives seem straightforward:
> define the thing you want.
{: .callout .callout-key}

But in practice, a large fraction of ML progress comes from something subtler:

> Reshaping difficult problems into **objectives that are easier to optimize**.
{: .callout .callout-key}

---

### Direct objectives are often hard

The gap between:
> what you want
{: .callout .callout-question}

and:
> what you can optimize effectively
{: .callout .callout-question}

is where much of ML design lives.

Direct objectives are often:

* sparse
* noisy
* unstable
* non-differentiable
* high variance

So the field repeatedly develops <span class="term" tabindex="0" data-tooltip="A more trainable stand-in for the thing you actually want. The point is to preserve the spirit of the task while giving optimization a usable signal.">surrogate objectives</span> that preserve the spirit of the task while making optimization feasible.

### Diffusion Models as Objective Design

Diffusion models are a striking example.

The underlying problem is:
> generative modeling over images.
{: .callout .callout-example}

Directly maximizing likelihood over high-dimensional data is difficult.

Diffusion reframes the task entirely:
* progressively corrupt images with noise
* train the model to reverse that corruption

Instead of:

> "generate an image"
{: .callout .callout-example}

the model learns:

> "predict the noise added to an image."
{: .callout .callout-example}

The architecture changed somewhat and I'm sure will continue to change.

But the objective redesign centering around what to optimize was arguably the more fundamental breakthrough.

---

### Flow Matching as Objective Design

Flow matching provides another example of objective design in generative modeling.

Like diffusion, the underlying goal is still:

> learn a data distribution.
{: .callout .callout-example}

And like diffusion, flow matching avoids treating generation as a single global mapping from noise to data.

Instead, it turns generation into learning a trajectory between distributions.

The difference is the **local learning target**.

Diffusion models commonly train the model to predict the noise added at a particular timestep, or equivalently to predict a denoising direction.

Flow matching trains the model to predict the velocity field along a path from a simple source distribution to the target data distribution.

So the optimized objective becomes:

> predict how a sample should move at a point along the path between distributions.
{: .callout .callout-example}

That makes flow matching useful to view as a change along the **objective** primitive.

The architecture can vary.

The representation can vary.

The parameterization can vary.

But the defining design move is a different objective: the model is trained on **velocity prediction rather than denoising or noise prediction**.


---

### PPO and surrogate objectives

Reinforcement learning provides another example.

Vanilla policy gradients optimize expected reward directly.

In practice, this is unstable due to high variance.

PPO introduces a surrogate objective:
- advantage-weighted probability ratios
- clipping constraints
- optional KL penalties

The system is still optimizing for reward.

But the optimization surface becomes dramatically more stable.

Conceptually:
> the objective is reshaped into a form that is safer to optimize.
{: .callout .callout-key}

This pattern shows up constantly:
- surrogate losses
- auxiliary losses
- contrastive objectives
- self-supervised pretraining

Often the "real" goal and the optimized objective are not identical.

The optimized objective is chosen because it provides a learning signal engineered to produce useful gradients.

---

### Objectives shape emergent behavior

A model is trained to optimize what its objective incentivizes.

This sounds obvious, but it’s easy to underestimate how much behavior emerges from objective design.

Examples:
- entropy bonuses encourage exploration
- reconstruction losses encourage compression
- contrastive losses encourage separation in latent space
- autoregressive objectives encourage predictive world modeling

Even subtle objective changes can reshape:
- representations
- optimization dynamics
- emergent capabilities

---

### Objectives Interact with Everything Else
Objectives are inseparable from:

* representation
* constraints
* data

The same objective applied to different architectures can produce radically different behavior.

And unstable objectives often require:

* regularization
* trust regions
* clipping
* normalization

to become usable at scale.

The objective is not isolated from the rest of the system.

It is one part of a coupled learning process.

--- 

## 4. Constraints and Regularization

If objectives answer:
> "What should the model optimize?"
{: .callout .callout-question}

then <span class="term" tabindex="0" data-tooltip="Mechanisms that keep learning from going off the rails: clipping, normalization, trust regions, regularization, and similar stabilizers.">constraints</span> answer:
> "What should the model avoid doing?"
{: .callout .callout-question}

The boundary between objectives and constraints can be blurry.

A rough distinction is:

> objectives define what behavior the system is trying to produce.  
> constraints shape which optimization paths or solutions are **allowed, discouraged, or stabilized**.
{: .callout .callout-key}

In practice, many mechanisms do both.

Constraints shape the geometry of learning.

Examples:
- weight decay
- gradient clipping
- KL penalties
- entropy regularization
- trust regions

This primitive is often underestimated.

Constraints are frequently treated as engineering patches added after the "real" design work is complete.

In reality, they often do substantive work:

* shaping optimization geometry
* improving generalization
* stabilizing learning
* preserving useful behaviors

A large fraction of modern ML can be interpreted as:
> unconstrained optimization made stable through **constraints**.
{: .callout .callout-key}

---
### Unconstrained → Constrained

A recurring pattern across ML is:

> unconstrained optimization → constrained optimization
{: .callout .callout-pattern}

Early versions of many algorithms are theoretically valid but in practice are unstable.

Over time:

* constraints are introduced
* hard constraints become soft constraints
* approximate constraints emerge for efficiency

Reinforcement learning makes this progression particularly visible.

---

### PPO as constraint design

PPO is a particularly clean example.

Vanilla policy gradients allow large policy updates.

This creates instability:
- catastrophic policy collapse
- destructive updates
- noisy optimization trajectories

TRPO introduced an explicit <span class="term" tabindex="0" data-tooltip="A rule that prevents the policy from changing too much in one update, because big jumps can destroy learned behavior.">trust-region constraint</span> via a classic constrained optimization formulation, i.e. "maximize [objective] subject to [condition]", which PPO later approximated with clipping and softer KL penalties.

At a high level, the progression was:

- unconstrained optimization
- hard constraints
- soft approximate constraints

This pattern repeats many places in ML.

---
### Constraints Often Hide Inside Architectures

One reason this primitive is easy to miss is that constraints frequently become absorbed into architecture and implementation.

Examples include:

* residual connections
* normalization layers
* attention scaling
* gradient clipping

These do not always look like constraints in the mathematical sense, but they often serve similar purposes:

> preventing the system from entering unstable regions of behavior.
{: .callout .callout-key}

---

### Why Constraints Matter
Constraints are not just safeguards.

Constraints shape:

* optimization stability
* generalization
* robustness
* exploration behavior

Weight decay discourages overly sharp solutions.

Entropy bonuses prevent premature policy collapse.

KL penalties preserve behavioral proximity to prior models.

Normalization stabilizes activation dynamics.

Sometimes constraints are so important that they become architectural assumptions.

Residual connections, normalization layers, and attention scaling all partly function as constraint optimization.

Many algorithms that appear fundamentally different are actually:

> different ways of constraining learning dynamics.
{: .callout .callout-key}

and many "new algorithms" are really constraint changes.

This is one of the most compressive ways to interpret ML progress.

A surprising number of methods reduce to:
> changing what regions of behavior are allowed or encouraged.
{: .callout .callout-key}

This is especially visible in RL, but it appears across the field.

---

### Constraints Couple Back into Representation and Optimization

Constraints affect:

* what representations are stable
* what parameterizations are trainable
* what optimization trajectories are reachable

As models become:

* larger
* more adaptive
* more expressive

constraints become increasingly necessary.

--- 

## 5. Credit Assignment

<span class="term" tabindex="0" data-tooltip="The problem of figuring out which earlier choices, parameters, or actions deserve credit or blame for an outcome.">Credit assignment</span> answers one of the hardest questions in learning:

> Which parts of the system caused the outcome, and by how much?
{: .callout .callout-question}

Or more generally:

> How does information about success or failure propagate through a learning system?
{: .callout .callout-question}

This primitive is slightly different from the others.

Representation, parameterization, objectives, and constraints describe components or properties of the learning system itself:

* what computations are possible
* what is learned
* what behavior is incentivized
* what behavior is discouraged

Credit assignment describes something more global:

> whether useful learning signals can successfully **propagate through the system at all**.
{: .callout .callout-key}

In that sense, credit assignment is less a standalone module and more a property of the entire learning process.

Representation determines what computations are expressible.
Credit assignment determines which of those computations are actually **learnable**.

A model may be expressive enough to represent a useful solution in theory, but if learning signals cannot reliably reach the right parts of the system, gradient-based learning may never discover it in practice.

---

### Learning Signals Degrade with Complexity

Credit assignment becomes harder as systems become:

* deeper
* longer-range
* more recursive
* more temporally extended
* more compositionally structured

The difficulty can emerge across:

* space (deep neural networks)
* time (reinforcement learning)
* structure (graphs, reasoning chains, programs)

As complexity increases:

* gradients vanish or explode
* learning signals become noisy
* dependencies become difficult to attribute
* useful supervision becomes sparse

Much of modern ML can be interpreted as trying to preserve usable learning signals as systems scale.

---

### Optimization vs Credit Assignment

Optimization and credit assignment are closely related, but they are not identical.

Optimization answers:

> How are parameters updated?
{: .callout .callout-question}

Examples include:

* SGD
* Adam
* momentum
* learning rate schedules
* second-order methods

These define how the system moves through parameter space.

Credit assignment answers a different question:

> Does useful information reliably reach the parameters that need updating?
{: .callout .callout-question}

Backpropagation sits at the intersection of both:

* it propagates learning signals backward through computation graphs
* optimization algorithms then use those signals to update parameters

This distinction matters because many advances that appear optimization-related are actually:

> improvements in attribution structure.
{: .callout .callout-key}

---

### A Recurring Pattern: Shortening Attribution Paths

One recurring pattern across ML is:

> long, sparse, opaque attribution paths → **shorter, denser, more structured attribution paths**
{: .callout .callout-pattern}

A surprising number of breakthroughs become easier to understand through this lens.

Many advances are not just making systems more expressive.
They are making useful learning signals easier to attribute.

---

### Attention Improved Credit Assignment

Transformers are usually described as representational breakthroughs.

That’s true.

Attention fundamentally changed how information and gradients propagate through sequences.

RNNs force information to move sequentially through long chains of recurrent computation. Learning a dependency between distant tokens requires signals to survive hundreds or thousands of intermediate steps.

Attention dramatically shortens those paths.

A token can directly interact with another distant token without passing through a long recurrent chain.

This improved:

* long-range dependency learning
* gradient propagation
* optimization stability
* training scalability

Attention is primarily a representational mechanism.
But one reason it succeeded so dramatically is because it also improved the system’s credit assignment properties.

This is a good example of how the primitives interact:

> a representational change reshaped the learnability of the system.
{: .callout .callout-key}

---

### Reinforcement Learning Makes the Problem Explicit

Reinforcement learning exposes the credit assignment problem especially clearly.

An action may occur now.
The reward may arrive much later.

The system must determine:

> which actions deserved credit for future outcomes.
{: .callout .callout-question}

This is difficult even conceptually, and even harder in practice when rewards are:

* sparse
* delayed
* noisy

Many core RL techniques exist primarily to improve temporal attribution:

* temporal difference learning
* replay buffers
* baselines
* generalized advantage estimation
* Monte Carlo rollouts

Replay buffers are a useful example.

At one level, they are a data mechanism:

> storing and resampling experience.
{: .callout .callout-example}

But one reason they matter is that they improve the quality and stability of <span class="term" tabindex="0" data-tooltip="Credit assignment across time: deciding which past actions mattered when the reward or failure shows up later.">temporal credit assignment</span> by decorrelating trajectories and reusing informative experiences.

Again:

> the primitives are conceptually separable, but operationally entangled.
{: .callout .callout-key}

---

### Iterative Refinement and Intermediate Structure

Another recurring pattern across ML is:

> single-pass computation → iterative refinement
{: .callout .callout-pattern}

This appears in:

* residual networks
* diffusion models
* flow matching
* recurrent reasoning
* tree search systems
* chain-of-thought prompting
* actor-critic / policy improvement loops

The common thread is not that all of these systems iterate in the same way.

They do not.

The common thread is that they replace one difficult transformation with a sequence of smaller transformations, each of which provides more structure for learning, inference, or both.

This often improves credit assignment because:

* learning signals become denser
* intermediate states become more structured
* optimization trajectories become smoother

Diffusion models are a particularly clean example. Instead of generating an image in one step, the model iteratively denoises over many smaller steps. Each step receives a relatively local learning signal, making the optimization problem dramatically easier.

Flow matching can be understood similarly. Rather than learning generation as a single opaque jump from noise to data, the model learns a continuous transformation process. Each point along the path provides a more local learning problem: predict how the sample should move next.

This makes the generative task easier to supervise because the model receives structured intermediate targets along the trajectory.

One way to interpret chain-of-thought prompting is through the same lens:

> intermediate reasoning steps create more structured attribution pathways through the computation.
{: .callout .callout-key}

Rather than forcing the model to map:

> problem → answer
{: .callout .callout-pattern}

in one opaque jump, the reasoning process becomes decomposed into smaller intermediate stages.

In RL methods like Soft Actor-Critic, the refinement happens across the training loop itself.

The actor produces behavior.

The critic estimates which actions were valuable.

The actor is then updated using that feedback, and the next round of data comes from a changed policy.

This creates an iterative policy improvement process where credit assignment is not just a single backward pass, but an **ongoing loop between behavior, evaluation, and update**.

---

### Why Credit Assignment Matters

Credit assignment determines:

* what systems remain trainable at scale
* what dependencies can realistically be learned
* how efficiently behaviors emerge
* whether optimization remains stable

Many important advances in ML are not just about making systems more expressive.

They are about making useful learning signals easier to propagate through increasingly complex computations.

Residual connections, normalization layers, replay buffers, attention mechanisms, and iterative reasoning structures all improved the learnability of systems by improving attribution structure.

Importantly, these mechanisms do not "belong" exclusively to the credit assignment primitive.

Residual connections are architectural choices, but their impact is partly about credit assignment: they create shorter paths for information and gradients to move through deep systems.
Replay buffers are primarily data mechanisms.
Attention is primarily representational and parameterized interaction.

But all of them also reshape how effectively learning signals propagate through the system.

That is what makes credit assignment different from the other primitives:

> it is less a category of components and more a **cross-cutting property of learnability** throughout the entire design space.
{: .callout .callout-key}

---

## Conclusion: Reading ML as Design Space Movement

The main idea of this post is not that every ML method fits neatly into one category.

It usually does not.

Most important methods move along several axes at once. A new system might change the data distribution, introduce a new representation, alter the objective, add new constraints, and improve credit assignment all at the same time.

But that is exactly why the framework is useful.

Instead of asking:

> What is the trick?
{: .callout .callout-question}

you can ask:

> What changed in the design space?
{: .callout .callout-question}

Did the data distribution change?

Did the representation change?

Did the parameterization change?

Did the objective or constraint structure change?

Did credit assignment become easier?

Once you start asking those questions, new ML papers become easier to parse. The field starts to look less like a sequence of unrelated breakthroughs and more like systematic exploration of a shared design space.

That does not make the details unimportant.

The math still matters.

The architecture still matters.

The implementation still matters.

But the details become easier to understand when you can see what kind of move they represent.

The names and equations will keep changing.

But many advances in ML are still recognizable as recurring moves through the same design space, such as:

* making interactions more global
* making fixed heuristics learnable
* reshaping objectives into tractable learning signals
* stabilizing optimization through constraints
* improving how learning signals propagate through increasingly complex systems

That is the lens I have found most useful so far:

> data defines the problem,  
> learning systems define the solution,  
> and progress often comes from moving through a small set of recurring design primitives.
{: .callout .callout-key}
