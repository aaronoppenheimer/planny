from requestmodel import *

def get_calendar_list():
    calendarList = service.calendarList().list().execute(http=decorator.http())
    return calendarList['items']

def get_calendar_from_calendar_id(the_calendar_id):
    calendar = service.calendars().get(calendarId=the_calendar_id).execute(http=decorator.http())
    return calendar

def get_events_from_calendar_id(the_calendar_id):
    eventList = service.events().list(calendarId=the_calendar_id).execute(http=decorator.http())
    return eventList

class CalListHandler(BaseHandler):
    @decorator.oauth_required
    def get(self):
        the_calendar_list = get_calendar_list()
        template_args = {
            'title' : "Calendar List",
            'the_calendar_list' : the_calendar_list,
        }
        self.render_template('calendar_list.html', template_args)

class EventListHandler(BaseHandler):
    @decorator.oauth_required
    def get(self):
        
        the_cal_id = self.request.get("calid",None)
        if the_cal_id is None:
            return # todo figure out what to do
            
        the_calendar = get_calendar_from_calendar_id(the_cal_id)
        the_event_list = get_events_from_calendar_id(the_cal_id)
        
        template_args = {
            'title' : "Event List",
            'the_calendar' : the_calendar,
            'the_event_list' : the_event_list['items']
        }
        self.render_template('calendar_events.html', template_args)
