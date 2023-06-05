from datetime import datetime

def format_dates(day, time):
    # Tue. July 4, 8:00pm
    original = datetime.strptime(f"{day} at {time}", "%Y-%m-%d at %I:%M %p")
    return original.strftime("%a. %B %d, %I:%M%p").replace(' 0', ' ')
