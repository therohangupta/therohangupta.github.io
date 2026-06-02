"""
Simple profiling and bottleneck example.

The point is not exact timing. The point is to collect per-request stage
profiles, aggregate p50/p95, and classify bottlenecks from measurements instead
of guesses.
"""

from dataclasses import dataclass
from statistics import median


@dataclass(frozen=True)
class RequestProfile:
    request_id: str
    route: str
    queue_ms: float
    tokenization_ms: float
    retrieval_ms: float
    prefill_ms: float
    decode_ms: float
    tool_ms: float
    postprocess_ms: float

    @property
    def total_ms(self) -> float:
        return (
            self.queue_ms
            + self.tokenization_ms
            + self.retrieval_ms
            + self.prefill_ms
            + self.decode_ms
            + self.tool_ms
            + self.postprocess_ms
        )

    def __post_init__(self) -> None:
        for field, value in self.__dict__.items():
            if field.endswith("_ms") and value < 0:
                raise ValueError(f"{field} cannot be negative")


def largest_stage(profile: RequestProfile) -> tuple[str, float]:
    stages = {
        "queue": profile.queue_ms,
        "tokenization": profile.tokenization_ms,
        "retrieval": profile.retrieval_ms,
        "prefill": profile.prefill_ms,
        "decode": profile.decode_ms,
        "tool": profile.tool_ms,
        "postprocess": profile.postprocess_ms,
    }
    return max(stages.items(), key=lambda item: item[1])


def percentile(values: list[float], pct: float) -> float:
    values = sorted(values)
    index = min(int(round((pct / 100) * (len(values) - 1))), len(values) - 1)
    return values[index]


def summarize_profiles(profiles: list[RequestProfile], latency_budget_ms: float) -> dict[str, float | str]:
    if not profiles:
        raise ValueError("profiles are required")

    totals = [profile.total_ms for profile in profiles]
    worst = max(profiles, key=lambda profile: profile.total_ms)
    stage, duration = largest_stage(worst)
    return {
        "count": len(profiles),
        "p50_ms": median(totals),
        "p95_ms": percentile(totals, 95),
        "budget_ms": latency_budget_ms,
        "budget_exceeded": percentile(totals, 95) > latency_budget_ms,
        "worst_request": worst.request_id,
        "largest_stage": stage,
        "largest_stage_ms": duration,
    }


def suggest_optimization(stage: str) -> str:
    suggestions = {
        "queue": "Improve batching policy, add capacity, or route long requests separately.",
        "tokenization": "Move tokenization off the hot path or batch CPU preprocessing.",
        "retrieval": "Cache common retrievals, tune indexes, or reduce fanout.",
        "prefill": "Shorten prompts, batch prefill, or use attention optimizations.",
        "decode": "Use continuous batching, quantization, speculative decoding, or shorter outputs.",
        "tool": "Parallelize tool calls, cache tool results, or set stricter timeouts.",
        "postprocess": "Simplify validation and serialization work.",
    }
    return suggestions[stage]


if __name__ == "__main__":
    profiles = [
        RequestProfile("req-1", "faq", 12, 6, 30, 40, 120, 0, 6),
        RequestProfile("req-2", "agent", 25, 8, 90, 55, 240, 35, 7),
        RequestProfile("req-3", "long_context", 40, 14, 50, 220, 180, 0, 9),
    ]
    summary = summarize_profiles(profiles, latency_budget_ms=350)
    print(summary)
    print(suggest_optimization(str(summary["largest_stage"])))
