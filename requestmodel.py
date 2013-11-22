"""
Base class for webapp2 request handlers
"""

import httplib2
import logging
import os

from apiclient import discovery
from oauth2client import appengine
from oauth2client import client
from google.appengine.api import memcache

import webapp2
from jinja2env import jinja_environment as je

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

class BaseHandler(webapp2.RequestHandler):

    def render_template(self, filename, params=None):
        if not params:
            params = {}

        template = je.get_template(filename)
        self.response.write(template.render(params))
        