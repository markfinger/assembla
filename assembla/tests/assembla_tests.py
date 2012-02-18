from collections import Counter
from datetime import datetime, date

from assembla.models import *
from assembla.tests.auth import auth


class TestAssembla:
    """
    Unit tests the Assembla API wrapper
    """
    assembla = API(auth)
    spaces = assembla.spaces()
    space = spaces[0]
    # Find a milestone with tickets.
    milestone = space.milestone(
        id=Counter(
            [ticket.milestone_id for ticket in space.tickets()]
            ).keys()[0]
        )
    # Find a user with assigned tickets.
    user = space.user(
        id=Counter([
            ticket.assigned_to_id for ticket in space.tickets()
                if ticket.assigned_to_id is not None
            ]).keys()[0]
        )

    ###################################
    #             API                 #
    ###################################

    def test_api_can_be_initialised(self):
        assert API(auth=('_','_',))

    def test_api_child_functions_exist(self):
        assert self.assembla.spaces
        assert self.assembla.space

    def test_api_init_accepts_auth_credentials(self):
        api = API(auth=auth)
        assert api.auth == auth

    def test_api_init_complains_if_no_auth_arg(self):
        try:
            API()
        except AssemblaError as e:
            assert e.code==100

    def test_credential_check_expect_success(self):
        assert self.assembla.check_credentials() is True

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
        assert len(self.spaces) > 0
        for space in self.spaces:
            assert self.__test_space_type(space)

    def test_space_returns_type_space(self):
        space = self.assembla.space(
            id=self.spaces[0].id,
            wiki_name=self.spaces[0].wiki_name,
        )
        assert space.id == self.spaces[0].id
        assert space.wiki_name == self.spaces[0].wiki_name
        assert self.__test_space_type(space)

    def test_bad_url_for_get_xml_tree(self):
        try:
            self.assembla._get_xml_tree(
                # Hopefully this fails :)
                url='http://www.csdhjbc****jsdbajcbsdjb.com/cdjsbjhcsbdjhcsj/cdhsjbcjsdhcjhscdhb/csdjhbcsdjbchsdjbbjcds',
                auth=('^__^', '^__^',)
                )
        except AssemblaError as e:
            assert e.code==130

    def test_cache_returns_copied_objects(self):
        ticket = self.space.tickets()[0]
        ticket.id = '{{{{{{========}}}}}}'
        same_ticket = self.space.tickets()[0]
        assert ticket.id != same_ticket.id

    ###################################
    #             SPACES              #
    ###################################

    def test_space_attributes_exist(self):
        # Base class
        assert self.space.Meta.relative_url
        assert self.space.Meta.primary_key
        assert self.space.Meta.base_url
        # Unique attributes

    def test_space_child_functions_exist(self):
        assert self.space.milestones
        assert self.space.milestone
        assert self.space.users
        assert self.space.user
        assert self.space.tickets
        assert self.space.ticket

    def test_space_urls(self):
        space = Space()
        setattr(space, space.Meta.primary_key, 'test_space_pk')
        assert space.url() == 'https://www.assembla.com/spaces/test_space_pk'
        assert space.list_url() == 'https://www.assembla.com/spaces/my_spaces'

    def __test_milestone_type(self, milestone):
        assert type(milestone) is Milestone
        assert type(milestone.space) is Space
        assert milestone.space_id == self.space.id
        assert milestone.space.pk() == self.space.pk()
        # Required attributes
        assert milestone.title is not None
        # Check that fields have been converted to Python types
        assert type(milestone.due_date) is date or type(milestone.due_date) is type(None)
        assert type(milestone.is_completed) is bool
        assert type(milestone.completed_date) is date or type(milestone.completed_date) is type(None)
        assert type(milestone.created_at) is datetime
        assert type(milestone.release_level) is int or type(milestone.release_level) is type(None)
        assert type(milestone.id) is int
        return True

    def __test_ticket_type(self, ticket):
        assert type(ticket) is Ticket
        assert type(ticket.space) is Space
        assert ticket.space_id == self.space.id
        assert ticket.space.pk() == self.space.pk()
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
        return True

    def __test_user_type(self, user):
        assert type(user) is User
        assert type(user.space) is Space
        assert user.space.pk() == self.space.pk()
        # Required attributes
        assert user.login is not None
        assert user.id is not None
        return True

    def test_space_child_functions_returns_mulitple_objects_of_the_correct_type(self):
        for milestone in self.space.milestones():
            self.__test_milestone_type(milestone)
        assert len(self.space.milestones()) > 0

        for ticket in self.space.tickets():
            self.__test_ticket_type(ticket)
        assert len(self.space.tickets()) > 0

        for user in self.space.users():
            self.__test_user_type(user)
        assert len(self.space.users()) > 0

    def test_child_singleton_functions_return_the_correct_types(self):
        milestone = self.space.milestone(
            **{Milestone.Meta.primary_key:self.space.milestones()[0].pk()}
        )
        assert milestone.pk() == self.space.milestones()[0].pk()
        assert self.__test_milestone_type(milestone)

        ticket = self.space.ticket(
            **{Ticket.Meta.primary_key:self.space.tickets()[0].pk()}
        )
        assert ticket.pk() == self.space.tickets()[0].pk()
        assert self.__test_ticket_type(ticket)

        user = self.space.user(
            **{User.Meta.primary_key:self.space.users()[0].pk()}
        )
        assert user.pk() == self.space.users()[0].pk()
        assert self.__test_user_type(user)

    ###################################
    #             MILESTONES          #
    ###################################

    def test_milestone_attributes_exist(self):
        # Base class
        assert self.milestone.Meta.relative_url
        assert self.milestone.Meta.primary_key
        assert self.milestone.Meta.base_url

    def test_milestone_child_functions_exist(self):
        assert self.milestone.tickets
        assert self.milestone.ticket

    def test_milestone_urls(self):
        space = Space()
        setattr(space, space.Meta.primary_key, 'test_space_pk')
        milestone = Milestone()
        milestone.space = space
        setattr(milestone, milestone.Meta.primary_key, 'test_milestone_pk')
        assert milestone.url() == 'https://www.assembla.com/spaces/test_space_pk/milestones/test_milestone_pk'

    def test_milestone_child_functions_returns_mulitple_objects_of_the_correct_type(self):
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

    ###################################
    #             USERS               #
    ###################################

    def test_user_attributes_exist(self):
        # Base class
        assert self.user.Meta.relative_url
        assert self.user.Meta.primary_key
        assert self.user.Meta.base_url

    def test_user_child_functions_exist(self):
        assert self.user.tickets
        assert self.user.ticket

    def test_user_urls(self):
        space = Space()
        setattr(space, space.Meta.primary_key, 'test_space_pk')
        user = User()
        user.space = space
        setattr(user, user.Meta.primary_key, 'test_pk')
        assert user.url() == 'https://www.assembla.com/profile/test_pk'
        assert user.list_url() == 'https://www.assembla.com/spaces/test_space_pk/users'

    def test_user_child_functions_returns_mulitple_objects_of_the_correct_type(self):
        for ticket in self.user.tickets():
            assert type(ticket) is Ticket
            assert type(ticket.space) is Space
            assert ticket.space_id == self.space.id
            assert ticket.space.pk() == self.space.pk()
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
        assert len(self.user.tickets()) > 0

        for user in self.space.users():
            assert type(user) is User
            assert type(user.space) is Space
            assert user.space.pk() == self.space.pk()
            # Required attributes
            assert user.login is not None
            assert user.id is not None
        assert len(self.space.users()) > 0

    ###################################
    #             TICKETS             #
    ###################################

    def test_ticket_attributes_exist(self):
        # Base class
        ticket = Ticket()
        assert ticket.Meta.relative_url
        assert ticket.Meta.primary_key
        assert ticket.Meta.base_url

    def test_ticket_urls(self):
        space = Space()
        setattr(space, space.Meta.primary_key, 'test_space_pk')
        ticket = Ticket()
        ticket.space = space
        setattr(ticket, ticket.Meta.primary_key, 'test_ticket_pk')
        assert ticket.url() == 'https://www.assembla.com/spaces/test_space_pk/tickets/test_ticket_pk'

    ###################################
    #             ERROR HANDLING      #
    ###################################

    def test_assembla_error_can_be_raised(self):
        try:
            raise AssemblaError(100)
        except TypeError:
            raise Exception('Should not get here.')
        except AssemblaError:
            pass

    def test_assembla_error_reports_message_correctly(self):
        try:
            raise AssemblaError(100)
        except AssemblaError as e:
            assert str(e) == AssemblaError.error_codes[100]