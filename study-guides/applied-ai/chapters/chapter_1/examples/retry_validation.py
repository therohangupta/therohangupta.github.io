"""Retry and validation pattern.

Retries should be bounded and driven by explicit validation failures, not by
blindly asking the model to try again forever.
"""

import json


class ParseFailure(ValueError):
    pass


class SemanticFailure(ValueError):
    pass


def fake_model(attempt: int, repair_hint: str | None = None) -> str:
    if attempt == 0:
        return "Sure, here is the answer: Friday"
    if attempt == 1:
        return '{"answer": "Friday", "confidence": 0.41}'
    if repair_hint:
        return '{"answer": "Friday", "confidence": 0.82}'
    return '{"answer": "Friday"}'


def validate(raw: str) -> dict:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ParseFailure("output was not valid JSON") from exc

    if not isinstance(data.get("answer"), str):
        raise SemanticFailure("answer must be a string")
    if not isinstance(data.get("confidence"), float):
        raise SemanticFailure("confidence must be a float")
    if data["confidence"] < 0.7:
        raise SemanticFailure("confidence too low for automatic use")
    return data


repair_hint = None
for attempt in range(3):
    try:
        print(validate(fake_model(attempt, repair_hint)))
        break
    except ParseFailure as exc:
        repair_hint = "Return only JSON matching the schema."
        print(f"attempt {attempt} parse failure: {exc}")
    except SemanticFailure as exc:
        repair_hint = f"Fix semantic issue: {exc}"
        print(f"attempt {attempt} semantic failure: {exc}")
else:
    print("fallback: route to human review instead of guessing")
