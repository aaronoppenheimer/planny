"""
Base class for webapp2 request handlers
"""

import httplib2
import cal
import logging

from google.appengine.api import users
import webapp2
from jinja2env import jinja_environment as je

class BaseHandler(webapp2.RequestHandler):

    def render_template(self, filename, params=None):
        if not params:
            params = {}

        params['the_user'] = users.get_current_user()

        template = je.get_template(filename)
        self.response.write(template.render(params))
        