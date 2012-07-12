from copy import deepcopy
from collections import MutableMapping


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

    def __init__(self, parent, schema, cache_responses=True):
        self.store = dict()
        self.schema = schema
        # Initiate the cache, using :schema
        self.clear()
        self.cache_responses = cache_responses
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
        return self.store.has_key(item) and self.store[item]

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
        for name in self.schema:
            self.__setitem__(name, [])
