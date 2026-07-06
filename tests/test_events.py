"""Tests for api/events.py against a mocked NPS API."""
from datetime import datetime
from unittest.mock import MagicMock, patch

from api.events import events


def _event(title, date, timestart, location, event_id, tags):
    return {
        'title': title,
        'date': date,
        'times': [{'timestart': timestart}] if timestart else [],
        'location': location,
        'id': event_id,
        'tags': tags,
    }


def test_events_skips_malformed_event_and_returns_expected_keys():
    good_astro = _event(
        'Stargazing - Milky Way Talk', '2024-07-10', '9:00 PM',
        'Apgar Amphitheater', '1', ['astronomy'],
    )
    good_nas = _event(
        'Drumming Circle', '2024-07-11', '2:00 PM',
        'St. Mary Visitor Center', '2', ['Native America Speaks'],
    )
    malformed = _event(
        'Broken Event', '2024-07-12', None,
        'Somewhere', '3', ['astronomy'],
    )

    page_response = MagicMock()
    page_response.raise_for_status.return_value = None
    page_response.json.return_value = {
        'total': 3,
        'data': [good_astro, good_nas, malformed],
    }

    with patch('api.events.requests.get', return_value=page_response) as mock_get:
        result = events(datetime(2024, 7, 9))

    assert set(result.keys()) == {'nas', 'astro', 'test'}
    assert 'Milky Way Talk' in result['astro']
    assert 'Broken Event' not in result['astro']
    assert 'Drumming Circle' in result['nas']
    assert result['test'] == 'The API is reading plain text.'
    assert mock_get.called
