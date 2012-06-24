from .cache import Cache
from .base_models import APIObject

class AssemblaObject(APIObject):
    """
    An object harvested from the Assembla API
    """
    pass

class CachesRequests(object):
    """
    Adds a caching system to the object, any requests routed through
    _get_from_cache will check for a match, before requesting the object
    from Assembla
    """
    def __init__(self, cache_responses=True):
        super(CachesRequests, self).__init__()
        self.cache_responses=cache_responses,
        self.cache = Cache(
            parent=self,
            schema=self.Meta.cache_schema,
            cache_responses=cache_responses,
        )

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

class InitialiseWith(object):
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
    """
    def __init__(self, initialise_with=None, *args, **kwargs):
        super(InitialiseWith, self).__init__()
        initialise_with = initialise_with or {}
        for attr_name, value in initialise_with.iteritems():
            setattr(self, attr_name, value)
        for attr_name, value in kwargs.iteritems():
            setattr(self, attr_name, value)
