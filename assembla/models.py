from base_models import APIObject, AssemblaObject
from error import AssemblaError


class API(APIObject):

    def __init__(self, auth=None, use_cache=True, *args, **kwargs):
        """
        :auth is a required argument which should be in the format:
            `('Username', 'Password',)`
        """
        super(API, self).__init__(*args, **kwargs)
        if not auth:
            raise AssemblaError(100)
        self.auth = auth
        self.use_cache = use_cache

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
        raw_data = self._harvest(url=Space().list_url(), auth=self.auth)
        return [
            Space(
                auth=self.auth,
                use_cache=self.use_cache,
                initialise_with=data[1]
                ) for data in raw_data
            ]

    def spaces(self):
        """
        Returns the spaces available to the user
        """
        return self._get_spaces()

    def space(self, **kwargs):
        """
        Returns the space with attributes matching the keyword arguments passed
        in.

        Ex: ```api.space(name='my space')```
        """
        return self._get(self.spaces(), **kwargs)


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
        raw_data = self._harvest(url=url, auth=self.auth)
        return [
            child_class(
                space=self,
                initialise_with=data[1]
                ) for data in raw_data
            ]

    def _get_from_cache(self, child):
        """
        Returns the cached data for the space's children denoted by :child.

        If the cache has no data for :child, the cache is updated and cached
        data is returned.

        If the cache has been deactivated, the data is freshly harvested from
        the API and returned.
        """
        child_func = getattr(self, '_get_{0}'.format(child))
        if self.cache.cache_responses:
            if not self.cache.has_cached(child):
                self.cache.set(child, child_func())
            return self.cache.get(child)
        else:
            return child_func()


    def _get_milestones(self):
        """
        Harvests the space's milestones from the API
        """
        return self._harvest_child_objects(Milestone)

    def milestones(self, **kwargs):
        """
        Returns the milestones in the space
        """
        return self._filter(
            self._get_from_cache('milestones'),
            **kwargs
            )

    def milestone(self, **kwargs):
        """
        Returns the milestone with attributes matching the keyword arguments
        passed in.

        Ex: ```space.milestone(name='my milestone')```
        """
        return self._get(self.milestones(), **kwargs)

    def _get_tickets(self):
        """
        Harvests the space's tickets from the API
        """
        return self._harvest_child_objects(Ticket)

    def tickets(self, **kwargs):
        """
        Returns the tickets in the space
        """
        return self._filter(
            self._get_from_cache('tickets'),
            **kwargs
            )

    def ticket(self, **kwargs):
        """
        Returns the ticket with attributes matching the keyword arguments passed
        in.

        Ex: ```space.ticket(number=51)```
        """
        return self._get(self.tickets(), **kwargs)

    def _get_users(self):
        """
        Harvests the space's users from the API
        """
        return self._harvest_child_objects(User)

    def users(self, **kwargs):
        """
        Returns the users in the space
        """
        return self._filter(
            self._get_from_cache('users'),
            **kwargs
            )


    def user(self, **kwargs):
        """
        Returns the user with attributes matching the keyword arguments passed
        in.

        Ex: ```space.user(name='John Smith')```
        """
        return self._get(self.users(), **kwargs)


class Milestone(AssemblaObject):
    class Meta(APIObject.Meta):
        primary_key = 'id'
        secondary_key = 'description'
        relative_url = 'spaces/{space}/milestones/{pk}'
        relative_list_url = 'spaces/{space}/milestones'

    def tickets(self, **kwargs):
        """
        Returns the tickets in the milestone
        """
        return self._filter(self.space.tickets(**kwargs), milestone_id=self.id)

    def ticket(self, **kwargs):
        """
        Returns the ticket with attributes matching the keyword arguments
        passed in.

        Ex: ```milestone.ticket(assigned_to_id=some_user.id)```
        """
        return self._get(self.tickets(), **kwargs)


class User(AssemblaObject):
    class Meta(APIObject.Meta):
        primary_key = 'id'
        secondary_key = 'name'
        relative_url = 'profile/{pk}'
        relative_list_url = 'spaces/{space}/users'

    def tickets(self, **kwargs):
        """
        Returns the tickets in the space which are assigned to the user
        """
        return self._filter(self.space.tickets(**kwargs), assigned_to_id=self.id)

    def ticket(self, **kwargs):
        """
        Returns the ticket with attributes matching the keyword arguments
        passed in.

        Ex: ```user.ticket(status_name='Accepted')```
        """
        return self._get(self.tickets(), **kwargs)


class Ticket(AssemblaObject):
    class Meta(APIObject.Meta):
        primary_key = 'number'
        relative_url = 'spaces/{space}/tickets/{pk}'
        relative_list_url = 'spaces/{space}/tickets'