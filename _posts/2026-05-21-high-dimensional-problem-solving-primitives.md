---
layout: post
title: "A Framework for High-Dimensional Problem Solving"
date: 2026-05-21 10:00:00 -0800
categories: general
image: /assets/images/blog/high-dim-problem-solving-framework.png
image_alt: "Minimal abstract title image for the high dimensional framework"
---

I have spent the last few years moving between robotics and EDA: two engineering worlds that should not feel similar, at first glance.

In robotics research, I worked on vision-and-language navigation, robot policy evaluation, imitation learning, diffusion-style policies, and multi-robot planning systems. The problems were physical and embodied: robots had to move through rooms, coordinate with each other, interpret language, avoid failures, and turn high-level goals into executable behavior.

More recently, as a machine learning engineer at Synopsys, I have been working on applying ML to chip design dealing with netlists, placement, routing, timing, quality-of-results data, differentiable optimization, learned circuit representations, and LLM-based agents for engineering tools.

Those two domains should not feel similar.

Robotics is about motion, geometry, dynamics, contact, sensors, actuators, uncertainty, and real-time decision-making. Chip design is about circuits, graphs, layouts, timing paths, physical constraints, manufacturability, and enormous combinatorial optimization problems. One field asks how a machine should act in the world. The other asks how computation should be physically arranged on silicon.

But the more time I spent in both, the more I kept having the same strange feeling: I was not learning robotics algorithms and chip-design algorithms as separate things — **I was learning recurring strategies for navigating enormous constrained spaces.**

The names changed. The objects changed. The tooling changed. But the underlying behaviors kept reappearing.

In robotics, many methods seemed to fall into a few recurring behaviors. Some **followed local signals or structure**: inverse kinematics, trajectory optimization, model predictive control. Some **expanded through reachable structure**: motion-planning trees, roadmaps, graph search. Others **sampled possibilities and kept pressure on the better ones**: stochastic trajectory optimization, evolution strategies, cross-entropy-style methods.

Then I started seeing the same behaviors in EDA. Analytical placement and timing optimization followed local structure. Routing graphs, maze routing, and rip-up-and-reroute expanded through reachable physical connectivity. Simulated annealing, randomized refinement, and other stochastic methods sampled possible layouts or transformations and biased the search toward better regions.

The domains were different, but the computational moves were the same.

At first, this looks like an analogy between two fields.

I think it is deeper than that.

This post is not fundamentally about robotics, EDA, SAT solving, dynamic programming, language models, or machine learning individually. It is about **a framework for the recurring strategies** that emerge whenever systems must navigate enormous constrained spaces.

The central claim is not that these domains are secretly the same. They are not. A robot arm, a chip layout, a Boolean formula, a dynamic program, and a generated text sequence have very different meanings.

The claim is more modest and more useful:

> Many complex problem-solving systems repeatedly rediscover the same computational components, proposal behaviors, memory structures, and other problem-solving primitive strategies.

Robotics and chip design are the main case studies because they are the places where I encountered this pattern most directly. SAT solvers, dynamic programming, and language models will appear later as stress tests of the framework.

**Note**: I used AI while writing this, because it is 2026 and refusing good tools is not a personality trait. The ideas, structure, edits, and final judgment are mine; AI helped me explore, pressure-test, and sharpen the writing.


## Table of Contents

- Table of Contents
{:toc}

---

## The Argument in One Page

The post moves through five levels to build a framework for high-dimensional problem solving.

First, robotics and chip design look strangely similar despite having different objects, tools, and vocabularies.

Second, those similarities become clearer when both fields are viewed as searches through enormous constrained spaces.

Third, many algorithms become instances of a smaller set of **proposal dynamics**: **follow local structure**, **expand reachability**, and **sample possibilities**.

Fourth, those proposal dynamics sit inside a larger framework that includes **representation**, **evaluation**, **memory**, **relaxation**, **decomposition**, **amortization**, and **hybridization**.

The scope is important: this framework is for systems that must navigate large constrained possibility spaces where exhaustive enumeration or direct closed-form computation is infeasible. It is not a theory of all computation, all intelligence, or all engineering.

Within that scope, the framework can be stress-tested beyond robotics and chips using SAT solvers, dynamic programming, graph search, Monte Carlo tree search, and language models.

The organized version of the framework looks like this:

* **Problem definition**: representation and evaluation.
* **Search / proposal dynamics**: follow, expand, and sample.
* **Persistence**: memory and amortization.
* **Complexity management**: relaxation and decomposition.
* **Composition**: hybridization.

Many things that initially look like separate algorithmic categories are better understood as interactions between these layers. Heuristics, dynamic programming, learned priors, deep learning, etc. are not all independent primitives. They emerge from how systems represent problems, propose moves, remember structure, decompose complexity, and reuse work across instances.

This describes the regime where many possibilities exist, validity matters, objectives compete, evaluation is costly, and useful structure has to be preserved across time.

---

## Spaces Instead of Domains

The first conceptual shift is to stop thinking in terms of **domains** and start thinking in terms of **spaces**.

A robot trajectory is a point in a space of possible trajectories.

A grasp is a point in a space of possible grasps.

A multi-robot task allocation is a point in a space of possible assignments, schedules, and execution plans.

A chip placement is a point in a space of possible layouts.

A routing topology is a point in a space of possible physical connections.

A SAT assignment is a point in a Boolean assignment space.

A dynamic-programming subproblem is a point in a decomposed state space.

A generated sentence is a trajectory through a combinatorial sequence space.

This framing does not erase domain knowledge. Domain knowledge is still everything. A robot is not a chip, a timing path is not a manipulator arm, and a routing guide is not a proof search. But the space-based view lets us ask a more general question:

> What does a system need in order to move intelligently through a space too large to enumerate?

At minimum, it needs a few things.

It needs a **representation** of candidate solutions.

It needs an **evaluation mechanism** that distinguishes valid from invalid and better from worse.

It needs **proposal dynamics**: ways of generating or modifying candidates.

It needs **memory** so that useful work persists within a solve.

It often needs **relaxation**, because the exact problem is too discrete, discontinuous, or expensive to optimize directly.

It often needs **decomposition**, because the full problem is too large to solve monolithically.

And increasingly, it uses **amortization**: memory whose usefulness persists across problem instances rather than only within a single solve.

The mistake is to treat individual algorithms as isolated inventions.

RRTs, gradient descent, SAT solvers, dynamic programming, transformers, simulated annealing, and model predictive controllers are not just separate techniques scattered across fields. They are combinations of recurring components.

