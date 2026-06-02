---
layout: page
title: "Chapter 12: AI Platform and Infrastructure Stack"
guide_type: chapter
---

# Chapter 12 — AI Platform and Infrastructure Stack

This chapter owns the platform and tooling layer: ML frameworks, distributed training libraries, serving stacks, orchestration systems, data/retrieval stacks, eval infrastructure, registries, observability, cloud/container infrastructure, and agent tooling stacks. Chapter 13 goes deeper into GPU/runtime/compiler mechanics.

# 1. Tech Stack Mental Models for Applied AI Roles

The job descriptions that matter for frontier AI engineering do not ask for tools as trivia.

They ask for tools because the tools reveal the shape of the work:

* training large models,
* scaling reinforcement learning,
* debugging distributed GPU jobs,
* building retrieval and knowledge systems,
* serving LLMs with low latency,
* running evals and experiments reproducibly,
* sandboxing long-horizon agents,
* making research infrastructure reliable enough that scientists can move fast.

The goal of this section is to build mental models for the stack. You do not need to be an expert in every tool. You do need to understand what problem each tool solves, what abstraction it exposes, what it composes with, and what failure modes it creates.

The best mental model is layered:

```text
data and environments
  -> tensors and model code
  -> training / post-training loop
  -> distributed execution
  -> inference serving
  -> product orchestration
  -> evaluation
  -> observability
  -> deployment and operations
```

Different roles emphasize different layers. RL infrastructure roles emphasize rollout workers, reward pipelines, distributed training, cluster scheduling, and reproducibility. Knowledge-system roles emphasize ingestion, indexing, ranking, RAG, query understanding, and evals. Product AI roles emphasize API design, retrieval, tools, safety boundaries, serving, observability, and rollout.

## 1.1 Where Tech Stacks Fit in This Study Guide

The stack is not a separate topic from the earlier chapters. It is the implementation surface of those ideas.

| Chapter | Stack connection |
| ------- | ---------------- |
| Chapter 0-1 | ML primitives, Transformer compute, tensors, gradients, and architecture foundations |
| Chapter 1 | Model APIs, structured outputs, prompt/version tooling, app integration |
| Chapter 2 | FAISS, pgvector, vector databases, Elasticsearch, rerankers, knowledge graphs |
| Chapter 3 | LangGraph, Temporal, MCP, sandboxed tools, workflow engines |
| Chapter 4 | Eval harnesses, judge tooling, tracing, regression datasets |
| Chapter 5 | RLHF, DPO, PPO, reward modeling, W&B, MLflow, distributed training loops |
| Chapter 6 | vLLM, TGI, Triton Inference Server, Ray Serve, Redis, queues, Kubernetes |
| Chapter 7 | Cloud architecture, auth, policy engines, rollout systems, platform composition |
| Chapter 8 | GPUs, TPUs, CUDA, Triton kernels, JAX, high-performance optimization |
| Chapter 9 | The mental-model index tying the concrete technologies together |

## 1.2 How to Learn a Technology

For any tool, ask seven questions:

1. What abstraction does it expose?
2. What bottleneck or complexity does it remove?
3. What does it make harder?
4. What does it compose with?
5. What assumptions does it make?
6. What failure modes does it introduce?
7. What would I monitor or test in production?

Weak answer:

> I know Kubernetes.

Strong answer:

> Kubernetes schedules and manages containerized workloads. In AI systems, it is useful for API services, workers, inference deployments, and some training jobs. But GPU scheduling, gang scheduling, storage locality, startup time, and observability still need careful design. For batch research clusters, Slurm may be a better fit.

That is the level of answer you want.

---

## 1.3 The Framework Layer: PyTorch, TensorFlow, JAX

The framework layer is where mathematical programs become executable tensor programs.

Mental model:

```text
Python code
  -> tensor operations
  -> computation graph or execution trace
  -> gradients
  -> optimizer update
  -> GPU / TPU kernels
```

### PyTorch

PyTorch's core mental model is:

```text
eager tensor program + autograd tape
```

You write Python code that runs immediately. Tensor operations execute eagerly. If tensors require gradients, PyTorch records the operations needed to compute gradients later.

This makes PyTorch feel like normal Python:

* easy to debug,
* easy to inspect intermediate tensors,
* easy to write custom training loops,
* easy to prototype research ideas.

Important concepts:

* `Tensor`: multidimensional array with device and dtype.
* `nn.Module`: composable model component with parameters.
* `autograd`: automatic differentiation engine.
* `optimizer`: parameter update rule.
* `Dataset` / `DataLoader`: data iteration.
* `cuda`: GPU device placement.
* `torch.compile`: compilation path for optimizing eager programs.

Where it sits:

```text
data loader -> PyTorch model -> loss -> autograd -> optimizer -> checkpoint
```

What it composes with:

* Hugging Face Transformers for model definitions and pretrained weights,
* DeepSpeed and FSDP for distributed training,
* W&B or MLflow for experiment tracking,
* Triton kernels for custom GPU operations,
* vLLM or TGI for serving models trained or exported from the PyTorch ecosystem.

Why jobs ask for it:

Frontier AI work often means changing model code, debugging training loops, testing new objectives, or optimizing throughput. PyTorch gives researchers and engineers a flexible surface for that work.

Failure modes:

* silent CPU/GPU device mismatch,
* accidental graph retention causing memory growth,
* inefficient data loading starving GPUs,
* too many small operations causing overhead,
* distributed training hangs,
* checkpoint incompatibility,
* mixed-precision instability.

Interview framing:

> PyTorch is strong for research iteration because it is eager and Pythonic. The mental model is tensors plus autograd plus modules. At scale, the hard parts become data loading, memory, distributed training, kernel efficiency, checkpointing, and observability.

### TensorFlow

TensorFlow's original mental model is:

```text
define computation graph -> optimize graph -> execute graph
```

Modern TensorFlow also supports eager execution, but a key idea remains graph compilation through `tf.function`.

Graph execution can enable:

* optimization,
* portability,
* deployment,
* serving,
* mobile and edge targets,
* static analysis.

