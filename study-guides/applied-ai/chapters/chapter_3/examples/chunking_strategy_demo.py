"""
Chunking strategy demo.

The example compares fixed-size chunking with heading-aware chunking. The point
is not that one strategy always wins, but that chunking determines what the
retriever can return as evidence. In production, bad chunking is one of the most
common retrieval quality failures — it silently limits what the model can cite.
"""

from __future__ import annotations
from dataclasses import dataclass


DOCUMENT = """
# Billing Guide

## Invoice Export
Enterprise invoices can be exported from the billing dashboard. The export
includes invoice ID, customer name, amount, and payment status.

## Permissions
Invoice export requires the finance admin role. Workspace admins can grant this
role from organization settings.

## Webhooks
Billing webhooks notify downstream systems when invoices are paid or voided.
"""


def fixed_size_chunks(text: str, words_per_chunk: int = 18, overlap: int = 4) -> list[str]:
    words = text.split()
    chunks = []
    step = words_per_chunk - overlap
    for start in range(0, len(words), step):
        chunk = words[start : start + words_per_chunk]
        if chunk:
            chunks.append(" ".join(chunk))
    return chunks


@dataclass
class SemanticChunk:
    heading: str
    text: str
    word_count: int = 0

    def __post_init__(self) -> None:
        self.word_count = len(self.text.split())


def heading_aware_chunks(text: str) -> list[SemanticChunk]:
    chunks: list[SemanticChunk] = []
    current_heading = "Untitled"
    current_lines: list[str] = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            if current_lines:
                chunks.append(SemanticChunk(heading=current_heading, text=" ".join(current_lines)))
                current_lines = []
            current_heading = line.lstrip("#").strip()
        else:
            current_lines.append(line)

    if current_lines:
        chunks.append(SemanticChunk(heading=current_heading, text=" ".join(current_lines)))
    return chunks


@dataclass
class IndexedChunk:
    chunk_id: str
    parent_doc_id: str
    section: str
    heading: str
    text: str


def attach_parent_metadata(chunks: list[SemanticChunk], parent_doc_id: str) -> list[IndexedChunk]:
    """Parent metadata lets retrieval return a chunk but cite the larger source.
    Production: also attach access-control labels, ingestion timestamp, and version."""
    enriched: list[IndexedChunk] = []
    for index, chunk in enumerate(chunks, start=1):
        enriched.append(
            IndexedChunk(
                chunk_id=f"{parent_doc_id}:{index}",
                parent_doc_id=parent_doc_id,
                section=chunk.heading,
                heading=chunk.heading,
                text=chunk.text,
            )
        )
    return enriched


def main() -> None:
    print("Fixed-size chunks:")
    for index, chunk in enumerate(fixed_size_chunks(DOCUMENT), start=1):
        print(f"\n[{index}] {chunk}")

    print("\nHeading-aware chunks:")
    for chunk in attach_parent_metadata(heading_aware_chunks(DOCUMENT), "billing-guide"):
        print(f"\n[{chunk.chunk_id}] {chunk.section}\n{chunk.text}")


if __name__ == "__main__":
    main()
