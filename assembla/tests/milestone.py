from datetime import datetime
from collections import Counter
from .. import API
from .auth import auth
from ..models import Milestone, Space, Ticket

class TestsForMilestone(object):

    API = API(auth)
    spaces = API.spaces()
    space = spaces[0]
    # Find a milestone with tickets.
    milestone = space.milestone(
        id=Counter(
            [ticket.milestone_id for ticket in space.tickets()]
            ).keys()[0]
        )

    def test_attributes_exist(self):
        # Base class
        assert self.milestone.Meta.relative_url
        assert self.milestone.Meta.primary_key
        assert self.milestone.Meta.base_url
    
    def test_child_functions_exist(self):
        assert self.milestone.tickets
        assert self.milestone.ticket

    def test_urls(self):
        space = Space()
        setattr(space, space.Meta.primary_key, 'test_space_pk')
        milestone = Milestone()
        milestone.space = space
        setattr(milestone, milestone.Meta.primary_key, 'test_milestone_pk')
        assert milestone.url() == 'https://www.assembla.com/spaces/test_space_pk/milestones/test_milestone_pk'

    def test_child_functions_returns_mulitple_objects_of_the_correct_type(self):
        for ticket in self.milestone.tickets():
            assert type(ticket) is Ticket
            assert type(ticket.space) is Space
            assert ticket.space_id == self.space.id
            assert ticket.space.pk() == self.space.pk()
            assert ticket.milestone_id == self.milestone.id
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
        assert len(self.milestone.tickets()) > 0

