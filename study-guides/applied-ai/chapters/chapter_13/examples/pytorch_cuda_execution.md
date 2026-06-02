# PyTorch CUDA Execution

This example lists the runtime behaviors that commonly surprise applied AI engineers.

## Async Execution

Many CUDA operations are asynchronous. Python may enqueue GPU work and continue before the GPU finishes.

Bad benchmark:

```python
start = time.time()
y = model(x)
elapsed = time.time() - start
```

Better benchmark:

```python
torch.cuda.synchronize()
start = time.time()
y = model(x)
torch.cuda.synchronize()
elapsed = time.time() - start
```

## Hidden Synchronization

Common synchronization points:

* `.item()`,
* copying tensors to CPU,
* printing GPU tensors,
* some logging paths,
* explicit `torch.cuda.synchronize()`.

## Tensor Layout

A tensor has shape and storage layout. Non-contiguous views can trigger hidden copies or inefficient memory access.

Checklist:

* inspect shape, dtype, device, and stride,
* check whether repeated `.contiguous()` calls are hiding costs,
* benchmark representative shapes,
* warm up compiled or cached paths before timing.

## Allocator Behavior

PyTorch uses a caching allocator. Memory may remain reserved after tensors are freed. That is often normal. In long-running servers, fragmentation and changing sequence sizes can still cause OOM.
