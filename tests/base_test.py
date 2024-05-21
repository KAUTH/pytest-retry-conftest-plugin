import random

import pytest
    

@pytest.mark.retry_failed
def test_base():
    """
    This test although marked with the `retry_failed` flag, is
    not affected by `.tests/dir_a/conftest.py`, so it won't be
    retried.
    """

    assert False == True
