---
layout: post
title: "Designing a Chip Is Designing a Factory"
date: 2026-09-03 10:00:00 -0800
categories: general
image: /assets/images/blog/designing-chip-as-factory.jpeg
image_alt: "Minimal abstract title image for this blog post"
---

I've spent the past two years at Synopsys working on AI/ML for <span class="term" tabindex="0" data-tooltip="Electronic Design Automation: the software used to design, verify, and physically implement chips.">EDA</span> — electronic design automation, the software used to design chips — so it figures I should write a post explaining chip design. I don't claim to be an expert. I never took a formal <span class="term" tabindex="0" data-tooltip="Very-Large-Scale Integration: packing a huge number of transistors onto one chip. The usual name for modern digital chip design.">VLSI</span> class, and I came in knowing software, ML, and computer science. What I have now is a working understanding of the space: from people around me at work, from digging into the parts that didn't make sense, and from learning the science and the economics of the industry.

What this post will emphasize most is the **systems view**. The hope is a mental model of **why chips and EDA exist**, rather than a catalog of what they are made from — the motivation over the means. In my experience, starting there, instead of from a pile of electrophysical laws, is what actually makes the space click for novices. I still count myself as one.

So with that out of the way, let's get started.

**Note**: I used AI while writing this, because it is 2026 and refusing good tools is not a personality trait. The ideas, structure, edits, and final judgment are mine; AI helped me explore, pressure-test, and sharpen the writing.

## Table of Contents

- Table of Contents
{:toc}

---

## Designing a Chip Is Designing a Factory

Most introductions to chip design begin at the bottom: <span class="term" tabindex="0" data-tooltip="Tiny electrical switches. Billions of them are packed onto a modern processor. A bit is a 0 or a 1 depending on whether a transistor is allowing current through or blocking it.">transistors</span> — tiny electrical switches — then <span class="term" tabindex="0" data-tooltip="Tiny logic circuits built from transistors that implement elementary operations such as AND, OR, and NOT.">gates</span>, <span class="term" tabindex="0" data-tooltip="Manufacturing the chip in a foundry: turning a layout into physical transistors and wires on silicon.">fabrication</span>, and progressively more complicated electrical structures. That is a valid way to explain what a chip is made from, but it can obscure **why anyone is arranging those structures in the first place**.

A bridge may be made from steel and concrete, but we do not begin understanding bridge design by memorizing the chemistry of steel. We begin with the job: carry people and vehicles across a gap without collapsing. The material matters because it determines what structures are physically possible, but **the structure is motivated by the job**.

The same distinction is useful for chips.

<span class="term" tabindex="0" data-tooltip="The physics of how transistors and wires actually behave: delay, energy, heat, and how small a feature can be manufactured.">Semiconductor physics</span> is the means by which chips are built. It determines how quickly signals can move, how much energy a computation consumes, how small a feature can be manufactured, and how much heat a device can survive. But the architectural motivation for a chip begins one level higher:

> We want to build a physical system that repeatedly transforms information, at some required speed, energy, cost, and level of reliability.

From that viewpoint, **designing a chip resembles designing a factory**.

A factory receives materials, moves them between stations, performs operations on them, stores unfinished work, coordinates which operation happens next, and eventually sends finished products out. A chip does the same thing with information. Its raw materials are **<span class="term" tabindex="0" data-tooltip="The chip's raw materials: a 0 or a 1, represented by more charge or less in some tiny structure.">bits</span>**. Its workstations are arithmetic and logical circuits. Its warehouses are memories. Its roads and conveyor belts are wires and communication networks. Its managers and schedules are control circuits. Its loading docks are external interfaces. Its electrical and clock systems keep the entire operation running.

This is not just an analogy for beginners. It captures the central systems problem of chip design: **what resources should exist**, **how many of each should exist**, and **how should information flow among them**?

---

## Why Chips Exist

Suppose we want a machine to perform some useful operation: add two numbers, render an image, encrypt a message, process a <span class="term" tabindex="0" data-tooltip="A formatted chunk of data sent over a network. A switch or network processor's raw material.">network packet</span>, or run a <span class="term" tabindex="0" data-tooltip="A computation built from many simple arithmetic operations, especially matrix multiplies. The workload many accelerators are built to run.">neural network</span>.

At the most abstract level, each task asks for a transformation:

$$
\text{output information} = f(\text{input information})
$$

Software describes which transformations we want. A chip is the **physical machinery that actually carries them out**.

That machinery is necessary because an abstract operation does not execute itself. To calculate (7 + 4), some physical system must represent 7 and 4, bring those representations to a circuit capable of addition, allow electrical signals to propagate through that circuit, and preserve the resulting representation of 11 somewhere afterward.

Even this trivial calculation already creates several distinct needs:

- Something must **perform** the addition.
- Something must **hold** the input and output values.
- Something must **move** those values to the correct places.
- Something must **decide** that addition is the next operation to perform.
- Something must provide the **power and timing** that make the physical operation possible.

A real workload repeats this process billions or trillions of times, with many operations in flight and many pieces of data competing for limited resources. Chip design is therefore not simply the design of individual calculators. **It is the design of an entire information-processing system.**

---

## A Chip Is a Finite Production System

Every chip has limited physical resources. There are only so many transistors, only so much area, only so much electrical power, and only so much heat that can be removed. Signals also require time and energy to travel across wires.

Consequently, no chip can contain an unlimited number of every useful component. **The designer must choose what kind of factory to build.**

A general-purpose <span class="term" tabindex="0" data-tooltip="Central Processing Unit: a general-purpose processor that can run many kinds of programs, including ones its designers never anticipated.">CPU</span> is like a flexible factory filled with adaptable workers. It can execute a huge variety of procedures, including procedures its designers never anticipated. That flexibility requires substantial machinery for interpreting <span class="term" tabindex="0" data-tooltip="The work orders a general-purpose processor reads and carries out. Interpreting them is extra machinery a specialized accelerator can often skip.">instructions</span>, tracking dependencies, predicting what work will come next, and recovering when those predictions are wrong.

A specialized <span class="term" tabindex="0" data-tooltip="A chip or block built around a narrower production line than a CPU: more of its area goes to one family of operations.">accelerator</span> is more like a factory arranged around a narrower production line. If the important workload repeatedly performs <span class="term" tabindex="0" data-tooltip="The dominant arithmetic of neural networks: combining rows and columns of numbers. A factory arranged around this operation looks very different from a CPU.">matrix multiplications</span>, video decoding, packet processing, or encryption, the chip can devote more of its area to exactly those operations. It sacrifices some flexibility in exchange for greater <span class="term" tabindex="0" data-tooltip="Useful work finished per second — more finished product leaving the factory — not the same thing as how fast the clock rings."><strong>throughput</strong></span> — more finished work per second — lower energy use, or both.

An <span class="term" tabindex="0" data-tooltip="Application-specific integrated circuit: a chip whose mix of resources is chosen for a particular application, not for general-purpose software.">ASIC</span>, or <span class="term" tabindex="0" data-tooltip="A chip whose mix of compute, memory, communication, and control is chosen for a particular application or family of applications, not for general-purpose software.">application-specific integrated circuit</span>, is a chip designed around a particular application or family of applications. “Application-specific” does not necessarily mean it performs only one operation. It means the balance of compute, memory, communication, and control has been deliberately chosen for a narrower purpose than a general-purpose processor.

The identity of a chip therefore comes less from whether it contains the standard categories of machinery — nearly all substantial chips do — and more from **the proportions and arrangement of that machinery**.

Two factories may both contain workstations, warehouses, roads, and managers while producing completely different goods. Likewise, a CPU, a <span class="term" tabindex="0" data-tooltip="Graphics Processing Unit: a processor built for highly parallel arithmetic. Originally for graphics; now also used for neural networks and other regular, wide computations.">GPU</span>, a neural-network accelerator, a network switch, and a storage controller all contain compute, memory, communication, and control. What differs is what they compute, what data they retain, how that data moves, and **which bottleneck the design is intended to eliminate**.

---

## The Basic Jobs Inside a Chip

It is easy to encounter chip terminology as an unstructured collection of names: <span class="term" tabindex="0" data-tooltip="Complete processing units, often general-purpose CPUs, that can fetch and execute instructions.">cores</span>, <span class="term" tabindex="0" data-tooltip="A small, fast memory that keeps recently or frequently used data close to compute, so the chip does not have to visit slower, larger storage as often.">caches</span>, <span class="term" tabindex="0" data-tooltip="Compute blocks specialized for the regular arithmetic of neural networks, especially matrix multiplies.">tensor units</span>, <span class="term" tabindex="0" data-tooltip="A shared communication path that multiple blocks take turns using, like a single corridor that everyone must share.">buses</span>, <span class="term" tabindex="0" data-tooltip="Blocks that forward messages through an on-chip network, choosing the next hop toward the destination.">routers</span>, <span class="term" tabindex="0" data-tooltip="Blocks that implement the rules and physical signaling for talking to memory chips off the die.">memory controllers</span>, <span class="term" tabindex="0" data-tooltip="Circuits that produce the periodic clock pulse — the factory's shift bell.">clock generators</span>, <span class="term" tabindex="0" data-tooltip="The electrical circuitry that drives signals off the chip. Same idea as a PHY.">physical interfaces</span>, <span class="term" tabindex="0" data-tooltip="Control logic that decides which piece of waiting work runs next.">schedulers</span>, and so on. A better approach is to classify each component by **the job it performs in the larger factory**.

Almost every chip component primarily contributes to one of the following needs:

1. Transform data.
2. Hold data.
3. Move data inside the chip.
4. Direct what happens next.
5. Exchange data with the outside world.
6. Keep the physical machine operating.
7. Protect, test, and observe the machine.

These are semantic categories: they describe **why a component exists**. A physical <span class="term" tabindex="0" data-tooltip="A named functional region of the chip, treated as one piece of the factory: a compute unit, a memory, a controller, and so on.">block</span> may contribute to more than one category, but asking for its primary job usually makes an unfamiliar design much easier to understand.

### 1. Compute

If a chip is a factory, **compute circuitry is the workstation floor**. Incoming materials — bits — arrive at a station, an operation is performed, and different materials leave.

An <span class="term" tabindex="0" data-tooltip="A compute circuit that produces a sum.">adder</span> produces a sum. A <span class="term" tabindex="0" data-tooltip="A compute circuit that determines which of two values is larger.">comparator</span> determines which value is larger. A <span class="term" tabindex="0" data-tooltip="A compute circuit that produces a product.">multiplier</span> produces a product. A <span class="term" tabindex="0" data-tooltip="A compute block that performs many multiplications and additions together, the usual workstation for neural-network arithmetic.">matrix engine</span> performs many multiplications and additions together. A video-decoding block turns compressed information into <span class="term" tabindex="0" data-tooltip="The color or brightness of one dot in an image. A video decoder's output.">pixel values</span>.

At the simplest level:

$$
\text{new data} = f(\text{existing data})
$$

An <span class="term" tabindex="0" data-tooltip="A compute workstation that packages several elementary arithmetic and logical operations, such as add, subtract, and compare. Useful, but not a complete processor by itself.">arithmetic logic unit (ALU)</span> packages several elementary arithmetic and logical operations together. But an <span class="term" tabindex="0" data-tooltip="Arithmetic logic unit: a compute workstation for elementary arithmetic and logical operations. Not a complete processor by itself.">ALU</span> is not a complete processor. A processor also needs storage for immediate values, control machinery that selects operations, and connections through which data arrives and departs. The workstation is useless without the rest of the plant.

When looking at a compute block, the important questions are:

- What transformations can it perform?
- How many operations can it perform at once?
- What kinds and sizes of values can it accept?
- How quickly can it receive new work?
- **Can the rest of the chip supply data quickly enough to keep it busy?**

That last question matters enormously. **A factory gains nothing from installing a thousand workstations if its conveyor belts can feed only ten of them.**

### 2. Memory

If compute units are workstations, **memories are the warehouses and staging areas**. Most computations require values to survive across time. Inputs must wait until the appropriate workstation becomes available. Intermediate results must remain somewhere until later operations consume them. Instructions, configuration, <span class="term" tabindex="0" data-tooltip="Memories that store precomputed answers so the chip can look up a result instead of calculating it from scratch.">lookup tables</span>, and final outputs must all be retained.

Memory satisfies this requirement. Conceptually, it establishes a mapping from a location to some stored bits:

$$
\text{location} \longrightarrow \text{stored value}
$$

Different memories occupy different levels of the factory. <span class="term" tabindex="0" data-tooltip="Tiny storage sitting immediately beside compute, holding values that are about to be used or have just been produced. Fast, but you cannot afford many of them.">Registers</span> are tiny storage locations positioned immediately beside compute circuits — the bins on the workbench. Larger on-chip memories hold more information but require more area and often more access time; they are the stockrooms on the plant floor. External memory can hold dramatically more data, but reaching it requires signals to cross the chip boundary. That is the off-site warehouse: huge, and expensive to visit.

This produces a persistent tradeoff:

**Data close to compute is quick to use but expensive to keep there; distant storage is larger but more expensive to reach.**

Registers, <span class="term" tabindex="0" data-tooltip="A small array of registers that a compute unit can read and write, like a rack of bins on the workbench.">register files</span>, <span class="term" tabindex="0" data-tooltip="A small, fast memory that keeps recently or frequently used data close to compute, so the chip does not have to visit slower, larger storage as often.">caches</span>, <span class="term" tabindex="0" data-tooltip="Software-managed local memories. Unlike a cache, the program decides what stays nearby.">scratchpads</span>, <span class="term" tabindex="0" data-tooltip="Memories that hold items in order until the next station can take them, like a line at a workstation.">queues</span>, <span class="term" tabindex="0" data-tooltip="A cell whose job is to strengthen a signal so it can drive a longer wire or more destinations without becoming slow and sloppy.">buffers</span>, and <span class="term" tabindex="0" data-tooltip="Memory that holds fixed values, such as lookup tables or boot code, and is not written during ordinary operation.">read-only memories</span> are all variations on the same basic job: **preserving information until some part of the chip needs it**.

### 3. Internal communication

Compute and memory are useful only if information can travel between them. **That travel is the job of the factory's roads and conveyor belts.**

For a tiny circuit, direct wires may be sufficient — a short walk across a small shop floor. As the number of components grows, communication becomes a system of its own. Multiple senders may want the same receiver. A destination may be temporarily busy. Messages may need to travel different distances, arrive in order, or compete for limited wire capacity.

Chips therefore contain structured <span class="term" tabindex="0" data-tooltip="The on-chip communication system that relocates data between blocks: wires, buses, crossbars, rings, and networks of routers.">interconnects</span>: shared <span class="term" tabindex="0" data-tooltip="A shared communication path that multiple blocks take turns using, like a single corridor that everyone must share.">buses</span>, <span class="term" tabindex="0" data-tooltip="Point-to-point wires between two blocks, with no sharing. Simple and fast, but they do not scale to many partners.">direct links</span>, <span class="term" tabindex="0" data-tooltip="A communication structure in which many senders can connect to many receivers at once, like a switchyard rather than a single shared corridor.">crossbars</span>, <span class="term" tabindex="0" data-tooltip="A communication topology in which blocks sit on a loop and pass messages around it.">rings</span>, and networks composed of routers. They also contain <span class="term" tabindex="0" data-tooltip="Circuits that decide who may use a contested path when several senders want the same road.">arbiters</span> that decide who may use a contested path — traffic controllers at the intersections — and <span class="term" tabindex="0" data-tooltip="Cells that strengthen a signal so it can drive a longer wire or more destinations.">buffers</span> that hold data while it waits.

