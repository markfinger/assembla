from .test import AssemblaTest
from ..models import User

class TestsForUser(AssemblaTest):

    def setup(self):
        super(TestsForUser, self).setup()
        self.user = User()

    def test_attributes_exist(self):
        # Base class
        assert self.user.Meta.relative_url
        assert self.user.Meta.primary_key
        assert self.user.Meta.base_url
        assert self.user.Meta.base_api_url
        # HasObject class
        assert self.user.Meta.has_objects
        assert hasattr(self.user, '_tickets')
        # Unique attributes

    def test_child_functions_exist(self):
        assert self.user.ticket
        assert self.user.tickets

    def test_urls(self):
        user = User()
        setattr(user, user.Meta.primary_key, 'test_pk')
        assert user.url == 'https://www.assembla.com/profiles/test_pk'
        assert user.api_url == 'https://www.assembla.com/user/best_profile/test_pk'