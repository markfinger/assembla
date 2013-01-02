from functools import wraps

class AssemblaObject(object):
    """
    Proxies getitem calls (eg: `instance['id']`) to a dictionary `instance._data['id']`.
    """

    def __init__(self, data, api):
        self.data = data
        self.api = api

    def __getitem__(self, key):
        return self.data[key]

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def get(self, *args, **kwargs):
        return self.data.get(*args, **kwargs)

def assembla_filter(func):
    """
    Filters :data for the objects in it which possess attributes equal in
    name/value to a key/value in kwargs.

    Each key/value combination in kwargs is compared against the object, so
    multiple keyword arguments can be passed in to constrain the filtering.
    """
    @wraps(func)
    def wrapper(class_instance, **kwargs):
        results = func(class_instance)
        if not kwargs:
            return results
        else:
            return filter(
                # Find the objects who have an equal number of matching attr/value
                # combinations as `len(kwargs)`
                lambda object: len(kwargs) == len(
                    filter(
                        lambda boolean: boolean,
                        [object.get(attr_name) == value
                            for attr_name, value in kwargs.iteritems()]
                    )
                ),
                results
            )
    return wrapper