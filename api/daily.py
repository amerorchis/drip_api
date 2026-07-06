import os
import json
from datetime import datetime

import pytz
import requests

from api.drip import add_to_workflow

def daily(args: dict):
    email, start, end = args.get('email'), args.get('start'), args.get('end')

    now = datetime.now(pytz.timezone('US/Mountain')).replace(tzinfo=None)

    dt_start = None
    if start:
        try:
            dt_start = datetime.strptime(start, "%Y-%m-%d")
        except ValueError:
            return "The start date was not in the expected YYYY-MM-DD format.", 400

    updates = {"email": email}
    tags = []
    custom_fields = {}

    # If the start date is today or earlier tag and add immediately
    if not start or dt_start <= now:
        tags.append("Glacier Daily Update")

        # If it's already gone out today, add them to the workflow now.
        if now.hour > 8:
            try:
                add_to_workflow(email, campaign_id='169298893')
            except Exception as e:
                print(e)

    # If start is in the future, store it in Drip.
    else:
        custom_fields['Daily_Start'] = start
        tags.append('Daily Start Set')


    if end:
        custom_fields['Daily_End'] = end
        tags.append('Daily End Set')

    # Store values in account
    updates["custom_fields"] = custom_fields
    updates["tags"] = tags

    account_id = os.environ['DRIP_ACCOUNT']
    url = f"https://api.getdrip.com/v2/{account_id}/subscribers"

    headers = {
        "Authorization": "Bearer " + os.environ['DRIP_TOKEN'],
        "Content-Type": "application/vnd.api+json"
    }

    data = {
        "subscribers": [updates]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        try:
            r = response.json()
            detail = r["errors"][0]["message"]
        except Exception:
            detail = str(e)
        print(f"Failed to subscribe {email} to the campaign. Error message:", detail)
        return f"Could not schedule {email}. Error: {detail}", 502

    print(f'Drip: {email} was updated!')
    return f"{email} was successfully added/scheduled.", 200
