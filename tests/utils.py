import time
from typing import Any, Callable

from pluggy import Result
from _pytest.nodes import Item


def retry_utility(
    item: Item,
    outcome: Result[Any],
    pytest_markers: set[str] | None,
    retry_on_exceptions: type[Exception] | tuple[type[Exception], ...] = Exception,
    max_calls: int = 1,
    retry_timeout_in_seconds: float = 10.0,
) -> None:
    """
    Helper function used when implementing the `pytest_runtest_call` hook wrapper.

    Adds a basic retry mechanism for tests that can be applied to specific markers.
    If no markers are provided, a test will be covered by the retry mechanism for any marker.

    Example usage:
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(item: Item) -> None:
        outcome = yield

        retry_utility(
            item=item,
            outcome=outcome,
            pytest_markers={"retry_failed"},
            retry_on_exceptions=Exception,
            max_calls=2,
            retry_timeout_in_seconds=10.0,
        )

    Reference:
    https://docs.pytest.org/en/latest/reference/reference.html#pytest.hookspec.pytest_runtest_call
    """

    item_markers = {marker.name for marker in item.iter_markers()}

    if pytest_markers is not None:
        common_markers = item_markers & pytest_markers

    # This filtering applies to a single test item
    if pytest_markers is None or len(common_markers) > 0:
        # These attributes can be used to make a retry report (`pytest_runtest_makereport` hook).
        item._max_calls = max_calls  # type: ignore[attr-defined]
        item._calls = 1  # type: ignore[attr-defined]

        exc_type = None
        if outcome.excinfo is not None:
            exc_type = outcome.excinfo[0]
            exc = outcome.excinfo[1]

        if exc_type is not None and issubclass(exc_type, retry_on_exceptions):
            failure = str(exc) + "\n"
            item.add_report_section(when="call", key="failure", content=failure)

            # First call happens outside this function, when `outcome` is yielded, so we need one
            # less than `max_calls`.
            while max_calls - 1 > 0:
                time.sleep(retry_timeout_in_seconds)

                try:
                    item._calls += 1  # type: ignore[attr-defined]
                    item.runtest()
                    return
                except retry_on_exceptions as e:
                    failure = str(e) + "\n"
                    item.add_report_section(when="call", key="failure", content=failure)

                    max_calls -= 1
