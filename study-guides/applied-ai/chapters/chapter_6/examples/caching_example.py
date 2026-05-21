"""
Caching sketch.

This example uses an in-memory dictionary, but the same shape applies to Redis:
build a cache key that includes the model and prompt version, check the cache,
and only call the model on a miss.
"""

import hashlib
import json
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class CacheContext:
    tenant_id: str
    model_version: str
    prompt_version: str


@dataclass
class CacheEntry:
    value: str
    model_version: str
    prompt_version: str
    expires_at: float


class ResponseCache:
    def __init__(self) -> None:
        self._values: dict[str, CacheEntry] = {}
        self.metrics = {"hit": 0, "miss": 0, "expired": 0}

    def get(self, key: str) -> str | None:
        entry = self._values.get(key)
        if entry is None:
            self.metrics["miss"] += 1
            return None
        if entry.expires_at < time.time():
            self.metrics["expired"] += 1
            del self._values[key]
            return None
        self.metrics["hit"] += 1
        return entry.value

    def set(self, key: str, value: str, context: CacheContext, ttl_seconds: int = 300) -> None:
        self._values[key] = CacheEntry(
            value=value,
            model_version=context.model_version,
            prompt_version=context.prompt_version,
            expires_at=time.time() + ttl_seconds,
        )

    def invalidate_prompt_version(self, prompt_version: str) -> None:
        self._values = {
            key: entry
            for key, entry in self._values.items()
            if entry.prompt_version != prompt_version
        }


def cache_key(context: CacheContext, prompt: str) -> str:
    # Include all fields that change correctness. Avoid cross-tenant or cross-version reuse.
    payload = {
        "tenant_id": context.tenant_id,
        "model_version": context.model_version,
        "prompt_version": context.prompt_version,
        "prompt": prompt,
    }
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def call_model(prompt: str) -> str:
    return f"expensive answer for: {prompt}"


def generate_with_cache(cache: ResponseCache, context: CacheContext, prompt: str) -> dict:
    if len(prompt) > 4_000:
        return {"cache": "skip", "reason": "prompt too large for cache"}

    key = cache_key(context, prompt)
    cached = cache.get(key)
    if cached is not None:
        return {"cache": "hit", "text": cached}

    output = call_model(prompt)
    cache.set(key, output, context)
    return {"cache": "miss", "text": output}


if __name__ == "__main__":
    cache = ResponseCache()
    context = CacheContext(
        tenant_id="tenant-a",
        model_version="model-v3",
        prompt_version="summarizer-v2",
    )

    print(generate_with_cache(cache, context, "Summarize this document."))
    print(generate_with_cache(cache, context, "Summarize this document."))
    cache.invalidate_prompt_version("summarizer-v2")
    print({"metrics": cache.metrics})
