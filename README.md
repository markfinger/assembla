===============================================================
Python wrapper for the Assembla API
===============================================================

An easy to use wrapper around the [Assembla API](http://www.assembla.com/spaces/breakoutdocs/wiki/Assembla_REST_API).

- [Basic Example](#basic-example)
- [Examples for Spaces](#examples-for-spaces)
- [Examples for Milestones](#examples-for-milestones)
- [Examples for Users](#examples-for-users)
- [Examples for Tickets](#examples-for-tickets)
- [Assembla's space-driven design and API caveats](#assemblas-space-driven-design-and-api-caveats)
- [Assembla resource reference](#assembla-resource-reference)
- [Caching](#caching)
- [Contributors](#contributors)


Basic Example
--------------------------------------------------

```python
from assembla import API

# Authenticate using your normal Assembla Username and Password
auth = (
	'' # Username,
	'' # Password,
)

assembla = API(auth)

print assembla.space(name='Big Project').ticket(number=201).status_name
```


Examples for Spaces
--------------------------------------------------

```python
# Retrieve your available spaces
spaces = assembla.spaces()

# Select a specific space
space = assembla.space(name='My Project')

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
milestone = assembla.space(name='My Project').milestone('Release Candidate 1')

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
user = assembla.space(name='My Project').user(name='John Smith')

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


Assembla's space-driven design and API caveats
--------------------------------------------------

The design of the API wrapper follows the conventions of Assembla's interface
and API, which is structured around Spaces for each project. The outcome of this
design is that extracting data is generally done by selecting a [Space](#examples-for-spaces)
and then narrowing down through it's data.

The positive is that it means that once you have selected a Space, you can
easily retrieve data that will always be contextually relevant.

The *big* downside is that it causes some data to be non-trivial to retrieve.
For example: every ticket assigned to one user across Assembla:

```python
user = assembla.space(name='My Project').user(name='John Smith')
tickets = []

for space in assembla.spaces():
	assigned_tickets = space.tickets(assigned_to_id=user.id)
	if assigned_tickets:
		tickets.append(assigned_tickets)

print tickets
```

Due to Assembla's API design, the above loop causes a request to be
sent to Assembla for every `space.tickets` call. While the wrapper uses a few
optimisations, such as the [caching system](#caching), to get around this, it is
an important flaw to be aware of.


Assembla resource reference
--------------------------------------------------

All resources are returned with fields corresponding to the data from
Assembla.

While naming conventions generally follow Assembla's
[API Reference](http://www.assembla.com/spaces/breakoutdocs/wiki/Assembla_REST_API),
one difference is that dashes are replaced with underscores, so
`status-name` would become `status_name`.

Where possible, values are coerced to native Python types, eg: dates are parsed
as as `datetime.datetime` objects.


Caching
--------------------------------------------------

The API wrapper uses an in-memory caching system to reduce the overheard on
repeated requests to Assembla.

The cache is activated by default, but you can deactivate it when instantiating
the wrapper by passing `cache_responses=False`:

```python
from assembla import API

assembla = API(
	...,
	cache_responses=False
)
```


Contributors
--------------------------------------------------

- [Mark Finger](http://github.com/markfinger)
- [Venkata Ramana](http://github.com/arjunc77)