The factory analogy is especially literal here. Adding more workstations increases theoretical production capacity, but real output may still be limited by congested roads or distant warehouses. **Modern chips frequently spend a large fraction of their energy not changing data, but moving it.**

This gives us a clean separation:

- **Compute** changes information.
- **Memory** retains information.
- **Interconnect** relocates information.

### 4. Control

A pile of compute units, memories, and wires does not spontaneously perform a useful workload. Something must determine which operation occurs, which values it consumes, where its result goes, and what should happen afterward.

**That is the job of control: the managers, dispatchers, and schedules of the factory.**

The simplest control structure is a <span class="term" tabindex="0" data-tooltip="A circuit that remembers the system's current situation and, given current inputs, selects a next situation and a set of actions. The most basic form of on-chip management.">state machine</span>. It remembers the system's current situation and uses current inputs to select a next situation and a set of actions:

$$
(\text{current state}, \text{inputs}) \longrightarrow (\text{next state}, \text{actions})
$$

In a CPU, control machinery fetches an <span class="term" tabindex="0" data-tooltip="One work order a processor fetches, interprets, and carries out.">instruction</span>, interprets it, finds its input values, activates the appropriate compute resources, and records the result. In a more specialized accelerator, the control may repeatedly fetch blocks of data, send them through a fixed sequence of operations, and store the outputs. One is a factory that reads a new work order at every station; the other is a factory whose line is already laid out for a known product.

<span class="term" tabindex="0" data-tooltip="Control logic that interprets an instruction and turns it into the signals that activate the right compute and memory resources.">Instruction decoders</span>, schedulers, <span class="term" tabindex="0" data-tooltip="Control machinery that remembers which operations are waiting on others, so work is not started before its inputs exist.">dependency trackers</span>, <span class="term" tabindex="0" data-tooltip="Control logic that holds waiting work and feeds it to stations as they become free.">work-queue managers</span>, <span class="term" tabindex="0" data-tooltip="Control logic that handles unexpected events — a finished transfer, an error, a timer — and steers the processor to deal with them.">interrupt controllers</span>, and <span class="term" tabindex="0" data-tooltip="Logic that programs how a block should behave: addresses, modes, enables, and routing tables, rather than the data being processed.">configuration logic</span> are all forms of control. They technically perform logical computation, but it is useful to distinguish their purpose:

- **<span class="term" tabindex="0" data-tooltip="The circuitry that transforms the workload's data — the plant floor — as opposed to the logic that decides how and when that floor operates.">Datapath</span> compute** transforms the workload's data.
- **Control logic** decides how and when the <span class="term" tabindex="0" data-tooltip="The circuitry that transforms the workload's data — the plant floor — as opposed to the logic that decides how and when that floor operates.">datapath</span> operates.

**Control is the difference between owning machinery and having an organized production process.**

### 5. External interfaces

A factory that never ships or receives anything is just a closed room. **The loading docks are where the chip meets the rest of the world.**

A chip rarely operates alone. It may need to exchange information with memory chips, storage devices, sensors, displays, networks, or other processors.

Crossing the chip boundary introduces two new problems.

First, the chip and the external device must agree on a conversation: what each message means, when it may be sent, how receipt is acknowledged, and what happens if something goes wrong. A **controller** implements these rules — the shipping paperwork, the language of the transaction, the sequence of the handoff.

Second, internal digital signals must be transmitted across real <span class="term" tabindex="0" data-tooltip="The housing and wiring around a die that gives it power, cooling, mechanical protection, and connections to memory, boards, and other chips.">package</span> and <span class="term" tabindex="0" data-tooltip="The board the packaged chip sits on, supplying power, clocks, reset, and connections to the rest of the system.">circuit-board</span> connections. Special physical circuitry generates and receives the required electrical signals. This circuitry is often called a <span class="term" tabindex="0" data-tooltip="Physical interface: the circuitry that actually drives and receives electrical signals across the package and board. The dock and transfer mechanism, as opposed to the paperwork of the transaction.">physical interface, or PHY</span>.

The distinction is similar to shipping goods internationally:

- The **controller** handles the language, forms, sequence, and rules of the transaction.
- The **physical interface** operates the dock, vehicles, and physical transfer mechanism.

Memory controllers, network controllers, storage controllers, peripheral controllers, and <span class="term" tabindex="0" data-tooltip="Communication between separate dies, across a package or board, rather than on one die's internal interconnect.">chip-to-chip</span> links all exist to let the internal factory **exchange information with a larger system**.

### 6. Operating infrastructure

A factory still needs power, a shift bell, and a way to start the day. **A chip is no different.** The information-processing machinery still needs a physical operating environment.

<span class="term" tabindex="0" data-tooltip="The on-chip electrical grid that delivers energy to every region of the die.">Power-distribution structures</span> deliver electrical energy throughout the chip — the plant's electrical grid. That energy arrives at a particular <span class="term" tabindex="0" data-tooltip="Electrical pressure. It pushes charge through transistors and wires. Higher voltage can make switches flip faster, but each flip costs more energy.">voltage</span>: the electrical pressure that pushes <span class="term" tabindex="0" data-tooltip="The stuff that flows in a wire. A bit is a 0 or a 1 because some tiny part of the chip is holding more charge or less.">charge</span> — the stuff that flows in a wire — through the transistors. The flow of that charge is <span class="term" tabindex="0" data-tooltip="The flow of charge through a wire. Current is what actually moves when the factory is working.">current</span>. Higher pressure can make switches flip faster; it also spends more energy.

<span class="term" tabindex="0" data-tooltip="The circuits that produce and distribute the periodic pulse that keeps the chip in rhythm. The factory's shift-bell system.">Clocking</span> circuits provide that rhythm. The clock is a periodic electrical pulse. Each pulse, a <span class="term" tabindex="0" data-tooltip="One tick of the clock: the instant storage elements capture new values.">clock edge</span>, is the moment storage elements are allowed to capture new values. The <span class="term" tabindex="0" data-tooltip="How many times per second the clock ticks, also called frequency. Faster is not free: every extra tick is another chance to spend energy.">clock rate</span>, also called <span class="term" tabindex="0" data-tooltip="How many times per second the clock ticks. Same idea as clock rate.">frequency</span>, is how many times per second the bell rings. A higher clock rate means more steps per second — but only if every station can finish its work before the next ring.

<span class="term" tabindex="0" data-tooltip="Circuitry that forces the machine into a known starting state when it boots, like opening the plant and putting every station in a defined position.">Reset</span> circuitry places the system into a known initial condition when it begins operating — opening the plant and putting every station into a defined starting state. <span class="term" tabindex="0" data-tooltip="Logic that slows or shuts down idle regions to save energy.">Power-management logic</span> can slow or shut down idle regions, while <span class="term" tabindex="0" data-tooltip="Sensors and logic that watch temperature and voltage and intervene before the chip becomes unsafe.">monitoring circuitry</span> prevents unsafe temperatures or voltages.

These components normally do not advance the user's workload directly. They are closer to a factory's electrical grid, ventilation, master timing system, and startup procedure. **They make organized operation possible at all.**

### 7. Protection and observability

Factories have inspectors, security, and quality control. **Chips need the same kinds of machinery**: something that watches the plant, restricts who can do what, and records what happened when things go wrong.

Real physical systems encounter <span class="term" tabindex="0" data-tooltip="Physical or electrical failures: corrupted bits, defective structures, overheating, or illegal accesses.">faults</span>. Bits may become corrupted. A fabricated structure may contain a <span class="term" tabindex="0" data-tooltip="A physical manufacturing mistake in one copy of the chip — a broken wire, a short, a bad transistor — even if the design itself is correct.">defect</span>. A block may overheat. Software may attempt an unauthorized memory access. A design may operate correctly most of the time but fail under one rare sequence of events.

Chips therefore contain machinery that watches and constrains the rest of the system. <span class="term" tabindex="0" data-tooltip="Circuitry that notices when stored or transmitted bits have flipped, and often repairs them.">Error-detection and correction</span> circuits protect stored or transmitted data. <span class="term" tabindex="0" data-tooltip="Logic that asks whether a requester is allowed to touch a given piece of memory or a given operation.">Permission checks</span> prevent one program from accessing another's memory. <span class="term" tabindex="0" data-tooltip="Logic that checks that only approved code is allowed to start the machine.">Secure-boot</span> logic verifies what code is allowed to start the machine. <span class="term" tabindex="0" data-tooltip="On-chip meters that record how often events happen — cache misses, stalls, retired operations — so software can see why the factory is slow.">Performance counters</span> and <span class="term" tabindex="0" data-tooltip="Small memories that record a recent history of internal events, used to debug rare failures.">trace buffers</span> record internal behavior. <span class="term" tabindex="0" data-tooltip="On-chip features, including scan and memory BIST, that help determine whether a manufactured copy is physically sound.">Built-in test structures</span> help determine whether the manufactured chip is physically sound.

These mechanisms answer three practical questions:

- Is the chip **functioning correctly**?
- Is every requester **permitted** to perform the operation it requested?
- If something fails or runs slowly, **can we determine why**?

---

## The Complete Chip Story

Now imagine that a chip must produce a result from some incoming data. The particular application does not matter; the same broad sequence appears in CPUs, GPUs, accelerators, network processors, and many other chips.

First, the input must enter the chip through an external interface — a loading dock — or already be present in local memory. It then waits in some storage structure until the relevant machinery is ready.

Control logic, the factory's management layer, recognizes that a piece of work is available. It determines which operation must happen and reserves the required resources. The internal interconnect — the roads — moves the input from its current storage location toward a compute block.

The compute block transforms the data. If the overall task requires several operations, intermediate results return to registers, buffers, caches, or other memories. Control selects the next operation, and the interconnect moves each intermediate value to wherever it must go. This cycle — **move, transform, hold, decide** — continues until the result is complete.

The final result is stored locally or carried through another external interface to memory, another chip, or a device. Throughout the process, clock and power infrastructure keep the physical machine operating, while protection and monitoring circuitry check that the operations are legal and the hardware remains healthy.

In compact form, the life of data inside a chip is:

> Arrive, wait, move, transform, wait again, and eventually leave — under continuous control and within physical limits.

The apparent complexity of a modern chip comes from repeating these simple jobs at enormous scale. There may be thousands of compute units, many kinds of memory, several overlapping communication networks, and numerous layers of scheduling. But the purpose of every structure can still be traced back to the same production system.

That mapping, lined up in one place:


| Factory                                   | Chip                                                   | Job                                  |
| ----------------------------------------- | ------------------------------------------------------ | ------------------------------------ |
| Raw materials                             | Bits and bytes                                         | What the plant processes             |
| Workstations                              | Compute blocks (ALUs, multipliers, matrix engines)     | Transform data                       |
| Warehouses and staging areas              | Memories (registers, caches, buffers, off-chip memory) | Hold data                            |
| Roads and conveyor belts                  | Interconnect (wires, buses, <span class="term" tabindex="0" data-tooltip="On-chip packet networks of routers, used when a simple shared bus is no longer enough to move data among many blocks.">networks-on-chip</span>)          | Move data inside the chip            |
| Managers and schedules                    | Control logic (state machines, schedulers, decoders)   | Direct what happens next             |
| Loading docks                             | External interfaces (controllers and PHYs)             | Exchange data with the outside world |
| Power grid, lighting, and shift bells     | Power, clocks, and reset                               | Keep the physical machine operating  |
| Inspectors, security, and quality control | Protection, test, and observability                    | Keep the factory trustworthy         |


---

## Chip Design Is the Art of Choosing the Bottleneck

No design makes every operation free. More compute consumes area and power. More memory also consumes area. Wider communication paths require additional wiring. A faster clock makes it harder to finish each step in time, and harder to deliver power cleanly. Greater flexibility requires more control machinery. Stronger reliability mechanisms impose their own costs.

The usual scoreboard for those costs is <span class="term" tabindex="0" data-tooltip="Power, Performance, and Area: the three coupled scores a chip is judged on. Improving one usually pressures the other two."><strong>PPA</strong></span>: **power, performance, and area**. Area is the size of the plant — how much silicon the chip occupies. Power is the electricity bill and the heat that must leave the building. Performance is how much useful product the factory ships, and how long one order takes.

These are not three independent scores. **They are three views of the same physical act: moving electrical charge through transistors and wires on a finite piece of silicon.**

A bit is a 0 or a 1 only because some tiny piece of the chip is holding more charge or less. To compute, or even to move a bit from one place to another, the chip has to push that charge around.

Every wire and transistor acts like a small bucket for that charge. How much charge the bucket can hold is its <span class="term" tabindex="0" data-tooltip="How much charge a wire or transistor can hold — the size of the bucket. Bigger buckets take more energy to fill.">capacitance</span>. Filling a bigger bucket takes more energy. Filling it more often takes more energy per second. That energy-per-second is power, and it comes in two main kinds.

<span class="term" tabindex="0" data-tooltip="Power spent doing useful switching: filling and emptying charge buckets every time a signal flips from 0 to 1 or 1 to 0.">Dynamic power</span> is the cost of useful switching. Every time a signal flips from 0 to 1 or 1 to 0, buckets get filled or emptied. Raise the clock rate — ring the shift bell more often — and you switch more times per second, so dynamic power rises.

<span class="term" tabindex="0" data-tooltip="Power wasted by imperfect switches. A little current seeps through even when a transistor should be off.">Leakage</span> is the cost of imperfect switches. A transistor is supposed to be fully on or fully off, but a little current seeps through even when it should be blocking. That trickle is wasted whether the factory is busy or idle, and a chip with more transistors leaks more.

That is why a PPA tradeoff exists at all. Every extra workstation, warehouse, or road occupies floor space. Those structures are also more buckets to fill and more switches that leak. Adding machinery to do more work usually costs **area and power together**. Making the remaining machinery faster usually costs **power, and often area too**. On a large modern chip you often cannot turn every workstation on at once: the power budget is smaller than the area budget.

The physics of going faster is especially unforgiving. Raise the voltage and transistors switch faster: the <span class="term" tabindex="0" data-tooltip="How long a signal takes to travel through a circuit and settle to a valid 0 or 1.">delay</span> — the time for a signal to travel through a circuit and settle to a valid 0 or 1 — gets shorter. But you also stuff more energy into every bucket, roughly with the square of the voltage, so power climbs steeply. Use larger, stronger transistors and delay also falls, but they occupy more silicon and are bigger buckets. **Speed is bought by moving more charge, more often, more violently.**

A larger plant can hold more machinery, which can raise throughput. It can also make the plant slower. Signals have farther to travel; long wires are both slow and energy-hungry. **Area can help performance, and area can hurt it.** The same coupling can run the other way: spending area on more parallel units, then running them at a lower clock, can deliver the same throughput at lower power than one screaming-fast unit. That is still a tradeoff. It is just a different point on the same surface.

This is also why **performance is not the same thing as timing**.

<span class="term" tabindex="0" data-tooltip="Whether every circuit finishes its step before the next clock edge. An implementation question; performance is a product question.">Timing</span> asks an implementation question: can this circuit finish its step before the next clock edge? The deadline is set by the slowest chain of stations that must complete in one tick — the <span class="term" tabindex="0" data-tooltip="The slowest chain of logic that must finish in one clock cycle. The whole chip's clock can only ring as often as this path allows.">critical path</span>. Miss that deadline and the whole line must slow down.

