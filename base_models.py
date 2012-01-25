from functools import partial
from StringIO import StringIO

import requests
from lxml import etree

from error import AssemblaError

class APIObject(object):
    """
    Base object for representations of objects on Assembla.
    """

    class Meta:
        # A string denoting the key identifier for the model
        primary_key = None
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
        return str(self.pk())

    def __unicode__(self):
        return unicode(self.pk())

    def pk(self):
        """
        Returns the value of the attribute denoted by self.primary_key
        """
        return getattr(self, self.Meta.primary_key)

    def url(self, base_url=None, relative_url=None, *args, **kwargs):
        """
        Generates an absolute url to a resource.
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

    def list_url(self, *args, **kwargs):
        return self.url(relative_url=self.Meta.relative_list_url, *args, **kwargs)

    def _get_pk_of_attr(self, attr, default=None):
        """
        Attempts to safely return the primary key of the attribute denoted
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

    def __parseIO(self, string):
        return StringIO(str(string))

    def _get_xml_tree(self, url, auth):
        """
        Returns the XML representation of :url as an lxml etree.
        """
        if not auth:
            raise AssemblaError(100)
        headers = {'Accept': 'application/xml'}
        session = requests.session(auth=auth, headers=headers)
        response = session.get(url)
        if response.status_code == 401: # Failed to authenticate
            raise AssemblaError(110)
        elif response.status_code != 200: # Unexpected response
            raise AssemblaError(130, status_code=response.status_code, url=url)
        else: # Parse the xml and return as an etree
            return etree.parse(StringIO(str(response.content)))

    def harvest(self, url, auth=None):
        """
        Returns :url as a dict
        """
        auth = auth or self.auth
        xml = self._get_xml_tree(url, auth)
        return xml