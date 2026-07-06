"""Direct unit tests for api/drip.py, independent of the Flask routes."""
import json
from unittest.mock import MagicMock, patch

import requests

import api.drip as drip


def _ok_response():
    response = MagicMock()
    response.raise_for_status.return_value = None
    return response


def test_untag_encodes_plus_in_email():
    with patch('api.drip.requests.request') as mock_request:
        mock_request.return_value = _ok_response()
        message, status = drip.untag('user+test@example.com', 'Glacier Daily Update')

    assert status == 200
    url = mock_request.call_args[0][1]
    assert 'user%2Btest@example.com' in url
    assert 'Glacier%20Daily%20Update' in url


def test_untag_request_exception_returns_502():
    with patch('api.drip.requests.request', side_effect=requests.exceptions.RequestException('down')):
        message, status = drip.untag('test@example.com', 'Some Tag')

    assert status == 502
    assert message


def test_tag_payload_contains_raw_email_not_encoded():
    with patch('api.drip.requests.request') as mock_request:
        mock_request.return_value = _ok_response()
        message, status = drip.tag('user+test@example.com', 'Resume Daily Spring')

    assert status == 200
    sent_kwargs = mock_request.call_args[1]
    payload = json.loads(sent_kwargs['data'])
    assert payload['tags'][0]['email'] == 'user+test@example.com'


def test_unsub_success():
    with patch('api.drip.requests.request') as mock_request:
        mock_request.return_value = _ok_response()
        message, status = drip.unsub('test@example.com')

    assert status == 200
    assert 'test@example.com' in message
