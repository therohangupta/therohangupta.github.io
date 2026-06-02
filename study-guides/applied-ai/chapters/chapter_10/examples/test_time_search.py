"""
Test-time search example.

This sketches a small inference-time branching controller. Real systems replace
the toy generator and verifier with model calls, tool checks, unit tests, or a
learned verifier. The core tradeoff is quality vs latency/cost.
"""

from dataclasses import dataclass, field


@dataclass(order=True)
class SearchNode:
    score: float
    state: "SearchState" = field(compare=False)
    depth: int = field(compare=False)


@dataclass(frozen=True)
class SearchState:
    prompt: str
    actions: tuple[str, ...] = ()
    estimated_tokens: int = 0
    cost_units: float = 0.0


@dataclass(frozen=True)
class VerificationResult:
    score: float
    rejected: bool
    reason: str | None = None


MAX_DEPTH = 3
BRANCHING_FACTOR = 3
KEEP_TOP_K = 2
MAX_TOKENS = 160
MAX_COST_UNITS = 8.0


def propose_next_steps(state: SearchState) -> list[SearchState]:
    actions = ["decompose", "use_tool", "final_answer"][:BRANCHING_FACTOR]
    next_states = []
    for action in actions:
        next_states.append(
            SearchState(
                prompt=state.prompt,
                actions=state.actions + (action,),
                estimated_tokens=state.estimated_tokens + 35,
                cost_units=state.cost_units + (2.0 if action == "use_tool" else 1.0),
            )
        )
    return next_states


def verify_state(state: SearchState) -> VerificationResult:
    """Toy verifier: prefer paths that used a tool and reached a final answer."""
    if state.estimated_tokens > MAX_TOKENS:
        return VerificationResult(0.0, True, "token budget exceeded")
    if state.cost_units > MAX_COST_UNITS:
        return VerificationResult(0.0, True, "cost budget exceeded")

    score = 0.0
    score += 0.4 if "decompose" in state.actions else 0.0
    score += 0.4 if "use_tool" in state.actions else 0.0
    score += 0.4 if "final_answer" in state.actions else 0.0
    score -= 0.1 * len(state.actions)
    return VerificationResult(score, False)


def test_time_search(prompt: str) -> SearchState:
    frontier = [SearchNode(score=0.0, state=SearchState(prompt=prompt), depth=0)]
    best = frontier[0]

    while frontier:
        expanded: list[SearchNode] = []
        for node in frontier:
            if node.depth >= MAX_DEPTH:
                continue
            for next_state in propose_next_steps(node.state):
                verification = verify_state(next_state)
                if verification.rejected:
                    print({"rejected": next_state.actions, "reason": verification.reason})
                    continue
                child = SearchNode(score=verification.score, state=next_state, depth=node.depth + 1)
                expanded.append(child)
                if child.score > best.score:
                    best = child

        if best.score >= 0.9:
            break
        if not expanded:
            break

        frontier = sorted(expanded, reverse=True)[:KEEP_TOP_K]

    return best.state


if __name__ == "__main__":
    print(test_time_search("answer customer billing question"))
