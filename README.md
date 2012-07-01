====================================================
Assembla: Python wrapper for Assembla's RESTful API
====================================================

An easy to use wrapper around the Assembla API.

- [Basic Example](#basic-example)
- [Examples for Spaces](#examples-for-spaces)
- [Examples for Milestones](#examples-for-milestones)
- [Examples for Users](#examples-for-users)
- [Examples for Tickets](#examples-for-tickets)
- [Model Reference](#model-reference)
- [Caching](#caching)


Basic Example
--------------------------------------------------

```python
from assembla import API

assembla = API(auth=('Username', 'Password',))

print assembla.space(name='Big Project').ticket(number=201).status_name
```


Examples for Spaces
--------------------------------------------------

```python
# Retrieve your available spaces
spaces = assembla.spaces()

# Select a specific space
space = assembla.space(name='Big Project')

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
```


Examples for Milestones
--------------------------------------------------

```python
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
```


Examples for Users
--------------------------------------------------

```python
# Select a specific user
user = assembla.space(name='Big Project').user(name='John Smith')

# Retrieve the user's tickets
tickets = user.tickets()

# Retrieve a specific ticket from the user
ticket = user.ticket(status_name='Test')
```


Examples for Tickets
--------------------------------------------------

```python
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
```


Model Reference
--------------------------------------------------

All models (Space, Milestone, User and Ticket) are returned with fields corresponding
to the data from Assembla. Naming conventions generally follow Assembla's `API
Reference <http://www.assembla.com/spaces/breakoutdocs/wiki/Assembla_REST_API>`_.
Where possible, values are coerced to native Python types.


Caching
--------------------------------------------------

Spaces have an in-memory caching system, which reduces the overheard on repeated
requests to Assembla. By default, it is activated. You can deactivate it::

```python
# Deactivate the cache for a space, all subsequent requests will return fresh data
space.cache.deactivate()

# Deactivate the cache for all spaces instantiated from `assembla`
assembla = API(auth=('Username', 'Password',), use_cache=False)
```

If you want to purge stale data from a space's cache and begin refilling it::
```python
# Purge stale data from the space's cache, any subsequent request will update the cache
space.cache.purge()
```


Contributors
--------------------------------------------------

- [Mark Finger](http://github.com/markfinger)
- [Venkata Ramana](http://github.com/arjunc77)