**Proposal dynamics are not the whole system.** They are movement behaviors operating inside larger systems.

**Amortization is cross-instance memory** in this picture. A cached DP table, a learned clause database, a trained neural network, and a reusable roadmap are different mechanisms, but they all answer a similar question: how can work from the past make the next solve cheaper?

**Hybridization is different.** It is not another primitive. It is what happens when these pieces are composed into a working system.

That distinction keeps the framework from turning into a list of algorithm names. The article is not trying to classify every method into one bucket. It is trying to identify the roles that methods play inside larger problem-solving systems.

---

## What This Framework Is Not About

The boundary matters.

This framework is not trying to describe every computation. Some systems do not need to navigate a large possibility space at all.

Matrix multiplication, FFTs, modular arithmetic, simple hash-table lookup, deterministic finite-state protocols, and straightforward regex execution are not natural examples of this framework. They may be important computations, but their execution path is largely direct, predetermined, or addressed by structure. There is no meaningful proposal dynamic, no broad exploration, and no search pressure in the sense this post cares about.

The same distinction applies inside a domain. Regex synthesis may involve search. Regex execution usually does not. Theorem proving may involve search. A deterministic symbolic rewrite pass may not. Simulating a known ODE forward in time may involve state evolution, but not necessarily problem solving through a possibility space.

The counterexamples are useful because they reveal the real scope:

> This framework describes systems under **search pressure**: many possibilities, hard constraints, expensive evaluation, limited compute, and no direct closed-form route to the answer.


When enough exploitable structure exists, search can collapse into direct computation. Linear algebra is often easier than SAT not because the objects are smaller, but because the structure is stronger. Gaussian elimination, FFTs, sorting networks, and some convex optimization problems show the opposite regime: the problem may be large, but the path through it is structured enough that broad exploration becomes unnecessary.

That is the boundary. This framework is about the regime where structure is useful but incomplete, so systems must navigate.

---

## Two Fields, One Problem Shape

Imagine planning a motion for a mobile manipulator.

The robot begins in one state and needs to accomplish a goal: pick up an object, navigate to a room, hand something to a person, open a drawer, or coordinate with another robot. It has joints with limits, wheels with constraints, sensors with noise, policies that may be uncertain, a map that may be incomplete, and a world that may change while it is acting.

Every possible behavior is a candidate solution.

Most candidates are useless. Some collide with the environment. Some violate joint limits. Some are dynamically infeasible. Some reach the object but with a bad grasp. Some succeed in simulation but fail on the real robot. Some complete the task but take too long, consume too much energy, or create an unsafe motion.

Now imagine designing a chip.

The system begins with a logical description of computation and needs to turn it into a physical implementation. Logic has to be mapped, placed, routed, timed, optimized, and checked. The design has to satisfy design rules, timing constraints, power budgets, area constraints, routability constraints, manufacturing constraints, and product-level quality goals.

Every possible physical implementation is also a candidate solution.

Most candidates are useless. Some violate design rules. Some cannot be routed. Some have terrible timing. Some waste area. Some create congestion hotspots. Some look good under an early proxy metric but fail downstream. Some satisfy one objective only by damaging another.

The domains are different, but the **problem shape** is similar:

> There is an enormous space of possible solutions. Most of it is invalid or bad. The system has to find a small region that is valid enough, good enough, and reachable with the computational budget available.

This is why the same computational behaviors keep returning. When a problem has the same shape, it creates similar pressure on the methods used to solve it.

The pressure is not caused by robotics specifically. It is not caused by chip design specifically. It is caused by high-dimensional constrained search.

---

## A Concrete Walk Through the Framework

Before going layer by layer, it helps to see the whole framework on two concrete problems.

Suppose a robot needs to pick up an object from a cluttered table and place it on a shelf.

The framework appears immediately:

* Representation: RGB-D observations, object detections, a map of free space, the robot's joint state, a candidate grasp pose, and a trajectory parameterization.
* Evaluation: collision checks, grasp reachability, object stability, joint limits, torque limits, task success, and safety.
* Proposal dynamics: sampled grasps, inverse kinematics, trajectory optimization, local replanning, graph search, or a learned policy that proposes an action chunk.
* Memory: a search tree, a cached map, a learned policy, a database of successful grasps, or the current belief about the scene.
* Relaxation: smoothed collision costs, simplified dynamics, approximate contact models, or continuous trajectory parameters.
* Decomposition: perception, grasp selection, motion planning, control, monitoring, and recovery.
* Amortization: learned grasp proposals or action distributions trained from previous experience.

Now suppose an EDA tool needs to produce a better physical implementation of part of a chip.

The same pattern appears again:

* Representation: netlists, cell features, net connectivity, timing paths, placement coordinates, density maps, routing resources, and quality-of-results metrics.
* Evaluation: legality, timing, congestion, wirelength, power, area, and downstream tool behavior.
* Proposal dynamics: cell moves, differentiable placement updates, buffering changes, routing decisions, randomized perturbations, or learned predictions about which regions deserve attention.
* Memory: the current design state, optimization history, timing graphs, congestion maps, learned embeddings, or model parameters trained across previous designs.
* Relaxation: continuous placement objectives, differentiable wirelength approximations, softened density constraints, or estimated congestion.
* Decomposition: synthesis, floorplanning, placement, routing, timing analysis, signoff, and repair loops.
* Amortization: learned models that use prior design data to guide future optimization.

These are not the same engineering problem.

But the checklist is eerily similar:

* What is the candidate?
* How do we know if it is legal?
* How do we know if it is good?
* How do we generate the next candidate?
* What information survives from one attempt to the next?
* What approximation are we relying on?
* How is the full problem broken into stages?
* What previous experience is being reused?

That checklist is **the framework**.

---

## Representation: How Problems Become Searchable

**Representation is the first layer** because it determines what kind of search is even possible.

The same underlying problem can become easy, hard, smooth, jagged, local, global, sparse, dense, differentiable, combinatorial, or learnable depending on how it is represented.

In robotics, a motion can be represented as a sequence of joint configurations, a continuous trajectory parameterized by splines, a path through an occupancy grid, a graph over sampled configurations, a policy mapping observations to actions, a sequence of symbolic skills, or a distribution over future action chunks.

In chip design, a circuit can be represented as a netlist, a hypergraph of cells and nets, a placement on a continuous or discrete canvas, a routing grid, a timing graph, a hierarchy of modules, a collection of quality-of-results features, or a learned embedding over circuit structure.

In symbolic and combinatorial systems, the representations look different again: CNF formulas, syntax trees, proof states, dynamic-programming tables, token sequences, game states, or search trees.

