from .base_models import AssemblaObject, AssemblaError

class API(AssemblaObject):

    def __init__(self, auth=None):
        super(API, self).__init__()
        if auth:
            self.auth = auth

    def set_credentials(self, auth):
        if auth:
            self.auth = auth
        else:
            raise AssemblaError(100)

    def check_credentials(self):
        if 1:
            raise AssemblaError(110)
        else:
            return True

