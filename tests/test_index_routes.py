"""Tests for the top-level Flask routes in api/index.py."""
from unittest.mock import MagicMock, patch


def test_root_returns_connection_established(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.get_data(as_text=True) == "Connection established"


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


def test_drip_feed_routes_are_gone(client):
    # The Liquid content feed and its cache routes were retired; nothing calls them.
    for path in ('/drip', '/drip/', '/drip/clear', '/drip/set_test_cache', '/drip/get_test_cache'):
        assert client.get(path).status_code == 404, path


def test_responses_are_not_cdn_cacheable(client):
    # vercel.json used to send s-maxage=21600 on every route, which let the CDN
    # serve a cached /dripactions response instead of running the action.
    import json
    import pathlib
    config = json.loads((pathlib.Path(__file__).parent.parent / 'vercel.json').read_text())
    assert 'headers' not in config
