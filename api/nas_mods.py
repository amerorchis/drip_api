from datetime import datetime

def format_date(date: str) -> datetime:
    month, day, DOW, time, pm = date.split()
    month = month.replace('Sept', 'September').replace('Aug', 'August').replace('.','')
    day = day.replace(',','')
    hour, minute = time.split(':')
    format_str = "%B %d %I:%M %p"
    dt = datetime.strptime(f'{month} {day} {hour}:{minute} {pm}', format_str)
    return dt.replace(year=datetime.now().year)

def str_from_key(key) -> str:
    return key.strftime('%a. %B %-d, %-I:%M%p').replace('AM', 'am').replace('PM', 'pm')
