import requests
import os
from datetime import datetime, timedelta
from api.event_class import Event
import math
import threading
from flask import jsonify

def events(now = datetime.now()):
    # Create the request
    next_week = now + timedelta(days=7)
    now, next_week = now.strftime("%Y-%m-%d"), next_week.strftime("%Y-%m-%d")
    endpoint = f"https://developer.nps.gov/api/v1/events?parkCode=glac&dateStart={now}&dateEnd={next_week}&expandRecurring=true&api_key={os.environ['NPS']}"

    # Get response from API
    r = requests.get(endpoint)
    response = r.json()
    total = int(response['total'])
    pages = math.ceil(total/10)

    astro_events = []
    nas_events = []
    lock = threading.Lock()

    def fetch_events(page):
        endpoint = f"https://developer.nps.gov/api/v1/events?parkCode=glac&dateStart={now}&dateEnd={next_week}&pageNumber={page}&expandRecurring=true&api_key={os.environ['NPS']}"
        r = requests.get(endpoint)
        response = r.json()
        page_of_astro = [Event(i) for i in response['data'] if "astronomy" in i['tags']]
        page_of_nas = [Event(i) for i in response['data'] if "Native America Speaks" in i['tags']]

        # Acquire the lock to safely update the shared events list
        with lock:
            astro_events.extend(page_of_astro)
            nas_events.extend(page_of_nas)
    
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