**Performance** asks a product question: how much useful work leaves the factory per second, and how long does one job take? Throughput can rise at the same clock if you add parallel workstations. <span class="term" tabindex="0" data-tooltip="How long one job takes from arrival to result — order time, not the same thing as clock-edge travel time."><strong>Latency</strong></span> — the time for one job to go from arrival to result — can fall if data stays local, even if the bell does not speed up. A design can meet a faster clock and still get no useful speedup if those workstations spend the extra ticks waiting for data.

So timing is one way to buy performance. <span class="term" tabindex="0" data-tooltip="More workstations doing the same kind of work at once. One way to buy performance without ringing the clock faster.">Parallelism</span> — more workstations doing the same kind of work at once — is another. <span class="term" tabindex="0" data-tooltip="The fraction of the factory that is actually busy. A thousand idle workstations are not a thousand workstations.">Utilization</span> — the fraction of the plant that is actually busy — is a third. All three spend area and power.


| Axis        | Factory reading            | Why it is scarce                                                                                             |
| ----------- | -------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Area        | Floor space of the plant   | Transistors and wires occupy silicon; a bigger <span class="term" tabindex="0" data-tooltip="The piece of silicon one chip is cut from. A larger die can hold more machinery, costs more to manufacture, and makes wires longer.">die</span> costs more, and wires grow longer                         |
| Power       | Electricity and heat       | Energy to switch signals (dynamic power), plus leakage when idle; the chip's case can only dump so much heat |
| Performance | Output rate and order time | Useful work per second — clock rate × parallelism × utilization — and the latency of one job                 |


**The designer is constantly deciding where limited physical resources create the most value.**

If compute units spend most of their time waiting for data, adding more compute will not help. The design may need more memory <span class="term" tabindex="0" data-tooltip="How much data a path or memory system can deliver per second.">bandwidth</span> — more data shipped per second from the warehouses — more local storage, or a better data-reuse strategy. If data is available but the compute units cannot transform it quickly enough, then more or faster compute may help. If many blocks are ready but messages are stuck competing for the same paths, the interconnect has become the constraint. If all of these resources exist but control cannot schedule them effectively, utilization remains low. In every case the temptation is to treat the bottleneck as a timing problem. Sometimes it is. Often it is an area or power problem wearing a performance costume.

This is why chip <span class="term" tabindex="0" data-tooltip="The large-scale choice of what machinery exists and how work moves among it: a hypothesis about flow and bottlenecks, before clock-by-clock detail."><strong>architecture</strong></span> is fundamentally a **systems discipline**. The objective is not to maximize any one component in isolation, and not to treat PPA as three knobs you can turn separately. **It is to arrange the whole factory so that the desired workloads flow through it efficiently, at a point on that tradeoff you can actually afford.**

Different chips make different bets about that flow. A CPU spends heavily on flexibility and sophisticated control. A GPU spends more heavily on parallel arithmetic and the machinery required to feed it. A neural-network accelerator may devote enormous area to matrix computation and local movement of <span class="term" tabindex="0" data-tooltip="The learned numbers of a neural network, read over and over during inference. Moving them is often the bottleneck.">weights</span> and <span class="term" tabindex="0" data-tooltip="The intermediate values a neural network produces as data flows through it. They must be stored and moved between operations.">activations</span>. A network-switch ASIC is organized around moving and classifying packets as fast as the incoming wires can deliver them. Each is a different physical answer to the question: **what work matters, and what arrangement of resources performs it best?**

---

## From a Desired Factory to a Physical Chip

So far, we have described a chip as a system: what jobs must be performed and how information should flow between them. But a description of the desired factory is not yet a manufacturable object.

The architectural idea must eventually become transistors and wires placed on a finite piece of <span class="term" tabindex="0" data-tooltip="The semiconductor material a chip is built on. “Silicon” is also used loosely for the finished chip itself.">silicon</span>. The intended behavior must be expressed precisely. That behavior must be converted into logic structures. Those structures must be assigned physical locations and connected with real wires. The completed geometry must obey manufacturing constraints and must still satisfy the required speed, power, area, and reliability targets.

This translation is the purpose of **electronic design automation, or EDA**.

EDA is not one program that “designs the chip.” It is a sequence of representations, transformations, analyses, and corrections that gradually turns an intended information-processing system into a physical pattern a <span class="term" tabindex="0" data-tooltip="The manufacturing plant that turns a finished chip design into physical silicon. Not the information factory on the chip — the plant that fabricates the chip.">foundry</span> can manufacture.

The flow exists because no single description can be simultaneously convenient for reasoning about product goals, precise enough to define every clock cycle, detailed enough to place billions of transistors, and fast enough to analyze repeatedly. Instead, engineers move through a ladder of representations:

> Desired behavior → architecture → cycle-by-cycle design → <span class="term" tabindex="0" data-tooltip="Register-transfer level: an executable description of what is stored in registers and how those values change at the next clock edge. Looks a bit like software; means physical circuitry.">register-transfer level (RTL)</span> → gates → <span class="term" tabindex="0" data-tooltip="The finished geometry of the chip: the shapes of transistors, wires, and vias that a foundry can manufacture.">physical layout</span> → silicon

Each step answers questions the previous representation could not answer. Each step also introduces new facts and exposes new ways the design can fail.

---

## The Complete EDA Journey in One Pass

The industry usually splits this ladder into two shops.

<span class="term" tabindex="0" data-tooltip="The logical side of EDA: specifying and checking what the machine should do, as symbols with no coordinates, from the product contract through RTL and verification, ending at a synthesized gate-level netlist.">Frontend</span> is the **logical** argument: what the factory should do, written as symbols that have no physical location yet. It runs from the product contract through architecture, <span class="term" tabindex="0" data-tooltip="The clock-by-clock internal organization of each block: pipelines, queues, handshakes, and what state survives from one tick to the next."><strong>microarchitecture</strong></span>, <span class="term" tabindex="0" data-tooltip="Register-transfer level: an executable description of what is stored in registers and how those values change at the next clock edge."><strong>RTL</strong></span>, and <span class="term" tabindex="0" data-tooltip="Trying to break the proposed RTL before anyone manufactures it, by simulation, assertions, coverage, and proof."><strong>verification</strong></span>. It ends at <span class="term" tabindex="0" data-tooltip="Converting an RTL description into a gate-level netlist: a list of real logic cells from a manufacturing library and the connections among them. Still a logical graph — no coordinates yet.">synthesis</span>: converting that RTL into a <span class="term" tabindex="0" data-tooltip="A list of logic cells and the connections among them. The lowest symbolic form of the chip: named gates, still with no physical locations.">gate-level netlist</span> — a list of real logic cells and the connections among them, still with no coordinates on the die. That <span class="term" tabindex="0" data-tooltip="A list of logic cells and the connections among them. The lowest symbolic form of the chip, still with no physical locations."><strong>netlist</strong></span> is the lowest symbolic form of the machine.

<span class="term" tabindex="0" data-tooltip="The physical side of EDA: turning a gate-level netlist into real geometry — floorplan, place, clocks, routes, extraction, signoff — then taping the layout out to the foundry.">Backend</span> is the **physical** argument: mapping that symbolic netlist onto real components, wires, and coordinates, then proving the geometry can be manufactured and will still meet its timing, power, and area targets.

Synthesis sits on the fence. It still produces a logical graph, but it is the first step that picks real cells from a <span class="term" tabindex="0" data-tooltip="Also called a technology library: the catalog of gates and other cells the chosen manufacturing process can actually build, each with known size, speed, and power. Synthesis may only use what is in this catalog.">manufacturing library</span> — the catalog of parts the chosen process can actually build, each with known size, speed, and power. <span class="term" tabindex="0" data-tooltip="Extra circuitry whose job is not the user's workload, but making manufacturing defects controllable and observable when the finished chip is tested.">Design-for-test</span>, or <span class="term" tabindex="0" data-tooltip="Design for test: extra circuitry whose job is not the user's workload, but making manufacturing defects controllable and observable."><strong>DFT</strong></span>, is extra circuitry for finding those defects. It is planned in the frontend and then stitched into the netlist, after which it travels with the design through the backend. <span class="term" tabindex="0" data-tooltip="Freezing the accepted layout and sending it to the foundry for manufacturing. The name survives from when the data was written to magnetic tape.">Tape-out</span> is the last backend milestone: freeze the layout and hand it to the foundry. <span class="term" tabindex="0" data-tooltip="The careful first experiments on newly arrived silicon: power, clocks, reset, a known register, one subsystem at a time. The goal is a live, controllable chip.">Bring-up</span> is the careful first power-on of the real chip. <span class="term" tabindex="0" data-tooltip="Comparing the physical system with the original product contract: throughput, latency, power, correctness, and reliability in the real environment.">Validation</span> asks whether that chip fulfills the original contract. Both happen after silicon exists; they are not EDA steps so much as the verdict on the whole argument.

Each step below is the same job in two languages: what the chip people do, and what a factory would be doing.

**Frontend — the logical factory**

**1. Product contract.** Write the externally meaningful requirements: which workloads, how much <span class="term" tabindex="0" data-tooltip="Useful work finished per second. Tokens, packets, frames, or requests — not how fast the clock rings.">throughput</span>, how much <span class="term" tabindex="0" data-tooltip="How long one job takes from arrival to result.">latency</span>, how much power, how much cost, which <span class="term" tabindex="0" data-tooltip="The foundry recipe and feature size used to fabricate the chip. It determines which cells exist and how small, fast, and leaky they are.">manufacturing process</span>. No gates yet. *Factory: write the customer order — what to ship, how many per day, at what quality and price — before anyone draws the plant.*

**2. <span class="term" tabindex="0" data-tooltip="The large-scale choice of what machinery exists and how work moves among it: a hypothesis about flow and bottlenecks, before clock-by-clock detail.">Architecture</span>.** Choose the major pieces of machinery and how work moves among them: how much compute, memory, communication, and control, and which bottleneck the design is meant to kill. *Factory: decide which departments exist, how large each is, where the warehouses sit, and which roads connect them. Still a site plan, not a construction drawing.*

**3. Microarchitecture.** Open each architectural box and specify it <span class="term" tabindex="0" data-tooltip="One tick of the clock: the coordinated step in which registers capture new values. The factory's shift-bell interval.">clock cycle</span> by clock cycle: <span class="term" tabindex="0" data-tooltip="Lines of stations that each finish one piece of the work in one clock tick, with several pieces of work in flight at once."><strong>pipelines</strong></span>, queues, <span class="term" tabindex="0" data-tooltip="Contracts between blocks about when data may transfer. The usual form is a valid-and-ready handshake."><strong>handshakes</strong></span>, what state survives from one tick to the next. *Factory: write the shift-by-shift work instructions for each department — who does what between bells, where unfinished work waits, what happens if the next station is not ready.*

**4. RTL.** <span class="term" tabindex="0" data-tooltip="Register-transfer level: an executable description of what is stored in registers and how those values change at the next clock edge. Looks a bit like software; means physical circuitry.">Register-transfer level</span> expresses that machine in a <span class="term" tabindex="0" data-tooltip="A language for describing hardware that will physically exist, not software a processor will execute. Verilog and SystemVerilog are the usual examples.">hardware-description language</span>. *Factory: the official construction drawings. Still paper, but exact enough that a contractor could build from them.*

**5. Verification.** Try to break the proposed RTL before anyone manufactures it. A <span class="term" tabindex="0" data-tooltip="An artificial environment around the RTL that supplies inputs, observes outputs, and checks behavior against the specification.">testbench</span> supplies fake traffic; a <span class="term" tabindex="0" data-tooltip="An independent, usually software, calculation of the correct result, kept separate from the RTL so it does not copy the same bug.">reference model</span> says what should have happened; <span class="term" tabindex="0" data-tooltip="A rule that must always hold — a queue must never overflow, a response cannot appear without a request.">assertions</span> watch for violations; <span class="term" tabindex="0" data-tooltip="A record of where tests have actually looked: which code ran, and which specification situations occurred.">coverage</span> records where you have and have not looked. *Factory: run the paper plant with fake orders and try to make it fail — jammed conveyors, late deliveries, two departments claiming the same crate — and keep a checklist of situations you have actually tried.*

**6. Synthesis.** Convert RTL into a <span class="term" tabindex="0" data-tooltip="A list of actual logic cells from the manufacturing library and the connections among them. The lowest symbolic form of the chip: named gates, still no coordinates.">gate-level netlist</span> by picking cells from a <span class="term" tabindex="0" data-tooltip="The catalog of real cells the chosen manufacturing process can build, each with known size, speed, and power.">technology library</span>. *Factory: go to the equipment catalog and choose actual machines that implement the drawings — a small cheap press, or a larger faster one — without yet deciding which bay each machine occupies.*

**The handoff**

**7. Design for test.** Add <span class="term" tabindex="0" data-tooltip="Extra circuitry whose job is not the user's workload, but making manufacturing defects controllable and observable when the finished chip is tested.">DFT</span> structures — especially <span class="term" tabindex="0" data-tooltip="A test-mode wiring of registers into a long shift register so a factory tester can load internal state, let the logic run, and read the result back out.">scan chains</span> — so a manufactured copy can be probed for physical defects. *Factory: install inspection hatches and test fixtures so QA can force every station into a known state and read what it did, instead of only watching what leaves the loading dock.*

**Backend — the physical factory**

**8. <span class="term" tabindex="0" data-tooltip="Drawing the large-scale geography of the die: where the big blocks sit, where power and I/O enter, where heavy traffic will run.">Floorplanning</span>.** Draw the large-scale geography: <span class="term" tabindex="0" data-tooltip="The dimensions of the piece of silicon one chip occupies. Larger dies hold more machinery, cost more, and make wires longer.">die size</span>, where the big blocks sit, where power and <span class="term" tabindex="0" data-tooltip="Input/output: the chip's connections to the outside world — the loading docks where signals enter and leave.">I/O</span> enter, where the heavy traffic will run. *Factory: the site plan. Place the giant machines first, decide where trucks arrive, and reserve corridors for power and roads before arranging the small workstations.*

**9. <span class="term" tabindex="0" data-tooltip="Assigning every standard cell a legal location on the die.">Placement</span>.** Assign every <span class="term" tabindex="0" data-tooltip="A tiny predesigned physical implementation of a common logic function — an inverter, NAND gate, or flip-flop — with standardized height so they pack into rows like bricks.">standard cell</span> a legal location, trading wire length against timing, <span class="term" tabindex="0" data-tooltip="Too many connections competing for the same scarce wiring tracks, like too many trucks on one corridor."><strong>congestion</strong></span>, and heat. *Factory: give every small workstation a bay on the floor. Connected stations should be neighbors; a <span class="term" tabindex="0" data-tooltip="A delivery that cannot afford a long walk: the slowest chain of logic that must finish in one clock cycle.">timing-critical path</span> is a delivery that cannot afford a long walk.*

**10. <span class="term" tabindex="0" data-tooltip="Building the network of wires and buffers that delivers the clock edge from one source to millions of registers with acceptable arrival times, sharpness, and power.">Clock-tree synthesis</span>.** Build the buffered network that delivers the same <span class="term" tabindex="0" data-tooltip="One tick of the clock: the instant registers capture new values.">clock edge</span> to millions of registers with controlled <span class="term" tabindex="0" data-tooltip="The difference in when the same clock edge arrives at different registers. Uncontrolled skew steals time from data.">skew</span>. *Factory: install the shift-bell wiring. One bell, heard everywhere at almost the same instant; if one wing hears it late, that wing's deadline has silently moved.*

