# How to write a simple pytest hook function

Code of article on [Medium](https://konpap.medium.com/how-to-write-a-simple-pytest-hook-function-e9762ca800ee).


## How to use
Add to your desired `conftest.py` file:

```python
import pytest
from _pytest.nodes import Item

# Import it from the appropriate location or directly add the code to the hook.
from tests.utils import retry_utility


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item: Item) -> None:
    outcome = yield

    retry_utility(
        item=item,
        outcome=outcome,
        pytest_markers={"retry_failed"},
        retry_on_exceptions=Exception,
        max_calls=3,
        retry_timeout_in_seconds=10.0,
    )
```

## Summary
Run all tests with:
`pytest tests/`

- `tests/base_test.py::test_base` which is set to always fail and will never be retried
since the local conftest plugin applies per directory and our pytest hooks are in
`tests/dir_a/conftest.py`. For more information see the [pytest documentation](https://docs.pytest.org/en/7.1.x/how-to/writing_plugins.html#local-conftest-plugins).

- `tests/dir_a/a_test.py::test_a_without_marker` which is set to always fail and will never be retried
since it is not marked with the `retry_failed` marker.

- `tests/dir_a/a_test.py::test_with_marker` which is set to randomly fail and will be retried if it does.