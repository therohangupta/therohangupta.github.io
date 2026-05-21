"""
Preference data pipeline example.

This sketch turns logged model candidates into preference records that could
feed SFT, DPO, reward modeling, or evaluation. Production systems would add
privacy filtering, data retention controls, reviewer tooling, dataset versioning,
and quality audits.
"""

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CandidateLog:
    request_id: str
    prompt: str
    response_a: str
    response_b: str
    model_a: str
    model_b: str
    user_rating_a: int | None
    user_rating_b: int | None
    safety_flag_a: bool
    safety_flag_b: bool


@dataclass(frozen=True)
class PreferenceRecord:
    prompt: str
    chosen: str
    rejected: str
    label_source: str
    metadata: dict[str, str]


def build_preferences(logs: Iterable[CandidateLog]) -> list[PreferenceRecord]:
    records: list[PreferenceRecord] = []

    for log in logs:
        if log.safety_flag_a and not log.safety_flag_b:
            records.append(to_record(log, chosen="b", source="safety_rule"))
            continue

        if log.safety_flag_b and not log.safety_flag_a:
            records.append(to_record(log, chosen="a", source="safety_rule"))
            continue

        if log.user_rating_a is None or log.user_rating_b is None:
            continue

        if abs(log.user_rating_a - log.user_rating_b) < 2:
            # Small rating gaps are noisy. Send these to human review instead
            # of using them as confident training labels.
            continue

        chosen = "a" if log.user_rating_a > log.user_rating_b else "b"
        records.append(to_record(log, chosen=chosen, source="user_rating"))

    return records


def to_record(log: CandidateLog, chosen: str, source: str) -> PreferenceRecord:
    if chosen == "a":
        chosen_response = log.response_a
        rejected_response = log.response_b
    else:
        chosen_response = log.response_b
        rejected_response = log.response_a

    return PreferenceRecord(
        prompt=log.prompt,
        chosen=chosen_response,
        rejected=rejected_response,
        label_source=source,
        metadata={
            "request_id": log.request_id,
            "model_a": log.model_a,
            "model_b": log.model_b,
        },
    )


def main() -> None:
    logs = [
        CandidateLog(
            request_id="req-001",
            prompt="Explain vector databases.",
            response_a="They store embeddings for similarity search.",
            response_b="They are databases with vectors.",
            model_a="policy-v3",
            model_b="policy-v4",
            user_rating_a=5,
            user_rating_b=2,
            safety_flag_a=False,
            safety_flag_b=False,
        ),
        CandidateLog(
            request_id="req-002",
            prompt="Unsafe request",
            response_a="Here are unsafe steps.",
            response_b="I cannot help with that request.",
            model_a="policy-v3",
            model_b="policy-v4",
            user_rating_a=5,
            user_rating_b=1,
            safety_flag_a=True,
            safety_flag_b=False,
        ),
    ]

    for record in build_preferences(logs):
        print(record)


if __name__ == "__main__":
    main()
