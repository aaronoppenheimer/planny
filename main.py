#
#   Planny the Happy Planner
#
#   VGS / AO 2013-11-21
#

import webapp2
import cal
import pagehandlers

app = webapp2.WSGIApplication(
    [
     ('/', pagehandlers.CalListHandler),
     (cal.decorator.callback_path, cal.decorator.callback_handler()),
     ('/calendar_list.html', pagehandlers.CalListHandler, 'cal_list'),
     ('/calendar_events', pagehandlers.EventListHandler, 'event_list'),
     ('/add_group', pagehandlers.NewGroupHandler),
     ('/delete_group', pagehandlers.DeleteGroupHandler)
    ],
    debug=True)
