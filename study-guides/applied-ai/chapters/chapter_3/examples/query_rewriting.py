"""Query rewriting for retrieval.

User questions are often underspecified. A rewrite can add conversation context,
normalize terminology, and generate multiple retrieval probes. The tradeoff is
recall vs query drift: more rewrites can find more evidence, but can also move
away from the user's actual question.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationContext:
    product: str = ""
    tier: str = ""
    max_rewrites: int = 4


@dataclass(frozen=True)
class QueryRewrite:
    query: str
    reason: str


def rewrite_query(user_query: str, context: ConversationContext) -> list[QueryRewrite]:
    if not user_query.strip():
        raise ValueError("query is required")
    if context.max_rewrites <= 0:
        raise ValueError("max_rewrites must be positive")

    base = user_query.strip("?")
    rewrites = [QueryRewrite(base, "original user question")]

    if context.product:
        rewrites.append(QueryRewrite(f"{context.product} {base}", "add product context"))
    if context.tier:
        rewrites.append(QueryRewrite(f"{context.tier} account {base}", "add account tier"))
    if "access" in base.lower():
        rewrites.append(QueryRewrite(base.lower().replace("access", "permissions"), "normalize access term"))

    deduped = list({rewrite.query: rewrite for rewrite in rewrites}.values())
    return deduped[: context.max_rewrites]


if __name__ == "__main__":
    context = ConversationContext(product="billing", tier="enterprise")
    for rewrite in rewrite_query("Who can access invoice exports?", context):
        print(rewrite)