The representation determines **what is visible**.

A netlist emphasizes connectivity. A placement emphasizes geometry. A routing grid emphasizes physical resources. A timing graph emphasizes paths and delays. A CNF formula emphasizes logical clauses and variable assignments. A token sequence emphasizes prefix-conditioned continuation. A DP table emphasizes subproblem identity and dependency structure.

Representation also defines **neighborhood**.

That may be the most important point.

Most search procedures need some notion of "nearby." A local optimizer needs nearby candidates. A graph search needs neighboring nodes. A sampler needs a distribution that places probability mass around some regions rather than others. A learned model needs input features or tokens that make useful regularities visible.

But **"nearby" is not an objective fact**. It is created by the representation.

Two robot trajectories may be close in joint space but far apart in task outcome. Two chip placements may have similar coordinates but very different timing behavior. Two SAT assignments may differ by one bit but trigger very different propagation behavior. Two token sequences may share a long prefix but diverge semantically.

If the representation gives the wrong notion of neighborhood, the search will make the wrong moves look natural.

This is why representation is not a preprocessing detail. **It is part of the algorithm.**

Many breakthroughs are **representational breakthroughs disguised as optimization breakthroughs**.

In robotics, the difference between planning directly in raw pixels and planning over objects, maps, contact modes, or skills is enormous. In chip design, the difference between treating a design as an unstructured bag of features and treating it as a graph with hierarchy, geometry, and timing structure is enormous. In language models, the decision to represent text as tokens and train over next-token prediction turns language generation into navigation through a sequence space.

Representation changes **locality, branching, smoothness, tractability**, and what can be cached, learned, searched, relaxed, and decomposed.

---

## Evaluation: Constraints Filter, Objectives Rank

Once a system can represent candidates, it needs to evaluate them.

Evaluation has two parts that are easy to blur together:

1. Is this candidate valid?
2. If it is valid, how good is it?

The first question is about constraints. The second is about objectives.

**Constraints filter. Objectives rank.**

In robotics, constraints include collision avoidance, joint limits, torque limits, stability, reachability, contact feasibility, timing, communication limits, and safety requirements. A trajectory that puts a robot arm through a table is not a low-scoring solution. It is invalid.

In chip design, constraints include design-rule correctness, timing closure, routability, voltage and power limits, manufacturing rules, clocking constraints, and physical legality. A placement that cannot route is not merely ugly. It breaks the pipeline.

In SAT, the constraint is literal: a complete assignment either satisfies the formula or it does not. In language generation, constraints may be softer or more contextual: syntax, formatting, tool-call schemas, factual consistency, or instruction following. In dynamic programming, constraints are often baked into the recurrence: which subproblems exist, which transitions are allowed, and what base cases are valid.

Objectives rank candidates inside the feasible region.

In robotics, objectives might include smoothness, speed, energy efficiency, robustness, task success, comfort, information gain, or coordination quality. In chip design, objectives might include wirelength, area, power, timing slack, congestion, thermal behavior, and downstream quality-of-results. In language generation, objectives might include likelihood, helpfulness, correctness, style, coherence, or tool success.

The hard part is that constraints and objectives are coupled.

A smoother robot trajectory may move too close to an obstacle. A faster trajectory may require more torque. In chip design, reducing wirelength may create congestion. Improving timing may increase area or power. In language generation, a fluent answer may be wrong, while a correct answer may require longer reasoning or tool use.

Real search spaces are not single landscapes. They are **several landscapes laid on top of each other**, with cliffs where hard constraints live and slopes where softer objectives live. A move can be downhill for one metric and uphill for another. It can improve a local proxy while damaging global feasibility.

This is where high-dimensional problem solving becomes more than "optimize a loss."

Real systems have webs of validity checks, proxy metrics, downstream consequences, and tradeoffs. Some are differentiable. Some are discrete. Some are expensive. Some are only known after another tool, verifier, simulator, compiler, or physical experiment runs.

That matters because every proposal method is only as good as the evaluation signal it receives.

If the evaluation is too weak, the system optimizes the wrong thing.

If the evaluation is too expensive, search becomes slow.

If the evaluation arrives too late in the pipeline, early stages make decisions without enough feedback.

If the evaluation is only a proxy, the system may learn to exploit the proxy instead of solving the real problem.

There is also a practical distinction between **scoring, verification, and repair**.

Scoring tells the system which candidate looks better according to some metric. Verification tells the system whether the candidate truly satisfies the rules that matter. Repair tries to turn a nearly valid candidate into a valid one.

A robot planner may score trajectories by smoothness, verify collision-freedom with a geometric checker, and repair a failed plan by replanning around an obstacle. A chip design tool may score placements by estimated wirelength or congestion, verify legality and timing with specialized engines, and repair violations through legalization, buffering, resizing, rerouting, or incremental optimization. A SAT solver may branch into a partial assignment, propagate implications, detect a conflict, and learn a clause that prevents returning to the same bad region.

A **score** is not a guarantee.

A **proxy** is not a verifier.

A **repair step** is not free.

Strong systems know which role each component is playing.

---

## Proposal Dynamics: How Systems Move Through Spaces

Once a system has representation and evaluation, it needs ways to propose candidates.

This is where many familiar algorithms live.

At a high level, I think many methods are built from **three recurring proposal dynamics**:

* follow
* expand
* sample

These are not the only kinds of algorithms. They are not mutually exclusive. Real systems mix them constantly. But they describe recurring ways systems traverse configuration spaces.

Learning can influence all three proposal dynamics. It can propose candidates, rank candidates, warm-start local refinement, bias sampling distributions, or decide where expansion should focus. I will treat it later under persistence, because learning's deeper role in this framework is to store useful structure from previous optimization so future search becomes cheaper.

The proposal dynamics are **the movement behaviors**. Learning changes how those movements are guided.

The key distinction is:

> **Follow improves known regions locally. Expand discovers previously unreached regions. Sample tests multiple possibilities without committing too early.**


### Follow

To **follow** is to use local structure to propagate improvement.

The simplest version is gradient descent: from where I am now, what nearby change improves the objective?

But **`Follow` is broader than gradients**.

It includes local iterative refinement, local propagation, value updates, message passing, unit propagation, constraint propagation, and other procedures where useful information moves through nearby structure.

In robotics, this appears in inverse kinematics, trajectory optimization, model predictive control, local planners, and many forms of optimal control. A robot may not know the global structure of the entire solution space, but it can estimate how a small change in joint angles changes end-effector position, how a small change in control affects future state, or how a small change in trajectory affects a cost function.