**11. <span class="term" tabindex="0" data-tooltip="Turning every remaining logical connection into exact metal geometry.">Routing</span>.** Turn every remaining logical connection into exact metal and <span class="term" tabindex="0" data-tooltip="A small vertical connector that moves a signal from one metal layer to another, like an elevator between floors of wiring.">vias</span>. *Factory: pour the actual roads and hang the conveyors. The drawings said A connects to B; routing decides the exact path, which overpass, which tunnel.*

**12. Extraction and timing.** Calculate the real <span class="term" tabindex="0" data-tooltip="How much a wire opposes current. Long, thin wires have more resistance, which drops voltage and slows signals.">resistance</span> and capacitance of those wires — the <span class="term" tabindex="0" data-tooltip="The unwanted but real electrical properties of finished wires: resistance, capacitance, and coupling to neighbors. Ideal netlist connections do not have them.">parasitics</span> — then run <span class="term" tabindex="0" data-tooltip="Static timing analysis: checking whether data arrives at registers in time across huge numbers of paths, without running every possible program.">STA</span> to ask whether signals still meet their deadlines. *Factory: walk the finished roads with a stopwatch and an electrician. The sketch said the trip was short; the real corridor has hills, narrows, and traffic beside it.*

**13. Physical <span class="term" tabindex="0" data-tooltip="The body of evidence that the physical design is finished: manufacturable, connected as intended, timed, powered, and reliable enough to tape out.">signoff</span>.** Collect the evidence that the layout is manufacturable (<span class="term" tabindex="0" data-tooltip="Design-rule checking: the finished shapes obey the foundry's geometric rules — widths, spacings, vias, density.">DRC</span>), is still the intended circuit (<span class="term" tabindex="0" data-tooltip="Layout-versus-schematic: the shapes still form the intended connections. No missing vias, no accidental shorts.">LVS</span>), meets timing, and will not collapse under power or long-term stress. *Factory: building inspector, electrician, and safety audit. Legal to construct, wired as drawn, able to run at the promised pace, and not going to burn down over a ten-year shift.*

**14. Tape-out.** Freeze the accepted layout and send it to the <span class="term" tabindex="0" data-tooltip="The manufacturing plant that turns a finished layout into physical silicon.">foundry</span>, which builds many copies on a <span class="term" tabindex="0" data-tooltip="A round slice of silicon on which many copies of the chip are manufactured at once, later cut into individual dies.">wafer</span> and cuts them into <span class="term" tabindex="0" data-tooltip="One rectangular piece of silicon cut from the wafer. The physical chip, before it is packaged.">dies</span>. *Factory: freeze the blueprints and hand them to the construction company. They pour the building, cut it from the site, and put it in a shell. You do not get to move a wall after the concrete is set.*

**After silicon**

**15. Bring-up and validation.** <span class="term" tabindex="0" data-tooltip="The careful first experiments on newly arrived silicon: power, clocks, reset, a known register, one subsystem at a time. The goal is a live, controllable chip.">Bring-up</span> asks whether the chip is alive. <span class="term" tabindex="0" data-tooltip="Comparing the physical system with the original product contract: throughput, latency, power, correctness, and reliability in the real environment.">Validation</span> asks whether it fulfills the original contract. *Factory: first day on the new floor. Turn on the lights, then one line, then a full shift — and only then ask whether you are actually shipping what the customer ordered.*

That sounds like a linear assembly line, but it is not. When a later stage uncovers a contradiction, work loops backward to the earliest decision that must change. To understand why those loops occur, we need to walk through the representations one at a time.

---

## Start with the Product Contract

*Factory: write the customer order before anyone draws the plant.*

The process begins before anyone writes RTL or places a gate. It begins by deciding what the product must accomplish.

For an <span class="term" tabindex="0" data-tooltip="A chip built to run already-trained neural networks quickly and cheaply, rather than to train them.">inference accelerator</span>, the requirements might specify:

- which neural-network models and operations it must support;
- how many <span class="term" tabindex="0" data-tooltip="The pieces of text a language model reads or writes. Throughput here is often measured in tokens per second.">tokens</span> or requests it must process per second;
- the acceptable latency for <span class="term" tabindex="0" data-tooltip="Prefill: ingesting the prompt. Decode: generating the next token. Two phases of running a language model, with different traffic through the factory.">prefill and decode</span>;
- which <span class="term" tabindex="0" data-tooltip="How numbers are represented in bits: integer, floating-point, and reduced-precision formats used in neural networks.">numerical formats</span> it must handle;
- how much external memory capacity and bandwidth it needs;
- how much power one chip, server, or rack may consume;
- how several chips must communicate;
- how much the product may cost;
- which manufacturing process and <span class="term" tabindex="0" data-tooltip="The technologies that house a die and connect it to memory, boards, and other chips. In advanced products this is part of the architecture, not a box around a finished chip.">packaging</span> technologies are available.

These requirements form the externally meaningful contract. They describe success from the perspective of whoever will use or sell the product.

At this stage, choosing the location of a particular <span class="term" tabindex="0" data-tooltip="A basic logic cell whose output is 0 only when every input is 1. One of the standard bricks from which larger logic is built.">NAND gate</span> would make no sense. The first unresolved problem is much larger:

> A performance target tells us what outcome we want, but it does not tell us what machine could produce it.

That problem motivates architecture.

---

## Architecture: Choose the Shape of the Factory

*Factory: decide which departments exist, how large each is, and how work flows among them. Still a site plan.*

Architecture decides which major pieces of machinery should exist and how work should move among them.

An inference-chip architecture might contain:

- arrays of matrix-multiplication engines;
- local on-chip memories;
- controllers that issue and schedule work;
- a network connecting compute and memory blocks;
- interfaces to external <span class="term" tabindex="0" data-tooltip="Stacked memory sitting very close to the chip, used when ordinary off-chip memory cannot feed the factory fast enough. Often shortened to HBM.">high-bandwidth memory (HBM)</span>;
- chip-to-chip communication links;
- small general-purpose processors for irregular control work;
- <span class="term" tabindex="0" data-tooltip="Machinery that keeps multiple blocks or chips in agreement about when shared work may proceed.">synchronization</span>, error-handling, and security mechanisms.

The product requirement may have said, “Produce this many tokens per second within this power budget.” Architecture proposes an answer such as, “Build this many compute arrays, give each one this much nearby memory, connect them with this network, and supply them with this much external bandwidth.”

Architects use <span class="term" tabindex="0" data-tooltip="Recorded sequences of real or realistic work, used to test an architecture in a performance model before the hardware exists.">workload traces</span> and <span class="term" tabindex="0" data-tooltip="Simplified simulations of how long work takes as it moves through the proposed factory, used before the hardware exists.">performance models</span> to test that proposal before the exact hardware exists. A model may approximate the time required to:

1. load weights from external memory;
2. move them into local storage;
3. feed them into matrix engines;
4. perform the arithmetic;
5. move <span class="term" tabindex="0" data-tooltip="Incomplete answers that must wait in storage until the rest of a larger operation finishes.">partial results</span> into the next operation.

The model asks system-level questions:

- Are there enough compute units?
- Can memory feed them quickly enough?
- Will the internal network become congested?
- Does the workload reuse data enough to justify more local memory?
- Would doubling arithmetic capacity help, or would it merely create more idle machinery waiting for data?
- Do latency-sensitive and throughput-sensitive workloads require different resource balances?

This is the first place where the factory viewpoint becomes **operational**. Architecture is not a catalog of parts. **It is a hypothesis about flow and bottlenecks.**

Eventually, that hypothesis becomes a <span class="term" tabindex="0" data-tooltip="A drawing of the major boxes — compute, memory, controllers, interfaces — and the connections among them. Purpose without clock-by-clock behavior.">block diagram</span>. But a box labeled “matrix engine” or “memory controller” is still ambiguous. It tells us the block's purpose without defining its exact behavior.

That remaining ambiguity motivates microarchitecture.

---

## Microarchitecture: Turn Each Department into a Clock-by-Clock Machine

*Factory: write the shift-by-shift work instructions for each department — what happens between bells, and where unfinished work waits.*

Microarchitecture opens each architectural box and specifies the machinery inside it.

If the architecture calls for a matrix engine, its microarchitecture must answer questions such as:

- How many multipliers and adders are present?
- How are they arranged?
- How many values enter during each clock cycle?
- Where do <span class="term" tabindex="0" data-tooltip="Running totals kept during a longer calculation, such as a matrix multiply, until the final result is ready.">partial sums</span> wait?
- How many <span class="term" tabindex="0" data-tooltip="The stations of a pipeline: each finishes one piece of the work in one clock tick.">pipeline stages</span> are used?
- Can several operations be in flight simultaneously?
- What happens if an input arrives late?
- What happens if the next block cannot accept the output?
- How does the engine know that an operation has completed?
- What state must survive from one cycle to the next?

The clock divides the machine's behavior into coordinated steps. If a large calculation cannot complete within one <span class="term" tabindex="0" data-tooltip="The time between two clock edges — one ring of the shift bell. All combinational work between registers must finish inside it.">clock period</span>, the designer can split it into a <span class="term" tabindex="0" data-tooltip="A line of stages that each finish one piece of the work in one clock tick, with several pieces of work in flight at once."><strong>pipeline</strong></span> — a line of stages, each finishing one piece of the work in one clock tick, with several pieces of work in flight at once:

1. Read the <span class="term" tabindex="0" data-tooltip="The input values an operation consumes, such as the two numbers being multiplied.">operands</span>.
2. Multiply them.
3. Add the product to a partial sum.
4. Write the completed result.

Registers are inserted between those stages. Each register preserves a set of bits from one clock edge to the next, allowing different pieces of work to occupy different pipeline stages at the same time.

Microarchitecture therefore defines two fundamental things:

1. **State:** the information the machine remembers.
2. **Transitions:** how current state and current inputs determine the next state.

In compact form:

$$
(\text{current state}, \text{current inputs})
\longrightarrow
(\text{next state}, \text{outputs})
$$

It also defines contracts between blocks. One common contract is a <span class="term" tabindex="0" data-tooltip="A two-signal contract between blocks: the sender says data is valid, the receiver says it is ready, and a transfer happens on a clock edge only when both are true. Prevents dropping, duplicating, or overwriting data."><strong>valid-and-ready handshake</strong></span>. A sender marks its data as <span class="term" tabindex="0" data-tooltip="The sender's half of a handshake: this word is a real item, not leftover junk on the wires."><strong>valid</strong></span> when it has a real item available. A receiver marks itself <span class="term" tabindex="0" data-tooltip="The receiver's half of a handshake: I have space, so a transfer is allowed this tick."><strong>ready</strong></span> when it has space. The transfer occurs on a clock edge when both conditions are true.

This small rule solves a real coordination problem: one block may produce data faster than the next block can consume it. If the two blocks disagree about when a transfer occurred, they can duplicate, drop, or overwrite information.

The microarchitecture specification therefore includes pipeline stages, registers, queues, state machines, interfaces, timing expectations, reset behavior, and exceptional cases. It describes the intended machine precisely enough for engineers to implement it—but it is still usually written partly in prose, diagrams, tables, and timing sketches.

Manufacturing tools cannot build a prose specification. The behavior must be expressed in an executable and formally structured description.

That motivates RTL.

---

## RTL: Express the Intended Machine as Hardware

*Factory: the official construction drawings. Still paper, but exact enough to build from.*

RTL means **register-transfer level** — an executable description of hardware, not a program a processor will run. The name describes its central perspective:

> Specify what information is stored in registers and what transformations and transfers determine their values at the next clock edge.

RTL is commonly written in <span class="term" tabindex="0" data-tooltip="The most common hardware-description language used to write RTL. Looks a bit like software; means physical circuitry.">SystemVerilog</span> or <span class="term" tabindex="0" data-tooltip="A hardware-description language, closely related to SystemVerilog, used to write RTL.">Verilog</span>, another hardware-description language in the same family. A simplified description might say:

```text
on every rising clock edge:
    if reset:
        counter becomes 0
    else if increment:
        counter becomes counter + 1
```

This resembles software, but it has a different meaning. A <span class="term" tabindex="0" data-tooltip="The 0-to-1 transition of the clock. The usual instant at which registers capture new values."><strong>rising clock edge</strong></span> is the 0-to-1 tick that tells registers to capture their new values.

Ordinary software describes instructions that an existing processor will execute. **RTL describes machinery that will physically exist**: a register holding the counter, an adder producing the next value, <span class="term" tabindex="0" data-tooltip="Logic that chooses one of several possible next values, such as keep the old count or take count-plus-one. Usually built from multiplexers.">selection logic</span> choosing whether to preserve or update the value, and wires carrying the relevant signals.

RTL modules also operate <span class="term" tabindex="0" data-tooltip="At the same time. Unlike ordinary software, RTL modules are not taking turns on one processor. They are separate circuits that exist and switch together.">concurrently</span>. A queue controller, network router, memory interface, multiplier, and error monitor do not wait for one another's source-code lines to execute. They are simultaneously existing circuits whose signals continually interact.

The RTL engineer repeatedly asks:

> What state exists now, and what should every piece of that state become at the next relevant clock edge?

Once the microarchitecture has been encoded as RTL, we possess a precise candidate implementation. But precision does not imply correctness. A forgotten condition may drop data only when several queues fill simultaneously. A scheduler may <span class="term" tabindex="0" data-tooltip="Never granting a requester access because others always win arbitration.">starve</span> one requester. A pipeline may attach the wrong identifier to a result. Reset may leave one register in an <span class="term" tabindex="0" data-tooltip="A register whose value after reset is not guaranteed. Later logic that assumes a known 0 or 1 can misbehave.">unknown state</span>.

A mistake in software can often be patched after deployment. **A mistake frozen into silicon can require months and millions of dollars to replace.** We therefore need to attack the proposed behavior before manufacturing it.

That motivates verification.

---

## Verification: Try to Break the Proposed Machine

*Factory: run the paper plant with fake orders and try to make it fail before you pour concrete.*

<span class="term" tabindex="0" data-tooltip="Checking that the RTL does what the specification says, under the situations you can simulate or prove, before anyone manufactures the chip.">Functional verification</span> asks:

> Does the RTL obey its specification under every relevant situation we can construct or prove?

The RTL being examined is often called the <span class="term" tabindex="0" data-tooltip="The piece of RTL being examined. The testbench is the fake world built around it.">design under test</span>. A <span class="term" tabindex="0" data-tooltip="An artificial environment around the RTL that supplies inputs, observes outputs, and checks behavior against the specification.">testbench</span> surrounds it with an artificial environment that supplies inputs, observes outputs, and checks behavior.

The basic procedure is simple:

1. Produce an input or sequence of events.
2. Feed it into the simulated RTL.
3. Observe how the design responds.
4. Independently calculate what the correct response should be.
5. Compare the actual and expected behavior.
6. Investigate any disagreement.

The difficulty is the size of the behavioral space. A queue may work when traffic is light but fail when it is full. A reset may work while the design is idle but fail in the middle of an operation. Two subsystems may work independently but <span class="term" tabindex="0" data-tooltip="Two or more blocks each waiting for the other, so no work moves. A jammed factory.">deadlock</span> when both apply <span class="term" tabindex="0" data-tooltip="A downstream block refusing new work because it is not ready. Upstream must wait, or the factory drops, duplicates, or overwrites data.">backpressure</span> at once.

### Generating situations worth testing

