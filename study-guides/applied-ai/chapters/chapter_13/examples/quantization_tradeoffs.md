# Quantization Tradeoffs

Quantization is usually a memory and bandwidth optimization first.

## Decision Matrix

| Choice | Benefit | Risk |
| ------ | ------- | ---- |
| FP16/BF16 | faster tensor-core execution, lower memory | possible numerical issues |
| FP8 | strong throughput and memory savings | hardware/runtime maturity and calibration |
| INT8 weight + activation | lower bandwidth and faster supported kernels | calibration and quality risk |
| INT4 weight-only | large memory reduction | quality loss and limited kernels |

## Calibration

INT8 activation quantization needs representative calibration data. If calibration misses rare but important activation ranges, the model may pass aggregate evals while failing high-risk slices.

## Evaluation Gate

Before shipping quantization, compare:

* quality on task and risk slices,
* p50/p95/p99 latency,
* memory use,
* throughput at realistic batch sizes,
* hardware/runtime support,
* fallback behavior when unsupported shapes appear.

## Interview Framing

I would not ask "is INT8 better?" I would ask whether it improves cost or latency for the target traffic while preserving quality on important slices.