Important concepts:

* `Tensor`: array data structure,
* `tf.function`: traces Python into graph form,
* Keras: high-level model API,
* `tf.data`: data pipeline API,
* TensorBoard: visualization and experiment inspection,
* TensorFlow Serving: model serving system,
* TFLite: mobile/edge deployment path.

Where it sits:

```text
data pipeline -> Keras / TensorFlow model -> graph execution -> serving artifact
```

What it composes with:

* TFX-style production ML pipelines,
* TensorFlow Serving,
* TensorBoard,
* mobile/edge deployment stacks,
* data validation and transformation tooling.

Tradeoff:

TensorFlow can be strong when graph optimization and production deployment are central. PyTorch often feels easier for research iteration and debugging. Modern usage has converged somewhat, but the historical mental models still matter in interviews.

Interview framing:

> TensorFlow is graph-oriented at heart. That can make deployment and optimization cleaner, but dynamic research code can feel less direct than PyTorch. The tradeoff is graph optimizability and production paths versus eager debugging flexibility.

### JAX

JAX's mental model is:

```text
NumPy-like functions + program transformations
```

The important transformations are:

* `grad`: take gradients of functions,
* `jit`: compile functions,
* `vmap`: vectorize functions,
* `pmap` / `pjit`: distribute computation across devices.

JAX asks you to think more functionally:

```text
params, batch -> loss
```

Instead of mutating model state inside object-oriented modules, you often pass state explicitly through pure functions.

What it composes with:

* XLA compilation,
* Flax or Haiku model libraries,
* Optax optimizers,
* TPU pods and GPU clusters,
* custom research training loops.

Why jobs ask for it:

JAX is popular in high-performance research environments because transformations make it powerful for vectorization, compilation, and distributed computation.

Failure modes:

* dynamic Python control flow can fight compilation,
* recompilation can destroy performance,
* shape changes can be expensive,
* debugging compiled code can be harder,
* state management requires discipline.

Interview framing:

> JAX is not just another neural network library. It is a system for transforming numerical Python functions. The power comes from `jit`, `grad`, `vmap`, and distributed transformations. The tradeoff is that you need to write code in a more functional and shape-stable way.

### PyTorch vs TensorFlow vs JAX

| Framework | Mental model | Best fit | Main tradeoff |
| --------- | ------------ | -------- | ------------- |
| PyTorch | Eager tensor programs plus autograd | Research iteration, LLM work, flexible training loops | Scaling and optimization require extra systems work |
| TensorFlow | Graph-oriented computation and deployment | Production ML, graph optimization, serving, mobile/edge | Less natural for dynamic research code |
| JAX | Functional numerical programs plus transformations | High-performance research, TPU/GPU scaling, compilation | Requires functional style and shape discipline |

The interview answer should not be "one is better." It should be:

> They optimize for different workflows. PyTorch optimizes for flexible research iteration, TensorFlow for graph/deployment-oriented production paths, and JAX for composable program transformations and high-performance compiled numerical code.

---

## 1.4 Model and Training Library Layer

Above the tensor framework are libraries that package model architectures, tokenizers, training utilities, and distributed training patterns.

Mental model:

```text
raw data
  -> tokenizer
  -> tensors
  -> model
  -> loss
  -> gradients
  -> optimizer
  -> checkpoint
```

### Hugging Face Transformers

Transformers is a standardized interface to model architectures, pretrained checkpoints, tokenizers, and generation utilities.

Mental model:

```text
model name -> config + tokenizer + weights + model class
```

What it is good for:

* loading pretrained models,
* fine-tuning,
* inference prototypes,
* standardizing model APIs,
* comparing architectures,
* accessing community checkpoints.

What it composes with:

* PyTorch, TensorFlow, JAX/Flax backends,
* Datasets,
* Tokenizers,
* Accelerate,
* PEFT/LoRA tooling,
* TRL for post-training,
* model hubs and registries.

Failure modes:

* tokenizer/model mismatch,
* hidden defaults in generation configs,
* memory surprises from model size,
* checkpoint compatibility issues,
* prototype code accidentally becoming production code.

### Datasets and Tokenizers

Datasets manage data loading, streaming, sharding, and preprocessing.

Tokenizers are the boundary between raw text and model tensors.

Mental model:

```text
text -> token ids -> tensors -> model
```

Why tokenizers matter:

* they define vocabulary,
* they affect sequence length,
* they affect cost,
* they affect multilingual behavior,
* they must match the model checkpoint.

In large-scale training, tokenization can become a real throughput bottleneck.

### Accelerate

Accelerate provides a simpler abstraction over multi-device training.

Mental model:

```text
same training loop -> configured device/distributed setup
```

It is useful when you want code to run on CPU, one GPU, multiple GPUs, or distributed environments with fewer changes.

### DeepSpeed

DeepSpeed is a training optimization system for large models.

The key mental model is memory partitioning.

ZeRO reduces memory pressure by sharding:

* optimizer states,
* gradients,
* parameters.

Instead of every GPU storing everything, GPUs store different pieces and communicate when needed.

Tradeoff:

* bigger models and batches fit,
* communication and configuration complexity increase.

### PyTorch FSDP

Fully Sharded Data Parallel is PyTorch's native approach to sharding model states across devices.

Mental model:

```text
each GPU stores shards
  -> gather parameters for computation
  -> compute
  -> reduce/scatter gradients
```

DeepSpeed ZeRO and FSDP solve similar memory-scaling problems, with different APIs and ecosystem integration.

### Fairseq and Megatron-LM Style Stacks

Fairseq and Megatron-style stacks represent research-oriented large-scale sequence modeling systems.

Mental model:

```text
model research code + distributed training patterns + optimized kernels + large-scale configs
```

They matter because many frontier training systems are not just simple library calls. They are large codebases that encode model architecture, data loading, distributed parallelism, checkpointing, and evaluation.

### PEFT and LoRA

Chapter 5 covers the theory of parameter-efficient fine-tuning: why freezing the base model and training a small adaptation can be a useful post-training strategy.