Model predictive control is a particularly clean example. The system repeatedly solves a local optimization problem over a moving horizon, executes the first part of the plan, observes what actually happened, and solves again. It does not need a perfect global plan. It needs a **locally useful model**, a **cost function**, **constraints**, and a fast enough loop to keep correcting itself.

In chip design, this appears in analytical placement, differentiable wirelength approximations, timing optimization, continuous relaxations, and gradient-like refinement of layout decisions. A discrete placement problem may be too combinatorial to solve directly, so the system softens it into something locally navigable.

Analytical placement has the same flavor. A brutally discrete layout problem is softened into a continuous one where cells can move under differentiable proxies for wirelength, density, congestion, or timing pressure. The common intuition of treating nets as **Hooke's-law springs** is useful here, as are **electrostatic density forces** in modern placers. The exact physical problem is not actually a spring system or an electrostatic system, but the relaxation creates forces that make local improvement possible.

In dynamic programming, Bellman updates also have a `Follow` flavor. They propagate local value improvements through a dependency structure. In SAT solving, unit propagation follows logical implications from partial assignments. In graph algorithms, relaxation steps propagate improved distances along edges.

The key idea is:

> Follow is local propagation of useful information through structure.

This is powerful when **locality is meaningful**. A sequence of local improvements can produce excellent global behavior when the representation and evaluation signal are aligned.

But the failure mode is clear: **local structure can lie**.

The slope may point toward a local minimum. A smooth approximation may hide a discrete cliff. A trajectory may look locally good but be globally trapped. A placement may improve wirelength while creating congestion that only appears later. A logical propagation step may be correct locally but embedded in a branch that is globally doomed.

Follow methods refine, correct, and propagate.

They do not, by themselves, explore an enormous space.

### Expand

To **expand** is to build connectivity through reachable regions.

The system asks a different question:

> What is reachable from what I already know?

This is the world of trees, graphs, branches, frontiers, roadmaps, routing grids, search states, and proof branches.

In robotics, rapidly-exploring random trees grow outward through configuration space. Probabilistic roadmaps sample feasible configurations and connect them into reusable graphs. Graph search methods discretize the world into nodes and edges, then search for paths. These methods care deeply about feasibility: collision-free motion, connected regions, narrow passages, and reachability.

In chip design, routing has an analogous flavor. Maze routing explores possible wire paths. Routing graphs encode physical connectivity. Global routing reasons about coarse resource allocation, while detailed routing turns those coarse plans into legal wires. Rip-up-and-reroute methods revise connectivity when conflicts appear.

In SAT solving, branching search expands a tree of partial assignments. In theorem proving, the system expands possible proof states. In planning, state-space search expands possible action sequences.

Expansion methods are not primarily asking what is best at first. They are asking **what can be connected to what**.

Sometimes **feasibility is the hard part**. If the feasible region is fragmented, narrow, or hidden, gradient-like improvement may be useless. You need to discover a path before you can optimize it.

The failure mode is also clear: coverage explodes.

A graph that is manageable in two dimensions becomes huge in twenty. A search tree that works in a small puzzle may become impossible in a large proof. A routing problem becomes difficult when millions of connections compete for limited physical channels. A planner can drown in its branching factor.

Expand methods accumulate reachability, but reachability can be expensive to map.

### Sample

To **sample** is to generate possibilities probabilistically and bias future search toward promising regions.

The system does not need a smooth gradient or a complete map. It needs a way to create variation and a way to score the results.

This is the world of stochastic optimization, evolution strategies, simulated annealing, random shooting, population methods, Monte Carlo tree search, randomized SAT solving, probabilistic decoding, and the cross-entropy method.

In robotics, a planner might sample many action sequences, roll them out, score them, and update its sampling distribution toward the best-performing ones. Evolution strategies can perturb policies or trajectories. Stochastic trajectory optimization can explore around a nominal plan.

In chip design, simulated annealing and randomized refinement have a long history. A layout can be perturbed, accepted, rejected, cooled, mutated, or recombined. Randomness helps the system escape the brittleness of purely local moves.

In game playing, Monte Carlo methods sample possible futures. In language models, probabilistic decoding samples continuations from a learned distribution. In SAT, randomized restarts and variable choices can help escape unlucky parts of the search tree.

Sampling is appealing because it can work when the objective is rough, black-box, discontinuous, or hard to differentiate. It can jump. It can maintain multiple hypotheses. It can discover regions that local methods might never reach.

But sampling always faces the **exploration-exploitation tradeoff**.

Explore too broadly and you waste compute. Exploit too quickly and you collapse onto a mediocre region. Keep too much randomness and progress is slow. Remove randomness too early and the method becomes brittle.

The cross-entropy method is a useful mental model. It maintains a distribution, samples candidates, selects elites, and updates the distribution toward them.

Informally:

> CEM finds a promising hill and zooms in.

That is both the strength and the danger.

If the hill is good, CEM improves quickly. If the hill is merely the first decent thing it found, the distribution may **collapse too early**.

The failure mode is premature convergence.

---

## Continuous and Combinatorial Spaces

The `follow / expand / sample` framing is easiest to see in continuous optimization, but it is not limited to continuous spaces.

Continuous spaces have **local geometry**. Small moves often mean something. Gradients, Jacobians, linearizations, smooth costs, and local approximations can be useful.

Trajectory optimization and placement relaxation live partly in this world.

Combinatorial spaces are different. They have **branching, weak locality, discrete transitions, and compositional structure**. A single bit flip in a SAT assignment, a single token in a generated sequence, or a single routing decision can have nonlocal consequences.

At first, symbolic systems can feel fundamentally different from robotics and EDA optimization.

But the same proposal dynamics still appear.

Unit propagation follows implications.

Branching expands a search tree.

Randomized restarts sample different regions.

Dynamic programming follows local recurrences through decomposed subproblems.

Language models sample, rank, and revise trajectories through sequence space.

What changes is not necessarily the underlying movement behavior. What changes is the **representation geometry**: locality, branching structure, constraints, and memory.

This is why I do not think "construction" needs to be a separate primitive. Autoregressive generation, proof construction, route construction, and plan construction can all be viewed as navigation through compositional spaces. The system is still following, expanding, sampling, remembering, and evaluating.

The constructed object is **the path through the space**.

---

## Stress Testing the Framework

If the framework only worked for robotics and EDA, it would be a useful analogy. The more interesting question is whether it survives contact with systems that look very different.

Here are a few quick stress tests.

### Dynamic Programming

Dynamic programming is useful because it initially seems hard to place in the framework.

