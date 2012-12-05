from StringIO import StringIO
from datetime import date, datetime

import requests
from lxml import etree

from error import AssemblaError


class APIObject(object):
    """
    Base object for representations of resources pulled from Assembla.
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
        # paths to resources on the API
        base_url = 'https://www.assembla.com/'

    def __str__(self):
        return str(unicode(self))

    def __unicode__(self):
        return u'{0}: {1}'.format(
            self.__class__.__name__,
            getattr(self, self.Meta.secondary_key, None) or self._pk()
        )

    def _pk(self):
        """
        Returns the value of the attribute denoted by self.primary_key
        """
        return getattr(self, self.Meta.primary_key)

    def _safe_pk(self):
        """
        Safer variant of self._pk(). Care should be used, as it suppresses
        errors.
        """
        try:
            return self._pk()
        except AttributeError:
            pass

    def _url(self, base_url=None, relative_url=None):
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

    def _list_url(self):
        """
        Generates an absolute url to a list of the model's type on the API.
        """
        return self._url(relative_url=self.Meta.relative_list_url)

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
            equivalent to self.space._pk.
        """
        return getattr(
            # Get the attribute specified by :attr
            getattr(self, attr, default),
            # Get the primary key function
            '_pk',
            # In case we are getting back None, wrap it up in a lambda so we
            # can safely call the result
            lambda: default
        )() # Need to execute either ._pk or the lambda

    def _get_xml_tree(self, url, auth):
        """
        Returns the XML representation of :_url as an lxml etree.
        """
        response = requests.session(
            auth=auth,
            headers={'Accept': 'application/xml'}
        ).get(url)

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
        if value is None or \
          (element.attrib.has_key('nil') and element.attrib['nil'] == 'true'):
            return None
        elif element.attrib.has_key('type'):
            type_attr = element.attrib['type'].lower()
            if type_attr == 'datetime':
                value = value[:-6] # Ignoring timezone
                return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
            elif type_attr == 'date':
                value = value.split('-')
                return date(
                    year=int(value[0]),
                    month=int(value[1]),
                    day=int(value[2])
                )
            elif type_attr == 'boolean':
                return {
                    'true': True,
                    'false': False,
                }[value]
            elif type_attr == 'integer':
                return int(value)
            elif type_attr == 'float':
                return float(value)
            elif type_attr == 'list' and 'custom' in element.tag:
                return element.attrib['name'], value
        else:
            return value

    def __clean_attr_name(self, name):
        """
        Replace any dashes in :name with underscores
        """
        return name.replace('-', '_')

    def _harvest(self, url, auth):
        """
        Retrieves an XML response from :url and returns it as a list
        of dictionaries
        """
        tree = self._get_xml_tree(url, auth)
        return map(self._recursive_dict, tree.getroot().getchildren())

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
        cost of the transparency when a user enters a typo for an argument name
        """
        return filter(
            # Find the objects who have an equal number of matching attr/value
            # combinations as `len(kwargs)`
            lambda object: len(kwargs) == len(
                filter(
                    lambda boolean: boolean,
                    [getattr(object, attr_name) == value
                        for attr_name, value in kwargs.iteritems()]
                )
            ),
            data
        )