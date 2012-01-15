from .. import API, AssemblaError
from .auth import auth

class Tests_General:
    # General usage tests.

    def test_api_can_be_initialised(self):
        assert API()

    def test_api_init_accepts_auth_credentials(self):
        assembla = API(auth)
        assert assembla.auth['username'] == auth['username']
        assert assembla.auth['password'] == auth['password']

    def test_api_set_credentials_sets_credentials(self):
        assembla = API()
        assembla.set_credentials(auth)
        assert assembla.auth['username'] == auth['username']
        assert assembla.auth['password'] == auth['password']

    def test_child_functions_exist(self):
        assert API(auth).space
        assert API(auth).spaces
        assert API(auth).milestone
        assert API(auth).milestones
        assert API(auth).user
        assert API(auth).users
        assert API(auth).ticket
        assert API(auth).tickets

    def test_credential_check_expect_success(self):
        assert API(auth).check_credentials() is True

    def test_credential_check_expect_fail(self):
        try:
            API({
                'username':None,
                'password':None
            }).check_credentials()
            raise Exception('Should have thrown an AssemblaError.')
        except AssemblaError as e:
            assert e.code==110