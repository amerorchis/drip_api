from datetime import datetime, timedelta
import requests
import os
import api.formatting

class NASEvent:
    """
    Takes the JSON response from the NPS API and formats the data correctly for use in email.
    """
    def __init__(self, data):
        self.title = data['title']
        self.title_cleanup()
        self.day = data['date']
        self.time = data['times'][0]['timestart']
        self.date = api.formatting.format_dates(self.day, self.time)
        self.location = data['location']
        self.location_cleanup()
        self.url = f'https://www.nps.gov/planyourvisit/event-details.htm?id={data["id"]}'
    
    def __str__(self):
        return f'<a href="{self.url}">{self.date} — {self.title}, {self.location}</a>'

    def location_cleanup(self):
        loc = self.location.split('/')[0]
        loc = loc.split('(')[0]
        loc = loc.replace('Amphitheater', '')
        loc = loc.replace('Lucerne Room', '')
        while loc[-1] == ' ':
            loc = loc[:-1]
        self.location = loc
    
    def title_cleanup(self):
        if '-' in self.title:
            self.title = self.title.split(' - ')[1]

def nas_events(now = datetime.now()):
    # Create the request
    next_week = now + timedelta(days=7)
    endpoint = f"https://developer.nps.gov/api/v1/events?parkCode=glac&dateStart={now}&dateEnd={next_week}"

    # Add authentication request
    key = os.environ['NPS']
    HEADERS = {"X-Api-Key":key}

    # Get response from API
    r = requests.get(endpoint,headers=HEADERS)
    response = r.json()

    # 
    nas = [NASEvent(i) for i in response['data'] if "Native America Speaks" in i['tags']]
    event_str = []
    for i in nas:
        event_str.append(i.__str__())
    return '|'.join(event_str)
