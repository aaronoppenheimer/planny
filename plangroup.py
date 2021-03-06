#
# plangroup class
#
# Aaron Oppenheimer
# 23 November 2013
#

from google.appengine.ext import ndb
from google.appengine.api import users

def plangroup_key():
    """Constructs a Datastore key for the plangroup parent"""
    return ndb.Key('Plangroup', 'planny')

#
# class for plangroup - just a set of pointers to google calendar objects
#
class Plangroup(ndb.Model):
    userid = ndb.StringProperty()
    name = ndb.StringProperty()
    events = ndb.StringProperty(repeated=True)
    
def new_plangroup(the_name):
    """ Make and return a new plangroup """
    the_plangroup = Plangroup(userid=users.get_current_user().user_id(), name=the_name, parent=plangroup_key())
    the_plangroup.put()
    return the_plangroup

def forget_plangroup_from_key(the_plangroup_key):
    """ Make a plangroup go away """
    the_plangroup_key.delete()
    
def add_event_to_plangroup_by_key(the_event_id, the_plangroup_key):
    """ Add an event to a plangroup """
    the_plangroup = the_plangroup_key.get()
    the_plangroup.events.append(the_event_id)
    the_plangroup.put()

def remove_event_from_plangroup_by_key(the_event_id, the_plangroup_key):
    """ Remove an event from a plangroup """
    the_plangroup = the_plangroup_key.get()
    if the_event_id in the_plangroup.events:
        the_plangroup.events.pop( the_plangroup.events.index(the_event_id) )
    the_plangroup.put()
    
def get_all_plangroups_for_user(keys_only=False):
    """ Get all plangroups for the logged-in user """
    plangroup_query = Plangroup.query(Plangroup.userid==users.get_current_user().user_id(), 
                                      ancestor=plangroup_key()).order(Plangroup.name)
    all_plangroups = plangroup_query.fetch(keys_only=keys_only)
    return all_plangroups

def get_plangroups_for_event(the_event_id):
    """ take an event ID and from that find a plangroup, if there is one """
    the_plangroup=None
    plangroup_query = Plangroup.query(Plangroup.userid==users.get_current_user().user_id(),
                                      Plangroup.events==the_event_id,
                                      ancestor=plangroup_key())
    plangroups = plangroup_query.fetch()
    return plangroups

def sort_events_by_plangroup(the_events):
    """ take all of the events for a user, then find the groups for the user and sort """
    
    the_sorted_list={}
    for e in the_events:
        the_plangroups = get_plangroups_for_event(e['id'])
        if len(the_plangroups) > 0:
            for a_plangroup in the_plangroups:
                pg_id = a_plangroup.key
            
                if pg_id in the_sorted_list:
                    the_sorted_list[pg_id][1].append(e)
                else:
                    the_sorted_list[pg_id] = (a_plangroup,[e])
        else:
            if None in the_sorted_list:
                the_sorted_list[None][1].append(e)
            else:
                the_sorted_list[None] = (None,[e])
                    
    return the_sorted_list
    
