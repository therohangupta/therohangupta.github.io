# GPU Memory Hierarchy

The practical mental model is:

```text
registers -> shared memory -> L1/L2 cache -> HBM/VRAM -> CPU RAM -> disk/network
```

Faster memory is smaller. Larger memory is slower. Many ML systems optimizations try to keep useful data closer to compute for longer.

| Level | Why It Matters |
| ----- | -------------- |
| registers | fastest storage for values used inside a thread |
| shared memory | fast block-local memory useful for tiled reuse |
| L1/L2 cache | hardware-managed locality for repeated access |
| HBM / VRAM | large GPU memory, but expensive to access repeatedly |
| CPU RAM | larger, but crossing CPU-GPU boundaries is costly |
| disk / network | persistent and distributed, but far from compute |

## How Patterns Map to Memory

* Fusion keeps intermediates out of HBM when possible.
* Tiling reuses blocks in shared memory.
* Quantization moves fewer bytes through the hierarchy.
* FlashAttention avoids writing the full attention matrix to HBM.
* PagedAttention manages KV cache blocks so memory is less fragmented.

## Debugging Cue

If a workload has low arithmetic intensity, the question is not "how do I add more FLOPs?" It is "why am I moving so many bytes for so little useful work?"
