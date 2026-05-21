"""Metadata filtering before semantic retrieval.

Filtering narrows the search space before ranking. This improves precision,
latency, and access control, but over-filtering can hide relevant evidence.
"""

from dataclasses import dataclass


ALLOWED_FILTERS = {"product", "tier", "acl"}


@dataclass(frozen=True)
class Document:
    doc_id: str
    text: str
    metadata: dict[str, str]


DOCUMENTS = [
    Document("d1", "Enterprise invoices can be exported as CSV.", {"product": "billing", "tier": "enterprise", "acl": "finance"}),
    Document("d2", "Free-tier workspaces cannot export invoices.", {"product": "billing", "tier": "free", "acl": "public"}),
    Document("d3", "Admins can reset user MFA.", {"product": "auth", "tier": "enterprise", "acl": "admin"}),
]


def filter_documents(filters: dict[str, str], widen_on_empty: bool = True) -> list[Document]:
    unknown = set(filters) - ALLOWED_FILTERS
    if unknown:
        raise ValueError(f"unsupported filter keys: {unknown}")

    filtered = [
        doc
        for doc in DOCUMENTS
        if all(doc.metadata.get(key) == value for key, value in filters.items())
    ]
    if filtered or not widen_on_empty:
        return filtered

    # Production systems may widen non-security filters, but should not bypass ACL.
    widened = {key: value for key, value in filters.items() if key == "acl"}
    return filter_documents(widened, widen_on_empty=False) if widened else DOCUMENTS


if __name__ == "__main__":
    for doc in filter_documents({"product": "billing", "tier": "enterprise", "acl": "finance"}):
        print(f"{doc.doc_id}: {doc.text}")
