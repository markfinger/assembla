from copy import deepcopy
from StringIO import StringIO
from datetime import date, datetime
from collections import MutableMapping

import requests
from lxml import etree

from error import AssemblaError


class APIObject(object):
    """
    Base object for representations of objects on Assembla.
    """

    class Meta:
        """
        Descriptive fields for models
        """
        # A string denoting the key identifier for the model
        primary_key = None
        # An optional string denoting the human readable identifier for the
        # model. Only required if the attribute is not the same as the
        # `primary_key` attribute
        secondary_key = None
        # Python formattable string, which denotes a relative path to
        # the model on Assembla's API.
        relative_url = None
        # Python formattable string, which denotes a relative path to
        # a list of objects on Assembla's API.
        relative_list_url = None
        # A URL which is prepended to all relative URLs to generate absolute
        # URLs to HTML pages
        base_url = 'https://www.assembla.com/'

    def __str__(self):
        return '{0}: {1}'.format(
            self.__class__.__name__,
            getattr(self, self.Meta.secondary_key, None) or self.pk()
            )

    def pk(self):
        """
        Returns the value of the attribute denoted by self.primary_key
        """
        return getattr(self, self.Meta.primary_key)

    def _safe_pk(self):
        """
        Safer variant of self.pk(). Care should be used, as it suppresses
        errors.
        """
        try:
            return self.pk()
        except AttributeError:
            pass

    def url(self, base_url=None, relative_url=None):
        """
        Generates an absolute url to a model's instance in the API.
        """
        return ''.join([
            base_url or self.Meta.base_url,
            relative_url or self.Meta.relative_url,
            ]).format(**{
                'space': self._get_pk_of_attr('space'),
                'milestone': self._get_pk_of_attr('milestone'),
                'user': self._get_pk_of_attr('user'),
                'ticket': self._get_pk_of_attr('ticket'),
                'pk': self._safe_pk(),
                })

    def list_url(self):
        """
        Generates an absolute url to a list of the model's type on the API.
        """
        return self.url(relative_url=self.Meta.relative_list_url)

    def _get_pk_of_attr(self, attr, default=None):
        """
        Attempts to safely return the primary key of the attribute denoted
        by :attr.

        Takes an optional argument :default, which acts in a similar manner
        to getattr's.

        Ex:
            ```
            self._get_pk('space')
            ```
            attempts to return the primary key of the space attribute;
            equivalent to self.space.pk.
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

    def _get_xml_tree(self, url, auth):
        """
        Returns the XML representation of :url as an lxml etree.
        """
        headers = {'Accept': 'application/xml'}
        session = requests.session(auth=auth, headers=headers)
        response = session.get(url)
        if response.status_code == 401: # Failed to authenticate
            raise AssemblaError(110)
        elif response.status_code != 200: # Unexpected response
            raise AssemblaError(130, status_code=response.status_code, url=url)
        else: # Parse the xml and return as an etree
            return etree.parse(StringIO(str(response.content)))

    def _recursive_dict(self, element):
        """
        Recursively generate a dictionary from the :element and any children.
        Where possible, returns values as native Python types or strings.
        """
        # Derived from http://lxml.de/FAQ.html#how-can-i-map-an-xml-tree-into-a-dict-of-dicts
        return (
            self.__clean_attr_name(element.tag),
            dict(map(self._recursive_dict, element)) or self.__clean_data(element),
            )

    def __clean_data(self, element):
        """
        Try to convert :element.text into a native Python type
        """
        value = element.text
        if value is None or (element.attrib.has_key('nil') and element.attrib['nil'] == 'true'):
            return None
        elif element.attrib.has_key('type'):
            type = element.attrib['type']
            if type == 'datetime':
                value = value[:-6] # Ignoring timezone
                return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
            elif type == 'date':
                value = value.split('-')
                return date(
                    year=int(value[0]),
                    month=int(value[1]),
                    day=int(value[2])
                    )
            elif type == 'boolean':
                return {
                    'true': True,
                    'false': False,
                    }[value]
            elif type == 'integer':
                return int(value)
        else:
            return value

    def __clean_attr_name(self, name):
        """
        Replace any dashes in :name with underscores
        """
        return name.replace('-', '_')

    def _harvest(self, url, auth):
        """
        Returns :url as a dict
        """
        tree = self._get_xml_tree(url, auth)
        return [
            self._recursive_dict(element)
                for element in tree.getroot().getchildren()
            ]

    def _get(self, data, **kwargs):
        """
        Retrieve a single object from :data, where the objects in it which
        possess attributes equal in name/value to a key/value in kwargs.

        Primary difference from _filter is that it will raise Exceptions if
        multiple objects are found
        """
        if not kwargs:
            raise AssemblaError(220)
        results = self._filter(data, **kwargs)
        if len(results) == 1:
            return results[0]
        elif len(results) > 1:
            raise AssemblaError(210, arguments=kwargs)

    def _filter(self, data, **kwargs):
        """
        Filters :data for the objects in it which possess attributes equal in
        name/value to a key/value in kwargs.

        Each key/value combination in kwargs is compared against the object, so
        multiple keyword arguments can be passed in to constrain the filtering.

        Ex:
            ```
            self._filter(
                [my_object, my_other_object],
                some_attribute=1
                some_other_attribute=True
                )
            ```
            which returns all objects in the first argument (an iterable) which
            have attributes 'some_attribute' and 'some_other_attribute' equal
            to `1` and `True` respectively.

        _filter will throw an AttributeError if any of the kwargs are not
        possessed by the objects in the iterable. While it might seem to be
        easier to wrap the comparisons in a try/except, it would come at the
        cost of reducing the transparency behind _filter's behaviour
        """
        return filter(
            lambda object: len(kwargs) == len(
                filter(
                    lambda element: element == True,
                    [getattr(object, attr_name) == value
                        for attr_name, value in kwargs.iteritems()]
                    )
                ),
            data
            )


class AssemblaObject(APIObject):
    """
    Adds a constructor which assigns attributes to the subclass based on
    corresponding keys and values from :initialise_with. Additionally, any key
    word arguments passed into the constructor will be assigned to the subclass.

    Ex: ```
        class SomeClass(AssemblaObject):
            pass

        some_class = SomeClass(
            initialise_with={'some_attribute': True},
            some_other_attribute=False,
            )
        ````
        creates an instance of SomeClass with the attributes
        'some_attribute' == True and 'some_other_attribute' == False.

    Note that the values of keyword arguments passed in can overwrite
    the values of similarly named keys from :initialise_with

    If the subclass has had a cache schema defined in Meta, the constructor will
    instantiate a Cache object for it.
    """
    def __init__(self, initialise_with=None, use_cache=True, **kwargs):
        # :initialise_with's assignments are kept before the :kwargs assignments
        # as :kwargs' values take precedence
        if not initialise_with: initialise_with = {}
        for attr_name, value in initialise_with.iteritems():
            setattr(self, attr_name, value)
        for attr_name, value in kwargs.iteritems():
            setattr(self, attr_name, value)
        if hasattr(self.Meta, 'cache_schema'):
            # Responses will be cached.
            # Call ```space.cache.purge()``` to purge all data from the cache
            self.cache = Cache(
                parent=self,
                schema=self.Meta.cache_schema,
                use_cache=use_cache,
            )
            if not use_cache:
                self.cache.deactivate()


class Cache(MutableMapping):
    """
    In-memory Cache storage. Reduces overheads on repeated requests, at the cost
    that some responses may have outdated data.

    Generally the cache will try to return copies of objects, rather than the
    objects themselves. This is to maintain a semi-immutable cache resembling
    the API as closely as possible.

    Call ```Cache.purge()``` to purge any data, any subsequent
    requests will return fresh data from Assembla.
    """

    def __init__(self, parent, schema, use_cache=True):
        self.store = dict()
        self.schema = schema
        # Initiate the cache, using :schema
        self.clear()
        self.cache_responses = use_cache
        self.parent = parent

    def __setitem__(self, key, value):
        self.store[key] = value
    set = __setitem__

    def __getitem__(self, item):
        """
        Return a copy of an item, rather than the actual item.

        The cache stores lists of objects, rather than returning the object
        directly, this traverses the stored list and returns deep copies of each
        object.
        """
        return map(deepcopy, self.store[item])

    def __delitem__(self, key):
        del self.store.pop[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def has_cached(self, item):
        return True if self.store.has_key(item) and self.store[item] is not None else False

    def activate(self):
        self.cache_responses = True

    def deactivate(self):
        self.cache_responses = False

    def purge(self):
        """
        Purges the cache of any data it may have by reinstantiating itself from
        the schema
        """
        self.store.clear()
        map(lambda name: self.__setitem__(name, []), self.schema)