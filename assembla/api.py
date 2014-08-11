import urllib
import requests
import json
from assembla.lib import AssemblaObject, assembla_filter
import settings


class API(object):
    cache_responses = False
    cache = {}

    def __init__(self, key=None, secret=None):
        """
        :key,
        :secret
            Your Assembla API access details, available from
            https://www.assembla.com/user/edit/manage_clients
        """
        if not key or not secret:
            raise Exception(
                'The Assembla API requires your API \'key\' and \'secret\', '
                'accessible from https://www.assembla.com/user/edit/manage_clients'
            )
        self.key = key
        self.secret = secret
        self.session = requests.Session()

    @assembla_filter
    def stream(self, extra_params=None):
        """
        All Events available
        """
        return self._get_json(Event, extra_params=extra_params)

    @assembla_filter
    def spaces(self, extra_params=None):
        """
        All Spaces available
        """
        return self._get_json(Space, extra_params=extra_params)

    def _get_json(self, model, space=None, rel_path=None, extra_params=None, get_all=None):
        """
        Base level method for fetching data from the API
        """
        # Only API.spaces and API.event should not provide
        # the `space argument
        if space is None and model not in (Space, Event):
            raise Exception(
                'In general, `API._get_json` should always '
                'be called with a `space` argument.'
            )

        if not extra_params:
            extra_params = {}

        # Handle pagination for requests carrying large amounts of data
        extra_params['page'] = extra_params.get('page', 1)

        # Generate the url to hit
        url = '{0}/{1}/{2}.json?{3}'.format(
            settings.API_ROOT_PATH,
            settings.API_VERSION,
            rel_path or model.rel_path,
            urllib.urlencode(extra_params),
        )

        # If the cache is being used and the url has been hit already
        if self.cache_responses and url in self.cache:
            response = self.cache[url]
        else:
            # Fetch the data
            headers = {
                'X-Api-Key': self.key,
                'X-Api-Secret': self.secret,
            }
            response = self.session.get(url=url, headers=headers)
            # If the cache is being used, update it
            if self.cache_responses:
                self.cache[url] = response

        if response.status_code == 200:  # OK
            results = []
            json_response = response.json()
            for obj in json_response:
                instance = model(data=obj)
                instance.api = self
                if space:
                    instance.space = space
                results.append(instance)
            # If it looks like there are more pages to fetch,
            # try and fetch the next one
            per_page = extra_params.get('per_page', None)
            if (
                get_all
                and per_page
                and len(json_response)
                and per_page == len(json_response)
            ):
                extra_params['page'] += 1
                results = results + self._get_json(model, space, rel_path, extra_params, get_all=get_all)
            return results
        elif response.status_code == 204:  # No Content
            return []
        else:  # Most likely a 404 Not Found
            raise Exception(
                'Code {0} returned from `{1}`. Response text: "{2}".'.format(
                    response.status_code,
                    url,
                    response.text
                )
            )

    def _post_json(self, instance, space=None, rel_path=None, extra_params=None):
        """
        Base level method for updating data via the API
        """

        model = type(instance)

        # Only API.spaces and API.event should not provide
        # the `space argument
        if space is None and model not in (Space, Event):
            raise Exception(
                'In general, `API._post_json` should always '
                'be called with a `space` argument.'
            )

        if 'number' in instance.data:
            raise AttributeError(
                'You cannot create a ticket which already has a number'
            )

        if not extra_params:
            extra_params = {}

        # Generate the url to hit
        url = '{0}/{1}/{2}?{3}'.format(
            settings.API_ROOT_PATH,
            settings.API_VERSION,
            rel_path or model.rel_path,
            urllib.urlencode(extra_params),
        )

        # Fetch the data
        response = requests.post(
            url=url,
            data=json.dumps(instance.data),
            headers={
                'X-Api-Key': self.key,
                'X-Api-Secret': self.secret,
                'Content-type': "application/json",
            },
        )

        if response.status_code == 201:  # OK
            instance = model(data=response.json())
            instance.api = self
            if space:
                instance.space = space
            return instance
        else:  # Most likely a 404 Not Found
            raise Exception(
                'Code {0} returned from `{1}`. Response text: "{2}".'.format(
                    response.status_code,
                    url,
                    response.text
                )
            )

    def _put_json(self, instance, space=None, rel_path=None, extra_params=None, id_field=None):
        """
        Base level method for adding new data to the API
        """

        model = type(instance)

        # Only API.spaces and API.event should not provide
        # the `space argument
        if space is None and model not in (Space, Event):
            raise Exception(
                'In general, `API._put_json` should always '
                'be called with a `space` argument.'
            )

        if not extra_params:
            extra_params = {}

        if not id_field:
            id_field = 'number'

        # Generate the url to hit
        url = '{0}/{1}/{2}/{3}.json?{4}'.format(
            settings.API_ROOT_PATH,
            settings.API_VERSION,
            rel_path or model.rel_path,
            instance[id_field],
            urllib.urlencode(extra_params),
        )

        # Fetch the data
        response = requests.put(
            url=url,
            data=json.dumps(instance.data),
            headers={
                'X-Api-Key': self.key,
                'X-Api-Secret': self.secret,
                'Content-type': "application/json",
            },
        )

        if response.status_code == 204:  # OK
            return instance
        else:  # Most likely a 404 Not Found
            raise Exception(
                'Code {0} returned from `{1}`. Response text: "{2}".'.format(
                    response.status_code,
                    url,
                    response.text
                )
            )

    def _delete_json(self, instance, space=None, rel_path=None, extra_params=None, id_field=None, append_to_path=None):
        """
        Base level method for removing data from the API
        """

        model = type(instance)

        # Only API.spaces and API.event should not provide
        # the `space argument
        if space is None and model not in (Space, Event):
            raise Exception(
                'In general, `API._delete_json` should always '
                'be called with a `space` argument.'
            )

        if not extra_params:
            extra_params = {}

        if not id_field:
            id_field = 'number'

        if not instance.get(id_field, None):
            raise AttributeError(
                '%s does not have a value for the id field \'%s\'' % (
                    instance.__class__.__name__,
                    id_field
                )
            )

        # Generate the url to hit
        url = '{0}/{1}/{2}/{3}{4}.json?{5}'.format(
            settings.API_ROOT_PATH,
            settings.API_VERSION,
            rel_path or model.rel_path,
            instance[id_field],
            append_to_path or '',
            urllib.urlencode(extra_params),
        )

        # Fetch the data
        response = requests.delete(
            url=url,
            headers={
                'X-Api-Key': self.key,
                'X-Api-Secret': self.secret,
                'Content-type': "application/json",
            },
        )

        if response.status_code == 204:  # OK
            return True
        else:  # Most likely a 404 Not Found
            raise Exception(
                'Code {0} returned from `{1}`. Response text: "{2}".'.format(
                    response.status_code,
                    url,
                    response.text
                )
            )

    def _bind_variables(self, instance, space):
        """
        Bind related variables to the instance
        """
        instance.api = self
        if space:
            instance.space = space
        return instance


