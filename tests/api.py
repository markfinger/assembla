from .. import API
from ..error import AssemblaError
from .auth import auth
from .test import AssemblaTest

class TestsForAPI(AssemblaTest):

    def setup(self):
        super(TestsForAPI, self).setup()
        # Ensure we're using a clean API
        self.API = API(auth)

    def test_api_can_be_initialised(self):
        assert API()

    def test_attributes_exist(self):
        # HasObject class
        assert self.API.Meta.has_objects
        assert hasattr(self.API, '_spaces')
        # Unique attributes

    def test_child_functions_exist(self):
        assert self.API.space
        assert self.API.spaces

    def test_api_init_accepts_auth_credentials(self):
        assert self.API.auth['username'] == auth['username']
        assert self.API.auth['password'] == auth['password']

    def test_api_set_credentials_sets_credentials(self):
        self.API = API()
        self.API.set_credentials(auth)
        assert self.API.auth['username'] == auth['username']
        assert self.API.auth['password'] == auth['password']

    def test_credential_check_expect_success(self):
        assert self.API.check_credentials() is True

    def test_credential_check_expect_fail(self):
        try:
            API({
                'username':None,
                'password':None
            }).check_credentials()
            raise Exception('Should have thrown an AssemblaError.')
        except AssemblaError as e:
            assert e.code==110