from datetime import datetime, timedelta
import pytz

def get_remaining_time():
    now = datetime.now(pytz.timezone('US/Mountain'))  # Get the current time in Mountain Time
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    remaining_time = (midnight - now).seconds
    return remaining_time