It is not primarily exploration in the RRT sense. It is not stochastic sampling. It is not simply gradient-like optimization. It is dominated by decomposition and reuse.

That is exactly why it is helpful.

Dynamic programming shows that **reuse does not need to be its own primitive**.

Reuse emerges from the combination of **decomposition, memory, and local propagation**.

A dynamic program breaks a large problem into subproblems. It stores the answers to those subproblems. Then it propagates useful information through a recurrence.

Bellman-Ford is a clean example. The algorithm repeatedly relaxes edges, propagating improved distance estimates through a graph. That is not gradient descent, but it is a form of `Follow`: local value propagation through structure.

The **DP table is memory**. The **recurrence is decomposition**. The **update is local propagation**.

Together, they create reuse.

### SAT Solvers

SAT solvers are another powerful stress test.

A modern SAT solver combines several framework components:

* Expand: branching search over partial assignments.
* Follow: unit propagation and implication propagation.
* Memory: learned clauses that prevent returning to previously discovered conflicts.
* Evaluation: satisfiability of clauses under partial or complete assignments.
* Decomposition: implicit factorization through clauses and variable structure.
* Sampling or randomness: restarts and heuristic variation in some solvers.

This is one of the strongest validations of the framework because SAT solving is far from robotics and chip placement on the surface. Yet the same pattern still appears.

The solver searches a huge constrained space. It expands possible assignments, follows logical implications, remembers conflicts, and uses that memory to prune future search.

### Breadth-First Search

Breadth-first search is a deliberately simple stress test.

It is mostly `Expand`: maintain a frontier, visit reachable states layer by layer, and remember what has already been seen. Its power comes from complete coverage under a simple representation. Its weakness is also obvious: if the branching factor is large, the frontier explodes.

That makes BFS a clean example of the framework's diagnostic value. The proposal dynamic is easy to name, the memory structure is simple, and the failure mode follows directly from the assumptions.

### Bellman-Ford

Bellman-Ford looks different from BFS because it is not primarily discovering new states. It repeatedly propagates better distance estimates through known graph structure.

That makes it a `Follow` method in the broader sense: local value propagation. The graph is the representation, edge relaxation is the proposal/update rule, the distance table is memory, and convergence depends on repeated local improvements becoming globally consistent.

### Monte Carlo Tree Search

Monte Carlo tree search is a hybrid stress test.

It expands a search tree, samples rollouts, evaluates outcomes, and remembers statistics on visited nodes. In learned systems like AlphaZero-style agents, a model also supplies priors and value estimates. That makes MCTS a compact example of `Expand`, `Sample`, `Evaluation`, `Memory`, and `Amortization` working together.

### Language Models

Language models stress-test the same question from another direction.

At inference time, an LLM is moving through a sequence space one token, tool call, or generated action at a time. The **next-token distribution** is a proposal mechanism learned from training. Sampling changes how broadly the model explores possible continuations. The **context window** is short-term memory. The **trained weights** are long-term amortized memory. Tool calls expand the system beyond pure sequence generation into external state. Tests, retrieval, execution results, and human feedback provide evaluation signals.

An LLM is not a SAT solver or a dynamic program. The point is not to collapse those systems into one category. The point is that the framework's questions still help. What proposes the next move? What evaluates it? What memory is being used? What computation was amortized into parameters? What external tools or checks make the output reliable?

The model proposes. The context remembers. Tools evaluate. Sampling explores. Training amortizes. The system becomes more capable when these pieces are composed carefully rather than treated as one monolithic intelligence.

Across these stress tests, reuse is not a primitive.

Reuse emerges when **memory is connected to decomposition and local propagation**.

Caching, learned clauses, DP tables, memoization, replay buffers, learned weights, route guides, maps, and search trees are all ways of making previous computation matter.

The central question is not just **"how does the system move?"**

It is also:

> What survives after the move?

---

## Memory: What Different Systems Accumulate

Proposal dynamics describe **how a method moves**. Memory describes **what it keeps**.

This distinction is subtle but important.

Two methods can both improve candidates over time while remembering very different things. And what a method remembers determines what kind of progress can compound.

Gradient descent remembers a current point, plus optimizer state such as momentum.

An RRT remembers a tree. Its progress is not just the current endpoint; it is the explored connectivity structure.

A probabilistic roadmap remembers a graph. That graph can be reused across queries if the environment or configuration space remains relevant.

The cross-entropy method remembers a distribution. Its knowledge is not a single candidate, but a belief over where good candidates may live.

A SAT solver remembers learned clauses.

A dynamic program remembers subproblem solutions.

A language model remembers training experience in parameters and immediate context in its prompt or KV cache.

This gives another way to compare systems:

| System | Proposal behavior | Memory structure |
|---|---|---|
| Gradient descent | Follow | Current point and optimizer state |
| Trajectory optimization | Follow | Refined trajectory |
| RRT | Expand | Search tree |
| Probabilistic roadmap | Expand | Connectivity graph |
| CEM | Sample | Distribution over candidates |
| Simulated annealing | Sample | Candidate and temperature |
| SAT solver | Expand + Follow | Clause database |
| Dynamic programming | Follow + Decompose | Cached subproblems |
| Learned policy | Amortized guidance | Parameters |
| LLM | Amortized guidance + Sample | Parameters + context |

**Memory is what prevents computation from being wasted.**

If a method remembers only the current point, it can refine efficiently but may lose diversity. If it remembers a graph, it can reuse reachability. If it remembers a distribution, it can shift probability mass toward promising regions. If it remembers clauses, it can avoid repeated contradictions. If it remembers a DP table, it can avoid recomputing subproblems. If it remembers a model, it can transfer experience across instances.

The table is useful because **it makes predictions**.

If a system keeps failing in the same way, ask **what it is failing to remember**. A local optimizer that keeps rediscovering the same bad basin may need population memory or restart structure. A planner that repeatedly explores the same infeasible corridor may need a better map, constraint cache, or learned cost. A SAT solver without learned clauses wastes work by revisiting conflicts. A robot policy that forgets uncertainty may act confidently outside its training distribution.

The table also suggests hybrids.

If `Expand` gives you reachability but not prioritization, add learned guidance or sampling. If `Sample` gives you diversity but not legality, add a verifier or repair step. If `Follow` gives you refinement but needs a good initialization, add amortized warm starts. If learned parameters give you fast guesses but weak guarantees, wrap them in classical checks.

When a system is hard to place in the table, that is often a clue rather than a failure of the framework. It may mean the system is using several memory structures at once, or that the important memory is hidden in data, tooling, prompts, caches, replay buffers, or human workflow rather than in the algorithm's name.

