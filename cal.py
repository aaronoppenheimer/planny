#
# Functions for getting calendars and events from Google Calendar
#
# AO 23 November 2013

import os
from apiclient import discovery
from oauth2client import appengine
from oauth2client import client
from google.appengine.api import memcache
import httplib2
import plangroup

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

http = httplib2.Http(memcache)
service = discovery.build('calendar', 'v3', http=http)

decorator = appengine.oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope=[
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message='uh oh')


def get_calendar_list():
    calendarList = service.calendarList().list().execute(http=decorator.http())
    return calendarList['items']

def get_calendar_from_calendar_id(the_calendar_id):
    calendar = service.calendars().get(calendarId=the_calendar_id).execute(http=decorator.http())
    return calendar

def get_events_from_calendar_id(the_calendar_id, the_start_date=None, the_end_date=None):
    
    # convert dates to iso strings
    if the_start_date:
        the_start_date= the_start_date.strftime("%Y-%m-%dT%H:%M:%S-05:00")
    if the_end_date:
        the_end_date= the_end_date.strftime("%Y-%m-%dT%H:%M:%S-05:00")

    eventList = service.events().list(calendarId=the_calendar_id, timeMin=the_start_date, timeMax=the_end_date).execute(http=decorator.http())
    return eventList

def get_events_by_plangroup_for_user(the_cal_id, the_start_date = None, the_end_date = None):
    """ get all events in the time, then sort by plangroup """
    the_events = get_events_from_calendar_id(the_cal_id, the_start_date=the_start_date, the_end_date=the_end_date )
    if the_events:
        the_sorted_events = plangroup.sort_events_by_plangroup(the_events['items'])
    return the_sorted_events