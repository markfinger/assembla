from .. import API
from datetime import datetime
from .auth import auth
from ..models import Space
from ..error import AssemblaError

class TestsForAPI(object):

    API = API(auth)
    spaces = API.spaces()

    def test_api_can_be_initialised(self):
        assert API(auth=('_','_',))

    def test_child_functions_exist(self):
        assert self.API.spaces
        assert self.API.space

    def test_api_init_accepts_auth_credentials(self):
        assert self.API.auth == auth

    def test_api_init_complains_if_no_auth_arg(self):
        try:
            API()
        except AssemblaError as e:
            assert e.code==100

    def test_credential_check_expect_success(self):
        assert self.API.check_credentials() is True

    def test_credential_check_expect_fail(self):
        try:
            API(auth=('_','_',)).check_credentials()
            raise Exception('Should have thrown an AssemblaError.')
        except AssemblaError as e:
            assert e.code==110
        # Reassigning .spaces to a nothing function as a hack to ensure
        # the exception is working.
        try:
            api = API(auth=('_','_',))
            api.spaces = lambda: []
            api.check_credentials()
            raise Exception('Should have thrown an AssemblaError.')
        except AssemblaError as e:
            assert e.code==110

    def __test_space_type(self, obj):
        assert type(obj) is Space
        # Required attributes
        assert obj.name is not None
        assert obj.wiki_name is not None
        # Despite this being a required field, it doesn't seem to be sent
        # back from the API. Leaving it in here in case it's just temporary
        # bug.
        # assert obj.wiki_format is not None
        assert obj.team_permissions is not None
        assert obj.public_permissions is not None
        # Check that fields have been converted to Python types
        assert type(obj.team_permissions) is int
        assert type(obj.can_join) is bool
        assert type(obj.created_at) is datetime
        assert type(obj.updated_at) is datetime
        assert type(obj.is_volunteer) is bool
        assert type(obj.is_commercial) is bool
        assert type(obj.is_manager) is bool
        return True

    def test_spaces_returns_mulitple_objects_of_type_space(self):
        for space in self.spaces:
            assert self.__test_space_type(space)
        assert len(self.spaces) > 0

    def test_space_returns_type_space(self):
        space = self.API.space(
            id=self.spaces[0].id,
            wiki_name=self.spaces[0].wiki_name,
        )
        assert space.id == self.spaces[0].id
        assert space.wiki_name == self.spaces[0].wiki_name
        assert self.__test_space_type(space)

    def test_bad_url_for_get_xml_tree(self):
        try:
            self.API._get_xml_tree(
                # Hopefully this fails :)
                url='http://www.csdhjbc****jsdbajcbsdjb.com/cdjsbjhcsbdjhcsj/cdhsjbcjsdhcjhscdhb/csdjhbcsdjbchsdjbbjcds',
                auth=('^__^', '^__^',)
                )
        except AssemblaError as e:
            assert e.code==130

