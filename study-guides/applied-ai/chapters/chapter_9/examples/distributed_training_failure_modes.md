# Distributed Training Failure Modes

Large training jobs are distributed systems with expensive failure modes.

## Parallelism Cheat Sheet

| Parallelism | Splits | Solves | Watch for |
| ----------- | ------ | ------ | --------- |
| Data parallelism | Examples | More throughput | Gradient sync time |
| Tensor parallelism | Layer math | Layers too large for one GPU | Communication inside layers |
| Pipeline parallelism | Layers | Model depth too large for one GPU | Pipeline bubbles |
| Sequence parallelism | Sequence activations | Long-context activation memory | Implementation complexity |
| Expert parallelism | MoE experts | Many sparse experts | Router imbalance |

## Checkpoint Contents

A reliable checkpoint should include:

- model parameters,
- optimizer state,
- scheduler state,
- random number generator state,
- data-loader or shard position,
- training step,
- config,
- code/data version metadata.

## Common Failure: Slowdown After Many Steps

Symptoms:

- GPU utilization drops.
- Step time increases.
- Data loader queue is empty.
- Checkpoint writes take longer.
- NCCL collectives wait.
- Memory fragmentation rises.

Debug order:

1. Compare compute time, communication time, and data-loading time.
2. Check GPU utilization and memory.
3. Inspect data-loader throughput and shard skew.
4. Check NCCL logs or collective timing.
5. Check checkpoint write duration and storage throughput.
6. Compare recent code/config/data changes.

## Common Failure: Restore Does Not Work

Causes:

- optimizer state not saved,
- wrong sharding metadata,
- missing tokenizer/config,
- data-loader position not restored,
- incompatible code version,
- checkpoint file partially written.

Prevention:

- save atomically,
- test restore in CI,
- store metadata with checkpoints,
- keep rollback checkpoints,
- record code and data versions.

## Interview Framing

> I would treat distributed training as a fault-tolerant system. Parallelism strategy decides the memory/communication tradeoff, and checkpointing decides whether failures are recoverable. I would monitor step time broken into compute, communication, data loading, and checkpoint overhead.

