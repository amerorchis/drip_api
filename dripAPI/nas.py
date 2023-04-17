import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dripAPI.nas_mods import *

def nas_events(now = datetime.now()):

    # Pull site and grab elements with event data
    r = requests.get('https://www.nps.gov/glac/planyourvisit/nas.htm')
    soup = BeautifulSoup(r.content, features='lxml')
    accords = soup.find_all("div", class_="accordion-collapse")

    # Extract the relevant text and save it in a list
    events = [i.text.split('\n') for i in accords]
    events = [i.strip().replace('*','') for i in events[0] + events[1] + events[2] + events[3] if i and " pm - " in i]

    dt_events = dict()
    events = [i.split(' - ') for i in events] # Seperate date from event info

    # Create a dict where each event is stored by its datetime object
    for i in events:
        details = " ".join(i[1:]).replace(', Evening Program, ', ', ').replace(', Cultural Presentation, ', ', ').replace('Amphitheater', '')
        dt_events[format_date(i[0])] = details

    # Create a range from now to a week from now
    next_week = now + timedelta(days=7)

    # Add events this week to a list and format them into strings
    events_this_week = []
    for i in dt_events:
        if i > now and i < next_week:
            events_this_week.append('{:<28}{}{}'.format(str_from_key(i), '— ',dt_events[i]))

    # Convert the list back into a string and return it.
    if events_this_week:
        event_str = '|'.join(events_this_week)
        return "Events this week:|" + event_str
    else:
        return ""
