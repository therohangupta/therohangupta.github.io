# Compiled Model Release Checklist

Treat a compiled model or inference engine as a release artifact. The compiled path can change latency, memory use, numerical behavior, supported shapes, and failure modes.

## Artifact

```text
source model: support-reranker-v4.pt
export: support-reranker-v4.onnx
runtime: TensorRT
precision: FP16
shape profile: batch 1-64, sequence 64-1024
target GPU: L4
```

## Validation Checklist

* Compare outputs against the source model on representative examples.
* Run regression evals on critical slices.
* Test minimum, typical, and maximum shape profiles.
* Verify unsupported operators are not silently replaced with poor fallbacks.
* Measure p50, p95, p99 latency.
* Measure peak memory and steady-state memory.
* Confirm cold-start behavior and engine load time.
* Test rollback to the previous artifact.
* Record compiler/runtime versions.

## Common Failures

| Failure | Detection |
| ------- | --------- |
| numerical drift | source-vs-engine output comparison |
| bad dynamic shape profile | latency by shape bucket |
| unsupported operator | export logs and runtime errors |
| precision regression | eval slices and golden examples |
| memory increase | peak memory benchmark |
| engine rebuild latency | startup and deploy tests |

## Rollout Plan

1. Shadow traffic and compare outputs.
2. Send 1% of low-risk traffic.
3. Increase by tenant or traffic class.
4. Watch quality, latency, memory, and error metrics.
5. Roll back if any critical slice regresses.

## Interview Framing

Compilation is not just an optimization flag. It changes the executable artifact. I would validate correctness, shape behavior, performance, and rollback before treating it as production-safe.
