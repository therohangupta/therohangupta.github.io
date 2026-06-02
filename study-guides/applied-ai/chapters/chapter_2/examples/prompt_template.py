"""Prompt template example.

The template separates instructions, context, and output constraints so the
model is less likely to confuse facts with commands.
"""

from dataclasses import dataclass


MAX_DOCUMENT_CHARS = 2_000


@dataclass(frozen=True)
class PromptInputs:
    document: str
    schema_name: str = "action_items_v1"


def validate_inputs(inputs: PromptInputs) -> None:
    if not inputs.document.strip():
        raise ValueError("document is required")
    if len(inputs.document) > MAX_DOCUMENT_CHARS:
        raise ValueError("document exceeds prompt budget; summarize or chunk first")
    if "ignore previous instructions" in inputs.document.lower():
        print("warning: possible prompt injection in document context")


def build_extraction_prompt(inputs: PromptInputs) -> str:
    validate_inputs(inputs)
    return f"""You are a careful data extraction system.

Task:
Extract action items from the document.

Rules:
- Use only facts present in the document.
- If owner or due date is missing, use null.
- Return JSON only.

Output schema:
{inputs.schema_name}: {{"items": [{{"task": str, "owner": str | null, "due_date": str | null}}]}}

Document:
{inputs.document}
"""


if __name__ == "__main__":
    print(build_extraction_prompt(PromptInputs("Rohan will send the draft by Friday. Follow up with Maya.")))
