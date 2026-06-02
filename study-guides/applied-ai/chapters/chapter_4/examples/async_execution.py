"""
Async execution sketch.

Useful when an agent performs independent slow work, such as searching multiple
sources or running checks that do not depend on each other.
"""

import asyncio
from dataclasses import dataclass, field


@dataclass
class Budget:
    max_parallel_tasks: int = 3
    timeout_seconds: float = 2.0
    completed: int = 0
    errors: list[str] = field(default_factory=list)


async def search_source(source: str, query: str) -> str:
    await asyncio.sleep(0.2)
    return f"{source}: result for {query}"


async def bounded_search(source: str, query: str, semaphore: asyncio.Semaphore) -> str:
    async with semaphore:
        return await search_source(source, query)


async def gather_evidence(query: str, sources: list[str], budget: Budget) -> list[str]:
    semaphore = asyncio.Semaphore(budget.max_parallel_tasks)
    tasks = [bounded_search(source, query, semaphore) for source in sources]

    try:
        results = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=budget.timeout_seconds,
        )
    except asyncio.TimeoutError:
        budget.errors.append("Timed out while gathering evidence")
        return []

    evidence: list[str] = []
    for result in results:
        if isinstance(result, Exception):
            budget.errors.append(str(result))
        else:
            budget.completed += 1
            evidence.append(result)
    return evidence


async def main() -> None:
    budget = Budget()
    evidence = await gather_evidence(
        "agent safety patterns",
        ["docs", "tickets", "runbooks", "incident_reports"],
        budget,
    )
    print(evidence)
    print(budget)


if __name__ == "__main__":
    asyncio.run(main())