Here, the focus is the engineering side: how PEFT/LoRA shows up in the stack, how it composes with training libraries and serving systems, and what has to be tracked so adapters do not become ambiguous artifacts.

Parameter-efficient fine-tuning changes a small number of trainable parameters instead of updating the full model.

LoRA's mental model is:

```text
frozen base weights + small trainable low-rank adapters
```

Why it matters:

* much lower GPU memory,
* cheaper fine-tuning,
* easier adapter swapping,
* useful domain adaptation,
* faster experimentation.

What it composes with:

* Transformers,
* PEFT libraries,
* quantization,
* Accelerate,
* DeepSpeed/FSDP for larger runs,
* model registries that track base model plus adapter version.

Failure modes:

* adapter/base mismatch,
* overfitting narrow data,
* degraded general capability,
* confusing deployment if the adapter is not loaded with the intended base model,
* evaluation that misses slices where the adapter hurts.

Interview framing:

> The theory of LoRA belongs in post-training: freeze the base model and train a low-rank adaptation. The engineering concern is artifact integrity. I would track the base model, tokenizer, adapter version, training data, and eval results together because the adapter alone is not a complete deployable model.

### Dataset and Checkpoint Formats

Large-scale AI work is also about file formats.

Common dataset/storage formats:

* **Parquet:** columnar analytics format, good for warehouse-style datasets and feature tables.
* **Arrow:** in-memory columnar format, useful for efficient data interchange and Hugging Face Datasets internals.
* **JSONL:** simple line-delimited records, easy for prompts and small/medium corpora but inefficient at huge scale.
* **WebDataset / tar shards:** shard-based format often used for large image or multimodal datasets.
* **TFRecord:** TensorFlow-oriented record format, common in TF pipelines.

Common checkpoint formats:

* PyTorch checkpoints,
* `safetensors`,
* TensorFlow SavedModel,
* sharded checkpoints for large models,
* optimizer-state checkpoints for training resumption.

Mental model:

```text
data format determines how fast and safely bytes become batches
checkpoint format determines how reliably training or serving can resume
```

Why jobs care:

Many large-scale failures are not algorithmic. They are data throughput, checkpoint corruption, slow startup, bad sharding, or unreproducible artifact problems.

Interview framing:

> I would treat datasets and checkpoints as production artifacts. They need versioning, integrity checks, metadata, lineage, and compatibility with the training or serving stack.

Reference-guided learning adds coupled artifacts. A distillation or self-distillation run should track:

* student checkpoint and tokenizer,
* teacher or reference checkpoint,
* EMA decay, target-network update interval, or checkpoint-promotion rule,
* reward model, verifier, or judge model version,
* teacher prompt template or privileged context,
* rollout-policy version,
* dataset and filtering version,
* token mask settings such as RMSD `T` and `S`,
* eval suite version and promotion decision.

The student checkpoint alone is not enough to reproduce behavior. If a regression appears after a teacher promotion, the team needs to know which teacher produced which targets, which rollouts were used, and which eval gate allowed the model to ship.

---

## 1.5 RL and Post-Training Stack

Post-training turns a pretrained model into a model that follows instructions, uses tools, refuses unsafe requests, or performs well on specific tasks.

Mental model:

```text
policy
  -> rollout / completion
  -> reward or preference signal
  -> optimization update
  -> eval
  -> new policy
```

### Gym and Gymnasium

Gym's mental model is the environment interface:

```text
observation = env.reset()
observation, reward, done, info = env.step(action)
```

This interface matters because RL is about interaction, not just static labels.

For LLM agents, an environment might be:

* a code repository,
* a browser,
* a tool sandbox,
* a game,
* a math problem environment,
* a simulated user,
* a computer-use task.

### TRL and RLHF Libraries

TRL-style libraries package common post-training workflows:

* supervised fine-tuning,
* reward modeling,
* PPO,
* DPO,
* preference optimization.

Mental model:

```text
prompts -> candidate responses -> preference/reward -> policy update
```

They compose with:

* Transformers,
* Datasets,
* Accelerate,
* DeepSpeed/FSDP,
* W&B/MLflow,
* eval harnesses.

### Ray and RLlib

Ray provides distributed Python tasks and actors.

RLlib builds RL abstractions on top of distributed workers.

Mental model:

```text
driver
  -> rollout workers
  -> reward/eval workers
  -> learner workers
  -> checkpoint/eval
```

Ray is useful when workloads are Python-native, distributed, and irregular.

### Custom Rollout Workers

Frontier labs often build custom rollout infrastructure because LLM RL workloads are specialized:

* model-generated trajectories can be long,
* tool calls may be slow,
* rewards may require separate models,
* environments may require sandboxes,
* data needs careful logging and replay,
* throughput and reproducibility matter.

Job-role connection:

The roles mention PPO, DPO, RLHF, reward modeling, rollout pipelines, reward pipelines, distributed workloads, throughput, reliability, and reproducibility. This is exactly this layer.

### Distillation and Self-Distillation Pipelines

Reference-guided training often looks like an RL or post-training stack, but with extra teacher and lineage paths.

A minimal OPSD/RMSD record should include:

* prompt `x`,
* teacher prompt `x'` or privileged context,
* student rollout `y`,
* student top-K logprobs at each prefix,
* teacher logprobs on the same prefixes,
* candidate high-disagreement token positions,
* judge-selected relevant token positions,
* masked loss metadata,
* student checkpoint before and after the update,
* teacher/reference checkpoint used for scoring.

The hidden costs are easy to miss:

* rollout generation uses autoregressive decode,
* teacher rescoring adds extra forward passes,
* top-K logprobs can be large to store,
* judge calls add latency and API cost,
* teacher checkpoint promotion or EMA updates add orchestration complexity,
* broad evals are required to detect forgetting and specificity failures.

Operationally, this is a data pipeline as much as a training algorithm. The system must join rollouts, teacher scores, masks, losses, evals, and checkpoints without losing provenance.

---

## 1.6 Distributed Training and Cluster Orchestration

Large training jobs are distributed systems.

Mental model:

