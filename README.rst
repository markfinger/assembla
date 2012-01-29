===========
Assembla: Python wrapper for API
===========

An easy to use wrapper around the Assembla API which allows you to retrieve
Spaces, Milestones, Tickets and Users.

Typical usage::

    import assembla

    API = assembla.API(
        'Username',
        'Password',
        )

    # Retrieve your available spaces
    spaces = API.spaces()

    # Select a specific space
    space = filter(
        lambda space: space.name=='My Space',
        spaces
        )[0]

    # Objects returned possess all the attributes available through the API.
    # For example, we can output the space's name
    print(space.name)

    # Retrieve the space's milestones, tickets and users
    milestones = space.milestones()
    tickets = space.tickets()
    users = space.users()

    # Select a specific milestone
    milestone = filter(
        lambda milestone: milestone.title=='Release Candidate 1',
        milestones
        )[0]

    # Retrieve and output the milestone's tickets
    for ticket in milestone.tickets():
        print(ticket.number, ticket.summary)

Source: https://github.com/markfinger/assembla

API Reference: http://www.assembla.com/spaces/breakoutdocs/wiki/Assembla_REST_API