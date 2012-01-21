from functools import partial
from error import AssemblaError

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
        # the model's HTML page on Assembla.
        relative_url = None
        # Python formattable string, which denotes a relative path to
        # the model on Assembla's API. This is an optional field, only necessary if
        # the API requires a different access path than the HTML front-end.
        relative_api_url = None
        # A URL which is prepended to all relative URLs to generate absolute
        # URLs to HTML pages.
        base_url = 'https://www.assembla.com/'
        # A URL which is prepended to all relative URLs to generate absolute
        # URLs to API links.
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
            # If the URL for the API is defined, use it.
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
            # can safely call .pk()
            lambda: default or None
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

#    could probably do some automated stuff to avoid all
#    the boilerplate below

    # has_harvested_<name> = False
    def __init__(self):
        for object_type in self.Meta.has_objects:
            # Add a list to the model, this will store the
            # object type.
            # Ex: if self.Meta.has_objects == ('tickets'),
            #   then self gets an attribute `_tickets` which is a list
            object_list_name = '_{0}s'.format(object_type)
            object_list = []
            setattr(self, object_list_name, object_list)
            # Adds a function which proxies to __objects.
            objects_func_name = '{0}s'.format(object_type)
            objects_func = partial(self.__objects, object_list_name=object_list_name)
            setattr(self, objects_func_name, objects_func)
            # Adds a function which proxies to __object.
            object_func_name = '{0}'.format(object_type)
            object_func = partial(self.__object, objects_func_name=objects_func_name)
            setattr(self, object_func_name, object_func)

    def __object(self, objects_func_name, pk):
        results = filter(
            lambda object: object.pk()==pk,
            getattr(self, objects_func_name)(), # Call __objects
        )
        if not results:
            raise AssemblaError(200, pk) # Not found
        elif len(results) > 1:
            raise AssemblaError(210, pk) # Too many results
        else:
            return results[0]

    def __objects(self, object_list_name):
        return getattr(self, object_list_name)

#class HasSpaces(HasObjects):
#
#    def __init__(self):
#        self._spaces = []
#
#    def space(self, name):
#        return reduce(
#            lambda space: space.name==name,
#            self._spaces
#        )
#
#    def spaces(self):
#        return self._spaces
#


