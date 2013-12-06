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
                
        the_calendar = cal.get_calendar_from_calendar_id(the_cal_id)
        the_event_list = cal.get_events_from_calendar_id(the_cal_id,
                                                     the_start_date = start_date, 
                                                     the_end_date = end_date)

        the_plangroup_list = plangroup.get_all_plangroups_for_user(keys_only=False)
        
        the_sorted_events = cal.get_events_by_plangroup_for_user(the_cal_id,
                                                                 the_start_date = start_date,
                                                                 the_end_date = end_date)
        # --- BEGIN VICTOR CODE ---                                                         
        the_event_list_allday=[]
        today = datetime.datetime.today()
    	display_start = datetime.datetime.fromordinal(today.toordinal() - today.weekday() - 21)
        for e in the_event_list['items']:
        	if 'start' in e and 'date' in e['start']:
        		timedelta = datetime.datetime.strptime((e['end'].get('date')),'%Y-%m-%d') - \
        					datetime.datetime.strptime((e['start'].get('date')),'%Y-%m-%d')
        		e['duration'] = timedelta.days
        		timedelta = datetime.datetime.strptime((e['start'].get('date')),'%Y-%m-%d') - \
        		            display_start
        		e['from_start'] = timedelta.days
        		if e['from_start'] < 0:
        		    e['duration'] = e['duration'] + e['from_start']
        		    e['from_start'] = 0
        		the_event_list_allday.append(e)	

        today = datetime.date.today()
    	display_start = datetime.date.fromordinal(today.toordinal() - today.weekday() - 21)
    	display_end   = datetime.date.fromordinal(display_start.toordinal() + 24 * 7)

        display_months=[]
        date_i = display_start
        while date_i < display_end:
		    month = date_i.month + 1
		    year = date_i.year 
		    if month > 12:
		        month = 1
		        year = year + 1
		    month_end = datetime.date.fromordinal(datetime.date(year, month, 1).toordinal() - 1).day
		    my_month = {
		        'name': date_i.strftime('%B'),
		        'days': month_end - date_i.day + 1
		    }
		    display_months.append(my_month)
		    date_i = datetime.date(year, month, 1)
        # --- END VICTOR CODE ----
        
        template_args = {
            'the_calendar' : the_calendar,
            'the_plangroup_list' : the_plangroup_list,
#            'the_event_list' : the_event_list['items'],
			'the_event_list': the_event_list_allday,
            'the_sorted_events' : the_sorted_events,
            'the_month_string' : start_date.strftime("%b, %Y"),
            'the_month' : start_date.month,
            'the_year' : start_date.year,
            'display_months': display_months,    
        }
        #self.render_template('calendar_events.html', template_args)
        self.render_template('calendar_timeline.html', template_args)
        
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
        
class AddEventToGroupHandler(BaseHandler):
    @cal.decorator.oauth_required
    def post(self):
        the_event_id = self.request.get('event_id','')
        the_group_keyurl = self.request.get('group_select','')
        
        if the_event_id == '' or the_group_keyurl == '':
            return # todo what to do?
        
        the_plangroup_key = ndb.Key(urlsafe = the_group_keyurl)
        plangroup.add_event_to_plangroup_by_key(the_event_id=the_event_id, the_plangroup_key=the_plangroup_key)
        
        return self.redirect('/')
        
class RemoveEventFromGroupHandler(BaseHandler):
    @cal.decorator.oauth_required
    def get(self):
    
        the_event_id = self.request.get('e','')
        the_group_keyurl = self.request.get('g','')

        if the_event_id == '' or the_group_keyurl == '':
            return # todo what to do?

        the_plangroup_key = ndb.Key(urlsafe = the_group_keyurl)
        plangroup.remove_event_from_plangroup_by_key(the_event_id=the_event_id, the_plangroup_key=the_plangroup_key)
        
        return self.redirect('/')
