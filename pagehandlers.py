from requestmodel import *
import datetime
import cal
import plangroup

from google.appengine.ext import ndb

class CalListHandler(BaseHandler):

    @cal.decorator.oauth_required
    def get(self):
        the_calendar_list = cal.get_calendar_list()

        the_cal_id = the_calendar_list[0]['id']
        for c in the_calendar_list:
            if 'primary' in c and c['primary']:
                the_cal_id = c['id']

        template_args = {
            'title' : "Calendar List",
            'the_calendar_list' : the_calendar_list,
            'the_calendar': the_cal_id
        }
        self.render_template('calendar_list.html', template_args)

class EventListHandler(BaseHandler):

    @cal.decorator.oauth_required
    def post(self):
        
        the_cal_id = self.request.get("c",None)
        if the_cal_id is None:
            the_calendar_list = cal.get_calendar_list()
            the_cal_id = the_calendar_list[0]['id']
            for c in the_calendar_list:
                if c['primary']:
                    the_cal_id = c['id']

        month_str=self.request.get("m",'')
        year_str=self.request.get("y",'')
        if month_str=='' or year_str=='':
            month_str = datetime.datetime.now().month
            year_str = datetime.datetime.now().year

        delta_str=self.request.get("d",'0')

        delta=int(delta_str)
        year=int(year_str)
        month=int(month_str)
        month=month+delta

        while month > 12:
            month = month-12
            year = year+1

        while month < 1:
            month=month+12
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
                
        the_calendar = cal.get_calendar_from_calendar_id(the_cal_id)
        the_event_list = cal.get_events_from_calendar_id(the_cal_id,
                                                     the_start_date = iso_start_date, 
                                                     the_end_date = iso_end_date)

        the_plangroup_list = plangroup.get_all_plangroups_for_user(keys_only=False)
        
        template_args = {
            'the_calendar' : the_calendar,
            'the_plangroup_list' : the_plangroup_list,
            'the_event_list' : the_event_list['items'],
            'the_month_string' : start_date.strftime("%b, %Y"),
            'the_month' : start_date.month,
            'the_year' : start_date.year,
        }
        self.render_template('calendar_events.html', template_args)

class NewGroupHandler(BaseHandler):
    @cal.decorator.oauth_required
    def post(self):
        
        the_new_name = self.request.get("new_group_name",'')
        if the_new_name != '':
            plangroup.new_plangroup(the_new_name)

        return self.redirect('/')

class DeleteGroupHandler(BaseHandler):
    @cal.decorator.oauth_required
    def get(self):
        
        the_group_keyurl = self.request.get('gid','')
        if the_group_keyurl == '':
            return # todo what to do?
            
        the_group_key = ndb.Key(urlsafe=the_group_keyurl)
        plangroup.forget_plangroup_from_key(the_group_key)
        return self.redirect('/')        