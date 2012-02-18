====================================================
Assembla: Python wrapper for Assembla's RESTful API
====================================================

An easy to use wrapper around the Assembla API.

 - `Basic Example`_
 - `Examples for Spaces`_
 - `Examples for Milestones`_
 - `Examples for Users`_
 - `Examples for Tickets`_
 - `Model Reference`_
 - `Caching`_


Basic Example
-------------

::

	from assembla import API

	assembla = API(auth=('Username', 'Password',))

	print assembla.space(name='Big Project').ticket(number=201).status_name

Examples for Spaces
-------------------
::

	# Retrieve your available spaces
	spaces = API.spaces()

	# Select a specific space
	space = API.space(name='Big Project')

	# Retrieve the space's milestones
	milestones = space.milestones()

	# Retrieve a specific milestone from the space
	milestone = space.milestone('Release Candidate 1')

	# Retrieve all of the space's tickets
	tickets = space.tickets()

	# Retrieve the space's tickets which are awaiting testing
	tickets = space.tickets(status_name='Test')

	# Retrieve a specific ticket from the space
	ticket = space.ticket(number=301)

	# Retrieve all of the space's users
	users = space.users()

	# Retrieve a specific user from the space
	user = space.user(name='John Smith')

Examples for Milestones
-----------------------
::

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

Examples for Users
------------------
::

	# Select a specific user
	user = assembla.space(name='Big Project').user(name='John Smith')

	# Retrieve the user's tickets
	tickets = user.tickets()

	# Retrieve a specific ticket from the user
	ticket = user.ticket(status_name='Test')

Examples for Tickets
--------------------
::

	# Retrieve a specific ticket
	ticket = space.ticket(number=201)

	# Retrieve all tickets awaiting code review
	tickets = space.tickets(status_name='Code Review')

	# Retrieve all tickets assigned to an individual which are of a certain priority
	# and awaiting testing
	tickets = space.tickets(
		assigned_to_id=user.id,
		priority=1,
		status_name='Test'
		)

Model Reference
---------------
All models (Space, Milestone, User and Ticket) are returned with fields corresponding
to the data from Assembla. Naming conventions generally follow Assembla's `API
Reference <http://www.assembla.com/spaces/breakoutdocs/wiki/Assembla_REST_API>`_.
Where possible, values are coerced to native Python types.

Caching
-------
Spaces have an in-memory caching system, which reduces the overheard on repeated
requests to Assembla. By default, it is activated. You can deactivate it::

	# Deactivate the cache for a space, all subsequent requests will return fresh data
	space.cache.deactivate()
	# Deactivate the cache for all spaces instantiated from `assembla`
	assembla = API(auth=('Username', 'Password',), use_cache=False)

If you want to purge stale data from a space's cache and begin refilling it::

	# Purge stale data from the space's cache, any subsequent request will update the cache
	space.cache.purge()

Source: https://github.com/markfinger/assembla