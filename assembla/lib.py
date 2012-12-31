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