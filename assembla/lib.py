from functools import wraps


class AssemblaObject(object):
    """
    Proxies getitem calls (eg: `instance['id']`) to a dictionary `instance.data['id']`.
    """
    def __init__(self, data={}):
        self.data = data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def get(self, *args, **kwargs):
        return self.data.get(*args, **kwargs)

    def __repr__(self):
        if 'name' in self.data:
            return "<%s: %s>" % (type(self).__name__, self.data['name'])

        if ('number' in self.data) and ('summary' in self.data):
            return "<%s: #%s - %s>" % (type(self).__name__, self.data['number'], self.data['summary'])

        return super(AssemblaObject, self).__repr__()


def assembla_filter(func):
    """
    Filters :data for the objects in it which possess attributes equal in
    name/value to a key/value in kwargs.

    Each key/value combination in kwargs is compared against the object, so
    multiple keyword arguments can be passed in to constrain the filtering.
    """
    @wraps(func)
    def wrapper(class_instance, **kwargs):

        # Get the result
        extra_params = kwargs.get('extra_params', None)
        if extra_params:
            del kwargs['extra_params']
        results = func(class_instance, extra_params)

        # Filter the result
        if kwargs:
            results = filter(
                # Find the objects who have an equal number of matching attr/value
                # combinations as `len(kwargs)`
                lambda obj: len(kwargs) == len(
                    filter(
                        lambda boolean: boolean,
                        [obj.get(attr_name) == value
                            for attr_name, value in kwargs.iteritems()]
                    )
                ),
                results
            )

        return results
    return wrapper