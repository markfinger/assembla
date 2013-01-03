===============================================================
Python wrapper for the Assembla API
===============================================================

An easy to use wrapper around the [Assembla API](http://api-doc.assembla.com/).

- [Installation](#installation)
- [Basic example](#basic-example)
- [User guide](#user-guide)
- [Filtering objects with keyword arguments](#filtering-objects-with-keyword-arguments)
- [Custom fields](#custom-fields)
- [Caching](#caching)


Installation
--------------------------------------------------

Install assembla with pip:

```
$ pip install assembla
```

Connecting to Assembla's API requires your user account's authentication key and secret,
which are accessible from https://www.assembla.com/user/edit/manage_clients.


Basic example
--------------------------------------------------

The following example connects to Assembla, retrieves a list of tickets for a
space and then outputs information about each.

```python
from assembla import API

assembla = API(
    key='8a71541e5fb2e4741120',
    secret='a260dc4448c81c907fc7c85ad09d31306c425417',
    # Use your API key/secret from https://www.assembla.com/user/edit/manage_clients
)

my_space = assembla.spaces(name='My Space')[0]

for ticket in my_space.tickets():
    print '#{0} - {1}'.format(ticket['number'], ticket['summary'])

# >>> #1 - My first ticket
# >>> #2 - My second ticket
# ...
```


User guide
--------------------------------------------------

The Assembla API wrapper uses a number of Python classes to represent
the objects retrieved from Assembla, some of which possess the following
methods and properties:

- [API](#api)
    - [stream](#apistream)
    - [spaces](#apispaces)
- [Space](#space)
    - [tickets](#spacetickets)
    - [milestones](#spacemilestones)
    - [users](#spaceusers)
- [Milestone](#milestone)
    - [tickets](#milestonetickets)
- [Ticket](#ticket)
    - [milestone](#ticketmilestone)
    - [user](#ticketuser)
- [User](#user)
    - [tickets](#usertickets)
- [Event](#event)


API
--------------------------------------------------

API instances are the primary facet of the Assembla API wrapper and are
the starting point for interactions with the API. APIs are instantiated
with authentication details (available from
https://www.assembla.com/user/edit/manage_clients) and offer two methods
of navigating Assembla's data:

###API.stream
Returns a list of [Event](#event) instances indicating the
activity stream you have access to. Events can be filtered using
keyword arguments
###API.spaces
Returns a list of [Space](#space) instances which represent
all the spaces that you have access to.

Here's an example which prints a list of the spaces available:
```python
from assembla import API

assembla = API(
    key='8a71541e5fb2e4741120',
    secret='a260dc4448c81c907fc7c85ad09d31306c425417',
    # Use your API key/secret from https://www.assembla.com/user/edit/manage_clients
)

for space in assembla.spaces():
	print space['name']
```


Space
--------------------------------------------------

See the [Space object field reference](http://api-doc.assembla.com/content/ref/space_fields.html#fields)
for field names and explanations.

Spaces possess the following methods:

###Space.tickets
Returns a list of all [Ticket](#ticket) instances inside the Space.
Tickets can be [filtered](#filtering-objects-with-keyword-arguments) using keyword arguments.
###Space.milestones
Returns a list of all [Milestone](#milestone) instances inside the Space.
Milestones can be [filtered](#filtering-objects-with-keyword-arguments) using keyword arguments.
###Space.users
Returns a list of all [User](#user) instances with access to the Space.
Users can be [filtered](#filtering-objects-with-keyword-arguments) using keyword arguments.

Here is an example which prints a report of all the tickets in a
Space which have the status 'New' and belong to a milestone called 'Alpha Release':
```python
space = assembla.spaces(name='My Space')[0]

milestone = my_space.milestones(title='Alpha Release')[0]

tickets = space.tickets(
	milestone_id=milestone['id'],
	status='New'
)

print 'New tickets in "{0}".format(milestone['title'])
for ticket in tickets:
    print '#{0} - {1}'.format(ticket['number'], ticket['summary'])

# >>> New tickets in "Alpha Release"
# >>> #1 - My first ticket
# >>> #2 - My second ticket
# ...
```


Milestone
--------------------------------------------------

See the [Milestone object field reference](http://api-doc.assembla.com/content/ref/milestones_fields.html#fields)
for field names and explanations.

Milestone instances possess the following method:

###Milestone.tickets
Returns a list of all [Ticket](#ticket) instances which are connected
to the Milestone. Tickets can be [filtered](#filtering-objects-with-keyword-arguments) using keyword arguments.

Here is an example which prints a report of all the tickets in a
milestone:
```python
milestone = space.milestones()[0]

for ticket in milestone.tickets():
    print '#{0} - {1}'.format(ticket['number'], ticket['summary'])

# >>> #1 - My first ticket
# >>> #2 - My second ticket
# ...
```


Ticket
--------------------------------------------------

See the [Ticket object field reference](http://api-doc.assembla.com/content/ref/ticket_fields.html#fields)
for field names and explanations.

Ticket instances possess the following properties:

###Tickets.milestone
An instance of the [Milestone](#milestone) that the Ticket belongs to.

###Tickets.user
An instance of the [User](#user) that the Ticket is assigned to.


User
--------------------------------------------------

See the [User object field reference](http://api-doc.assembla.com/content/ref/user_fields.html#fields)
for field names and explanations.

User instances possess the following method:

###User.tickets
Returns a list of all [Ticket](#ticket) instances which are assigned
to the User. Tickets can be [filtered](#filtering-objects-with-keyword-arguments) using keyword arguments.

Here is an example which prints a report of all the tickets assigned
to a user named 'John Smith':
```python
user = space.users(name='John Smith')[0]

for ticket in user.tickets():
    print '#{0} - {1}'.format(ticket['number'], ticket['summary'])

# >>> #1 - John's first ticket
# >>> #2 - John's second ticket
# ...
```


Event
--------------------------------------------------

See the [Event object field reference](http://api-doc.assembla.com/content/ref/event_fields.html#fields)
for field names and explanations.


Filtering objects with keyword arguments
--------------------------------------------------

Most data retrieval methods allow for filtering of the objects based on
the data returned by Assembla. The keyword arguments to use correlate to
the field names returned by Assembla, for example [Tickets](#ticket) can
be filtered with keyword arguments similar to field names specified in
[Assembla's Ticket Fields documentation](http://api-doc.assembla.com/content/ref/ticket_fields.html)

Using [Space.tickets](#spacetickets) as an example of filtering with keyword
arguments:
- `space.tickets(number=100)` will return the ticket with the number 100.
- `space.tickets(status='New', assigned_to_id=100)` will return new tickets assigned to a user with the id 100

The following methods allow for keyword filtering:
- [API.stream](#apistream)
- [API.spaces](#apispaces)
- [Space.tickets](#spacetickets)
- [Space.milestones](#spacemilestones)
- [Space.users](#spaceusers)
- [Milestone.tickets](#milestonetickets)
- [User.tickets](#usertickets)


Custom fields
--------------------------------------------------

An object's custom fields are retrieved similarly to most fields, the only difference
is that they are nested within a dictionary named `custom_fields`.

Here's an example to get a custom field 'billing_code' from a ticket:
```python
billing_code = ticket['custom_fields']['billing_code']
```


Caching
--------------------------------------------------

The API wrapper has an optional response caching system which is deactivated
by default. Turning the caching system on will reduce the overhead on repeated
requests, but can cause stale data to perpetuate for long-running processes.
Turning the cache on is done by setting an [API](#api) instance's `cache_responses`
variable to `True`. The cache can be turned off by setting `cache_responses`
to `False`.

Here is an example of how to instantiate the wrapper and activate the cache.
```python
from assembla import API

assembla = API(
	# Auth details...
)

assembla.cache_responses = True
```