A **<span class="term" tabindex="0" data-tooltip="A hand-written test that creates one known situation and checks one known outcome. Easy to understand; cannot cover every interaction in a large chip.">directed test</span>** intentionally creates one known situation: send a particular operation, <span class="term" tabindex="0" data-tooltip="Intentionally holding back a block or a transfer for some number of cycles, often to test whether the factory recovers cleanly.">stall</span> its destination for four cycles, release the stall, and verify that exactly one correct result appears.

Directed tests are easy to understand and excellent for requirements, <span class="term" tabindex="0" data-tooltip="A saved suite of tests rerun after every change, to catch old bugs coming back.">regressions</span>, and known <span class="term" tabindex="0" data-tooltip="Rare or extreme situations — a queue that is exactly full, a reset in the middle of an operation — where bugs like to hide.">corner cases</span>. But engineers cannot manually enumerate every strange interaction in a large design.

**<span class="term" tabindex="0" data-tooltip="Generating many legal random combinations of operations, delays, and pressure, instead of writing every test by hand. Constraints keep the random activity inside the system's rules.">Constrained-random testing</span>** explores a wider space by generating random combinations of legal operations, delays, queue pressure, resets, and interface behavior. “Constrained” means that the generated activity follows the system's rules unless the test intentionally targets illegal input.

The goal is not randomness for its own sake. It is to discover interactions the human author did not think to write explicitly.

### Deciding what the answer should have been

A **<span class="term" tabindex="0" data-tooltip="An independent, usually software, calculation of the correct result, kept separate from the RTL so it does not copy the same bug.">reference model</span>** computes the intended result at a higher level of abstraction. A **<span class="term" tabindex="0" data-tooltip="A checker that records expected results from the reference model and compares them with what the RTL actually produced.">scoreboard</span>** records the results that should eventually appear and compares them with the RTL's actual outputs.

For a matrix engine, the reference model might calculate a matrix product using ordinary software. The scoreboard then verifies that the hardware produces the same values in the correct order and associates them with the correct requests.

This separation is important. Reimplementing the hardware's exact internal procedure in the checker can reproduce the same mistake twice. A useful reference model expresses the specification independently.

### Stating rules that must always hold

An <span class="term" tabindex="0" data-tooltip="A rule that must always hold — a queue must never overflow, a response cannot appear without a request."><strong>assertion</strong></span> expresses a required property:

- A queue's <span class="term" tabindex="0" data-tooltip="How many items a queue or buffer currently holds."><strong>occupancy</strong></span> — how many items it currently holds — must never exceed its capacity.
- A response cannot appear unless some request caused it.
- An accepted request must eventually receive exactly one response.
- Two agents cannot simultaneously own an exclusive resource.

Assertions watch for violations during <span class="term" tabindex="0" data-tooltip="Running a software model of the RTL over time to see how it behaves, without manufacturing anything.">simulation</span>. <span class="term" tabindex="0" data-tooltip="Using mathematical search or proof to ask whether a property can ever be violated, rather than waiting for a simulation to stumble on the failing case.">Formal verification</span> tools can also explore whether certain properties are mathematically reachable, rather than waiting for a test to happen upon a failing input sequence.

Formal proof is especially useful when the state space can be constrained enough for exhaustive reasoning. Simulation and formal methods complement one another: simulation can run rich realistic workloads, while formal analysis can prove targeted properties across all behaviors represented by its model.

### Measuring where we have looked

A million passing tests are weak evidence if they repeat essentially the same easy situation.

Coverage asks which portions of the implementation and specification have actually been exercised.

**<span class="term" tabindex="0" data-tooltip="A record of which lines, branches, and states in the RTL the tests actually exercised. Passing tests that never touch a path are weak evidence for that path.">Code coverage</span>** records whether RTL lines, branches, states, and signal transitions occurred. It can reveal logic that the tests never activated.

**<span class="term" tabindex="0" data-tooltip="A record of whether meaningful specification scenarios occurred — not merely whether lines of code ran.">Functional coverage</span>** begins from meaningful scenarios in the specification. It may ask whether every command occurred while a queue was empty, partially full, and completely full, or whether each operation type was tested under every relevant form of backpressure.

**Coverage does not prove correctness.** It identifies where the verification effort has and has not gathered evidence.

### Debugging failures without being misled by their symptoms

When a test fails, <span class="term" tabindex="0" data-tooltip="Textual records of events during a test. Useful, but waveforms are usually the microscope for the actual signals.">logs</span> provide textual events and <span class="term" tabindex="0" data-tooltip="A plot of how signals change over simulated time. The usual microscope for debugging a failing test.">waveforms</span> record how signals changed over simulated time.

The first reported failure is not necessarily the original cause. A queue may drop one request, after which thousands of cycles pass before a scoreboard times out waiting for the missing response. The <span class="term" tabindex="0" data-tooltip="A checker giving up after waiting too long for something that should have happened. Often a symptom of an earlier dropped request, not the original bug.">timeout</span> is the visible symptom; the incorrect queue transition is the causal failure.

Debugging therefore works backward:

1. Identify the earliest meaningful divergence between expected and actual behavior.
2. Determine which state or transfer first became incorrect.
3. Trace that value back through the logic that produced it.
4. Reduce the failure to the smallest reproducible situation.
5. Decide whether the fault belongs to the RTL, the testbench, the specification, or the surrounding infrastructure.

Large regressions make this a <span class="term" tabindex="0" data-tooltip="Sorting a pile of failures into distinct root causes so the team does not debug the same bug four thousand times.">triage</span> problem as well. Four thousand failed tests may represent one broken reset condition followed by four thousand secondary symptoms. The useful unit of work is not the number of failures; it is the number of distinct <span class="term" tabindex="0" data-tooltip="The distinct original bugs, as opposed to the thousands of secondary failures one bug can cause.">root causes</span>.

Verification continues throughout the project. Passing RTL simulation merely provides enough confidence to take the next representational step.

---

## Synthesis: Turn Described Behavior into Available Gates

*Factory: go to the equipment catalog and choose actual machines that implement the drawings, without yet assigning each one a bay.*

RTL may say “add these two values,” but a manufactured chip needs a particular collection of transistors and wires that performs the addition.

<span class="term" tabindex="0" data-tooltip="Converting RTL into a gate-level netlist by choosing real cells from a manufacturing library and restructuring the logic to meet timing, area, and power.">Logic synthesis</span> converts RTL into a **<span class="term" tabindex="0" data-tooltip="A list of actual logic cells from the manufacturing library and the connections among them. Named gates, still no coordinates.">gate-level netlist</span>**. The netlist lists physical building blocks and their logical connections. Conceptually, it says:

```text
flip-flop 17 output → NAND gate 5 input
NAND gate 5 output → inverter 12 input
inverter 12 output → flip-flop 23 input
```

The available components come from a technology library associated with the manufacturing process. That library contains predesigned cells such as <span class="term" tabindex="0" data-tooltip="Logic cells that turn a 1 into a 0 and a 0 into a 1. Also used to strengthen or clean up a signal.">inverters</span>, <span class="term" tabindex="0" data-tooltip="Basic logic cells whose output is 0 only when every input is 1.">NAND gates</span>, <span class="term" tabindex="0" data-tooltip="Logic cells that select one of several inputs to pass through, like a switchyard choosing which incoming road continues.">multiplexers</span>, adders, and <span class="term" tabindex="0" data-tooltip="The standard-cell version of a register: a small memory that captures its input when the clock ticks and holds that value until the next tick.">flip-flops</span>.

There may be several versions of the same logical operation:

- a small cell that consumes little area and power but changes its output relatively slowly;
- a larger cell that drives more <span class="term" tabindex="0" data-tooltip="How hard a signal is to drive: the capacitance of the wires and destinations it must fill. A bigger load makes the edge slower and sloppier.">electrical load</span> and changes its output faster;
- cells with different leakage and switching characteristics;
- specialized cells for clocks, <span class="term" tabindex="0" data-tooltip="Circuitry that translates a signal between regions that run at different voltages.">level conversion</span>, <span class="term" tabindex="0" data-tooltip="Circuitry that electrically disconnects a region that has been powered down, so it does not corrupt neighbors that are still on.">isolation</span>, or other physical needs.

Synthesis chooses cells and restructures logic while balancing three major goals:

- **Timing:** can signals reach their destinations before their deadlines?
- **Area:** how much silicon will the chosen cells occupy?
- **Power:** how much energy will switching and leakage consume?

The tool needs constraints to know what counts as acceptable. A one-<span class="term" tabindex="0" data-tooltip="One billionth of a second. A typical modern clock period is a small number of nanoseconds.">nanosecond</span> clock period — a billionth of a second — tells it that the <span class="term" tabindex="0" data-tooltip="Logic with no memory of its own: outputs depend only on current inputs. Must finish between one clock tick and the next.">combinational work</span> between registers must complete within the usable portion of that interval.

If the requested operation cannot meet the deadline, synthesis may choose faster cells or <span class="term" tabindex="0" data-tooltip="Change how the function is built from gates — not just swap a cell — to shorten a path that will not close.">restructure the logic</span>. But it cannot rescue every design. The real fix may be another pipeline stage, a lower <span class="term" tabindex="0" data-tooltip="How many times per second the clock ticks. Lowering it is a way to make timing legal that also lowers performance.">clock frequency</span>, or an altered microarchitecture.

After synthesis, <span class="term" tabindex="0" data-tooltip="A check that two representations of the same machine — usually RTL and the synthesized gates — still mean the same logical behavior.">equivalence checking</span> asks whether the chosen gate network preserves the RTL's logical behavior. We have changed representations; we need evidence that the translation did not change the intended machine.

The result is no longer an abstract arithmetic operation. It is a network of particular cells and connections. Those cells do not yet have physical locations, however, and their connections do not yet have real wires.

Before arranging them, the design also needs a way to expose manufacturing defects hidden inside the eventual chip.

---

## Design for Test: Make Physical Defects Controllable and Observable

*Factory: install inspection hatches and test fixtures so QA can force every station into a known state, not only watch what leaves the dock.*

Functional verification asks whether the design is logically correct. It assumes that the manufactured transistors and wires faithfully implement the design.

Reality adds another failure mode: the design can be correct while one <span class="term" tabindex="0" data-tooltip="One manufactured instance of the chip. The design can be correct while this particular copy is defective.">physical copy</span> is defective. A <span class="term" tabindex="0" data-tooltip="A tiny manufacturing defect — a broken wire, a short, a transistor that will not switch — in one physical copy.">microscopic fault</span> might break a wire, short two shapes together, leave a <span class="term" tabindex="0" data-tooltip="An electrical point in the circuit — a wire or a cell pin — that should be a 0 or a 1. A defect can pin it permanently high or low.">node</span> <span class="term" tabindex="0" data-tooltip="A node stuck at 1 or stuck at 0. A classic manufacturing-defect model used when generating factory tests."><strong>permanently high or low</strong></span> (stuck at 1 or 0), or damage part of a <span class="term" tabindex="0" data-tooltip="A dense grid of memory cells, as in an SRAM, rather than a collection of ordinary flip-flops.">memory array</span>.

Testing only the chip's external inputs and outputs may not expose every internal defect. Some internal state is difficult to create through normal operation, and some fault effects are difficult to propagate to an <span class="term" tabindex="0" data-tooltip="A connection that leaves the chip — a loading-dock door. Testers and boards can only see pins unless DFT opens internal hatches.">external pin</span>.

<span class="term" tabindex="0" data-tooltip="Extra circuitry whose job is not the user's workload, but making manufacturing defects controllable and observable at factory test.">Design for test, or DFT</span>, adds structures that make internal circuitry controllable and observable in a <span class="term" tabindex="0" data-tooltip="An operating mode in which DFT structures such as scan chains are active, used in the factory, not by the end user.">manufacturing-test mode</span>.

### Scan chains

A <span class="term" tabindex="0" data-tooltip="A test-mode wiring of registers into a long shift register so a factory tester can load internal state, let the logic run, and read the result back out."><strong>scan chain</strong></span> is a test-mode wiring of registers into a long <span class="term" tabindex="0" data-tooltip="Registers connected so a bit can be shifted from one to the next, like a bucket brigade. Scan chains are shift registers used for manufacturing test.">shift register</span>. In ordinary operation, registers receive values through the functional logic. In <span class="term" tabindex="0" data-tooltip="A test configuration in which registers are wired into shift chains so a factory tester can load and read internal state."><strong>scan mode</strong></span>, many registers can be connected into long shift chains:

```text
external tester → register → register → register → ... → external tester
```

The <span class="term" tabindex="0" data-tooltip="External factory equipment that drives the chip's test pins, shifts scan data in and out, and compares results against a good chip.">tester</span> can then:

1. Shift a chosen internal state into the registers.
2. Allow the <span class="term" tabindex="0" data-tooltip="Logic with no memory of its own: outputs depend only on current inputs. The work that must finish between one clock tick and the next.">combinational logic</span> to operate.
3. Capture the result in registers.
4. Shift that result out.
5. Compare it with the expected value.

This gives the tester direct leverage over internal situations that ordinary software might struggle to create or observe.

<span class="term" tabindex="0" data-tooltip="Software that searches for input patterns a factory tester can use to distinguish a good chip from one with a modeled manufacturing defect. Often shortened to ATPG.">Automatic test-pattern generation (ATPG)</span> then searches for patterns that distinguish a good chip from chips containing <span class="term" tabindex="0" data-tooltip="The defect types test-pattern generation assumes, such as a node stuck high or low, used to search for factory tests.">modeled faults</span>. Memory arrays commonly receive their own <span class="term" tabindex="0" data-tooltip="On-chip machinery, especially for memories, that tests itself rather than relying entirely on an external factory tester. Often shortened to BIST.">built-in self-test (BIST)</span> machinery because their dense, repetitive structure has characteristic failure modes.

DFT is not one isolated event performed after synthesis and forgotten. Test requirements influence RTL and clocking early; <span class="term" tabindex="0" data-tooltip="Registers and cells that can join a scan chain in test mode, in addition to doing their ordinary functional job.">scan-capable</span> cells are introduced around synthesis; scan chains affect placement and routing; and final test patterns depend on the implemented design. It is best understood as a concern that crosses the flow, even though it becomes physically concrete around the <span class="term" tabindex="0" data-tooltip="Described as actual library cells and wires among them, rather than as RTL operations like add these two values.">gate-level</span> design.

Now we possess actual cells, logical connections, and test structures. The next unresolved question is literal:

> Where on the die will all of this machinery go?

That motivates physical implementation.

---

## Physical Implementation: Give the Factory a Geography

*Factory: move from drawings to a real site — distance, corridors, power, and limited floor space now matter.*

Until this point, a connection between two cells was an abstract relationship. It did not specify whether those cells would sit beside one another or on opposite sides of the die.

Physical design introduces distance, shape, obstruction, heat, local power demand, and limited wiring space. The design must be arranged on a real two-dimensional surface with several stacked layers of metal above it.

### Floorplanning: position the largest structures first

*Factory: the site plan — giant machines, truck docks, and power corridors first.*

Floorplanning establishes the chip's large-scale geography. Engineers decide:

- the dimensions of the die and its usable <span class="term" tabindex="0" data-tooltip="The usable interior of the die after space is reserved for I/O, power rings, and other edge structures.">core area</span>;
- where major functional regions belong;
- where large physical blocks will sit;
- where external connections enter and leave;
- how <span class="term" tabindex="0" data-tooltip="The two rails of the electrical supply: power pushes current in; ground is the return path.">power and ground</span> will be distributed;
- where major data flows must travel;
- which regions are likely to become congested or hot.

