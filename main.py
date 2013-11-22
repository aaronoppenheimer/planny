#
#   Planny the Happy Planner
#
#   VGS / AO 2013-11-21
#

import webapp2
import cal

app = webapp2.WSGIApplication(
    [
     ('/', cal.CalListHandler),
     (cal.decorator.callback_path, cal.decorator.callback_handler()),
     ('/calendar_list.html', cal.CalListHandler, 'cal_list'),
     ('/calendar_events', cal.EventListHandler, 'event_list')
    ],
    debug=True)
