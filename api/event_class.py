import api.formatting

class Event:
    """
    Takes the JSON response from the NPS API and formats the data correctly for use in email.
    """
    def __init__(self, data):
        self.title = data['title']
        self.title_cleanup()
        self.day = data['date']
        self.time = data['times'][0]['timestart']
        self.date, self.date_sortable = api.formatting.format_dates(self.day, self.time)
        self.location = data['location']
        self.location_cleanup()
        self.url = f'https://www.nps.gov/planyourvisit/event-details.htm?id={data["id"]}'
    
    def __str__(self):
        return f'<a href="{self.url}">{self.date} — {self.title}, {self.location}</a>'

    def location_cleanup(self):
        loc = self.location.split('/')[0].split('<br>')[0]
        loc = loc.split('(')[0]
        loc = loc.replace(' Amphitheater', '')
        loc = loc.replace('Lucerne Room', '')
        loc = loc.replace(', Lake McDonald Valley', '').replace(', St. Mary Valley', '')
        while loc[-1] == ' ':
            loc = loc[:-1]
        self.location = loc
    
    def title_cleanup(self):
        if '-' in self.title:
            self.title = self.title.split(' - ')[1]
        self.title = self.title.replace(' (Apgar)','').replace(' (St. Mary)','')
