from base_models import *
from error import AssemblaError


class _API(APIObject):

    class Meta(APIObject.Meta):
        pass

    def __init__(self, auth=None):
        super(_API, self).__init__()
        if not auth:
            raise AssemblaError(100)
        self.auth = auth

    def check_credentials(self):
        """
        Attempt to check the authenticity of the auth credentials by retrieving
        a list of the user's spaces. Returns True on success.
        """
        if not self.spaces():
            raise AssemblaError(110)
        else:
            return True

    def space(self, id=None, name=None):
        """
        Return the space which has an id equal to :id or name equal to :name.
        """
        assert id or name # One of the arguments are required
        return reduce(
            lambda space: space.id==id or space.name==name,
            self.spaces(),
        )

    def spaces(self):
        return self.harvest(
            url=Space().list_url(),
        )



class Space(APIObject):
    id = None
    class Meta(APIObject.Meta):
        primary_key = 'id'
        relative_url = 'spaces/{pk}'
        relative_list_url = 'spaces/my_spaces'
        has_objects = ('milestone', 'ticket', 'user',)


class Milestone(APIObject):
    class Meta(APIObject.Meta):
        primary_key = 'id'
        relative_url = 'spaces/{space}/milestones/{pk}'
        relative_list_url = relative_url
        has_objects = ('ticket', 'user',)


class User(APIObject):
    class Meta(APIObject.Meta):
        primary_key = 'id'
        # Should test if profiles/{pk} works, this seems a bit weird
        relative_url = 'user/best_profile/{pk}'
        relative_list_url = relative_url
        has_objects = ('ticket',)


class Ticket(APIObject):
    class Meta(APIObject.Meta):
        primary_key = 'number'
        relative_url = 'spaces/{space}/tickets/{pk}'
        relative_list_url = relative_url
