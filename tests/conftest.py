"""Shared pytest fixtures for the drip_api test suite.

Sets fake credentials before the app is imported (env vars are read inside
functions at call time, but setting them up front keeps things simple), and
provides a Flask test client. Redis env vars are cleared so the rate limiter
never talks to a real Redis instance.
"""
import os

import pytest

# Fake credentials so anything reading os.environ at call time doesn't KeyError.
os.environ.setdefault('DRIP_TOKEN', 'test-drip-token')
os.environ.setdefault('DRIP_ACCOUNT', 'test-drip-account')

# Ensure the app never sees a real Redis in tests: with no REDIS_HOST the rate
# limiter falls back to in-memory storage.
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


@pytest.fixture
def app():
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()
