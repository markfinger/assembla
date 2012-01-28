from ..models import Space, Milestone, Ticket, User
from datetime import datetime, date
from .. import API
from ..auth import auth

class TestsForSpace(object):

    def setup(self):
        self.API = API(auth)
        self.spaces = self.API.spaces()
        self.space = self.spaces[0]
        self.milestones = self.space.milestones()
        self.tickets = self.space.tickets()
        self.users = self.space.users()

    def test_attributes_exist(self):   
        # Base class
        assert self.space.Meta.relative_url
        assert self.space.Meta.primary_key
        assert self.space.Meta.base_url
        # Unique attributes

    def test_child_functions_exist(self):
        assert self.space.milestones
        assert self.space.users
        assert self.space.tickets

    def test_urls(self):
        space = Space()
        setattr(space, space.Meta.primary_key, 'test_space_pk')
        assert space.url() == 'https://www.assembla.com/spaces/test_space_pk'
        assert space.list_url() == 'https://www.assembla.com/spaces/my_spaces'

    def test_string_representiation_of_space(self):
        assert str(self.space) == str(self.space.pk())

    def test_child_functions_returns_mulitple_objects_of_the_correct_type(self):
        for milestone in self.milestones:
            assert type(milestone) is Milestone
            assert type(milestone.space) is Space
            assert milestone.space_id == self.space.id
            assert milestone.space == self.space
            # Required attributes
            assert milestone.title is not None
            # Check that fields have been converted to Python types
            assert type(milestone.due_date) is date or type(milestone.due_date) is type(None)
            assert type(milestone.is_completed) is bool
            assert type(milestone.completed_date) is date or type(milestone.completed_date) is type(None)
            assert type(milestone.created_at) is datetime
            assert type(milestone.release_level) is int or type(milestone.release_level) is type(None)
            assert type(milestone.id) is int
        assert len(self.milestones) > 0

        for ticket in self.tickets:
            assert type(ticket) is Ticket
            assert type(ticket.space) is Space
            assert ticket.space_id == self.space.id
            assert ticket.space == self.space
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