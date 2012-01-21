from base_models import *
from error import AssemblaError


class _API(AssemblaObject, HasObjects):
    class Meta:
        has_objects = ('space',)
    def __init__(self, auth=None):
        super(_API, self).__init__()
        if auth:
            self.auth = auth

    def set_credentials(self, auth):
        if auth:
            self.auth = auth
        else:
            raise AssemblaError(100)

    def check_credentials(self):
        if 1:
            raise AssemblaError(110)
        else:
            return True


class Space(APIObject, HasObjects):
    class Meta(APIObject.Meta):
        primary_key = 'id'
        relative_url = 'spaces/{pk}'
        has_objects = ('milestone', 'ticket', 'user',)


class Milestone(APIObject, HasObjects):
    class Meta(APIObject.Meta):
        primary_key = 'id'
        relative_url = 'spaces/{space}/milestones/{pk}'
        has_objects = ('ticket', 'user',)


class User(APIObject, HasObjects):
    class Meta(APIObject.Meta):
        primary_key = 'id'
        relative_url = 'profiles/{pk}'
        # Should test if profiles/{pk} works, this seems a bit weird
        relative_api_url = 'user/best_profile/{pk}'
        has_objects = ('ticket',)


class Ticket(APIObject):
    class Meta(APIObject.Meta):
        primary_key = 'number'
        relative_url = 'spaces/{space}/tickets/{pk}'
