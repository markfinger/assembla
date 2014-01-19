import unittest
from assembla import API
from assembla.tests.auth import auth
import datetime
import time


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

class TestAssembla(unittest.TestCase):

    assembla = API(
        key=auth[0],
        secret=auth[1],
    )
    assembla.cache_responses = True

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
            if key not in (
                'completed_date','component_id', 'assigned_to_id',
                'description', 'milestone_id'
            ):
                try:
                    self.assertIsNotNone(ticket[key])
                except AssertionError:
                    print key, "is None in"
                    print ticket.data
                    raise

    def __space_with_tickets(self, cutoff=1, skip=0):
        s = 0
        for space in self.assembla.spaces():
            if s >= skip and len(space.tickets()) > cutoff:
                return space
            s = s + 1
        raise ValueError("No spaces had tickets")

    def __milestone_with_tickets(self, cutoff=1, skip=0):
        space = self.__space_with_tickets(cutoff=cutoff, skip=skip)
        for milestone in space.milestones():
            if len(milestone.tickets()) > cutoff:
                return milestone
        #reached when a space with tickets doesn't have milestones with tickets.
        return self.__milestone_with_tickets(cutoff, skip=skip+1)


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
                    'banner_link', 'style', 'description', 'commercial_from',
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

    def test_space_tickets(self):
        space = self.__space_with_tickets()
        ticket = space.tickets()[0]
        self.__check_ticket_is_valid(ticket)
        self.assertEqual(ticket.space['id'], space['id'])
        self.assertEqual(ticket.api, self.assembla)

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
        milestone = self.__milestone_with_tickets()
        for key in (
            'id', 'due_date', 'title', 'user_id', 'created_at', 'created_by',
            'space_id', 'is_completed', 'completed_date',
            'updated_at', 'updated_by', 'release_level', 'release_notes',
            'planner_type', 'pretty_release_level',
        ):
            self.assertIn(key, milestone.keys())
            # Some of the fields may have been returned with null-esque values
            if key not in (
                'completed_date', 'release_level', 'release_notes', 'due_date',
                'user_id', 'description',
            ):
                self.assertIsNotNone(milestone[key])
        self.assertIsNotNone(milestone.space)
        self.assertEqual(milestone.api, self.assembla)

    def test_space_users(self):
        for space in self.assembla.spaces():
            for user in space.users():
                for key in ('id', 'login', 'name'):
                    self.assertIn(key, user.keys())
                self.assertEqual(user.api, self.assembla)
                # Exit once we've hit a space with tickets
                return

    def test_milestone_tickets(self):
        milestone = self.__milestone_with_tickets()
        ticket = milestone.tickets()[0]
        self.__check_ticket_is_valid(ticket)
        self.assertEqual(ticket.milestone['id'], milestone['id'])
        self.assertEqual(ticket.milestone.space['id'], milestone.space['id'])
        self.assertIsNotNone(ticket.space)
        self.assertEqual(ticket.api, self.assembla)


    def test_user_tickets(self):
        for space in self.assembla.spaces():
            for user in space.users():
                for ticket in user.tickets():
                    self.__check_ticket_is_valid(ticket)
                    self.assertEqual(ticket['assigned_to_id'], user['id'])
                    self.assertEqual(ticket.user['id'], user['id'])
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
        space = self.__space_with_tickets()
        last_ticket = space.tickets()[-1]
        self.assertEqual(
            len(space.tickets(number=last_ticket.get('number'))),
            1
        )
        # This works 100% of the time, most of the time
        self.assertGreater(
            len(space.tickets(priority=last_ticket.get('priority'))),
            1
        )

    def test_space_tickets_does_not_return_duplicates(self):
        space = self.__space_with_tickets(10)
        ids = [t['id'] for t in space.tickets()]
        self.assertItemsEqual(ids, list(set(ids)))

    def test_space_tickets_does_not_return_duplicates_if_paginating(self):
        space = self.__space_with_tickets(1000)
        ids = [t['id'] for t in space.tickets()]
        self.assertItemsEqual(ids, list(set(ids)))

    def test_extra_params_filtering(self):
        # Find two different timestamps in the stream and filter by the later one
        # so that we can see if the filtering by extra_params works

        stream = self.assembla.stream()
        first_time = None
        second_time = None
        for event in stream:
            # Strip the time from the Event
            time_struct = time.strptime(event.get('date'), '%Y-%m-%dT%H:%M:%S+00:00')
            # Instantiate a datetime using only the Year, Month, Day, Hour and Minute
            event_time = datetime.datetime(*time_struct[:5])

            if not first_time:
                first_time = event_time

            if event_time < first_time:
                second_time = event_time

        filter_from = first_time.strftime('%Y-%m-%d %H:%M')
        filtered_stream = self.assembla.stream(extra_params={"from": filter_from})

        self.assertLess(len(filtered_stream), len(stream))

if __name__ == '__main__':
    unittest.main()