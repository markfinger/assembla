from assembla import API
from assembla.tests.auth import auth
from unittest import TestCase


def test_instantiating_assembla_api():
    API(key='', secret='')

def test_assembla_auth_details():
    assert(
        len(auth) == 2
    )

class TestAssembla(TestCase):

    assembla = API(
        key=auth[0],
        secret=auth[1]
    )
    space = assembla.spaces()[0]

    def test_api_methods_exist(self):
        attrs = ('spaces', 'stream',)
        for attr in attrs:
            self.assertTrue(
                hasattr(self.assembla, attr),
                'assembla.API does not have an attribute named {0}'.format(attr)
            )

    def test_api_stream(self):
        stream = self.assembla.stream()
        self.assertGreater(len(stream), 0)
        for event in stream:
            for key in (
                'date', 'operation', 'object', 'object_id',
                'title', 'space_id', 'space_name', 'author_id',
                'author_name'
            ):
                self.assertIn(key, event.keys())

    def test_api_spaces(self):
        spaces = self.assembla.spaces()
        self.assertGreater(len(spaces), 0)
        for space in spaces:
            for key in (
                'id', 'name', 'description', 'wiki_name', 'public_permissions',
                'team_permissions', 'watcher_permissions', 'share_permissions',
                'team_tab_role', 'created_at', 'updated_at', 'default_showpage',
                'tabs_order', 'parent_id', 'restricted', 'restricted_date',
                'commercial_from', 'banner', 'banner_height', 'banner_text',
                'banner_link', 'style', 'status', 'approved', 'is_manager',
                'is_volunteer', 'is_commercial', 'can_join', 'last_payer_changed_at',
            ):
                self.assertIn(key, space.keys())

    def test_space_methods_exist(self):
        attrs = ('milestones', 'users', 'tickets',)
        for attr in attrs:
            self.assertTrue(
                hasattr(self.space, attr),
                'assembla.Space does not have an attribute named {0}'.format(attr)
            )
