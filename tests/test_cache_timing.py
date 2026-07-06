"""Tests for api/cache_timing.py."""
from api.cache_timing import get_remaining_time


def test_get_remaining_time_is_int_within_a_day():
    remaining = get_remaining_time()
    assert isinstance(remaining, int)
    assert 0 <= remaining <= 86400
