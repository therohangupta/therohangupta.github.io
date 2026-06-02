"""Memory gating and forgetting policy sketch.

Not every conversation turn should become memory. A gate decides whether the
candidate is durable, useful, scoped, and safe enough to store.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class CandidateMemory:
    text: str
    kind: str
    confidence: float
    contains_sensitive_data: bool = False
    user_id: str = "user-123"
    updated_at: datetime = datetime.now(timezone.utc)


def should_write_memory(candidate: CandidateMemory) -> tuple[bool, str]:
    if candidate.contains_sensitive_data:
        return False, "do not store sensitive data"
    if candidate.confidence < 0.8:
        return False, "confidence too low"
    if candidate.kind not in {"preference", "project", "profile"}:
        return False, "not durable enough"
    if len(candidate.text.split()) < 4:
        return False, "too little context"
    return True, "store"


def should_forget_memory(candidate: CandidateMemory, now: datetime, ttl_days: int = 90) -> tuple[bool, str]:
    if candidate.kind == "preference":
        ttl_days = 180
    if candidate.updated_at < now - timedelta(days=ttl_days):
        return True, "expired retention window"
    return False, "keep"


if __name__ == "__main__":
    candidates = [
        CandidateMemory("User prefers concise answers with examples.", "preference", 0.92),
        CandidateMemory("User mentioned password reset token abc123.", "secret", 0.95, True),
        CandidateMemory("Maybe likes charts.", "preference", 0.51),
    ]

    for candidate in candidates:
        print(candidate.text, "->", should_write_memory(candidate))
        print("forget?", should_forget_memory(candidate, datetime.now(timezone.utc)))
