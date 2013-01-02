from assembla import API
from assembla.tests.auth import auth
from unittest import TestCase


def test_instantiating_assembla_api():
    API(key='key', secret='secret')

def test_failed_instantiating_assembla_api():
    try:
        API()
    except:
        return
    # Shouldn't hit this
    raise Exception

def test_assembla_auth_details_used_for_testing():
    # If this fails, it means the auth template needs to be filled out.
    # Copy `auth.tmpl.py` to `auth.py` and fill it out with your key and secret
    # which are accessible from https://www.assembla.com/user/edit/manage_clients
    assert(
        len(auth) == 2
    )

class TestAssembla(TestCase):

    assembla = API(
        key=auth[0],
        secret=auth[1],
        cache_responses=True,
    )

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
                self.assertIsNotNone(event[key])

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
                # A few of the fields appear not to have had their values set
                if key not in (
                    'tabs_order', 'parent_id', 'restricted_date', 'banner_link',
                    'last_payer_changed_at', 'banner', 'banner_height', 'banner_text',
                    'banner_link', 'style'
                ):
                    self.assertIsNotNone(space[key])

    def test_space_methods_exist(self):
        space = self.assembla.spaces()[0]
        attrs = ('milestones', 'users', 'tickets',)
        for attr in attrs:
            self.assertTrue(
                hasattr(space, attr),
                'assembla.Space does not have an attribute named {0}'.format(attr)
            )

    def __check_ticket_is_valid(self, ticket):
        for key in (
            'id', 'number', 'summary', 'description', 'priority', 'completed_date',
            'component_id', 'created_on', 'permission_type', 'importance', 'is_story',
            'milestone_id', 'notification_list', 'space_id', 'state',
            'status', 'story_importance', 'updated_at', 'working_hours', 'estimate',
            'total_estimate', 'total_invested_hours', 'total_working_hours',
            'assigned_to_id', 'reporter_id', 'custom_fields',
        ):
            self.assertIn(key, ticket.keys())
            # Some of the fields may have been returned with null-esque values
            if key not in ('completed_date','component_id', 'assigned_to_id',):
                self.assertIsNotNone(ticket[key])

    def test_space_tickets(self):
        for space in self.assembla.spaces():
            for ticket in space.tickets():
                self.__check_ticket_is_valid(ticket)
                self.assertEqual(ticket.space['id'], space['id'])
                self.assertEqual(ticket.api, self.assembla)
                # Exit once we've hit a space with tickets
                return

    def test_pagination(self):
        # WARNING: this wont pass unless you have some spaces with more than 1000 tickets in them
        for space in self.assembla.spaces():
            if len(space.tickets()) > 1000:
                # Exit once we've hit a space with correctly paginated tickets
                return
        self.assertTrue(
            False,
            'This may fail if you Assembla spaces have insufficient '
            'numbers of tickets to trigger pagination'
        )

    def test_space_milestones(self):
        for space in self.assembla.spaces():
            for milestone in space.milestones():
                for key in (
                    'id', 'due_date', 'title', 'user_id', 'created_at', 'created_by',
                    'space_id', 'description', 'is_completed', 'completed_date',
                    'updated_at', 'updated_by', 'release_level', 'release_notes',
                    'planner_type', 'pretty_release_level',
                ):
                    self.assertIn(key, milestone.keys())
                    # Some of the fields may have been returned with null-esque values
                    if key not in ('completed_date', 'release_level', 'release_notes',):
                        self.assertIsNotNone(milestone[key])
                self.assertEqual(milestone.space['id'], space['id'])
                self.assertEqual(milestone.api, self.assembla)
                # Exit once we've hit a space with tickets
                return

    def test_space_users(self):
        for space in self.assembla.spaces():
            for user in space.users():
                for key in (
                    'id', 'login', 'name', 'email', 'organization', 'organization',
                    'im', 'im2'
                ):
                    self.assertIn(key, user.keys())
                self.assertEqual(user.api, self.assembla)
                # Exit once we've hit a space with tickets
                return

    def test_milestone_tickets(self):
        for space in self.assembla.spaces():
            for milestone in space.milestones():
                for ticket in milestone.tickets():
                    self.__check_ticket_is_valid(ticket)
                    self.assertEqual(ticket.milestone['id'], milestone['id'])
                    self.assertEqual(ticket.milestone.space['id'], milestone.space['id'])
                    self.assertEqual(ticket.space['id'], space['id'])
                    self.assertEqual(ticket.api, self.assembla)
                    # Exit once we've hit a milestone with tickets
                    return
        self.assertTrue(False, 'this may fail if your Assembla account has insufficient data')

    def test_user_tickets(self):
        for space in self.assembla.spaces():
            for user in space.users():
                for ticket in user.tickets():
                    self.__check_ticket_is_valid(ticket)
                    self.assertEqual(ticket['assigned_to_id'], user['id'])
                    self.assertEqual(ticket.user['id'], user['id'])
                    self.assertEqual(ticket.space['id'], space['id'])
                    self.assertEqual(ticket.api, self.assembla)
                    # Exit once we've hit a user with tickets
                    return
        self.assertTrue(False, 'this may fail if your Assembla account has insufficient data')

    def test_api_space_filtering(self):
        test_space = self.assembla.spaces()[-1]
        filtered_spaces = self.assembla.spaces(
            id=test_space.get('id'),
            name=test_space.get('name'),
        )
        self.assertEqual(len(filtered_spaces), 1)
        for space in filtered_spaces:
            self.assertEqual(
                space.get('id'),
                test_space.get('id')
            )

    def test_space_ticket_filtering(self):
        space_with_tickets = None
        for space in self.assembla.spaces():
            if len(space.tickets()) > 1:
                space_with_tickets = space
                break
        last_ticket = space_with_tickets.tickets()[-1]
        self.assertEqual(
            len(space_with_tickets.tickets(number=last_ticket.get('number'))),
            1
        )
        # This works 100% of the time, most of the time
        self.assertGreater(
            len(space_with_tickets.tickets(priority=last_ticket.get('priority'))),
            1
        )