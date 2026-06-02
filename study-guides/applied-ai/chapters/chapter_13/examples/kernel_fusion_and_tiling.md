# Kernel Fusion and Tiling

Fusion and tiling are two of the most reusable ML systems ideas.

## Kernel Fusion

Naive execution:

```text
read A from HBM
compute op1
write intermediate to HBM
read intermediate from HBM
compute op2
write result to HBM
```

Fused execution:

```text
read A from HBM
compute op1 and op2 while intermediate is still close
write result to HBM
```

Fusion reduces memory traffic, kernel launches, and synchronization. It can hurt if the fused kernel becomes too large and reduces occupancy.

## Tiling

Tiling is about reuse:

```text
load a tile once -> reuse it many times -> move to the next tile
```

Matrix multiplication is the classic case. A tile of `A` and a tile of `B` can contribute to many outputs, so keeping them in fast memory increases arithmetic intensity.

## FlashAttention Connection

FlashAttention uses the same ideas for attention:

* tile attention blocks,
* avoid materializing the full attention matrix,
* fuse operations around each tile,
* recompute cheap values to avoid storing huge intermediates.

The lesson is that the fastest algorithm is often the one that moves less data.
