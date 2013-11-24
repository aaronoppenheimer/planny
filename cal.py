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
    eventList = service.events().list(calendarId=the_calendar_id, timeMin=the_start_date, timeMax=the_end_date).execute(http=decorator.http())
    return eventList
