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

        # set up some initial date/view parameters
        the_focus = datetime.datetime.today().toordinal()
        the_weeks = 24

        template_args = {
            'title' : "Calendar List",
            'the_calendar_list' : the_calendar_list,
            'the_calendar': the_cal_id,
            'the_focus' : the_focus,
            'the_weeks' : the_weeks
        }
        self.render_template('calendar_list.html', template_args)

class EventListHandler(BaseHandler):

    @cal.decorator.oauth_required
    def post(self):
        
        the_cal_id = self.request.get("cal",None)
        if the_cal_id is None:
            the_calendar_list = cal.get_calendar_list()
            the_cal_id = the_calendar_list[0]['id']
            for c in the_calendar_list:
                if c['primary']:
                    the_cal_id = c['id']

        the_start_date_str = self.request.get("focus",None)
        if the_start_date_str:
            center_day = datetime.datetime.fromordinal(int(the_start_date_str))
        else:
            center_day = datetime.datetime.now()

        the_weeks_str = self.request.get("weeks",None)
        if the_weeks_str:
            the_weeks = int(the_weeks_str)
        else:
            the_weeks = 24

        the_start_date = datetime.datetime.fromordinal(center_day.toordinal() - center_day.weekday() - 21)
        the_end_date = datetime.datetime.fromordinal(center_day.toordinal() - center_day.weekday() + (the_weeks * 7))
                
        the_calendar = cal.get_calendar_from_calendar_id(the_cal_id)
        the_event_list = cal.get_events_from_calendar_id(the_cal_id,
                                                     the_start_date = the_start_date, 
                                                     the_end_date = the_end_date)

        the_plangroup_list = plangroup.get_all_plangroups_for_user(keys_only=False)
        
        the_sorted_events = cal.get_events_by_plangroup_for_user(the_cal_id,
                                                                 the_start_date = the_start_date,
                                                                 the_end_date = the_end_date)
        # --- BEGIN VICTOR CODE ---                                                         
        the_event_list_allday=[]
    	display_start = the_start_date
    	display_end = the_end_date
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

        the_sorted_events_allday={}
        for pg in the_sorted_events.keys():
            group_info = the_sorted_events[pg]
            for e in group_info[1]:
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
        		    if pg in the_sorted_events_allday:
        		        the_sorted_events_allday[pg][1].append(e)
        		    else:
        		        the_sorted_events_allday[pg] = (group_info[0],[e])
        		        
        display_months=[]
        date_i = display_start
        while date_i < display_end:
		    month = date_i.month + 1
		    year = date_i.year 
		    if month > 12:
		        month = 1
		        year = year + 1
		    month_end = datetime.datetime.fromordinal(datetime.datetime(year, month, 1).toordinal() - 1).day
		    my_month = {
		        'name': date_i.strftime('%B'),
		        'days': month_end - date_i.day + 1
		    }
		    display_months.append(my_month)
		    date_i = datetime.datetime(year, month, 1)
        # --- END VICTOR CODE ----
        
        template_args = {
            'the_calendar' : the_calendar,
            'the_plangroup_list' : the_plangroup_list,
#            'the_event_list' : the_event_list['items'],
			'the_event_list': the_event_list_allday,
            'the_sorted_events' : the_sorted_events_allday,
            'display_months': display_months,    
        }
        self.render_template('calendar_timeline.html', template_args)
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
