"""
Toy continual learning and update gating example.

Continual learning should not mean "train on the newest data and deploy."
This sketch shows a candidate model update being promoted only if it improves
the target slice without regressing core capability or safety gates.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class EvalReport:
    model_version: str
    target_task_accuracy: float
    general_regression_accuracy: float
    safety_pass_rate: float
    hallucination_rate: float
    latency_p95_ms: int


@dataclass(frozen=True)
class GateThresholds:
    min_target_improvement: float = 0.02
    max_general_regression_drop: float = 0.01
    min_safety_pass_rate: float = 0.995
    max_hallucination_rate: float = 0.03
    max_latency_p95_ms: int = 2_000


def should_promote(
    baseline: EvalReport,
    candidate: EvalReport,
    thresholds: GateThresholds,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    target_gain = candidate.target_task_accuracy - baseline.target_task_accuracy
    if target_gain < thresholds.min_target_improvement:
        reasons.append(f"target gain too small: {target_gain:.3f}")

    general_drop = baseline.general_regression_accuracy - candidate.general_regression_accuracy
    if general_drop > thresholds.max_general_regression_drop:
        reasons.append(f"general regression too large: {general_drop:.3f}")

    if candidate.safety_pass_rate < thresholds.min_safety_pass_rate:
        reasons.append(f"safety pass rate too low: {candidate.safety_pass_rate:.3f}")

    if candidate.hallucination_rate > thresholds.max_hallucination_rate:
        reasons.append(f"hallucination rate too high: {candidate.hallucination_rate:.3f}")

    if candidate.latency_p95_ms > thresholds.max_latency_p95_ms:
        reasons.append(f"p95 latency too high: {candidate.latency_p95_ms}ms")

    return len(reasons) == 0, reasons


def main() -> None:
    baseline = EvalReport(
        model_version="policy-v4",
        target_task_accuracy=0.82,
        general_regression_accuracy=0.88,
        safety_pass_rate=0.997,
        hallucination_rate=0.025,
        latency_p95_ms=1_700,
    )

    candidate = EvalReport(
        model_version="policy-v5-continual",
        target_task_accuracy=0.86,
        general_regression_accuracy=0.875,
        safety_pass_rate=0.996,
        hallucination_rate=0.028,
        latency_p95_ms=1_850,
    )

    promote, reasons = should_promote(baseline, candidate, GateThresholds())
    if promote:
        print(f"promote {candidate.model_version} to canary")
    else:
        print(f"do not promote {candidate.model_version}:")
        for reason in reasons:
            print(f"- {reason}")


if __name__ == "__main__":
    main()
