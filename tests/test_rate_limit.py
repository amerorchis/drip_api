"""Rate limiting on the unauthenticated write endpoints."""
from unittest.mock import patch


def test_dripactions_rate_limited_after_ten_per_minute(client):
    with patch('api.index.drip.untag', return_value=("ok", 200)):
        for _ in range(10):
            resp = client.get('/dripactions?action=stopdaily&email=a@b.com')
            assert resp.status_code == 200
        resp = client.get('/dripactions?action=stopdaily&email=a@b.com')
    assert resp.status_code == 429
    assert 'Too many requests' in resp.get_data(as_text=True)


def test_rate_limit_is_per_client_ip(client):
    with patch('api.index.drip.untag', return_value=("ok", 200)):
        for _ in range(11):
            resp = client.get('/dripactions?action=stopdaily&email=a@b.com',
                              headers={'x-real-ip': '203.0.113.1'})
        assert resp.status_code == 429

        # A different client IP is not affected by the first one's limit.
        resp = client.get('/dripactions?action=stopdaily&email=a@b.com',
                          headers={'x-real-ip': '203.0.113.2'})
        assert resp.status_code == 200


def test_clear_cache_rate_limited_after_three_per_hour(client, mock_cache):
    for _ in range(3):
        resp = client.get('/drip/clear')
        assert resp.status_code == 200
    resp = client.get('/drip/clear')
    assert resp.status_code == 429