A language agent is a good example. If you only look at the LLM, you might say the memory is just parameters and context. But a working agent often also has retrieved documents, tool outputs, test results, edit history, shell state, user feedback, and sometimes long-term project conventions. The "memory" is distributed across the model, the prompt, external tools, and the surrounding workflow. Difficulty placing the system in one row tells you something real: the system's capability comes from several persistence mechanisms layered together.

This is one reason hybrid systems are so powerful: they combine different kinds of memory.

A learned model may remember experience across many previous problems. A planner may remember local reachability for the current problem. An optimizer may remember local improvement direction. A verifier may remember hard rules. A solver may remember conflicts. Together, they form a richer problem-solving system than any one method alone.

---

## Relaxation: Making Hard Problems Navigable

Many real problems are discrete, combinatorial, non-convex, non-differentiable, or all of the above.

Yet many of our best tools want smoothness.

They want gradients. They want continuity. They want local geometry. They want a search space where small changes produce somewhat predictable effects.

**Relaxation is the art of turning a hard problem into a softer one.**

This is one of the most important hidden moves in engineering.

In robotics, we linearize dynamics. We smooth collision costs. We approximate contact. We optimize trajectories with continuous parameters even when the actual task involves discrete events. We plan over simplified models before executing in the real world. We replace a hard feasibility problem with a penalty that can be optimized.

In chip design, relaxation is everywhere. Placement begins as a brutally discrete problem: cells ultimately need legal physical locations. But analytical placers often work with continuous approximations first. Wirelength is approximated by differentiable functions. Density constraints are softened. Congestion is estimated before detailed routing. Timing costs may be represented through proxies before exact signoff.

Even symbolic systems sometimes relax hard discreteness. Soft logic, differentiable SAT approximations, neural theorem-proving heuristics, and learned value functions all try to make brittle combinatorial spaces more navigable.

The pattern is:

> Solve the problem you can optimize, then repair or project back toward the problem you actually need to satisfy.

This is not a hack. It is often the only way to make progress.

The true problem may be too hard to search directly. A relaxation exposes enough structure to guide movement. Then later stages restore **discreteness, legality, or fidelity**.

But **relaxation creates a debt**.

The relaxed problem is **not the real problem**.

If the relaxation is faithful, it helps. If it is too loose, the optimizer may find solutions that look good only in the softened world. A robot trajectory may optimize a smooth collision penalty but still be unsafe under exact geometry. A placement may optimize a wirelength proxy but create detailed routing problems. A learned surrogate may rank candidates incorrectly in the regions that matter most.

Relaxation is powerful because **it creates gradients**.

It is dangerous because **it creates illusions**.

Good engineering is often about choosing relaxations that are useful without becoming dishonest.

In mature systems, relaxations are usually paired with correction mechanisms. Continuous placement is followed by legalization. Smooth collision penalties are followed by exact collision checks. Learned estimates are compared against expensive ground-truth tools. The relaxation proposes a direction; the rest of the system keeps it accountable.

---

## Decomposition: Surviving Scale Through Hierarchy

Large high-dimensional problems are rarely solved all at once.

They are decomposed.

This is not just software organization. It is a computational survival strategy.

In robotics, a system may decompose behavior into task planning, motion planning, control, perception, mapping, and execution monitoring. A high-level planner decides what should happen. A motion planner decides how to move. A controller handles tracking. A perception system updates the state. A recovery module handles failures.

In multi-robot systems, the decomposition becomes even more explicit. There may be task allocation, scheduling, communication, per-robot planning, coordination constraints, and execution feedback. Trying to optimize the entire joint policy of every robot over every future timestep is usually impossible. The system has to introduce structure.

Chip design is also deeply decomposed.

The flow moves through logic synthesis, floorplanning, placement, clock-tree synthesis, routing, optimization, extraction, timing analysis, signoff, and many intermediate repair loops. Routing itself decomposes into global and detailed stages. Placement decomposes across hierarchy, regions, macros, standard cells, and legalization.

Symbolic systems decompose too. Dynamic programming decomposes into subproblems. Theorem proving decomposes goals into subgoals. Compilers decompose programs into intermediate representations and passes. Language agents decompose tasks into tool calls, plans, retrieval steps, and edits.

The important point is that decomposition changes the problem.

It creates interfaces.

Each stage passes a representation to the next stage. Each stage optimizes proxies for downstream success. Each stage makes assumptions about what later stages can repair. Each stage hides some detail and exposes other detail.

That is both necessary and risky.

**Decomposition creates a kind of debt.**

Call it **interface debt**, or **decomposition debt**:

> Every boundary between stages makes the problem easier to solve locally, but creates the possibility that one stage optimizes a proxy the next stage cannot live with.


A robot task planner may choose a sequence that is symbolically valid but motion-planning impossible. "Pick up the object from the back of the shelf" may be a legal symbolic action, but the arm may not be able to reach it without collision or unstable contact. The task planner solved its abstraction; the motion planner inherits the physical debt.

A chip placer may produce a layout that looks good under density and wirelength objectives but creates routing congestion or timing failures downstream. The placement was locally defensible. The routing and timing stages still pay for it.

A language agent may produce a plausible plan that fails when an actual tool is called. The plan was coherent in text space. The environment exposes that one of its assumptions was false.

This is not a bug in decomposition. **It is the cost of decomposition.**

This is why feedback loops matter.

Real pipelines are rarely one-way. They iterate. They repair. They rip up and reroute. They replan after execution failure. They use downstream signals to adjust upstream decisions.

Simple diagrams make pipelines look sequential: perception then planning then control, or synthesis then placement then routing. But real pipelines are full of backpressure. A controller exposes that a plan is hard to track. A motion planner exposes that a symbolic task is infeasible. A router exposes that a placement created congestion. Timing analysis exposes that an apparently good physical layout damaged a critical path.

Good systems let **later stages teach earlier stages**.

Decomposition makes the problem solvable. **Feedback makes the decomposition less blind.**

The practical art is not merely choosing the right stages. It is designing the interfaces so that upstream proxies are honest enough, downstream repair is not overwhelmed, and feedback arrives early enough to change bad decisions before they harden into the system.

A good decomposition interface usually has a few properties:

* The upstream objective is predictive of downstream success.
* The downstream stage has enough information to diagnose failures.
* Typical upstream mistakes are repairable without restarting the whole pipeline.
* Feedback arrives before the system commits too much irreversible work.
* The interface exposes the constraints that actually matter, not just the ones that were convenient to model.

