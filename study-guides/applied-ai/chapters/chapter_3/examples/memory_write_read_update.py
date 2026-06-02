"""
Memory write/read/update example.

This sketch separates logs from memory. Only durable information becomes memory,
and each memory carries scope, type, confidence, and timestamp metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class Memory:
    memory_id: str
    user_id: str
    kind: str
    text: str
    confidence: float
    updated_at: datetime


class MemoryStore:
    def __init__(self) -> None:
        self.memories: dict[str, Memory] = {}

    def write_or_update(self, memory: Memory) -> None:
        existing = self.memories.get(memory.memory_id)
        if existing is None or memory.updated_at >= existing.updated_at:
            self.memories[memory.memory_id] = memory

    def read(self, user_id: str, query: str, limit: int = 3) -> list[Memory]:
        query_terms = set(query.lower().split())
        scoped = [memory for memory in self.memories.values() if memory.user_id == user_id]

        def score(memory: Memory) -> tuple[float, datetime]:
            overlap = len(query_terms & set(memory.text.lower().split()))
            return (overlap * memory.confidence, memory.updated_at)

        return sorted(scoped, key=score, reverse=True)[:limit]

    def forget_expired(self, now: datetime, ttl_days: int = 90) -> None:
        cutoff = now - timedelta(days=ttl_days)
        self.memories = {
            memory_id: memory
            for memory_id, memory in self.memories.items()
            if memory.updated_at >= cutoff
        }


def extract_candidate_memory(user_id: str, message: str) -> Memory | None:
    """Toy extractor. A real system would use a classifier or structured LLM call."""
    now = datetime.now(timezone.utc)
    lowered = message.lower()
    if "prefer concise" in lowered:
        return Memory(
            memory_id=f"{user_id}:preference:answer_length",
            user_id=user_id,
            kind="preference",
            text="User prefers concise answers.",
            confidence=0.95,
            updated_at=now,
        )
    if "working on billing migration" in lowered:
        return Memory(
            memory_id=f"{user_id}:project:billing_migration",
            user_id=user_id,
            kind="project",
            text="User is working on a billing migration project.",
            confidence=0.85,
            updated_at=now,
        )
    return None


def main() -> None:
    store = MemoryStore()
    user_id = "user-123"

    for message in [
        "I prefer concise answers.",
        "I am working on billing migration this week.",
    ]:
        candidate = extract_candidate_memory(user_id, message)
        if candidate:
            store.write_or_update(candidate)

    # Update an existing memory instead of storing a duplicate.
    existing = store.memories[f"{user_id}:preference:answer_length"]
    store.write_or_update(replace(existing, text="User prefers concise answers with examples."))

    print("Relevant memories:")
    for memory in store.read(user_id, "How should you answer my billing migration question?"):
        print(f"{memory.kind}: {memory.text}")

    store.forget_expired(datetime.now(timezone.utc), ttl_days=90)


if __name__ == "__main__":
    main()
