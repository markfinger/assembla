===============================================================
Python wrapper for the Assembla API
===============================================================

An easy to use wrapper around the [Assembla API](http://api-doc.assembla.com/).

Getting started
	Installation
		pypi
		pip/easy_install
	Basic Tutorial
		from assembla import API
		assembla = API(key, secret)
		space = assembla.spaces(name='My Project')
		space.tickets(number=143)

API Structure
	API
		-> Stream
		-> Spaces
	Space
		-> Milestones
		-> Tickets
		-> Users
	Milestone
		-> Tickets
	Tickets
		-> Milestone
		-> User
	User
		-> Tickets

Caching

Custom fields
	-> Ticket example