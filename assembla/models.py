from base_models import APIObject, AssemblaObject, Cache
from error import AssemblaError


class API(APIObject):

    class Meta(APIObject.Meta):
        cache_schema = ('spaces',)

    def __init__(self, auth=None, *args, **kwargs):
        """
        :auth is a required argument which should be in the format:
            `('Username', 'Password',)`
        """
        super(API, self).__init__(*args, **kwargs)
        if not auth:
            raise AssemblaError(100)
        self.auth = auth
        # Responses are cached, call ```API.cache.flush()``` to purge any old data.
        self.cache = Cache(self.Meta.cache_schema)

    def __str__(self):
        return 'Assembla API'

    def check_credentials(self):
        """
        Attempt to check the authenticity of the auth credentials by retrieving
        a list of the user's spaces. Returns True on success.
        """
        if not self.spaces():
            raise AssemblaError(110)
        else:
            return True

    def _get_spaces(self):
        raw_data = self._harvest(
            url=Space().list_url(),
            )
        return [
            Space(
                auth=self.auth,
                initialise_with=data[1]
                ) for data in raw_data
            ]
    
    def spaces(self):
        """
        Return the spaces available to the user
        """
        if not self.cache['spaces']:
            self.cache['spaces'] = self._get_spaces()
        return self.cache['spaces']

    def space(self, **kwargs):
        """
        Return the space with attributes matching the keyword arguments passed
        in.

        Ex: ```api.space(name='my space')```
        """
        return self._filter(self.spaces(), **kwargs)


class Space(AssemblaObject):

    class Meta(APIObject.Meta):
        primary_key = 'id'
        secondary_key = 'name'
        relative_url = 'spaces/{pk}'
        relative_list_url = 'spaces/my_spaces'
        cache_schema = ('milestones', 'users', 'tickets',)

    def _harvest_child_objects(self, child_class):
        """
        Harvests and returns the space's objects matching :child_class.
        """
        url = child_class(space=self).list_url()
        raw_data = self._harvest(url=url)
        return [
            child_class(
                space=self,
                initialise_with=data[1]
                ) for data in raw_data
            ]

    def _get_milestones(self):
        """
        Harvests the space's milestones from the API
        """
        return self._harvest_child_objects(Milestone)


    def milestones(self):
        """
        Return the milestones in the space
        """
        if not self.cache.get('milestones'):
            self.cache['milestones'] = self._get_milestones()
        return self.cache.get('milestones')

    def milestone(self, **kwargs):
        """
        Return the milestone with attributes matching the keyword arguments
        passed in.

        Ex: ```space.milestone(name='my milestone')```
        """
        return self._filter(self.milestones(), **kwargs)

    def _get_tickets(self):
        """
        Harvests the space's tickets from the API
        """
        return self._harvest_child_objects(Ticket)

    def tickets(self):
        """
        Return the tickets in the space
        """
        if not self.cache.get('tickets'):
            self.cache['tickets'] = self._get_tickets()
        return self.cache.get('tickets')


    def ticket(self, **kwargs):
        """
        Return the ticket with attributes matching the keyword arguments passed
        in.

        Ex: ```space.ticket(number=51)```
        """
        return self._filter(self.tickets(), **kwargs)

    def _get_users(self):
        """
        Harvests the space's users from the API
        """
        return self._harvest_child_objects(User)

    def users(self):
        """
        Return the users in the space
        """
        if not self.cache.get('users'):
            self.cache['users'] = self._get_users()
        return self.cache.get('users')


    def user(self, **kwargs):
        """
        Return the user with attributes matching the keyword arguments passed
        in.

        Ex: ```space.user(name='John Smith')```
        """
        return self._filter(self.users(), **kwargs)


class Milestone(AssemblaObject):
    class Meta(APIObject.Meta):
        primary_key = 'id'
        secondary_key = 'description'
        relative_url = 'spaces/{space}/milestones/{pk}'
        relative_list_url = 'spaces/{space}/milestones'

    def tickets(self):
        """
        Return the tickets in the milestone
        """
        return filter(
            lambda ticket: ticket.milestone_id == self.id,
            self.space.tickets(),
            )

    def ticket(self, **kwargs):
        """
        Return the ticket with attributes matching the keyword arguments
        passed in.

        Ex: ```milestone.ticket(assigned_to_id=some_user.id)```
        """
        return self._filter(self.tickets(), **kwargs)


class User(AssemblaObject):
    class Meta(APIObject.Meta):
        primary_key = 'id'
        secondary_key = 'name'
        relative_url = 'profile/{pk}'
        relative_list_url = 'spaces/{space}/users'

    def tickets(self):
        """
        Return the tickets in the space which are assigned to the user
        """
        return filter(
            lambda ticket: ticket.assigned_to_id == self.id,
            self.space.tickets(),
            )

    def ticket(self, **kwargs):
        """
        Return the ticket with attributes matching the keyword arguments
        passed in.

        Ex: ```user.ticket(status_name='Accepted')```
        """
        return self._filter(self.tickets(), **kwargs)


class Ticket(AssemblaObject):
    class Meta(APIObject.Meta):
        primary_key = 'number'
        relative_url = 'spaces/{space}/tickets/{pk}'
        relative_list_url = 'spaces/{space}/tickets'