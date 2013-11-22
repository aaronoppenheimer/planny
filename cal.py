from requestmodel import *
import datetime

def get_calendar_list():
    calendarList = service.calendarList().list().execute(http=decorator.http())
    return calendarList['items']

def get_calendar_from_calendar_id(the_calendar_id):
    calendar = service.calendars().get(calendarId=the_calendar_id).execute(http=decorator.http())
    return calendar

def get_events_from_calendar_id(the_calendar_id, the_start_date=None, the_end_date=None):
    eventList = service.events().list(calendarId=the_calendar_id, timeMin=the_start_date, timeMax=the_end_date).execute(http=decorator.http())
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

        month_str=self.request.get("m",None)
        year_str=self.request.get("y",None)
        if month_str==None or year_str==None:
            start_date = datetime.datetime.now()
        else:
            delta_str=self.request.get("d",0)
            delta=int(delta_str)
            year=int(year_str)
            month=int(month_str)
            month=month+delta
            if month>12:
                month = 1
                year = year+1
            if month<1:
                month=12
                year = year-1
            start_date = datetime.datetime(year=year, month=month, day=1)
                        
        month = start_date.month
        year = start_date.year
        month=month+1
        if month>12:
            month = 1
            year = year+1
        if month<1:
            month=12
            year = year-1
        end_date = datetime.datetime(year=year, month=month, day=1)

        iso_start_date= start_date.strftime("%Y-%m-%dT%H:%M:%S-05:00")
        iso_end_date= end_date.strftime("%Y-%m-%dT%H:%M:%S-05:00")
        
        the_calendar = get_calendar_from_calendar_id(the_cal_id)
        the_event_list = get_events_from_calendar_id(the_cal_id,
                                                     the_start_date = iso_start_date, 
                                                     the_end_date = iso_end_date)
        
        template_args = {
            'title' : "Event List",
            'the_calendar' : the_calendar,
            'the_event_list' : the_event_list['items'],
            'the_month_string' : start_date.strftime("%b, %Y"),
            'the_month' : start_date.month,
            'the_year' : start_date.year,
        }
        self.render_template('calendar_events.html', template_args)
