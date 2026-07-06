"""Tests for the top-level Flask routes in api/index.py."""
from unittest.mock import MagicMock, patch


def test_root_returns_connection_established(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.get_data(as_text=True) == "Connection established"


def test_drip_cache_hit_returns_cached_json(client, mock_cache):
    cached = {'nas': 'a', 'astro': 'b', 'test': 'c'}
    mock_cache.get.return_value = cached

    resp = client.get('/drip')

    assert resp.status_code == 200
    assert resp.get_json() == cached
    mock_cache.get.assert_called_with('cached_events')


def test_drip_cache_miss_returns_fresh_data_not_null(client, mock_cache, monkeypatch):
    # Headline bug regression: on a cache miss, /drip used to return null.
    mock_cache.get.return_value = None
    fresh_data = {'nas': 'nas-events', 'astro': 'astro-events', 'test': 'The API is reading plain text.'}
    monkeypatch.setattr('api.index.events', lambda day: fresh_data)

    resp = client.get('/drip')

    assert resp.status_code == 200
    body = resp.get_json()
    assert body is not None
    assert body == fresh_data
    mock_cache.set.assert_called_once()
    set_args = mock_cache.set.call_args
    assert set_args[0][0] == 'cached_events'
    assert set_args[0][1] == fresh_data


def test_drip_cache_miss_with_events_error_returns_502(client, mock_cache, monkeypatch):
    mock_cache.get.return_value = None

    def boom(day):
        raise RuntimeError('NPS API is down')

    monkeypatch.setattr('api.index.events', boom)

    resp = client.get('/drip')

    assert resp.status_code == 502
    assert resp.get_json() == {'error': 'Could not fetch events data.'}


def test_drip_preview_uses_test_cache_key(client, mock_cache):
    cached = {'nas': 'x', 'astro': 'y', 'test': 'z'}
    mock_cache.get.return_value = cached

    resp = client.get('/drip?preview=true')

    assert resp.status_code == 200
    assert resp.get_json() == cached
    mock_cache.get.assert_called_with('cached_test_events')


def test_drip_preview_cache_miss_uses_fixed_test_date(client, mock_cache, monkeypatch):
    mock_cache.get.return_value = None
    captured_days = []

    def fake_events(day):
        captured_days.append(day)
        return {'nas': '', 'astro': '', 'test': 'The API is reading plain text.'}

    monkeypatch.setattr('api.index.events', fake_events)

    resp = client.get('/drip?preview=true')

    assert resp.status_code == 200
    mock_cache.get.assert_called_with('cached_test_events')
    mock_cache.set.assert_called_once()
    assert mock_cache.set.call_args[0][0] == 'cached_test_events'
    assert len(captured_days) == 1
    from datetime import datetime
    assert captured_days[0] == datetime(2023, 7, 4)


def test_dripactions_missing_action_and_email_returns_400(client):
    resp = client.get('/dripactions')
    assert resp.status_code == 400


def test_dripactions_unknown_action_returns_400(client):
    resp = client.get('/dripactions?action=bogus&email=test@example.com')
    assert resp.status_code == 400
    assert resp.get_data(as_text=True) == "No action was specified."


def test_dripactions_stopdaily_success(client):
    with patch('api.drip.requests.request') as mock_request:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        resp = client.get('/dripactions?action=stopdaily&email=test@example.com')

    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert 'removed' in body

    mock_request.assert_called_once()
    method, url = mock_request.call_args[0][0], mock_request.call_args[0][1]
    assert method == 'DELETE'
    assert 'Glacier%20Daily%20Update' in url


def test_dripactions_optout_without_tag_returns_400(client):
    resp = client.get('/dripactions?action=optout&email=test@example.com')
    assert resp.status_code == 400
    assert resp.get_data(as_text=True) == "No tag was specified."


def test_dripactions_untilspring_partial_failure_returns_502_with_message(client):
    import requests

    def side_effect(method, url, **kwargs):
        response = MagicMock()
        if method == 'DELETE':
            response.raise_for_status.return_value = None
            return response
        raise requests.exceptions.RequestException('tag service unavailable')

    with patch('api.drip.requests.request', side_effect=side_effect):
        resp = client.get('/dripactions?action=untilspring&email=test@example.com')

    assert resp.status_code == 502
    body = resp.get_data(as_text=True)
    # Regression: this used to come back as an empty/None message.
    assert body
    assert body.strip() != ""
