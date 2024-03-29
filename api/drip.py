import requests
import os
import json
import urllib.parse

def stopdaily(email):
    email = urllib.parse.quote(email, safe='@')
    drip_token = os.environ['DRIP_TOKEN']
    account_id = os.environ['DRIP_ACCOUNT']
    api_key = drip_token
    tag = 'Glacier%20Daily%20Update'
    url = f"https://api.getdrip.com/v2/{account_id}/subscribers/{email}/tags/{tag}"

    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/vnd.api+json"
    }

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        if response.status_code == 204:
            return f"{email} was succesfully removed from Glacier Daily Updates"
        else:
            print(response.reason)
            return f'Error Response Code: {response.status_code}'
    except requests.exceptions.RequestException as e:
        # Handle errors
        return f"Error: {e}"

def untag(email, tag):
    email = urllib.parse.quote(email, safe='@')
    drip_token = os.environ['DRIP_TOKEN']
    account_id = os.environ['DRIP_ACCOUNT']
    api_key = drip_token
    url = f"https://api.getdrip.com/v2/{account_id}/subscribers/{email}/tags/{tag}"

    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/vnd.api+json"
    }

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        if response.status_code == 204:
            return f"{email} was succesfully removed from {tag}."
        else:
            print(response.reason)
            return f'Error Response Code: {response.status_code}'
    except requests.exceptions.RequestException as e:
        # Handle errors
        return f"Error: {e}. Opt out failed."

def unsub(email):
    email = urllib.parse.quote(email, safe='@')
    drip_token = os.environ['DRIP_TOKEN']
    account_id = os.environ['DRIP_ACCOUNT']
    api_key = drip_token
    tag = 'Glacier%20Daily%20Update'
    url = f"https://api.getdrip.com/v2/{account_id}/subscribers/{email}/unsubscribe_all"

    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/vnd.api+json"
    }

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        if response.status_code == 200:
            return f"{email} was unsubscribed from all marketing."
        else:
            print(response.reason)
            return f'Error Response Code: {response.status_code}'
    except requests.exceptions.RequestException as e:
        # Handle errors
        return f"Error: {e}"

def tag(email, tag):
    email = urllib.parse.quote(email, safe='@')
    drip_token = os.environ['DRIP_TOKEN']
    account_id = os.environ['DRIP_ACCOUNT']
    api_key = drip_token

    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/vnd.api+json"
    }

    url = f'https://api.getdrip.com/v2/{account_id}/tags'

    payload= { 
        "tags": [{ 
            "email": email, 
            "tag": tag
        }] 
    }

    try:
        data = json.dumps(payload)
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        if response.status_code == 201:
            return f"{email} was tagged {tag}."
        else:
            print(response.reason)
            return f'Error Response Code: {response.status_code}'
    except requests.exceptions.RequestException as e:
        # Handle errors
        return f"Error: {e}"

def add_to_workflow(email, campaign_id):
    email = urllib.parse.quote(email, safe='@')
    drip_token = os.environ['DRIP_TOKEN']
    account_id = os.environ['DRIP_ACCOUNT']
    api_key = drip_token

    url = f"https://api.getdrip.com/v2/{account_id}/workflows/{campaign_id}/subscribers"
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/vnd.api+json"
    }

    data = {
        "subscribers": [{
            "email": email,
        }]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    r = response.json()
    
    if response.status_code == 201:
        print(f'Drip: Email sent successfully to {email}!')
        return True
    
    else:
        print(f"Failed to subscribe {email} to the campaign. Error message:", r["errors"][0]["code"], ' - ', r["errors"][0]["message"])

def custom_field(email, custom_fields: dict):
    email = urllib.parse.quote(email, safe='@')
    drip_token = os.environ['DRIP_TOKEN']
    account_id = os.environ['DRIP_ACCOUNT']
    api_key = drip_token
    url = f"https://api.getdrip.com/v2/{account_id}/subscribers"

    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/vnd.api+json"
    }

    data = {
        "subscribers": [{
            "email": email,
            "custom_fields": custom_fields
        }]
    }

if __name__ == "__main__":
    print(tag('andrew@glacier.org', 'DA test'))