Bad interfaces violate one of these. They hide the geometry a motion planner needs. They hide congestion from a placer. They hide tool failures from a language agent until the final answer. They optimize a proxy because it is cheap, then discover too late that the proxy was not faithful.

This is why decomposition is not just a scaling trick. It is **a bet about which information can be safely hidden**.

---

## Learning and Amortization: Optimization Reused Across Instances

Learning deserves its own section because it is easy to misunderstand what it contributes.

The naive view is:

> Classical methods optimize. Learned methods infer.

There is some truth there, but it hides the deeper relationship.

Learning is often **optimization moved to another time scale**.

A classical optimizer solves a particular instance online. Given this robot state, this environment, this chip design, this SAT formula, or this prompt, it searches for a solution now.

A learned model performs expensive optimization during training so that future inference becomes cheap. It uses many previous instances to shape parameters that can produce useful outputs quickly on new instances.

So the better framing is:

> Classical methods perform online optimization. Learning performs offline optimization that can be reused.


This is why learning becomes attractive when a domain has repeated structure.

Robots encounter many related states, tasks, objects, and environments. Chip design tools process many designs, many blocks, many netlists, many timing paths, and many optimization histories. Language models train over enormous corpora of sequences and learn reusable statistical structure about continuation, syntax, semantics, and tool-like patterns.

> Learning is optimization compressed into parameters.


This framing makes learning feel less magical and more connected to the rest of the framework.

The model did not escape optimization. **It inherited optimization.** The training process optimized parameters. The data distribution encoded assumptions. The labels, rewards, demonstrations, human preferences, or downstream signals defined what the model learned to care about.

For LLMs, this means the model can be seen as an amortized navigation system over combinatorial sequence space. At inference time, it proposes next tokens, tool calls, code edits, or reasoning steps using structure compressed from training. Decoding may sample. Tool use may expand into external state. Chain-of-thought-like reasoning may follow local dependencies. Retrieval and context provide short-term memory. But the model's core capability comes from optimization work already stored in parameters.

That does not make language models the same as SAT solvers or robot planners. It means they share framework roles: representation, proposal, evaluation, memory, and amortization.

But amortization only helps when **the cost of training is paid back across future use**.

If every instance is completely unique, learning has little to reuse. If the training distribution is narrow, inference is brittle. If the model learns a proxy that diverges from the real downstream objective, it may accelerate the wrong behavior.

This is where ML in engineering differs from ML in demos.

In real systems, the learned model is rarely the entire solution. It is usually **a component inside a larger loop**. It predicts, initializes, ranks, proposes, filters, summarizes, or guides. Then classical tools check, optimize, repair, and verify.

That is not a weakness of learning. It is the natural role of learning in high-stakes constrained systems.

Learning is often best at "where to look."

Classical methods are often best at "what is valid."

The deepest systems use both.

---

## Historical Convergence Across Robotics and EDA

The similarity between robotics and chip design is not just a coincidence of modern ML.

Both fields have gone through a similar broad evolution.

Early systems leaned heavily on explicit models, analytical methods, and handcrafted structure.

In robotics, this meant kinematics, dynamics, geometry, control theory, optimal control, and carefully engineered planners. In chip design, this meant analytical placement, explicit timing models, handcrafted heuristics, and optimization procedures designed around domain knowledge.

This was not primitive or naive. Explicit structure is powerful. When the problem is small enough or the assumptions are clean enough, model-based methods can be extraordinarily effective.

Then scale and complexity pushed both fields toward approximation.

Robots moved into cluttered, uncertain, partially observable, contact-rich environments. They needed to handle language, perception, long-horizon tasks, and real-world messiness. Chips became larger, denser, more constrained, and more expensive to optimize exactly. The number of interacting decisions exploded.

Both fields adopted heuristics, sampling, decomposition, and stochastic search.

Exactness gave way to tractability.

Then learning entered not as a replacement for optimization, but as another layer in the framework.

Robotics began using learned perception, learned policies, learned dynamics, learned rewards, learned value functions, and learned proposal distributions. Chip design began using learned congestion predictors, timing estimators, placement guidance, netlist embeddings, graph neural networks, and now LLM-style interfaces and agents around tools.

But the important lesson is:

> Machine learning did not replace optimization. It changed where optimization happens.

Some optimization now happens during training. Some expensive evaluations are approximated by learned surrogates. Some search spaces are navigated with learned priors. Some human tool knowledge is exposed through agents. Some initial guesses come from models instead of handcrafted heuristics.

The old methods did not disappear.

They became part of **hybrid systems**.

---

## Hybrid Systems: The Modern Pattern

The most capable systems are **rarely pure**.

They do not only follow gradients.

They do not only expand graphs.

They do not only sample.

They do not only learn.

They combine methods because each component solves one part of the problem and fails somewhere else.

A robot system may use a learned policy for fast action, a task planner for long-horizon structure, a motion planner for feasibility, a controller for tracking, a simulator for data generation, and an evaluator for measuring policy reliability. In a multi-robot system, an LLM or symbolic planner may propose a task decomposition, while lower-level planners and robot APIs determine what can actually be executed.

A chip design pipeline may use analytical placement, learned congestion prediction, differentiable optimization, timing analysis, routing heuristics, legalization, signoff checks, and interactive tool agents. A model may guide the search, but the pipeline still needs hard validation.

A SAT solver combines branching, propagation, conflict analysis, clause learning, and restarts. A modern language agent may combine an LLM, retrieval, code execution, tool calls, scratchpads, tests, and human feedback.

This hybridization flows in two directions.

### Classical Methods Guide Learning

Classical methods provide structure, supervision, constraints, and data.

In robotics, planners and controllers can generate demonstrations. Simulators can produce trajectories. Kinematics can constrain policy outputs. Model predictive control can provide a strong teacher. Domain structure can reduce the amount of data needed for learning.

In chip design, classical tools generate enormous traces of decisions, metrics, and outcomes. Placers, routers, timing analyzers, and optimization engines create data that can supervise learned predictors. Analytical losses can shape training. Design rules can constrain model outputs.

In symbolic systems, SAT solvers and theorem provers can generate traces, proofs, conflicts, and supervision for learned heuristics.

Classical methods keep learning grounded.

They narrow the search space. They encode hard-won domain knowledge. They prevent models from wasting probability mass on impossible regions.

### Learning Guides Classical Methods

Learning provides priors, approximations, rankings, and warm starts.

