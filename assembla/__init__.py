import urllib
import requests
from .lib import AssemblaObject, assembla_filter


class API(object):
    cache_responses = False
    cache = {}

    def __init__(self, key=None, secret=None):
        """
        :key,
        :secret
            Your Assembla API access details, available from
            https://www.assembla.com/user/edit/manage_clients
        :cache_responses
            If a truthy value is provided, a caching system is activated which
            reduces the overhead on repeated requests
        """
        if not key or not secret:
            raise Exception(
                'The Assembla API requires your API \'key\' and \'secret\', '
                'accessible from https://www.assembla.com/user/edit/manage_clients'
            )
        self.key = key
        self.secret = secret

    @assembla_filter
    def stream(self):
        """
        All Events available
        """
        return self._get_json(Event)

    @assembla_filter
    def spaces(self):
        """
        All Spaces available
        """
        return self._get_json(Space)

    def _get_json(self, model, rel_path=None, extra_params=None):

        # Pagination for requests carrying large amounts of data
        if not extra_params:
            extra_params = {}
        extra_params['page'] = extra_params.get('page', 1)

        # Generate the url to hit
        url = 'https://api.assembla.com/{0}/{1}.json?{2}'.format(
            'v1', # API version
            rel_path or model.rel_path,
            urllib.urlencode(extra_params),
        )

        # If the cache is being used and the url has been hit already
        if self.cache_responses and url in self.cache:
            response = self.cache[url]
        else:
            # Fetch the data
            response = requests.get(
                url=url,
                headers={
                    'X-Api-Key': self.key,
                    'X-Api-Secret': self.secret,
                },
            )
            # If the cache is being used, update it
            if self.cache_responses:
                self.cache[url] = response

        if response.status_code == 200: # OK
            results = [
                self._bind_variables(
                    model(data=json, api=self)
                ) for json in response.json()
            ]
            # If the number of results is divisible by the maximum limit per
            # page, then we need to fetch the next page
            per_page = extra_params.get('per_page', None)
            if (
                per_page
                and len(results)
                and per_page % len(results) == 0
            ):
                extra_params['page'] = extra_params['page'] + 1
                results = results + self._get_json(model, rel_path, extra_params)
            return results
        elif response.status_code == 204: # No Content
            return []
        else: # Most likely a 404 Not Found
            raise Exception(
                'Code {0} returned from `{1}`.'.format(
                    response.status_code,
                    url,
                )
            )

    def _bind_variables(self, instance):
        """
        Bind related variables to the instance
        """
        instance.api = self
        if instance.get('space_id', None):
            instance.space = filter(
                lambda space: space['id'] == instance['space_id'],
                self.spaces()
            )[0]
        return instance


class Event(AssemblaObject):
    rel_path = 'activity'


class Space(AssemblaObject):
    rel_path = 'spaces'

    @assembla_filter
    def tickets(self):
        """
        All Tickets in this Space
        """
        return self.api._get_json(
            Ticket,
            rel_path=self._build_rel_path('tickets'),
            extra_params={
                'per_page': 1000,
                'report': 0 # All tickets
            }
        )

    @assembla_filter
    def milestones(self):
        """
        All Milestones in this Space
        """
        return self.api._get_json(
            Milestone,
            rel_path=self._build_rel_path('milestones/all'),
        )

    @assembla_filter
    def users(self):
        """
        All Users with access to this Space
        """
        return self.api._get_json(
            User,
            rel_path=self._build_rel_path('users'),
        )

    def _build_rel_path(self, to_append=None):
        return '{0}/{1}/{2}'.format(
            self.rel_path,
            self['id'],
            to_append if to_append else ''
        )


class Milestone(AssemblaObject):
    @assembla_filter
    def tickets(self):
        """
        All Tickets which are a part of this Milestone
        """
        return filter(
            lambda ticket: ticket.get('milestone_id', None) == self['id'],
            self.space.tickets()
        )


class Ticket(AssemblaObject):
    @property
    def milestone(self):
        """
        The Milestone that the Ticket is a part of
        """
        if self.get('milestone_id', None):
            return filter(
                lambda milestone: milestone['id'] == self['milestone_id'],
                self.space.milestones()
            )[0]

    @property
    def user(self):
        """
        The User currently assigned to the Ticket
        """
        if self.get('assigned_to_id', None):
            return filter(
                lambda user: user['id'] == self['assigned_to_id'],
                self.space.users()
            )[0]


class User(AssemblaObject):
    @assembla_filter
    def tickets(self):
        """
        A User's tickets across all available spaces
        """
        tickets = []
        for space in self.api.spaces():
            tickets += filter(
                lambda ticket: ticket.get('assigned_to_id', None) == self['id'],
                space.tickets(),
            )
        return tickets