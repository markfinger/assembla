from ..models import Ticket, Space
from .. import API
from .auth import auth

class TestsForTicket(object):

    def setup(self):
        self.ticket = Ticket()
        self.API = API(auth)

    def test_attributes_exist(self):
        # Base class
        assert self.ticket.Meta.relative_url
        assert self.ticket.Meta.primary_key
        assert self.ticket.Meta.base_url
        # Unique attributes

    def test_child_functions_exist(self):
        pass

    def test_urls(self):
        space = Space()
        setattr(space, space.Meta.primary_key, 'test_space_pk')
        ticket = Ticket()
        ticket.space = space
        setattr(ticket, ticket.Meta.primary_key, 'test_ticket_pk')
        assert ticket.url() == 'https://www.assembla.com/spaces/test_space_pk/tickets/test_ticket_pk'