```text
training job
  -> scheduler
  -> nodes
  -> GPUs
  -> communication
  -> checkpoints
  -> metrics
```

### Kubernetes

Kubernetes orchestrates containers.

It handles:

* scheduling,
* service discovery,
* health checks,
* restarts,
* deployments,
* autoscaling,
* resource requests and limits.

AI use cases:

* API services,
* inference workers,
* embedding services,
* retrieval services,
* batch jobs,
* some training jobs.

Tradeoffs:

Kubernetes is excellent for service/platform workloads. GPU training at cluster scale may require extra tooling for gang scheduling, topology awareness, storage, and job lifecycle management.

### Slurm

Slurm is an HPC-style batch scheduler.

Mental model:

```text
submit job -> wait in queue -> allocated nodes -> run script -> release resources
```

It is common in research clusters because training jobs often look like long-running batch jobs that need a specific number of nodes and GPUs.

Kubernetes vs Slurm:

| System | Mental model | Best fit |
| ------ | ------------ | -------- |
| Kubernetes | container orchestration for services and jobs | production services, inference, platform workloads |
| Slurm | batch scheduling for cluster jobs | research training, HPC-style GPU jobs |

### Ray

Ray is a distributed execution framework for Python.

Mental model:

```text
Python function -> remote task
Python class -> remote actor
```

Ray is useful for:

* distributed data processing,
* RL rollouts,
* parallel evaluation,
* model serving,
* task orchestration.

### Docker and Containers

Containers package code, dependencies, and runtime environment.

Mental model:

```text
code + dependencies + OS-level runtime -> image -> container
```

Containers improve reproducibility, but they do not solve everything:

* GPU drivers still matter,
* data paths still matter,
* network and permissions still matter,
* image size and startup time matter.

### NCCL

NCCL is a communication library for GPUs.

It underlies common distributed training operations:

* all-reduce,
* broadcast,
* reduce-scatter,
* all-gather.

Mental model:

```text
GPU workers compute local gradients
  -> NCCL communicates across GPUs
  -> workers synchronize updates
```

Why it matters:

Distributed training performance often depends on communication. If NCCL is slow or hanging, GPUs sit idle even if model code is correct.

### Parallelism Types

Large-model training usually combines several kinds of parallelism.

| Type | Mental model | What it solves | Cost |
| ---- | ------------ | -------------- | ---- |
| Data parallelism | Replicate model, split data | More batch throughput | Gradient synchronization |
| Tensor parallelism | Split matrix operations across GPUs | Layers too large for one GPU | Frequent communication |
| Pipeline parallelism | Split layers across stages | Model depth too large for one GPU | Pipeline bubbles and scheduling |
| Sequence parallelism | Split sequence dimension or related activations | Long sequence activation memory | More complex implementation |
| Expert parallelism | Place MoE experts across devices | Many experts / large sparse models | Routing and load balance |

Mental model:

```text
data parallelism splits examples
tensor parallelism splits math inside layers
pipeline parallelism splits layers
sequence parallelism splits long-token activations
expert parallelism splits sparse expert capacity
```

Why this matters:

When a training run is slow, you need to know whether the bottleneck is compute, memory, communication, pipeline bubbles, data loading, or checkpointing. Parallelism choices change all of those.

Interview framing:

> Distributed training is not one trick. I would choose the parallelism strategy based on what does not fit: batch size, parameters, activations, sequence length, or expert capacity. Then I would monitor GPU utilization, communication time, memory, data loading, and checkpoint overhead.

### Scale-Up, Scale-Out, and MoE Rack Layout

Large sparse models are shaped by physical hardware topology.

Two network domains matter:

| Domain | Mental model | Typical property |
| ------ | ------------ | ---------------- |
| Scale-up | fast local accelerator fabric inside a rack or pod | high bandwidth, low latency, dense connectivity |
| Scale-out | network between racks or pods | slower, more hops, more topology constraints |

MoE layers are especially sensitive to this because expert routing creates all-to-all communication.

Mental model:

```text
tokens on every GPU
  -> router chooses experts
  -> tokens are sent to expert GPUs
  -> expert outputs are sent back and combined
```

If experts live inside one fast scale-up domain, any GPU can send tokens to any expert with high bandwidth. If the expert layer crosses rack boundaries, many routed tokens must use slower scale-out links.

This is why one rack or one scale-up domain becomes a natural boundary for an MoE layer. The model architecture wants:

```text
all-to-all expert traffic
  -> fast dense interconnect
  -> keep experts inside the scale-up domain when possible
```

Interview framing:

> MoE is not just an algorithmic sparsity trick. It creates an all-to-all communication pattern, so the physical interconnect can determine how large an expert-parallel group should be.

### Why Expert Parallelism Fits MoE

Expert parallelism places different experts on different devices.

This matches the structure of an MoE layer:

```text
many experts
  -> split experts across GPUs
  -> route tokens to the selected experts
```

The good part:

* active compute per token can stay low,
* total parameter capacity can grow,
* each GPU only owns a subset of experts.

The hard part:

* token routing can be imbalanced,
* all-to-all communication can dominate,
* expert placement must respect topology,
* larger sparsity may need larger batches to amortize weight movement,
* total parameter memory still has to fit somewhere.

This is the systems reason sparse models often depend on careful co-design between model architecture, router behavior, batch size, and hardware topology.

### Pipeline Parallelism Limits

Pipeline parallelism splits layers across stages:

```text
layers 1-20 -> stage 1
layers 21-40 -> stage 2
layers 41-60 -> stage 3
```

It helps when model weights do not fit in one device or one scale-up domain.

But it introduces pipeline bubbles:

```text
start of batch:
  later stages wait

end of batch:
  earlier stages wait
```

Micro-batches reduce idle time by keeping multiple chunks in flight. This is easier during inference because there is only a forward pass. During training, the backward pass, gradient accumulation, and optimizer step make scheduling much more complicated.

The deeper limitation for LLM inference is KV cache.