This is the moment when the earlier architectural block diagram begins acquiring literal distance.

If a compute array repeatedly consumes data from an on-chip memory, placing the two on opposite sides of the die produces longer wires, greater delay, higher movement energy, and more competition for the routing space between them. A logical relationship has become a geographic traffic problem.

#### Standard cells and macros are different kinds of physical building block

Most custom digital logic is constructed from **<span class="term" tabindex="0" data-tooltip="Tiny predesigned physical implementations of common logic functions — inverter, NAND, flip-flop — with standardized height so they pack into rows like bricks.">standard cells</span>**. A <span class="term" tabindex="0" data-tooltip="A tiny predesigned physical implementation of a common logic function — an inverter, NAND gate, or flip-flop — with standardized height so they pack into rows like bricks.">standard cell</span> is a small, predesigned physical implementation of a common logical function: an <span class="term" tabindex="0" data-tooltip="A logic cell that turns a 1 into a 0 and a 0 into a 1. Also used to strengthen or clean up a signal.">inverter</span>, NAND gate, <span class="term" tabindex="0" data-tooltip="A logic cell that selects one of several inputs to pass through, like a switchyard choosing which incoming road continues.">multiplexer</span>, <span class="term" tabindex="0" data-tooltip="The standard-cell version of a register: a small memory that captures its input when the clock ticks and holds that value until the next tick.">flip-flop</span>, <span class="term" tabindex="0" data-tooltip="A cell whose job is to strengthen the clock so it can drive the next stretch of the clock network.">clock buffer</span>, or another modest piece of logic.

The cells have <span class="term" tabindex="0" data-tooltip="Every standard cell in a library is the same height so the cells pack into rows like bricks.">standardized heights</span> so they can be packed into <span class="term" tabindex="0" data-tooltip="The standardized horizontal strips into which standard cells are packed, like bricks in a wall.">rows</span>. Each one comes with known dimensions, <span class="term" tabindex="0" data-tooltip="Where the connection points sit on a cell or macro. Placement and routing have to reach those exact spots.">pin locations</span>, logical behavior, timing characteristics, and power models. Synthesis selects them; placement will later assign each selected instance a position.

A **<span class="term" tabindex="0" data-tooltip="A large block whose internal layout is already frozen. Chip-level tools see its outline, pins, and timing model, but do not rearrange the transistors inside.">hard macro</span>** is different. It is a much larger block whose internal physical implementation is already fixed. The <span class="term" tabindex="0" data-tooltip="The whole-chip view, as opposed to a block implemented and frozen on its own. Top-level tools see macros as opaque shapes.">top-level</span> placement tool sees its outer shape, <span class="term" tabindex="0" data-tooltip="The named connection points on a cell or macro where wires attach.">pins</span>, power connections, timing models, and <span class="term" tabindex="0" data-tooltip="Regions a router may not use, often because a hard macro already occupies those metal layers.">routing obstructions</span>, but it does not break the <span class="term" tabindex="0" data-tooltip="A large block treated as one physical object, usually a hard macro whose internal layout is already frozen.">macro</span> apart and rearrange its internal transistors.

An <span class="term" tabindex="0" data-tooltip="Static random-access memory: the usual on-chip memory block, built as a dense custom array rather than from ordinary flip-flops.">SRAM</span> is the canonical example. Its memory cells and supporting circuits are laid out as an extremely dense, regular custom structure. Building a large memory from ordinary flip-flops would consume far more area and power and would create a routing disaster. <span class="term" tabindex="0" data-tooltip="Tools that generate optimized SRAM macros for a requested capacity and width, instead of assembling a memory from ordinary flip-flops.">Memory compilers</span> therefore generate optimized <span class="term" tabindex="0" data-tooltip="Static random-access memory: the usual on-chip memory block, built as a dense custom array rather than from ordinary flip-flops.">SRAM</span> <span class="term" tabindex="0" data-tooltip="Large blocks treated as one physical object, usually hard macros whose internal layout is already frozen.">macros</span> for requested capacities and widths.

<span class="term" tabindex="0" data-tooltip="Circuitry that deals with continuous voltages rather than clean 0/1 digital levels, often used in PHYs and sensors.">Analog circuits</span> and high-speed physical interfaces are also commonly delivered as hard macros because their behavior depends on carefully controlled transistor geometry and physical relationships.

The word “macro” is sometimes also used for a **<span class="term" tabindex="0" data-tooltip="A logical hierarchical block, such as an RTL processor core, whose final physical layout has not yet been frozen.">soft macro</span>**: a logical hierarchical block, such as an RTL processor core, whose final physical layout has not yet been fixed. In a floorplanning discussion, however, “macro placement” normally refers to the large hard blocks that already have physical dimensions.

#### Why macros are placed before standard cells

Hard macros are the giant machines in the factory. Standard cells are the smaller workstations arranged around them.

Macros must be placed early because:

- they occupy large contiguous regions;
- their pins appear at fixed positions;
- they may block some routing layers;
- thousands of standard cells may communicate with them;
- their locations determine major <span class="term" tabindex="0" data-tooltip="Which blocks talk to which others, and how much. Macro placement largely decides how far that traffic has to travel.">traffic patterns</span>;
- moving one later would invalidate large amounts of surrounding placement and routing.

Even a macro's <span class="term" tabindex="0" data-tooltip="Which way a macro is rotated. Pins on the wrong side can force thousands of wires to travel around the block.">orientation</span> matters. If an SRAM's relevant pins are on its east side but the compute logic consuming its data lies to the west, thousands of wires may have to travel around the block. Rotating the memory could improve one flow while worsening another.

#### Why the chip is not constructed entirely from hard macros

Large fixed blocks are valuable when a function benefits from a highly optimized and reusable physical implementation. But a chip also contains enormous amounts of design-specific logic: queue controllers, arbiters, pipeline registers, <span class="term" tabindex="0" data-tooltip="Logic that produces the sequence of memory addresses a block should visit, like a forklift route through a warehouse.">address generators</span>, <span class="term" tabindex="0" data-tooltip="Logic that translates one conversation format into another so two blocks that speak different languages can still exchange work.">protocol converters</span>, state machines, scheduling logic, error handling, and synchronization.

That logic changes as the product evolves. Standard cells allow synthesis to construct exactly the functions, widths, pipeline depths, and interfaces the current design requires.

If everything had to be selected from a catalog of hard macros, the catalog would need a distinct fixed block for every possible combination of behavior, data width, number of <span class="term" tabindex="0" data-tooltip="The connection points of a block or memory — how many independent conversations it can have at once.">ports</span>, performance target, interface, and physical shape. The system would lose the flexibility required to build a unique chip.

The division of labor is therefore:

- Use hard macros when a large function benefits from a carefully optimized, fixed implementation.
- Use standard cells to construct the flexible custom digital logic that makes this particular chip behave as intended.

The boundary is hierarchical rather than absolute. A team can synthesize and physically implement a digital block from standard cells, freeze that implementation, and then reuse the entire block as a hard macro at the top level. Hierarchy makes enormous designs computationally manageable and gives teams reusable ownership boundaries. Freezing a block too early, however, also makes later changes harder. Designers choose macro boundaries by balancing reuse, predictability, tool capacity, and flexibility.

#### Power planning is part of the geography

The <span class="term" tabindex="0" data-tooltip="The chip's large-scale geography: die size, where the big blocks sit, where power and I/O enter, where heavy traffic will run."><strong>floorplan</strong></span> must also deliver electrical power across the die. Billions of transistors switching draw current through a non-ideal network of metal wires.

Because those wires have resistance, current causes voltage to fall as it travels. This is called **<span class="term" tabindex="0" data-tooltip="Voltage falling as current travels through resistive power wires. A region may receive less voltage than intended, so transistors switch more slowly or incorrectly.">IR drop</span>**. A region expecting a particular supply voltage may momentarily receive less, causing its transistors to switch more slowly or incorrectly.

The power network therefore needs appropriately sized <span class="term" tabindex="0" data-tooltip="The shapes of the on-chip power network: rings around regions, straps across them, and a grid of intersecting rails."><strong>rings, straps, and grids</strong></span>, and connections. <span class="term" tabindex="0" data-tooltip="Parts of the die that draw a lot of supply current and therefore need especially strong power-delivery paths.">High-current regions</span> need strong delivery paths, while the signal-routing system needs enough remaining space to connect the logic. Power and data movement compete for the same physical world.

Once the large geography and power structure are credible, the smaller standard cells can be arranged in the remaining regions.

### Placement: assign every standard cell a legal position

*Factory: give every small workstation a bay. Connected stations should be neighbors.*

Placement chooses physical locations for the standard cells produced by synthesis.

The naive objective would be to put connected cells close together and minimize total wire length. But not all connections matter equally, and short total wire length does not guarantee a working chip.

The placer must balance:

- <span class="term" tabindex="0" data-tooltip="The slowest routes data must travel between registers. These deliveries cannot afford a long walk, so they get the shortest wires.">timing-critical paths</span>;
- <span class="term" tabindex="0" data-tooltip="Too many connections competing for the same scarce wiring tracks, like too many trucks on one corridor.">routing congestion</span>;
- local <span class="term" tabindex="0" data-tooltip="How tightly standard cells are packed in a region. Too dense and there is no room to route; too sparse and wires get long.">cell density</span>;
- power concentration;
- access to macro pins;
- room for the clock network;
- legal cell orientations and row locations;
- enough routing capacity for later stages.

A connection with almost no remaining <span class="term" tabindex="0" data-tooltip="How much spare time a path has before it misses the next clock edge. Almost no margin means the path is living on the deadline.">timing margin</span> may deserve a much shorter path even if several noncritical connections become slightly longer.

Placement algorithms repeatedly estimate timing and congestion, move cells, and estimate again. After optimization, <span class="term" tabindex="0" data-tooltip="The placement cleanup that snaps every cell into an allowed row site with no overlaps.">legalization</span> moves every cell into an <span class="term" tabindex="0" data-tooltip="A legal parking spot on a standard-cell row. Legalization snaps every cell into one with no overlaps.">allowed site</span> with no overlaps or prohibited arrangements.

At this point, the data logic has locations. But one of the most widely distributed signals on the chip—the clock—still needs a real <span class="term" tabindex="0" data-tooltip="The power grid that is supposed to keep voltage high enough everywhere.">delivery network</span>.

### Clock-tree synthesis: deliver coordinated clock edges

*Factory: install the shift-bell wiring so every station hears the same tick.*

Registers change their stored values in response to clock edges. A single <span class="term" tabindex="0" data-tooltip="The origin of the clock pulse — the master shift bell — from which the clock network fans out to every register.">clock source</span> may need to reach millions of registers spread across an irregular chip.

Connecting that source directly to every register with one giant wire would create an enormous electrical load. The signal would become slow and distorted, and registers at different locations would see the clock edge at different times.

Clock-tree synthesis constructs a <span class="term" tabindex="0" data-tooltip="Building the chip from nested blocks rather than one giant flat netlist, so tools and teams can work on pieces.">hierarchy</span> of wires and buffers:

```text
clock source
    → large regional buffers
        → intermediate buffers
            → local buffers
                → registers
```

Each buffer drives a manageable portion of the downstream wire and register load.

The clock network is judged by several properties:

- **<span class="term" tabindex="0" data-tooltip="Clock latency: how long the shift bell's pulse takes to travel from the clock source to a register. Not the same as job latency.">Latency</span>:** how long a clock edge takes to reach a register — not the same as job latency earlier; this is the travel time of the shift bell, not the time to finish an order.
- **Skew:** the difference between its <span class="term" tabindex="0" data-tooltip="When a clock or data edge actually shows up at a register. Different arrival times at different registers are skew.">arrival times</span> at different registers.
- **<span class="term" tabindex="0" data-tooltip="Whether a clock or data edge rises or falls sharply enough. A slow, sloppy edge is late and more easily disturbed."><strong>Transition quality</strong></span>:** whether the <span class="term" tabindex="0" data-tooltip="The actual rise or fall of a voltage, which takes time and can be slow or sloppy on a heavy wire.">electrical edge</span> changes sharply enough.
- **Power:** how much energy is consumed by a network that switches constantly.

Skew changes the time available for data to travel between registers. If the launching and <span class="term" tabindex="0" data-tooltip="The register that must catch the arriving value at a later clock edge, ending a timing path.">capturing registers</span> receive nominally identical clock edges at different times, the effective data deadline moves. <span class="term" tabindex="0" data-tooltip="Useful skew: deliberately arriving the clock a little earlier or later at some registers to give a hard data path more time."><strong>Carefully controlled skew</strong></span> can sometimes help timing, but uncontrolled skew creates failures.

#### The H-tree is the clean symmetric idea, not the universal answer

Imagine four registers positioned symmetrically around one clock source. We could split the clock into two equal branches and then split each branch again. If every path has equal length, <span class="term" tabindex="0" data-tooltip="Inserting amplifier cells so a signal can drive a long wire or many destinations without becoming slow and sloppy.">buffering</span>, and load, the edge should reach the four endpoints at approximately the same time.

Repeating this symmetric branching pattern across a two-dimensional region produces shapes resembling nested letters H, hence **<span class="term" tabindex="0" data-tooltip="A symmetrically branching clock network shaped like nested letter H's. The clean idea of equal path length; real chips usually need a messier tree, spine, or mesh.">H-tree</span>**.

The important idea is recursive symmetry, not the letter itself:

> Give every destination an electrically similar path from the source.

Real chips are not empty symmetric squares. Registers are unevenly distributed. SRAM macros obstruct routes. <span class="term" tabindex="0" data-tooltip="Turning off the clock to idle regions so those registers stop switching and waste less dynamic power.">Clock-gating</span> structures create unequal loads. <span class="term" tabindex="0" data-tooltip="Regions of the chip that run at different supply voltages. Complicates clocks, power, and the interfaces between regions.">Voltage domains</span>, power grids, and operating modes complicate the network. One branch may drive hundreds of registers while another drives thousands.

Consequently, real <span class="term" tabindex="0" data-tooltip="Building the network of wires and buffers that delivers the clock edge from one source to millions of registers.">clock-tree synthesis</span> (<span class="term" tabindex="0" data-tooltip="Clock-tree synthesis: building the network that delivers clock edges to registers.">CTS</span>) may create an <span class="term" tabindex="0" data-tooltip="A clock network whose branches are not equal, sized to the actual register locations and loads instead of a pretty H.">irregular buffered tree</span>, a long <span class="term" tabindex="0" data-tooltip="A long main trunk of the clock network, with local branches off it, used when a perfectly symmetric tree does not fit the chip.">clock spine</span> with local branches, a connected <span class="term" tabindex="0" data-tooltip="A grid of clock wires that gives several paths to each region, reducing sensitivity to variation at the cost of more metal and switching power.">clock mesh</span>, or a hybrid in which a tree feeds <span class="term" tabindex="0" data-tooltip="Local grids of clock wires fed by a tree, a hybrid of tree and mesh.">regional meshes</span>. A mesh can reduce sensitivity to local variation by providing several paths, but it consumes much more wire and switching power.

<span class="term" tabindex="0" data-tooltip="Clock-tree synthesis: building the network that delivers clock edges to registers."><strong>CTS</strong></span> is therefore not “apply an H-tree algorithm.” It is an optimization problem:

