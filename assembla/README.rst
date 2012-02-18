===========
Assembla: Python wrapper for Assembla's RESTful API
===========

An easy to use wrapper around the Assembla API.

Typical usage::
	
	import assembla

	API = assembla.API(auth=('Username', 'Password',))

	# SPACES

	# Retrieve your available spaces
	spaces = API.spaces()

	# Select a specific space
	space = API.space(name='My Space')

	# Retrieve the space's milestones, tickets and users
	milestones = space.milestones()
	tickets = space.tickets()
	users = space.users()

	# MILESTONES

	# Select a specific milestone
	milestone = space.milestone('Release Candidate 1')

	# Retrieve and output the milestone's tickets
	for ticket in milestone.tickets():
		print(ticket.number, ticket.summary)

	# Select a specific user
	user = filter(
		lambda user: user.login_name=='John Smith',
		users
		)[0]

	# Retrieve and output the user's tickets
	for ticket in user.tickets():
		print(ticket.number, ticket.summary)

Source: https://github.com/markfinger/assembla

API Reference: http://www.assembla.com/spaces/breakoutdocs/wiki/Assembla_REST_API
