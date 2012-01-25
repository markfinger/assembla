from ..models import Milestone, Space
from .test import AssemblaTest

class TestsForMilestone(AssemblaTest):

    def setup(self):
        super(TestsForMilestone, self).setup()
        self.milestone = Milestone()
    
    def test_attributes_exist(self):
        # Base class
        assert self.milestone.Meta.relative_url
        assert self.milestone.Meta.primary_key
        assert self.milestone.Meta.base_url
    
    def test_child_functions_exist(self):
        pass
#        assert self.milestone.user
#        assert self.milestone.users
#        assert self.milestone.ticket
#        assert self.milestone.tickets

    def test_urls(self):
        space = Space()
        setattr(space, space.Meta.primary_key, 'test_space_pk')
        milestone = Milestone()
        milestone.space = space
        setattr(milestone, milestone.Meta.primary_key, 'test_ticket_pk')
        assert milestone.url() == 'https://www.assembla.com/spaces/test_space_pk/milestones/test_ticket_pk'