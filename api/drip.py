import requests
import os
import json
import urllib.parse

def _headers():
    return {
        "Authorization": "Bearer " + os.environ['DRIP_TOKEN'],
        "Content-Type": "application/vnd.api+json"
    }

def _account_id():
    return os.environ['DRIP_ACCOUNT']

def _request(method, url, error_message, **kwargs):
    try:
        response = requests.request(method, url, headers=_headers(), **kwargs)
        response.raise_for_status()
        return None
    except requests.exceptions.RequestException as e:
        return f"{error_message} Error: {e}"

def untag(email, tag):
    encoded_email = urllib.parse.quote(email, safe='@')
    encoded_tag = urllib.parse.quote(tag)
    url = f"https://api.getdrip.com/v2/{_account_id()}/subscribers/{encoded_email}/tags/{encoded_tag}"

    error = _request('DELETE', url, f"Could not remove {email} from {tag}.")
    if error:
        return error, 502
    return f"{email} was successfully removed from {tag}.", 200

def tag(email, tag):
    url = f"https://api.getdrip.com/v2/{_account_id()}/tags"

    payload = {
        "tags": [{
            "email": email,
            "tag": tag
        }]
    }

    error = _request('POST', url, f"Could not tag {email} with {tag}.", data=json.dumps(payload))
    if error:
        return error, 502
    return f"{email} was tagged {tag}.", 200

def unsub(email):
    encoded_email = urllib.parse.quote(email, safe='@')
    url = f"https://api.getdrip.com/v2/{_account_id()}/subscribers/{encoded_email}/unsubscribe_all"

    error = _request('POST', url, f"Could not unsubscribe {email}.")
    if error:
        return error, 502
    return f"{email} was unsubscribed from all marketing.", 200

def add_to_workflow(email, campaign_id):
    url = f"https://api.getdrip.com/v2/{_account_id()}/workflows/{campaign_id}/subscribers"

    data = {
        "subscribers": [{
            "email": email,
        }]
    }

    response = requests.post(url, headers=_headers(), data=json.dumps(data))
    r = response.json()

    if response.status_code == 201:
        print(f'Drip: Email sent successfully to {email}!')
        return True

    else:
        print(f"Failed to subscribe {email} to the campaign. Error message:", r["errors"][0]["code"], ' - ', r["errors"][0]["message"])
