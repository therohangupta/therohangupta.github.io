# RLHF / Post-Training Infrastructure Stack

Post-training systems are distributed feedback loops.

## Core Loop

```text
prompt dataset
  -> policy model
  -> rollout workers
  -> reward model / preference labels
  -> PPO / DPO / RLHF update
  -> checkpoint
  -> eval harness
  -> next policy
```

## Components

### Policy Model

Common stack:

- PyTorch or JAX,
- Transformers or custom model code,
- FSDP or DeepSpeed for memory scaling.

### Rollout Workers

Rollout workers generate trajectories.

They may call:

- model servers,
- tool environments,
- code sandboxes,
- simulated users,
- reward services.

### Reward / Preference Layer

Can be:

- human preference labels,
- reward model scores,
- rule-based validators,
- task outcomes,
- judge model scores.

### Trainer

Common algorithms:

- SFT,
- PPO,
- DPO,
- reward-model training,
- rejection sampling / best-of-N style loops.

### Distributed Execution

Possible stack:

- Slurm for batch GPU jobs,
- Kubernetes for services/workers,
- Ray for rollout orchestration,
- NCCL for GPU collectives,
- object storage for checkpoints.

### Experiment Tracking

Track:

- policy checkpoint,
- reward model version,
- prompt dataset version,
- rollout config,
- algorithm hyperparameters,
- eval results,
- throughput,
- failure rates.

Tools:

- W&B,
- MLflow,
- custom dashboards,
- Prometheus/Grafana/OpenTelemetry.

## Failure Modes

- Rollout workers are slower than the learner.
- Reward model service becomes the bottleneck.
- Tool environments leak state across episodes.
- Checkpoints are missing or inconsistent.
- PPO run becomes unstable.
- DPO dataset has bad chosen/rejected labels.
- Training throughput drops after many steps.
- Eval improves while safety regresses.

## Interview Framing

> I would design RLHF infrastructure as a distributed loop: rollout generation, reward/preference scoring, policy update, checkpointing, and eval. The hard parts are throughput, reproducibility, reward correctness, distributed training stability, and observability.

