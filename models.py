from base_models import *


class API(AssemblaObject, HasSpaces):
    pass


class Space(AssemblaObject, HasMilestones, HasTickets, HasUsers):
    primary_key = '?????'
    relative_url = 'spaces/{pk}/'
    relative_api_url = ''

class Milestone(AssemblaObject, HasTickets, HasUsers):
    primary_key = '????'
    relative_url = 'spaces/{space}/milestones/{pk}'
    relative_api_url = ''


class User(AssemblaObject, HasSpaces, HasTickets):
    primary_key = 'loginname'
    relative_url = 'profiles/{pk}'
    relative_api_url = 'user/best_profile?login={pk}'


class Ticket(AssemblaObject):
    primary_key = 'number'
    relative_url = 'spaces/{space}/tickets/{pk}/'
    relative_api_url = ''