class Event(AssemblaObject):
    rel_path = 'activity'


class Space(AssemblaObject):
    rel_path = 'spaces'

    @assembla_filter
    def tickets(self, extra_params=None):
        """
        All Tickets in this Space
        """

        # Default params
        params = {
            'per_page': settings.MAX_PER_PAGE,
            'report': 0,  # Report 0 is all tickets
        }

        if extra_params:
            params.update(extra_params)

        return self.api._get_json(
            Ticket,
            space=self,
            rel_path=self._build_rel_path('tickets'),
            extra_params=params,
            get_all=True,  # Retrieve all tickets in the space
        )

    @assembla_filter
    def milestones(self, extra_params=None):
        """
        All Milestones in this Space
        """
        
        # Default params
        params = {
            'per_page': settings.MAX_PER_PAGE,
        }

        if extra_params:
            params.update(extra_params)
            
        return self.api._get_json(
            Milestone,
            space=self,
            rel_path=self._build_rel_path('milestones/all'),
            extra_params=params,
            get_all=True,  # Retrieve all milestones in the space
        )

    @assembla_filter
    def tools(self, extra_params=None):
        """"
        All Tools in this Space
        """
        return self.api._get_json(
            SpaceTool,
            space=self,
            rel_path=self._build_rel_path('space_tools'),
            extra_params=extra_params,
        )

    @assembla_filter
    def components(self, extra_params=None):
        """"
        All components in this Space
        """
        return self.api._get_json(
            Component,
            space=self,
            rel_path=self._build_rel_path('ticket_components'),
            extra_params=extra_params,
        )

    @assembla_filter
    def users(self, extra_params=None):
        """
        All Users with access to this Space
        """
        return self.api._get_json(
            User,
            space=self,
            rel_path=self._build_rel_path('users'),
            extra_params=extra_params,
            )

    @assembla_filter
    def Tags(self, extra_params=None):
        """"
        All Tags in this Space
        """
        return self.api._get_json(
            Tag,
            space=self,
            rel_path=self._build_rel_path('tags'),
            extra_params=extra_params,
        )

    @assembla_filter
    @assembla_filter
    def wiki_pages(self, extra_params=None):
        """
        All Wiki Pages with access to this Space
        """
        return self.api._get_json(
            WikiPage,
            space=self,
            rel_path=self._build_rel_path('wiki_pages'),
            extra_params=extra_params,
        )

    def _build_rel_path(self, to_append=None):
        """
        Build a relative path to the API endpoint
        """
        return '{0}/{1}/{2}'.format(
            self.rel_path,
            self['id'],
            to_append if to_append else ''
        )