Pipeline parallelism divides model weights across stages, but it does not necessarily reduce KV-cache pressure in the way people first expect. To keep $P$ pipeline stages busy, the system often needs roughly $P$ micro-batches in flight. Splitting layers across $P$ stages reduces per-stage KV layers, but increasing in-flight micro-batches pushes active sequence count up. Those effects can cancel.

Mental model:

```text
pipeline parallelism:
  helps weight capacity
  adds scheduling complexity
  creates bubbles
  can add cross-stage latency
  does not magically solve long-context KV pressure
```

This is why pipeline parallelism is often a tradeoff rather than a pure win.

### Pipeline Parallelism and Research Iteration

Pipeline boundaries can also constrain architecture.

If a model has simple sequential layers, splitting layers across stages is natural. But newer architectures may include:

* attention patterns that refer to residuals from many previous layers,
* alternating global and local attention layers,
* nonuniform MoE or routing behavior,
* layer types with very different compute or memory cost.

Those features can create load imbalance or force awkward cross-stage communication.

The engineering risk:

```text
parallelism scheme hard-codes architecture assumptions
  -> model researchers avoid changes that break the system
  -> iteration slows down
```

Strong infrastructure should support the model architecture rather than accidentally dictating it.

### Checkpointing and Fault Tolerance

Large training jobs fail.

They fail because:

* nodes die,
* GPUs error,
* network links degrade,
* jobs are preempted,
* storage stalls,
* code has bugs,
* data shards are corrupt.

Checkpointing is what makes failure recoverable.

A good checkpoint includes:

* model parameters,
* optimizer state,
* scheduler state,
* random number generator state,
* data-loader position or shard state,
* training step,
* config,
* code/data version references.

For very large models, checkpoints are often sharded. That means restore logic must know how shards map back to distributed ranks.

Interview framing:

> I would design checkpointing as part of the training system, not an afterthought. A checkpoint should allow reliable resume with the same optimizer, scheduler, data position, and config. I would test restore regularly because untested checkpoints are just expensive files.

---

## 1.7 Inference and Serving Stack

Serving systems turn trained models into product behavior.

Mental model:

```text
request
  -> gateway
  -> router
  -> queue / batcher
  -> model runtime
  -> stream tokens
  -> trace
```

### vLLM

vLLM is a high-throughput LLM serving system.

Mental model:

```text
continuous batching + efficient KV cache management
```

It is known for PagedAttention, which manages KV cache memory more efficiently.

Good for:

* high-throughput LLM serving,
* many concurrent requests,
* open-weight model deployment.

Interview focus:

* continuous batching,
* KV-cache pressure,
* prefill vs decode,
* throughput vs latency.

### TGI

Text Generation Inference is Hugging Face's LLM serving stack.

Mental model:

```text
standardized server for text generation models
```

Good for:

* serving Hugging Face-compatible models,
* production-ish deployment,
* streaming generation,
* batching and model management.

### Triton Inference Server

Triton Inference Server serves models across multiple frameworks.

Mental model:

```text
model repository + inference server + batching + multiple backends
```

Good for:

* heterogeneous model serving,
* non-LLM inference,
* ensembles,
* GPU inference services.

Do not confuse Triton Inference Server with the Triton language for writing GPU kernels.

### Ray Serve

Ray Serve is Python-native model serving on top of Ray.

Mental model:

```text
Python deployments + distributed routing + autoscaling
```

Good for:

* Python-heavy inference pipelines,
* multi-stage inference graphs,
* custom routing,
* integration with Ray workloads.

### FastAPI and Starlette

FastAPI and Starlette sit at the API layer.

Mental model:

```text
HTTP request -> validation -> async handler -> response
```

They compose with:

* Pydantic schemas,
* async model clients,
* Redis,
* queues,
* tracing middleware,
* auth systems.

They should not become the whole inference platform. Keep API concerns separate from GPU/runtime concerns.

### Redis and Queues

Redis is often used for:

* caching,
* rate limiting,
* coordination,
* lightweight queues,
* session state.

Celery, Dramatiq, and RQ provide background task queues.

Mental model:

```text
API accepts work -> queue stores work -> workers process work
```

Failure modes:

* unbounded queue growth,
* duplicate jobs,
* stuck jobs,
* missing idempotency,
* overloaded workers,
* stale cache values.

---

## 1.8 Data Engineering and ETL Stack

Data systems feed training, retrieval, evals, monitoring, and learning loops.

Mental model:

```text
raw events
  -> durable storage
  -> transformation
  -> features / evals / training data
  -> monitoring
```

### Spark

Spark is distributed batch processing.

Mental model:

```text
large dataset -> partitioned transformations -> distributed execution
```

Good for:

* large historical datasets,
* joins,
* aggregations,
* feature generation,
* ETL.

Failure modes:

* shuffles dominate runtime,
* skewed partitions,
* memory pressure,
* expensive joins,
* poor file layout.

### Beam

Beam provides a unified batch and streaming programming model.

Mental model:

```text
pipeline definition -> runner executes it
```

The same logical pipeline can run on different runners.

Good for:

* systems that need both batch and streaming semantics,
* windowing,
* event-time processing,
* portability across execution engines.

### Dask

Dask is Python-native distributed computation.

Mental model:

```text
familiar Python dataframe/array tasks -> distributed scheduler
```

Good for:

* Python teams,
* parallel dataframes,
* custom workflows,
* workloads that do not fit neatly into Spark.

### Kafka

Kafka is a durable event log.

Mental model:

```text
producers -> append events to topics -> consumers read offsets
```

Good for:

* streaming events,
* decoupling services,
* replay,
* near-real-time features,
* monitoring pipelines.

Failure modes:

* consumer lag,
* bad partition keys,
* duplicate processing,
* schema evolution,
* poison messages.

### Airflow, Dagster, Prefect

These orchestrate workflows.

Mental model:

```text
task graph -> scheduler -> retries -> lineage/metadata
```

Airflow is widely used for scheduled DAGs. Dagster emphasizes software-defined assets and lineage. Prefect emphasizes Pythonic workflows and operational ergonomics.

### dbt

dbt is a SQL transformation and analytics engineering tool.

