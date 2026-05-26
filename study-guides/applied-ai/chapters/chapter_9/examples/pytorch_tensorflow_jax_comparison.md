# PyTorch vs TensorFlow vs JAX

## One-Line Mental Models

| Framework | Mental model |
| --------- | ------------ |
| PyTorch | Eager tensor programs plus autograd tape |
| TensorFlow | Graph-oriented computation with production/deployment paths |
| JAX | NumPy-like functions plus transformations |

## PyTorch

```text
Python control flow
  -> eager tensor operations
  -> autograd records operations
  -> backward computes gradients
```

Best for:

- research iteration,
- custom model code,
- debugging intermediate tensors,
- LLM ecosystem work.

Composes with:

- Transformers,
- DeepSpeed,
- FSDP,
- W&B/MLflow,
- Triton kernels,
- vLLM/TGI serving paths.

Common interview point:

> PyTorch is easy to debug and modify because execution is eager, but large-scale training still needs careful distributed systems work.

## TensorFlow

```text
Python-like model code
  -> traced or defined graph
  -> optimized execution
  -> serving/mobile artifact
```

Best for:

- production ML workflows,
- graph optimization,
- TensorFlow Serving,
- mobile/edge deployment,
- TFX-style pipelines.

Composes with:

- Keras,
- tf.data,
- TensorBoard,
- TensorFlow Serving,
- TFLite.

Common interview point:

> TensorFlow's graph mental model can make optimization and deployment cleaner, but dynamic research iteration can feel less direct.

## JAX

```text
pure-ish numerical function
  -> grad / jit / vmap / pmap transformations
  -> compiled execution
```

Best for:

- high-performance research,
- TPU/GPU scaling,
- functional training loops,
- vectorized experiments.

Composes with:

- XLA,
- Flax,
- Haiku,
- Optax,
- TPU pods,
- custom distributed training loops.

Common interview point:

> JAX gives powerful program transformations, but it rewards functional, shape-stable code and can be harder to debug when compilation is involved.

## Decision Framing

Do not say one is universally better.

Say:

> PyTorch optimizes for flexible research iteration, TensorFlow for graph/deployment-oriented production workflows, and JAX for composable transformations and compiled high-performance numerical programs.