class SpaceTool(AssemblaObject):
    pass


class Component(AssemblaObject):
    pass


class Milestone(AssemblaObject):
    @assembla_filter
    def tickets(self, extra_params=None):
        """
        All Tickets which are a part of this Milestone
        """
        return filter(
            lambda ticket: ticket.get('milestone_id', None) == self['id'],
            self.space.tickets(extra_params=extra_params)
        )


class Ticket(AssemblaObject):

    def tags(self, extra_params=None):
        """
        All Tags in this Ticket
        """

        # Default params
        params = {
            'per_page': settings.MAX_PER_PAGE,
        }

        if extra_params:
            params.update(extra_params)

        return self.api._get_json(
            Tag,
            space=self,
            rel_path=self.space._build_rel_path(
                'tickets/%s/tags' % self['number']
            ),
            extra_params=params,
            get_all=True,  # Retrieve all comments in the ticket
        )


    def milestone(self, extra_params=None):
        """
        The Milestone that the Ticket is a part of
        """
        if self.get('milestone_id', None):
            milestones = self.space.milestones(id=self['milestone_id'], extra_params=extra_params)
            if milestones:
                return milestones[0]

    def user(self, extra_params=None):
        """
        The User currently assigned to the Ticket
        """
        if self.get('assigned_to_id', None):
            users = self.space.users(
                id=self['assigned_to_id'],
                extra_params=extra_params
            )
            if users:
                return users[0]

    def component(self, extra_params=None):
        """
        The Component currently assigned to the Ticket
        """
        if self.get('component_id', None):
            components = self.space.components(id=self['component_id'], extra_params=extra_params)
            if components:
                return components[0]

    @assembla_filter
    def comments(self, extra_params=None):
        """
        All Comments in this Ticket
        """

        # Default params
        params = {
            'per_page': settings.MAX_PER_PAGE,
        }

        if extra_params:
            params.update(extra_params)

        return self.api._get_json(
            TicketComment,
            space=self,
            rel_path=self.space._build_rel_path(
                'tickets/%s/ticket_comments' % self['number']
            ),
            extra_params=params,
            get_all=True,  # Retrieve all comments in the ticket
        )


    def write(self):
        """
        Create or update the Ticket on Assembla
        """
        if not hasattr(self, 'space'):
            raise AttributeError("A ticket must have a 'space' attribute before you can write it to Assembla.")

        if self.get('number'):  # Modifying an existing ticket
            method = self.space.api._put_json
        else:  # Creating a new ticket
            method = self.space.api._post_json

        return method(
            self,
            space=self.space,
            rel_path=self.space._build_rel_path('tickets'),
        )

    def delete(self):
        """
        Remove the Ticket from Assembla
        """
        if not hasattr(self, 'space'):
            raise AttributeError("A ticket must have a 'space' attribute before you can remove it from Assembla.")

        return self.space.api._delete_json(
            self,
            space=self.space,
            rel_path=self.space._build_rel_path('tickets'),
        )


class TicketComment(AssemblaObject):
    pass


class Tag(AssemblaObject):
    pass


class User(AssemblaObject):
    @assembla_filter
    def tickets(self, extra_params=None):
        """
        A User's tickets across all available spaces
        """
        tickets = []
        for space in self.api.spaces():
            tickets += filter(
                lambda ticket: ticket.get('assigned_to_id', None) == self['id'],
                space.tickets(extra_params=extra_params)
            )
        return tickets


class WikiPage(AssemblaObject):
    def write(self):
        """
        Create or update a Wiki Page on Assembla
        """
        if not hasattr(self, 'space'):
            raise AttributeError("A WikiPage must have a 'space' attribute before you can write it to Assembla.")

        self.api = self.space.api

        if self.get('id'):  # We are modifying an existing wiki page
            return self.api._put_json(
                self,
                space=self.space,
                rel_path=self.space._build_rel_path('wiki_pages'),
                id_field='id'
            )
        else:  # Creating a new wiki page
            return self.api._post_json(
                self,
                space=self.space,
                rel_path=self.space._build_rel_path('wiki_pages'),
            )

    def delete(self):
        """
        Remove the WikiPage from Assembla
        """
        if not hasattr(self, 'space'):
            raise AttributeError("A WikiPage must have a 'space' attribute before you can remove it from Assembla.")

        self.api = self.space.api

        return self.api._delete_json(
            self,
            space=self.space,
            rel_path=self.space._build_rel_path('wiki_pages'),
            id_field='id',
            append_to_path='/container'
        )