Mental model:

```text
raw warehouse tables -> versioned SQL models -> tested analytical datasets
```

It is useful when the transformation layer is mostly SQL and teams need tests, lineage, documentation, and repeatability.

### Object Stores and Warehouses

S3 and GCS are common storage backbones.

Mental model:

```text
cheap durable object storage for datasets, checkpoints, logs, artifacts
```

Warehouses like BigQuery, Snowflake, and Redshift support analytical querying.

They are not usually low-latency request-path databases. They are for analytics, training data, eval analysis, and reporting.

### Feature Stores

A feature store manages reusable ML features across training and serving.

Mental model:

```text
feature definition
  -> offline historical values
  -> online low-latency values
  -> consistent training and serving access
```

Examples include Feast-style systems and custom internal feature platforms.

Why they matter:

* reduce training-serving skew,
* centralize feature definitions,
* support point-in-time correct training data,
* provide online low-latency feature lookup,
* improve reuse across models.

Tradeoffs:

* operational complexity,
* feature ownership,
* freshness guarantees,
* backfill complexity,
* online/offline consistency.

Interview framing:

> I would use a feature store when multiple models need shared, versioned, point-in-time-correct features with online serving. For simpler systems, a warehouse plus careful pipeline contracts may be enough.

---

## 1.9 Retrieval, Search, and Knowledge Systems Stack

Knowledge systems are central to applied AI.

Mental model:

```text
documents
  -> parsing
  -> chunking
  -> embeddings / sparse index
  -> retrieval
  -> reranking
  -> context assembly
  -> model
```

### FAISS

FAISS is a library for vector search.

Mental model:

```text
local vector index inside your own service or batch job
```

Good for:

* experiments,
* local indexes,
* custom retrieval systems,
* high-performance vector search when you own the service layer.

Tradeoff:

You manage persistence, metadata, filtering, scaling, and service APIs yourself.

### pgvector

pgvector adds vector search to Postgres.

Mental model:

```text
relational metadata + vector similarity in one database
```

Good for:

* small to medium corpora,
* apps already using Postgres,
* strong metadata filtering,
* simpler operations.

Tradeoff:

It may not match dedicated vector systems at very large scale or specialized latency targets.

### Managed Vector Databases

Examples include Pinecone, Weaviate, and Milvus-style systems.

Mental model:

```text
dedicated vector retrieval service
```

Good for:

* larger corpora,
* operational offload,
* vector-specific indexing and scaling,
* APIs around metadata and namespaces.

Tradeoff:

You add a specialized dependency, cost, and possible vendor/platform constraints.

### Elasticsearch and OpenSearch

These are sparse search systems.

Mental model:

```text
inverted index over terms + filtering + ranking
```

Good for:

* BM25,
* exact term matching,
* logs,
* document search,
* filters and facets.

They compose well with dense retrieval in hybrid search.

### Rerankers

Rerankers improve precision after first-stage retrieval.

Mental model:

```text
retrieve many candidates cheaply -> score fewer candidates carefully
```

Cross-encoder rerankers look at query and document together, which is often better but slower.

### Knowledge Graphs

Knowledge graphs organize entities and relationships.

Mental model:

```text
entities + relations + attributes -> graph queries and reasoning
```

Good for:

* structured relationships,
* provenance,
* entity-centric retrieval,
* multi-hop queries.

Tradeoff:

They require schema design, entity resolution, maintenance, and often still need text retrieval alongside them.

---

## 1.10 Evaluation and Experimentation Stack

Evals are the bridge between change and confidence.

Mental model:

```text
candidate change
  -> fixed eval set
  -> metrics and slices
  -> trace inspection
  -> ship / canary / rollback
```

### pytest

pytest is deterministic software testing.

Use it for:

* schema validators,
* prompt rendering,
* tool argument validation,
* retrieval filters,
* deterministic business rules,
* regression tests around known failures.

### Eval Harnesses

OpenAI Evals-style or custom harnesses run model/system behavior against datasets.

They should track:

* input,
* expected behavior,
* model output,
* scoring rubric,
* model version,
* prompt version,
* retrieval context,
* tool traces.

### LangSmith, Braintrust, Ragas-Style Tools

These tools help with traces, datasets, model comparison, and RAG evaluation.

Mental model:

```text
production/eval traces -> labeled datasets -> comparison runs -> failure analysis
```

Do not treat any eval platform as magic. The quality comes from good datasets, clear rubrics, and careful slice analysis.

### W&B and MLflow

W&B and MLflow track experiments, metrics, artifacts, and models.

Mental model:

```text
run config + code version + data version + metrics + artifacts
```

Track:

* hyperparameters,
* model config,
* dataset version,
* checkpoint path,
* metrics,
* eval results,
* logs,
* system utilization,
* random seed,
* code commit.

### Hydra and Config Systems

Config systems make experiments reproducible.

Mental model:

```text
experiment = code + data + config + seed + environment
```

Without configuration discipline, research results become hard to reproduce.

### Model Registries and Artifact Stores

Model registries track deployable model artifacts and their metadata.

Mental model:

```text
model artifact + metadata + lineage + approval state -> deployable version
```

A good registry tracks:

* model weights,
* tokenizer,
* base model and adapter,
* training data version,
* eval results,
* safety review status,
* owner,
* deployment status,
* rollback target.

Artifact stores hold the underlying files:

* checkpoints,
* datasets,
* eval outputs,
* logs,
* generated samples,
* model cards.

Why this matters:

A model is not just a `.pt` file. It is a bundle of weights, tokenizer, config, data lineage, eval evidence, and deployment policy.

Interview framing:

> I would not ship an anonymous checkpoint. I would promote a model through a registry with versioned artifacts, eval results, owner metadata, and rollback information.

### CI for Research and ML Infrastructure

Research code still needs tests.

Useful checks:

* unit tests for data transforms,
* small overfit tests for training loops,
* shape tests for model changes,
* deterministic smoke tests,
* checkpoint save/restore tests,
* eval harness regression tests,
* lint/type checks for production code,
* launch tests for distributed job configs.

