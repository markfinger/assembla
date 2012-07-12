from .mixins import AssemblaObject, CachesRequests, InitialiseWith
from .error import AssemblaError


class API(AssemblaObject, CachesRequests):
    class Meta:
        cache_schema = ('spaces', 'tasks', 'events',)

    def __init__(self, auth=None, *args, **kwargs):
        """
        :auth is a required argument which should be in the format:
            `('Username', 'Password',)`
        """
        super(API, self).__init__(*args, **kwargs)
        if not auth or len(auth) != 2:
            raise AssemblaError(100)
        self.auth = auth

    def check_credentials(self):
        """
        Attempt to check the authenticity of the auth credentials by retrieving
        a list of the user's spaces. Returns `True` on success.
        """
        self.spaces()
        return True

    def _harvest_child_objects(self, child_class):
        """
        Returns the API's objects matching :child_class.
        """
        url = child_class()._list_url()
        raw_data = self._harvest(url=url, auth=self.auth)
        return [
            child_class(
                auth=self.auth,
                cache_responses=self.cache_responses,
                initialise_with=data[1]
                ) for data in raw_data
            ]

    def _get_spaces(self):
        """
        Returns the authenticated user's spaces from the API
        """
        return self._harvest_child_objects(Space)

    def spaces(self, **kwargs):
        """
        Returns the spaces available to the user
        """
        return self._filter(
            self._get_from_cache('spaces'),
            **kwargs
            )

    def space(self, **kwargs):
        """
        Returns the space with attributes matching the keyword arguments passed
        in.

        Ex: ```api.space(name='my space')```
        """
        return self._get(self.spaces(), **kwargs)

    def _get_tasks(self):
        """
        Returns the authenticated user's tasks from the API
        """
        return self._harvest_child_objects(Task)

    def tasks(self, **kwargs):
        """
        Returns the currently authenticated user's tasks.
        """
        return self._filter(
            self._get_from_cache('tasks'),
            **kwargs
            )

    def task(self, **kwargs):
        """
        Returns the task with attributes matching the keyword arguments passed
        in.

        Ex: ```api.task(description='some work was done')```
        """
        return self._get(self.tasks(), **kwargs)

    def _get_events(self):
        """
        Returns the authenticated user's stream from the API
        """
        return self._harvest_child_objects(Event)

    def events(self, **kwargs):
        """
        Returns the authenticated user's stream as Stream instances.
        """
        return self._filter(
            self._get_from_cache('events'),
            **kwargs
            )

    def event(self, **kwargs):
        """
        Returns the event with attributes matching the keyword arguments passed
        in.

        Ex: ```api.event(title='#734: Display Error')```
        """
        return self._get(self.events(), **kwargs)


class Space(AssemblaObject, InitialiseWith, CachesRequests):
    class Meta(AssemblaObject.Meta):
        primary_key = 'id'
        secondary_key = 'name'
        relative_url = 'spaces/{pk}'
        relative_list_url = 'spaces/my_spaces'
        cache_schema = ('milestones', 'users', 'tickets',)

    def _harvest_child_objects(self, child_class):
        """
        Returns the space's objects matching :child_class.
        """
        space = getattr(self, 'space', self)
        url = child_class(space=space)._list_url()
        raw_data = self._harvest(url=url, auth=self.auth)
        return [
            child_class(
                space=self,
                initialise_with=data[1]
                ) for data in raw_data
            ]

    def _get_milestones(self):
        """
        Returns the space's milestones from the API
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
        Returns the space's tickets from the API
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
        Returns the space's users from the API
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


class Milestone(AssemblaObject, InitialiseWith):
    class Meta(AssemblaObject.Meta):
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


class User(AssemblaObject, InitialiseWith):
    class Meta(AssemblaObject.Meta):
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


class Ticket(AssemblaObject, InitialiseWith):
    class Meta(AssemblaObject.Meta):
        primary_key = 'number'
        relative_url = 'spaces/{space}/tickets/{pk}'
        relative_list_url = 'spaces/{space}/tickets'


class Task(AssemblaObject, InitialiseWith):
    class Meta(AssemblaObject.Meta):
        primary_key = 'id'
        relative_url = 'user/time_entries/{pk}'
        relative_list_url = 'user/time_entries'


class Event(AssemblaObject, InitialiseWith):
    class Meta(AssemblaObject.Meta):
        primary_key = 'id'
        relative_list_url = 'activity'
