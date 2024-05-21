import random

import pytest
    

@pytest.mark.retry_failed
def test_a_with_marker():
    """A test marked with the `retry_failed` marker"""
    
    assert random.choice([True, False])


def test_a_without_marker():
    """A test NOT marked with the `retry_failed` marker"""
    
    assert False == True
