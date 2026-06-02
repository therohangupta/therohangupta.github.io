"""Structured output validation sketch.

Prompting asks for JSON, but production code still validates the shape before
trusting it. This example uses only the standard library and demonstrates
nested validation plus a small repair step for common malformed output.
"""

import json
from typing import Any


REQUIRED_ITEM_KEYS = {"task"}
OPTIONAL_ITEM_KEYS = {"owner", "due_date", "priority"}
PRIORITIES = {"low", "medium", "high"}


def parse_json_object(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Common model failure: prose around the JSON object.
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        data = json.loads(raw[start : end + 1])

    if not isinstance(data, dict):
        raise ValueError("top-level output must be an object")
    return data


def validate_action_items(raw: str) -> dict:
    data = parse_json_object(raw)
    if not isinstance(data.get("items"), list):
        raise ValueError("items must be a list")

    for item in data["items"]:
        if not isinstance(item, dict):
            raise ValueError("each item must be an object")

        keys = set(item)
        missing = REQUIRED_ITEM_KEYS - keys
        unknown = keys - REQUIRED_ITEM_KEYS - OPTIONAL_ITEM_KEYS
        if missing:
            raise ValueError(f"missing required item keys: {missing}")
        if unknown:
            raise ValueError(f"unknown item keys: {unknown}")

        if not isinstance(item["task"], str):
            raise ValueError("task must be a string")
        if "owner" not in item:
            item["owner"] = None
        if "due_date" not in item:
            item["due_date"] = None
        if "priority" not in item:
            item["priority"] = "medium"
        if item["priority"] not in PRIORITIES:
            raise ValueError(f"bad priority: {item['priority']}")
    return data


if __name__ == "__main__":
    output = """
    Sure, here is the JSON:
    {"items": [{"task": "send draft", "owner": "Rohan", "due_date": "Friday"}]}
    """
    print(validate_action_items(output))