> Given the actual register locations, electrical loads, obstacles, timing requirements, and available clock cells, build a clock network with acceptable arrival times, signal quality, power, and routing cost.

Once the clock network exists, the remaining logical connections need exact physical paths.

### Routing: turn logical connections into metal

*Factory: pour the actual roads and hang the conveyors. The drawings said A connects to B; routing chooses the path.*

The netlist says that one cell's output connects to another cell's input. Routing decides exactly how that connection travels across the die.

Modern chips contain several stacked <span class="term" tabindex="0" data-tooltip="Stacked wiring floors above the transistors. A connection may travel on one floor, then take a via-elevator to another.">metal layers</span> above the transistor layer. A connection may travel horizontally on one layer, vertically on another, and move between layers through small vertical connectors called <span class="term" tabindex="0" data-tooltip="Tiny vertical connectors that move a signal from one metal layer to another, like elevators between floors of wiring.">vias</span>. It must navigate around macros, power structures, existing wires, and other blockages while competing with millions of other connections for finite <span class="term" tabindex="0" data-tooltip="The legal lanes on a metal layer that wires may occupy. Finite, like lanes on a highway.">routing tracks</span>.

Routing can be understood in two conceptual stages.

**<span class="term" tabindex="0" data-tooltip="The first routing stage: assign approximate corridors and layers, and find congestion, before drawing exact wires.">Global routing</span>** assigns approximate corridors and layers. It predicts where groups of connections should travel and identifies congestion before committing to exact geometry.

**<span class="term" tabindex="0" data-tooltip="The second routing stage: choose exact tracks, widths, spacings, and vias. The result is manufacturable geometry.">Detailed routing</span>** chooses exact tracks, widths, spacings, vias, and layer transitions. Its result is literal geometry that can eventually be manufactured.

The router is balancing much more than total wire length:

- completing every required connection;
- meeting timing goals;
- avoiding congestion;
- limiting resistance, capacitance, and <span class="term" tabindex="0" data-tooltip="Unwanted influence of one switching wire on a neighbor through capacitive coupling.">crosstalk</span>;
- reducing unnecessary vias and detours;
- respecting current and reliability constraints;
- producing geometry that manufacturing can print.

#### Routing constructs rule-aware geometry, but it does not certify the whole chip

It is reasonable to ask why a later design-rule check is necessary. If the router knows the foundry's rules, why not require it to produce a layout that is already proven legal?

In an idealized problem, one tool could receive every connection, every electrical goal, every manufacturing rule, and unlimited computation time, then return a globally optimal layout with a proof of correctness.

Real routing is computationally enormous. The router must make practical decisions for millions or billions of pins while balancing timing, congestion, power, crosstalk, via count, and manufacturability. It uses <span class="term" tabindex="0" data-tooltip="Practical search rules that usually find a good-enough route or placement, not a proof of the global optimum.">heuristics</span> and a fast working model of relevant rules. It absolutely attempts to create legal geometry; it does not knowingly draw arbitrary wires and leave legality for later.

But that constructive rule checking is not a complete final proof.

First, foundry rules can be deeply contextual. Legality may depend on a shape's width, the length for which two wires run beside one another, <span class="term" tabindex="0" data-tooltip="How a drawn wire stops. Foundry rules about line endings are a common source of design-rule violations.">line endings</span>, bends, via combinations, shapes on neighboring layers, local density, <span class="term" tabindex="0" data-tooltip="Using light and masks to form shapes on a layer. Foundry rules also restrict which pattern combinations are legal to print.">patterning</span> restrictions, or special electrical regions. A routing engine needs rule models fast enough to consult during billions of search and optimization decisions. The signoff checker uses the complete authoritative <span class="term" tabindex="0" data-tooltip="The foundry's authoritative list of geometric manufacturing rules. The signoff DRC checker uses this complete deck, not the router's faster approximation.">rule deck</span> for exhaustive analysis of the finished geometry.

Second, the router does not create every shape in the chip. The final layout also contains the internal geometry of standard cells and macros, power networks, clock wires, manually designed analog blocks, <span class="term" tabindex="0" data-tooltip="Dummy standard cells that fill empty sites in a row so the row is electrically and geometrically complete.">filler</span> and <span class="term" tabindex="0" data-tooltip="On-chip capacitors that locally store charge so a sudden burst of switching does not collapse the supply voltage.">decoupling cells</span>, <span class="term" tabindex="0" data-tooltip="Dummy metal added so each layer has even density, which manufacturing requires. It can change parasitics after routing thinks it is done.">metal fill</span>, <span class="term" tabindex="0" data-tooltip="Late, local edits to an otherwise-kept layout, often to fix a bug without a full rebuild.">engineering-change patches</span>, I/O structures, and foundry-required features. Shapes that are legal independently can create an illegal combination at their boundaries.

Third, later steps may modify the geometry. Metal fill is added to maintain suitable material density during fabrication. <span class="term" tabindex="0" data-tooltip="Extra vertical connections added beside a required via so one manufacturing defect is less likely to disconnect the signal.">Redundant vias</span>, <span class="term" tabindex="0" data-tooltip="Edits that prevent a long wire from collecting damaging charge during manufacturing, before it is connected to a transistor gate.">antenna fixes</span>, power changes, and late engineering changes can also alter the supposedly finished layout.

Finally, independent checking protects against tool bugs, stale or incorrectly translated rule files, configuration errors, omitted layers, and incorrect <span class="term" tabindex="0" data-tooltip="Simplified models of a block's outline, pins, and metal blockages, used so top-level tools need not see every transistor.">physical abstractions</span> around <span class="term" tabindex="0" data-tooltip="Macros or IP whose internal layout comes from someone else. The top-level tools see an abstraction, which can be wrong.">imported blocks</span>.

The relationship is therefore:

- The router tries to **construct** legal, high-quality connections efficiently.
- The signoff design-rule checker independently **verifies** the complete assembled geometry using the foundry's authoritative rules.

When routing finishes, we finally know the actual shapes and lengths of the signal wires. That newly available physical detail allows the next level of analysis.

---

## Extraction and Timing: Calculate What the Real Geometry Does

*Factory: walk the finished roads with a stopwatch and an electrician. The sketch was optimistic.*

Before routing, tools estimate <span class="term" tabindex="0" data-tooltip="Time a signal spends traveling along a real wire, from the wire's resistance and capacitance, on top of the delay of the gates.">wire delay</span> using approximate locations and routes. After routing, they can calculate the electrical consequences of the actual geometry.

Every real wire has resistance. It also stores electrical charge relative to nearby structures, giving it capacitance. Neighboring wires couple to one another as well. These unwanted but unavoidable properties are called <span class="term" tabindex="0" data-tooltip="The real electrical properties of finished wires: resistance, capacitance, and coupling to neighbors. Ideal netlist connections do not have them.">parasitics</span>.

**<span class="term" tabindex="0" data-tooltip="Calculating the real resistance, capacitance, and coupling of finished wires from their actual shapes, instead of treating connections as ideal.">Parasitic extraction</span>** derives resistance, capacitance, and coupling values from the completed layout. The exact routes can now be treated as electrical components rather than ideal connections.

<span class="term" tabindex="0" data-tooltip="Checking whether data arrives at registers in time across huge numbers of paths, without running every possible program.">Static timing analysis, or STA</span>, combines:

- the <span class="term" tabindex="0" data-tooltip="The delay numbers in the cell library that STA uses for each gate.">characterized delay</span> of each selected cell;
- the <span class="term" tabindex="0" data-tooltip="Wire delay computed from the real routed shapes after extraction, replacing the earlier optimistic estimate.">extracted delay</span> of the routed wires;
- the real clock-distribution network;
- the timing requirements and operating modes.

Consider a path:

```text
launching register
    → combinational cells
        → routed wires
            → capturing register
```

For <span class="term" tabindex="0" data-tooltip="The requirement that a new value arrive and settle at a register early enough before the capturing clock edge.">setup timing</span>, the question is:

> After the <span class="term" tabindex="0" data-tooltip="The register that releases a new value at a clock edge, starting a timing path.">launching register</span> releases a new value, does that value propagate through every gate and wire and become stable at the capturing register early enough for the intended <span class="term" tabindex="0" data-tooltip="The clock edge at which a capturing register is supposed to take a snapshot of its input.">capture edge</span>?

For <span class="term" tabindex="0" data-tooltip="The requirement that an old value stay stable long enough after a clock edge that the register is not corrupted by the next value arriving too soon.">hold timing</span>, the question is:

> After a capture edge, does the old value remain stable long enough that the capturing register is not disturbed by a new value arriving too quickly?

<span class="term" tabindex="0" data-tooltip="Static timing analysis: checking whether data arrives at registers in time across huge numbers of paths, without running every possible program.">STA</span> does not run every possible program. It propagates earliest and latest possible signal-arrival times through the <span class="term" tabindex="0" data-tooltip="The STA model of the chip as a graph of cells and wires, used to propagate earliest and latest possible arrival times.">timing graph</span>. This allows it to analyze enormous numbers of paths without enumerating all functional input sequences.

The chip must also work despite variation. Manufacturing produces slightly different transistor characteristics. Supply voltage moves. Temperature changes. The chip may have several clock configurations and functional or test modes.

Timing is therefore checked across required combinations of <span class="term" tabindex="0" data-tooltip="Manufacturing makes transistors slightly different from copy to copy and from place to place on the die. Timing must still close across that spread.">process variation</span>, voltage, temperature, modes, and extracted interconnect conditions.

If a path fails, engineers may:

- replace a cell with a faster or stronger version;
- <span class="term" tabindex="0" data-tooltip="Add an amplifying cell on a slow or heavily loaded net to improve delay or signal sharpness.">insert a buffer</span>;
- move cells closer together;
- reroute a connection;
- alter the clock network;
- restructure the logic;
- add a pipeline stage;
- reduce the <span class="term" tabindex="0" data-tooltip="The clock rate the product is supposed to reach. Reducing it is a performance concession, not a free timing fix.">target clock frequency</span>.

Notice how the scale of the fix depends on the cause. A slightly slow wire might need a <span class="term" tabindex="0" data-tooltip="A small physical fix — resize a cell, move a few neighbors, reroute a wire — that does not throw away the rest of the layout.">local repair</span>. Too much computation assigned to one clock cycle may require a microarchitectural change. Physical analysis is where earlier abstractions are forced to confront the behavior of real geometry.

---

## Physical Signoff: Establish Every Required Meaning of “Correct”

*Factory: building inspector, electrician, and safety audit. Legal to construct, wired as drawn, safe to run.*

A routed design can be fully connected and still be unsafe to manufacture. A design can obey every manufacturing geometry rule and still connect the wrong components. It can be connected correctly and still fail timing. It can pass timing at an <span class="term" tabindex="0" data-tooltip="The voltage the schematic assumes every transistor sees. Real IR drop means some regions see less.">ideal supply voltage</span> and fail when heavy current causes the real voltage to sag.

There is no single meaning of “the physical chip is correct.” Signoff is the body of evidence covering all the meanings that matter.

### Manufacturing correctness

**<span class="term" tabindex="0" data-tooltip="Checking the finished shapes against the foundry's geometric manufacturing rules: widths, spacings, vias, density.">Design-rule checking</span>**, or <span class="term" tabindex="0" data-tooltip="Design-rule checking: do the finished shapes obey the foundry's geometric manufacturing rules?"><strong>DRC</strong></span>, examines the complete layout against the foundry's authoritative manufacturing rules. It checks requirements involving widths, spacing, vias, line endings, density, pattern combinations, and many other geometric conditions.

DRC is run repeatedly during implementation, not because the team wants to perform the final ceremony many times, but because it is much cheaper to find problems while their causes are still local.

A block can be checked before <span class="term" tabindex="0" data-tooltip="Assembling previously designed blocks into the whole chip and checking the boundaries between them.">top-level integration</span>. The integrated chip can be checked at <span class="term" tabindex="0" data-tooltip="The interfaces and physical edges where separately designed pieces meet. A common place for checking surprises.">block boundaries</span>. Relevant checks can be rerun after fill, rerouting, power changes, or an <span class="term" tabindex="0" data-tooltip="A local repair to an otherwise-kept physical design, rather than rebuilding the chip from scratch.">engineering change</span>. The exact <span class="term" tabindex="0" data-tooltip="The exact geometry that will be taped out. Later checks on this layout are the ones that count.">frozen layout</span> receives the definitive final run.

Waiting until the end to discover hundreds of thousands of violations would turn a checker into a disaster report. Earlier runs make the final signoff a confirmation of accumulated evidence rather than the first serious inspection.

### Connectivity correctness

**<span class="term" tabindex="0" data-tooltip="Checking that the shapes on the chip still form the intended circuit: no missing connections, no accidental shorts.">Layout-versus-schematic checking</span>**, or <span class="term" tabindex="0" data-tooltip="Layout-versus-schematic: do those shapes still form the intended circuit?"><strong>LVS</strong></span>, asks whether the connectivity extracted from the physical geometry matches the circuit represented by the intended netlist.

Every individual shape could be legal while a <span class="term" tabindex="0" data-tooltip="A vertical connection that should join two metal layers but is absent, leaving a signal disconnected.">missing via</span> leaves a signal disconnected or a <span class="term" tabindex="0" data-tooltip="An accidental connection between two signals that should be separate, so they electrically fight.">short</span> joins two signals that should be separate. DRC establishes geometric legality; LVS establishes <span class="term" tabindex="0" data-tooltip="Layout-versus-schematic passing: the shapes still implement the intended circuit, not merely legal geometry.">structural identity</span>.

### Timing and signal correctness

<span class="term" tabindex="0" data-tooltip="Accurate enough to be part of the tape-out evidence, not merely a quick estimate during implementation.">Signoff-quality</span> extraction and STA establish that data and clocks satisfy their timing requirements across the required <span class="term" tabindex="0" data-tooltip="The process, voltage, temperature, and modes under which timing and power must still be legal.">operating conditions</span>.

<span class="term" tabindex="0" data-tooltip="Checking whether nearby switching wires disturb or delay each other. A legally drawn route can still behave poorly as an electrical neighbor.">Signal-integrity analysis</span> examines interference between nearby wires. When one signal switches, <span class="term" tabindex="0" data-tooltip="Two neighboring wires acting like a capacitor, so a switch on one disturbs or delays the other. The cause of crosstalk.">capacitive coupling</span> can disturb or delay a neighboring signal. That interaction is called crosstalk. A route that is logically connected and geometrically legal can still behave poorly as an <span class="term" tabindex="0" data-tooltip="A nearby wire that can disturb a victim through coupling even though the two nets are not logically connected.">electrical neighbor</span>.

### Power and long-term reliability

<span class="term" tabindex="0" data-tooltip="Checking whether the on-chip power network keeps voltage high enough everywhere under realistic switching. Includes static and dynamic IR drop.">Power-integrity analysis</span> calculates whether the delivery network maintains adequate voltage throughout the chip under realistic activity. It checks <span class="term" tabindex="0" data-tooltip="Voltage sag on the power network: the steady sag from average current, plus extra sag when many transistors switch at once."><strong>static and dynamic IR drop</strong></span> rather than assuming every transistor receives an ideal supply.

<span class="term" tabindex="0" data-tooltip="Checking whether sustained current will slowly shove metal atoms along a wire until it thins, voids, or fails over the product lifetime.">Electromigration analysis</span> examines whether sustained <span class="term" tabindex="0" data-tooltip="How much current is packed through a given cross-section of metal. Too high for too long and electromigration can damage the wire.">current density</span> can gradually move metal atoms and damage a wire. A connection can work correctly on day one and still be physically unreliable over the product's required lifetime.

