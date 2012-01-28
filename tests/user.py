from collections import Counter
from datetime import datetime

from .. import API
from ..models import User, Space, Ticket
from ..auth import auth

class TestsForUser(object):

    def setup(self):
        self.API = API(auth)
        self.spaces = self.API.spaces()
        self.space = self.spaces[0]
        self.users = self.space.users()
        # Find a user with assigned tickets.
        user_id = Counter([
            ticket.assigned_to_id for ticket in self.space.tickets()
                if ticket.assigned_to_id is not None
        ]).keys()[0]
        self.user = filter(lambda user: user.id == user_id,self.users)[0]
        self.tickets = self.user.tickets()

    def test_attributes_exist(self):
        # Base class
        assert self.user.Meta.relative_url
        assert self.user.Meta.primary_key
        assert self.user.Meta.base_url
        # Unique attributes

    def test_child_functions_exist(self):
        assert self.user.tickets

    def test_urls(self):
        space = Space()
        setattr(space, space.Meta.primary_key, 'test_space_pk')
        user = User()
        user.space = space
        setattr(user, user.Meta.primary_key, 'test_pk')
        assert user.url() == 'https://www.assembla.com/profile/test_pk'
        assert user.list_url() == 'https://www.assembla.com/spaces/test_space_pk/users'

    def test_child_functions_returns_mulitple_objects_of_the_correct_type(self):
        for ticket in self.tickets:
            assert type(ticket) is Ticket
            assert type(ticket.space) is Space
            assert ticket.space_id == self.space.id
            assert ticket.space == self.space
            assert ticket.assigned_to_id == self.user.id
            # Required attributes
            assert ticket.number is not None
            assert ticket.summary is not None
            assert ticket.reporter_id is not None
            assert ticket.priority is not None
            assert ticket.status is not None
            # Check that fields have been converted to Python types
            assert type(ticket.number) is int
            assert type(ticket.priority) is int
            assert type(ticket.milestone_id) is int
            assert type(ticket.created_on) is datetime
            assert type(ticket.id) is int
        assert len(self.tickets) > 0

        for user in self.users:
            assert type(user) is User
            assert type(user.space) is Space
            assert user.space == self.space
            # Required attributes
            assert user.login is not None
            assert user.id is not None
        assert len(self.users) > 0