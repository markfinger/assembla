===========
Assembla: Python wrapper for Assembla's RESTful API
===========

An easy to use wrapper around the Assembla API.

Basic Example::

	from assembla import API

	assembla = API(auth=('Username', 'Password',))

	print assembla.space(name='Big Project').ticket(number=201).status_name

Space Examples::

	# Retrieve your available spaces
	spaces = API.spaces()

	# Select a specific space
	space = API.space(name='Big Project')

	# Retrieve the space's milestones
	milestones = space.milestones()
	# Retrieve a specific milestone from the space
	milestone = space.milestone('Release Candidate 1')

	# Retrieve the space's tickets
	tickets = space.tickets()
	# Retrieve a specific ticket from the space
	ticket = space.ticket(number=301)

	# Retrieve the space's users
	users = space.users()
	# Retrieve a specific user from the space
	user = space.user(name='John Smith')

Milestone Examples::

	# Select a specific milestone
	milestone = assembla.space(name='Big Project').milestone('Release Candidate 1')

	# Retrieve the milestone's tickets
	tickets = milestone.tickets()
	# Retrieve a specific ticket from the milestone
	ticket = milestone.ticket(number=301)

	# Retrieve the milestone's users
	users = milestone.users()
	# Retrieve a specific user from the milestone
	user = milestone.user(name='John Smith')

User Examples::

	# Select a specific user
	user = assembla.space(name='Big Project').user(name='John Smith')

	# Retrieve the user's tickets
	tickets = user.tickets()
	# Retrieve a specific ticket from the user
	ticket = user.ticket(status_name='Test')

Model Reference: fields generally follow Assembla's reference: http://www.assembla.com/spaces/breakoutdocs/wiki/Assembla_REST_API

Spaces have an in-memory caching system, which reduces the overheard on repeated
requests to Assembla. By default, it is activated. You can deactivate it::

	# Deactivate the cache for a space, all subsequent requests will return fresh data
	space.cache.deactivate()
	# Deactivate the cache for all spaces instantiated from `assembla`
	assembla = API(auth=('Username', 'Password',), use_cache=False)

If you want to purge stale data from a space's cache and begin refilling it::

	# Purge stale data from the space's cache, any subsequent request will update the cache
	space.cache.clear()

Source: https://github.com/markfinger/assembla