The job-role signal is clear: teams want infrastructure that lets researchers move quickly without breaking the pipeline.

Interview framing:

> I would build CI that catches cheap failures before expensive GPU runs: import errors, config mistakes, data schema breaks, shape mismatches, checkpoint restore failures, and small training-loop regressions.

---

## 1.11 Observability and Reliability Stack

Observability answers:

> What happened, where, and why?

Mental model:

```text
request id
  -> spans
  -> metrics
  -> logs
  -> dashboard
  -> alert
  -> incident response
```

### OpenTelemetry

OpenTelemetry standardizes instrumentation for traces, metrics, and logs.

Mental model:

```text
instrument code once -> export telemetry to different backends
```

In AI systems, spans should cover:

* prompt construction,
* retrieval,
* reranking,
* model call,
* tool call,
* validation,
* streaming,
* database queries.

### Prometheus

Prometheus collects and queries time-series metrics.

Good for:

* counters,
* gauges,
* histograms,
* latency percentiles,
* service health,
* queue depth,
* GPU utilization if exported.

### Grafana

Grafana visualizes metrics and logs from multiple sources.

Mental model:

```text
metrics source -> dashboard -> operational picture
```

Good dashboards answer a debugging question. They are not just charts.

### Datadog-Style Platforms

Hosted observability platforms combine metrics, traces, logs, dashboards, and alerts.

Mental model:

```text
one operational surface for service behavior
```

Useful when teams need integrated incident debugging and do not want to run every observability component themselves.

### Sentry

Sentry focuses on application errors and exceptions.

Good for:

* stack traces,
* error grouping,
* release tracking,
* user/session context.

For AI systems, make sure sensitive prompts and retrieved content are redacted.

---

## 1.12 Cloud, Containers, and Sandboxing Stack

AI systems run inside infrastructure.

Mental model:

```text
code + dependencies
  -> image
  -> isolated runtime
  -> scheduled workload
  -> monitored execution
```

### Docker

Docker packages code and dependencies into images.

Good for:

* reproducible services,
* consistent worker environments,
* deployment pipelines,
* local/prod parity.

Failure modes:

* huge images,
* dependency drift,
* missing GPU runtime configuration,
* secrets baked into images,
* slow cold starts.

### Kubernetes

Kubernetes schedules and manages containers.

It composes with:

* Docker/container images,
* service meshes,
* ingress controllers,
* autoscalers,
* GPU node pools,
* observability agents,
* config/secrets systems.

For AI, Kubernetes is common for services and inference fleets, but research training may still use Slurm or specialized schedulers.

### AWS and GCP

Cloud platforms provide:

* compute,
* GPUs/TPUs,
* object storage,
* managed databases,
* networking,
* IAM,
* logging,
* managed Kubernetes,
* warehouses.

Mental model:

```text
managed building blocks + operational contracts + cost model
```

Interview focus:

Do not list services. Explain how compute, storage, networking, identity, and observability compose.

### VMs and Sandboxing

Agents that run code or use computers need isolation.

Mental model:

```text
untrusted action -> isolated environment -> controlled outputs
```

Sandboxing protects:

* host filesystem,
* network,
* credentials,
* other tenants,
* production systems.

Technologies and concepts:

* VMs,
* containers,
* gVisor-style syscall isolation,
* Firecracker-style microVMs,
* seccomp,
* network policies,
* resource limits.

The point is not the brand name. The point is the boundary.

---

## 1.13 Performance and Systems Languages

Python is the orchestration language for much of AI, but performance often comes from lower layers.

Mental model:

```text
Python orchestration
  -> native runtimes
  -> kernels
  -> hardware execution
```

### CUDA

CUDA is NVIDIA's programming model for GPUs.

Mental model:

```text
many lightweight threads execute the same kernel over data in parallel
```

The execution hierarchy is:

```text
grid
  -> blocks
  -> warps
  -> threads
```

* A **thread** executes one lane of work.
* A **warp** is a group of threads that execute in lockstep on NVIDIA GPUs.
* A **block** is a group of threads that can cooperate through shared memory.
* A **grid** is the full set of blocks launched for a kernel.

This is why GPU code works best when the same operation is applied across many data elements with regular memory access. Branch-heavy or irregular workloads can underuse the hardware because different threads in the same warp want to do different things.

You do not need to write CUDA for every role, but you should understand why GPU performance depends on:

* memory bandwidth,
* kernel fusion,
* occupancy,
* communication,
* data movement,
* tensor shapes.

Key performance intuition:

```text
slow path:
  CPU loop calls many tiny GPU operations

better path:
  one larger fused kernel does more work per launch
```

Kernel launches have overhead. CPU-GPU transfers have overhead. Moving data repeatedly between host memory and device memory can dominate runtime even when each individual operation is fast.

For AI workloads, many optimizations come from:

* keeping tensors on the GPU,
* fusing operations to reduce intermediate reads/writes,
* choosing tensor shapes that hit efficient kernels,
* increasing arithmetic intensity,
* reducing synchronization points,
* overlapping compute and communication when possible.

Interview framing:

> I do not need to hand-write CUDA to reason about GPU performance. I would look for CPU-GPU transfers, many small kernel launches, poor tensor shapes, memory-bandwidth limits, and synchronization. The high-level fix is usually to batch, fuse, keep data resident, and use optimized kernels.

### Triton Language

Triton is a Python-like language for writing GPU kernels.

Mental model:

```text
write custom tensor kernel -> compile to efficient GPU code
```

It is often used when framework operations are not efficient enough or when a new attention/MLP/kernel pattern needs optimization.

Do not confuse Triton language with Triton Inference Server.

### C++

C++ is used for:

* runtimes,
* inference engines,
* high-performance services,
* native extensions,
* kernels,
* systems where latency and memory control matter.

Mental model:

```text
manual control and performance at the cost of complexity
```

### Rust

Rust is used when teams want systems-level performance with stronger memory safety.

Good fits:

* control-plane services,
* sandboxes,
* CLIs,
* high-reliability infrastructure,
* agents/tools that need safety boundaries.

