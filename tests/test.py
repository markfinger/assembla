from .. import API
from . import auth


class AssemblaTest(object):

    def setup(self):
        self.API = API(auth)

    def teardown(self):
        pass