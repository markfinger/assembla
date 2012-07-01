===============================================================
Python wrapper for the Assembla API
===============================================================

An easy to use wrapper around the Assembla API.

- [Basic Example](#basic-example)
- [Examples for Spaces](#examples-for-spaces)
- [Examples for Milestones](#examples-for-milestones)
- [Examples for Users](#examples-for-users)
- [Examples for Tickets](#examples-for-tickets)
- [Model Reference](#model-reference)
- [Caching](#caching)
- [Contributors](#contributors)


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


Assembla resource reference
--------------------------------------------------

All resources are returned with fields corresponding to the data from
Assembla.

While naming conventions generally follow Assembla's
[API Reference](http://www.assembla.com/spaces/breakoutdocs/wiki/Assembla_REST_API),
one difference is that dashes are replaced with underscores, so
`status-name` would become `status_name`.

Where possible, values are coerced to native Python types.


Caching
--------------------------------------------------

The API wrapper uses an in-memory caching system to reduce the overheard on
repeated requests to Assembla.

The cache is activated by default, but you can deactivate it when instantiating
the wrapper:

```python
assembla = API(auth=('Username', 'Password',), cache_responses=False)
```


Contributors
--------------------------------------------------

- [Mark Finger](http://github.com/markfinger)
- [Venkata Ramana](http://github.com/arjunc77)