from typing import Any, Iterator

import pytest
from pluggy import Result
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from _pytest.terminal import TerminalReporter

from tests.utils import retry_utility


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: CallInfo[None]) -> Iterator[Result[Any]]:
    """
    Implemented hook to:
    - store attributes that will be used to create the retry summary

    This hook is called after each test item's setup, call and teardown stage.

    Reference:
    https://docs.pytest.org/en/latest/reference/reference.html#pytest.hookspec.pytest_runtest_makereport
    """

    outcome: Result[Any] = yield  # type: ignore[misc, assignment]
    result = outcome.get_result()

    if result.when == "setup":
        # Set default attributes before every run, they should be used appropriately on `call`.
        item._max_calls = 1  # type: ignore[attr-defined]
        item._calls = 1  # type: ignore[attr-defined]

    if result.when == "call" and result.outcome == "failed":
        # Mark the final result outcome as `passed` if we never reach the max calls.
        if item._calls != item._max_calls:  # type: ignore[attr-defined]
            result.outcome = "passed"


def pytest_terminal_summary(terminalreporter: TerminalReporter) -> None:
    """
    Implemented hook to add a section to terminal summary reporting.

    Reference:
    https://docs.pytest.org/en/latest/reference/reference.html#pytest.hookspec.pytest_terminal_summary
    """

    tr = terminalreporter
    tr.write_sep("=", "Retry Summary")

    for report in tr.stats.get("failed", []) + tr.stats.get("passed", []):
        retry_number = 1

        for section in report.sections:
            if section[0] == "Captured failure call":
                tr.write_line(f"- {report.nodeid} attempt #{retry_number}")
                tr.write_line(f"Reason: {section[1]}\n")
                retry_number += 1


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item: Item) -> Iterator[Any]:
    """
    Implemented hook wrapper to:
    - retry running failing tests

    Reference:
    https://docs.pytest.org/en/latest/reference/reference.html#pytest.hookspec.pytest_runtest_call
    """

    # First run of the test with `yield` (no exceptions are raised in any case).
    outcome: Result[Any] = yield  # type: ignore[assignment]

    retry_utility(
        item=item,
        outcome=outcome,
        pytest_markers={"retry_failed"},
        retry_on_exceptions=Exception,
        max_calls=2,
        retry_timeout_in_seconds=1.0,
    )
