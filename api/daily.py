from api.drip import *

from datetime import datetime

def daily(args: dict):
    email, start, end = args.get('email'), args.get('start'), args.get('end')

    now = datetime.now()

    dt_start = None
    if start:
        dt_start = datetime.strptime(start, "%Y-%m-%d")

    updates = {"email": email}
    custom_fields = {}

    # If the start date is today or earlier tag and add immediately
    if dt_start <= now or not start:
        updates['tags'] = ["Glacier Daily Update"]

        # If it's already gone out today, add them to the workflow now.
        if now.hour > 8:
            try:
                add_to_workflow(email, campaign_id='169298893')
            except Exception as e:
                print(e)

    # If start is in the future, store it in Drip.
    else:
        custom_fields['Daily_Start'] = start
    
    if end:
        custom_fields['Daily_End'] = end

    # Store values in account
    updates["custom_fields"] = custom_fields

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
        "subscribers": [updates]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    r = response.json()
    
    if response.status_code == 200:
        print(f'Drip: {email} was updated!')
        return f"{email} was successfully added/scheduled."
    
    else:
        print(f"Failed to subscribe {email} to the campaign. Error message:", r["errors"][0]["code"], ' - ', r["errors"][0]["message"])
        return False
        