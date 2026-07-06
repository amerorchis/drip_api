"""Direct unit tests for api/daily.py."""
import json
from unittest.mock import MagicMock, patch

from api.daily import daily


def test_daily_bad_start_date_returns_400_without_http_call():
    with patch('api.daily.requests.post') as mock_post:
        message, status = daily({'email': 'test@example.com', 'start': 'not-a-date'})

    assert status == 400
    assert message
    mock_post.assert_not_called()


def test_daily_success_no_start_date_tags_glacier_daily_update():
    with patch('api.daily.requests.post') as mock_post, patch('api.daily.add_to_workflow') as mock_add:
        response = MagicMock()
        response.raise_for_status.return_value = None
        mock_post.return_value = response

        message, status = daily({'email': 'test@example.com'})

    assert status == 200
    mock_post.assert_called_once()
    sent_kwargs = mock_post.call_args[1]
    payload = json.loads(sent_kwargs['data'])
    tags = payload['subscribers'][0]['tags']
    assert 'Glacier Daily Update' in tags