### OS Internals

OS fundamentals matter for:

* processes,
* threads,
* memory,
* files,
* sockets,
* scheduling,
* signals,
* containers,
* cgroups.

Many AI infra bugs are OS bugs wearing ML clothing: file descriptor leaks, process zombies, memory pressure, slow disks, network timeouts, or bad scheduling.

---

## 1.14 Agent and Tooling Stack

Agent systems compose models with state, tools, and control flow.

Mental model:

```text
state
  -> policy / model
  -> tool or action
  -> observation
  -> state update
  -> stop condition
```

### LangGraph

LangGraph models agent workflows as graphs of state transitions.

Good for:

* explicit state,
* multi-step workflows,
* branching,
* controlled loops,
* tool use.

Mental model:

```text
stateful graph, not free-form chat
```

### Temporal

Temporal is durable workflow orchestration.

Good for:

* long-running workflows,
* retries,
* durable state,
* human approvals,
* compensation logic,
* exactly-once-ish business processes.

Mental model:

```text
workflow state persists outside the worker process
```

Temporal solves reliability problems that prompts cannot solve.

### MCP

MCP standardizes how models and agents access tools and context.

Mental model:

```text
agent client -> standardized server -> tools/resources/prompts
```

It matters because tool integration becomes more reusable when context and actions have a standard interface.

### Sandboxed Code Execution

Code agents need to run untrusted or model-generated code safely.

Components:

* isolated filesystem,
* restricted network,
* timeouts,
* CPU/memory limits,
* process cleanup,
* audit logs,
* artifact capture.

This composes with containers, VMs, workflow engines, and evaluation environments.

---

## 1.15 Stack Patterns by Role Type

Different roles emphasize different combinations.

### RL Infrastructure / Post-Training Engineer

Core stack:

```text
PyTorch or JAX
  -> Transformers / custom model code
  -> rollout workers
  -> reward model
  -> PPO / DPO / RLHF trainer
  -> distributed scheduler
  -> checkpoint store
  -> eval harness
  -> W&B / MLflow
  -> Prometheus / Grafana / OpenTelemetry
```

What to know:

* distributed training,
* rollout throughput,
* reward pipeline reliability,
* checkpointing,
* reproducibility,
* GPU utilization,
* debugging slowdowns after many steps.

### Knowledge / Retrieval Engineer

Core stack:

```text
document ingestion
  -> parsing / chunking
  -> embedding model
  -> FAISS / pgvector / vector DB
  -> Elasticsearch / OpenSearch
  -> reranker
  -> context builder
  -> model API
  -> RAG evals
```

What to know:

* dense vs sparse retrieval,
* metadata filtering,
* access control,
* ranking,
* query understanding,
* index freshness,
* citation support,
* knowledge graph tradeoffs.

### Inference / Serving Engineer

Core stack:

```text
FastAPI / gateway
  -> auth / quota
  -> router
  -> Redis cache
  -> queue / batcher
  -> vLLM / TGI / Triton / Ray Serve
  -> GPU workers
  -> OpenTelemetry / Prometheus / Grafana
```

What to know:

* prefill vs decode,
* batching,
* KV cache,
* GPU memory,
* streaming,
* admission control,
* cost per token,
* fallback behavior.

### Research Infrastructure Engineer

Core stack:

```text
PyTorch / JAX
  -> distributed training framework
  -> Slurm / Kubernetes / Ray
  -> object storage checkpoints
  -> data pipeline
  -> experiment tracker
  -> observability
```

What to know:

* researcher ergonomics,
* reproducibility,
* cluster utilization,
* debugging distributed jobs,
* data throughput,
* checkpoint reliability,
* performance profiling.

### Agent Platform Engineer

Core stack:

```text
model API
  -> LangGraph / custom orchestrator
  -> Temporal / durable workflow
  -> MCP / tool registry
  -> sandboxed execution
  -> retrieval
  -> eval harness
  -> observability
```

What to know:

* explicit state,
* tool permissions,
* idempotency,
* durable workflows,
* human approvals,
* sandboxing,
* trace-based debugging.

---

# 12. Chapter Takeaways

Software engineering fundamentals are not separate from applied AI. They are what make applied AI usable.

Key ideas:

* Python runtime behavior matters because AI payloads are large and services are long-running.
* The GIL matters when choosing between threads, processes, async, and native code.
* Async is powerful for IO-bound orchestration, but blocking the event loop can break the whole service.
* Memory leaks usually come from reachable objects, unbounded caches, traces, tasks, or native allocations.
* SQL performance depends on query plans, indexes, partitioning, materialization, and realistic data.
* Distributed data systems trade simplicity for capacity and availability.
* ML data pipelines need schema contracts, lineage, validation, backfills, and skew monitoring.
* Scalable AI backends need separation between API orchestration and inference execution.
* Tech stacks should be learned as abstractions and failure modes, not as brand-name checklists.
* PyTorch, TensorFlow, and JAX differ mainly in execution and transformation mental models.
* Distributed training, serving, retrieval, evals, and observability each have distinct stack layers that must compose cleanly.
* Observability is not optional; it is how you debug probabilistic systems.

Compact interview framing:

> A production AI system is a normal distributed system with an unusually expensive, probabilistic core. I need to reason about Python runtime behavior, data systems, queues, caches, model calls, framework execution, distributed training, serving stacks, and observability together, because failures usually appear at the boundaries.

---

# 13. Bridge to ML Systems and Inference Engineering

Chapter 11 teaches the software and stack vocabulary. [Chapter 13](../chapter_13/guide.html) goes deeper into the runtime and hardware behavior behind that vocabulary.

The reinforcement mental model is:

```text
frameworks are bottleneck-management tools
```

PyTorch optimizes development flexibility, JAX and XLA emphasize compilation and transformations, ONNX gives portability, TensorRT optimizes NVIDIA execution, vLLM manages KV-cache-heavy serving, Ray manages distributed Python work, and Kubernetes manages container orchestration. Strong answers explain what resource each layer manages instead of listing tool names.
