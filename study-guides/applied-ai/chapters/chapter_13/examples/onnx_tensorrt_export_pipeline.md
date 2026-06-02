# ONNX and TensorRT Export Pipeline

Treat export and compilation as a release pipeline.

```text
PyTorch model
  -> export to ONNX
  -> validate graph
  -> build TensorRT engine
  -> benchmark shape profiles
  -> compare outputs
  -> canary rollout
```

## Checks

| Step | What Can Go Wrong |
| ---- | ----------------- |
| export | unsupported ops, dynamic control flow, version mismatch |
| graph validation | shape inference fails, wrong dtypes |
| TensorRT build | poor optimization profile, unsupported precision |
| benchmarking | fixed-shape benchmark hides production variance |
| output comparison | numerical drift or slice-specific regressions |
| rollout | cold-start or engine-load behavior surprises production |

## Release Record

```json
{
  "source_model": "reranker-v4.pt",
  "export": "reranker-v4.onnx",
  "runtime": "tensorrt",
  "precision": "fp16",
  "shape_profile": "batch=1..64, seq=64..1024",
  "target_gpu": "l4",
  "rollback_artifact": "reranker-v3.engine"
}
```

## Interview Framing

ONNX gives portability. TensorRT gives NVIDIA-specific optimization. Neither removes the need to validate correctness, shape behavior, latency, memory, and rollback.
