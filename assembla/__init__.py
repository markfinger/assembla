import requests

class API(object):

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def stream(self):
        return self._get_json(Event)

    def spaces(self):
        return self._get_json(Space)

    def _get_json(self, model):
        response = requests.get(
            url='https://api.assembla.com/v1/{0}.json'.format(model.rel_path),
            headers={
                'X-Api-Key': self.key,
                'X-Api-Secret': self.secret,
            },
        )
        return [model(data=json, api=self) for json in response.json()]

class AssemblaObject(object):
    """
    Proxies getitem calls (eg: `obj['id']` to a dictionary `_data`.
    """

    def __init__(self, data, api):
        self._data = data
        self.api = api

    def __getitem__(self, key):
        return self._data[key]

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def get(self, *args, **kwargs):
        return self._data.get(*args, **kwargs)


class Event(AssemblaObject):
    rel_path = 'activity'


class Space(AssemblaObject):
    rel_path = 'spaces'

    tickets = None
    milestones = None
    users = None

# TODO
class Ticket(AssemblaObject):
    pass
class Milestone(AssemblaObject):
    pass
class User(AssemblaObject):
    pass