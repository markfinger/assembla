from StringIO import StringIO
import re

from django.template.defaultfilters import slugify

import requests
from lxml import etree

from ._models import *
from tests import auth


headers = {
    'Accept': 'application/xml'
}
session = requests.session(auth=auth, headers=headers)

def parseIO(string):
    return StringIO(str(string))

def harvest_spaces():
    """
    Get a list of spaces available to the user and create a Space
    instance for each.
    """

    url = 'http://www.assembla.com/spaces/my_spaces'
    tree = etree.parse(parseIO(session.get(url).content))

    # Harvest spaces
    for node in tree.findall('space'):
        assembla_id = node.find('id').text
        name = node.find('name').text
        description = node.find('description').text

        # Descriptions are sometimes returned as None
        if not description:
            description = ''

        Space.objects.get_or_create(
            assembla_id=assembla_id,
            defaults={
                'name': name,
                'description': description,
                'slug': slugify(name[:50])
            }
        )

def harvest_milestones():
    """
    Get a list of milestones for each space and create a Milestone
    instance for each.
    """

    spaces = Space.objects.filter(is_active=True)
    for space in spaces:
        url = 'http://www.assembla.com/spaces/{0}/milestones/'.format(space.assembla_id)
        tree = etree.parse(parseIO(session.get(url).content))
        # Harvest milestones
        for node in tree.findall('milestone'):
            assembla_id = node.find('id').text
            name = node.find('title').text
            description = node.find('description').text
            due_date = node.find('due-date').text

            if not description:
                description = ''
            if not due_date:
                # Time travelling milestone...
                due_date = date(year=1970, month=1, day=1)
            else:
                # Harvest date from the string.
                due_date = due_date.split('-')
                due_date = date(
                    year=int(due_date[0]),
                    month=int(due_date[1]),
                    day=int(due_date[2])
                )

            Milestone.objects.get_or_create(
                assembla_id=assembla_id,
                defaults={
                    'name': name,
                    'slug': slugify(name[:50]),
                    'description': description,
                    'due_date': due_date,
                    'space': space,
                }
            )

def harvest_users():
    """
    Get a list of users for each space and create a User
    instance for each unique user.
    """

    spaces = Space.objects.filter(is_active=True)
    for space in spaces:
        url = 'http://www.assembla.com/spaces/{0}/users/'.format(space.assembla_id)
        tree = etree.parse(parseIO(session.get(url).content))
        # Harvest users
        for node in tree.findall('user'):
            assembla_id = node.find('id').text
            name = node.find('name').text

            User.objects.get_or_create(
                assembla_id=assembla_id,
                defaults={
                    'name': name,
                }
            )

def harvest_ticket_statuses():
    """
    Get a list of available ticket statuses for each space and create
    a TicketStatus instance for each.
    """
    spaces = Space.objects.filter(is_active=True)
    for space in spaces:
        url = 'http://www.assembla.com/spaces/{0}/tickets/custom_statuses'.format(space.assembla_id)
        tree = etree.parse(parseIO(session.get(url).content))
        # Harvest ticket statuses.
        for node in tree.findall('ticket-status'):
            name = node.find('name').text

            TicketStatus.objects.get_or_create(
                space=space,
                name=name
            )

def harvest_tickets():
    """
    Get a list of tickets for each milestone and create a Ticket
    instance for each.
    """

    spaces = Space.objects.filter(is_active=True)
    for space in spaces:
        url = 'https://www.assembla.com/spaces/{0}/tickets/report/0'.format(space.assembla_id)
        tree = etree.parse(parseIO(session.get(url).content))
        # Harvest tickets
        for node in tree.findall('ticket'):
            ticket_num = node.find('number').text
            description = node.find('description').text
            if not description:
                description = ''
            summary = node.find('summary').text
            number = node.find('number').text
            priority = node.find('priority').text
            # Extract the estimate and cast to an integer
            try:
                estimate = re.sub("[^0-9.]", "", node.find('estimate').text) # = '13.0'
                estimate = int(float(estimate)) # = 13
            except TypeError:
                estimate = 0
            try:
                assigned_to = User.objects.get(assembla_id=node.find('assigned-to-id').text)
            except User.DoesNotExist:
                # Tickets can be unassigned
                assigned_to = None
            try:
                milestone = Milestone.objects.get(assembla_id=node.find('milestone-id').text)
            except Milestone.DoesNotExist:
                # Milestones can be unassigned
                milestone = None

            # Get or create the ticket, cant use get_or_create as we may need to update values.
            try:
                ticket = Ticket.objects.get(
                    number=ticket_num,
                    space=space
                )
            except Ticket.DoesNotExist:
                ticket = Ticket()
                ticket.number = ticket_num
            # Update all the values to reflect the current state of the ticket.
            ticket.description = description
            ticket.summary = summary
            ticket.number = number
            ticket.priority = priority
            ticket.estimate = estimate
            ticket.space = space
            ticket.assigned_to = assigned_to
            ticket.milestone = milestone
            ticket.save()

            # Harvest the time when the ticket was created.
            datetime_updated = node.find('created-on').text
            # Extract the datetime, ignoring the timezone.
            timestamp = datetime.strptime(datetime_updated[:-6], '%Y-%m-%dT%H:%M:%S')
            # Create a historical entry representing the creation of the ticket.
            TicketHistory.objects.get_or_create(
                ticket=ticket,
                status=space.new_status(),
                datetime=timestamp,
            )

def harvest_ticket_histories():
    """
    Get a list of status changes for each ticket and create a
    TicketHistory instance for each.
    """
    tickets = Ticket.objects.filter(
        milestone__isnull=False,
        milestone__is_active=True,
        space__is_active=True
    )
    for ticket in tickets:
        url = 'https://www.assembla.com/spaces/{0}/tickets/{1}/comments'.format(ticket.space.assembla_id, ticket.number)
        tree = etree.parse(parseIO(session.get(url).content))
        # Harvest tickets histories from status changes in the ticket's comments.
        for node in tree.findall('comment'):
            ticket_changes = node.find('ticket-changes').text
            if ticket_changes and 'status' in ticket_changes:
                # Harvest the new status
                statuses = re.findall(r'  - (.*?)\n', ticket_changes)
                space_statuses = [space.name for space in TicketStatus.objects.filter(space=ticket.space)]
                # The loop ticks through all the statuses and exits with status_name set to
                # the 2nd matching status, which is what the ticket's been set to on assembla.
                for status in statuses:
                    if status in space_statuses:
                        status_name = status
                status = ticket.space.statuses.get(name=status_name)

                # Harvest the time when the ticket was updated.
                datetime_updated = node.find('created-on').text
                # Extract the datetime, ignoring the timezone.
                timestamp = datetime.strptime(datetime_updated[:-6], '%Y-%m-%dT%H:%M:%S')

                TicketHistory.objects.get_or_create(
                    ticket=ticket,
                    status=status,
                    datetime=timestamp,
                )
