# Distributed Training Parallelism

Large training jobs combine parallelism strategies because no single strategy solves every bottleneck.

| Strategy | What It Splits | Helps With | Main Cost |
| -------- | -------------- | ---------- | --------- |
| DDP | data across replicated models | simple throughput scaling | gradient all-reduce |
| FSDP / ZeRO | parameters, gradients, optimizer states | memory capacity | gather/scatter communication |
| tensor parallelism | operations inside layers | very large layers | frequent communication |
| pipeline parallelism | layers into stages | model depth and memory | bubbles and scheduling |
| expert parallelism | MoE experts | sparse capacity | routing and all-to-all traffic |

## Memory Breakdown

```text
parameters + gradients + optimizer states + activations + temporary buffers
```

Optimizer states and activations can dominate memory. Gradient checkpointing trades extra compute for lower activation memory.

## Debugging Scaling

If 64 GPUs are not much faster than 8 GPUs, inspect:

* communication time,
* dataloader throughput,
* stragglers,
* batch size per GPU,
* checkpoint stalls,
* network topology,
* compute/communication overlap.