In robotics, a learned model can suggest promising actions, predict dynamics, score candidate plans, initialize trajectory optimization, or decide which real-world experiments are most informative. In policy evaluation, learned uncertainty or active selection can reduce the cost of testing every possible task condition.

In chip design, a learned model can predict congestion before routing, estimate timing before expensive analysis, initialize placement, rank transformations, detect likely problem regions, or provide embeddings that help downstream optimizers.

In symbolic systems, learned models can guide branching, rank proof steps, select premises, propose lemmas, or prioritize search.

Learning helps the classical system **spend compute where it matters**.

This is the line I keep returning to:

> Learning handles where to look.  
> Classical methods handle what is valid.


It is not a law. There are learned systems that enforce constraints and classical systems that guide search. But as a practical mental model, it captures a lot.

Learning is good at pattern recognition, prioritization, approximation, and amortized inference. Classical methods are good at explicit constraints, verification, repair, and exploiting known structure.

The modern pattern is not **learning versus optimization**.

It is **learning inside optimization**.

This also makes the framework more actionable. The right hybrid depends on which part of the system is expensive or unreliable:

* If local geometry is meaningful, use `Follow` methods to refine quickly.
* If feasibility is the bottleneck, use `Expand` methods to build reachable structure.
* If the landscape is rough, black-box, or multi-modal, use `Sample` methods to preserve diversity.
* If evaluation is cheap, spend compute on more proposals.
* If evaluation is expensive, learn surrogates, warm starts, or priors.
* If validity is hard and non-negotiable, keep classical verifiers, repair steps, or constraint checkers in the loop.
* If the same failure recurs, add memory: cached constraints, learned clauses, maps, replay, or model parameters.

This is not a recipe, but it is a useful design habit. **Diagnose the bottleneck first**, then choose the framework component that attacks that bottleneck directly.

---

## Failure Modes Reveal Assumptions

Every method carries assumptions.

Failures are what happen when those assumptions stop being true.

Follow methods assume local structure is useful. When the landscape is deceptive, they get trapped in local minima, follow bad gradients, propagate misleading values, or overfit to a relaxation.

Expand methods assume feasible connectivity can be discovered at reasonable cost. When the space is too large, narrow, or high-dimensional, coverage becomes expensive.

Sample methods assume evaluation and selection can gradually move probability mass toward better regions. When selection pressure is wrong, they converge too early, waste compute, or collapse diversity.

Relaxations assume the softened problem preserves enough of the true problem. When the relaxation is too loose, the system optimizes an illusion.

Decompositions assume upstream and downstream stages are aligned. When the interfaces are bad, one stage creates problems another stage cannot repair.

Memory assumes the retained structure will remain useful. When the environment, design family, objective, or formula distribution changes, cached structure can become misleading.

Amortization assumes future instances resemble past data. When the distribution shifts, learned systems extrapolate poorly.

Evaluation assumes the metrics capture what matters. When the metric is a proxy, the system may exploit it.

This is why engineering judgment matters.

The question is not **"which algorithm is best?"**

The question is:

> **Which assumptions are acceptable for this problem, and how will the system fail when they are violated?**

That question is much closer to how real practitioners think.

In a robotics lab, a policy that works in simulation is not done. You ask how it fails under lighting changes, object variation, calibration error, latency, contact, or a different robot. In chip design, a learned predictor that performs well on a benchmark is not done. You ask how it behaves across design families, process nodes, optimization stages, and downstream signoff checks. In language models, a fluent answer is not enough. You ask what validates it, what tools it can call, what context it used, and how it fails outside familiar distributions.

The framework helps because it gives you places to look.

Is the representation missing structure?

Is the evaluation signal too weak?

Is the proposal method too local?

Is memory accumulating the wrong thing?

Is the relaxation misleading?

Is the decomposition creating bad interfaces?

Is the learned component being asked to extrapolate?

These are better questions than simply asking whether the method is "AI" or "classical."

---

## Beyond Robotics and Chips

Robotics and chip design are the examples I know best from direct experience. SAT solvers, dynamic programming, and language models are the stronger **stress tests** in this essay because they are concrete computational systems with recognizable representations, proposal dynamics, evaluation rules, and memory structures.

**That is enough generalization for one post.**

Other domains may fit parts of the pattern too. Game-playing systems combine search trees, learned value functions, rollouts, and memory. Biological evolution combines variation, selection, inherited structure, and accumulated adaptation. Scientific discovery and cognition may also involve representation, evaluation, sampling, decomposition, and memory.

But those are **looser analogies**. I would treat them as places to investigate next, not as evidence already proven here.

It would be easy to overclaim here.

I do not think this framework explains intelligence by itself. I do not think every system is secretly the same. The details matter enormously. A contact-rich robot manipulation problem, a chip routing problem, a theorem-proving problem, and an evolutionary process are not interchangeable.

But they may be pressured by the same kind of computational bottleneck.

The more modest claim is enough:

> Whenever a system must efficiently navigate a massive constrained space, the same pressures tend to reappear.

It needs a way to represent candidates, judge them, propose changes, and retain useful structure. When the space becomes too hard to search directly, it often needs to soften the problem, split it into stages, reuse previous optimization work, and combine multiple imperfect methods.

That recurrence is the interesting thing.

---

## Different Domains, Same Framework

Robotics and chip design are not the same.

SAT solving, dynamic programming, graph search, Monte Carlo tree search, and language modeling are not the same either.

Their objects are different. Their constraints are different. Their tools are different. Their cultures are different. Their failure cases are different.

But within the scope of this essay, they repeatedly point toward a similar computational framework because they face a similar underlying challenge.

They must navigate spaces too large to enumerate.

They must satisfy constraints that are not optional.

They must optimize objectives that conflict.

They must use approximations without being fooled by them.

They must decompose problems without losing the dependencies between stages.

They must decide what to learn, what to search, what to verify, and what to remember.

That is why the same moves keep showing up:

* Follow structure when local information is useful.
* Expand feasibility when reachability is the bottleneck.
* Sample possibilities when the landscape is rough.
* Remember useful structure when computation should not be repeated.
* Relax the problem when the exact version is too hard.
* Decompose the system when the whole thing is too large.
* Amortize optimization when the domain repeats.
* Hybridize when no single method has the right assumptions everywhere.

For me, the value of this lens is that new methods stop looking like isolated tricks. They become design choices inside a larger framework. I can ask: what is the representation, what is the evaluation signal, how are candidates proposed, what is remembered, what has been relaxed, how is the problem decomposed, and where has optimization been amortized?

Those questions do not solve the problem automatically.

But they make the problem legible.

Before a system can solve a hard problem, it has to **make the problem searchable**.