Power and <span class="term" tabindex="0" data-tooltip="Checking whether the workload's heat stays within what the package and cooling can remove, because temperature changes timing and leakage.">thermal analysis</span> evaluate whether the workload stays within electrical and <span class="term" tabindex="0" data-tooltip="How much heat the package, board, and system can remove. Performance that does not fit in the cooling budget is not performance you can ship.">cooling limits</span>. Temperature feeds back into timing and leakage, so these concerns cannot be treated as independent bookkeeping.

Additional checks address fabrication effects such as charge accumulated on wires during manufacturing, suitable material density, and correct interactions between different voltage regions.

Passing one check cannot substitute for the others:

- DRC asks whether the shapes can be manufactured.
- LVS asks whether those shapes form the intended circuit.
- STA asks whether the circuit operates within its <span class="term" tabindex="0" data-tooltip="The legal intervals for data to arrive relative to clock edges — setup and hold — across required corners.">timing windows</span>.
- Power analysis asks whether the supply network supports that operation.
- Signal-integrity and reliability analysis ask whether physical interactions and long-term stress remain acceptable.

Only when the organization accepts this combined evidence does the candidate design become eligible for tape-out.

---

## Tape-Out and Fabrication: Commit the Argument to Matter

*Factory: freeze the blueprints and hand them to the construction company. Walls do not move after the concrete sets.*

Tape-out freezes the accepted physical layout and delivers it to the foundry. The historical name survived from an era when design data was physically written to magnetic tape.

The final data describes the geometry required for <span class="term" tabindex="0" data-tooltip="The parts of the layout that become actual transistors after fabrication, as opposed to the metal wiring above them.">transistor regions</span>, <span class="term" tabindex="0" data-tooltip="The tiny vertical connections from transistors up to the first metal layer.">contacts</span>, vias, metal layers, and other manufacturing structures. The foundry prepares <span class="term" tabindex="0" data-tooltip="The stencils the foundry uses to pattern each layer of the chip. Layout data is turned into these before silicon is built.">masks</span> and uses repeated processes—including material <span class="term" tabindex="0" data-tooltip="Adding a layer of material onto the wafer during fabrication.">deposition</span>, patterning, <span class="term" tabindex="0" data-tooltip="Chemically or physically removing material that was not protected during patterning.">etching</span>, <span class="term" tabindex="0" data-tooltip="Shooting dopants into silicon to form transistor regions.">implantation</span>, and <span class="term" tabindex="0" data-tooltip="Flattening the wafer between layers so the next layer can be built on a level surface.">polishing</span>—to build many copies of the design on a wafer.

One rectangular physical copy cut from the wafer is a **die**. A die may implement the entire primary chip design, or it may serve as one <span class="term" tabindex="0" data-tooltip="One die used as a component inside a larger multi-die package, rather than as the entire product by itself.">chiplet</span> within a larger package. “Die” describes the physical piece of silicon; “chiplet” describes its role as one component in a multi-die system.

The wafer and individual dies are tested so that <span class="term" tabindex="0" data-tooltip="Manufactured copies that fail wafer or package test and should not be shipped.">defective units</span> can be identified before the most expensive packaging steps. The surviving dies then have to become usable members of a larger physical system.

---

## Packaging, Boards, and Firmware: Build the Environment Around the Die

*Factory: put the finished building in a shell, hook it to the power grid and the highway, and write the opening-day checklist.*

A <span class="term" tabindex="0" data-tooltip="A piece of silicon that has been cut from the wafer but not yet packaged. Not a deployable product by itself."><strong>bare die</strong></span> is not yet a deployable product. It needs power, cooling, mechanical protection, and electrical connections to memory, other dies, <span class="term" tabindex="0" data-tooltip="The boards packaged chips sit on, supplying power, clocks, reset, and connections to the rest of the system.">circuit boards</span>, and external systems.

The package provides those connections. In an advanced accelerator, <span class="term" tabindex="0" data-tooltip="The physical arrangement of the package, which can set memory bandwidth and chip-to-chip performance in advanced products.">package geometry</span> can determine memory bandwidth and chip-to-chip communication performance, so packaging is part of system architecture rather than an ornamental box around a finished chip.

The <span class="term" tabindex="0" data-tooltip="The board the packaged chip sits on, supplying power, clocks, reset, and connections to the rest of the system.">circuit board</span> supplies <span class="term" tabindex="0" data-tooltip="Board circuitry that turns a coarse supply into the stable voltages the chip requires.">voltage regulation</span>, <span class="term" tabindex="0" data-tooltip="Clean periodic signals supplied from the board that the chip uses to generate its internal clocks.">reference clocks</span>, reset control, <span class="term" tabindex="0" data-tooltip="Small CPUs on the board or chip that handle bring-up, monitoring, and configuration rather than the user's main workload.">management processors</span>, network or <span class="term" tabindex="0" data-tooltip="Links to the computer that owns the accelerator and sends it work.">host connections</span>, sensors, and physical signal paths. A <span class="term" tabindex="0" data-tooltip="A system of many boards and chips in one rack, with its own power, cooling, and communication — the factory campus, not one building.">rack-scale</span> system adds power delivery, cooling, communication, and coordination across many boards and chips.

<span class="term" tabindex="0" data-tooltip="Low-level software that wakes and configures the hardware: clocks, reset order, memories, high-speed links, and the handoff to drivers.">Firmware</span> is the low-level software that wakes and configures the hardware. On startup, it may:

1. establish <span class="term" tabindex="0" data-tooltip="Conservative frequencies and sources used at power-on before firmware trusts the high-speed clocks.">safe clock settings</span>;
2. hold or release blocks from reset in the required order;
3. initialize and test memories;
4. <span class="term" tabindex="0" data-tooltip="Calibrating a high-speed link until both ends agree on timing and signal quality. Until training finishes, the dock is not trustworthy.">train</span> <span class="term" tabindex="0" data-tooltip="Fast chip-to-chip or chip-to-memory connections that usually need training before they are reliable.">high-speed external links</span>;
5. configure <span class="term" tabindex="0" data-tooltip="Configuration memories that tell the interconnect and schedulers where work should go.">routing and scheduling tables</span>;
6. inspect <span class="term" tabindex="0" data-tooltip="Status locations firmware reads to see whether blocks came up correctly and whether faults have been logged.">health and error registers</span>;
7. expose the accelerator to <span class="term" tabindex="0" data-tooltip="System software that exposes the chip to programs: the layer above firmware.">drivers</span> and higher-level software.

Package, board, cooling, and firmware development cannot sensibly wait until fabrication finishes. They proceed in parallel using models, simulation, <span class="term" tabindex="0" data-tooltip="Mapping the RTL onto specialized machines that can run much larger workloads than software simulation, still before real silicon exists.">emulation</span>, and <span class="term" tabindex="0" data-tooltip="Early hardware stand-ins — emulation, FPGA boards, previous chips — used to develop firmware and software before the real ASIC arrives.">prototypes</span>.

RTL simulation provides detailed visibility but becomes extremely slow for an entire large chip. <span class="term" tabindex="0" data-tooltip="Mapping the RTL onto specialized machines that can run much larger workloads than software simulation, still before real silicon exists.">Hardware emulation</span> maps the RTL onto specialized systems capable of running much larger workloads before silicon exists. <span class="term" tabindex="0" data-tooltip="Mapping parts of the design onto reconfigurable chips so hardware and software can interact before the ASIC exists. Not a perfect speed or power replica.">FPGA prototyping</span> can map portions of the design onto <span class="term" tabindex="0" data-tooltip="Hardware whose logic can be changed after manufacturing. FPGA prototypes are the usual example.">reprogrammable chips</span> so hardware and software can interact early, although an <span class="term" tabindex="0" data-tooltip="Field-programmable gate array: a reconfigurable chip used to prototype hardware before the real ASIC exists.">FPGA</span> cannot reproduce the ASIC's exact speed, power, <span class="term" tabindex="0" data-tooltip="Continuous voltages and currents, as opposed to clean digital 0/1 levels. An FPGA prototype will not match the ASIC here.">analog behavior</span>, or <span class="term" tabindex="0" data-tooltip="The real delays of the manufactured silicon, which an FPGA or emulator cannot reproduce exactly.">physical timing</span>.

These methods reduce uncertainty. None can perfectly substitute for the manufactured object.

---

## Bring-Up: Establish That the New Chip Is Alive

*Factory: first day on the new floor. Lights first, then one line, then a full shift.*

When the first packaged chips arrive, engineers do not immediately apply maximum power and launch the largest workload. They introduce complexity gradually so that each new observation has a limited set of possible causes.

A simplified <span class="term" tabindex="0" data-tooltip="The ordered first experiments on new silicon: power, clocks, reset, a known register, then one subsystem at a time.">bring-up sequence</span> might be:

1. Inspect the package and board.
2. Apply power under controlled limits.
3. Verify <span class="term" tabindex="0" data-tooltip="The named supply voltages on the board and package that feed the chip. Bring-up checks they are present and within limits before asking the chip to work.">voltage rails</span> and <span class="term" tabindex="0" data-tooltip="How much supply current the chip is drawing. Bring-up checks this before asking the chip to do real work.">current consumption</span>.
4. Confirm that reference clocks exist.
5. Check reset behavior.
6. Connect through a basic <span class="term" tabindex="0" data-tooltip="A slow, reliable port used to peek at internal registers when the chip first comes up, before high-speed links are trusted.">debug interface</span>.
7. Read a known identification or <span class="term" tabindex="0" data-tooltip="A small on-chip memory location that reports identity or health. Reading a known value is often the first proof the chip is alive.">status register</span>.
8. Test small on-chip memories.
9. Enable and test one subsystem at a time.
10. Initialize external memory and communication links.
11. Boot increasingly complete firmware.
12. Run small <span class="term" tabindex="0" data-tooltip="Small, targeted tests run during bring-up to prove one subsystem at a time before launching a full workload.">diagnostics</span> followed by realistic workloads.
13. Sweep voltage, frequency, and temperature.

This is bring-up: moving the device from inert silicon to basic controlled operation while preserving enough experimental discipline to localize failures.

---

## Silicon Validation: Return to the Original Promise

*Factory: are we actually shipping what the original customer order promised?*

A chip being alive does not mean the product is successful. Validation closes the loop by comparing the physical system with the original requirements.

The team asks:

- Does every feature work?
- Are numerical results correct?
- Does the chip reach its target clock frequency?
- Does it sustain the promised throughput and latency?
- Does external memory deliver the expected bandwidth?
- Does chip-to-chip communication remain reliable?
- How much power does the actual workload consume?
- Does the system remain correct across temperature and voltage variation?
- Are there rare failures under hours or days of stress?
- Does the packaged chip interoperate with boards, firmware, drivers, and other devices?

Failures are difficult to diagnose because their symptoms appear at the <span class="term" tabindex="0" data-tooltip="Symptoms seen only when the whole product is running: chip, package, board, firmware, and software together.">complete-system level</span>. A wrong result could come from RTL, <span class="term" tabindex="0" data-tooltip="A path that barely meets or barely misses its deadline, so it works in some conditions and fails in others.">marginal physical timing</span>, incorrect firmware initialization, a <span class="term" tabindex="0" data-tooltip="A failure in the copper and connectors of the board, not inside the silicon.">board-level signal problem</span>, package behavior, a manufacturing defect, a <span class="term" tabindex="0" data-tooltip="System software that talks to the chip. A wrong result can be a driver bug rather than a silicon bug.">driver</span> bug, or even faulty measurement equipment.

The investigation again moves backward through representations. Engineers narrow the system condition, identify the first corrupted state or failed interface, and determine which earlier claim about the design reality has contradicted.

If the problem can be handled safely in firmware or software, the product may be recoverable. If it requires different physical logic or geometry, the chip may need a <span class="term" tabindex="0" data-tooltip="A new manufacturing spin of the chip after a bug that firmware cannot hide. Another tape-out.">new revision</span> and another tape-out.

---

## The Flow Is Not an Assembly Line

The design flow moves from abstraction toward physical reality, but it does not march through each stage exactly once.

There are at least three nested kinds of iteration.

### Tools optimize repeatedly inside a stage

A placer proposes locations, estimates timing and congestion, moves cells, and estimates again.

A clock-tree tool builds branches, analyzes skew and electrical load, resizes or adds buffers, and analyzes again.

A router creates paths, detects congestion or violations, tears up problematic wires, and tries different paths.

Even a single nominal “run” is an <span class="term" tabindex="0" data-tooltip="A tool repeatedly proposing a solution, scoring it, and proposing again. Even one run of place or route is many such loops.">optimization loop</span>.

### Engineers repair an existing physical design locally

Suppose accurate timing analysis discovers that one path is slightly too slow. The team may resize one cell, move several nearby cells, reroute the affected connections, re-extract those wires, and rerun the relevant checks.

This limited modification is an <span class="term" tabindex="0" data-tooltip="A local repair to an otherwise-kept physical design: resize a cell, move a few neighbors, reroute a wire. Not a rebuild from scratch.">engineering change order, or ECO</span>. The team does not necessarily discard the entire floorplan and rebuild the chip from the beginning.

Local repairs are possible when the design's basic structure remains sound and the violation has enough nearby flexibility.

### Fundamental contradictions force a return to an earlier representation

Other failures cannot be repaired locally.

If one clock cycle contains too much logical work, the microarchitecture may need another pipeline stage. If compute units remain idle because memory cannot feed them, the architecture may need a different <span class="term" tabindex="0" data-tooltip="The staged warehouses from tiny registers beside compute out to huge off-chip memory. Each level is larger and slower than the one above it."><strong>memory hierarchy</strong></span> or resource balance. If power delivery is inadequate in an entire region, the floorplan may have to change. If the required performance cannot fit within the available power and area, the product requirements themselves may need renegotiation.

The size of the backward loop should match the level at which the false assumption was made:

```text
small physical violation
    → local cell or wire repair

logic or pipeline failure
    → RTL or microarchitecture change

system bottleneck
    → architecture change

infeasible product target
    → requirements change
```

After a meaningful RTL change, the <span class="term" tabindex="0" data-tooltip="Verification, synthesis, and physical signoff that must be rebuilt after a meaningful RTL or architectural change.">downstream evidence</span> must be rebuilt: verification, synthesis, placement, routing, extraction, timing analysis, and signoff all need to establish that the new candidate works.

This is why signoff analysis happens repeatedly during implementation. Signoff is not a ceremonial stamp applied to a design that everyone already knows is correct. Its analyses reveal whether the current candidate is actually finished and what must change if it is not. The exact frozen layout receives the definitive final checks, but earlier candidates need the same kinds of scrutiny so the team can converge on that final candidate.

The deepest way to understand the entire process is therefore this:

> Chip design is not a simple assembly line. It is a progressively more physically accurate argument that a proposed machine will work—and every stage tries to break that argument before reality does.

The product requirements make the first claim. Architecture proposes a factory capable of satisfying it. Microarchitecture explains its cycle-by-cycle operation. RTL makes that explanation formal. Verification challenges its behavior. Synthesis demonstrates that available gates can implement it. Physical design proves that those gates and their wires can fit into real geometry. Signoff challenges that geometry using manufacturing and electrical reality. Fabrication turns the argument into matter. Bring-up and validation deliver the final verdict.

And if reality disagrees, the flow moves backward — not as an exception to chip design, but as **the mechanism by which chip design works**.