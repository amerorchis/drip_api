import requests
import os
from datetime import datetime, timedelta
from api.event_class import Event
import math
import threading

def events(now = None):
    if now is None:
        now = datetime.now()

    # Create the request
    next_week = now + timedelta(days=7)
    now, next_week = now.strftime("%Y-%m-%d"), next_week.strftime("%Y-%m-%d")
    endpoint = f"https://developer.nps.gov/api/v1/events?parkCode=glac&dateStart={now}&dateEnd={next_week}&expandRecurring=true&api_key={os.environ['NPS']}"

    # Get response from API
    r = requests.get(endpoint)
    r.raise_for_status()
    response = r.json()
    total = int(response.get('total', 0))
    pages = math.ceil(total/10) if total else 0

    astro_events = []
    nas_events = []
    lock = threading.Lock()

    def make_events(data, tag):
        made = []
        for i in data:
            if tag not in i['tags']:
                continue
            try:
                made.append(Event(i))
            except Exception as e:
                print(f'Skipping malformed event {i.get("id")}: {e}')
        return made

    def fetch_events(page):
        try:
            endpoint = f"https://developer.nps.gov/api/v1/events?parkCode=glac&dateStart={now}&dateEnd={next_week}&pageNumber={page}&expandRecurring=true&api_key={os.environ['NPS']}"
            r = requests.get(endpoint)
            r.raise_for_status()
            response = r.json()
            page_of_astro = make_events(response['data'], "astronomy")
            page_of_nas = make_events(response['data'], "Native America Speaks")

            # Acquire the lock to safely update the shared events list
            with lock:
                astro_events.extend(page_of_astro)
                nas_events.extend(page_of_nas)
        except Exception as e:
            print(f'Skipping page {page} due to error: {e}')

    threads = []

    for page in range(pages):
        t = threading.Thread(target=fetch_events, args=[(page + 1)])
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    def stringify_events(events):
        events.sort(key=lambda x: x.date_sortable)
        event_str = []
        for i in events:
            # print(i.__str__())
            event_str.append(i.__str__())
        return '|'.join(event_str)

    return {'nas': stringify_events(nas_events), 'astro':stringify_events(astro_events), 'test': 'The API is reading plain text.'}
