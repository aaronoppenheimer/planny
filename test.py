from apiclient.discovery import build
import json
from oauth2client.appengine import OAuth2Decorator
import webapp2

decorator = OAuth2Decorator(
  client_id='your_client_id',
  client_secret='your_client_secret',
  scope='https://www.googleapis.com/auth/calendar')

service = build('calendar', 'v3')


class MainPage(webapp2.RequestHandler):
  @decorator.oauth_required
  def get(self):
    # This will force the user to go through OAuth
    self.response.write(...)
    # show some page to them
    
app = webapp2.WSGIApplication([
    ('/', MainPage),
    (decorator.callback_path, decorator.callback_handler())
    ],
    debug=True)    