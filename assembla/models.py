from base_models import APIObject, AssemblaObject, Cache
from error import AssemblaError


class API(APIObject):
    def __init__(self, auth=None, *args, **kwargs):
        """
        :auth is a required argument which should be in the format:
            `('Username', 'Password',)`
        """
        super(API, self).__init__(*args, **kwargs)
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

    def spaces(self):
        """
        Return the spaces available to the user, each space is instantiated as
        a Space
        """
        raw_data = self._harvest(
            url=Space().list_url(),
            )
        return [
            Space(
                auth=self.auth,
                initialise_with=data[1]
                ) for data in raw_data
            ]

    def space(self, **kwargs):
        """
        Return the space with attributes matching the keyword arguments passed
        in.

        Ex:
            ```
            space(id=1, name='my space')
            ```
            returns the space with matching attributes
        """
        return self._filter(self.spaces(), **kwargs)


class Space(AssemblaObject):

    cache = Cache()

    class Meta(APIObject.Meta):
        primary_key = 'id'
        relative_url = 'spaces/{pk}'
        relative_list_url = 'spaces/my_spaces'

    def _milestones(self):
        """
        Returns a list of Milestone instances created from the API
        """
        url = Milestone(space=self).list_url()
        raw_data = self._harvest(url=url)
        return [
            Milestone(
                space=self,
                initialise_with=data[1]
                ) for data in raw_data
            ]

    def milestones(self):
        """
        Return the milestones in the space
        """
        if not self.cache['milestones']:
            self.cache['milestones'] = self._milestones()
        return self.cache['milestones']

    def milestone(self, **kwargs):
        """
        Return the milestone with attributes matching the keyword arguments
        passed in.

        Ex:
            ```
            milestone(id=1, name='my milestone')
            ```
            returns the milestone with matching attributes
        """
        return self._filter(self.milestones(), **kwargs)

    def _tickets(self):
        """
        Returns a list of Ticket instances created from the API
        """
        url = Ticket(space=self).list_url()
        raw_data = self._harvest(url=url)
        return [
            Ticket(
                space=self,
                initialise_with=data[1]
                ) for data in raw_data
            ]

    def tickets(self):
        """
        Return the tickets in the space
        """
        if not self.cache['tickets']:
            self.cache['tickets'] = self._tickets()
        return self.cache['tickets']


    def ticket(self, **kwargs):
        """
        Return the ticket with attributes matching the keyword arguments passed
        in.

        Ex:
            ```
            ticket(id=1, name='my ticket')
            ```
            returns the ticket with matching attributes
        """
        return self._filter(self.tickets(), **kwargs)

    def _users(self):
        """
        Returns a list of User instances created from the API
        """
        url = User(space=self).list_url()
        raw_data = self._harvest(url=url)
        return [
            User(
                space=self,
                initialise_with=data[1]
                ) for data in raw_data
            ]

    def users(self):
        """
        Return the users in the space
        """
        if not self.cache['users']:
            self.cache['users'] = self._users()
        return self.cache['users']


    def user(self, **kwargs):
        """
        Return the user with attributes matching the keyword arguments passed
        in.

        Ex:
            ```
            user(id=1, name='John Smith')
            ```
            returns the user with matching attributes
        """
        return self._filter(self.users(), **kwargs)


class Milestone(AssemblaObject):
    class Meta(APIObject.Meta):
        primary_key = 'id'
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

        Ex:
            ```
            ticket(id=1, name='my ticket')
            ```
            returns the ticket with matching attributes
        """
        return self._filter(self.tickets(), **kwargs)


class User(AssemblaObject):
    class Meta(APIObject.Meta):
        primary_key = 'id'
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

        Ex:
            ```
            ticket(id=1, name='my ticket')
            ```
            returns the ticket with matching attributes
        """
        return self._filter(self.tickets(), **kwargs)


class Ticket(AssemblaObject):
    class Meta(APIObject.Meta):
        primary_key = 'number'
        relative_url = 'spaces/{space}/tickets/{pk}'
        relative_list_url = 'spaces/{space}/tickets'