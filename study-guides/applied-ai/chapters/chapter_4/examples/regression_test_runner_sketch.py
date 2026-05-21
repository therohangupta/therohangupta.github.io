"""
Regression test runner sketch.

The runner compares a candidate system against a baseline and blocks release
when important slices regress beyond a configured tolerance.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegressionCase:
    id: str
    input: str
    expected_keyword: str
    critical: bool
    tags: tuple[str, ...]


@dataclass(frozen=True)
class VersionResult:
    case_id: str
    passed: bool
    critical: bool
    tags: tuple[str, ...]
    version_name: str


def baseline_system(user_input: str) -> str:
    if "delete my account" in user_input.lower():
        return "Account deletion is permanent. Follow the account deletion settings flow."
    return "Please contact support."


def candidate_system(user_input: str) -> str:
    if "delete my account" in user_input.lower():
        return "Follow the account deletion settings flow."
    return "Please contact support."


def run_version(cases: list[RegressionCase], version_name: str) -> list[VersionResult]:
    runner = baseline_system if version_name == "baseline" else candidate_system
    results: list[VersionResult] = []

    for case in cases:
        output = runner(case.input)
        results.append(
            VersionResult(
                case_id=case.id,
                passed=case.expected_keyword.lower() in output.lower(),
                critical=case.critical,
                tags=case.tags,
                version_name=version_name,
            )
        )

    return results


def should_block_release(
    baseline: list[VersionResult],
    candidate: list[VersionResult],
    max_slice_regression: float = 0.2,
) -> bool:
    baseline_by_id = {result.case_id: result for result in baseline}
    if set(baseline_by_id) != {result.case_id for result in candidate}:
        raise ValueError("baseline and candidate suites must contain the same cases")

    for result in candidate:
        previous = baseline_by_id[result.case_id]
        if previous.passed and not result.passed and result.critical:
            print(f"BLOCK: critical regression in {result.case_id}")
            return True

    tags = sorted({tag for result in candidate for tag in result.tags})
    for tag in tags:
        base_slice = [result for result in baseline if tag in result.tags]
        cand_slice = [result for result in candidate if tag in result.tags]
        base_rate = sum(result.passed for result in base_slice) / len(base_slice)
        cand_rate = sum(result.passed for result in cand_slice) / len(cand_slice)
        if base_rate - cand_rate > max_slice_regression:
            print(f"BLOCK: slice regression tag={tag} baseline={base_rate:.2f} candidate={cand_rate:.2f}")
            return True

    return False


if __name__ == "__main__":
    suite = [
        RegressionCase(
            id="account_deletion_warns_permanence",
            input="I want to delete my account.",
            expected_keyword="permanent",
            critical=True,
            tags=("account", "safety", "past_incident"),
        ),
        RegressionCase(
            id="unknown_routes_support",
            input="I have a weird problem.",
            expected_keyword="support",
            critical=False,
            tags=("fallback",),
        ),
    ]

    baseline_results = run_version(suite, "baseline")
    candidate_results = run_version(suite, "candidate")

    blocked = should_block_release(baseline_results, candidate_results)
    print(f"release_blocked={blocked}")
