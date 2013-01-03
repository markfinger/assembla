===============================================================
Python wrapper for the Assembla API
===============================================================

An easy to use wrapper around the [Assembla API](http://api-doc.assembla.com/).

- [Installation](#installation)
- [Basic example](#basic-example)
- [User guide](#user-guide)
	- [API](#api)
    - [Space](#space)
    - [Milestone](#milestone)
    - [Ticket](#ticket)
    - [User](#user)
    - [Event](#event)
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
the objects retrieved from Assembla, some of which possess specific
methods:

- [API](#api)
    - [stream](#)
    - [spaces](#)
- [Space](#space)
    - [tickets](#)
    - [milestones](#)
    - [users](#)
- [Milestone](#milestone)
    - [tickets](#)
- [Ticket](#ticket)
    - [milestone](#)
    - [user](#)
- [User](#user)
    - [tickets](#)
- [Event](#event)


API
--------------------------------------------------

API instances are the primary facet of the Assembla API wrapper and are
the starting point for interactions with the API. APIs are instantiated
with authentication details (available from
https://www.assembla.com/user/edit/manage_clients) and offer two methods
of navigating Assembla's data:

	- ###Stream
	    Returns a list of [Event](#event) instances indicating the
	    activity stream you have access to.
	- ###Spaces
		Returns a list of [Space](#space) instances which represent
		all the spaces that you have access to.

```python
from assembla import API

assembla = API(
    key='8a71541e5fb2e4741120',
    secret='a260dc4448c81c907fc7c85ad09d31306c425417',
    # Use your API key/secret from https://www.assembla.com/user/edit/manage_clients
)

my_spaces = assembla.spaces()
my_stream = assembla.stream()
```


Custom fields
--------------------------------------------------
Custom fields
	-> Ticket example


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