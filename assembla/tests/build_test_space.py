from time import sleep
from random import choice
import json
import requests
from assembla import API, Space, Milestone, Ticket, settings
from assembla.tests.auth import auth


SPACE_NAME = 'API Test Space 7500'

NUMBER_OF_MILESTONES = 5
MILESTONE_TITLE_FORMAT = 'Test Milestone #{0}'

NUMBER_OF_TICKETS = 7500
TICKET_SUMMARY_FORMAT = 'Test Ticket #{0}'

assembla = API(
    key=auth[0],
    secret=auth[1],
)


class TestDataBuilder(object):
    """
    Build a space with sufficient data to run the tests against
    """

    def _post_json(self, model, rel_path=None, data=None):
        url = '{0}/{1}/{2}.json'.format(
            settings.API_ROOT_PATH,
            settings.API_VERSION,
            rel_path or model.rel_path
        )

        if data:
            data = json.dumps(data)

        # Try not to hammer the API too much
        sleep(5)

        # Fetch the data
        response = requests.post(url=url,headers={'Content-type': 'application/json','X-Api-Key': auth[0],'X-Api-Secret': auth[1],},data=data)

        if response.status_code != 201:
            import pdb; pdb.set_trace()

        return response

    def _create_space(self):
        self.space = self._get_space()
        if not self.space:
            print 'Creating space: "{0}"'.format(SPACE_NAME)
            self._post_json(Space, data={
                'space': {
                    'name': SPACE_NAME
                }
            })
            self.space = self._get_space()

        # TODO: add Space Tools to the models

        print 'Creating ticket space tool'
        # Add the ticket tool
        self._post_json(
            Space,
            rel_path=self.space._build_rel_path('space_tools/13/add')
        )

        print 'Creating milestone space tool'
        # Add the milestone tool
        self._post_json(
            Space,
            rel_path=self.space._build_rel_path('space_tools/9/add')
        )

    def _get_space(self):
        spaces = assembla.spaces(name=SPACE_NAME)
        if spaces:
            return spaces[0]

    def _create_milestones(self):
        milestones = self.space.milestones()
        if len(milestones) < NUMBER_OF_MILESTONES:
            for i in xrange(len(milestones) + 1, NUMBER_OF_MILESTONES + 1):
                print 'Creating milestone: "{0}"'.format(MILESTONE_TITLE_FORMAT.format(i))
                self._post_json(
                    Milestone,
                    rel_path=self.space._build_rel_path('milestones'),
                    data={
                        'milestone': {
                            'title': MILESTONE_TITLE_FORMAT.format(i)
                        }
                    }
                )
        self.milestones = self.space.milestones()

    def _create_tickets(self):
        tickets = self.space.tickets()

        if len(tickets) < NUMBER_OF_TICKETS:
            if tickets:
                start = tickets[-1]['number'] + 1
                end = start + NUMBER_OF_TICKETS - len(tickets)
            else:
                start = 1
                end = start + NUMBER_OF_TICKETS

            print "Creating {0} tickets...\n".format(end - start)
            for i in xrange(start, end):
                # Assign the ticket to a random milestone
                milestone = choice(self.milestones)
                self._post_json(
                    Ticket,
                    rel_path=self.space._build_rel_path('tickets'),
                    data={
                        'ticket': {
                            'summary': TICKET_SUMMARY_FORMAT.format(i),
                            'milestone_id': milestone['id']
                        }
                    }
                )
                print 'Created: "{0}"'.format(TICKET_SUMMARY_FORMAT.format(i))

    def build_data(self):
        self._create_space()

        self._create_milestones()

        self._create_tickets()