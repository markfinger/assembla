from functools import partial
from error import AssemblaError

__data__ = {}

class AssemblaObject(object):
    """
    Base object
    """
    pass

class APIObject(AssemblaObject):
    """
    Base object for representations of objects on Assembla.
    """

    class Meta:
        # A string denoting the key identifier for the model
        primary_key = None
        # Python formattable string, which denotes a relative path to
        # the model's HTML page on Assembla
        relative_url = None
        # Python formattable string, which denotes a relative path to
        # the model on Assembla's API. This is an optional field, only necessary if
        # the API requires a different access path than the HTML front-end
        relative_api_url = None
        # A URL which is prepended to all relative URLs to generate absolute
        # URLs to HTML pages
        base_url = 'https://www.assembla.com/'
        # A URL which is prepended to all relative URLs to generate absolute
        # URLs to API links
        base_api_url = base_url

    def __str__(self):
        return str(self.pk())

    def __unicode__(self):
        return unicode(self.pk())

    def pk(self):
        """
        Returns the value of the attribute denoted by self.primary_key
        """
        return getattr(self, self.Meta.primary_key)

    def _url(self, base_url=None, relative_url=None):
        """
        Generates an absolute url to a resource. Does the heavy lifting for .url
        and .api_url.

        Takes optional arguments :base_url and :relative_url which denote
            overrides for Meta.base_url and Meta.relative_url
        """
        return ''.join([
            base_url or self.Meta.base_url,
            relative_url or self.Meta.relative_url,
        ]).format(**{
            'space': self._get_pk_of_attr('space'),
            'milestone': self._get_pk_of_attr('milestone'),
            'user': self._get_pk_of_attr('user'),
            'ticket': self._get_pk_of_attr('ticket'),
            'pk': self.pk(),
        })

    @property
    def url(self):
        """
        Returns a string representing the absolute url to the model's
        corresponding HTML page on Assembla
        """
        return self._url()

    @property
    def api_url(self):
        """
        Returns a string representing the absolute url to the model on
        Assembla's API
        """
        return self._url(
            # If the URL for the API is defined, use it
            relative_url=self.Meta.relative_api_url or None
        )


    def _get_pk_of_attr(self, attr, default=None):
        """
        Safely attempts to return the primary key of the attribute denoted
        by :attr.

        Takes an optional argument :default, which acts in a similar manner
        to getattr's.

        Example: self._get_pk('space') attempts to return the primary key of the
        space attribute; equivalent to self.space.pk.
        """
        return getattr(
            # Get the attribute specified by :attr
            getattr(self, attr, default),
            # Get the primary key function
            'pk',
            # In case we are getting back None, wrap it up in a lambda so we
            # can safely call the result
            lambda: default
        )() # Need to execute either .pk or the lambda

class HasObjects(object):
    """
    Base object

    subclass.has = ('tickets',)

    generates
        subclass._tickets: a List to store tickets in
        subclass.tickets: a method to return tickets, or harvest and return
            them if they haven't been retrieved yet
        subclass.ticket: a method taking :pk which searches through self.tickets
            for the matching object

    """
    def __init__(self):
        for object_type in self.Meta.has_objects:
            # Add a list to the model, this will store the
            # object type.
            # Ex: if self.Meta.has_objects == ('tickets'),
            #   then self gets an attribute `_tickets` which is a list
            object_list_name = '_{0}s'.format(object_type)
            object_list = []
            setattr(self, object_list_name, object_list)

            # Adds a function which proxies to __get_objects
            name_of_proxy_to_get_objects = '{0}s'.format(object_type)
            proxy_to_get_objects = partial(
                self.__get_objects,
                object_list_name=object_list_name
            )
            setattr(
                self,
                name_of_proxy_to_get_objects,
                proxy_to_get_objects
            )

            # Adds a function which proxies to __get_object_by_pk
            name_of_proxy_to_get_object_by_pk = '{0}'.format(object_type)
            proxy_to_get_object_by_pk = partial(
                self.__get_object_by_pk, 
                name_of_proxy_to_get_objects=name_of_proxy_to_get_objects
            )
            setattr(
                self, 
                name_of_proxy_to_get_object_by_pk,
                proxy_to_get_object_by_pk
            )
            setattr(
                self,
                '__data__',
                __data__
            )

    def __add_object(self, objects_func_name, pk):
        """
        Might need this to bubble up to the space's store.

        maybe use a __data attr for the API which contains pks pointing to data
        eg:
        API.__spaces = {
            '<space_pk_1>':
                'milestones': {
                    '<pk_1>': <milestone_1>,
                    '<pk_2>': <milestone_2>,
                    ...
                    '<pk_x>': <milestone_x>,
                },
                'tickets' : {
                    ...
                },
                ...
        }
        """
        pass

    def __get_object_by_pk(self, objects_func_name, pk):
        """
        gets __get_objects and filters for the pk
        """
        results = filter(
            lambda object: object.pk()==pk,
            getattr(self, objects_func_name)(), # Call the proxy to __get_objects
        )
        if not results: # Not found
            raise AssemblaError(200, object=objects_func_name, pk=pk)
        elif len(results) > 1: # Too many results
            raise AssemblaError(210, object=objects_func_name, pk=pk)
        else: # Found a singleton with corresponding pk
            return results[0]

    def __get_objects(self, object_list_name):
        """
        retrieves the list of objects

        if the objects have not been harvested yet, get them through the API and
        return,
        otherwise return them immediately
        """
        return getattr(self, object_list_name)

