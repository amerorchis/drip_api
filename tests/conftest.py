"""Shared pytest fixtures for the drip_api test suite.

Sets fake credentials before the app is imported (env vars are read inside
functions at call time, but setting them up front keeps things simple), and
provides a Flask test client plus a mocked `api.index.cache` so no test ever
talks to a real Redis instance.
"""
import os
from unittest.mock import MagicMock

import pytest

# Fake credentials so anything reading os.environ at call time doesn't KeyError.
os.environ.setdefault('DRIP_TOKEN', 'test-drip-token')
os.environ.setdefault('DRIP_ACCOUNT', 'test-drip-account')
os.environ.setdefault('NPS', 'test-nps-key')

# Ensure the app never sees a real Redis in tests: with no REDIS_HOST the rate
# limiter falls back to in-memory storage, and the cache is mocked per-test.
# Must happen before api.index is imported (it reads these at import time).
for _var in ('REDIS_HOST', 'REDIS_PASSWORD', 'REDIS_PORT'):
    os.environ.pop(_var, None)

from api.index import app as flask_app  # noqa: E402  (import after env setup)


@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Clear rate-limit counters so tests don't trip limits set by earlier tests."""
    from api.index import limiter
    limiter.reset()
    yield


@pytest.fixture(autouse=True)
def fake_env(monkeypatch):
    """Ensure every test sees fake, consistent env vars regardless of order."""
    monkeypatch.setenv('DRIP_TOKEN', 'test-drip-token')
    monkeypatch.setenv('DRIP_ACCOUNT', 'test-drip-account')
    monkeypatch.setenv('NPS', 'test-nps-key')


@pytest.fixture
def app():
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_cache(monkeypatch):
    """Replace api.index.cache with a MagicMock so no Redis call ever happens.

    Defaults cache.get(...) to None (cache miss) since that's the more
    interesting/common path to exercise; tests that want a cache hit just set
    mock_cache.get.return_value explicitly.
    """
    import api.index as index_module

    mock = MagicMock()
    mock.get.return_value = None
    monkeypatch.setattr(index_module, 'cache', mock)
    return mock
