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
        assert API(auth=('_','_',))

    def test_child_functions_exist(self):
        assert self.API.space
        assert self.API.spaces

    def test_api_init_accepts_auth_credentials(self):
        assert self.API.auth == auth

    def test_credential_check_expect_success(self):
        assert self.API.check_credentials() is True

    def test_credential_check_expect_fail(self):
        try:
            API(auth=('_','_',)).check_credentials()
            raise Exception('Should have thrown an AssemblaError.')
        except AssemblaError as e:
            assert e.code==110